"""
운동 대사량(METs) 기반 소모 칼로리 계산 도구 모듈
미국 스포츠의학회(ACSM) 및 WHO 표준 운동 대사량(Compendium of Physical Activities) 기준
공식: 소모 칼로리 (kcal) = 1.05 * METs * 체중(kg) * 운동시간(시간)
"""

from typing import Dict, Any, Tuple

# 표준 운동별 METs 계수 데이터베이스
METS_DATABASE = {
    # 걷기 & 달리기
    "가벼운 걷기": 3.0,
    "보통 걷기": 3.5,
    "빠른 걷기": 4.5,
    "만보기 산책": 3.0,
    "산책": 3.0,
    "조깅": 7.0,
    "러닝": 8.5,
    "달리기": 8.5,
    "전력 질주": 11.5,
    "트레드밀": 7.5,
    "런닝머신": 7.5,
    
    # 헬스 & 근력 운동
    "웨이트 트레이닝": 5.5,
    "헬스": 5.5,
    "근력 운동": 5.5,
    "스쿼트": 5.5,
    "데드리프트": 6.0,
    "벤치프레스": 5.0,
    "맨몸 운동": 4.5,
    "홈트": 5.0,
    "크로스핏": 8.0,
    "플랭크": 3.5,
    
    # 유산소 & 스포츠
    "자전거": 6.0,
    "실내 자전거": 6.0,
    "사이클": 7.5,
    "수영": 7.0,
    "수영 자유형": 7.5,
    "수영 평영": 6.5,
    "줄넘기": 10.0,
    "계단 오르기": 8.0,
    "등산": 7.5,
    "배드민턴": 6.0,
    "테니스": 7.3,
    "축구": 8.0,
    "농구": 6.5,
    "복싱": 9.0,
    "필라테스": 3.5,
    "요가": 2.5,
    "스트레칭": 2.3,
    "탁구": 4.0,
    "볼링": 3.0,
    "골프": 3.8
}

def calculate_exercise_calories(exercise_name: str, duration_minutes: float, user_weight: float = 70.0) -> Dict[str, Any]:
    """
    운동명과 운동 시간(분), 체중(kg)을 입력받아 소모 칼로리(kcal)를 계산합니다.
    """
    if not exercise_name or duration_minutes <= 0:
        return {"error": "운동명과 유효한 운동 시간(분)을 입력해주세요."}
        
    exercise_clean = exercise_name.strip()
    
    # 1. 일치하는 METs 계수 탐색
    mets = None
    matched_name = exercise_clean
    
    # 정확한 일치
    if exercise_clean in METS_DATABASE:
        mets = METS_DATABASE[exercise_clean]
    else:
        # 부분 일치 검색
        for name, m in METS_DATABASE.items():
            if name in exercise_clean or exercise_clean in name:
                mets = m
                matched_name = name
                break
                
    # 기본값 (일반 중강도 운동 5.0 METs)
    if mets is None:
        mets = 5.0
        matched_name = f"{exercise_clean} (일반 운동)"
        
    # 2. 칼로리 계산: 1.05 * METs * 체중(kg) * (시간 / 60)
    duration_hours = duration_minutes / 60.0
    burned_calories = 1.05 * mets * user_weight * duration_hours
    burned_calories = round(burned_calories, 1)
    
    return {
        "운동명": matched_name,
        "운동시간(분)": round(duration_minutes, 1),
        "적용체중(kg)": round(user_weight, 1),
        "METs계수": mets,
        "소모칼로리(kcal)": burned_calories,
        "설명": f"{user_weight}kg 기준 {matched_name} {duration_minutes}분 수행 시 약 {burned_calories} kcal 소모"
    }

if __name__ == "__main__":
    print(calculate_exercise_calories("러닝", 30, 70.0))
    print(calculate_exercise_calories("스쿼트", 40, 65.0))
    print(calculate_exercise_calories("수영", 45, 75.0))
