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

2026-10-17 21:43 KST에 저장된 `mt-evolve-v2-agg` 최종 파일을 10월 18일 다시 확인했다. `database_exploration/schema_drift`, 요청 모델 `deepseek/deepseek-v4.1-flash`, `multiturn-v1`, solver reasoning `medium`, required recall, `e5` retriever 조건이다. Refiner는 `claude-cli:opus`, reasoning `medium`이다.

| 조건 | 정답 | normalized score | 평균 SQL 수 | 전반 정확도 | 후반 정확도 |
|---|---:|---:|---:|---:|---:|
| fixed_pg | 26/40 (65%) | 0.4333 | 5.600 | 60% | 70% |
| evolved_pg | 34/40 (85%) | 0.6067 | 4.675 | 95% | 75% |

두 조건 모두 메모리와 PG를 쓴다. 이 표는 PG 유무가 아니라 고정 그래프와 수정 그래프의 비교다. 해당 실행에서는 정확도가 20pt 높고 SQL 수도 적었지만 조건당 1회다. 반복 실험의 분산이나 유의성을 확인하지 않았으므로 일반적인 개선으로 결론 내리지 않는다. 전반·후반 차이만으로 난이도 차이, 과적합 또는 학습 효과의 원인을 특정할 수도 없다.

메타데이터에는 train index 0, validation indices `[1, 6]`, test index 3, stride 5가 기록돼 있다. 학습 자료는 기존 `mt-evolve-v2`와 `mt-guided-idx2-{a,b,c}`의 pass 네 개를 재사용했다. 따라서 **val/test 구분 자체는 확인됐다.** 다만 index가 다르다는 사실만으로 문항·DB·trajectory 간 독립성이나 누출 부재가 입증되지는 않는다.

체크포인트는 두 후보 평가를 기록한다. 첫 후보는 validation 평균 score 0.5675로 채택됐다. 다음 후보는 score 0.6150으로 높았지만 후반 정확도가 평균 7.5pt 낮아져 허용치 5pt를 넘었다는 drift guard 진단으로 기각됐다. 최종 test는 채택된 그래프를 대상으로 한다. score만 높이는 편집과 schema drift 이후 성능을 함께 보는 편집 선택이 다를 수 있음을 보여주는 실행 기록이다.

## 같은 계열의 반복 실행과 비교

`mt-memonly-idx{1,2}-{a,b,c}`와 `mt-guided-idx{1,2}-{a,b,c}`의 완료된 최종 파일도 재집계했다. 모두 요청 모델 `deepseek/deepseek-v4.1-flash`, reasoning `medium`, 40문항, stride 10, required recall, `e5` 조건이다. 아래는 각 stream에서 세 실행의 산술평균이다. guided는 각 파일의 `evolved_pg`, memory는 `fixed_pg` 행을 사용하되, 실제 조건 플래그로 PG 유무를 구분했다. 이름만으로 조건을 판단하면 안 된다.

| stream index | 조건 | 실행 수 | 평균 정확도 | 평균 SQL 수 | 평균 score |
|---|---|---:|---:|---:|---:|
| 1 | memory | 3 | 77.50% | 7.258 | 0.4411 |
| 1 | memory + guided PG | 3 | 79.17% | 5.533 | 0.5222 |
| 2 | memory | 3 | 70.00% | 6.658 | 0.4156 |
| 2 | memory + guided PG | 3 | 77.50% | 5.600 | 0.5167 |

이 조건에서는 정확도 차이보다 SQL 호출 수 감소가 두 stream에서 일관되게 관찰된다. 정확도 차이는 stream마다 다르며 유의성 검정은 하지 않았다. 이 guided 실행은 `generations_requested=0`이므로 evolved라는 행 이름이 있어도 각 실행 안에서 새로운 진화를 수행한 결과가 아니다. `mt-evolve-v2-agg`와는 stride와 비교 대상이 달라 같은 반복군으로 합산하지 않는다.

`e0731-*`는 이번에 확인한 범위에서 checkpoint 파일만 있었고 완료된 최종 비교 파일이 없었다. 중간 결과는 이 표에 넣지 않는다.

## 확인하지 못한 것

- 포커 `pg_memory`에서 그래프 노드가 실제로 활성화됐는지 로그를 확인하지 않았다. 이전에 STATUS 노드가 활성 노드가 되지 못하는 문제가 있었다.
- 포커는 조건당 정확히 3회지만 상대 유형 하나만 대상으로 했다. 최종 진화 비교는 조건당 1회다.
- 문항별 누출 감사, 실제 활성 노드 추적, 전체 비용 비교, 유의성 검정과 유료 재실행은 이번 갱신 범위에 포함하지 않았다. STATUS 노드 문제의 존재만으로 이 실행 전체가 무효라고 단정하지 않는다.

## 출처와 재검산 범위

원 코드는 [procedural-graphs-lab](https://github.com/donggyun112/procedural-graphs-lab)의 수집 기준 커밋 `2c265f7` 이후 로컬 상태다. 이번에 읽은 결과 폴더는 원 저장소에서 미추적 상태였고 일부 구현에도 미커밋 변경이 있었다. 커밋만 checkout해서 동일 실행을 복원할 수 있다고 주장하지 않는다.

지식베이스 저장소의 [집계 근거 JSON](https://github.com/donggyun112/knowledge-base/blob/main/docs/procedural-graphs-followup-2026-10-18.json)에 원 파일 상대 경로, SHA-256, 모델·분할 조건과 결과 지표를 남겼다. 평균은 실행별 값을 동일 가중치로 계산했다. 원시 trajectory, 메모리 본문, 데이터셋과 실행 로그는 공개 자료에 포함하지 않았다. 이 자료는 **저장된 결과의 재집계 근거**이며 독립 재현 결과는 아니다.
