---
title: "Harness² 파일럿 — 조건·변경 기록과 재계산"
tags: [memory-research, harness, reproducibility, evaluation]
date: 2026-10-16
---

# 검증 범위

[[메모리-연구/harness2/RESULTS|실제 실행 보고서]]의 수치를 다시 계산하고, 어떤 조건에서 나온 결과인지 확인하기 위한 문서다. 공개 파일은 원시 실행 증거의 전체 복제본이 아니다. 새 모델 실행, 기존 결과의 독립 재채점, CSV 집계 검산을 구분한다.

## 고정한 조건

| 항목 | 설정 |
| --- | --- |
| 실행일 | 2026-10-16 UTC |
| 최초 프로토콜 고정 | 2026-10-16 03:24:46 UTC |
| 공식 코어 | `1cfe254e8d25b15f37048c3730134686abe60335` |
| JobBench 데이터 | `d43a66575635da0d3f6cb9a20976dc1a60f3ffc9` |
| 비교 | 무변경 기본 실행과 PPC `k=1`의 합성 후 실행 |
| 표본 | 회계·장부 task1/task2, IT 지원 task1/task2 |
| 순서 | 직군별 task1 → task2, 직군별 라이브러리 분리 |
| 모델 | 동일 내장 모델 구성 상속, 정확한 스냅샷·추론 설정은 확인 불가 |
| 세션 상한 | 1,200초 |
| 자료 접근 | 미리 제공한 로컬 원본·참조 자료, 실행 과정의 웹 접근 금지 지시 |
| 격리 | 새 문맥과 파일 범위 지시, 공유 파일시스템 |
| 주 지표 | 원본 JobBench 가중 루브릭의 이진 판정 점수 |
| 평가 | 산출물 해시 고정 후 과제별 새 익명 A/B 평가 문맥 |
| 보조 지표 | 산출물 계약 검사, 사전 지정 CPU 기준 제외 민감도 분석 |
| 비용·토큰 | 실제 내장 사용량 정보 없음, 외부 모델 API 호출 없음 |

평가 점수를 보고 과제를 고르거나 결과를 제거하지 않았다. 루브릭 정보와 채점 결과를 실행·편집·회고에 피드백하지 않았다. 실제 완료 수는 솔버 16회, 편집·합성 12회, 회고 4회이며 별도 평가가 4회다.

## 실행 중 수정·정정

아래는 점수 해석에 필요한 구현 변경과 보고상의 정정을 요약한 것이다. 원시 실행 로그는 공개하지 않는다.

| UTC 시각 | 변경 | 영향 범위 |
| --- | --- | --- |
| 03:25 | 회계 task1의 원본 파일명 별칭을 명확히 안내 | 데이터·과제·비교 조건·채점 기준 변경 없음 |
| 03:33 | task2 무변경 기본 실행을 미리 병렬 수행 | 개선·라이브러리 순서는 task1 → task2 유지 |
| 03:39 | SQLite 표·뷰의 읽기 전용 텍스트 추출 보완 | 편집 단계 이전 적용, 원본 바이너리 유지, 모델 재실행 없음 |
| 03:49 | 추론 설정·토큰·비용의 미노출을 명시 | 설계 메타데이터를 관측된 설정으로 취급하지 않음. 어댑터의 비용 0은 측정값이 아님 |
| 04:16 | PPTX 표·그룹 텍스트를 미리보기에 포함 | task2 개선 전에 적용. task1은 PPTX 출력이 없어 영향 없음. 모델 재실행 없음 |
| 05:19 | 기본/후보 하네스 재직렬화 차이를 추가 교란으로 기록 | 전체 산출물 고정 뒤의 보고 정정. 출력 수정·재실행·채점 변경 없음 |

안전한 재개는 저장된 과제 완료 체크포인트에서 확인했다. 임의의 편집 단계 중간부터 중복 없이 재개된다는 보장은 검증하지 않았다.

## CSV 집계 검산

[results.csv](results.csv)는 최종 보고와 같은 네 행을 담고 있다. 단위는 백분율이며 `delta_percentage_points`는 PPC − 기본의 퍼센트포인트 차이다. sensitivity 열은 사전 지정 CPU 항목 제외 분석이다. 이 경우 기본 열과 값이 같다.

저장소 루트에서 Python 표준 라이브러리만으로 실행한다. 모델이나 외부 API는 호출하지 않는다.

```sh
python3 - <<'PY'
import csv
import math
from pathlib import Path
from statistics import mean

path = Path("content/메모리-연구/harness2/results.csv")
with path.open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 4
assert len({r["task_id"] for r in rows}) == 4
base = [float(r["base_percent"]) for r in rows]
ppc = [float(r["ppc_percent"]) for r in rows]
deltas = [b - a for a, b in zip(base, ppc)]
for row, delta in zip(rows, deltas):
    assert math.isclose(delta, float(row["delta_percentage_points"]), abs_tol=1e-9)
wins = sum(d > 1e-9 for d in deltas)
ties = sum(abs(d) <= 1e-9 for d in deltas)
losses = sum(d < -1e-9 for d in deltas)
print(f"base={mean(base):.2f}%, ppc={mean(ppc):.2f}%, delta={mean(deltas):.2f}pp")
print(f"wins/ties/losses={wins}/{ties}/{losses}")
for condition in ("base", "ppc"):
    value = mean(float(r[f"{condition}_sensitivity_percent"]) for r in rows)
    print(f"{condition} sensitivity={value:.2f}%")
PY
```

예상 결과는 기본 `35.28%`, PPC `29.51%`, 차이 `−5.77pp`, 승/동점/패 `0/3/1`이다. 이 검사는 집계 산술과 CSV 내부 일관성을 확인한다. 점수의 원본 증거를 재판정하거나 루브릭의 타당성을 검증하지는 않는다.

## 공식 코어의 별도 스모크 테스트

실험 당시 Python 3.12.14/Linux에서 공식 결정론적 데모의 병렬·순차 `k=2` 실행과 공식 회귀검사 5개가 통과했다. 내장 모델 어댑터의 회귀검사도 8개 통과했다. 데모는 고정된 편집·선택 규칙을 쓰므로 모델의 학습이나 과제 성능의 증거가 아니다.

공식 코어만 다시 확인하려면 새 작업 폴더에서 아래처럼 고정 커밋을 사용한다. 출력 폴더 이름은 기존 결과와 겹치지 않게 한다. 별도 의존성 설치 없이 당시 실행한 표준 라이브러리 데모·검사 경로다.

```sh
git clone https://github.com/google-research/harness2.git harness2-source
git -C harness2-source checkout --detach 1cfe254e8d25b15f37048c3730134686abe60335
cd harness2-source
env -i PATH="$PATH" HOME=/tmp PYTHONPATH=. \
  python3 -m harness2.cli.demo --output ../harness2-smoke-output --k 2
env -i PATH="$PATH" HOME=/tmp PYTHONPATH=. \
  python3 -m unittest discover -s tests -v
```

전체 벤치마크 런처는 모델 접근, 비용 한도, 평가 정보 누출 방지 설정이 필요하다. 위 명령은 전체 모델 벤치마크를 실행하지 않는다. 동일 내장 모델 스냅샷을 지정할 수 없고 원본 어댑터·산출물 전체도 이 저장소에 없으므로, 네 과제의 모델 실행을 그대로 복제하는 one-command 재현은 제공하지 않는다.

## 다음 실험에서 필요한 대조

고정 모델·추론 설정, 동일 총 예산의 best-of-N 또는 반복 기준선, 여러 과제 순서, 라이브러리 on/off, 하네스의 실제 변경량, 평가자 반복 또는 전문가 재채점을 함께 설계할 필요가 있다. 이는 후속 검증 제안이며 이번에 완료한 실험에 포함되지 않는다.
