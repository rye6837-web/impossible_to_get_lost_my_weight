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

def clean_api_key(key: Optional[str]) -> str:
    """API 키 문자열의 양 끝 공백, 따옴표 등을 안전하게 제거합니다."""
    if not key:
        return ""
    return str(key).strip().strip('"').strip("'").strip()

def test_gemini_api_key(api_key: str) -> Tuple[bool, str]:
    """Gemini API 키의 유효성을 경량 네트워크 핑으로 사전 검증합니다."""
    cleaned = clean_api_key(api_key)
    if not cleaned:
        return False, "API 키를 입력해주세요."
    try:
        test_client = genai.Client(api_key=cleaned)
        _ = [m for m in test_client.models.list(config={"page_size": 1})]
        return True, "API 키가 성공적으로 검증되었습니다."
    except Exception as e:
        err_str = str(e)
        if "API_KEY_INVALID" in err_str or "API key not valid" in err_str:
            return False, "Google API 서버에서 거절된 유효하지 않은 API 키입니다. Google AI Studio에서 'AIzaSy'로 시작하는 올바른 키를 확인해주세요."
        return False, f"API 키 검증 중 오류: {err_str}"

def get_api_key() -> str:
    """Gemini API 키를 여러 소스에서 순차적으로 탐색합니다."""
    if "GEMINI_API_KEY" in st.session_state and st.session_state["GEMINI_API_KEY"]:
        cleaned = clean_api_key(st.session_state["GEMINI_API_KEY"])
        if cleaned:
            return cleaned
    try:
        if "GEMINI_API_KEY" in st.secrets:
            cleaned = clean_api_key(st.secrets["GEMINI_API_KEY"])
            if cleaned:
                return cleaned
    except Exception:
        pass
    env_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    return clean_api_key(env_key)

# 3. 에이전트 시스템 프롬프트 (공식 출처 표기 & 스마트 폴백 & ReAct 가이드라인)
SYSTEM_INSTRUCTION = """
당신은 전문적이고 친절한 'AI 다이어트 & 종합 웰니스 코치 에이전트'입니다.

당신은 다음 3가지 전문 도구(Tools)를 적극적으로 활용해야 합니다:
1. `search_food_nutrition(food_name)`: 사용자가 음식이나 식단을 이야기하면, 칼로리와 영양소를 절대 임의로 지어내지 말고 반드시 이 도구를 호출하여 식약처 표준 영양 수치를 확인하세요.
2. `calculate_exercise_calories(exercise_name, duration_minutes, user_weight, custom_mets)`: 사용자가 운동(러닝, 헬스, 수영 등)을 했다고 하면, 이 도구를 호출하여 과학적인 METs 기반 소모 칼로리를 계산하세요. 만약 생소하거나 특이한 운동(예: 링피트, VR게임 등)일 경우 당신의 스포츠의학 지식으로 추정한 METs 강도 계수를 `custom_mets` 인자에 전달할 수 있습니다.
3. `search_nutrition_knowledge(query)`: 사용자가 혈당 관리, 다이어트 정체기, 단백질 흡수 타이밍, 대체 식재료, 야식 대처법 등 다이어트 상식/원리를 물어보면 이 도구를 검색하여 전문적인 가이드를 제공하세요.

답변 가이드라인:
- 영양/식단 분석 시: 섭취한 음식의 총 칼로리 및 탄/단/지/나트륨 수치를 요약하고, 사용자의 일일 목표치 대비 진단과 다음 식사 추천 팁을 친절히 안내하세요.
- [스마트 폴백 대응]: 도구 호출 결과에서 `is_fallback: True`인 경우, 해당 음식이 식약처 공식 DB 미등록 항목이어서 일반 조리법 추정치가 적용되었음을 안내하고, 실제 섭취량이나 조리법에 따라 필요 시 말씀해주시면 조정해 드리겠다고 안내하세요.
- 운동 분석 시: 소모된 칼로리가 오늘 식단 관리에 얼마나 기여했는지 격려하고 칭찬해 주세요.
- [필수: 공식 출처(Citation) 표기]: 도구를 호출하여 수치나 팁을 제시한 경우, 답변 본문 맨 마지막(태그 직전)에 반드시 아래 형식으로 참조 근거를 명시하세요:
  📌 [참조 근거: 식품의약품안전처 2024 통합식품영양성분DB / 미국스포츠의학회(ACSM) METs 가이드라인 / 보건복지부 한국인 영양소 섭취기준(KDRIs)]
  (활용한 도구의 출처만 간결하게 포함하세요)

[중요: 복합 질문 처리 및 다중 메타데이터 태그 규칙]
- 사용자가 식단과 운동을 함께 언급하거나 복수의 활동을 이야기한 경우:
  1) `search_food_nutrition`과 `calculate_exercise_calories` 전문 도구를 반드시 모두 호출하여 식단 영양소와 운동 소모 칼로리를 각각 분석하세요.
  2) 섭취 칼로리와 운동 소모 칼로리를 비교하여 오늘 순 칼로리(Net Calories) 및 다이어트에 미친 긍정적 영향을 종합 진단하세요.
  3) 분석 완료 후, 응답 맨 마지막 줄에 반드시 아래와 같이 두 태그를 각각 독립된 줄로 모두 출력해야 합니다 (순서 무관):
<!-- MEAL_DATA: {"food_name": "대표 음식명(또는 종합 식단명)", "calories": 520, "carbs": 65, "protein": 32, "fat": 14, "sugar": 5, "sodium": 650, "meal_type": "점심"} -->
<!-- EXERCISE_DATA: {"exercise_name": "운동명", "duration_min": 30, "calories_burned": 220} -->
- 식단만 언급된 경우 MEAL_DATA 태그만, 운동만 언급된 경우 EXERCISE_DATA 태그만 단독 출력하세요.
"""

class DietAgent:
    def __init__(self, api_key: str = ""):
        self.api_key = clean_api_key(api_key or get_api_key())
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. API 키를 입력하거나 .streamlit/secrets.toml에 등록해주세요.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.current_model_idx = 0
        self._init_chat(CANDIDATE_MODELS[self.current_model_idx])

    def _init_chat(self, model_name: str, history=None):
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
            ),
            history=history
        )

    def _prune_history_if_needed(self, max_turns: int = 8):
        """
        슬라이딩 윈도우(Sliding Window Buffer):
        대화가 길어질 경우 최근 max_turns턴(기본 8턴 = 16개 메시지)만 유지하여
        토큰 낭비 및 429 Rate Limit, 503 과부하 에러를 원천 차단합니다.
        """
        try:
            history = self.chat.get_history()
            max_msgs = max_turns * 2
            if len(history) > max_msgs:
                pruned_history = history[-max_msgs:]
                self._init_chat(self.active_model, history=pruned_history)
                print(f"[INFO] 슬라이딩 윈도우 적용: {len(history)}개 -> 최근 {len(pruned_history)}개 메시지 유지")
        except Exception as e:
            pass

    def send_message(self, contents) -> str:
        """
        다중 모델 폴백(Fallback) 및 슬라이딩 윈도우가 내장된 메시지 전송 메서드.
        503(과부하), 429(속도제한) 발생 시 순차적으로 예비 모델로 자동 전환하여 재시도합니다.
        API_KEY_INVALID 발생 시 모델 전환 없이 즉시 명확한 오류를 발생시킵니다.
        """
        last_error = None
        
        # 1. 호출 전 슬라이딩 윈도우 점검
        self._prune_history_if_needed(max_turns=8)
        
        for idx in range(len(CANDIDATE_MODELS)):
            model_to_try = CANDIDATE_MODELS[(self.current_model_idx + idx) % len(CANDIDATE_MODELS)]
            
            if self.active_model != model_to_try:
                try:
                    # 기존 대화 히스토리 유지하며 모델 전환
                    current_history = None
                    try:
                        current_history = self.chat.get_history()
                    except Exception:
                        pass
                    self._init_chat(model_to_try, history=current_history)
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
                # API 키 자체 오류인 경우 예비 모델로 전환해도 소용없으므로 즉시 탈출
                if "API_KEY_INVALID" in err_msg or "API key not valid" in err_msg or "INVALID_ARGUMENT" in err_msg:
                    raise ValueError("⚠️ 등록된 Gemini API 키가 유효하지 않습니다 (API_KEY_INVALID). API 키를 확인 후 다시 입력해주세요.") from e
                
                print(f"[WARN] [{model_to_try}] 일시적 과부하/오류 ({err_msg[:60]}...) -> 예비 모델로 자동 전환합니다.")
                time.sleep(1.5)
                continue
                
        raise last_error or RuntimeError("모든 예비 Gemini 모델의 응답에 실패했습니다. 잠시 후 다시 시도해주세요.")

def parse_agent_metadata(response_text: str) -> Tuple[str, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    에이전트 응답 텍스트에서 MEAL_DATA 및 EXERCISE_DATA 메타데이터 태그를 파싱하여 분리합니다.
    re.findall을 사용하여 식단과 운동이 동시에 감지되거나 복수의 태그가 출력될 때도 100% 누락 없이 수집합니다.
    반환: (클린 텍스트, 식단 메타데이터 딕셔너리, 운동 메타데이터 딕셔너리)
    """
    meal_data = None
    exercise_data = None
    
    # 1. 모든 MEAL_DATA 태그 파싱
    meal_matches = re.findall(r'<!--\s*MEAL_DATA:\s*(\{.*?\})\s*-->', response_text, re.DOTALL)
    meals = []
    for raw in meal_matches:
        try:
            m = json.loads(raw)
            meals.append(m)
        except Exception:
            pass
            
    if meals:
        meal_data = meals[0]
        if len(meals) > 1:
            meal_data["_all_meals"] = meals

    # 2. 모든 EXERCISE_DATA 태그 파싱
    ex_matches = re.findall(r'<!--\s*EXERCISE_DATA:\s*(\{.*?\})\s*-->', response_text, re.DOTALL)
    exercises = []
    for raw in ex_matches:
        try:
            e = json.loads(raw)
            exercises.append(e)
        except Exception:
            pass
            
    if exercises:
        exercise_data = exercises[0]
        if len(exercises) > 1:
            exercise_data["_all_exercises"] = exercises

    # 3. 본문에서 주석 태그 제거
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
