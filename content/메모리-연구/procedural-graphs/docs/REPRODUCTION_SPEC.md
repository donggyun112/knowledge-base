---
title: "Two-paper reproduction specification"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/procedural-graphs-lab) · 원본 `docs/REPRODUCTION_SPEC.md` · 수집 2026-10-16 · 커밋 `2c265f7fb194627f1b39d90207e9dca03b6cee28`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# Two-paper reproduction specification

Primary sources:

- [Grounding Agent Memory, arXiv:2609.11060](https://arxiv.org/html/2609.11060v1)
- [Procedural Graphs, arXiv:2609.09153](https://arxiv.org/html/2609.09153v1)

이 문서는 논문의 역할·정보 경계·학습 절차가 코드와 benchmark adapter에 어떻게 대응하는지
정의한다. Exact score replication과 공개 자료로 가능한 independent replication은 구분한다.

## Grounding Agent Memory mapping

| Paper mechanism | Required boundary | Implementation |
|---|---|---|
| Fresh task agent | environment action + read-only `memory_read`; no memory writes | `CLBenchCombinedSystem` |
| Raw trajectory | query, recall ids, action/observation, terminal feedback | per-question episode artifact |
| Non-writing Distiller | trajectory evidence only; no memory/environment write | `GroundedMemoryPipeline.distill` |
| Separate Curator | evidence, terminal feedback, nearby records | `GroundedMemoryPipeline.curate` |
| Record contract | category, confidence, scope, lemma, provenance | `MemoryRecord` |
| Exclusive write authority | Curator alone can create/update/delete | curator tool loop + `MemoryStore` |
| Environment grounding | current SQLite snapshot, read-only, maximum four probes | `CLBenchProbeEnvironment` |
| Retrieval | E5 query/passage embeddings and scoped ranking | `E5MemoryRetriever` |

Memory는 정답 dictionary로 초기화하지 않는다. 매 task가 끝난 뒤 실제 trajectory에서 Distiller와
Curator가 record를 만들고 다음 fresh task agent가 이를 읽는다. Grounded condition만 Curator가
현재 DB를 probe한다.

Canonical run은 cheap provider가 tool call을 생략하는 편차를 제거하기 위해 task 시작 시
`memory_read`를 한 번 강제한다. 논문의 on-demand tool surface와 동일하지 않으므로 결과 metadata와
보고서에 편차를 기록한다.

## Procedural Graph mapping

| Paper mechanism | Required boundary | Implementation |
|---|---|---|
| Directed attributed graph | node + relation/condition/guidance/pitfalls edge | `PaperGraph`, `PGNode`, `PGEdge` |
| Locate | most recent action exact-match, initial `Start` | `GuidanceGenerator.generate` |
| Extract | outgoing directed 2-hop neighborhood | `PaperGraph.local` |
| Generate | separate LLM reads query, recent trajectory, local graph | `GuidanceGenerator` |
| Solver | query, full trajectory, optional soft guidance | benchmark-specific agent loop |
| Soft guidance | graph never executes actions or evaluates conditions in Python | prompt boundary |
| Refiner | scored train traces + retained graph + rejection memory | `GraphRefiner.propose` |
| Candidate | copy-on-write edit + structural validation | `PaperGraph.apply_edits/validate` |
| Validation gate | commit iff held-out score is non-decreasing | `GraphRefiner.evolve_once` |
| Rejection memory | rejected edit and diagnostics retained | `RejectionRecord` |

MultiChallenge adapter는 baseline과 PG에 같은 cognitive action catalog를 제공한다. 모델이 곧바로
text answer를 내서 PG path를 우회하지 않도록 function action을 required로 둔다. 이는 action
serialization 제약이며 PG가 특정 next action을 강제하는 것은 아니다.

## Combined system

```text
fresh CLBench task
  ├─ question-only E5 recall → semantic record block ─────────┐
  └─ latest action → 2-hop PG → Guidance LLM advice ──────────┤
                                                               ▼
                                                one Solver context
                                                               │
                                                   SQL query / answer
                                                               │
                                                         environment

after task closure, semantic-only source condition
  trajectory → Distiller → Curator ↔ current read-only DB
                               │ exclusive CRUD
                               ▼
                         next-question store
```

Semantic record body는 Guidance LLM에 주지 않는다. Guidance LLM은 PG와 recent trajectory만 보고,
Solver가 semantic facts와 procedural advice를 함께 소비한다. Current SQL observation이 external
memory보다 우선한다.

## Factorial invariant

Semantic-only run이 질문 `i` 직전에 가진 store `Mᵢ`를 artifact에 기록한다. Combined run은 같은
질문에서 `Mᵢ`를 완전히 대체 로드하고 write를 비활성화한다.

```text
Semantic-only: Mᵢ → recall → solver → curator → Mᵢ₊₁
Combined:      Mᵢ → same recall → PG guidance + solver → no write
```

따라서 두 조건의 차이는 memory를 새로 학습한 결과가 아니라 같은 memory 위에 PG guidance가
추가된 효과다. PG-only와 Combined는 query/answer core graph를 공유한다. 최종 analyzer가 snapshot,
recall, no-write, graph-core 불변식을 모두 검사한다.

## Training/test separation

- Grounded semantic memory는 CLBench stream에서 이전 task 경험만 다음 task에 전달한다.
- PG self-evolution은 MultiChallenge train traces와 validation gate만 사용한다.
- MultiChallenge test는 graph edit에 사용하지 않는다.
- CLBench 결합 test stream을 보고 PG를 수정하지 않는다.
- 이전 synthetic/evolution pilot이나 invalid dual run은 canonical score에 합치지 않는다.

## Claim boundary

공개 CLBench와 MultiChallenge subset에서 논문 메커니즘을 실제 LLM으로 실행한다. 다만 원 모델,
다섯 seed, 정확한 MultiChallenge IDs/checkpoint/prompt, adapted APEX ordering이 모두 공개·재현된 것은
아니다. 따라서 결과는 cost-controlled independent replication이며 논문 표 수치의 exact
replication으로 표현하지 않는다.
