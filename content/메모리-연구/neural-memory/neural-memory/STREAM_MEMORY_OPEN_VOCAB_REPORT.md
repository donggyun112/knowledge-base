---
title: "값 다양성 대조와 미학습 값 전이 — 2026-09-27"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `neural-memory/STREAM_MEMORY_OPEN_VOCAB_REPORT.md` · 수집 2026-10-16 · **로컬 미커밋 문서 사본** (원격 커밋과 동일하다고 보장하지 않음)
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# 값 다양성 대조와 미학습 값 전이 — 2026-09-27

## 확인된 결과

**구조를 바꾸지 않고 학습 정답 값의 다양성을 늘리자, 미학습 값의 기억 전이가 두 seed에서 개선됐다.** 별도 64개 시험 값/128사례의 전체 어휘 정확도는 seed 7에서 0% → 54.69%, seed 17에서 0% → 50.00%였다. 같은 최대 추가 학습 예산의 8값 대조는 모두 0%였다. 단순히 오래 학습한 효과만으로 이번 차이를 설명할 수 없다.

새 잡담 및 32·64턴 조건에서도 전이가 유지됐다. 그러나 **정정은 해결되지 않았고 일부 조건에서 악화됐다.** 이전 값 clock을 계속 출력하는 실패를 확인했다. 따라서 열린 값의 단일 사실 전달은 개선됐지만, 선택적 갱신·사람 대화 일반화·기억 텍스트/침묵 타이밍이 완성됐다는 뜻은 아니다.

후속 [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_REVISION_REPORT|정정 학습 보고서]]에서는 같은 구조로 변경 대화를 학습해 이 clock 정정 실패를 크게 줄였다. 이 문서의 이전 결과는 보존하며, 후속 실험에서도 반복 간섭의 회귀와 미학습 표현의 남은 실패를 별도로 기록한다.

## 실제 수행한 대조

같은 seed의 기존 `stream-rmt-control-acquire-joint-seed{7,17}.pt`를 두 조건의 공통 시작점으로 사용했다. 모든 실행은 Apple MPS/float32, 기존 8슬롯·576차원 상태와 gated/query 구조, Q/V 저차원 갱신 및 bridge/gate/query 총 568,513 학습 파라미터를 유지했다. 대화 초기 기억은 여전히 0이며 상태 크기도 18 KiB다.

학습 값 목록은 **공개 MSC train의 사람 대화 4,000개에서 단어 빈도만 추출**해 만들었다. 단일 토큰 후보 12,787개 중 빈도가 높은 512개에서 고정 seed 9013으로 선택·분리했다. 실제 학습 문장은 여전히 인공 secret-word 대화다. 사람 대화 전체로 기억을 학습한 실험이라고 부르지 않는다.

| 답 값 집합 | 수 | 사용 |
| --- | ---: | --- |
| 학습 | 256 | 원래 8값 포함, 나머지 값 추가 |
| 검증 | 32 | 학습 값과 별개, checkpoint 선택만 사용 |
| 새 시험 | 64 | 학습·검증 값과 별개, 학습 완료 후 평가 |
| 이전 실패 검사 | 8 | cat/sun/paper/bird/ocean/table/blue/cloud, 이번 학습·검증에도 제외 |

모든 split의 답 문자열과 실제 토큰 ID는 서로 겹치지 않는다. 새 값은 정해진 잡담/질문 단어에서도 제외했다. 미학습은 **메모리 학습의 답 값으로 미사용**이라는 뜻이지 LM 사전학습 미사용이라는 뜻은 아니다.

다양한 조건은 256개 값을 사용하고, 8값 조건은 원래 8개를 32번 반복해 같은 크기의 목록을 만들었다. 두 조건 모두 96블록/768대화, 잡담 2·4·8턴을 완전한 값 목록 사이클마다 적용했다. source/answer 토큰만 가린 전체 학습 입력 SHA-256은 네 실행 모두 같았다. 같은 seed에서는 같은 행을 같은 순서로 뽑고, 내용 손실 토큰 예산도 같았다(seed 7: 10,477, seed 17: 10,635).

최대 추가 600스텝, batch 2, lr 0.0003, gradient norm 1 clipping, 50스텝마다 검증했다. 손실은 같은 **마지막 미래 구간의 모든 대화 내용 next-token CE**다. 저장 중요도·저장 여부·과거 사실 라우팅·tool 문법 라벨은 사용하지 않았다. 사실/답 annotation을 바꿔도 손실이 같고 writer 파라미터에 gradient가 생기는지 검사했다.

초기 checkpoint도 선택 가능하고, 별도 32값 검증 NLL로 최선을 선택했다. 선택 스텝은 8값 seed 7/17: 50/150, 다양한 값 seed 7/17: 550/500이다. **최대 예산과 선택 규칙이 같은 대조**이지 선택된 가중치가 모두 600번 갱신됐다는 뜻은 아니다. 600스텝 마지막 가중치도 별도 `-last.pt`로 보존했다.

## 주 시험: 별도 64개 값

각 모델은 동일한 64개 값 × 새 잡담 2배치 = 128사례를 평가했다. 주 지표는 후보 제한 없이 LM 전체 어휘에서 고른 단일 토큰의 정확도다.

| seed | 조건 | 8지선다 | 전체 어휘 | 정답 NLL |
| --- | --- | ---: | ---: | ---: |
| 7 | 8값 대조 | 14.06% | 0% | 18.1799 |
| 7 | 다양한 값 | 81.25% | 54.69% (70/128) | 4.4670 |
| 17 | 8값 대조 | 14.06% | 0% | 18.7604 |
| 17 | 다양한 값 | 80.47% | 50.00% (64/128) | 4.5141 |

두 다양한 모델의 빈 기억·교환 기억은 전체 어휘 정확도 0%였다. 빈 기억의 8지선다는 12.50%이고, 교환 기억에서 원래 답의 8지선다는 2.34%/3.13%로 떨어졌다. 기증 답을 따르는 8지선다는 자기 상태의 81.25%/80.47%와 같았다. 기억을 사용하지 않고 새 답을 맞혔다고 해석할 수 없다.

반복된 같은 8값 그룹의 두 잡담 배치를 묶어 **8개의 답 그룹**을 bootstrap한 정확도 개선의 95% 탐색적 구간은 seed 7에서 +41.41~+68.75%p, seed 17에서 +37.50~+62.50%p다. 128행을 독립 표본으로 취급하지 않았다. 작은 인공 표본에 한정하며 다중 비교 보정은 하지 않았다.

오답은 대소문자만 다른 것이 아니었다. 사후 대소문자 무시 진단도 각각 54.69%/50.00%로 같았고, 틀린 단어 출력은 각각 58건/64건(각 128사례)이었다. 이 진단으로 주 지표를 바꾸지 않았다.

## 새 잡담·긴 거리 시험

같은 미학습 64개 값에 별도 잡담 seed 6009를 사용했다. 각 칸은 128사례의 전체 어휘 정확도다.

| 모델 | 새 잡담 8·16턴 | 새 잡담 32·64턴 |
| --- | ---: | ---: |
| 8값 seed 7 | 0% | 0% |
| 다양한 값 seed 7 | 59.38% | 61.72% (79/128) |
| 8값 seed 17 | 0% | 0% |
| 다양한 값 seed 17 | 56.25% | 65.63% (84/128) |

다양한 모델의 빈/교환 기억은 두 거리 조건 모두 전체 어휘 0%였다. 긴 조건의 다양한 값 − 8값 개선의 답 그룹 bootstrap 구간은 seed 7에서 +52.34~+70.31%p, seed 17에서 +52.34~+76.56%p다. 짧은 조건과 긴 조건은 잡담 draw/사실 위치도 달라 **길어질수록 좋아진다는 인과 주장**은 하지 않는다. checkpoint를 이 시험으로 다시 고르지 않았다.

## 재검사에서 드러난 남은 실패

이전 [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_TRANSFER_REPORT|전이 검사]]의 원문/seed 4009를 그대로 다시 사용했다. 아래는 다양한 모델의 전체 어휘 정확도이며, 각 조건은 64사례다.

| 어휘 | 시나리오 | seed 7 | seed 17 |
| --- | --- | ---: | ---: |
| 원래 8개 | 중립 | 100% | 100% |
| 원래 8개 | 후보 단어 언급 잡담 | 96.88% | 96.88% |
| 원래 8개 | 다른 화자의 후보 사실 | 82.81% | 95.31% |
| 원래 8개 | 본인 정정 | 62.50% | 23.44% |
| 이전 미학습 8개 | 중립 | 62.50% | 78.13% |
| 이전 미학습 8개 | 후보 단어 언급 잡담 | 59.38% | 70.31% |
| 이전 미학습 8개 | 다른 화자의 후보 사실 | 45.31% | 60.94% |
| 이전 미학습 8개 | 본인 정정 | 7.81% | 3.13% |

새 값 중립 검사에서 이전의 0%는 개선됐다. 하지만 본인 정정의 원래 8값은 이전 공동학습 seed 7/17의 100%/54.69%보다 나빠졌다. `My secret word is clock` 뒤에 `Actually, my secret word is cat`처럼 변경했을 때, 이전 미학습 8값 정정에서는 seed 7이 54/64, seed 17이 62/64번 **옛 clock을 출력**했다. 변경 사실을 제대로 반영하지 못하는 직접적인 실패다. gate 하나가 원인이라고 확정하는 실험은 아니다.

다른 화자가 clock을 반복하는 별도 대조도 새 8값에서 26.56%/1.56%에 불과했다. 간섭 내성을 해결했다고 말하지 않는다. 후보를 제한하면 상당한 정보를 구별해도 전체 어휘 답은 clock이 될 수 있어, 8지선다만으로 성공을 판정하지 않는다.

다른 헤더/잡담 배치의 `original_values` 시험은 두 방법 모두 75%였고, 위의 동일한 기존 중립 재검사는 100%였다. 서로 다른 입력 배치를 합치거나 기존 값 유지가 모든 형식에서 완벽하다고 주장하지 않는다.

## 검증·보존·재현

4건의 GPU 학습, 4건의 새 거리 평가, 2건의 기존 간섭/정정 재검사를 완료했다. 같은 시작 가중치·행 배치·손실 토큰 예산·선택 규칙을 검사하고, 실제 학습 입력을 다시 만들어 기록된 digest와 정확히 일치하는지 확인했다.

seed 17 config 일부 noise/block 필드는 시작 checkpoint의 이전 메타데이터를 상속했다. **실제 학습은 위의 96블록, 2·4·8턴 조건**이며, 두 seed 모두 `training_audits`의 입력 재생성으로 검증했다. seed 7 저장부터 메타데이터도 실제 조건으로 명시했다. 기록 오류는 모델 계산에 영향을 주지 않았고 원본 결과 파일을 소급 수정하지 않았다.

단어/토큰 분리·역변환, 균형 사이클, 동일 입력, 그룹별 후보, annotation 독립성, writer gradient, 예산/시작 모델 불일치 거부, 답 그룹 clustering, 스트레스 비교 거부를 검사했다. 전체 **542 passed, 1 기존 requires-grad scalar 경고**다. codecanvas에서 새 함수를 찾지 못해 정적 그래프 영향 증거는 얻지 못했고, 회귀 검사 및 실제 CPU/GPU 실행으로 확인했다.

원래 체크포인트와 사용자 변경 파일은 보존했다. artifact는 `local-data/stream-rmt-open-vocab-*`이며 manifest/학습 JSON/선택·마지막 가중치/거리 시험/이전 검사/비교 요약을 보관한다. 저장 중요도 라벨이나 외부 검색 메모리는 추가하지 않았다. 사람 대화의 일반 기억 및 기억 텍스트 반환/침묵은 검증되지 않는다.

`neural-memory/`에서 수행한 명령 예시다. 기존 학습 artifact는 덮어쓰기를 거부하므로 재실행할 때 새 출력 파일명을 사용한다.

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_stream_memory_open_vocab.py --manifest local-data/stream-rmt-open-vocab-manifest.json --prepare-manifest
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_stream_memory_open_vocab.py --manifest local-data/stream-rmt-open-vocab-manifest.json --warm-start local-data/stream-rmt-control-acquire-joint-seed17.pt --seed 17 --steps 600 --mode diverse --output local-data/stream-rmt-open-vocab-diverse-seed17.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_stream_memory_open_vocab.py --manifest local-data/stream-rmt-open-vocab-manifest.json --warm-start local-data/stream-rmt-control-acquire-joint-seed17.pt --seed 17 --steps 600 --mode eight --output local-data/stream-rmt-open-vocab-eight-seed17.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python eval_stream_memory_open_stress.py --checkpoint local-data/stream-rmt-open-vocab-diverse-seed17.pt --manifest local-data/stream-rmt-open-vocab-manifest.json --output local-data/stream-rmt-open-vocab-stress-diverse-seed17.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python eval_stream_memory_transfer.py --checkpoint local-data/stream-rmt-open-vocab-diverse-seed17.pt --compare local-data/stream-rmt-transfer-joint-seed17.json --output local-data/stream-rmt-open-vocab-transfer-seed17.json
```

seed 7은 입력·출력 파일명과 seed를 같이 바꾼다. `analyze_stream_memory_open_vocab.py`의 `--eight/--diverse`에 두 seed의 학습 JSON을, `--stress-eight/--stress-diverse`에 대응하는 거리 평가 JSON을 주면 `stream-rmt-open-vocab-comparison.json`과 같은 입력 감사·비교를 재현할 수 있다.
