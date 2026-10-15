---
title: "절차 그래프 재현 — 초기 README"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/procedural-graphs-lab) · 원본 `README.md` · 수집 2026-10-16 · 커밋 `2c265f7fb194627f1b39d90207e9dca03b6cee28`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# Grounded Memory × Procedural Graphs

두 논문의 agent 구조를 각각 원 benchmark에서 검증한 뒤 하나의 agent로 결합하는 재현 레포다.

- [Grounding Agent Memory](https://arxiv.org/html/2609.11060v1)
- [Procedural Graphs](https://arxiv.org/html/2609.09153v1)
- [[메모리-연구/procedural-graphs/results/EXPERIMENT_REPORT_KO|한국어 종합 보고서]]

## 현재 결과

Grounding 논문은 공식 CLBench `database_exploration/schema_drift` 40문항에서 독립 실행했다.

| condition | pass | SQL/question |
|---|---:|---:|
| Stateless | 11/40 (27.5%) | 11.800 |
| Trajectory memory | 10/40 (25.0%) | 11.175 |
| Grounded memory | 8/40 (20.0%) | 11.875 |

이 저비용 1-run에서는 논문의 memory 향상을 재현하지 못했다. 선택한 memory를 live DB evidence와
대조한 결과 unsupported generalization, terminal-answer 누출, 불완전한 lemma, 올바른 memory를
무시한 solver 오류가 모두 발견됐다.

PG 논문은 공개 MultiChallenge에서 deterministic train 8 / validation 8 / test 16 subset으로
독립 실행했다.

| condition | pass | mean solver steps |
|---|---:|---:|
| Unguided baseline | 5/16 (31.2%) | 3.938 |
| Expert PG | 6/16 (37.5%) | 5.125 |
| Scratch evolved PG | 6/16 (37.5%) | 5.063 |

PG가 한 문항 더 맞혔지만 paired McNemar `p=1.0`이다. Candidate graph는 validation 3/8 대
3/8 동률로 commit됐고 test에서 expert graph 이상의 추가 이득은 없었다.

최종 CLBench 2×2 factorial도 같은 40문항에서 완료했다.

```text
Baseline             = no semantic memory, no PG
Semantic-only        = online grounded memory Mᵢ
PG-only              = PG, no semantic memory
Semantic + PG        = PG + exact same frozen Mᵢ
```

| condition | pass | pre/post drift | SQL/question |
|---|---:|---:|---:|
| Baseline | 11/40 (27.5%) | 30.0% / 25.0% | 11.800 |
| Semantic-only | 8/40 (20.0%) | 10.0% / 30.0% | 11.875 |
| PG-only | 9/40 (22.5%) | 20.0% / 25.0% | 9.800 |
| Semantic + PG | 11/40 (27.5%) | 10.0% / 45.0% | 10.700 |

Semantic+PG는 Semantic-only가 질문 `i` 직전에 가진 store와 실제 recalled record를 그대로 replay하며
자체 memory write를 하지 않는다. Snapshot, recall, graph core, write-disable 검사는 모두 통과했다.
관측된 factorial interaction은 `+12.5%p`였지만 Semantic-only 대비 paired McNemar는 `p=0.453`,
baseline 대비 정확도는 동률이다. 따라서 결합의 상호보완 신호는 있으나 성능 향상이 입증됐다고
말할 수는 없다.

## 구조

```text
                       fresh task agent
                              │
           ┌──────────────────┴──────────────────┐
           │                                     │
    memory_read only                    active action localization
           │                                     │
  grounded semantic records               outgoing 2-hop PG
           │                                     │
           │                                Guidance LLM
           └──────────────────┬──────────────────┘
                              │
                         Solver action
                              │
                          Environment

task complete                           offline graph refinement
      │                                           │
Distiller → Curator ↔ read-only probe       train trajectories
                 │                                │
           exclusive CRUD                    LLM ΔG proposal
                                                  │
                                    structural + validation gate
```

Python은 PG edge condition을 실행해 다음 action을 강제하지 않는다. 별도 Guidance LLM이 현재
node의 2-hop subgraph를 자연어 조언으로 만들고 Solver가 다음 action을 선택한다. Semantic memory는
task agent가 직접 쓰지 못하며 별도 Curator만 CRUD 권한을 가진다.

## 재현 경계

- Grounding 논문: primary 모델은 GPT-5.4, 다섯 paired run이다. 이 레포의 완료 run은 OpenRouter
  DeepSeek, run index 0 한 번이며 provider 편차를 막기 위해 pre-solver recall을 강제했다.
- Adapted APEX의 정확한 90-task ordering과 adapter는 공개되지 않아 APEX라고 가장한 대체 실험을
  만들지 않았다.
- PG 논문의 공식 코드, sampled IDs, graph checkpoint, prompt는 공개되지 않았다. MultiChallenge
  공개 266개와 criterion은 사용했지만 split 내부 ID는 SHA-256 정렬로 재구성했다.
- 작은 subset과 한 run으로 논문의 최종 성능 수치를 재현했다고 주장하지 않는다.

자세한 데이터 출처는 [[메모리-연구/procedural-graphs/docs/BENCHMARK|benchmark notes]], 논문-코드 대응은
[[메모리-연구/procedural-graphs/docs/REPRODUCTION_SPEC|reproduction specification]], 결합 경계는
[[메모리-연구/procedural-graphs/docs/DUAL_MEMORY|dual-memory design]]에 있다.

## 실행

OpenRouter key는 `[로컬 경로 생략]`에서 읽으며 artifact에 저장하지 않는다.

```bash
make benchmark-setup
make benchmark-check
make grounding-paper-live
make pg-paper-subset
make pg-paper-audit
make combined-pg-arm
make combined-semantic-pg-arm
make combined-paper-merge
make combined-paper-audit
make test
```

## 주요 artifact

```text
results/
  grounding-paper/run-0/
    clbench_latest.json
    memory_audit.md
    memory_support_audit.md
  pg-paper/subset-0/
    multichallenge_pg_latest.json
    paired_audit.md
  combined-paper/
    run-0/                 # PG-only arm
    combined-arm-0/        # frozen semantic + PG arm
    factorial-run-0/       # merged final artifact + fairness audit
```

과거 synthetic, independent-store dual, unforced-action smoke artifact는 삭제하지 않았지만 현재 성능
결론에는 사용하지 않는다.
