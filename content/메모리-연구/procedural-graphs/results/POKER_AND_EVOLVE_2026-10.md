---
title: "포커 포트와 그래프 진화 추가 실행 — 2026-10"
tags:
  - memory-research
  - procedural-graphs
---

> [!info] 범위
> 초기 보고서 이후의 로컬 실행 폴더(`results/poker`, `results/mt-evolve-v2-agg`)를 읽은 기록이다. 결합모델의 입증 결과가 아니다. 기존 [[메모리-연구/procedural-graphs/results/EXPERIMENT_REPORT_KO|종합 보고서]] 수치와 합산하지 않는다.

## 왜 포커인가

CLBench `database_exploration`은 사실 문제라서 절차 쪽 기여를 잴 수 없었다(드리프트 후 memory 75.0%, memory+PG 75.0%). 그래서 `exploitable_poker` 어댑터를 붙였다. 상대 유형이 바뀌는 120 hands 스트림이라 절차 쪽을 잴 여지가 있다.

## 포커 결과

- 모델: `deepseek-v4-flash`, 상대 loose-aggressive, 조건당 3회, 지표는 bb/hand.

| 조건 | 평균 | 3회 값 |
|---|---:|---|
| stateless | +1.21 | 1.40, 1.14, 1.08 |
| memory + PG (결합) | +0.85 | 1.45, 0.60, 0.51 |
| graph prompt | +0.60 | 1.34, 0.23, 0.24 |
| memory | +0.22 | −0.19, 0.69, 0.16 |
| graph prompt + memory | +0.18 | −0.95, 1.99, −0.51 |

읽는 법:

- 결합은 memory 단독보다 평균이 +0.63 높다. 표준편차가 0.4~0.5이고 n=3이라 이 차이는 노이즈와 구분되지 않는다.
- 메모리가 붙은 조건은 모두 stateless보다 낮다. 이 과제에서 메모리가 이득이라는 근거는 없다.
- 결합이 stateless를 넘지 못했으므로 결합모델이 입증됐다고 쓸 수 없다.

## 그래프 진화 단일 실행

`mt-evolve-v2-agg`: fixed 그래프 65.0%, evolved 그래프 85.0%(각 40문항 1회). 같은 설정이 12.5pt, 같은 그래프가 최대 35pt 흔들린 적이 있어 이 차이는 결론이 아니다. evolved는 pre 95%에서 post 75%로 떨어졌고 val/test stream 구분도 확인하지 못했다.

## 확인하지 못한 것

- 포커 `pg_memory`에서 그래프 노드가 실제로 활성화됐는지 로그를 확인하지 않았다. 이전에 STATUS 노드가 활성 노드가 되지 못하는 문제가 있었다.
- 반복 3회 미만이고 같은 상대 유형 하나만 대상으로 했다.
- 위 두 실행은 원시 로그를 승격해 쓰지 않은 폴더이며 코드·로그는 공개하지 않는다.
