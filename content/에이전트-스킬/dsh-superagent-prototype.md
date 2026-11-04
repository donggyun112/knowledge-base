---
title: DSH Superagent — 작업 상태와 외부 실행을 분리하는 구조
source: https://github.com/deepseek-ai/dsh-superagent-prototype
source_updated: 2026-10-31
researched: 2026-11-04
radar_quadrant: Tools
radar_ring: Assess
reading_status: unread
tags: [agents, runtime, persistence, recovery, technology-radar]
---

# DSH Superagent — 작업 상태와 외부 실행을 분리하는 구조

## 자료와 검토 범위

- **원문**: [DeepSeek 팀의 공개 저장소](https://github.com/deepseek-ai/dsh-superagent-prototype)
- **확인한 버전**: [8c32a9d](https://github.com/deepseek-ai/dsh-superagent-prototype/tree/8c32a9dc5d72c033816c6a8110b37f40cf94fba4)
- **확인된 수정일**: 해당 커밋의 committer timestamp는 2026-10-31 20:06:31 +08:00이다. 프로젝트 최초 발행일과 구별한다.
- **수집일**: 2026-11-04 KST
- **단계 / 읽기 상태**: Tools / Assess / 읽기 전
- **검증 범위**: README, 실행·배포·아키텍처 문서와 Engine, Tickets, Effects 구현의 정적 검토. 설치·모델 호출·실행·장애 실험은 하지 않았다.

README는 공식 DeepSeek 제품이나 production-ready 소프트웨어가 아닌 연구 프로토타입이라고 명시한다. 내부 버전 및 설계 글과 공개 구현이 같지 않고, 글의 일부 구상은 아직 미구현이다. 이 노트는 공개 코드에서 확인한 경계만 다룬다.

## 핵심 요약

이 구현은 한 GitHub 저장소를 담당하는 DeepSeek Harness 번들이다. GitHub와 선택적 Feishu 입력을 받아 Router가 작업을 분류하고, Ticket별 Worker가 실제 작업을 한다. 자율성의 기반은 LLM을 계속 실행하는 것만이 아니라 **작업의 정체성, 권한 근거, 후속 입력과 외부 실행을 저장하는 일반 프로그램**이다.

| 구성 | 책임 |
| --- | --- |
| Router / main Session | 입력을 새 작업으로 수락하거나 기존 작업에 연결하고, 결과·질문을 원래 대화로 전달 |
| Ticket | 여러 실행 시도와 후속 이벤트에 걸쳐 유지되는 작업 |
| Assignment | 한 Ticket의 실행 시도. 재시도·복구 때 교체할 수 있음 |
| Executor / Worker Session | Ticket별 세션·디렉터리에서 조사·수정·테스트 수행 |
| Engine | Trigger, Thread, Decision, Ticket, Assignment 변경의 트랜잭션 경계 |
| Effects / Outbox | 실행·전달·발신 작업을 먼저 저장하고 커밋 이후 수행 |

[아키텍처 문서](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/8c32a9dc5d72c033816c6a8110b37f40cf94fba4/docs/007-architecture.md)는 Engine을 도메인 상태의 단일 쓰기 진입점으로 설명한다. Runtime은 구성 요소의 조립·기동·종료를 맡는다.

## 수락에서 외부 실행까지

1. Source가 외부 입력을 Trigger로 전달한다. Thread 구독으로 기존 Ticket에 후속 입력을 연결한다.
2. 새 작업 후보는 평가와 정책 검사를 거친다. Router의 판단과 작업을 허용하는 정책은 같은 개념이 아니다.
3. 수락 시 Ticket, 권한 근거인 Mandate, 첫 Assignment와 구독을 만들고 접수 응답 및 실행을 예약한다.
4. Engine 명령이 트랜잭션을 끝낸 뒤 Effects가 Worker 실행이나 메시지 전달을 수행한다.
5. Worker 결과와 PR 이벤트가 다시 Engine으로 들어와 상태를 갱신한다.

[Engine](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/8c32a9dc5d72c033816c6a8110b37f40cf94fba4/src/core/engine.ts)의 명령은 동기적으로 도메인 상태를 변경한다. [Tickets.create](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/8c32a9dc5d72c033816c6a8110b37f40cf94fba4/src/core/tickets.ts)는 작업과 첫 실행, 구독, 접수 응답 및 실행 요청을 연결한다. 이는 DB 변경과 외부 API 호출을 하나의 분산 트랜잭션으로 만든다는 뜻이 아니다.

## 영속 큐에서 볼 부분

[Effects 구현](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/8c32a9dc5d72c033816c6a8110b37f40cf94fba4/src/app/effects.ts)은 SQLite 기반이며 별도 Kafka나 Redis 큐가 아니다.

- 같은 `kind`와 `key`의 대기 작업은 합치면서 큐 위치를 유지한다.
- payload가 갱신될 때 `generation`을 증가시킨다. 실행 중이던 옛 시도의 완료 처리가 새 payload를 지우지 않도록 `seq`와 `generation`까지 일치해야 삭제한다.
- 종류별 동시성, 순서 보장 여부, 지수 백오프를 따로 설정한다. 순서가 필요한 종류는 앞선 실패가 뒤 항목을 막는다.
- 실행 슬롯이 없어 미루는 `Later`와 실제 실패를 구별한다. 전자는 실패 횟수를 증가시키지 않는다.

**이 노트의 해석:** 저장된 작업과 외부 효과를 분리하면 프로세스 중단 뒤 실행 의도를 복구하기 쉬워진다. 하지만 외부 요청 성공 직후 로컬 완료 기록 전에 죽는 경우까지 자동으로 exactly-once가 되는 것은 아니다. 외부 시스템의 멱등성·상태 조회 계약은 별도 검토 대상이다. [[에이전트-스킬/idempotent-api-retries|멱등 API 재시도]]와 함께 읽을 만하다.

## 작업 완료와 턴 종료는 다르다

[실행 문서](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/8c32a9dc5d72c033816c6a8110b37f40cf94fba4/docs/003-execution.md)는 `ready` 보고와 Ticket 완료를 구분한다. PR이 없는 ready는 완료될 수 있지만 PR을 따르는 작업은 관련 PR의 종료 조건을 확인한다. 사람의 후속 요청을 아직 처리 중이면 PR이 닫혀도 곧바로 끝내지 않는 조건이 있다.

재시도는 같은 세션·디렉터리·브랜치·PR을 유지하며 Assignment를 새로 만든다. 재시작 복구 메시지는 디렉터리, git 이력, GitHub 상태를 먼저 확인하고 외부 작업을 반복하지 말라고 안내한다. 전달된 입력과 실제 세션 이력에 들어간 입력도 구별한다. 이 안내 자체가 외부 중복을 수학적으로 방지하는 보장은 아니다.

## 운영상 한계

- Worker 디렉터리와 CLI wrapper는 보안 샌드박스가 아니다. [배포 문서](https://github.com/deepseek-ai/dsh-superagent-prototype/blob/8c32a9dc5d72c033816c6a8110b37f40cf94fba4/docs/006-deployment.md)는 Router·Worker가 운영자 OS 사용자 권한의 `danger-full-access`로 실행되며 home을 읽거나 절대 경로로 프로그램을 실행할 수 있다고 밝힌다.
- 작업 디렉터리의 prepare 명령이 없으면 빈 디렉터리에서 시작한다. 모든 Ticket이 자동으로 git worktree를 받는다고 가정하면 안 된다.
- 정책 검사, 프롬프트상의 작업 규칙, OS 접근 통제는 서로 다른 강도의 경계다. 예컨대 문서는 auto-merge 지침과 GitHub branch protection의 강제를 구분한다.
- 정적 검토로 장애 복구의 완전성, 처리량, 실제 과제 성능이나 운영 안전성을 입증한 것은 아니다. 다른 런타임에 같은 구조를 도입해야 한다는 결론도 아니다.

## 질문과 작은 검증 제안

아래는 아직 수행하지 않은 검증 후보다.

1. 외부 전송 성공과 DB 완료 기록 사이에 중단하면 같은 메시지가 다시 전송되는가? 외부 receipt 조회나 멱등 키로 불확실성을 해소할 수 있는가?
2. Effects 실행 중 같은 key의 payload를 갱신한 뒤 옛 실행이 끝나면 새 generation이 남는가?
3. PR 종료와 사람의 후속 입력이 경합할 때, 읽지 않은 요청이 사라지거나 중복 평가되지 않는가?
4. 순서 보장 큐의 앞선 실패가 다른 작업의 전달까지 막는 범위는 무엇인가?

실험한다면 실제 GitHub 쓰기나 유료 모델 호출 전에 모의 어댑터와 격리된 로컬 상태로 조건을 정의해야 한다. 결과가 없는 현재는 Assess를 유지한다.

## 결정 이력

- **2026-11-04**: 공개 구현을 정적으로 검토하고 Tools / Assess로 수집했다. 설치·실행·채택 근거는 없으며 읽기 상태는 읽기 전이다.
