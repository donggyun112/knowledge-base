---
title: "결합 모델 재설계: 공진화하는 절차 귀속 메모리"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/procedural-graphs-lab) · 원본 `docs/COMBINED_DESIGN.md` · 수집 2026-10-16 · 커밋 `2c265f7fb194627f1b39d90207e9dca03b6cee28`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# 결합 모델 재설계: 공진화하는 절차 귀속 메모리

작성일: 2026-09-19 (v2)
상태: 설계안. 1~4단계 구현 완료, 5단계 이후 미구현.

## 0. v1에서 무엇이 틀렸나

v1은 **메모리만 그래프에 귀속**시키고 그래프는 고정이라고 암묵적으로 가정했다. 두 가지가
사실과 달랐다.

1. **CLBench 경로에는 그래프 진화가 아예 없다.** `clbench_eval.py`는 `database_graph()`로
   고정 그래프를 만들고 구조 검증만 한다. `graph_validation.heldout_score`가 `None`으로
   박혀 있는 것이 그 증거다. `GraphRefiner`는 임포트조차 되지 않는다. 진화는
   `multichallenge_pg_eval.py`와 `evolution_live.py`에만 있다.
   → v1 §3.4 "레코드와 그래프 편집을 같은 게이트로 커밋"은 성립 불가능한 전제였다.

2. **메모리는 이미 진화하고 있다.** 큐레이터가 에피소드마다 create/update/delete를 수행한다.
   즉 결합 시스템에서 **양쪽 다 진화하며, 서로 다른 시계와 게이트로 움직인다.**

| | 주기 | 게이트 | 현재 CLBench |
|---|---|---|---|
| 메모리 | 에피소드마다 (40×) | probe 기반 사실 검증 | ✅ 동작 |
| 그래프 | stride마다 (2×) | held-out 점수 | ❌ 없음 (고정) |

메모리가 20배 빠르다. 이 비대칭이 아래 §3의 고아 문제를 만든다.

## 1. 왜 다시 설계하는가

기존 결합 조건 `pg_frozen_grounded_memory`의 2×2 factorial
(`results/combined-paper/factorial-v3/`, 40문항, `deepseek/deepseek-v4.1-flash`):

| | PG 없음 | PG 있음 | PG 효과 |
|---|---:|---:|---:|
| memory 없음 | 30.0% | 25.0% | −5.0%p |
| memory 있음 | 60.0% | 62.5% | +2.5%p |
| | | | interaction **+7.5%p** |

> memory 없음 행은 factorial-v2 재사용(`stateless`/`pg_only`는 큐레이터를 타지 않는다).
> memory 있음 행은 큐레이터 truncation 버그를 고친 뒤 재측정한 값이다. `max_tokens=450`에
> 응답이 잘리면 tool_call이 없어 루프가 "의도적 종료"로 읽고 아무것도 커밋하지 않았고,
> 궤적이 긴 PG arm이 더 자주 잘려서 PG만 손해 보는 것처럼 보였다. 버그 아래의 옛 수치는
> 62.5% / 57.5% → interaction −0.0%p였다. **옛 2×2는 폐기.**
>
> 다만 +2.5%p는 40문항에서 1문항이고, 호출당 정확도로는 PG가 진다(1.02‰ vs 0.72‰).
> 단일 스트림 40문항으로는 노이즈와 구분되지 않는다.

interaction이 버그 아래에서 정확히 0이었던 것은 방법의 성질이 아니라 설계의 산물이다.
결합점이 단 하나이고 단방향이었다.

```
MemoryStore ──(recalled 레코드)──> Guidance LLM
```

실측상 이 통로는 흐른다(guidance 394건 중 120건이 `mem-` ID 인용). 그러나 recall 쿼리가
질문에 고정되어 그래프가 "무엇을 조회할지" 지휘하지 못했고, 쓰기 경로가 없었으며, 그래프가
진화하지 않았다.

**핵심 인식: 상호작용은 읽기가 아니라 쓰기에서 만들어진다.** 큐레이터가 그래프를 모른 채
레코드를 쓰고 PG가 그걸 읽기만 하면, 두 축은 쓰기 시점에 만난 적이 없다.

## 2. 논문이 정한 경계 (본문에서 확인)

### Grounding (arXiv:2609.11060)

> "The agent has **no memory create, update, or delete tool**, so it cannot change shared
> memory during task execution."
>
> 큐레이터가 "the **only** agent allowed to mutate ℳ."

- 솔버: `memory_read`만. 쓰기 도구 없음.
- 큐레이터: 4개 도구. 답 제출 후 비동기 기동. **propose–probe–commit** (evidential support,
  transfer value, scope, actionability, current validity, redundancy 검사).
- 금지 이유: task-time 변경이 다음 task로 새는 것을 막고 probe를 응답 경로에서 분리.

### Procedural Graph (arXiv:2609.09153)

- `gt = Ψ(𝒢t, q, 𝒯t−w:t)` — 2-hop 부분그래프, 전체 초기 지시 `q`, 최근 w=3 스텝.
- soft guidance. 코드가 조건을 판정하거나 액션을 실행하지 않는다.
- 편집: refiner 제안 → 구조 검증 → held-out 비감소 시 커밋. 거절은 `ℋrejected`에 축적.

## 3. 설계: 공진화 (co-evolution)

### 3.1 한 줄 요약

**솔버는 쓰지 않는다. 전이 시점에 표식만 남긴다. 큐레이터가 사후에 표식을 읽어 레코드를 엣지에
귀속시킨다. 그래프는 별도 주기로 진화하되, anchor 밀도를 편집 근거로 받는다.**

두 방향이 모두 열린다.

```
그래프 → 메모리 : active node가 recall 범위를 결정        [1~4단계 구현 완료]
메모리 → 그래프 : anchor 밀도가 편집 제안의 근거           [6단계 미구현]
```

### 3.2 실행 중 (구현 완료)

```
active node 결정 (직전 액션 exact match)
   ↓
2-hop 부분그래프 + 해당 노드에 귀속된 레코드 조회   ← 그래프가 recall을 지휘
   ↓
Guidance LLM(부분그래프, q, 최근 3스텝, 귀속 레코드)
   ↓
Solver(전체 궤적 + guidance + 조회된 레코드)
   ↓
액션 실행 → 전이 완료 시 learning_marker 기록 (쓰기 아님, 궤적 주석)
```

`learning_marker`: `{edge: [source, target], observation_ref, claim, instance_index}`.
솔버 도구에 **선택적** `learned` 필드를 추가해 수집한다. `required`에 넣지 않으므로 침묵하는
솔버도 유효하고 액션 공간은 바뀌지 않는다.

**localization 실패 시 전역 레코드로 degrade한다.** 조회 결과가 0이 되지 않는다.

### 3.3 에피소드 종료 후 (구현 완료)

```
terminal feedback → Distiller(궤적 + <transition_markers>) → evidence packet
                 → Curator: propose → probe(≤4) → commit, anchor 부여
```

Distiller 프롬프트가 `edge[source->target]: claim` 형식으로 귀속을 보존하도록 지시한다.
레코드 스키마에 `anchor_edges` / `anchor_nodes`가 추가되며, **비면 전역 레코드**다. 기존
레코드는 전부 전역으로 로드된다.

anchor는 **선택적**이다. 어디서나 성립하는 lemma는 전역으로 둔다.

### 3.4 그래프 진화 이식 (미구현)

CLBench에 `GraphRefiner`를 연결한다. held-out 확보 방법:

| 방법 | 장점 | 단점 |
|---|---|---|
| `run_index` 분리 (0=학습, 1=검증, 2=test) | 각 run이 완전한 40문항 스트림, drift 경계 보존 | 같은 문항 풀 — 문항 과적합은 못 거름 |
| 다른 task 계열로 검증 | 문항 완전 분리 | 계열 간 절차 전이가 성립하는지 자체가 가정 |

`run_index`는 `pre_shuffled + post_shuffled`로 섞으므로 **drift 구조가 유지된다**. 40문항을
train/val/test로 쪼개는 안은 각 13문항이 되고 순서 구조가 깨지므로 채택하지 않는다.

### 3.5 고아 anchor 처리 (미구현 — 현재 코드의 결함)

그래프가 진화하면 레코드가 anchor한 엣지가 삭제될 수 있다. 현재 구현은 `anchored_at()`이
영원히 매칭되지 않아 **레코드가 조용히 조회 불가 상태가 된다.** 삭제도 아니고 전역도 아닌
유령 상태다.

정책을 정해야 한다.

| 정책 | 동작 | 위험 |
|---|---|---|
| 전역 승격 | anchor를 비워 전역 레코드로 | 범위를 잃어 무관한 문항에 끼어듦 |
| 최근접 엣지로 재귀속 | 삭제된 엣지의 source 노드가 남아 있으면 node anchor로 강등 | 의미가 어긋날 수 있음 |
| 폐기 후보로 표시 | 다음 큐레이션에서 재검토 | 그 사이 조회 불가 |

**권고: 최근접 강등 → 실패 시 전역 승격.** source 노드가 살아 있으면 `anchor_nodes`로
낮추고, 노드마저 사라졌으면 전역으로 올린다. 둘 다 아티팩트에 기록해 사후 감사 가능하게 한다.

**그래프 편집 시점에 일괄 수행**한다. 편집이 커밋될 때만 엣지가 사라지므로 그 순간이 유일한
정합 지점이다.

### 3.6 역방향 통로: anchor 밀도 (미구현 — 진짜 결합)

엣지에 레코드가 많이 쌓였다는 것은 **그 전이가 실제로 지식을 요구한다**는 신호다. 반대로
레코드가 하나도 붙지 않은 엣지는 절차상 자리만 차지할 수 있다.

refiner 프롬프트에 엣지별 anchor 통계를 투입한다.

```
edge_stats = [
  {"edge": ["inspect_schema","database_query"], "anchored_records": 7, "total_reads": 31},
  {"edge": ["draft_answer","database_answer"],  "anchored_records": 0, "total_reads": 0},
]
```

refiner는 이를 근거로 밀도 높은 전이를 세분화하거나, 죽은 전이를 제거하는 편집을 제안할 수
있다. **이 통로가 열려야 메모리가 그래프를 바꾼다.** 이것이 v1에 없던 부분이며 결합의 본체다.

### 3.7 두 축이 맞물리는 지점 종합

| 결합점 | 방향 | 상태 |
|---|---|---|
| active node가 recall 범위를 결정 | 그래프 → 메모리 | ✅ 구현 |
| 전이 표식이 큐레이션 입력이 됨 | 그래프 → 메모리 | ✅ 구현 |
| 귀속 레코드가 guidance에 주입 | 메모리 → 그래프 | ✅ 기존 |
| anchor 밀도가 편집 제안 근거 | 메모리 → 그래프 | ❌ 6단계 |
| 엣지 삭제 시 고아 재배치 | 양방향 정합 | ❌ 5단계 |

## 4. 비교 설계

레코드가 그래프 위치에 귀속되면 semantic-only는 같은 레코드를 가질 수 없다. "동일 메모리 +
PG만 추가"라는 기존 공정성 불변식은 성립하지 않는다. **예산 정합**으로 바꾼다.

| 조건 | semantic | PG | 그래프 진화 |
|---|---|---|---|
| Baseline | ✗ | ✗ | — |
| Semantic-only | ✓ (전역) | ✗ | — |
| PG-only | ✗ | ✓ | ✓ |
| **Co-evolving combined** | ✓ (귀속) | ✓ | ✓ |

맞출 것: 문항 순서(`run_index`), SQL 예산(15), probe 예산(4), **총 LLM 호출 예산**. 후자가
핵심이다. PG는 guidance LLM 때문에 호출이 2배이므로 맞추지 않으면 "많이 호출해서 이겼다"와
"구조 때문에 이겼다"를 구분할 수 없다.

보고: 정확도, 평균 SQL, **정확도/총 호출**, paired McNemar.

## 5. 검증 계획 (실행 전 통과 필수)

| 불변식 | 확인 방법 | 상태 |
|---|---|---|
| 솔버가 메모리를 바꾸지 않음 | 에피소드 전후 store 해시 동일 | 미구현 |
| 전이 표식이 실제 생성됨 | 에피소드당 marker ≥ 1, edge가 실제 그래프 엣지 | 미구현 |
| 표식이 distiller를 통과해 보존됨 | packet에 `edge[...]` 문자열 존재 | 미구현 |
| anchor가 부여됨 | 커밋 레코드 중 `anchor_edges` 비지 않은 비율 > 0 | 미구현 |
| **그래프가 recall을 지휘함** | 같은 질문·다른 active node에서 조회 결과 상이 | ✅ 단위 테스트 |
| 고아가 발생하지 않음 | 편집 커밋 후 조회 불가 레코드 0건 | 미구현 |
| 예산 정합 | 조건별 총 LLM 호출 편차 < 10% | 미구현 |

기존 게이트(`verify_paper_contract.py`, `check_combined_smoke.py`)에 추가한다.

## 6. 알려진 위험

**anchor 과적합.** 특정 엣지에 묶인 레코드는 그 절차를 지나지 않는 문항에서 조회되지 않는다.
완화: 전역 레코드 허용, 큐레이터가 전역/귀속을 선택.

**두 진화의 시계 차이.** 메모리는 40회, 그래프는 2회 갱신된다. stride 한 번 도는 동안 쌓인
레코드가 전제한 엣지가 stride 끝에 사라질 수 있다. §3.5가 이를 다룬다.

**held-out의 약함.** `run_index` 분리는 문항 풀이 같아 문항 과적합을 거르지 못한다. 순서
의존적 절차 지식만 분리된다.

**비용.** 진화 라운드마다 validation 40문항 전체를 돌아야 한다. CLBench는 문항당 최대 15 SQL에
probe까지 붙어 MultiChallenge보다 비싸다. 라운드 수를 예산에 맞춰 제한해야 한다.

**논문 이탈.** anchor, 전이 표식, anchor 밀도 피드백은 두 논문 어디에도 없다. **재현이 아니라
확장**이며 보고서에서 재현 결과와 분리해 기술한다.

## 7. 구현 순서

1. ✅ `learning_marker` 기록 (솔버 루프, 쓰기 없음)
2. ✅ distiller가 표식 보존
3. ✅ 레코드 `anchor_edges` / `anchor_nodes` + 레거시 호환
4. ✅ anchor 기반 recall (active node → 조회 범위)
5. ⬜ CLBench에 그래프 진화 이식 (`run_index` held-out) + 고아 anchor 재배치
6. ⬜ anchor 밀도를 refiner 입력으로 투입 (역방향 통로)
7. ⬜ 예산 정합 계측 + 게이트 확장
8. ⬜ 게이트 전체 통과 확인 후에만 본 실행
