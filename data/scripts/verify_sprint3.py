import sys
import os
import time
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import app_tools.food_db as fdb
import app_tools.nutrition_rag as rag
import app_tools.exercise_tool as ex

print("=== Sprint 3 Full Verification Suite ===")

# 1. FTS5 Search Benchmark
test_queries = ["김치찌개", "닭가슴살", "바나나", "삼겹살", "비빔밥"]
latencies = []
print("\n[1] FTS5 Food DB Latency Test:")
for q in test_queries:
    t0 = time.perf_counter()
    res = fdb.search_food_nutrition(q)
    t1 = time.perf_counter()
    dt = (t1 - t0) * 1000
    latencies.append(dt)
    print(f"  - '{q}' -> '{res.get('식품명')}' ({res.get('칼로리(kcal)')} kcal) | {dt:.2f} ms | Source: {res.get('출처')[:15]}...")

avg_latency = sum(latencies) / len(latencies)
print(f"  => Average FTS5 Query Latency: {avg_latency:.2f} ms")

# 2. Smart Fallback Test (Unregistered Food)
print("\n[2] Smart Fallback Test (Unregistered Item):")
res_fallback = fdb.search_food_nutrition("마법의우주괴물된장찌개뚝배기")
is_fallback = res_fallback.get("is_fallback")
inferred_cat = res_fallback.get("추정카테고리")
print(f"  - Query: '마법의우주괴물된장찌개뚝배기'")
print(f"  - is_fallback: {is_fallback}")
print(f"  - Inferred Category: {inferred_cat}")
print(f"  - Estimated Calories: {res_fallback.get('칼로리(kcal)')} kcal")

# 3. Hybrid RAG Test
print("\n[3] Hybrid RAG (BM25 + Semantic + RRF) Test:")
rag_queries = [
    ("간헐적 단식할 때 블랙커피 마셔도 돼?", "간헐적 단식"),
    ("살이 갑자기 안 빠져서 정체기 온 것 같아", "정체기"),
    ("밤에 너무 배고픈데 야식 참는 법 있어?", "가짜 배고픔"),
    ("술 마실 때 살 덜 찌는 안주 추천해줘", "음주")
]

all_rag_passed = True
for user_q, expected_keyword in rag_queries:
    rag_res = rag.search_nutrition_knowledge(user_q)
    topic = rag_res.get("주제", "")
    passed = expected_keyword in topic or expected_keyword in rag_res.get("내용", "")
    if not passed:
        all_rag_passed = False
    print(f"  - Q: '{user_q}'")
    print(f"    -> Matched Topic: [{topic}] (Success: {passed})")

# 4. Exercise Tool Citation
print("\n[4] Exercise Tool Citation:")
ex_res = ex.calculate_exercise_calories("러닝", 40, 70)
print(f"  - Exercise: {ex_res.get('운동명')} {ex_res.get('운동시간(분)')}분 -> {ex_res.get('소모칼로리(kcal)')} kcal | Source: {ex_res.get('출처')}")

print("\n" + "="*40)
if avg_latency < 10 and is_fallback and all_rag_passed:
    print("🎉 ALL SPRINT 3 VERIFICATIONS PASSED SUCCESSFULLY!")
else:
    print("⚠️ Some checks did not pass as expected.")
print("="*40)
