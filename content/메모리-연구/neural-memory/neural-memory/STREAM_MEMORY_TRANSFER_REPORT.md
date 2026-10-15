---
title: "어휘 전이·경쟁 잡담·정정 검사 — 2026-09-27"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `neural-memory/STREAM_MEMORY_TRANSFER_REPORT.md` · 수집 2026-10-16 · **로컬 미커밋 문서 사본** (원격 커밋과 동일하다고 보장하지 않음)
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# 어휘 전이·경쟁 잡담·정정 검사 — 2026-09-27

## 결론

**현재 메모리 경로는 학습한 8개 정답 밖으로 일반화하지 못했다.** 읽기 고정/공동학습 × seed 7/17의 네 모델 모두 새 단어 중립 시험에서 전체 어휘 정답률 0/64였다. 새 단어의 여섯 시나리오 전체에서도 각각 0/384였다. 이전 긴 잡담 시험의 100%는 알려진 단어를 기억하는 좁은 성공이지 범용 기억 모델의 성공이 아니다.

같은 가중치의 reader에 과거 원문 전체를 직접 주면 seed 17의 두 모델은 같은 새 단어 64/64를 맞혔다. 따라서 새로운 단어를 원문에서 읽을 능력 자체가 없는 것은 아니다. 문제는 원문을 잠재 기억으로 획득·전달하고 그 상태를 읽는 경로의 일반화에 있다. 이번 검사만으로 writer, 보존, latent-state reader 중 하나를 단독 원인으로 확정하지 않는다.

후속 [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_OPEN_VOCAB_REPORT|값 다양성 대조]]에서는 같은 구조에서 학습 값을 256개로 늘려 별도 64개 값의 전이가 50.00~54.69%로 개선됐다. 이 문서의 실패 결과는 이전 8값 학습 모델에 대한 기록으로 유지한다. 정정 실패는 후속 실험에도 남아 있다.

## 고정한 조건

- 기존 `stream-rmt-control-acquire-{frozen,joint}-seed{7,17}.pt`를 수정 없이 평가했다. 추가 학습 0스텝, Apple MPS/float32. 완료 후 네 adapter가 저장 파일과 정확히 같은지 확인했다.
- 메모리 학습 정답: apple, moon, glass, dog, river, chair, green, stone.
- 새 정답: cat, sun, paper, bird, ocean, table, blue, cloud. **메모리 추가 학습의 정답 어휘에서 미사용**이라는 뜻이지 LM 사전학습에서 미사용이라는 뜻은 아니다. 이 목록은 GPU 성능을 보기 전에 선택하고 실제 토크나이저로 검증했다.
- 각 조건은 같은 잡담 seed 4009, 8개의 독립 잡담 블록 × 8개 답 = 64사례. 기본 잡담 8/16턴을 번갈아 사용하고, 원래 평가와 같은 뒤 잡담 3턴을 더했다.
- 2개 어휘 집합 × 6개 시나리오 × 4개 모델, 총 3,072사례. 신뢰구간은 독립 사례 수가 아니라 **8개 잡담 블록**을 재표집한다.
- 같은 블록의 8개 원문은 과거 정답 근거 토큰과 최종 정답 토큰 두 곳만 다르다. 잡담·간섭·질문은 답에 따라 바꾸지 않는다. 정답 근거가 마지막 원문 창 밖에 있는지 검사한다.
- 어휘·블록·원문 토큰 SHA-256·근거/정답 위치가 일치해야 모델끼리 비교한다. 마지막 미래 정답 토큰을 바꿔도 메모리 평가의 예측이 같다는 회귀 검사도 통과했다.

검사 시나리오는 다음과 같다.

| 이름 | 사실 이후 추가 내용 |
| --- | --- |
| neutral | 기존 생성기 그대로의 중립 잡담 |
| mentions_neutral | `Friend: The word topic appeared in the book I read.` 8회 |
| mentions | 위 문장의 topic 대신 8개 정답 후보를 각 1회 언급 |
| other_fact_neutral | `Friend: My secret word is clock.` 8회 |
| other_fact | 위 문장의 clock 대신 8개 정답 후보를 각 1회 언급 |
| correction | 앞서 `Me: My secret word is clock.`을 말하고, 새 근거를 `Me: Actually, my secret word is ...`로 정정 |

mentions/other_fact의 후보 순서는 블록마다 무작위이며 모든 정답에 동일하다. 짝지은 neutral 대조와 토큰 길이·사실/정답 위치·마지막 질문 창이 실제 토크나이저에서도 동일한지 확인했다. other_fact는 다른 화자의 사실 간섭 검사이며, 여러 속성을 각각 질의하는 본격적인 다중 사실 벤치마크는 아니다. correction은 고정된 옛 단어와 새로운 정정 문장 형식을 함께 바꾸므로 그 둘의 효과를 분리하지 않는다.

## 결과: 학습한 단어

아래는 전체 어휘에서 단일 토큰 argmax 정확도다. 알려진 단어 조건은 8지선다 정확도도 같은 값이었다.

| 시나리오 | 고정 7 | 공동 7 | 고정 17 | 공동 17 |
| --- | ---: | ---: | ---: | ---: |
| neutral | 100% | 100% | 100% | 100% |
| mentions_neutral | 100% | 100% | 100% | 100% |
| mentions | 90.63% | 65.63% | 76.56% | 95.31% |
| other_fact_neutral | 96.88% | 76.56% | 65.63% | 92.19% |
| other_fact | 73.44% | 56.25% | 68.75% | 76.56% |
| correction | 93.75% | 100% | 79.69% | 54.69% |

짝지은 mentions 대조에서 정확도 변화(후보 언급 − topic 언급)는 고정 7: −9.38%p, 공동 7: −34.38%p, 고정 17: −23.44%p, 공동 17: −4.69%p다. paired block-bootstrap의 95% 구간은 각각 [−15.63, −4.69], [−53.13, −15.63], [−45.31, −6.25], [−10.94, 0]%p다. 따라서 세 모델에서는 정확도 하락 구간이 0을 포함하지 않으며, 공동 17은 정확도 기준으로 불확실하다. 8블록의 탐색적 비교이고 다중 비교 보정은 하지 않았다.

other_fact는 clock을 반복하는 대조부터 일부 모델이 악화된다. 후보 단어를 넣었을 때의 추가 악화도 고정 17에서는 나타나지 않았다(65.63% → 68.75%, paired 구간에 0 포함). 다른 화자의 사실을 전반적으로 안정적으로 분리한다고 말할 수 없지만, 모든 seed가 동일한 간섭 양상을 보인다고도 말하지 않는다.

## 결과: 새 단어

| 모델 | 중립 8지선다 | 중립 전체 어휘 | 자기 기억 NLL | 빈 기억 NLL |
| --- | ---: | ---: | ---: | ---: |
| 고정 7 | 17.19% | 0% | 8.6152 | 6.2424 |
| 공동 7 | 23.44% | 0% | 10.3112 | 6.4738 |
| 고정 17 | 23.44% | 0% | 9.2890 | 7.2650 |
| 공동 17 | 29.69% | 0% | 9.5059 | 8.1583 |

빈 기억의 8지선다는 모두 12.50%다. 새 정답 8개로 **출력 후보를 강제로 제한**하면 일부 정보는 구별되지만, 제한 없이 답 토큰을 고르면 정답이 전혀 나오지 않는다. 이를 완전한 무정보 상태라고 단정하지는 않는다. 정답 NLL도 네 모델 모두 빈 기억보다 나빠, 현재 상태가 새 단어의 정상적인 예측에 도움이 되었다고 평가할 수 없다.

새 단어 조건 전체 1,536사례의 전체 어휘 argmax는 모두 기존 8개 학습 단어 중 하나였다. 이는 **8개 값에 맞춘 코드북/분류기처럼 행동한다는 해석**과 일치하지만, 내부 표현이 실제 8개의 이산 코드뿐이라는 증명은 아니다.

공동 17의 첫 중립 블록에서 실제 출력은 다음과 같았다. 모든 사례는 같은 잡담과 질문이며 과거 사실의 단어만 바뀐다.

| 과거 사실의 단어 | 전체 어휘 출력 |
| --- | --- |
| cat | dog |
| sun | moon |
| paper | apple |
| bird | green |
| ocean | dog |
| table | dog |
| blue | dog |
| cloud | dog |

예를 들어 `Me: My secret word is cat.` 전후로 잡담을 처리하고 `Friend: What was your secret word? / Me:`에서 예측하면 dog가 나왔다. 동일한 원문 전체를 같은 공동 17 reader에 직접 주면 cat가 나왔다. source/answer annotation을 읽기 모델에 주입하지는 않았다.

## 원문 직접 읽기 대조

기억 없이 **실제 과거 원문 전부**를 같은 Q/V adapter의 Transformer에 한 번에 주고 마지막 답 직전에서 예측했다. 미래 정답 토큰은 입력에서 아예 제외했다. 반복 기억 압축을 건너뛰는 정보 상한 대조이며, 제안하는 메모리 구조가 아니다.

| 새 단어, 같은 긴 원문 | 고정 7 | 공동 7 | 고정 17 | 공동 17 |
| --- | ---: | ---: | ---: | ---: |
| 기억 경로: 전체 어휘 정확도 | 0% | 0% | 0% | 0% |
| 원문 직접 읽기: 8지선다 | 100% | 100% | 100% | 100% |
| 원문 직접 읽기: 전체 어휘 정확도 | 14.06% | 57.81% | 100% | 100% |
| 원문 직접 읽기: 대소문자만 무시한 단어 일치 | 100% | 100% | 100% | 100% |

seed 7 원문 대조의 오답은 Cat/Sun 같은 대문자 토큰이었다. 대소문자 무시 지표는 이를 해석하려고 **사후 추가한 진단**이며, 기본 전체 어휘 단일 토큰 정확도를 대체하지 않는다. 짧은 `Me: My secret word is ...` 원문/질문 대조에서는 네 adapter 모두 새 8개 단어를 소문자 정답 그대로 맞혔다(8/8, 단일 템플릿).

adapter가 없는 원래 사전학습 LM도 함께 검사했다. 원문을 직접 주었을 때 새 단어 8지선다는 100%지만 전체 어휘 정확도는 0%였다. My/It 또는 대문자 답을 먼저 내는 경향이 있어서다. 따라서 원래 LM 자체의 자유 출력 100%를 근거로 삼지 않는다. 결정적인 대조는 **동일한 학습된 가중치·동일한 원문**에서 seed 17이 원문 직접 읽기 100%, 기억 경로 0%였다는 결과다.

## 해석과 다음 실험

확인된 실패는 열린 어휘 기억과 경쟁 잡담 내성이다. 8개 정답·규칙적 사실 문장·비경쟁 잡담만으로 훈련했기 때문에, 미래 예측 손실을 잘 줄이는 특화된 경로를 배웠을 가능성이 먼저 의심된다. **이는 학습 분포에 관한 가설**이다. 더 다양한 값의 학습이나 구조 변경을 실제 비교하기 전에는 원인을 확정하지 않는다.

다음 순서는 같은 구조/손실에서 정답 값의 다양성을 늘린 학습 대조다. 훈련에 수백 개 단일 토큰 값을 사용하고 검증/시험 정답 어휘를 서로 분리해, 미학습 값에도 전이되는지 먼저 판정한다. 저장 중요도·저장/검색 tool 라벨을 추가할 이유는 없다. 이 좁은 전이가 되지 않으면 사람 대화로 규모만 키우거나 긴 잡담 정확도만 다시 올리는 것은 충분한 검증이 아니다.

그 다음에 다른 화자/다른 속성의 사실, 정정, 경쟁 잡담을 학습과 독립된 형식으로 검사한다. 최종 목표인 사람 대화의 일반적 저장 판단, 여러 사실의 선택적 유지·망각, 기억 텍스트 출력, 자동 반환/침묵은 여전히 구현·검증되지 않았다.

## 구현·검사·재현

- `controls_from_cases`로 기존 tokenizer/stream 경로를 재사용했다. 기존 중립 생성기의 원문·span이 정확히 같다는 회귀 검사를 추가했다.
- 준비 검사, 답별 잡담 동일성, 서로 다른 후보 토큰, 마지막 창 근거 누출, 앞선 원문 단어/정정 근거, 매칭 조건 위치, 미래 답 토큰 독립성, 원문 대조의 미래 답 완전 제외, 잘못된 paired 비교 거부를 검사했다.
- codecanvas 색인에서 새 실험 함수가 검색되지 않아 변경 영향에 대한 정적 그래프 증거는 얻지 못했다. 기존 경로 동등성 및 실제 CPU/GPU 실행으로 검증 범위를 명시했다.
- 전체 검사 **521 passed, 1 기존 requires-grad scalar 경고**. GPU 평가 네 건 및 원문 진단은 모두 정상 완료했고, 체크포인트 가중치가 바뀌지 않았다.

프로젝트의 `neural-memory/`에서 실행한다.

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python eval_stream_memory_transfer.py --checkpoint local-data/stream-rmt-control-acquire-joint-seed7.pt --output local-data/stream-rmt-transfer-joint-seed7.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python eval_stream_memory_transfer.py --checkpoint local-data/stream-rmt-control-acquire-joint-seed17.pt --compare local-data/stream-rmt-transfer-joint-seed7.json --output local-data/stream-rmt-transfer-joint-seed17.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python diagnose_stream_memory_vocabulary.py --checkpoints local-data/stream-rmt-control-acquire-frozen-seed7.pt local-data/stream-rmt-control-acquire-joint-seed7.pt local-data/stream-rmt-control-acquire-frozen-seed17.pt local-data/stream-rmt-control-acquire-joint-seed17.pt --output local-data/stream-rmt-transfer-native-readers.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python summarize_stream_memory_transfer.py --reports local-data/stream-rmt-transfer-frozen-seed7.json local-data/stream-rmt-transfer-joint-seed7.json local-data/stream-rmt-transfer-frozen-seed17.json local-data/stream-rmt-transfer-joint-seed17.json --native local-data/stream-rmt-transfer-native-readers.json --output local-data/stream-rmt-transfer-summary.json
```

고정 조건은 첫 두 명령의 `joint`를 `frozen`으로 바꾼다. 준비만 검사하려면 `--prepare-only`를 사용한다. 기존 최선 모델 선택이나 가중치 학습에는 이번 평가 자료를 사용하지 않았다.
