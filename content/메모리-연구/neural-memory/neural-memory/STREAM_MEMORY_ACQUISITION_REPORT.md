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

이번 인공 단일 사실 과제에서는 읽기 가중치를 고정한 모델과 함께 학습한 모델이 모두 개선됐다. 새 32·64턴 잡담 시험에서 두 조건의 두 seed는 각각 192/192를 전체 어휘 기준으로 맞혔다. 따라서 읽기 고정이 필수라는 증거는 없지만, **읽기 가중치를 바꾸지 않고 기억 갱신 파라미터만 학습해도 이 과제를 개선할 수 있음**은 확인했다. 일반 사람 대화에서 무엇을 저장해야 하는지 학습했다는 결론까지 내리지는 않는다.

후속 [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_TRANSFER_REPORT|어휘 전이 보고서]]에서 이 성공의 경계를 확인했다. 네 모델 모두 새 단어의 기억 경로 정확도는 0%였고, 후보 단어가 등장하는 잡담과 다른 화자의 사실에도 간섭을 받았다. 아래의 알려진 8개 단어 결과를 열린 어휘 기억의 성공으로 해석하지 않는다.

## 실험 목적과 범위

앞선 실험에서 성능이 낮았던 seed는 사실 앞에 잡담 4구간을 넣으면 25%, 같은 잡담을 사실 뒤에 넣으면 100%였다. 이번 질문은 이렇게 기존 상태가 있을 때의 새 사실 획득을 개선하는 데 읽기 가중치까지 바꿔야 하는가다. 이를 확인하려고 읽기/QV 가중치를 고정한 조건과 공동학습 조건을 비교했다. 사람이 지정한 저장 중요도 라벨이나 과거 정답 토큰을 직접 전달하는 경로는 사용하지 않았다.

“읽기 고정”의 범위에는 주의가 필요하다. 현재 Transformer는 읽기와 쓰기 처리를 공유하므로, 이 조건에서는 **공유 Transformer의 Q/V 저차원 가중치도 고정**된다. 별도의 쓰기 전용 Transformer를 학습하는 실험은 아니다.

고정 조건에서 학습하는 것은 기억 bridge, gate, suffix query의 338,113개 파라미터다. 공동학습 조건은 여기에 Q/V를 포함해 568,513개를 학습한다.

두 조건은 같은 seed의 이전 **oracle-prefix 없는 단계적 학습 체크포인트**에서 출발했다. 기존 짧은 단계 400 + 긴 단계 400에 이번 400을 추가하므로 전체 예산은 1,200스텝이다.

따라서 이전 800스텝 모델보다 좋아졌다는 사실만으로 읽기 고정의 효과를 주장할 수는 없다. 핵심 비교는 시작 가중치·자료·학습량을 맞춘 고정 조건과 공동학습 조건 사이의 차이다.

## 학습·선택

- 학습 자료는 64블록/512사례, 검증 자료는 16블록/128사례다. 잡담은 2·4·8·16·32턴에 뒤 잡담 3턴을 더했다.
- 배치 크기 2, 구간 길이 32, rank 4, 학습률 0.0003을 사용했다. 기울기 노름은 1로 제한하며 Apple MPS/float32에서 실행했다.
- 각 독립 대화의 기억은 0에서 시작한다. 실제 원시 텍스트를 시간순으로 처리하고 구간 사이 상태의 역전파를 끊지 않는다.
- 손실은 마지막 미래 구간의 모든 대화 내용에 대한 다음 토큰 교차엔트로피(CE)다. 사실/정답 위치 표시는 오라클 없는 학습 손실에 사용하지 않는다.
- 검증 자료에서 자기 기억을 사용한 정답 NLL로 최선 체크포인트를 선택한다. **초기 체크포인트(0스텝)도 선택 가능**하므로, 추가 학습으로 악화된 모델을 억지로 채택하지 않는다.
- 고정 조건은 실행마다 최종 학습 가중치와 시작 Q/V 어댑터를 정확히 비교한다. 선택한 최선 가중치로 되돌리기 **전**에 확인해 학습 도중의 변경이 복원 과정에 가려지지 않게 한다.

시작 체크포인트를 만들 때의 자료와 이번 자료는 분포가 다르다. 그래서 초기·최종 모델의 검증값은 모두 이번에 새로 만든 검증 자료에서 계산했다. 이 전후 비교는 같은 모델 조건 안에서 추가 학습의 영향을 보는 개입이다.

## 평가

기존 96사례 시험은 이미 반복해서 확인한 탐색적 평가다. 이와 별도로 새 잡담(seed 3009)의 24블록/192사례를 만들어 이전 모델과 읽기 고정/공동학습 모델을 같은 입력으로 비교했다. 잡담 길이는 8·16턴과 32·64턴이며, 이 자료는 체크포인트 선택에 사용하지 않았다.

위치 진단에서는 이전과 같은 사실과 마지막 원문 구간을 유지하고, 잡담 0·4·8·16·32구간을 사실 앞 또는 뒤에 추가했다. 이 토큰 블록 검사는 한 인공 템플릿의 8사례만 사용하므로 새 잡담을 통한 일반화 평가와 구분한다.

기존 96사례 test 결과는 다음과 같다.

| 조건 | seed | 선택 스텝 | 8지선다 | 전체 어휘 단일 토큰 | 정답 NLL |
| --- | ---: | ---: | ---: | ---: | ---: |
| 읽기 고정 | 7 | 375 | 100% | 92.71% | 0.24900 |
| 공동학습 | 7 | 375 | 100% | 97.92% | 0.02525 |
| 읽기 고정 | 17 | 175 | 100% | 98.96% | 0.03500 |
| 공동학습 | 17 | 175 | 100% | 100% | 0.00091 |

기억을 비우면 모든 모델의 8지선다 정확도는 12.50%였다. 다른 대화의 기억으로 바꾸면 원래 단어는 0%, 기억을 제공한 대화의 단어는 100%였다.

읽기 고정의 두 seed에서는 `frozen_reader_unchanged=true`, `backbone_gradient_present=false`를 확인했다. 빈 상태와 과거 단어 오라클의 NLL도 이전의 같은 읽기 모델 값과 일치했다. 따라서 이 조건의 개선은 읽기 가중치를 바꾼 결과가 아니라 기억 갱신 파라미터를 학습한 결과다.

공동학습도 좋은 성능을 냈으므로 **읽기 고정이 필수이거나 공동학습보다 항상 낫다는 결론은 아니다.** 앞서 실패했던 다양화 실험과는 시작 체크포인트와 총 학습량이 다르다. 여기서 확인한 것은 더 긴 단계까지 학습된 모델에서 출발해 추가 학습하면, 고정된 읽기 모델에 맞는 갱신 경로도 이 과제를 배울 수 있다는 점이다.

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

긴 잡담에서 개선 폭의 불확실성을 확인하려고 동일한 24블록을 짝지어 2,000회 재표집했다. 이 짝지은 부트스트랩에서 이전 모델 대비 고정 모델의 **전체 어휘 정확도 개선**은 seed 7에서 +39.58%p (95% 구간 +23.96~+56.25%p), seed 17에서 +77.08%p (+67.71~+84.38%p)였다.

이 구간은 같은 인공 자료 분포 안에서의 비교다. 더 넓은 대화 분포에 대한 신뢰구간으로 해석하지 않는다. 모두 맞힌 조건의 부트스트랩 구간이 [100%, 100%]여도 일반 모집단에서 오류가 없다는 뜻은 아니다.

공동학습 대비 고정의 우위는 나타나지 않았다. 두 seed의 긴 잡담 정확도는 같고, seed 17의 짧은 잡담에서 공동학습은 전체 어휘 기준 +3.65%p (paired 95% 구간 +0.52~+8.33%p) 높았다. 이 결과는 reader를 고정해야만 학습된다는 가설을 지지하지 않는다.

### 앞/뒤 잡담 개입

사실 앞 또는 뒤에 잡담 0·4·8·16·32 token-block을 넣는 총 10조건에서, 두 seed의 고정/공동학습 모델 모두 8지선다와 전체 어휘 정확도 100%였다. 이전 약한 seed 17의 사실 앞 4·8·16·32구간 정확도 25%가 100%로 회복됐다. 이미 이전부터 통과했던 강한 seed 7도 유지됐다.

이 진단은 각 조건당 같은 단일 템플릿의 8사례뿐이다. 새로 생성한 잡담 시험과도 평가 범위가 다르며, 여러 독립 사실을 구분하거나 충돌하는 사실을 정정할 수 있다는 증거로 쓰지 않는다.

## 저장·검사

읽기 모델을 고정했더라도 해당 Q/V 어댑터는 체크포인트에 저장해야 한다. `requires_grad`인 텐서만 저장하면 학습하지 않는 읽기 가중치가 빠져 평가 때 복원되지 않기 때문이다. 이를 막기 위해 **고정하기 전 어댑터 이름을 수집하고 모두 별도 사본으로 저장**했다. 큰 기존 LM 본체는 이전과 마찬가지로 포함하지 않는다.

저장과 복원도 따로 검사했다. CPU에 저장한 사본이 실행 중 파라미터와 같은 저장 공간을 공유하지 않는지, 읽기 모델을 고정한 뒤에도 미래 손실이 bridge/gate/query까지 도달하는지, 읽기 모델에는 기울기나 가중치 변경이 없는지를 확인했다. 고정된 읽기 가중치를 포함한 체크포인트가 정상 복원되는지와 저장 중요도 표시가 손실에 영향을 주지 않는지도 검사했다.

새 잡담 평가에는 모델 간 짝지은 블록 부트스트랩 비교를 추가했다. 블록·사실 위치·질문 위치가 다르면 비교를 거부한다. 전체 검사에서 481개가 통과했고 기존 경고 1개가 남았다.

처음의 짝지은 평가는 같은 잡담 선택을 서로 다르게 표현해 비교 검사에서 중단됐다. 실행 중에는 tuple, 저장 JSON에는 list를 사용한 것이 원인이었다. 표현을 정규화하고 회귀 검사를 추가한 뒤 해당 고정 seed 17 평가를 다시 실행했고, 공동학습 비교도 정상 완료했다. 학습이나 모델 계산에는 영향이 없었다. 보고한 수치는 완료된 재실행 파일에서만 가져왔다.

별도의 1스텝/lr=0 GPU 동작 확인에서도 `best_step=0`이 유지되고 읽기 가중치 불변성 검사가 통과했다. 이로써 초기 체크포인트를 선택하는 경로가 실제 실행에서도 작동함을 확인했다. 이 동작 확인의 수치는 성능 결과에 넣지 않는다.

## 결론과 다음 검증

이번에 확인한 범위는 좁다. 미래 대화 예측 손실로 학습한 갱신 경로가 **이미 비어 있지 않은 상태에 새 단일 사실을 반영하고, 잡담이 이어져도 유지할 수 있었다.** 정답을 저장하라는 중요도 라벨이나 도구 호출 문법은 학습에 쓰지 않았다.

그러나 사실 위치와 질문 형식은 규칙적이고, 정답은 학습 때부터 본 8개 단일 토큰 단어다. 잡담도 정답 단어와 경쟁하지 않는 제한된 문장 집합이다. 이 조건을 넘어 일반적인 저장 중요도 판단까지 배웠다고 해석하지 않는다.

앞선 다양화 실패와 비교할 때에는 출발 모델의 학습 단계와 총 예산이 모두 달라졌다. 추가 400스텝의 효과인지, 더 잘 학습된 시작 상태의 효과인지, 단계적으로 난이도를 높인 효과인지 이번 대조만으로는 주원인을 분리할 수 없다.

다음에는 학습에 없던 정답 단어, 정답 후보가 섞인 경쟁 잡담, 여러 사실, 뒤늦은 정정을 각각 분리해 시험한다. 최종 목표인 사람 대화로의 일반화, 기억 텍스트 반환, 반환할 때와 침묵할 때를 고르는 기능은 아직 구현·검증되지 않았다.

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
