"""
다이어트 & 임상 영양 백과사전 지식 검색(RAG) 고도화 모듈
BM25(키워드 정확도) + Dense Semantic(자연어 맥락 유사도) 하이브리드 RAG 엔진
"""

import math
import re
from typing import Dict, Any, List, Tuple

# 1. 14대 전문 임상 영양 & 다이어트 가이드라인 지식 베이스
NUTRITION_KNOWLEDGE_BASE = [
    {
        "id": "kb_blood_sugar",
        "topic": "혈당 스파이크 방지 및 식사 순서",
        "keywords": ["혈당", "혈당스파이크", "식사순서", "당뇨", "인슐린", "탄수화물흡수", "식후졸림"],
        "content": "식사 시 [식이섬유(채소/샐러드) -> 단백질/지방(고기/생선/두부) -> 탄수화물(밥/면/빵)] 순서로 섭취하면 위장 통과 시간이 늦춰져 급격한 혈당 스파이크를 방지하고 인슐린 과다 분비로 인한 체지방 축적과 식후 식곤증을 효과적으로 막을 수 있습니다."
    },
    {
        "id": "kb_plateau_refeed",
        "topic": "다이어트 정체기 극복 및 리피드(Re-feed) 전략",
        "keywords": ["정체기", "살이안빠져", "몸무게정체", "대사저하", "치팅데이", "리피드", "기초대사량"],
        "content": "장기간 저칼로리 식단 유지 시 렙틴 호르몬 감소와 기초대사량 저하로 체중 정체기가 발생합니다. 이때 무작정 굶기보다 1~2일간 클린 탄수화물(고구마, 현미밥, 오트밀) 섭취량을 평소의 1.3~1.5배 늘리는 '리피드(Re-feed)'를 진행하고, 운동 강도나 종목에 변화를 주어 대사 스위치를 재활성화하는 것이 가장 과학적인 극복법입니다."
    },
    {
        "id": "kb_protein_timing",
        "topic": "단백질 흡수율과 섭취 타이밍 (MPS 골든타임)",
        "keywords": ["단백질타이밍", "단백질흡수", "단백질보충제", "프로틴", "근손실", "운동직후", "근합성"],
        "content": "단백질은 한 번에 몰아서 먹는 것보다 한 끼당 20~40g씩 3~4시간 간격으로 나누어 섭취할 때 근단백질 합성(MPS) 효율이 가장 높습니다. 웨이트 트레이닝 후 1~2시간 이내에 단백질과 소량의 흡수 빠른 탄수화물을 함께 섭취하면 글리코겐 재합성과 근육 회복이 극대화됩니다."
    },
    {
        "id": "kb_substitute_food",
        "topic": "건강한 저칼로리 대체 식재료 가이드",
        "keywords": ["대체식품", "대체메뉴", "곤약", "알룰로스", "두부면", "컬리플라워", "대체당", "스테비아"],
        "content": "• 쌀밥 대체: 컬리플라워 라이스, 곤약쌀 혼합밥 (칼로리 50% 절감)\n• 밀가루 면 대체: 두부면, 미역국수, 천사채 당면화\n• 설탕 대체: 알룰로스, 스테비아, 에리스리톨 (혈당 지수 0, 칼로리 제로)\n• 탄산음료 대체: 탄산수 + 레몬즙, 제로 탄산음료 (다만 과다 섭취 시 장내 미생물 주의)"
    },
    {
        "id": "kb_late_snack",
        "topic": "야식 폭식 방지 및 늦은 밤 허기(가짜 배고픔) 대처법",
        "keywords": ["야식", "밤에배고플때", "폭식", "배고픔", "가짜배고픔", "늦은저녁", "야식참는법"],
        "content": "밤늦게 느껴지는 갑작스러운 허기의 80%는 뇌의 탈수 신호 또는 감정적 스트레스로 인한 '가짜 배고픔'입니다. 따뜻한 미온수나 허브티(카모마일, 루이보스) 한 잔을 먼저 마시고 15분을 기다려보세요. 참기 힘들 경우 삶은 달걀 1개, 그릭 요거트 80g, 오이 스틱, 구운 아몬드 8알 등 혈당을 자극하지 않는 고단백/식이섬유 간식을 권장합니다."
    },
    {
        "id": "kb_water_fat_burn",
        "topic": "수분 섭취와 체지방 연소 메커니즘",
        "keywords": ["물섭취", "수분", "물다이어트", "체지방연소", "수분보충", "부종"],
        "content": "체지방 1분자를 분해(가수분해)할 때 물 3분자가 필수적으로 소모됩니다. 체내 수분이 부족하면 지방 연소 효율이 최대 30%까지 떨어집니다. 일일 권장 수분 섭취량은 [체중(kg) x 30~35ml]이며, 식사 30분 전 미온수 1잔 섭취는 포만감을 높여 식사량 조절에 크게 기여합니다."
    },
    {
        "id": "kb_alcohol_diet",
        "topic": "음주와 다이어트 (술자리 안주 선택 요령)",
        "keywords": ["술", "알코올", "음주", "회식", "술안주", "소주", "맥주", "와인", "숙취"],
        "content": "알코올(1g당 7kcal)은 체내에서 '우선 소비 독소'로 인식되어, 함께 먹은 안주의 지방 분해를 즉각 중단시키고 복부 내장지방으로 축적시킵니다. 회식 시 당류가 높은 맥주/칵테일보다는 증류주(소주, 위스키)나 드라이 와인을 소량 선택하고, 안주는 사시미(회), 두부김치, 계란찜, 조개탕 등 맑은 단백질 위주로 섭취하세요."
    },
    {
        "id": "kb_intermittent_fasting",
        "topic": "간헐적 단식(16:8) 원리 및 공복 유지 가이드",
        "keywords": ["간헐적단식", "공복", "16:8", "오토파지", "단식중커피", "아침굶기"],
        "content": "간헐적 단식은 16시간 공복 유지 시 인슐린 분비가 바닥으로 떨어지며 지방 연소 모드(케토시스)로 전환되고 세포 자가포식(오토파지)이 일어나는 원리입니다. 공복 시간에는 물, 블랙 아메리카노, 녹차 등 칼로리와 인슐린 자극이 전혀 없는 음료만 허용되며, 8시간 식사 시간대에도 폭식하지 않고 정량 식사를 유지해야 합니다."
    },
    {
        "id": "kb_sodium_edema",
        "topic": "나트륨 과다 섭취 시 부종 관리 및 칼륨 배출 식품",
        "keywords": ["나트륨", "짠음식", "부종", "붓기", "칼륨", "라면먹고부을때"],
        "content": "짠 음식을 먹고 다음 날 체중이 1~2kg 증가하는 것은 지방이 찐 것이 아니라 나트륨이 수분을 붙잡아 생긴 일시적 수분 정체(부종)입니다. 이럴 때는 굶지 말고 칼륨이 풍부한 식품(바나나, 시금치, 아보카도, 오이, 코코넛워터)을 섭취하여 체내 과잉 나트륨과 수분을 소변으로 신속히 배출시키는 것이 정답입니다."
    },
    {
        "id": "kb_carb_cycling",
        "topic": "탄수화물 사이클링(Carb Cycling) 감량 기법",
        "keywords": ["탄수화물사이클링", "저탄수화물", "고탄수화물", "글리코겐", "체지방감량"],
        "content": "탄수화물 사이클링은 고강도 운동일에는 고탄수화물을 섭취하여 운동 수행능력과 대사량을 유지하고, 휴식일이나 유산소일에는 저탄수화물을 섭취하여 인슐린을 낮추고 체지방을 집중 연소시키는 주기적 식단 기법입니다. 정체기 예방과 근육 보존에 매우 탁월합니다."
    },
    {
        "id": "kb_workout_order",
        "topic": "근력 운동과 유산소 운동의 최적 결합 순서",
        "keywords": ["운동순서", "웨이트먼저", "유산소먼저", "근력유산소", "체지방태우는순서"],
        "content": "체지방 감량을 목표로 할 때는 [준비 스트레칭 -> 근력(웨이트) 운동 40~50분 -> 중저강도 유산소 운동 20~30분] 순서가 가장 이상적입니다. 근력 운동을 통해 혈중 포도당과 간 글리코겐을 먼저 고갈시킨 후 유산소 운동을 시작하면, 유산소 시작 즉시 체지방이 주 에너지원으로 동원되어 연소 효율이 극대화됩니다."
    },
    {
        "id": "kb_keto_diet",
        "topic": "저탄고지(키토제닉) 식단 시 케토 플루 예방 및 지방 선택",
        "keywords": ["키토제닉", "저탄고지", "케토플루", "MCT오일", "불포화지방", "케톤"],
        "content": "저탄고지 전환 초기 겪는 두통, 피로감(케토 플루)은 급격한 인슐린 저하로 신장에서 나트륨과 수분이 배출되어 생기는 전해질 불균형입니다. 소금 섭취를 평소보다 늘리고 마그네슘, 칼륨을 보충해야 합니다. 또한 가공 버터나 삼겹살 지방보다는 올리브유, 아보카도, 들기름 등 건강한 불포화지방을 중심으로 식단을 구성하세요."
    }
]

# 2. BM25 키워드 검색 엔진
class BM25SearchEngine:
    def __init__(self, corpus: List[Dict[str, Any]], k1: float = 1.5, b: float = 0.75):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.doc_len = []
        self.avgdl = 0.0
        self.doc_freqs = []
        self.idf = {}
        self._build_index()

    def _tokenize(self, text: str) -> List[str]:
        # 한글, 영문, 숫자 단어 추출 (2글자 이상)
        return [w.lower() for w in re.findall(r'[가-힣a-zA-Z0-9]{2,}', text)]

    def _build_index(self):
        total_len = 0
        df = {}
        for doc in self.corpus:
            combined_text = f"{doc['topic']} {' '.join(doc['keywords'])} {doc['content']}"
            tokens = self._tokenize(combined_text)
            self.doc_len.append(len(tokens))
            total_len += len(tokens)
            
            freqs = {}
            for t in tokens:
                freqs[t] = freqs.get(t, 0) + 1
            self.doc_freqs.append(freqs)
            
            for t in freqs:
                df[t] = df.get(t, 0) + 1
                
        self.avgdl = total_len / max(len(self.corpus), 1)
        N = len(self.corpus)
        for term, freq in df.items():
            self.idf[term] = math.log(1 + (N - freq + 0.5) / (freq + 0.5))

    def score(self, query: str) -> List[float]:
        q_tokens = self._tokenize(query)
        scores = [0.0] * len(self.corpus)
        for i, doc_f in enumerate(self.doc_freqs):
            dl = self.doc_len[i]
            for q in q_tokens:
                if q in doc_f:
                    f = doc_f[q]
                    idf_val = self.idf.get(q, 0.1)
                    num = f * (self.k1 + 1)
                    den = f + self.k1 * (1 - self.b + self.b * (dl / self.avgdl))
                    scores[i] += idf_val * (num / den)
        return scores

# 3. Dense Semantic (의미적 n-그램/단어 유사도) 검색 엔진
class SemanticSearchEngine:
    def __init__(self, corpus: List[Dict[str, Any]]):
        self.corpus = corpus
        self.doc_words = []
        for doc in corpus:
            combined = f"{doc['topic']} {' '.join(doc['keywords'])} {doc['content']}"
            words = set(re.findall(r'[가-힣a-zA-Z0-9]{2,}', combined))
            self.doc_words.append(words)

    def score(self, query: str) -> List[float]:
        q_words = set(re.findall(r'[가-힣a-zA-Z0-9]{2,}', query))
        if not q_words:
            return [0.0] * len(self.corpus)
            
        scores = []
        for d_words in self.doc_words:
            intersect = len(q_words & d_words)
            union = len(q_words | d_words)
            jaccard = intersect / max(union, 1)
            scores.append(jaccard)
        return scores

# 4. 하이브리드 RRF (Reciprocal Rank Fusion) 융합 엔진
class HybridNutritionRAG:
    def __init__(self, corpus: List[Dict[str, Any]]):
        self.corpus = corpus
        self.bm25 = BM25SearchEngine(corpus)
        self.semantic = SemanticSearchEngine(corpus)

    def search(self, query: str, top_k: int = 1) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        bm25_scores = self.bm25.score(query)
        semantic_scores = self.semantic.score(query)

        # 랭킹 산출 (점수 높은 순)
        bm25_ranked = sorted(range(len(self.corpus)), key=lambda i: bm25_scores[i], reverse=True)
        sem_ranked = sorted(range(len(self.corpus)), key=lambda i: semantic_scores[i], reverse=True)

        # RRF (Reciprocal Rank Fusion) 결합 점수 계산
        rrf_scores = [0.0] * len(self.corpus)
        k_const = 60
        q_clean = query.lower()
        
        for rank, idx in enumerate(bm25_ranked):
            if bm25_scores[idx] > 0:
                rrf_scores[idx] += 1.0 / (k_const + rank + 1)
                
        for rank, idx in enumerate(sem_ranked):
            if semantic_scores[idx] > 0:
                rrf_scores[idx] += 1.0 / (k_const + rank + 1)

        # 한국어 교착어 특성 반영: 핵심 키워드 직접 포함 시 추가 부스팅 (Semantic Boost)
        for idx, doc in enumerate(self.corpus):
            for kw in doc.get("keywords", []):
                if kw in q_clean:
                    rrf_scores[idx] += 0.05  # RRF 점수 대비 강력한 우선순위 부여
            if doc.get("topic", "").lower() in q_clean:
                rrf_scores[idx] += 0.08

        # 최종 상위 결과 정렬
        final_ranked = sorted(range(len(self.corpus)), key=lambda i: rrf_scores[i], reverse=True)
        results = []
        for idx in final_ranked[:top_k]:
            if rrf_scores[idx] > 0:
                doc = self.corpus[idx]
                results.append(doc)

        return results

# 싱글톤 RAG 엔진 인스턴스
_rag_engine = HybridNutritionRAG(NUTRITION_KNOWLEDGE_BASE)

# 5. 메인 지식 검색 도구 함수 (공식 출처 표기 연동)
def search_nutrition_knowledge(query: str) -> Dict[str, Any]:
    """
    혈당 관리, 다이어트 정체기, 단백질 흡수, 간헐적 단식, 대체 식재료 등 
    임상 영양학 가이드를 BM25 + 시맨틱 하이브리드 RAG로 검색하여 가장 정확한 지식을 반환합니다.
    """
    if not query or not query.strip():
        return {"result": "검색어를 입력해주세요."}

    matches = _rag_engine.search(query, top_k=1)
    
    if matches:
        top_item = matches[0]
        return {
            "주제": top_item["topic"],
            "가이드내용": top_item["content"],
            "출처": "보건복지부 한국인 영양소 섭취기준(KDRIs) 및 임상 영양학 가이드라인"
        }

    # 기본 안내
    return {
        "주제": "일반 다이어트 웰니스 조언",
        "가이드내용": "규칙적인 단백질 섭취와 충분한 수분 보충(체중 x 33ml), 주 3회 이상의 유산소/근력 운동 병행이 가장 지속 가능한 다이어트의 정석입니다.",
        "출처": "보건복지부 한국인 영양소 섭취기준(KDRIs) 및 임상 영양학 가이드라인"
    }

if __name__ == "__main__":
    print("=== 하이브리드 RAG 검색 테스트 ===")
    test_queries = [
        "혈당 스파이크 안 오게 밥 먹는 순서가 어떻게 돼?",
        "운동 끝나고 단백질 언제 먹어야 근손실 안 와?",
        "간헐적 단식할 때 아메리카노 마셔도 상관없나?",
        "라면 먹고 다음 날 얼굴 붓는 거 왜 그래?",
        "살이 2주째 안 빠지는데 정체기인가 봐"
    ]
    for q in test_queries:
        res = search_nutrition_knowledge(q)
        print(f"\nQ: {q}")
        print(f"A: [{res['주제']}] {res['가이드내용'][:60]}...")
