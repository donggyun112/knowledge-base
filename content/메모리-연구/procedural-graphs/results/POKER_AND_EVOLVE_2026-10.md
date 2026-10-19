---
title: "포커 포트와 그래프 진화 추가 실행 — 2026-10"
tags:
  - memory-research
  - procedural-graphs
---

> [!info] 범위
> 원 저장소 [procedural-graphs-lab](https://github.com/donggyun112/procedural-graphs-lab) 수집 커밋 `2c265f7` 이후의 로컬 상태를 2026-10-18에 재집계한 기록이다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽는다. 초기 보고서 이후의 로컬 실행 폴더(`results/poker`, `results/mt-evolve-v2-agg`)를 읽은 기록이다. 결합모델의 입증 결과가 아니다. 기존 [[메모리-연구/procedural-graphs/results/EXPERIMENT_REPORT_KO|종합 보고서]] 수치와 합산하지 않는다.

## 왜 포커인가

CLBench `database_exploration`에서 관찰한 정확도만으로는 절차 그래프의 추가 기여가 분명하지 않았다. `exploitable_poker` 어댑터는 베팅 행동 선택과 상대에 대한 기억을 함께 살펴보는 후속 과제다. 이번 15개 결과 파일은 모두 120 hands, `loose_aggressive`, `schedule_id=default`를 기록한다. 이 집계만으로 상대 유형 전환에 대한 적응을 측정했다고 해석하지 않는다.

## 포커 결과

이 표에서 bb/hand는 한 판당 얻거나 잃은 칩을 큰 블라인드(big blind) 단위로 나타낸 값이다. 높을수록 좋지만, 같은 조건도 받은 패와 진행에 따라 흔들릴 수 있다. 따라서 평균 순위뿐 아니라 오른쪽의 세 실행 값을 함께 본다.

비교는 두 단계로 읽는다. 먼저 memory와 stateless를 비교해 상대를 기억하는 것 자체가 도움이 됐는지 본다. 그다음 memory + PG와 memory를 비교해 절차 안내의 추가 이득을 본다. 결합이 memory를 이겨도 stateless보다 낮다면, ‘아무 장치 없이 하는 것보다 나아졌다’는 결론은 나오지 않는다. `graph prompt`와 PG를 쓴 결합은 표에 별도 조건으로 남겨 두었으며, 이름만으로 두 구현을 같다고 가정하지 않는다.

- 기록된 요청 모델: `~deepseek/deepseek-v4-flash-latest`, 상대 loose-aggressive, 조건당 3회, 지표는 bb/hand. 가변 alias이므로 현재 같은 이름이 같은 모델 버전을 뜻한다고 보장하지 않는다.

| 조건 | 평균 | 3회 값 |
|---|---:|---|
| stateless | +1.21 | 1.40, 1.14, 1.08 |
| memory + PG (결합) | +0.85 | 1.45, 0.60, 0.51 |
| graph prompt | +0.60 | 1.34, 0.23, 0.24 |
| memory | +0.22 | −0.19, 0.69, 0.16 |
| graph prompt + memory | +0.18 | −0.95, 1.99, −0.51 |

읽는 법:

- 결합은 memory 단독보다 평균이 약 +0.63 높다. 조건당 3회라는 작은 표본이며 유의성 검정을 하지 않았다. 이 차이를 효과 입증이나 노이즈 판정으로 단정하지 않는다.
- 메모리가 붙은 조건은 모두 stateless보다 낮다. 이 과제에서 메모리가 이득이라는 근거는 없다.
- 결합이 stateless를 넘지 못했으므로 결합모델이 입증됐다고 쓸 수 없다.

## 그래프 진화 단일 실행

포커 표와 달리 여기서는 다시 DB 탐색 과제로 돌아온다. 질문도 바뀐다. ‘PG를 붙일까?’가 아니라 **‘이미 메모리와 PG를 함께 쓰는 상태에서, 그래프를 경험으로 고치면 더 나아질까?’**다. 따라서 비교 상대는 메모리 없는 에이전트가 아니라 고정 그래프를 쓰는 에이전트다.

2026-10-17 21:43 KST에 저장된 `mt-evolve-v2-agg` 최종 파일을 10월 18일 다시 확인했다. `database_exploration/schema_drift`, 요청 모델 `deepseek/deepseek-v4.1-flash`, `multiturn-v1`, solver reasoning `medium`, required recall, `e5` retriever 조건이다. Refiner는 `claude-cli:opus`, reasoning `medium`이다.

| 조건 | 정답 | normalized score | 평균 SQL 수 | 전반 정확도 | 후반 정확도 |
|---|---:|---:|---:|---:|---:|
| fixed_pg | 26/40 (65%) | 0.4333 | 5.600 | 60% | 70% |
| evolved_pg | 34/40 (85%) | 0.6067 | 4.675 | 95% | 75% |

두 조건 모두 메모리와 PG를 쓴다. 이 표는 PG 유무가 아니라 고정 그래프와 수정 그래프의 비교다. 해당 실행에서는 정확도가 20pt 높고 SQL 수도 적었지만 조건당 1회다. 반복 실험의 분산이나 유의성을 확인하지 않았으므로 일반적인 개선으로 결론 내리지 않는다. 전반·후반 차이만으로 난이도 차이, 과적합 또는 학습 효과의 원인을 특정할 수도 없다.

메타데이터에는 train index 0, validation indices `[1, 6]`, test index 3, stride 5가 기록돼 있다. 학습 자료는 기존 `mt-evolve-v2`와 `mt-guided-idx2-{a,b,c}`의 pass 네 개를 재사용했다. 따라서 **val/test 구분 자체는 확인됐다.** 다만 index가 다르다는 사실만으로 문항·DB·trajectory 간 독립성이나 누출 부재가 입증되지는 않는다.

체크포인트는 두 후보 평가를 기록한다. 첫 후보는 validation 평균 score 0.5675로 채택됐다. 다음 후보는 score 0.6150으로 높았지만 후반 정확도가 평균 7.5pt 낮아져 허용치 5pt를 넘었다는 drift guard 진단으로 기각됐다. 최종 test는 채택된 그래프를 대상으로 한다. score만 높이는 편집과 schema drift 이후 성능을 함께 보는 편집 선택이 다를 수 있음을 보여주는 실행 기록이다.

## 같은 계열의 반복 실행과 비교

앞의 85%가 한 번의 실행에만 나온 것인지 판단하려면 반복 결과가 필요하다. 아래 실행군은 그 판단에 참고할 수 있지만 동일한 반복 실험은 아니다. 여기서는 memory 단독과 미리 준비된 guided PG의 차이를 보며, 각 실행 안에서 그래프를 새로 진화시키지 않았다. 이 구분을 지켜야 ‘안내를 사용하는 효과’와 ‘안내를 학습한 효과’를 섞지 않는다.

`mt-memonly-idx{1,2}-{a,b,c}`와 `mt-guided-idx{1,2}-{a,b,c}`의 완료된 최종 파일도 재집계했다. 모두 요청 모델 `deepseek/deepseek-v4.1-flash`, reasoning `medium`, 40문항, stride 10, required recall, `e5` 조건이다. 아래는 각 stream에서 세 실행의 산술평균이다. guided는 각 파일의 `evolved_pg`, memory는 `fixed_pg` 행을 사용하되, 실제 조건 플래그로 PG 유무를 구분했다. 이름만으로 조건을 판단하면 안 된다.

| stream index | 조건 | 실행 수 | 평균 정확도 | 평균 SQL 수 | 평균 score |
|---|---|---:|---:|---:|---:|
| 1 | memory | 3 | 77.50% | 7.258 | 0.4411 |
| 1 | memory + guided PG | 3 | 79.17% | 5.533 | 0.5222 |
| 2 | memory | 3 | 70.00% | 6.658 | 0.4156 |
| 2 | memory + guided PG | 3 | 77.50% | 5.600 | 0.5167 |

이 조건에서는 정확도 차이보다 SQL 호출 수 감소가 두 stream에서 일관되게 관찰된다. 정확도 차이는 stream마다 다르며 유의성 검정은 하지 않았다. 이 guided 실행은 `generations_requested=0`이므로 evolved라는 행 이름이 있어도 각 실행 안에서 새로운 진화를 수행한 결과가 아니다. `mt-evolve-v2-agg`와는 stride와 비교 대상이 달라 같은 반복군으로 합산하지 않는다.

`e0731-*`는 2026-10-18 확인 시점에는 checkpoint 파일만 있었다. 이후 `deepseek-v4-flash-0731`로 2×2 네 조건을 stream 1에서 처음부터 3회씩 다시 돌렸다. 그 결과와 이어받기 실행이 결과를 바꾼 사례는 [[메모리-연구/procedural-graphs/results/EXPERIMENT_REPORT_KO|개정된 종합 보고서]] §1에 있으며, 이 표와는 모델이 달라 합산하지 않는다.

## 확인하지 못한 것

현재 다음 판단을 가르는 것은 최고 점수의 재인용보다 실행 경로와 비교 조건의 확인이다. DB 탐색에서는 동일 조건의 반복과 문항별 누출·비용 감사가 있어야 단일 20pt 차이를 일반적인 개선으로 해석할 수 있다.

### 그래프 노드 활성화 확인 (2026-10-19)

저장된 guidance 이벤트의 `active` 값을 집계했다. 과거에는 STATUS 노드가 활성 노드가 되지 못하는 문제가 있었지만, 이 실행들에서는 STATUS 노드도 활성화됐다.

| 실행 | 활성 노드와 횟수 |
|---|---|
| 포커 `pg_memory` run0 | `read_known`(STATUS) 145, `Start` 104, `poker_action` 91, `read_unknown` 1 |
| 포커 `pg_memory` run1 | `read_known` 137, `Start` 104, `poker_action` 77, `read_unknown` 1 |
| 포커 `pg_memory` run2 | `read_known` 109, `Start` 104, `poker_action` 56, `read_unknown` 3 |
| DB 진화 그래프 (8노드, `mt-guided-idx1-a`에 저장된 pass 1개) | `database_query` 62, `PriceSemanticsNeeded` 56, `TimeStatusSemanticsNeeded` 48, `memory_read` 40, `AttrTaxonomyNeeded` 38, `CandidateReady` 4 |

- 포커에서 `read_unknown`은 run당 1~3회뿐이고 `hand_over`는 한 번도 활성화되지 않았다. 그래프의 이 분기가 거의 쓰이지 않았으므로, PG의 효과는 사실상 `read_known`과 `poker_action` 쪽 안내에서 나왔다. 상대 유형이 바뀔 때의 분기를 시험했다고 해석하지 않는다.
- 노드가 활성화됐다는 것과 그 안내가 정확도에 도움이 됐다는 것은 다른 이야기다. 포커에서 결합은 stateless를 넘지 못했다.
- 이 집계는 저장된 이벤트의 횟수 계산이며 안내 내용이 solver의 행동을 바꿨는지는 확인하지 않았다.

### 남은 한계

- 포커는 조건당 정확히 3회지만 상대 유형 하나만 대상으로 했다. 최종 진화 비교는 조건당 1회다.
- 문항별 누출 감사, 전체 비용 비교, 유의성 검정은 이번 갱신 범위에 포함하지 않았다.

## 출처와 재검산 범위

원 코드는 [procedural-graphs-lab](https://github.com/donggyun112/procedural-graphs-lab)의 수집 기준 커밋 `2c265f7` 이후 로컬 상태다. 이번에 읽은 결과 폴더는 원 저장소에서 미추적 상태였고 일부 구현에도 미커밋 변경이 있었다. 커밋만 checkout해서 동일 실행을 복원할 수 있다고 주장하지 않는다.

지식베이스 저장소의 [집계 근거 JSON](https://github.com/donggyun112/knowledge-base/blob/main/docs/procedural-graphs-followup-2026-10-18.json)에 원 파일 상대 경로, SHA-256, 모델·분할 조건과 결과 지표를 남겼다. 평균은 실행별 값을 동일 가중치로 계산했다. 원시 trajectory, 메모리 본문, 데이터셋과 실행 로그는 공개 자료에 포함하지 않았다. 이 자료는 **저장된 결과의 재집계 근거**이며 독립 재현 결과는 아니다.
