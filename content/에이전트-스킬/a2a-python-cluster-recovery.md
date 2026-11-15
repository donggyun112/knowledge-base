---
title: A2A Python 클러스터 — 상태 공유와 장애 복구의 경계
source: https://github.com/a2aproject/a2a-python/pull/1281
type: implementation
category: 에이전트-스킬
tags: [research, a2a, agent, backend, reliability, technology-radar]
researched: 2026-11-15
radar_quadrant: Languages and frameworks
radar_ring: Assess
reading_status: unread
---

# A2A Python 클러스터 — 상태 공유와 장애 복구의 경계

**다른 복제본에서 작업을 조회할 수 있다는 것과, 실행 중인 복제본이 죽어도 작업을 끝낼 수 있다는 것은 다르다.** A2A Python의 출시된 클러스터 기능과 후속 장애 복구 제안을 나란히 읽으면 이 경계가 드러난다.

- **대표 원문**: [클러스터 모드 구현 PR #1281](https://github.com/a2aproject/a2a-python/pull/1281)
- **보조 원문**: [v1.2.0 릴리즈](https://github.com/a2aproject/a2a-python/releases/tag/v1.2.0), [장애 복구 요구와 운영 경험 #1324](https://github.com/a2aproject/a2a-python/issues/1324), [복구 구현 Draft PR #1395](https://github.com/a2aproject/a2a-python/pull/1395)
- **확인된 날짜**: #1281 생성·병합 및 v1.2.0 발행 2026-09-29 UTC. #1324 생성 2026-10-07, GitHub 최종 갱신 2026-10-18 UTC. #1395 생성·최종 갱신 2026-10-27 UTC. 갱신 시각은 GitHub 항목 메타데이터이며 본문 수정만 뜻하지 않음
- **수집일**: 2026-11-15 KST
- **상태**: Languages and frameworks / Assess · 읽기 전
- **검증 범위**: 공식 릴리즈·PR·이슈 본문과 상태를 정적 확인. SDK 설치·실행·장애 주입은 하지 않음. 아래 테스트 경험은 작성자의 보고이지 이 노트의 재현 결과가 아님

## 1. 출시된 기능: 상태 충돌과 이벤트 전달

v1.2.0은 #1281의 다중 복제본 클러스터 모드를 포함한다. `DefaultRequestHandlerV2`에 선택적으로 다음 두 저장 경로를 연결한다.

- `VersionedTaskStore`: 읽었던 작업 revision을 저장 시 비교해 다른 복제본의 변경을 조용히 덮어쓰지 않는다.
- `TaskEventStream`: 실행 복제본 밖에서도 이벤트를 전달할 수 있게 공유 기록을 둔다. 재구독은 현재 작업을 반환한 뒤 그 지점부터 이벤트를 따라간다.

DB 구현은 `task_versions`, `task_events`를 추가한다. 원격 취소도 공유 상태에 기록되며 실제 실행 복제본은 다음 저장 시 이를 알아차린다. 따라서 취소 기록 순간 모든 실행이 즉시 멈춘다고 해석하면 안 된다. 작성자는 실제 Postgres·MySQL의 두 복제본을 이용한 조회·구독·취소·후속 대화 테스트를 보고한다. [#1281](https://github.com/a2aproject/a2a-python/pull/1281), [릴리즈](https://github.com/a2aproject/a2a-python/releases/tag/v1.2.0)

## 2. 남는 구멍: 살아 있는 복제본 간 조정과 죽은 실행의 정리

#1324 작성자는 실행 복제본이 중간에 죽으면 작업이 `WORKING`에 남고, 다른 복제본의 구독도 종료 이벤트를 기다린다고 보고한다. 상태 timestamp는 에이전트 이벤트가 있을 때 움직이므로 긴 도구 호출과 죽은 프로세스를 구분하는 heartbeat가 아니다.

특히 직접 운영한 heartbeat·sweeper에서 만났다는 다음 경쟁 조건이 읽을 가치가 있다.

1. `execute()` 반환이 아니라 **종료·중단 상태의 영속 저장 이후** lease를 해제해야 한다. 큐에만 남은 종료 이벤트와 프로세스 종료 사이에 틈이 있다.
2. 재개된 턴의 첫 저장은 이전 `INPUT_REQUIRED` 상태를 다시 저장할 수 있다. 상태 값만 보고 lease를 해제하면 실행 시작부터 보호가 사라진다.
3. 해제 뒤 도착한 heartbeat가 upsert로 lease를 되살리지 않아야 한다.
4. tenant별 조회 필터가 있다면 sweeper에도 작업 소유자 범위가 필요하다.

이는 이슈 작성자의 경험과 제안이며 SDK 전체의 보장으로 일반화하지 않는다. [#1324](https://github.com/a2aproject/a2a-python/issues/1324)

## 3. 아직 제안: lease와 실패 확정

수집 시점 #1395는 **열린 Draft PR이며 미병합**이다. v1.2.0의 기능으로 소개하면 안 된다.

제안은 실행 중 lease를 갱신하고, 만료된 lease를 `AbandonedTaskSweeper`가 선점하여 작업을 `FAILED`로 바꾸는 방식이다. 실패는 이벤트·푸시 경로에도 전달한다. 이미 입력을 기다리는 작업은 lease만 정리한다. 다른 복제본이 lease를 가진 동안의 후속 실행은 거절하며, lease를 잃은 실행자는 중지하고 늦은 이벤트를 버린다고 설명한다. lease store는 선택 사항이다.

중요한 구분은 **실패를 판정하고 알리는 복구**이지 자동 재실행·체크포인트 재개가 아니라는 점이다. #1324의 선택적 재실행 정책 제안과도 구별해야 한다. PR 작성자는 DB별 테스트와 프로세스 강제 종료 테스트를 보고하지만 여기서는 검증하지 않았다. [#1395](https://github.com/a2aproject/a2a-python/pull/1395)

## 활용 맥락과 한계

다중 복제본 에이전트 서버의 설계 검토에 유용하다. 요구를 **상태 충돌 방지 / 구독 전달 / 실행 소유권 / 죽은 실행 판정 / 외부 효과의 중복 방지**로 나누어 확인할 수 있다.

이 노트의 해석으로는 DB revision 비교와 늦은 이벤트 차단만으로 외부 API의 중복 효과까지 방지했다고 볼 수 없다. 오래된 실행자가 이미 외부 요청을 보냈다면, 외부 시스템의 멱등 키나 이전 실행 권한을 거부하는 장치가 별도로 필요할 수 있다. 공개 자료만으로 exactly-once 실행, 운영비 절감, 모든 장애에서의 안전성을 주장하지 않는다. Draft 내용과 API는 이후 바뀔 수 있다.

## 다음 질문과 작은 실험 제안

아래는 제안이며 실행하지 않았다.

- 종료 이벤트를 큐에 넣은 뒤 영속 저장 전에 중단하면, 작업·lease·구독자는 각각 어떤 상태에 남는가?
- DB 단절이 lease TTL을 넘은 뒤 오래된 실행자가 돌아오면, 상태 저장뿐 아니라 외부 효과도 차단되는가? 효과 수와 저장된 이벤트 수를 따로 센다.
- 입력 대기에서 재개하는 순간과 heartbeat·lease 해제가 겹칠 때 잘못된 실패 판정이 없는가?
- 검증 버전을 고정하고 정상 완료·프로세스 사망·느린 도구 호출을 분리해 탐지 지연과 오탐을 측정할 수 있는가?

관련: [[에이전트-스킬/a2a-task-lifecycle|A2A 프로토콜의 작업 수명주기]] · [[에이전트-스킬/idempotent-api-retries|멱등 API 재시도]] · [[기술-레이더/languages-frameworks|언어와 프레임워크 레이더]]
