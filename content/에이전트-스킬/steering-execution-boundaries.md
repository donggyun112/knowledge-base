---
title: 실행 중 지시 변경 — 접수·모델 반영·도구 중단의 경계
source: https://docs.openclaw.ai/concepts/queue-steering
type: documentation
category: 에이전트-스킬
tags: [research, agent, runtime, steering, backend, technology-radar]
researched: 2026-11-16
radar_quadrant: Techniques
radar_ring: Assess
reading_status: unread
---

# 실행 중 지시 변경 — 접수·모델 반영·도구 중단의 경계

**새 지시가 접수됐다는 사실만으로 모델이 이미 반영했거나 실행 중인 도구가 멈췄다고 판단하면 안 된다.** OpenClaw의 큐와 Responses API의 steering을 비교해, 대화 입력과 실행 제어 사이의 계약을 읽는다.

- **대표 원문**: [OpenClaw: Steering queue](https://docs.openclaw.ai/concepts/queue-steering)
- **비교 원문**: [OpenAI: Mid-turn steering](https://developers.openai.com/api/docs/guides/steering)
- **발행·수정일**: 두 문서 본문 모두 날짜 미표기. 사이트의 릴리즈 날짜를 이 문서의 수정일로 대체하지 않음
- **수집일**: 2026-11-16 KST
- **상태**: Techniques / Assess · 읽기 전
- **검증 범위**: 공식 문서 본문 정적 검토. SDK·런타임 설치, 모델 호출, 도구 실행 및 장애 실험은 하지 않음. 배포 버전별 실제 동작은 미검증

## 1. OpenClaw: 입력을 끼워 넣을 경계는 어디인가

일반 steering은 이미 실행 중인 도구를 중단하지 않는다. 내장 런타임의 순차 호출은 첫 실행 가능한 도구를 steering 검사 없이 시작한다. 같은 assistant 메시지에서 하나라도 시작한 뒤에는 뒤따르는 호출 전에 검사하여, 대기 중인 입력이 있으면 아직 시작하지 않은 나머지를 건너뛴다. 병렬 묶음은 시작 시 steering 검사 없이 함께 실행하며 대기 입력 때문에 생략되지 않는다.

묶음이 끝나면 다음 모델 호출 전에 입력을 반영한다. 생략한 호출에도 합성 결과를 남겨 도구 요청과 결과의 짝을 유지한다. Control UI의 **Send now**는 지원되는 실행 도구만 중단하는 별도 경로다. 프로세스 상태 조회를 중단해도 독립된 백그라운드 명령은 계속될 수 있다.

Codex app-server 경로는 자체 `turn/steer`와 모델 경계 스케줄링을 사용한다. 여기에 내장 런타임의 도구별 선점 동작을 그대로 적용하면 안 된다. 문서는 transcript 저장 확인도 모델이 읽었다는 증거와 구분한다. [공식 설명](https://docs.openclaw.ai/concepts/queue-steering)

## 2. Responses API: 접수 뒤에도 후속 응답을 추적한다

문서는 GPT-6 계열의 WebSocket Responses API를 대상으로 한다. `response.created` 뒤 같은 연결에서 응답 ID를 지정해 `response.steer`를 보낸다. `response.steer.accepted`는 **큐 접수**이지 반영 완료가 아니다.

서버는 현재 출력 항목과 이미 진행 중인 hosted tool 작업을 마친 뒤 후속 응답을 만든다. 애플리케이션의 도구 결과나 승인이 필요한 경우는 예외다. 접수 직후 새 `response.create`를 중복 전송하지 않고 이벤트를 계속 읽어야 한다. 원래 응답은 `incomplete`와 `steered` 사유로 끝나거나, 먼저 정상 완료된 뒤에도 steering 후속 응답이 생길 수 있다.

이미 보낸 출력·이전 효과를 되돌리거나 시작된 도구를 취소하지 않는다. 자동 후속 응답은 원 요청 설정을 물려받지만 토큰·도구 호출 한도는 응답마다 별도로 적용된다. 따라서 원래 응답의 완료와 전체 상호작용의 완료, 응답별 한도와 전체 예산을 구별해야 한다. [공식 설명](https://developers.openai.com/api/docs/guides/steering)

## 기술적 활용 맥락: 제어면과 실제 효과를 분리하기

다음은 두 계약에서 도출한 설계 검토 관점이며 제품의 추가 보장이 아니다.

| 관찰할 사건 | 아직 단정할 수 없는 것 |
| --- | --- |
| 입력 전송·큐 접수 | 모델이 읽고 계획을 바꿨는지 |
| transcript 저장 | 해당 입력을 포함한 모델 호출이 시작됐는지 |
| 미시작 도구 생략 | 이미 실행 중인 도구도 멈췄는지 |
| 호출 중단·대기 종료 | 외부 효과나 백그라운드 작업까지 취소됐는지 |
| 원 응답 완료 | 새 지시를 처리한 후속 응답도 완료됐는지 |

장시간 도구를 쓰는 대화형 에이전트에서 UI 상태와 실행 로그를 설계할 때 유용하다. 메시지 ID, 도구 시작·종료, 입력을 포함한 모델 요청, 후속 응답 ID를 연결해야 사용자의 정정이 언제 효력을 얻었는지 설명할 수 있다.

## 한계와 다음 질문

두 제품의 API가 같은 것은 아니며 문서만으로 반영 지연·신뢰성·운영비 개선을 수치화하지 않는다. 민감한 외부 작업의 승인 철회는 자연어 steering만 믿지 말고 실행 직전 권한 검사와 취소 결과 확인을 별도로 검토할 문제다.

작은 실험은 **제안만** 남긴다. 유료 모델이나 실제 외부 시스템 대신 가짜 도구와 이벤트 스케줄로 다음을 확인할 수 있다.

1. 첫 도구 시작 전·실행 중·다음 도구 시작 직전에 입력을 넣고, 순차/병렬에서 시작한 도구 수와 생략 결과를 따로 센다.
2. 큐 접수 직후 연결이 끊겼을 때 입력 전달 여부를 모르는 상태와 확실한 미전달을 구분한다. 불확실한 입력을 무조건 재전송하면 어떤 중복이 생기는가?
3. 원 응답의 정상 완료 뒤 후속 응답이 생기는 경우 UI가 너무 일찍 완료를 표시하지 않는가?
4. 도구 대기만 중단된 경우에도 가짜 외부 효과가 계속 발생하는지 기록한다. 중단 확인과 효과 확인에 필요한 증거는 무엇인가?

관련: [[에이전트-스킬/mcp-tasks-cancellation-contract|MCP Tasks의 취소 계약]] · [[에이전트-스킬/a2a-task-lifecycle|A2A 작업 수명주기]] · [[기술-레이더/techniques|기법 레이더]]
