---
title: "Grounded semantic memory + procedural memory"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/procedural-graphs-lab) · 원본 `docs/DUAL_MEMORY.md` · 수집 2026-10-16 · 커밋 `2c265f7fb194627f1b39d90207e9dca03b6cee28`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# Grounded semantic memory + procedural memory

## 최종 결합 구조

이 문서의 질문은 ‘두 기억을 어떻게 함께 보여 줄까?’와 ‘함께 보여 준 효과를 어떻게 공정하게 잴까?’다. Semantic memory는 과거 작업에서 확인한 사실을, procedural graph는 지금 단계에서 취할 절차를 제공한다. 둘 중 하나가 맞더라도 현재 환경의 관찰과 충돌할 수 있으므로, 최종 행동은 최신 관찰까지 보는 Solver가 고른다.

여기의 ‘최종’은 이 동결 메모리 비교 프로토콜 안에서의 구조를 뜻한다. 그래프가 기억의 쓰기·조회까지 바꾸는 후속 확장은 [[메모리-연구/procedural-graphs/docs/COMBINED_DESIGN|재설계 문서]]의 별도 가설이다.

```text
                            fresh task agent
                                   │
                 ┌─────────────────┴─────────────────┐
                 ▼                                   ▼
       grounded semantic memory              procedural graph
       "무엇을 알고 있는가"                  "다음에 무엇을 할까"
                 │                                   │
       question-scoped recall              active action localization
       stage/provenance metadata            outgoing 2-hop subgraph
                 │                                   │
                 │                              Guidance LLM
                 └─────────────────┬─────────────────┘
                                   ▼
                                Solver
                                   ▼
                         action / observation
```

두 memory는 역할과 write lifecycle이 다르다.

- Semantic memory는 실행 환경에 관한 재사용 가능한 사실과 절차 lemma를 저장한다.
- Procedural memory는 action 사이의 condition, guidance, pitfalls를 graph edge에 저장한다.
- Task agent는 semantic memory를 읽을 수 있지만 쓸 수 없다.
- 별도 Curator만 task 종료 뒤 semantic CRUD를 수행한다.
- 별도 Guidance LLM만 localized PG를 자연어 실행 조언으로 바꾼다.
- Solver는 semantic recall, PG guidance, live trajectory를 함께 보고 다음 action을 선택한다.
- Live environment observation은 두 external memory보다 우선한다.

PG가 다음 action을 강제하거나 semantic fact를 변형하지 않는다. Semantic record는 Guidance LLM에
들어가지 않고 Solver context에서 별도 블록으로 유지된다.

## Fair factorial protocol

두 조건이 각자 기억을 만들게 두면, 한쪽이 우연히 잘못된 규칙을 저장한 것만으로 점수가 달라질 수 있다. 그러면 PG의 효과인지 기억 품질의 차이인지 알 수 없다. 그래서 Semantic-only와 Semantic+PG에 **질문마다 같은 기억과 같은 검색 결과를 주는 것**을 가장 중요한 비교 조건으로 삼는다. 여기서 frozen은 40문항 내내 하나의 고정 기억을 쓴다는 뜻이 아니다. Semantic-only가 질문마다 갱신한 기억을, 결합 조건이 같은 시점에 그대로 재생한다는 뜻이다.

```text
Grounded semantic-only stream
        │
        ├─ question 1 직전 store M₁
        ├─ question 2 직전 store M₂
        ├─ ...
        └─ question 40 직전 store M₄₀
                         │
                         ▼ exact replay
              PG + frozen grounded memory
```

Semantic+PG는 질문 `i`에서 정확히 `Mᵢ`를 로드한다. 자체 curation은 비활성화하므로 결합 trajectory가
semantic store를 갈라놓지 않는다. PG가 solver의 `memory_read` query 자체를 바꿀 수 있으므로 그
문구는 trajectory에 보존하되, retrieval 결과는 Semantic-only의 질문별 exact recall schedule을
replay한다. 따라서 recalled record 배열도 동일해야 한다.

최종 네 조건은 다음 2×2 설계다.

| | PG 없음 | PG 있음 |
|---|---|---|
| Semantic 없음 | `stateless` | `pg_only` |
| Semantic 있음 | `grounded_memory` | `pg_frozen_grounded_memory` |

아래 뺄셈은 모두 같은 문항에서의 점수를 비교한다. 특히 interaction은 결합 점수 자체가 아니다. 메모리가 있을 때의 PG 효과가 없을 때보다 얼마나 달라졌는지다. 이 값이 양수여도 결합이 baseline보다 좋다는 뜻은 아니므로 네 조건의 실제 점수를 함께 본다.

이를 통해 다음 효과를 분리한다.

- Semantic effect without PG = Semantic-only − Baseline
- PG effect without semantic = PG-only − Baseline
- PG effect with semantic = Combined − Semantic-only
- Interaction = Combined − Semantic-only − PG-only + Baseline

## Artifact invariants

`analyze_combined.py`는 최종 merged artifact에서 다음을 검사한다.

1. 모든 조건이 같은 question index 40개를 포함한다.
2. Semantic-only와 Combined의 `memory_before`가 질문별로 완전히 같다.
3. 두 조건의 `recalled_memory`가 질문별로 완전히 같다.
4. Combined의 모든 episode에서 `writes_disabled=true`다.
5. PG-only와 Combined의 query/answer core edge가 같다.

하나라도 실패하면 해당 결과를 결합 효과로 보고하지 않는다.

## 왜 예전 dual run은 제외하는가

과거 `dual_memory`는 sibling resolver 구조를 시험했지만 두 condition이 각자의 trajectory에서 semantic
store를 독립적으로 학습한 실행도 있었다. 그 비교에는 PG 효과와 semantic-store divergence가
섞였다. 이후 shared-memory run은 snapshot을 맞췄지만 현재와 다른 7-node state adapter를 사용했다.

현재 canonical 조건은 단순한 `pg_frozen_grounded_memory`다. Grounding run의 실제 snapshot을 그대로
replay하고 PG-only와 공통인 query/answer graph core만 더한다. 과거 dual 결과는 audit history로만
보존하며 최종 factorial 표에 포함하지 않는다.

## Evolution 경계

PG self-evolution은 MultiChallenge의 disjoint train/validation/test에서 독립 검증한다. CLBench
결합 test 40문항을 보고 graph를 수정하지 않는다. 이 원칙은 test leakage를 막지만, MultiChallenge에서
학습한 graph를 데이터베이스 action graph로 직접 이식한다는 뜻도 아니다. 결합 실험은 검증된 PG
메커니즘을 CLBench action vocabulary에 맞춘 attributed graph로 사용한다.
