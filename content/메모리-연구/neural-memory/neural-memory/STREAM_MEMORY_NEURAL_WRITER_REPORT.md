---
title: "학습형 writer와 상태 소실 진단 — 2026-09-28"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `neural-memory/STREAM_MEMORY_NEURAL_WRITER_REPORT.md` · 수집 2026-10-16 · **로컬 미커밋 문서 사본** (원격 커밋과 동일하다고 보장하지 않음)
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# 학습형 writer와 상태 소실 진단 — 2026-09-28

## 결론

학습 가능한 cross-attention writer를 순환 잠재 메모리에 추가했지만, 이번 반사실 대화 과제에서는 개인별 단어를 기억하지 못했다. 기존 suffix writer보다 개선되지 않았으며, 테스트에서 자기 상태와 다른 대화의 상태를 바꿔 넣어도 8개 후보 중 정답률은 모두 우연 수준인 12.5%였다. 새 writer까지 기울기는 도달했다. 따라서 단순한 역전파 단절이 아니라, 현재 학습 목표와 반복 갱신 아래에서 단어별 차이를 형성·유지하지 못한 결과다.

## 조건

- 과거 발화 `Me: My secret word is <word>` 뒤 잡담을 두고 나중에 같은 단어를 묻는 8-way 반사실 대화. 각 블록은 단어와 답을 제외하면 잡담·질문·길이가 같다. 정답 단어는 마지막 원문 구간에 없다.
- 학습 16블록/128사례, 검증 4블록/32사례, 테스트 12블록/96사례. 테스트 잡담은 8·16턴으로 늘렸다.
- 고정 SmolLM2-135M-Instruct, 8×576 순환 상태, 읽기는 동일한 학습형 residual adapter, LoRA rank 0, 쓰기는 기존 suffix 또는 새 cross-attention. 메모리 갱신은 overwrite. Apple MPS/float32, seed 41, 300스텝, batch 2, lr 0.0003.
- 중요도·사실 위치 라벨이나 정답 토큰의 특권 라우팅 없이 마지막 미래 구간 **대화 내용 전체**의 다음 토큰 손실을 학습했다. 검증의 자기 상태 NLL로 체크포인트를 선택했다. 정확한 과거 토큰을 주입하는 oracle은 학습 경로가 아니라 별도 진단 조건이다.

| 쓰기 방식 | 선택 스텝 | 테스트 자기/교환/빈 NLL | 자기/교환 8-way 정확도 | 자기 전체 어휘 정확도 |
| --- | ---: | --- | --- | ---: |
| 기존 suffix | 300 | 3.775389 / 3.775471 / 15.226600 | 12.5% / 12.5% | 11.46% |
| 학습형 attention | 250 | 4.357145 / 4.357146 / 15.226600 | 12.5% / 12.5% | 2.08% |

빈 상태 대비 손실 개선은 일반적인 과제/문장 패턴을 메모리 경로가 보정해도 생길 수 있다. 두 방식 모두 자기와 교환 상태의 손실이 사실상 같으므로 이를 개인별 기억으로 해석하면 안 된다. 전체 어휘 정확도도 정답 단어별 구별 없이 빈번한 한 단어를 출력해 얻을 수 있다.

## 상태가 사라지는 위치

선택된 체크포인트에서 같은 반사실 블록의 서로 다른 상태를 교환한 RMS 차이를 사실이 포함된 구간 직후와 질문 직전에 측정했다. 상태 자체의 RMS와 나눈 상대 차이도 함께 기록했다.

| 쓰기 방식 | 사실 직후 상태 차이 | 질문 직전 상태 차이 | 감소 배율 | 질문 직전 상대 차이 |
| --- | ---: | ---: | ---: | ---: |
| 기존 suffix | 0.053433 | 0.001719 | 약 31배 | 0.000871 |
| 학습형 attention | 0.004098 | 0.0000337 | 약 121배 | 0.0000170 |

학습형 attention은 사실 직후의 상태 구별부터 더 약했고, 후속 잡담 구간을 거쳐 그 차이가 거의 사라졌다. 그 모델의 질문 위치에서 자기/교환 상태가 만든 후보 단어 logit RMS 차이는 0.0000388이었다. 이는 **현재 구현의 쓰기·보존 경로가 병목이라는 강한 증거**다. 다만 상태 차이만으로 읽기 쪽의 기여가 없다고 단정할 수는 없다. 사실 직후 측정도 단어가 그 구간에 처음 등장한 순간과 정확히 일치하는 별도의 인과 개입 시험은 아니다.

## 구현·검증·범위

- 모델 (`neural_memory/stream_recurrent_memory.py`; 원 저장소의 파일 참조)에 슬롯이 관측 텍스트 hidden state를 cross-attend하는 `attend` 쓰기 모드를 추가했다. 기존 `suffix` 기본 동작은 유지했다. 입력은 텍스트 토큰이고, 외부 key-value 저장소나 검색 인덱스는 없다.
- 대조 실행기 (`run_stream_memory_control.py`; 원 저장소의 파일 참조)에 쓰기/읽기 방식 선택, writer 기울기 및 상태·logit 교환 차이 계측을 추가했다. 첫 단계 attention writer gradient norm은 8.11로 0이 아니었고, 고정 backbone에는 gradient가 없었다.
- 상태 진단 (`diagnose_control_state_spread.py`; 원 저장소의 파일 참조)은 저장된 체크포인트에서 사실 직후와 질문 직전의 상태 차이를 별도로 계산한다.
- 이것은 단일 인공 사실 과제의 한 seed 진단이며 실제 사람 대화 E2E, 장기 보존, 자동 반환 타이밍, 텍스트 메모리 출력의 성공을 뜻하지 않는다. `past_token_oracle`은 이 checkpoint로 읽기만 했으므로 그 낮은 성능을 읽기 인터페이스의 절대 한계로 해석하지 않는다.

원자료: `local-data/stream-rmt-control-suffix-residual-rank0-seed41.json`, `local-data/stream-rmt-control-attend-residual-rank0-seed41-diagnostic.json`, `local-data/stream-rmt-control-suffix-residual-rank0-seed41-state-spread.json`, `local-data/stream-rmt-control-attend-residual-rank0-seed41-state-spread.json`. 각 실행기의 같은 이름 `.pt`가 선택된 학습 가중치를 보존한다.

## 후속: 보존 게이트와 짧은 거리부터 학습

같은 seed 41, 고정 backbone, rank 0, residual 읽기, 8개 슬롯을 유지하고 `gated` 갱신을 검사했다. 학습형 attention writer에 게이트를 넣어 긴 거리로 바로 300스텝 학습하면 테스트 8지선다 자기/교환이 둘 다 12.5%였다. 상태 차이는 사실 직후 0.000668, 질문 직전 0.000578로 대부분 **유지**됐으나, 차이 자체가 너무 작아 정답을 구별하지 못했다. 게이트가 지워지는 문제를 줄였어도 사실을 강하게 쓰는 문제는 남았다.

다음은 oracle 라우팅 없이 짧은 잡담 0·1턴과 뒤 잡담 1턴으로 먼저 400스텝 학습하고, 필요하면 기존 긴 거리로 400스텝 이어 학습하는 대조였다. 기존 suffix 쓰기는 공유 쓰기 query 0.02를 사용했다. 두 방식 모두 마지막 미래 구간의 대화 내용 전체 next-token 손실을 썼다. 짧은 단계에서 attention writer의 검증 정답률은 평가한 모든 스텝에서 12.5%였으므로 긴 단계로 진행하지 않았다.

| 경로 | 짧은 단계 검증 자기/교환 | 기본 긴 테스트 자기/교환 | 더 긴 32·64턴 새 잡담 자기/교환 |
| --- | --- | --- | --- |
| 게이트 + attention writer, 짧은 단계 400스텝 | 12.5% / 12.5% | 12.5% / 12.5% | 미평가 |
| 게이트 + suffix writer, 짧은 단계 400스텝 | 25.0% / 12.5% | 13.54% / 12.5% | 미평가 |
| 게이트 + suffix writer, 이어서 긴 단계 400스텝 | 12.5% / 12.5% (긴 검증) | 17.71% / 9.38% | 12.5% / 12.5% |

마지막 행은 긴 단계의 검증 NLL 최저인 125스텝 체크포인트다. 긴 단계 첫 25스텝부터 검증의 대화별 상태 차이가 약 0.077에서 0.000002로 줄고, 이후 모든 검증 스텝에서 정답률은 12.5%였다. 기본 긴 테스트에서 보이는 작은 자기/교환 차이는 검증에 재현되지 않았다. 새 잡담 seed 1009의 8·16턴 96사례는 자기 17.71%, 교환 10.42%였지만 95% 블록 bootstrap 정확도 구간이 [12.5%, 26.04%]로 우연 수준을 포함했다. 더 긴 32·64턴에서는 두 조건 모두 12.5%, 최종 상태 차이는 0.00000024였다. **지속 가능한 대화별 기억 성공으로 판정하지 않는다.**

이 추가 비교는 정보 보존과 정보 획득을 분리해 준다. 고정 게이트만으로 이미 약한 attention-writer 상태 신호를 충분히 키우지 못한다. suffix + query는 짧은 거리에서 일부 신호를 얻지만 긴 거리 학습·평가에 안정적으로 옮기지 못한다. 두 writer는 파라미터 구조와 초기화가 달라 단일 seed의 엄격한 인과적 우열 실험도 아니다. 실제 사람 대화 E2E나 기억 반환 기능은 이 실험에서 평가하지 않았다.

후속 원자료: `local-data/stream-rmt-control-attend-residual-gated-cold-seed41.json`, `local-data/stream-rmt-control-attend-residual-gated-cold-seed41-state-spread.json`, `local-data/stream-rmt-control-attend-residual-gated-short-seed41.json`, `local-data/stream-rmt-control-suffix-residual-gated-short-seed41.json`, `local-data/stream-rmt-control-suffix-residual-gated-curriculum-seed41.json`, `local-data/stream-rmt-control-suffix-residual-gated-curriculum-seed41-stress.json`. 스트레스 실행기는 새 checkpoint의 `read_mode`·`write_mode`를 그대로 복원하도록 갱신했다.
