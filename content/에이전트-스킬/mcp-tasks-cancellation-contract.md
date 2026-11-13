---
title: MCP Tasks — 비동기 작업의 완료·취소·보존 계약
source: https://tasks.extensions.modelcontextprotocol.io/specification/2026-07-28/tasks
type: documentation
category: 에이전트-스킬
tags: [mcp, async-task, cancellation, reliability, technology-radar]
researched: 2026-11-13
radar_quadrant: Techniques
radar_ring: Assess
reading_status: unread
---

# MCP Tasks — 비동기 작업의 완료·취소·보존 계약

긴 도구 실행을 요청·응답 연결과 분리할 때는 작업 ID만으로 충분하지 않다. **요청을 받았다는 응답, 도구의 결과, 실제 외부 효과를 구분하는 계약**이 필요하다. MCP Tasks 확장은 그 차이를 구체적으로 검토할 자료다.

- **원문**: [MCP Tasks 확장 명세, 2026-07-28 버전](https://tasks.extensions.modelcontextprotocol.io/specification/2026-07-28/tasks)
- **확인한 고정 출처**: [명세 본문](https://github.com/modelcontextprotocol/ext-tasks/blob/cc9aaac1047a9440b07486e38f37060bbebeef4c/specification/2026-07-28/tasks.md), [TypeScript 스키마](https://github.com/modelcontextprotocol/ext-tasks/blob/cc9aaac1047a9440b07486e38f37060bbebeef4c/schema/2026-07-28/schema.ts)
- **발행·수정일**: 발행일은 별도 미표기. `2026-07-28`은 명세 버전명이다. 확인한 본문의 마지막 수정 커밋은 [2026-10-09 22:40:57 UTC](https://github.com/modelcontextprotocol/ext-tasks/commit/899c1bbc869567670093face3591b39c28ce3219)다.
- **수집일**: 2026-11-13 KST
- **상태**: Techniques / Assess / 읽기 전
- **검증 범위**: 공식 명세·스키마와 변경 이력의 정적 검토. SDK 설치·도구 호출·장애 실험은 하지 않았다.

## 명세에서 확인한 경계

- **생성**: 요청별 capability 선언을 전제로 서버가 비동기 전환을 선택한다. 현재 대상은 `tools/call`이다. 생성 응답 전에 해당 ID의 `tasks/get`이 조회 가능해야 한다.
- **완료**: `completed`에도 `isError: true`인 도구 결과가 포함된다. `failed`는 JSON-RPC 실행 오류다. 상태명만으로 업무 성공을 판단할 수 없다.
- **취소**: `tasks/cancel` 응답은 접수 확인이다. 실제 중단이나 최종 `cancelled` 전환을 보장하지 않는다.
- **보존**: `ttlMs`는 생성 시점 기준이며 변경 가능하다. 만료 뒤 실패 처리·삭제가 가능하므로 강제 실행 종료 시각으로 해석하지 않는다.
- **추가 입력**: `inputRequests`는 `tasks/get`으로 받고 `tasks/update`로 응답한다. 키는 작업 수명 동안 재사용하지 않으며, 클라이언트는 중복 표시·응답을 피한다. update 응답 뒤에도 관측 상태 반영은 늦을 수 있다.

세부 규범은 [고정 본문의 생성·폴링·입력·취소 절](https://github.com/modelcontextprotocol/ext-tasks/blob/cc9aaac1047a9440b07486e38f37060bbebeef4c/specification/2026-07-28/tasks.md)에서 확인한다.

## 이전 Tasks와 섞지 않기

[2025-11-25 명세](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks)는 요청자가 task 사용을 선택하고 `tasks/result`로 결과를 받았다. `isError: true`는 `failed`에 대응했고, 취소 응답 전 상태를 `cancelled`로 바꾸도록 요구했다. 그 버전도 실제 실행 중단까지 보장하지는 않았다.

이번 확장은 서버가 생성 여부를 정하고 `tasks/get`에 결과를 담는다. 따라서 상태 이름이 같다는 이유로 이전 클라이언트의 완료·취소 처리를 재사용하면 의미가 달라질 수 있다.

## 활용 맥락과 한계

아래는 이 노트의 설계 해석이다. 외부 배치 API를 도구로 감싸거나 장시간 에이전트 작업을 관리하는 백엔드에서 다음 항목을 따로 저장하면 좋다.

| 관찰 | 별도로 확인할 것 |
| --- | --- |
| 작업 생성 응답을 받음 | 작업 ID 저장과 재접속 후 조회 |
| 작업 상태가 completed | 도구 오류 여부와 기대한 외부 결과 |
| 취소 응답을 받음 | 취소 요청 시각, 실제 실행의 최종 결과 |
| TTL이 지남 | 결과 증거의 보존 기간과 조회 불가 처리 |

작업 ID와 입력 키는 서로 다른 범위의 식별자다. 입력 중복 억제를 외부 효과의 정확히 한 번 실행 보장으로 확대해서는 안 된다. 취소 후에도 외부 효과가 남을 수 있는 작업은 제품의 취소 안내·정산·결과 조회 정책을 별도로 정해야 한다.

**문서 일관성에도 주의가 필요하다.** 확인한 [스키마](https://github.com/modelcontextprotocol/ext-tasks/blob/cc9aaac1047a9440b07486e38f37060bbebeef4c/schema/2026-07-28/schema.ts)는 `CreateTaskResult`를 평평한 `Result & Task` 형태로 정의하지만 본문에는 아직 `embedded task`, `task.taskId` 설명이 남아 있다. 예제만 복사하지 말고 고정 버전의 타입과 규범을 대조해야 한다. 실제 SDK 간 호환성·저장 내구성은 이 정적 검토에서 검증하지 않았다.

## 작은 검증 제안

실행하지 않은 제안이다.

1. 같은 모의 도구에 정상 결과, `isError: true`, JSON-RPC 오류를 넣고 상태와 업무 성공 표시가 구분되는지 검사한다.
2. 취소 접수 직후 작업이 완료되는 경쟁 상황을 만들고, 화면이 확인되지 않은 중단을 확정적으로 알리지 않는지 본다.
3. 입력 응답 후 오래된 `input_required` 스냅샷을 다시 받는 경우를 구성한다. 같은 키의 질문이 중복 표시되거나 외부 효과가 반복되는지 분리해서 확인한다.
4. 생성 응답 직후 재접속, TTL 만료 전후 조회를 각각 설계한다. 상태 복구와 결과 증거 보존의 성공 기준을 별도로 둔다.

**남은 질문:** 프로토콜의 작업 상태와 사용자가 기대하는 완료·취소를 어떤 증거로 연결할 것인가?

## 결정 이력

- **2026-11-13**: 공식 확장 명세를 Techniques / Assess로 수집했다. 직접 검증·채택 근거가 없으므로 읽기 전 상태를 유지한다.

[[에이전트-스킬/a2a-task-lifecycle|A2A 작업 수명주기]] · [[에이전트-스킬/mcp-authorization-boundaries|MCP 보안 경계]] · [[에이전트-스킬/idempotent-api-retries|멱등 API 재시도]] · [[기술-레이더/techniques|기법 레이더]] · [[index|주제별 목차]]
