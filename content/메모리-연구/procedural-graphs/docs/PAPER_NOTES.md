---
title: "Two-paper claim ledger"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/procedural-graphs-lab) · 원본 `docs/PAPER_NOTES.md` · 수집 2026-10-16 · 커밋 `2c265f7fb194627f1b39d90207e9dca03b6cee28`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# Two-paper claim ledger

Primary sources:

1. [Grounding Agent Memory: Environment-Probing Curation for Enterprise Agents](https://arxiv.org/html/2609.11060)
2. [Procedural Graphs: Self-Evolving Execution Structures for LLM Agents](https://arxiv.org/html/2609.09153v1)

이 문서는 논문 주장, 구현된 메커니즘, 아직 재현하지 않은 benchmark 주장을 구분한다.

## Grounded memory

| ID | 논문 메커니즘 | 레포 구현 | 검증 상태 |
|---|---|---|---|
| M1 | task trajectory를 별도 Distiller가 evidence로 압축 | `GroundedMemoryPipeline.distill` | 실제 LLM 실행 |
| M2 | Distiller는 memory writer가 아니며 grade/tool 접근이 없음 | distiller tool 없음, raw trajectory만 전달 | 경계 테스트 |
| M3 | 별도 Curator가 feedback과 related records를 보고 CRUD | `curate`, `MemoryStore` | 실제 LLM tool calls |
| M4 | curator-only read-only environment probing | `ServiceWorld.probe_*` | probe operation을 결과에 기록 |
| M5 | scoped reusable record contract | category, confidence, applies_to, lemma, provenance | schema 테스트 |
| M6 | grounded curation이 CLBench/APEX 성능을 개선 | 공식 CLBench independent adapter 1-run | grounded 62.5%, trajectory 17.5%; 논문 설정·통계는 미재현 |

Semantic memory는 task 답이나 ground-truth mapping을 미리 주입한 것이 아니다. 완료된 경험에서
post-task pipeline이 만든 persistent record이며, 다음 fresh task agent는 `memory_read`만 할 수
있다.

## Procedural Graph

| ID | 논문 메커니즘 | 레포 구현 | 검증 상태 |
|---|---|---|---|
| P1 | attributed procedure graph | `PGNode`, `PGEdge`, `PaperGraph` | 구조 테스트 |
| P2 | latest action locate, outgoing 2-hop, full-graph fallback | `GuidanceGenerator.generate` | 경계 테스트 + 실제 LLM 실행 |
| P3 | separate Guidance LLM과 full-trajectory Solver | `GuidanceGenerator`, `TaskAgent` | 실제 LLM 실행 |
| P4 | graph는 soft guidance이며 condition을 코드가 실행하지 않음 | local edges 전체를 LLM에 전달 | 입력 경계 테스트 |
| P5 | scored traces에서 LLM Refiner가 edit 제안 | `GraphRefiner.propose` | 실제 LLM proposal 1회 |
| P6 | copy-on-write, structural checks, held-out non-decrease gate | `apply_edits`, `validate`, `evolve_once` | 실제 validation rollout |
| P7 | rejection memory | `RejectionRecord` | malformed/regressive proposal 테스트 |
| P8 | 논문의 7개 benchmark 성능 및 expert/scratch graph 결과 | 원 논문 benchmark 결과 | **미재현** |

Solver의 one-action serialization은 선택한 모델의 불안정한 text ReAct 형식 때문에 native function
calling을 쓴다. 이는 solver가 보는 정보와 가능한 action은 바꾸지 않지만, 원 논문의 wire format과
완전히 동일하지 않은 구현 차이다.

## 결합 가설과 관찰

| ID | 가설 | 연결 방식 | 현재 관찰 |
|---|---|---|---|
| H1 | semantic fact와 procedural guidance가 상보적 | recalled records를 Guidance LLM semantic context로 전달 | 공식 CLBench 1-run에서 combined 37.5%, grounded 62.5%; 반증 방향 (위키 편집자 주: 이 수치는 [[메모리-연구/procedural-graphs/REVIEW|재현 후기]] 2026-09-22 정정에서 철회된 guidance interference 해석과 같은 실행에 기댄다. 최종 근거로 쓰지 않는다) |
| H2 | probing이 더 정확하고 compact한 memory를 만든다 | 같은 curator schema에 probe tool만 추가 | 공식 CLBench 1-run에서 grounded 62.5%, trajectory 17.5%; answer caching 혼입 |
| H3 | 두 external states가 같은 경험으로 self-improve할 수 있다 | task 후 memory curate, batch 후 PG refine | 실제 폐루프 1회 완료 |

### 공식 CLBench independent adapter 1-run

| condition | pass | total reward | SQL/question | reads |
|---|---:|---:|---:|---:|
| stateless | 30.0% | 3.8667 | 11.750 | 0 |
| trajectory_memory | 17.5% | 1.7333 | 13.375 | 40 |
| grounded_memory | 62.5% | 14.2668 | 7.200 | 40 |
| pg_only | 22.5% | 3.2667 | 9.775 | 0 |
| pg_grounded_memory | 37.5% | 7.0667 | 8.225 | 40 |

Memory 조건은 provider의 named-tool 편차를 제거하기 위해 solver 전에 원 질문 기반 recall을 한 번
수행하는 동일 adapter protocol을 쓴다. 이는 논문의 on-demand memory tool과 다르다. Grounded와
combined paired 결과는 both 12, combined-only 3, grounded-only 13, neither 12이므로 결합 시너지는
관찰되지 않았다. Curator가 일부 task-specific 숫자를 저장해 prompt contract를 위반한 사례도 있어,
grounded 62.5%를 순수한 procedural generalization으로 해석하지 않는다.

### 작은 로컬 6조건 live pilot

| condition | test success | mean environment tools | memory reads | records |
|---|---:|---:|---:|---:|
| stateless_react | 4/4 | 7.00 | 0 | 0 |
| trajectory_memory_only | 2/4 | 5.75 | 4 | 7 |
| grounded_memory_only | 3/4 | 8.25 | 0 | 4 |
| procedural_graph_only | 4/4 | 4.25 | 0 | 0 |
| pg_plus_trajectory_memory | 4/4 | 4.00 | 4 | 4 |
| pg_plus_grounded_memory | 4/4 | 4.25 | 4 | 1 |

`grounded_memory_only`의 3/4를 grounding 효과로 해석할 수 없다. test agent가 memory를 읽지 않았기
때문이다. 초기 레포의 0/12는 비대칭 oracle guidance 비교, 12.8%는 non-LLM simulator였으므로
모두 논문 검증 수치에서 제외한다.

### self-evolution live pilot

Initial validation은 4/4, candidate도 4/4였고 mean environment tools는 4.50에서 4.25로
감소했다. 논문의 non-decrease 규칙에 따라 candidate를 commit했고 unseen test는 4/4였다. 이는
mutation-to-gate 폐루프가 실행됐다는 증거이지, 작은 4-case world에서 일반적 개선을 입증한 것은
아니다.

## 재현 경계

현재 레포는 두 방법의 역할과 상태 전이를 재현하고 공식 CLBench task에서 independent adapter
1-run을 수행했다. 논문의 비공개 GHCP harness, GPT-5.4 five-run 설정과 APEX, HotpotQA,
MultiChallenge, GDPval, ALFWorld, tau-bench, BFCL, EnterpriseArena의 원 split, judge, 모델 조건과
headline 수치는 재현하지 않았다. 따라서 논문의 성능 주장을 검증하려면 동일 조건의 여러 paired
run과 significance test가 추가로 필요하다.

Raw artifacts:

- official CLBench aggregate report (`../results/clbench_summary.md`; 원 저장소의 파일 참조)
- six-condition live JSON (`../results/faithful_latest.json`; 원 저장소의 파일 참조)
- self-evolution live JSON (`../results/evolution_live.json`; 원 저장소의 파일 참조)
- [[메모리-연구/procedural-graphs/docs/REPRODUCTION_SPEC|paper-to-code mapping]]
