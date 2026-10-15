---
title: "기억 갱신 경로 진단 — 2026-09-27"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `neural-memory/STREAM_MEMORY_UPDATE_REPORT.md` · 수집 2026-10-16 · **로컬 미커밋 문서 사본** (원격 커밋과 동일하다고 보장하지 않음)
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# 기억 갱신 경로 진단 — 2026-09-27

후속 같은 800스텝 대조와 거리·위치 다양화 평가: [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_GENERALIZATION_REPORT|일반화 보고서]]. 아래는 갱신 구조와 첫 curriculum 실험의 기록이다.

결론: **빈 기억에서 과거 대화를 읽고, 저장 중요도 라벨 없이 단일 사실을 학습·사용하는 경로를 얻었다.** gate/공유 query를 추가하고 짧은 거리부터 학습했을 때 두 seed의 시험 정확도는 8지선다 98.96% / 57.29%, 전체 어휘 83.33% / 56.25%였다. 기억을 비우면 둘 다 12.50%였고 교환하면 기증 대화의 단어를 답했다. 다만 seed·거리 일반화 편차가 크며 최종 목표인 일반 대화 기억·자동 텍스트 반환은 아직 아니다.

## 확인한 문제와 수정

이미 읽을 수 있는 기억도 기존 순환 갱신이 훼손했다. 원시 대화만으로 학습할 수 없다는 증명이 아니라, 현재 구현에서 보존 경로와 학습 시작 조건을 고쳐야 한다는 좁은 결과다.

`diagnose_stream_memory_update.py`는 이전 읽기 오라클 체크포인트의 모든 파라미터를 고정한다. **실제로 과거에 등장한 단어**를 한 번 상태로 초기화한 후, 정답 정보 없는 동일 잡담 블록을 반복해서 처리한다. 모든 조건에서 읽기 가중치와 질문은 같다. 초기 사실 위치 라우팅은 특권이므로 이 검사는 저장 학습 성공이 아니라 이미 읽을 수 있는 상태의 보존 검사다.

96사례, 12개 동일 잡담/질문 대조 블록에서 측정했다. 정답률은 8지선다, 전체 어휘 정확도는 단일 토큰 argmax다.

| 상태 갱신 | 잡담 갱신 횟수 | 8지선다 정확도 | 전체 어휘 정확도 |
| --- | ---: | ---: | ---: |
| 갱신 전 과거 단어 상태 | 0 | 93.75% | 83.33% |
| 전부 덮어쓰기 | 1 | 15.63% | 4.17% |
| 전부 덮어쓰기 | 16 | 13.54% | 3.13% |
| 고정 1% blend, 진단용 | 16 | 91.67% | 83.33% |
| 그대로 유지, 진단용 | 16 | 93.75% | 83.33% |

한 대조 블록에서 최종 정답 NLL의 state gradient를 역전파하면 덮어쓰기의 `초기 상태 gradient norm / 최종 상태 gradient norm`은 8회 갱신 약 17,931배, 16회 약 1.26억 배였다. 1% blend의 16회 값은 0.861배였다. 특정 손실 방향의 기울기 증폭이며 Jacobian의 최대 특잇값이나 전체 학습의 유일한 실패 원인으로 해석하지 않는다.

수정은 두 가지를 별도 옵션으로 추가했다.

- `gated`: 이전 상태의 직접 전달 경로와 학습 가능한 슬롯별 갱신 게이트. 초기 gate는 0.01이고 이후 학습한다. 비어 있던 첫 상태는 관측 구간으로 채운다.
- 공유 쓰기 query: 쓰기 위치에 작은 학습 파라미터를 추가한다. 개인 정보가 아니라 모든 대화에서 공유하는 파라미터이며, 개인의 초기 기억은 여전히 0이다. 현재 텍스트는 이 쓰기 위치를 볼 수 없다.

이전 덮어쓰기 구현은 기본값으로 유지했다. 저장/검색 명령, 외부 사실 레코드, 벡터 DB를 추가한 것이 아니다. gate와 query도 대화 예측 손실로 학습한다.

## 같은 읽기 사전학습에서 시작한 대조

모든 행이 동일한 읽기 오라클 체크포인트에서 시작한다. 이후 400스텝은 빈 기억에서 실제 과거 대화를 처리하고 마지막 미래 구간의 **모든 대화 내용**을 예측한다. 이 단계에는 사실 위치 라우팅이나 저장 중요도 라벨이 없다. 다만 시작 체크포인트가 특권 읽기 학습을 거쳤으므로, 전체 학습이 원시 대화만이었다고 주장하지 않는다.

seed 7, train 64/valid 32/test 96사례, batch 2, chunk 32, AdamW lr 0.0003, norm 1 clipping. valid 자기 상태 NLL로 체크포인트를 선택했다. 후보 8개 단어와 대화 틀은 학습과 시험에 공통이며 잡담·사실 위치는 달라진다.

| 변경 | 선택 스텝 | 시험 8지선다 | 전체 어휘 | 빈 상태 8지선다 |
| --- | ---: | ---: | ---: | ---: |
| 기존 덮어쓰기 | 400 | 12.50% | 10.42% | 12.50% |
| gate만 | 400 | 15.63% | 13.54% | 12.50% |
| 공유 query만 | 300 | 12.50% | 10.42% | 12.50% |
| gate + 공유 query | 375 | 86.46% | 80.21% | 12.50% |

수정 모델에서 다른 대화의 기억을 넣으면 원래 단어 정답률은 2.08%, 기증 대화의 단어 정답률은 86.46%였다. 따라서 현재 문맥/읽기 가중치만으로 푸는 것이 아니라 기억에 들어 있는 사실에 답이 반응한다. 그러나 이 한 과제에서 얻은 결과를 일반적 저장 판단이나 반환 타이밍으로 확장하지 않는다.

같은 수정 모델의 새로운 잡담 추출(seed 1009)에서도 8·16턴 조건 73.96%, 32·64턴 조건 59.38%였다. 후자는 15~28개 구간에 해당하며 전체 어휘 정확도는 56.25%, 빈 상태는 12.50%였다. 길어지면 성능이 낮아진다. 새로운 단어/질문/사실 종류를 시험한 것은 아니다.

## 읽기 오라클 없이 시작하는 학습

언어 모델의 기존 언어 능력은 사용하되 기억 파라미터는 새로 초기화한다. 수정 구조를 곧바로 기존 길이에서 400스텝 학습한 시험 정확도는 15.63%였다. 그러므로 구조 수정만으로 원시 대화 공동학습이 해결됐다고 볼 수 없다.

다음은 사실 위치를 알려 주지 않고 짧은 거리부터 시작하는 curriculum이다. 첫 단계는 잡담 0·1턴 + 뒤 잡담 1턴, 두 번째는 기존 잡담 2·4·8턴 + 뒤 잡담 3턴이다. 첫 단계에서도 원래 사실이 마지막 원문 구간에 없다는 검사를 통과해야 한다. 구간별 중요도 라벨 대신 마지막 구간의 관측 텍스트를 예측하며, 모든 앞선 구간에 역전파한다.

seed 7의 첫 단계 400스텝은 짧은 valid에서 100%를 맞혔지만 기존 긴 test는 19.79%였다. seed 17의 첫 단계도 짧은 valid에서 100%였고 긴 test는 41.67%였다. 즉 짧은 기억 거리의 학습과 긴 기억 거리로의 일반화는 다르다.

seed 7은 짧은 거리 체크포인트에서 긴 거리 400스텝을 이어 학습한 뒤(합계 800스텝, optimizer는 새로 초기화) valid NLL로 375스텝을 선택했다. 시험 96사례 중 95개, **8지선다 98.96% / 전체 어휘 83.33%**였다. 빈 상태는 12.50%, 교환 상태는 원래 단어 0%, 기증 단어 98.96%였다. 이 실행의 기억 학습에는 oracle-prefix를 사용하지 않았다.

새 잡담 추출에서도 8·16턴 조건 92.71%(전체 어휘 80.21%), 32·64턴 조건 70.83%(전체 어휘 70.83%)였다. 후자는 466~860토큰, 15~28구간이며 빈 상태는 12.50%였다. 긴 거리는 여전히 성능이 떨어진다.

긴 거리 학습까지의 두 seed 결과는 다음과 같다. 두 번째 seed의 재현은 첫 seed보다 상당히 낮았다.

| seed | 긴 단계 선택 스텝 | 시험 8지선다 | 전체 어휘 | 빈 상태 8지선다 | 교환 상태 원래/기증 단어 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 7 | 375 | 98.96% | 83.33% | 12.50% | 0% / 98.96% |
| 17 | 400 | 57.29% | 56.25% | 12.50% | 6.25% / 57.29% |

두 seed는 짧은 valid와 긴 단계 valid에서 100%에 도달했지만 시험 성능은 다르다. 잡담 위치·거리의 일반화가 안정적이지 않다. seed 변경은 초기화, 학습 순서, 잡담 추출을 모두 바꾸므로 어느 하나의 영향으로 분해하지 않는다.

동일한 stress 잡담 추출을 seed 17 모델에 적용하면 8·16턴은 48.96%(전체 어휘 40.63%), 32·64턴은 21.88%(전체 어휘 21.88%)였다. seed 7의 92.71% / 70.83%만을 장기 보존 성능으로 대표시키면 안 된다. 두 모델 모두 stress 조건의 빈 상태는 12.50%였다.

8지선다 정답률은 자유 출력 정확도가 아니다. seed 7의 기본 시험에서 전체 어휘 정답률이 83.33%이고 정답 NLL은 2.59785였다. 후보 중에서는 맞는 단어를 선호해도 어휘 전체에서는 다른 토큰을 더 높게 평가할 수 있다. 이 차이를 숨기지 않는다.

curriculum은 총 800스텝, 곧바로 긴 거리의 cold 실행은 400스텝이었다. 같은 예산의 800스텝 cold 대조를 수행하지 않았으므로 **curriculum이 유일한 원인이거나 필수라는 주장까지 하지는 않는다.** 확인한 것은 특권 사실 라우팅 없이도 이 학습 경로로 단순한 개인별 사실을 사용할 수 있다는 점이다.

## 검사와 한계

전체 검사 467 passed, 1 기존 경고. 새 구조에 대해 초기 빈 읽기/인과성(eager, SDPA), padding/빈 구간 불변성, 미래 손실에서 gate/query로의 역전파, checkpoint 누락 검출, 사실·정답 annotation을 바꿔도 non-oracle 학습 손실이 같음을 검사했다. 모든 실험은 Apple MPS/float32로 실행했다.

첫 bridge gradient norm은 warm 덮어쓰기 약 298만, query만 약 3.12억, gate만 약 1.78만, 둘 다 약 6,956이었다. 모두 학습 전에 clipping한다. 소수 첫 배치 값이므로 일반적인 안정성 순위나 성공 원인의 독립적 증명으로 삼지 않는다.

반복 확인한 작은 인공 시험이므로 탐색적 결과다. 아직 사람 대화 유효성, 여러 사실 보존/정정, 보지 않은 사실 종류, 기억 텍스트 출력, 반환/침묵 타이밍을 입증하지 않았다.

다음은 같은 예산의 cold 대조와 더 다양한 거리/잡담 위치로 일반화 편차를 검사한 후, 복수 사실·정정·새 단어 및 실제 사람 대화로 확대하는 것이다. 자동 반환/침묵 인터페이스는 이와 별도 검증이 필요하다.

## 실행 및 산출물

`local-data/stream-rmt-update-diagnostic-seed7.json`에 전체 보존/기울기 진단이 있다. `stream-rmt-control-{overwrite,gate-only,queries-only,gated}-warm-seed7.json/.pt`는 동일 초기 읽기 가중치 대조다. `stream-rmt-control-gated-warm-stress-seed7.json`은 새 잡담/긴 거리 평가다. `stream-rmt-control-gated-cold-seed7.json/.pt`는 읽기 오라클 없이 곧바로 기존 길이에서 학습한 실행이다.

`stream-rmt-control-gated-cold-short-seed{7,17}.json/.pt`와 `stream-rmt-control-gated-curriculum-seed{7,17}.json/.pt`가 oracle-prefix 없는 짧은/긴 단계다. 새 잡담/긴 거리 평가는 `stream-rmt-control-gated-curriculum-stress-seed{7,17}.json`에 있다. 이 문서의 중괄호 표기는 해당 이름의 여러 파일을 뜻한다.

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python diagnose_stream_memory_update.py --checkpoint local-data/stream-rmt-control-oracle-future-selection-fixed-seed7.pt --output local-data/stream-rmt-update-diagnostic-seed7.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_stream_memory_control.py --steps 400 --loss-scope future-block --update-rule gated --gate-init 0.01 --write-query-scale 0.02 --train-noise 0 1 --valid-noise 0 1 --train-trailing-noise 1 --valid-trailing-noise 1 --output local-data/stream-rmt-control-gated-cold-short-seed7.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_stream_memory_control.py --steps 400 --loss-scope future-block --update-rule gated --gate-init 0.01 --write-query-scale 0.02 --warm-start local-data/stream-rmt-control-gated-cold-short-seed7.pt --output local-data/stream-rmt-control-gated-curriculum-seed7.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python eval_stream_memory_stress.py --checkpoint local-data/stream-rmt-control-gated-curriculum-seed7.pt --output local-data/stream-rmt-control-gated-curriculum-stress-seed7.json
```

seed 17 재현은 짧은/긴 단계 모두 `--seed 17`과 해당 seed의 입력·출력 파일을 사용한다. stress seed는 두 모델 모두 기본값 1009다.
