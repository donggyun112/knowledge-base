---
title: "기존 상태 이후 새 사실 획득 — 2026-09-27"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `neural-memory/STREAM_MEMORY_ACQUISITION_REPORT.md` · 수집 2026-10-16 · **로컬 미커밋 문서 사본** (원격 커밋과 동일하다고 보장하지 않음)
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# 기존 상태 이후 새 사실 획득 — 2026-09-27

이번 인공 단일 사실 과제에서는 읽기 고정과 공동학습 모두 개선됐다. 새 32·64턴 잡담 시험에서 두 조건·두 seed가 각각 192/192를 전체 어휘 기준으로 맞혔다. 읽기 고정은 필수 조건이 아니지만, **읽기 가중치 변경 없이 기억 갱신 파라미터만 학습해도 개선할 수 있음**은 확인했다. 일반 사람 대화에서 저장할 정보의 특징을 학습했다는 결론은 아직 아니다.

후속 [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_TRANSFER_REPORT|어휘 전이 보고서]]에서 이 성공의 경계를 확인했다. 네 모델 모두 새 단어의 기억 경로 정확도는 0%였고, 후보 단어가 등장하는 잡담과 다른 화자의 사실에도 간섭을 받았다. 아래의 알려진 8개 단어 결과를 열린 어휘 기억의 성공으로 해석하지 않는다.

## 실험 목적과 범위

이전 약한 seed는 사실 앞 잡담 4구간에서 25%, 같은 잡담을 사실 뒤에 두면 100%였다. 이번은 그 조건을 개선하는 학습에서 읽기/QV 가중치를 고정한 효과를 공동학습 대조와 비교한다. 사람이 지정한 저장 중요도 라벨이나 과거 정답 토큰의 직접 라우팅은 사용하지 않는다.

현재 Transformer가 읽기와 쓰기 processor를 공유하므로 “읽기 고정”은 **공유 Transformer의 Q/V 저차원 가중치까지 고정**하는 조건이다. 독립적인 writer Transformer를 학습하는 실험이 아니다. 해당 조건의 학습 파라미터는 기억 bridge, gate, suffix query 338,113개다. 공동학습은 Q/V도 포함한 568,513개다.

두 조건 모두 같은 seed의 이전 **oracle-prefix 없는 curriculum 체크포인트**에서 시작한다. 기존 짧은 400 + 긴 400에 이번 400을 추가하므로 전체 학습 예산은 1,200스텝이다. 따라서 이전 800스텝 모델과의 차이만으로 reader 고정 효과라고 주장하지 않는다. 고정/공동학습끼리의 같은 시작·자료·스텝 대조가 핵심이다.

## 학습·선택

- train 64블록/512사례, valid 16블록/128사례, 잡담 2·4·8·16·32턴 + 뒤 잡담 3턴.
- batch 2, chunk 32, rank 4, lr 0.0003, gradient norm 1 clipping, Apple MPS/float32.
- 모든 독립 대화의 기억은 0에서 시작하고, 실제 원시 텍스트를 시간순으로 처리한다. 구간 사이 state를 detach하지 않는다.
- 손실은 마지막 미래 구간의 모든 대화 내용 next-token CE다. 사실/정답 위치 annotation은 non-oracle 학습 손실에서 사용하지 않는다.
- valid 자기 기억의 정답 NLL로 최선 체크포인트를 고른다. **초기 체크포인트(0스텝)도 선택 가능**하게 해 계속 학습해 악화된 모델을 강제로 고르는 것을 막는다.
- 고정 조건은 매 실행에서 최종 학습 가중치와 시작 Q/V adapter를 정확 비교한다. 선택한 best로 되돌리기 **전** 비교해 중간 학습의 변경을 가리지 않는다.

초기 checkpoint가 사용한 자료와 이번 자료의 분포가 다르므로 검증값은 이번 새 valid에서 계산한다. 초기/최종 비교는 같은 모델 조건 내 개입이다.

## 평가

기존 96사례 test는 반복 확인한 탐색적 시험이다. 별도로 같은 새 잡담(seed 3009), 24블록/192사례에서 이전 모델과 고정/공동학습 모델을 비교한다. 8·16턴과 32·64턴 조건이며 checkpoint 선택에 이 자료를 사용하지 않는다.

앞/뒤 잡담 token-block 진단은 이전과 같은 사실·마지막 원문 구간을 고정하고 추가 잡담 0·4·8·16·32구간을 배치한다. 한 인공 템플릿/8사례이므로 일반화 평가와 구분한다.

기존 96사례 test 결과는 다음과 같다.

| 조건 | seed | 선택 스텝 | 8지선다 | 전체 어휘 단일 토큰 | 정답 NLL |
| --- | ---: | ---: | ---: | ---: | ---: |
| 읽기 고정 | 7 | 375 | 100% | 92.71% | 0.24900 |
| 공동학습 | 7 | 375 | 100% | 97.92% | 0.02525 |
| 읽기 고정 | 17 | 175 | 100% | 98.96% | 0.03500 |
| 공동학습 | 17 | 175 | 100% | 100% | 0.00091 |

모두 빈 기억은 8지선다 12.50%, 교환 기억은 원래 단어 0%, 기증 단어 100%였다. 고정 두 seed는 `frozen_reader_unchanged=true`, `backbone_gradient_present=false`이며, 빈 상태 및 과거 단어 오라클의 NLL도 이전 같은 reader의 값과 일치했다. 따라서 고정 조건의 개선은 읽기 가중치 변경 없이 기억 갱신 파라미터로 얻었다.

공동학습도 좋은 성능을 보이므로 **읽기 고정이 필수거나 공동학습보다 항상 낫다고 주장하지 않는다.** 이번 조건은 앞선 실패한 다양화와 시작 체크포인트 및 총 스텝 수가 다르다. 확인된 것은 더 긴 단계까지 학습한 초기 모델에서 추가 학습하면, 고정된 reader를 위한 갱신 경로도 이 과제를 배울 수 있다는 점이다.

### 새 잡담 평가

각 칸은 `8지선다 / 전체 어휘 단일 토큰` 정확도다. 각 조건은 24블록/192사례이며, 모든 모델을 동일한 seed 3009 자료로 비교했다.

| 모델 | seed | 잡담 8·16턴 | 잡담 32·64턴 |
| --- | ---: | ---: | ---: |
| 이전 curriculum, 800스텝 | 7 | 90.63% / 82.29% | 69.79% / 60.42% |
| 읽기 고정, 추가 400스텝 | 7 | 100% / 100% | 100% / 100% |
| 공동학습, 추가 400스텝 | 7 | 100% / 100% | 100% / 100% |
| 이전 curriculum, 800스텝 | 17 | 54.17% / 51.56% | 23.96% / 22.92% |
| 읽기 고정, 추가 400스텝 | 17 | 97.40% / 96.35% | 100% / 100% |
| 공동학습, 추가 400스텝 | 17 | 100% / 100% | 100% / 100% |

완료된 고정/공동학습 평가의 빈 기억은 모두 8지선다 12.50%다. 교환 기억에서 기증 단어 정확도는 자기 기억의 8지선다 정확도와 같았다. 긴 잡담 조건의 정답 NLL은 고정 seed 7/17에서 0.00149/0.01955, 공동학습에서 0.00089/0.00180이다.

같은 24블록을 묶어 2,000회 재표집한 paired bootstrap에서, 긴 잡담의 이전 모델 대비 고정 모델 **전체 어휘 정확도 개선**은 seed 7에서 +39.58%p (95% 구간 +23.96~+56.25%p), seed 17에서 +77.08%p (+67.71~+84.38%p)였다. 이는 동일한 인공 자료 분포 내 비교이며, 더 넓은 대화 분포에 대한 신뢰구간이 아니다. 모두 정답인 조건의 bootstrap 구간 [100%, 100%]도 일반 모집단에서 오류가 없다는 뜻이 아니다.

공동학습 대비 고정의 우위는 나타나지 않았다. 두 seed의 긴 잡담 정확도는 같고, seed 17의 짧은 잡담에서 공동학습은 전체 어휘 기준 +3.65%p (paired 95% 구간 +0.52~+8.33%p) 높았다. 이 결과는 reader를 고정해야만 학습된다는 가설을 지지하지 않는다.

### 앞/뒤 잡담 개입

사실 앞 또는 뒤에 잡담 0·4·8·16·32 token-block을 넣는 총 10조건에서, 두 seed의 고정/공동학습 모델 모두 8지선다와 전체 어휘 정확도 100%였다. 이전 약한 seed 17의 사실 앞 4·8·16·32구간 정확도 25%가 100%로 회복됐다. 이미 이전부터 통과했던 강한 seed 7도 유지됐다.

이 진단은 각 조건당 같은 단일 템플릿의 8사례뿐이다. 새로 생성한 잡담 시험과도 평가 범위가 다르며, 여러 독립 사실을 구분하거나 충돌하는 사실을 정정할 수 있다는 증거로 쓰지 않는다.

## 저장·검사

reader를 고정해도 체크포인트에 해당 Q/V adapter는 저장해야 한다. `requires_grad`인 텐서만 저장하면 평가 시 고정된 읽기 가중치가 빠지는 문제가 생기므로, **고정 전 adapter 이름을 수집해 전부 별도 snapshot**한다. 큰 기존 LM 본체는 계속 포함하지 않는다.

CPU snapshot이 실시간 파라미터와 storage를 공유하지 않는지, reader 고정 뒤 미래 손실이 bridge/gate/query에 도달하는지, reader에 gradient/변경이 없는지, 고정 reader를 포함한 checkpoint가 정상 복원되는지 검사했다. 저장 중요도 annotation 독립성도 검사했다. 새 잡담에는 모델끼리의 paired block-bootstrap 비교를 추가하고 블록/사실 위치/질문 위치가 다르면 비교를 거부한다. 전체 검사 481 passed, 1 기존 경고.

최초 paired 평가 실행은 live tuple과 저장 JSON list가 같은 잡담 선택인데도 달라서 비교 guard에서 중단됐다. 표현을 정규화하고 회귀 검사를 추가한 뒤 해당 고정 seed 17 평가를 재실행했다. 이후 공동학습 비교도 정상 완료했다. 학습/모델 계산에는 영향을 주지 않았고, 수치는 완료된 재실행 파일만 사용한다.

별도 1스텝/lr=0 GPU smoke에서는 `best_step=0`이 유지되고 reader 불변성 검사가 통과해 초기 체크포인트 선택 경로도 실제 실행으로 확인했다. 이 smoke 수치는 성능 결과에 포함하지 않는다.

## 결론과 다음 검증

확인된 것은 미래 대화의 예측 손실로 학습되는 갱신 경로가, 비어 있지 않은 상태에서 새 단일 사실을 반영하고 잡담을 지나 유지할 수 있다는 좁은 결과다. 정답을 저장하라는 중요도 라벨이나 tool 문법은 학습에 쓰지 않았다. 하지만 사실 위치·질문 형식이 규칙적이고, 정답은 학습 때부터 본 8개 단일 토큰 단어다. 잡담도 이 정답 단어들과 경쟁하지 않는 제한된 문장 집합이다. 따라서 일반적인 중요도 판단 학습으로 확대 해석하지 않는다.

앞선 실패한 다양화와는 초기 모델의 학습 단계 및 총 예산이 다르다. 추가 400스텝, 더 잘 학습된 초기 상태, 단계적 난이도 중 무엇이 개선의 주원인인지는 이번 대조로 분리하지 못했다.

다음 검증은 학습에 없는 정답 단어, 정답 후보 단어가 섞인 경쟁 잡담, 여러 사실 및 뒤늦은 정정을 분리한 시험이다. 최종 목표인 사람 대화 일반화, 기억 텍스트 반환과 반환/침묵 타이밍은 아직 구현·검증되지 않았다.

## 재현

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_stream_memory_control.py --seed 17 --steps 400 --train-blocks 64 --valid-blocks 16 --train-noise 2 4 8 16 32 --valid-noise 2 4 8 16 32 --loss-scope future-block --update-rule gated --gate-init 0.01 --write-query-scale 0.02 --warm-start local-data/stream-rmt-control-gated-curriculum-seed17.pt --freeze-reader --allow-initial-best --output local-data/stream-rmt-control-acquire-frozen-seed17.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_stream_memory_control.py --seed 17 --steps 400 --train-blocks 64 --valid-blocks 16 --train-noise 2 4 8 16 32 --valid-noise 2 4 8 16 32 --loss-scope future-block --update-rule gated --gate-init 0.01 --write-query-scale 0.02 --warm-start local-data/stream-rmt-control-gated-curriculum-seed17.pt --allow-initial-best --output local-data/stream-rmt-control-acquire-joint-seed17.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python eval_stream_memory_stress.py --checkpoint local-data/stream-rmt-control-gated-curriculum-seed17.pt --blocks 24 --seed 3009 --output local-data/stream-rmt-control-acquire-baseline-stress-seed17.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python eval_stream_memory_stress.py --checkpoint local-data/stream-rmt-control-acquire-frozen-seed17.pt --blocks 24 --seed 3009 --compare local-data/stream-rmt-control-acquire-baseline-stress-seed17.json --output local-data/stream-rmt-control-acquire-frozen-stress-fixed-seed17.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python eval_stream_memory_stress.py --checkpoint local-data/stream-rmt-control-acquire-joint-seed17.pt --blocks 24 --seed 3009 --compare local-data/stream-rmt-control-acquire-frozen-stress-fixed-seed17.json --output local-data/stream-rmt-control-acquire-joint-stress-seed17.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python diagnose_stream_memory_position.py --checkpoint local-data/stream-rmt-control-acquire-frozen-seed17.pt --output local-data/stream-rmt-control-acquire-frozen-position-seed17.json
```

seed 7도 입력·출력 파일과 `--seed`를 같이 바꾼다. 두 조건의 새 잡담 seed는 모두 3009다. 학습 JSON에는 설정, 초기/검증/시험 지표와 가중치 불변성 검사가 있고, `.pt`에는 frozen adapter를 포함한 선택 가중치가 있다.

실제 seed 7 고정 평가 파일은 `local-data/stream-rmt-control-acquire-frozen-stress-seed7.json`이다. seed 17만 비교 입력 표현 문제 수정 뒤 재실행해 `stress-fixed-seed17` 이름을 사용했다. 앞/뒤 진단 결과는 각 조건의 `stream-rmt-control-acquire-{frozen,joint}-position-seed{7,17}.json`에 저장했다.
