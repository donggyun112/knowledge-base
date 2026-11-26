---
title: Univer Worktree와 Compare — 문서 에이전트의 검토본과 실제 반영을 분리하기
source: https://docs.univer.ai/overview/features/shared/worktree
type: implementation
category: 에이전트-스킬
tags: [research, agent, document-editing, collaboration, technology-radar]
researched: 2026-11-26
radar_quadrant: Languages and frameworks
radar_ring: Assess
reading_status: unread
---

# Univer Worktree와 Compare — 문서 에이전트의 검토본과 실제 반영을 분리하기

**사람이 검토한 버전은 고정해도, 병합할 원본은 계속 바뀐다.** Univer는 Office 문서의 작업 초안, 변경 검토, 실제 병합을 별도 연산으로 제공한다. 이 구분을 쓰면 “에이전트가 무엇을 바꿨나?”와 “지금 반영하면 무엇이 달라지나?”를 다른 질문으로 다룰 수 있다.

- **대표 원문**: [Univer Worktree](https://docs.univer.ai/overview/features/shared/worktree)
- **보조 원문**: [Compare](https://docs.univer.ai/overview/features/shared/compare), [AI SDK Worktree 흐름](https://docs.univer.ai/ai/worktree), [CLI Gateway의 구조화 diff 계약](https://github.com/dream-num/univer-cli/blob/ccdaa6b33567adf191cc19accfd78f2b386d6349/packages/collab-gateway-contract/README.md#agent-diff-contract), [Office 파일 변환](https://docs.univer.ai/server/import-export), [GRID 재계산 검사용 코드](https://github.com/GRID-is/spreadsheet-benchmark/blob/compatibility-v1/replay/verify-recalc.ts)
- **확인된 날짜**: Univer 공식 문서 표기 버전 v1.6.2, 개별 페이지 발행·수정일 미표기. CLI 계약 고정 커밋 2026-09-03 UTC. GRID 호환성 자료 발행 2026-11-10.
- **수집일**: 2026-11-26 KST
- **상태**: Languages and frameworks / Assess · 읽기 전
- **검증 범위**: 공식 문서·고정 커밋 계약·공개 검사 코드의 정적 검토. SDK 실행, 동시 편집, XLSX 변환과 재계산은 직접 시험하지 않았다.

## 1. 초안 저장, 검토본 확정, 원본 반영

Worktree는 Git 디렉터리가 아니라 문서 객체(Unit)의 격리된 작업본이다. 생성할 때 Unit별 원본(trunk) revision을 기준점으로 잡는다. 이후 원본과 초안은 별개로 진행한다. AI SDK에서 읽기·쓰기·스크린샷·웹 검토가 같은 작업본을 보려면 애플리케이션이 `worktreeID + unitID`를 같은 대상으로 해석해야 한다. Unit ID만으로는 원본과 초안을 구별할 수 없다. [AI SDK 가이드](https://docs.univer.ai/ai/worktree)

| 연산 | 확정하는 것 | 확정하지 않는 것 |
| --- | --- | --- |
| `runtime.commit()` | 초안의 변경과 새 revision | 원본 반영 |
| `markReady()` | 각 Unit의 수정 불가 검토 revision. 추가 수정은 Reopen 후 가능 | 원본 잠금 |
| `evaluateUnitMerge()` | 요청 시점 원본에 반영했을 때의 읽기 전용 예상 결과 | 실제 병합 결과 예약 |
| `mergeWorktree()` | 실행 시점 원본에 Unit별 변경 적용 | 여러 Unit의 원자적 일괄 반영 |

기존 Unit은 기준점에서 검토본까지의 변경을 모아 원본 협업 서비스에 제출한다. 원본이 앞서 있으면 OT(동시 변경에 맞춰 편집 연산을 변환하는 방식)를 적용한다. 변환할 수 없는 변경은 충돌로 돌려주며, 기술적으로 적용 가능해도 업무 의미가 맞는지는 별도 판단이다. 여러 Unit 중 앞 문서만 반영되고 뒤 문서에서 실패할 수 있다. 따라서 검토, 예상 병합, 실제 Unit별 결과를 UI에서 각각 보여줄 이유가 있다. [Worktree 병합과 검토](https://docs.univer.ai/overview/features/shared/worktree)

## 2. 구조화된 diff도 범위와 확실성을 함께 읽는다

Compare는 두 revision을 복원한 전체 스냅샷을 제품별로 비교한다. Sheet라면 셀 값·수식·행·열 같은 단위로 표현한다. 행 삽입과 같이 좌표를 밀어내는 작업은 대응 changeset이 있을 때 더 정확히 맞출 수 있다. 두 스냅샷만 있는 경우도 비교할 수 있지만 같은 확신을 가정하지 않는다. [Compare 공식 문서](https://docs.univer.ai/overview/features/shared/compare)

고정 커밋의 **CLI Gateway 계약**은 변경 객체의 `stableId`, 좌우 위치, 필드별 변경 전후 값과 타입을 준다. 답이 비어 있다면 `coverage`와 `diagnostics`를 확인해야 한다. 미지원 또는 좌표 대응이 모호한 경우를 “변경 없음”으로 승인하면 안 된다. 페이지 조회 중 `stale`이면 비교를 다시 만들고 서로 다른 시점의 페이지를 섞지 않는다. 이는 해당 Gateway 계약의 필드이며, 모든 서비스에서 동일한 ID나 구조가 보장된다는 주장은 아니다. PDF는 공식 Compare·Worktree 지원 대상에 포함되지 않는다. [CLI Gateway 계약](https://github.com/dream-num/univer-cli/blob/ccdaa6b33567adf191cc19accfd78f2b386d6349/packages/collab-gateway-contract/README.md#agent-diff-contract)

## 3. 제안: 승인된 변경과 인도할 파일을 따로 검증하기

1. **같은 두 revision을 비교한다.** 값이 비슷한 두 행 사이에 행을 삽입하고 기존 행 하나의 수식을 바꾼다. changeset이 있을 때와 스냅샷만 있을 때에 대해 행 대응, 수식 전후 값, 비교 범위와 진단을 각각 기록한다.
2. **미리보기 뒤 원본을 바꾼다.** 검토본은 그대로 두고 원본의 관련 행을 편집한다. 기존 미리보기와 실제 병합의 차이를 기록한다. 별도 케이스에서는 Unit별로 성공·충돌을 기록해 일부 성공을 전체 완료로 표시하지 않는지 확인한다.
3. **최종 XLSX를 다시 연다.** 공개 GRID canary는 `1 + 2`를 계산하는 셀의 저장된 결과를 일부러 `99999`로 둔다. checker의 기댓값은 `3`이다. 이 아이디어를 인도 검사에 쓰려면 내보낸 파일의 수식과 저장된 결과를 먼저 확인하고, 받는 쪽 앱으로 열어 표시값도 따로 확인한다. 앱이 열 때 재계산하면 오래된 저장값이 가려질 수 있다. GRID 검사는 재계산 여부를 가르는 예제이지 Univer의 병합·상용 XLSX 왕복 성능 검증이 아니다. [GRID checker](https://github.com/GRID-is/spreadsheet-benchmark/blob/compatibility-v1/replay/verify-recalc.ts) · [Univer 파일 교환의 확인 절차](https://docs.univer.ai/server/import-export#check-the-integration)

다음 질문: **승인 기록에 어떤 revision을 남기고, 병합 뒤 어떤 Unit별 결과와 파일 검사를 전달해야 “완료”라고 말할 수 있는가?**
