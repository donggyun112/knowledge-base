---
title: "Benchmark acquisition and evaluation protocol"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/procedural-graphs-lab) · 원본 `docs/BENCHMARK.md` · 수집 2026-10-16 · 커밋 `2c265f7fb194627f1b39d90207e9dca03b6cee28`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# Benchmark acquisition and evaluation protocol

## Grounding Agent Memory: CLBench

CLBench를 고른 이유는 기억이 낡는 상황을 직접 만들 수 있기 때문이다. 전반 20문항을 풀며 배운 DB 지식이, 스키마가 바뀐 후반 20문항에도 유효한지 시험한다. 정답률은 문제 해결 여부를, SQL 호출 수는 그 답에 도달하기 위해 얼마나 탐색했는지를 보여 준다. 적은 호출만으로 좋은 시스템이라고 할 수 없으므로 둘을 함께 기록한다.

Grounding 논문의 primary experiment에 맞춰 Continual Learning Bench의 공식
`database_exploration` task를 사용한다.

- upstream: https://github.com/pgasawa/continual-learning-bench
- local path: `benchmarks/continual-learning-bench`
- pinned commit: `5f8c50eb1e84b2eda2ef4faff757dfc812a0ea26`
- variant: `schema_drift`
- schedule: migration 전 20문항 + migration 후 20문항
- per-question exploratory query budget: 15

`make benchmark-setup`은 `products.db`, `products_drifted.db`, `questions.json`,
`questions_post_drift.json`을 공식 setup 경로로 받는다. 두 DB는 `PRAGMA quick_check`를 통과했고,
`clbench doctor database_exploration`의 required check도 통과했다. 대용량 DB는 upstream ignore 규칙을
따라 parent repository에 commit하지 않는다.

```bash
make benchmark-setup
make benchmark-check
make grounding-paper-live
```

### Grounding adapter

각 question은 fresh task-agent session이다. Task agent는 SQLite read-only action과
`memory_read`만 사용할 수 있다. Task 종료 뒤:

1. non-writing Distiller가 raw trajectory를 evidence packet으로 압축한다.
2. 별도 Curator가 terminal feedback과 nearby memory를 읽는다.
3. Grounded 조건의 Curator만 현재 stage DB를 `mode=ro`로 최대 네 번 probe할 수 있다.
4. Curator만 memory create/update/delete 권한을 가진다.

공개 appendix는 실제 run의 recall 호출 정책을 완전히 지정하지 않는다. Cheap OpenRouter provider가
named tool choice를 건너뛴 사례가 있어 canonical run은 solver 전에 question-only query로
`memory_read`를 정확히 한 번 강제한다. 이는 논문과의 명시적 편차이며 artifact의
`recall_policy=required`에 기록된다.

### APEX 경계

논문은 adapted APEX 90 tasks / 6 worlds를 보고하지만 정확한 task ordering, world adapter,
실험 harness artifact를 공개하지 않았다. 해당 ordering을 복원할 증거가 없으므로 임의 task를
APEX 재현이라고 부르지 않는다. 현재 공개적으로 검증 가능한 Grounding benchmark는 CLBench다.

## Procedural Graph: MultiChallenge

MultiChallenge는 앞 대화의 지시와 제약을 유지하며 답해야 하는 과제다. 여기서는 DB 사실을 기억하는 능력보다 ‘문맥 확인 → 제약 정리 → 답 검토’ 같은 실행 절차가 도움이 되는지 본다. train은 수정할 재료, validation은 수정안을 고르는 기준, test는 선택이 끝난 뒤의 평가다. 이 역할을 섞으면 그래프가 평가 문항에 맞춰져도 학습 효과처럼 보일 수 있다.

이 문서는 초기 저비용 subset 프로토콜을 기록한다. 이후 전체 100/100/56 분할과 텍스트 ReAct로 바꾼 실행은 [[메모리-연구/procedural-graphs/results/EXPERIMENT_REPORT_KO|종합 보고서]]에 따로 있다. 아래 required action 설정을 후속 실행에도 그대로 적용한 것으로 읽지 않는다.

PG 논문의 benchmark suite 중 public dataset과 criterion을 직접 확보할 수 있는
`ScaleAI/MultiChallenge`를 사용한다.

- source dataset: `ScaleAI/MultiChallenge`
- rows: 266
- local normalized JSONL:
  `benchmarks/multichallenge/benchmark_questions.jsonl`
- normalized JSONL SHA-256:
  `d0752d58164685227f05657fe1bb6245ddb17e5175016b3d3ff39e93e37e9c03`
- source parquet SHA-256:
  `2711646aba61f814823297714aaf757e3a1b71c66c501402231de48490650515`

논문 construction split의 크기 train 100 / validation 100 / test 56에 맞춰 전체 266개를
`sha256(paper-split-v1|question_id)`로 정렬한다. 논문이 실제 sampled IDs를 공개하지 않았으므로
동일한 크기와 disjointness를 재현하지만 동일 ID split이라고 주장하지 않는다.

비용 제한 canonical run은 각 pool의 앞 train 8 / validation 8 / test 16을 사용한다.

```bash
make pg-paper-subset
make pg-paper-audit
```

### PG adapter

- baseline과 PG 조건은 같은 cognitive tool catalog를 사용한다.
- 모델이 tool path를 생략하지 않도록 action tool choice를 required로 둔다.
- PG 조건은 마지막 action을 graph node에 정확히 매칭한다.
- 현재 node의 outgoing 2-hop subgraph 전체를 별도 Guidance LLM에 제공한다.
- Guidance는 soft prompt이며 Python이 edge condition을 실행하거나 next action을 선택하지 않는다.
- scratch graph refinement는 train traces만 사용한다.
- candidate는 structural validation과 별도 validation subset에서 점수가 비감소할 때만 commit한다.
- 마지막 test subset은 graph edit와 gate에서 보지 않는다.

PG 논문은 공식 implementation, prompt, sampled IDs, initial/expert graph checkpoint를 공개하지 않았다.
따라서 이 실행은 public-data mechanism replication이지 paper table의 exact score replica가 아니다.

## Combined 2×2 CLBench protocol

독립 검증 뒤 결합 효과는 하나의 task에서 다음 네 조건으로 잰다.

| condition | semantic memory | PG |
|---|---|---|
| `stateless` | 없음 | 없음 |
| `grounded_memory` | online curation | 없음 |
| `pg_only` | 없음 | query/answer PG |
| `pg_frozen_grounded_memory` | 동일 frozen schedule | query/answer PG |

Grounded condition이 질문 `i` 직전에 가진 전체 store를 `Mᵢ`로 저장한다. 결합 condition은 같은
질문에 정확히 같은 `Mᵢ`를 로드하고 memory write를 하지 않는다. Solver가 생성하는 `memory_read`
query는 기록하되 retrieval 결과는 Semantic-only의 질문별 recall schedule을 그대로 replay한다.
따라서 서로 다른 query 문구나 trajectory가 store/retrieval divergence를 만드는 것을 막는다.

실행 시간이 긴 두 신규 arm은 별도 output에서 병렬 수행한다. 병합기는 다음을 강제한다.

- benchmark/variant/question count/run/model/temperature/recall/retriever metadata 일치
- 두 arm에 재사용된 stateless와 grounded row의 완전 일치
- 네 condition을 한 번씩만 포함
- condition별 unique API cost 합산

최종 analyzer는 다음을 추가 검증한다.

- semantic와 combined의 40개 question index 일치
- 질문별 `memory_before`와 `recalled_memory` 완전 일치
- combined의 모든 curation write 차단
- PG-only/combined의 query-answer core edge 일치
- paired transition과 exact McNemar
- 2×2 factorial interaction

```bash
make combined-pg-arm
make combined-semantic-pg-arm
make combined-paper-merge
make combined-paper-audit
```

## Statistical interpretation

같은 문항을 두 조건으로 풀었을 때는 총점만큼 ‘어느 문항에서 승패가 바뀌었나’가 중요하다. paired 비교는 한쪽만 맞힌 문항들을 대응시켜 본다. 작은 표본에서 한두 문항 차이가 나거나 검정이 비유의하다는 결과는, 그 방법이 언제나 좋다거나 효과가 전혀 없다는 결론과 다르다.

Grounding paper는 GPT-5.4 기반 다섯 paired run을 사용한다. 현재 canonical CLBench 결과는 더 싼
DeepSeek 모델의 run index 0 한 번이다. PG run도 test 16개의 cost-controlled subset이다. 따라서
관측된 차이는 mechanism/debugging evidence로 보고하고, 신뢰구간이나 다중 seed 없이 일반적인
성능 우위로 해석하지 않는다.
