import os
import sys
import json
import re
import time
import streamlit as st
from google import genai
from google.genai import types
from typing import Optional, Dict, Any, Tuple, List

# 1. 모듈 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from app_tools.food_db import search_food_nutrition
from app_tools.exercise_tool import calculate_exercise_calories
from app_tools.nutrition_rag import search_nutrition_knowledge

# 2. 다중 모델 폴백(Fallback) 우선순위 리스트 (gemini-3.5-flash-lite 1순위 구성)
CANDIDATE_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash"
]

def get_api_key() -> str:
    """Gemini API 키를 여러 소스에서 순차적으로 탐색합니다."""
    if "GEMINI_API_KEY" in st.session_state and st.session_state["GEMINI_API_KEY"]:
        return st.session_state["GEMINI_API_KEY"]
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY", "")

# 3. 에이전트 시스템 프롬프트
SYSTEM_INSTRUCTION = """
당신은 전문적이고 친절한 'AI 다이어트 & 종합 웰니스 코치 에이전트'입니다.

당신은 다음 3가지 전문 도구(Tools)를 적극적으로 활용해야 합니다:
1. `search_food_nutrition(food_name)`: 사용자가 음식이나 식단을 이야기하면, 칼로리와 영양소를 절대 임의로 지어내지 말고 반드시 이 도구를 호출하여 식약처 표준 영양 수치를 확인하세요.
2. `calculate_exercise_calories(exercise_name, duration_minutes, user_weight, custom_mets)`: 사용자가 운동(러닝, 헬스, 수영 등)을 했다고 하면, 이 도구를 호출하여 과학적인 METs 기반 소모 칼로리를 계산하세요. 만약 생소하거나 특이한 운동(예: 링피트, VR게임 등)일 경우 당신의 스포츠의학 지식으로 추정한 METs 강도 계수를 `custom_mets` 인자에 전달할 수 있습니다.
3. `search_nutrition_knowledge(query)`: 사용자가 혈당 관리, 다이어트 정체기, 단백질 흡수 타이밍, 대체 식재료, 야식 대처법 등 다이어트 상식/원리를 물어보면 이 도구를 검색하여 전문적인 가이드를 제공하세요.

답변 가이드라인:
- 영양/식단 분석 시: 섭취한 음식의 총 칼로리 및 탄/단/지/나트륨 수치를 요약하고, 사용자의 일일 목표치 대비 진단과 다음 식사 추천 팁을 친절히 안내하세요.
- 운동 분석 시: 소모된 칼로리가 오늘 식단 관리에 얼마나 기여했는지 격려하고 칭찬해 주세요.

[중요: 데이터베이스 자동 저장을 위한 메타데이터 태그 규칙]
- 사용자가 먹은 식단을 분석하여 총 칼로리와 영양소가 도출되었을 때, 응답의 맨 마지막 줄에 반드시 아래 형식의 JSON 태그를 한 줄로 붙여주세요 (사용자에게는 숨겨지고 시스템이 파싱합니다):
<!-- MEAL_DATA: {"food_name": "대표 음식명(또는 종합 식단명)", "calories": 520, "carbs": 65, "protein": 32, "fat": 14, "sugar": 5, "sodium": 650, "meal_type": "점심"} -->

- 사용자가 수행한 운동을 분석하여 소모 칼로리가 도출되었을 때, 응답의 맨 마지막 줄에 반드시 아래 형식의 JSON 태그를 한 줄로 붙여주세요:
<!-- EXERCISE_DATA: {"exercise_name": "운동명", "duration_min": 30, "calories_burned": 220} -->
"""

class DietAgent:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or get_api_key()
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. API 키를 입력하거나 .streamlit/secrets.toml에 등록해주세요.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.current_model_idx = 0
        self._init_chat(CANDIDATE_MODELS[self.current_model_idx])

    def _init_chat(self, model_name: str):
        """특정 모델명으로 대화 세션을 생성합니다."""
        self.active_model = model_name
        self.chat = self.client.chats.create(
            model=model_name,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[
                    search_food_nutrition, 
                    calculate_exercise_calories, 
                    search_nutrition_knowledge
                ],
            )
        )

    def send_message(self, contents) -> str:
        """
        다중 모델 폴백(Fallback) 기능이 내장된 메시지 전송 메서드.
        503(과부하), 429(속도제한) 발생 시 순차적으로 예비 모델로 자동 전환하여 재시도합니다.
        """
        last_error = None
        
        for idx in range(len(CANDIDATE_MODELS)):
            model_to_try = CANDIDATE_MODELS[(self.current_model_idx + idx) % len(CANDIDATE_MODELS)]
            
            if self.active_model != model_to_try:
                try:
                    self._init_chat(model_to_try)
                except Exception as init_err:
                    continue
                    
            try:
                response = self.chat.send_message(contents)
                if response and response.text:
                    self.current_model_idx = (self.current_model_idx + idx) % len(CANDIDATE_MODELS)
                    return response.text
            except Exception as e:
                err_msg = str(e)
                last_error = e
                print(f"⚠️ [{model_to_try}] 일시적 과부하/오류 ({err_msg[:60]}...) -> 예비 모델로 자동 전환합니다.")
                time.sleep(1.5)
                continue
                
        raise last_error or RuntimeError("모든 예비 Gemini 모델의 응답에 실패했습니다. 잠시 후 다시 시도해주세요.")

def parse_agent_metadata(response_text: str) -> Tuple[str, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    에이전트 응답 텍스트에서 MEAL_DATA 또는 EXERCISE_DATA 메타데이터 태그를 파싱하여 분리합니다.
    반환: (클린 텍스트, 식단 메타데이터 딕셔너리, 운동 메타데이터 딕셔너리)
    """
    meal_data = None
    exercise_data = None
    
    # MEAL_DATA 정규식 매칭
    meal_match = re.search(r'<!--\s*MEAL_DATA:\s*(\{.*?\})\s*-->', response_text, re.DOTALL)
    if meal_match:
        try:
            meal_data = json.loads(meal_match.group(1))
        except Exception:
            pass
            
    # EXERCISE_DATA 정규식 매칭
    ex_match = re.search(r'<!--\s*EXERCISE_DATA:\s*(\{.*?\})\s*-->', response_text, re.DOTALL)
    if ex_match:
        try:
            exercise_data = json.loads(ex_match.group(1))
        except Exception:
            pass
            
    # 본문에서 주석 태그 제거
    clean_text = re.sub(r'<!--\s*(?:MEAL_DATA|EXERCISE_DATA):\s*\{.*?\}\s*-->', '', response_text, flags=re.DOTALL).strip()
    return clean_text, meal_data, exercise_data

def create_diet_agent(api_key: str = ""):
    return DietAgent(api_key=api_key)

if __name__ == "__main__":
    print("🤖 다중 모델 자동 폴백(Fallback) 탑재 에이전트 테스트 중...")
    try:
        agent = create_diet_agent()
        resp = agent.send_message("오늘 점심 식단으로 닭가슴살 100g이랑 사과 먹었어")
        clean, meal, ex = parse_agent_metadata(resp)
        print("\n[성공한 활성 모델]:", agent.active_model)
        print("\n[클린 응답]:\n", clean)
        print("\n[추출된 식단]:", meal)
    except Exception as e:
        print(f"\n❌ 실행 오류: {e}")
