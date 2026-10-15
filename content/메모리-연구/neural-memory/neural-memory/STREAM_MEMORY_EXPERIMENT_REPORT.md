---
title: "연속 대화 메모리 파일럿 — 2026-09-27"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `neural-memory/STREAM_MEMORY_EXPERIMENT_REPORT.md` · 수집 2026-10-16 · **로컬 미커밋 문서 사본** (원격 커밋과 동일하다고 보장하지 않음)
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# 연속 대화 메모리 파일럿 — 2026-09-27

후속으로 같은 읽기 가중치를 고정한 갱신 진단, gate/query 제거 대조, 짧은 거리부터의 학습을 수행했다. 아래는 최초 파일럿 기록이며 최신 결과는 [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_UPDATE_REPORT|갱신 진단 보고서]]에 별도로 보존한다.

## 결과 요약

중요도 라벨 없이 원시 대화 내용의 다음 토큰 손실로 학습하는 순환 기억 경로를 구현했다. 기억은 Transformer 입력에서부터 다음 구간에 참여하며, 뒤 구간의 손실이 앞선 기억 갱신까지 역전파된다. 이전의 최종 hidden residual 보정 모듈과는 다른 구조다.

**현재 구현·학습 조건에서는 대화별 정보를 보존하는 기억의 이득이 확인되지 않았다.** 사람 대화 파일럿은 두 seed 모두 자기 상태가 교환 상태보다 명확하게 낫지 않았다. 인공 단어 회상에서도 쓰기·읽기 공동학습은 우연 수준이었다. 정확한 과거 단어를 직접 prefix로 전달하는 읽기 경로를 따로 학습하면 93.75%를 맞혔으므로, 이 인터페이스로 정보를 이용하는 것 자체는 가능하다.

이 결과는 “대화만으로 기억 특징을 학습할 수 없다”는 일반적 반증이 아니다. 아주 짧은 prefix·적은 학습량·제한된 파라미터 갱신으로 수행한 구현의 실패다. 자동 저장·망각·반환 타이밍·텍스트 기억 출력까지 완성한 모델도 아니다.

## 구현과 검사

- [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_SPEC|설계]]
- 모델 (`neural_memory/stream_recurrent_memory.py`; 원 저장소의 파일 참조): 빈 `M0`, 읽기/쓰기 기억 위치, 인과적 텍스트 attention, 구간 간 KV cache 없음.
- 사람 대화 실행기 (`run_stream_recurrent_memory.py`; 원 저장소의 파일 참조): 중요도·근거·구간 제거 라벨, 교사 증류, contrastive 학습 없음.
- 대조 실행기 (`run_stream_memory_control.py`; 원 저장소의 파일 참조): 인공 단일 사실 과제로 읽기 가능성과 학습 경로를 확인.
- 초기 기억은 8×576개의 0, 대화별 float32 약 18 KiB. 독립 대화 사이에 초기화하고 구간 사이에 전달한다.
- 고정 SmolLM2-135M-Instruct + Q/V 저차원 갱신(rank 4) + 기억 projection, 학습 파라미터 562,176개. RMT 원리를 따른 계산 절감 변형이지 원 논문의 전체 학습 재현은 아니다.
- 빈 기억과 메모리 없는 동일 모델의 hidden 일치, 미래 토큰 인과성, padding 불변성, 구간 경계 target 누락/중복 없음, 뒤 손실의 앞 기억 역전파, 고정 출력 헤드 무기울기 등을 검사했다.
- eager 및 실제 실행에 사용하는 SDPA backend에서 인과성·빈 기억 검사를 수행했다. padding에 따라 쓰기 위치가 달라지는 문제를 발견해 rotary position을 보정했다.
- 실제 GPU 실행은 Apple MPS/float32. 최신 전체 검사 **451 passed, 1 기존 경고**.

## 사람 대화 파일럿

MSC train 256쌍, valid 64쌍, test 96쌍. 시간순으로 각 대화의 앞부분 최대 379토큰을 읽는다. 64토큰 구간 6개, 경계에 관측 토큰 1개를 겹쳐 target 누락을 막는다. 모든 대화가 잘렸으므로 완전한 다중 세션·장기 기억 실험으로 해석할 수 없다.

손실은 화자·세션 표식을 제외한 **모든 대화 내용의 next-token cross entropy**다. 학습 중 구간 사이 기억을 detach하지 않는다. 학습 200스텝, batch 2, AdamW lr 0.0003. valid에서 `min(빈−자기, 교환−자기)`가 가장 큰 체크포인트를 고른다. 다음 표는 첫 구간을 제외한 미래 구간 내용 NLL의 대화별 평균이다.

| seed | 선택 스텝 | 자기 NLL | 빈 NLL | 교환 NLL | 빈−자기 | 교환−자기, 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 7 | 50 | 3.50154 | 3.59758 | 3.49791 | +0.09604 | −0.00363 [−0.01858, +0.01138] |
| 17 | 200 | 3.48602 | 3.49109 | 3.48643 | +0.00507 | +0.00041 [−0.00062, +0.00150] |

첫 seed는 빈 상태보다 좋아도 타인 상태와 구별하지 못했다. 두 번째 seed는 빈 대비 이득도 작았다. 따라서 대화별 기억 성공 기준을 통과하지 못했다. 상태 간 cosine은 각각 0.8602, 0.9969였으나 상태가 서로 다르다는 것만으로 유용한 내용 보존을 주장할 수 없다.

첫 배치의 clipping 전 기억 projection gradient norm은 약 5.4천, 533만이었다. 모두 유한값이고 실제 업데이트 전에 norm 1로 clipping했다. 이는 긴 순환 경로의 학습 안정성을 점검해야 할 신호지만, 한 배치 관측으로 gradient explosion이 실패의 유일한 원인이라고 확정하지 않는다.

seed 7 선택 자료의 원시 ID 기준 train/valid 및 train/test 교집합은 없었다. 기존 MSC test는 이전 연구에서 반복 확인한 자료이며, swap donor 의존성을 전부 재표집하지 않은 대화별 bootstrap이므로 탐색적 결과다.

## 같은 경로의 인공 단어 회상 대조

과거에 임의의 비밀 단어를 말하고, 잡담 뒤에 그 단어를 묻는 대화다. 정답은 8개 단어, 동일 잡담·질문·사실 위치에서 단어만 바뀌는 대조 블록을 사용한다. source fact가 마지막 구간 원문에 들어 있지 않은지 검사한다. train 8블록/64사례, valid 4블록/32사례, test 12블록/96사례. train 잡담 2·4·8턴, test 8·16턴에 동일한 추가 잡담을 붙인다. 32토큰 구간, batch 2, 400스텝, lr 0.0003.

| 학습 경로 | 선택 스텝 | 자기 상태 정답률 | 빈 상태 | 교환 상태 |
| --- | ---: | ---: | ---: | ---: |
| 모든 대화 내용 손실, 쓰기·읽기 공동학습 | 250 | 12.50% | 12.50% | 12.50% |
| 마지막 미래 구간 내용 손실, 쓰기·읽기 공동학습 | 350 | 12.50% | 12.50% | 12.50% |

마지막 구간 손실은 앞부분의 사실을 중요하다고 지정하는 라벨이 아니다. 앞부분을 문맥으로 읽고 뒤의 관측 텍스트를 예측하는 손실이며, source/answer annotation을 바꿔도 non-oracle 학습 손실이 동일한지 검사했다. 이 과제에서 두 방식 모두 기억의 쓰기·읽기를 함께 배우지 못했다. 따라서 단순히 모든 토큰 평균 손실이 희석돼서 실패했다고만 결론 낼 수도 없다.

별도 **읽기 오라클 학습**에서는 이미 관측된 과거 단어의 모델 내부 입력 상태를 memory prefix로 반복 전달하고 마지막 구간 손실로 읽기 파라미터를 학습했다. 미래 단어를 미리 입력한 것이 아니다. 다만 정답 근거 위치를 아는 특권을 사용하는 **진단용 경로**이며, 학습된 쓰기 또는 원시 대화 알고리즘이 아니다.

| 진단 경로 | valid 정답률 | test 정답률 | test 정답 NLL |
| --- | ---: | ---: | ---: |
| 과거 단어 prefix 오라클, 읽기 학습 | 100% | 93.75% | 2.28081 |

정답률은 8지선다 기준, NLL은 전체 LM 어휘 기준이다. 장문 잡담 조건에서 6개를 틀렸고 일부 높은 확신의 오답 때문에 평균 NLL이 높다. 자유 텍스트 생성 정확도는 측정하지 않았다. 오라클은 한 사실을 모든 슬롯에 반복하므로 복수 사실 중 적절한 기억 선택을 검증하지도 않는다.

오라클과 공동학습 모델은 **같은 읽기 구조지만 학습된 파라미터가 다르다**. 따라서 “쓰기만 고장이고 읽기는 이미 완벽하다”는 엄밀한 분리는 아니다. 확인된 것은 같은 인터페이스의 읽기 가능성과, 현재 공동학습 경로의 실패다.

초기 오라클 실행에는 checkpoint를 실제 학습한 오라클 경로가 아니라 자기 상태 NLL로 고르는 오류가 있었다. 경로에 맞는 검증값으로 수정하고 검사와 전체 400스텝 재실행을 수행했다. 위 수치는 `selection-fixed` 파일만 사용한다. 기존 오류 실행은 기록을 보존했지만 판정에서 제외한다.

## 다음의 좁은 검증

사람 대화의 다음 발화 평균 예측만 늘리기 전에, 이 작은 회상 과제에서 기억 갱신을 배우도록 만드는 조건을 분리한다. 우선 직접 전달한 상태와 순환 writer 상태의 분포 차이, 역전파 구간 수별 gradient 크기, 초기 쓰기 위치와 상태 projection의 학습 안정성을 검사한다. 읽기·쓰기 파라미터가 공유되는 현재 구조의 결합도 함께 고려해야 한다.

그 이후에만 더 긴 원시 대화, 사실 수정·여러 사실·불필요한 반환 억제, 실제 기억 내용 텍스트 출력으로 확장한다. “대화로 기억 특징이 학습될 수 있다”는 가설은 유지하지만, 이번 구현이 그 가설을 실현했다고 말하지 않는다.

## 재현

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_stream_recurrent_memory.py --seed 7 --train-dialogues 256 --valid-dialogues 64 --test-dialogues 96 --steps 200 --batch-size 2 --segments 6 --chunk 64 --rank 4 --lr 0.0003 --eval-every 25 --output local-data/stream-rmt-dialogue-seed7.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_stream_recurrent_memory.py --seed 17 --train-dialogues 256 --valid-dialogues 64 --test-dialogues 96 --steps 200 --batch-size 2 --segments 6 --chunk 64 --rank 4 --lr 0.0003 --eval-every 25 --output local-data/stream-rmt-dialogue-seed17.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_stream_memory_control.py --steps 400 --output local-data/stream-rmt-control-seed7.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_stream_memory_control.py --steps 400 --loss-scope future-block --output local-data/stream-rmt-control-future-seed7.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_stream_memory_control.py --steps 400 --loss-scope future-block --oracle-prefix --output local-data/stream-rmt-control-oracle-future-selection-fixed-seed7.json
```

JSON에는 전체 지표·설정·학습 기록이 있고, 같은 이름의 `.pt`에는 학습 파라미터만 저장했다. 원래의 큰 고정 모델 가중치는 포함하지 않는다.
