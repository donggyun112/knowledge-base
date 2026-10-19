---
title: "Stream-memory regression repair — 2026-09-28"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `neural-memory/STREAM_MEMORY_REGRESSION_REPAIR_REPORT.md` · 수집 2026-10-16 · **로컬 미커밋 문서 사본** (원격 커밋과 동일하다고 보장하지 않음)
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# Stream-memory regression repair — 2026-09-28

## Status

이 실험의 질문은 ‘새 표현을 배우면서 기존에 맞히던 기억 문제도 그대로 맞힐 수 있는가’다. 여기서 성능 회귀(regression)는 새 학습 뒤에 기존 정확도가 떨어지는 현상을 뜻한다.

검증 자료에서는 기존 17개 조건의 정확도를 모두 유지하는 학습 후보를 찾았다. 그러나 seed-7 독립 시험에서는 새 표현의 큰 개선과 기존 revision 조건의 회복을 확인하는 동시에, 다섯 조건의 정확도 하락도 발견했다. seed-17 반복 실험에서는 학습된 체크포인트가 하나도 선택 기준을 통과하지 못했다. **기존 성능이 전혀 떨어지지 않는 대체 모델은 아직 얻지 못했다.** 원래 체크포인트는 수정하거나 교체하지 않았다.

정답 후보 간 점수 차이를 보존하는 후속 실험도 마쳤다. 단순 보존 회상은 한 사례 더 맞혀 76.5625%에서 77.34375%로 올랐지만, 원래의 79.6875%에는 못 미쳤다. 미리 정한 채택 기준을 통과하지 못했으므로 **성능 저하는 줄었지만 완전히 해결되지는 않았다.** 마지막으로 남겨 둔 미사용 값 여덟 개는 평가하지 않았으며 그대로 남아 있다.

## Intervention

각 `stream-rmt-revision-clean-seed{7,17}.pt`에서 출발했다. 기존 어댑터 파라미터는 비트 단위로 그대로 두고, Q/V 어댑터에 rank 네 개를 추가해 새로 배울 부분을 만들었다. 각 projection에 들어오는 내부 표현으로 sigmoid gate를 계산해 추가 경로를 얼마나 사용할지 학습한다.

검증을 통과한 후보에서는 이 추가 경로가 읽기·텍스트 처리와 쓰기 모두에 적용된다. 따라서 **읽기 부분을 고정한 구조가 아니다.**

새 대화는 뒤에 실제로 나오는 내용의 다음 토큰 cross entropy로 학습한다. 기존 대화는 시작 모델을 교사로 삼아 두 가지를 보존한다. 전체 어휘의 출력 확률분포를 맞추는 KL 손실과, 과거를 읽고 만든 상태를 맞추는 증류 손실이다.

기존 정답에 대한 cross entropy 가중치는 0이다. 기존 정답을 새로 잘 맞히도록 훈련하는 것이 아니라 교사의 기존 행동을 유지하는 목적이며, 교사의 오답도 함께 보존한다. 사실 위치나 답 위치 주석은 학습 손실에 관여하지 않는다. 교사 모델은 학습 중에만 필요하고, 추론에서는 메모리 모델 하나만 실행한다.

한 배치의 여덟 사례는 대화 문맥이 같고 저장할 값만 다르다. 새 대화와 재학습용 기존 대화 모두 여덟 사례를 한 묶음으로 뽑는다. 그래야 같은 문맥에 특정 정답 값 하나만 들어 있는 배치가 되지 않는다. 학습은 네 순환으로 진행하며, 사이에 끼는 무관한 발화의 길이는 4, 8, 16, 32턴을 다룬다.

모든 대화의 순환 기억은 여전히 0에서 시작한다. 상태는 8 × 576개의 float32 값, 즉 18 KiB로 유지한다. 외부 key/value 데이터베이스나 과거 원문 캐시는 없다. 새로 추가한 실질 학습 용량은 265,020개 파라미터이고, 원래 어댑터는 568,513개 파라미터다.

## Selection and data boundaries

- 적응 학습용 값 256개, 검증용 값 32개, 한 번도 쓰지 않은 시험용 값 32개를 나눈다. 세 집합의 토큰 ID는 겹치지 않는다.
- 이전에 이미 시험한 값 192개는 성능 하락을 다시 확인하는 회귀 자료다. 새로운 시험 자료로 세지 않는다.
- 체크포인트 선택에는 17개 검증 조건만 사용한다. 각 조건의 정확도 하락을 **전혀 허용하지 않는다.** 통과한 후보 중 최악 조건의 전체 어휘 정확도를 먼저 최대화하고, 동률이면 평균 정답 NLL을 최소화한다. NLL은 정답에 얼마나 낮은 확률을 주었는지를 재는 손실로, 낮을수록 좋다.
- 각 seed는 200스텝, batch-8로 고정한다. 50스텝마다 검증하며 학습률 0.0002, KL 가중치 128, 상태 손실 가중치 40, 재학습 CE 가중치 0을 쓴다.
- seed-17 반복 실행은 seed-7 시험 결과를 읽기 전에 시작했다. 시험 결과를 보고 체크포인트·하이퍼파라미터·선택 규칙을 바꾸지 않는다.
- 독립 평가는 선택 후보와 짝이 맞는 원본을 정확히 같은 대화 흐름에서 비교하며 기울기로 갱신하지 않는다. 새 시험은 값마다 두 번 추출해 잡담 8턴과 16턴 조건을 모두 다룬다.

단어 목록은 MSC 학습 자료의 단어 빈도에서 가져왔다. 하지만 실제 학습 대화는 조건을 통제해 만든 **합성 대화이며, 실제 MSC 대화를 학습한 실험은 아니다.** ‘미학습 값’은 이번 적응 학습에서 보지 않은 값이라는 뜻이다. 기반 언어모델도 사전학습에서 처음 보는 단어라고 보장하지 않는다.

## Trials that did not solve the regression

| Trial | Selected checkpoint | Outcome |
| --- | --- | --- |
| Uniform / Q/V-versus-interface delta interpolation, seeds 7 and 17 | Small deltas | Old validation preserved, but new `now` accuracy remained zero |
| Added rank, ungated shared processing | Step 0 | Learned candidates regressed; original fallback only |
| Added rank, suffix-only writing | Step 0 | Old validation regressed; original fallback only |
| Conditional suffix-only writing | Step 0 | Gating alone did not preserve old accuracy |
| Conditional writing, matched batch 8, old CE + KL/state | Step 50 | Old validation preserved, but new `now` accuracy remained zero |
| Conditional writing, matched batch 8, teacher-only old loss | Step 50 | Same zero-new-accuracy limitation |
| Keep learned gates while shrinking writing deltas | Small deltas | Preserved old validation, but new `now` accuracy remained zero |

별도 진단에서는 사실이 들어 있는 구간의 주석을 이용해 원래 쓰기 gate를 강제로 열었다. 그래도 `now`는 해결되지 않았고 일반적인 정정 조건은 오히려 나빠졌다. 따라서 gate를 항상 열어 두는 것만으로 고칠 수 있다는 근거는 없다. 이 주석의 특권을 쓴 진단은 학습 지도에도, 실제 실행의 경로 선택에도 사용하지 않았다.

## Seed-7 validation result

선택된 `stream-rmt-protected-shared-gated-seed7.pt`는 마지막 200스텝이 아니라 150스텝의 상태다. 17개 검증 조건에서 전체 어휘 정확도를 모두 유지했다. 평균 정답 NLL은 4.36914에서 3.09793으로 내려갔다.

| Condition | Original | Selected |
| --- | ---: | ---: |
| `now` | 0% | 71.875% |
| `now_competing` | 0% | 43.75% |
| `revision` | 75% | 75% |
| Worst condition across all 17 | 0% | 40.625% |

별도 감사 파일 `stream-rmt-protected-shared-gated-seed7-training-audit.json`에서 원래 파라미터의 모든 부분, 다시 생성한 입력 해시, 정확한 표본 추출·토큰 예산, 검증 자료만 이용한 선택을 확인했다. 200스텝 동안 새 대화의 미래 내용 토큰 14,240개와 기존 대화의 미래 내용 토큰 13,536개를 처리했다. 기존 토큰은 KL의 비교 대상이며, 기존 정답 CE를 최적화하는 대상은 아니다.

## Verification

### Seed-17 replication

같은 고정 200스텝 절차로 seed-17을 실행했지만, 학습된 후보 중 17개 검증 조건을 모두 지킨 것은 없었다. 150스텝에서는 `now` 78.125%, `now_competing` 40.625%를 얻고 revision 87.5%도 유지했지만 `changed_competing`이 떨어졌다.

따라서 선택 결과는 0스텝, 즉 비트 단위로 원본과 같은 되돌림 상태다. 이를 학습에 성공한 복구로 보지 않는다. 독립 학습 감사에서도 이 되돌림, 기존 파라미터 부분, 입력 해시, 추출 예산을 확인했다. 예산은 새 미래 토큰 14,616개와 재학습 미래 토큰 12,552개였다.

### Seed-7 independent test

seed-7 독립 시험은 체크포인트마다 33개 조건, 대화 사례 2,272개를 평가했다. 원본과 선택 모델의 어댑터 텐서는 모두 평가 전후 비트 단위로 같았고, 평가 중 학습 스텝은 0이었다. 짝지은 감사로 입력 해시도 같음을 확인했다. 다만 **전체 조건 보존과 기존 조건 보존은 둘 다 실패**로 판정됐다.

| Test condition | Original | Selected |
| --- | ---: | ---: |
| Fresh `now` | 4.6875% | 82.8125% |
| Fresh `now_competing` | 0% | 62.5% |
| Legacy correction | 82.8125% | 84.375% |
| Legacy revision | 77.34375% | 78.90625% |
| Legacy other-fact recall | 73.4375% | 73.4375% |
| Legacy simple retained recall | 79.6875% | 76.5625% |

전체 어휘 정확도가 떨어진 다섯 조건을 빠짐없이 적으면 다음과 같다. ‘Net fewer correct’는 같은 사례 수에서 정답 개수가 순수하게 얼마나 줄었는지를 뜻한다.

| Condition | Difference | Net fewer correct |
| --- | ---: | ---: |
| Fresh revision | −1.5625 percentage points | 1 of 64 |
| Fresh other-fact recall | −1.5625 points | 1 of 64 |
| Fresh incidental mentions | −1.5625 points | 1 of 64 |
| Legacy neutral | −0.78125 points | 1 of 128 |
| Legacy simple retained recall | −3.125 points | 4 of 128 |

이 개선이 익숙한 값을 추측한 효과인지 확인하려고 기억을 지우거나 다른 대화의 기억으로 교환했다. 두 새 `now` 조건에서 기억을 지우면 전체 어휘 정확도가 0%였고, 교환해도 0%였다. 따라서 실제 대화별 기억이 기여한다는 근거가 된다.

정답 묶음 단위 bootstrap으로 계산한 개선 구간은 `now`가 [59.375, 93.75]포인트, `now_competing`이 [18.75, 93.75]포인트다. 다만 독립적인 정답 묶음이 네 개뿐인 구간이다. 보존 회상의 변화 구간에는 0이 포함되지만, 그렇다고 관측된 정확도 하락이 ‘보존 통과’로 바뀌지는 않는다.

이 독립 시험에 사용한 새 값 32개는 이제 한 번 확인한 자료가 됐다. 다음 조정에서는 이를 회귀 자료로 취급하고, 새로운 독립 성능 주장을 하려면 다시 미사용 값을 남겨 두어야 한다.

저장소 테스트 711개가 모두 통과했다. 실제 AdamW 갱신에서의 보존, 쓰기·읽기의 인과적 분리, 공유 처리 경로의 동작, 주석과 무관한 손실, 과거 상태 손실에서 미래 정답의 제외, 선택 구조의 순환 체크포인트 재로드 시 비트 단위 일치를 검사했다. 기울기 추적 스칼라를 변환할 때 나오는 기존 경고 하나는 남아 있다.

### Decision-boundary follow-up (completed and rejected)

출력 분포와 상태를 가깝게 유지하는 KL/상태 손실만으로는, 가장 높은 점수의 토큰(argmax)이 일부 바뀌는 것을 막지 못했다. 두 후보의 점수가 가까우면 작은 변화도 최종 답을 바꿀 수 있기 때문이다.

후속 실험은 **재학습 대화의 모든 미래 내용 토큰**에서 교사만 기준으로 삼는 margin 손실을 추가했다. 답 위치만 고르는 마스크는 쓰지 않는다. 토큰마다 교사가 선택한 argmax가 학생의 가장 강한 경쟁 토큰보다 앞서도록 하며, 목표 점수 차이는 `min(teacher margin, 0.1)`이다.

이 손실은 원래 모델에서는 0이고, 동률 처리도 평가와 같은 argmax 규칙을 쓴다. 교사 logit은 학습 연결을 끊어 고정하며 실제 정답이 무엇인지 확인하지 않는다. 기존 모델의 잘못된 결정도 보호한다. 즉 재학습 정답을 더 잘 맞히게 만드는 것이 아니라, 기존 결정을 유지하는 장치다.

두 seed 모두 원래의 깨끗한 기준 모델에서 다시 시작했다. 앞선 설정과 200스텝 예산은 그대로 두고 결정 손실 가중치 64를 추가했다. 체크포인트는 여전히 검증 자료로 선택한다. 추론 중에는 학습하지 않으며 두 번째 모델도 필요하지 않다.

seed 7은 200스텝을 모두 마쳤고 150스텝을 선택했다. 17개 검증 조건을 모두 유지했으며 최악 정확도는 40.625%, 평균 정답 NLL은 3.09718이었다. 독립 학습 감사를 통과했고, 표본 추출·토큰 예산은 앞선 seed-7 실행과 같았다.

한편 기울기 계산이 큰 batch-8 작업을 두 개 동시에 돌리자 메모리 압박과 큰 속도 저하가 발생했다. seed-17 후속 실행은 중단하고 학습 작업을 하나씩 실행하도록 바꿨다. **완료된 seed-17 decision-margin 결과는 없다.** 중간 검증만으로 반복 검증에 성공했다고 보고하지 않는다. 원래 체크포인트와 완료된 실험 산출물은 삭제하지 않았다.

`stream-rmt-decision-manifest.json`은 **동일한** 무작위 순서의 512단어 풀에서 마지막 미사용 값 여덟 개를 남긴다. 앞서 시험한 224개 값은 모두 제외하고 학습/검증/진단 분할은 유지한다. 이 작은 최종 집합으로 넓은 일반화 주장을 할 수는 없다. 이전 32값 시험은 이번 후속 실험에서는 회귀 자료이며 새 독립 시험이 아니다.

후속 성능 시험을 보기 전에 다음 채택 기준을 고정했다.

- 검증으로 선택한 체크포인트에 실제 학습 변화가 있어야 한다.
- 이미 본 32값 회귀 묶음의 33개 조건을 모두 유지해야 한다.
- 짝이 맞는 원본보다 두 `now` 조건을 각각 최소 25퍼센트포인트 개선해야 한다.

이를 모두 통과한 후보만 마지막 미사용 값 여덟 개에서 평가한다. 두 시험 묶음 어느 쪽으로도 체크포인트나 alpha를 선택하지 않는다. 기준을 못 넘으면 그 시험에 맞춰 더 최적화하는 대신 후보를 기각한다.

2,272사례 회귀 재평가를 끝냈지만 다섯 조건의 하락이 남았다. 새 revision, 새 other-fact recall, 새 incidental mentions는 각각 1/64씩, 기존 neutral은 1/128, 기존 retained recall은 3/128씩 정답을 잃었다. 새 `now`와 `now_competing`의 이득은 각각 82.8125%, 62.5%로 유지됐다. 기존 revision도 원래 77.34375%보다 높은 78.90625%를 유지했다.

앞선 공유 gate 후보와 비교하면 margin 항은 보존 회상 한 사례를 되찾았지만 다른 하락까지 없애지는 못했다. 짝지은 회귀 감사에서 읽기 전용 평가와 동일 입력을 확인했고, 전체 조건 보존 및 기존 조건 보존 표시는 모두 false였다.

따라서 마지막 여덟 값을 시험할 기준에 도달하지 못했다. 기각 후 seed-17 margin 학습이나 최종 독립 시험을 추가로 실행하지 않았다.

최종 산출물은 다음과 같다.

- `local-data/stream-rmt-protected-decision-seed7.pt`: 검증으로 선택한 학습 후보. **성능 하락 없는 대체 모델로 채택된 것은 아니다.**
- `local-data/stream-rmt-protected-decision-seed7.json`: 학습·선택 기록.
- `local-data/stream-rmt-protected-decision-seed7-training-audit.json`: 보존 대상 파라미터 부분, 입력, 표본 추출, 선택 검증.
- `local-data/stream-rmt-protected-decision-seed7-regression.json`: 33개 동일 조건, 묶음별 원시 예측, 대조 결과.
- `local-data/stream-rmt-protected-decision-seed7-regression-audit.json`: 하락을 포함한 짝지은 차이와 정답 묶음 bootstrap 구간.

실험 당시 lean-ctx skill을 사용해 읽기와 긴 실험 출력의 양을 제한했다. CodeCanvas에는 이 실험용 Python 함수가 색인되지 않았으므로, 인과성과 로딩에 대한 주장은 근거 없는 그래프 해석 대신 실행 가능한 테스트로 확인했다.

## Limits

이번에 검사한 것은 속성 하나의 토큰을 기억하고 갱신하는 과제다. 완성된 범용 메모리 모델, 실제 사람 대화의 E2E 성능, 자동 `NO_MEMORY`/반환 시점 디코더를 검증한 것은 아니다.

특히 기존 파라미터를 비트 단위로 보존해도 예측이 보존되는 것은 **아니다.** 추가 경로가 출력에 영향을 줄 수 있으므로, 독립적인 회귀 평가가 반드시 필요하다.
