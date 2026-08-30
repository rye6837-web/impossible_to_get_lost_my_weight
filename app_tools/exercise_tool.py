"""
운동 소모 칼로리 계산 도구 모듈
미국 스포츠의학회(ACSM / Ainsworth Compendium of Physical Activities) 공인 METs(Metabolic Equivalent of Task) 기반
공식: 소모 칼로리(kcal) = 1.05 * METs * 체중(kg) * (운동시간(분) / 60)
"""

from typing import Dict, Any, Optional

# 1. 스포츠의학 공인 표준 METs(운동 대사 당량) 데이터베이스 (70+ 종목 확장)
EXERCISE_METS_DB = {
    # 🏃 유산소 & 보행/러닝
    "걷기": 3.5,
    "가볍게 걷기": 2.8,
    "빠르게 걷기": 4.5,
    "산책": 3.0,
    "조깅": 7.0,
    "러닝": 8.5,
    "달리기": 8.5,
    "인터벌 러닝": 10.5,
    "트레드밀": 7.5,
    "러닝머신": 7.5,
    "천국의 계단": 9.0,
    "스텝밀": 9.0,
    "계단 오르기": 8.0,
    "줄넘기": 10.0,
    "고강도 줄넘기": 12.0,
    
    # 🏋️ 헬스 & 근력 & 홈트레이닝
    "웨이트 트레이닝": 5.5,
    "헬스": 5.5,
    "근력 운동": 5.5,
    "스쿼트": 5.5,
    "데드리프트": 6.0,
    "벤치프레스": 5.0,
    "맨몸 운동": 4.5,
    "홈트": 5.0,
    "홈트레이닝": 5.0,
    "크로스핏": 8.5,
    "타바타": 9.5,
    "HIIT": 9.0,
    "고강도 인터벌": 9.0,
    "플랭크": 3.5,
    "버피": 10.0,
    "버피테스트": 10.0,
    "푸시업": 5.0,
    "팔굽혀펴기": 5.0,
    "풀업": 6.0,
    "턱걸이": 6.0,
    "케틀벨": 8.0,
    "로잉머신": 7.0,
    "점핑잭": 8.0,
    
    # 🚴 사이클 & 수영 & 수상 스포츠
    "자전거": 6.0,
    "실내 자전거": 6.0,
    "사이클": 7.5,
    "스피닝": 8.5,
    "수영": 7.0,
    "수영 자유형": 7.5,
    "수영 평영": 6.5,
    "수영 접영": 11.0,
    "수영 배영": 6.0,
    "서핑": 5.0,
    "패들보드": 4.5,
    
    # 🏸 라켓 & 구기 스포츠
    "배드민턴": 6.0,
    "테니스": 7.3,
    "스쿼시": 11.0,
    "탁구": 4.0,
    "축구": 8.0,
    "풋살": 9.0,
    "농구": 6.5,
    "야구": 5.0,
    "배구": 4.0,
    "골프": 4.0,
    "스크린 골프": 3.5,
    "볼링": 3.0,
    "당구": 2.5,
    
    # 🥊 격투기 & 무술
    "복싱": 9.0,
    "샌드백 복싱": 8.0,
    "스파링": 11.0,
    "킥복싱": 10.0,
    "주짓수": 9.0,
    "태권도": 8.0,
    "유도": 8.5,
    "무에타이": 10.0,
    
    # 🧘 유연성 & 댄스 & 아웃도어
    "필라테스": 3.5,
    "기구 필라테스": 4.0,
    "요가": 2.5,
    "핫요가": 4.0,
    "스트레칭": 2.3,
    "등산": 7.5,
    "가벼운 등산": 6.0,
    "암벽등반": 8.0,
    "클라이밍": 8.0,
    "볼더링": 8.0,
    "댄스": 6.0,
    "줌바": 6.5,
    "에어로빅": 6.5,
    "발레": 5.0,
    "스키": 6.5,
    "스노보드": 6.0,
    "스케이트": 7.0,
    "인라인스케이트": 7.5
}

def calculate_exercise_calories(
    exercise_name: str, 
    duration_minutes: float, 
    user_weight: float = 70.0,
    custom_mets: Optional[float] = None
) -> Dict[str, Any]:
    """
    운동명, 운동시간(분), 사용자 체중(kg)을 입력받아 소모 칼로리를 정밀 계산합니다.
    
    Args:
        exercise_name (str): 운동 이름 (예: "러닝", "스쿼트", "필라테스", "링피트")
        duration_minutes (float): 운동 시간(분)
        user_weight (float): 사용자 체중(kg) (기본값: 70.0)
        custom_mets (Optional[float]): AI 에이전트가 추정한 맞춤 METs 계수 (미등록 희귀 운동 시)
        
    Returns:
        Dict[str, Any]: 계산된 소모 칼로리 및 상세 영양 대사 메타데이터
    """
    exercise_clean = exercise_name.strip()
    mets: Optional[float] = None
    matched_name = exercise_clean
    is_custom = False
    
    # 1. AI 에이전트가 직접 추정한 맞춤 custom_mets가 있는 경우 최우선 적용
    if custom_mets is not None and custom_mets > 0:
        mets = round(float(custom_mets), 1)
        matched_name = f"{exercise_clean} (AI 맞춤 추정)"
        is_custom = True
    else:
        # 2. 내장 70+ 공인 METs 데이터베이스 탐색
        # 2-1. 완전 일치 검색
        if exercise_clean in EXERCISE_METS_DB:
            mets = EXERCISE_METS_DB[exercise_clean]
            matched_name = exercise_clean
        else:
            # 2-2. 부분 일치 검색
            for name, m in EXERCISE_METS_DB.items():
                if name in exercise_clean or exercise_clean in name:
                    mets = m
                    matched_name = name
                    break
                    
        # 2-3. 미등록 신규 운동 시 표준 중강도 기본값(5.0 METs) 폴백
        if mets is None:
            mets = 5.0
            matched_name = f"{exercise_clean} (일반 중강도 운동)"
        
    # 3. ACSM 공식 소모 칼로리 정밀 계산: 1.05 * METs * 체중(kg) * (시간(분) / 60)
    duration_hours = duration_minutes / 60.0
    burned_calories = 1.05 * mets * user_weight * duration_hours
    burned_calories = round(burned_calories, 1)
    
    return {
        "운동명": matched_name,
        "운동시간(분)": round(duration_minutes, 1),
        "적용체중(kg)": round(user_weight, 1),
        "METs계수": mets,
        "소모칼로리(kcal)": burned_calories,
        "AI맞춤추정여부": is_custom,
        "설명": f"{user_weight}kg 기준 {matched_name} {duration_minutes}분 수행 시 약 {burned_calories} kcal 소모"
    }

if __name__ == "__main__":
    print("1. 표준 DB 등록 종목:", calculate_exercise_calories("천국의 계단", 30, 70.0))
    print("2. 부분 일치 종목:", calculate_exercise_calories("야외 러닝 훈련", 40, 65.0))
    print("3. AI 맞춤 추정 종목:", calculate_exercise_calories("닌텐도 링피트", 45, 70.0, custom_mets=6.5))
    print("4. 미등록 기본값 종목:", calculate_exercise_calories("미지의 외계 운동", 30, 70.0))
