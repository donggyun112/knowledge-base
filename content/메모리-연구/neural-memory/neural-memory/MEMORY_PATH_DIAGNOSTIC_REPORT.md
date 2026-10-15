---
title: "메모리 경로 원인 분리 실험 — 2026-09-26"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `neural-memory/MEMORY_PATH_DIAGNOSTIC_REPORT.md` · 수집 2026-10-16 · **로컬 미커밋 문서 사본** (원격 커밋과 동일하다고 보장하지 않음)
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# 메모리 경로 원인 분리 실험 — 2026-09-26

## 결론

현재 residual 읽기 구조가 정보를 반환하는 것 자체는 가능하다. 같은 구조의 읽기를 학습한 오라클은 100%, 모든 과거 토큰을 처리하는 순환 쓰기는 약 90%의 지연 회상 정답률을 보였다. 오라클 사전학습 없이 쓰기·읽기를 처음부터 함께 학습해도 seed 7에서 93.2%, seed 17에서 87.5%였다.

하지만 **기존 MSC 모델의 실패 원인을 확정한 것은 아니다.** 이번 과제는 단일 사실을 회상하는 인공 양성 대조다. 확인된 구현상의 문제는 이 과제에서의 16토큰 간격 입력에 따른 성능 저하와, 짧은 잡담만 학습했을 때 긴 잡담에 대한 불안정한 일반화다. 다음 발화 예측이라는 기존 목적함수의 문제는 여전히 유력한 가설이지 이번 실험으로 직접 분리된 원인이 아니다.

## 실험 통제

- 고정 SmolLM2-135M-Instruct, float32, Apple MPS GPU. 언어모델과 출력 헤드는 전부 고정.
- 모든 메모리 실험은 기존 `SelectiveTokenMemory.read`와 동일한 최종 hidden residual 경로를 사용. 기존 MSC 체크포인트를 재사용한 것이 아니라 진단용 가중치를 새로 학습했다.
- 과거 대화에 `Me: My secret word is apple.`처럼 한 사실이 등장하고, 무관한 잡담을 사이에 두고 `What was your secret word?`를 물음.
- 정답은 apple/moon/glass/dog/river/chair/green/stone의 8개. 실제 토크나이저에서 과거 사실과 정답이 같은 단일 토큰인지 검사한다.
- 각 독립 잡담 블록에는 정답 단어만 다른 8개 대조 사례를 생성한다. 질문, 에피소드 표식, 잡담, 사실 위치는 블록 안에서 동일하다. 질문만으로 정답을 구별할 수 없다.
- train 32블록/256사례, valid 8블록/64사례, test 24블록/192사례. train/valid의 잡담 2·4턴, test의 잡담 4·8·16턴. 블록 ID는 split 사이에 겹치지 않는다.
- 메모리 폭 128, 잠재 슬롯 8개. 순환 쓰기는 매 사례의 0 상태에서 시작한다. 외부 검색 또는 key/value 레코드 저장은 추가하지 않았다.
- 학습 손실은 8지선다 전용 분류 손실이 아니라 **고정 LM 전체 어휘에 대한 정답 토큰 cross entropy**다.
- 오라클은 정답이 실제로 등장한 **과거 토큰 위치**의 LM 상태를 전달받는다. 미래 정답을 입력한 것이 아니다. 근거 위치를 아는 특권은 있다.
- 오라클 상태는 단일 사실을 모든 슬롯에 반복한다. 따라서 복수 사실 중 질의별 선택 능력까지 검증하는 실험은 아니다.
- 상태 교환은 같은 잡담 블록 내에서 순환 교환하므로 기증자 정답은 반드시 다르다. 기증자 단어로 답이 바뀌는지도 별도로 측정한다.
- 빈 상태는 엄격한 zero residual이다. 빈 상태의 8지선다 정답률은 12.5%, 전체 어휘 top-1 정답률은 0%다.
- NLL 차이의 신뢰구간은 상관된 8개 사례가 아닌 독립 잡담 블록을 재표집한다. 단, 여러 대조를 같은 test에 수행했으므로 결과는 탐색적이다.

## 결과

아래 메모리 모델에서는 8지선다와 전체 어휘 top-1 자기 상태 정답률이 동일했다. 상태 교환 열은 기증자 정답이 아니라 **원래 정답**에 대한 정답률이다.

| 초기화·학습 | 입력 간격 | seed | 각 단계 스텝 | 자기 상태 | 교환 상태 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 정확한 과거 근거 오라클 | 해당 없음 | 7·17 | 400 | 100% | 0% |
| 오라클 읽기 고정, 쓰기만 학습 | 모든 토큰 | 7 | 400 | 93.23% | 0% |
| 오라클 읽기 고정, 쓰기만 학습 | 모든 토큰 | 17 | 400 | 89.58% | 0% |
| 오라클 초기화 후 쓰기·읽기 공동학습 | 모든 토큰 | 7 | 400 | 95.31% | 0% |
| 오라클 초기화 후 쓰기·읽기 공동학습 | 모든 토큰 | 17 | 400 | 85.94% | 0% |
| 사전학습 없이 쓰기·읽기 공동학습 | 모든 토큰 | 7 | 400 | 93.23% | 0.52% |
| 사전학습 없이 쓰기·읽기 공동학습 | 모든 토큰 | 17 | 400 | 87.50% | 4.17% |
| 오라클 읽기 고정, 쓰기만 학습 | 16토큰 | 7 | 400 | 59.38% | 3.13% |
| 오라클 초기화 후 쓰기·읽기 공동학습 | 16토큰 | 7 | 400 | 61.46% | 4.17% |
| 사전학습 없이 쓰기·읽기 공동학습 | 16토큰 | 7 | 400 | 12.50% | 12.50% |
| 사전학습 없이 쓰기·읽기 공동학습 | 모든 토큰 | 7 | 2000 | 83.85% | 0.52% |
| 사전학습 없이 쓰기·읽기 공동학습 | 16토큰 | 7 | 2000 | 17.71% | 10.42% |

오라클 초기화 모델은 오라클 400스텝 + 쓰기 단계 400스텝이다. 따라서 scratch 400스텝과 동등한 학습량으로 해석하면 안 된다. scratch의 직접적인 입력 간격 비교는 같은 seed·데이터·스텝으로 맞췄다.

### 노이즈와 학습량

| seed 7, 사전학습 없음 | 잡담 4턴 | 잡담 8턴 | 잡담 16턴 |
| --- | ---: | ---: | ---: |
| 모든 토큰, 400스텝 | 100% | 98.44% | 81.25% |
| 모든 토큰, 2000스텝 | 100% | 93.75% | 57.81% |
| 16토큰 간격, 400스텝 | 12.50% | 12.50% | 12.50% |
| 16토큰 간격, 2000스텝 | 26.56% | 14.06% | 12.50% |

2000스텝 체크포인트도 valid NLL로 선택했다. 짧은 잡담 valid에서 손실이 더 낮아져도 긴 잡담 test에서 성능이 하락했다. **더 오래 학습시키는 것만으로 노이즈 내성이 좋아지지는 않는다.**

16토큰 간격 비교는 writer가 받는 관측 지점과 순환 업데이트 횟수를 동시에 바꾼다. 따라서 정보를 반드시 잃었다거나, 관측 손실과 업데이트 동역학 중 어느 하나가 유일한 원인이라고 단정할 수 없다. 모든 토큰의 LM 상태 자체도 앞선 문맥을 포함하므로, writer가 원시 토큰 기억을 단독으로 학습했다고 주장할 수 없다.

과거 전체를 원래 LM 프롬프트로 넣은 조건은 8지선다에서 100%였지만 전체 어휘 top-1은 0%였다. 이는 답 형식이 LM의 자연스러운 다음 토큰과 맞지 않기 때문일 수 있으며, 해당 조건의 자유 생성 성공으로 해석하면 안 된다.

## 기존 실패에 대한 판단 수정

1. 읽기 통로가 원천적으로 불가능하다는 해석은 지지되지 않는다. 그러나 단일 단어 결과로 여러 사실·자연어 문장·기존 체크포인트의 읽기 능력을 보증할 수는 없다.
2. 쓰기·읽기를 함께 학습하는 것 자체도 불가능하지 않다. 사전학습 없는 모든 토큰 모델도 두 seed에서 기억을 사용했다.
3. 16토큰 간격을 계산 최적화로 사용한 이전 실험은 안전한 근사라는 보장이 없었다. 같은 과제·seed에서 실제로 성능이 크게 떨어졌다. 실제 MSC에서 이 변경의 효과는 별도 실험이 필요하다.
4. 빈 상태 대비 큰 NLL 개선만으로 기억 성공을 선언할 수 없다는 점이 다시 확인됐다. 16토큰 scratch 400스텝 모델은 빈 상태 NLL 16.97을 자기 상태 2.44로 낮췄지만, 자기와 교환 상태 모두 12.5%였다. 단어 집합의 공통 사전확률만 익혀도 그런 개선이 가능하다.
5. 기존 목적함수와 이번 과제는 다르다. 따라서 원래 MSC 목적함수가 실패의 유일한 원인이라는 인과 결론은 아직 없다.

## 다음 검증 순서

먼저 여러 사실·수정된 사실·회상할 필요 없는 질문을 포함하고, 잡담 길이를 학습 분포에서도 다양하게 넣는다. 그다음 실제 사람 대화의 사실을 뒤늦게 묻는 과제로 이동한다. 매 단계에서 자기/빈/교환 상태, 질문에 불필요한 메모리의 억제, 사실 수정 후 최신 정보 회상을 따로 평가한다.

이 진단은 RMT/TTT/Titans 재현을 대체하지 않는다. 논문 충실도 비교와 실제 대화 실험은 별도로 남아 있다. 자동 저장 판단·반환 타이밍·장기 다중 사실 메모리도 아직 검증되지 않았다.

## 코드와 재현

- 실행기: run_memory_path_diagnostic.py (`run_memory_path_diagnostic.py`; 원 저장소의 파일 참조)
- 검사: tests/test_memory_path_diagnostic.py (`tests/test_memory_path_diagnostic.py`; 원 저장소의 파일 참조)
- 원본 결과·각 arm 체크포인트: `local-data/path-diagnostic-*.json`, `local-data/path-diagnostic-*-<arm>.pt`.
- 전체 테스트: **430 passed, 1 기존 경고**.

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_memory_path_diagnostic.py --seed 7 --token-stride 1 --steps 400 --output local-data/path-diagnostic-token1-seed7.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_memory_path_diagnostic.py --seed 17 --token-stride 1 --steps 400 --output local-data/path-diagnostic-token1-seed17.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_memory_path_diagnostic.py --seed 7 --token-stride 16 --steps 400 --output local-data/path-diagnostic-token16-seed7.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_memory_path_diagnostic.py --seed 7 --token-stride 1 --steps 400 --arms writer_joint_scratch --output local-data/path-diagnostic-scratch400-token1-seed7.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_memory_path_diagnostic.py --seed 7 --token-stride 1 --steps 2000 --arms writer_joint_scratch --output local-data/path-diagnostic-scratch2000-token1-seed7.json
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python run_memory_path_diagnostic.py --seed 7 --token-stride 16 --steps 2000 --arms writer_joint_scratch --output local-data/path-diagnostic-scratch2000-token16-seed7.json
```

첫 seed 7 모든 토큰 파일은 오라클·고정 읽기·공동학습 3 arm으로 실행한 초기 버전이다. scratch arm은 별도 파일에 있다. 현재 기본 실행은 scratch를 포함한 4 arm이다. 실제 결과 파일은 보존했고 새 버전으로 덮어쓰지 않았다.
