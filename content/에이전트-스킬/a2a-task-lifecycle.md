---
title: A2A 작업 수명주기 — 스트림 재연결과 실행 재시도의 경계
source: https://a2a-protocol.org/latest/topics/life-of-a-task/
type: documentation
category: 에이전트-스킬
tags: [research, a2a, agent, streaming, backend, technology-radar]
researched: 2026-11-07
radar_quadrant: Techniques
radar_ring: Assess
reading_status: unread
---

# A2A 작업 수명주기 — 스트림 재연결과 실행 재시도의 경계

**연결이 끊긴 것, 작업이 끝난 것, 작업을 다시 실행하는 것은 서로 다른 사건이다.** A2A 공식 문서는 이 구분을 작업 식별자와 상태 전이로 설명한다.

- **대표 원문**: [Life of a Task](https://a2a-protocol.org/latest/topics/life-of-a-task/)
- **보조 원문**: [Streaming & Asynchronous Operations](https://a2a-protocol.org/latest/topics/streaming-and-async/), [Protocol Specification](https://a2a-protocol.org/latest/specification/)
- **발행·수정일**: 대표 문서 본문에는 미표기. 저장소의 해당 파일 마지막 수정 커밋은 [2026-09-10 UTC, 6d6640c](https://github.com/a2aproject/A2A/commit/6d6640c29b102f7a8d23784901351b5d2454fe71). 이는 최초 발행일이나 전체 명세의 수정일이 아님
- **수집일**: 2026-11-07 KST
- **상태**: Techniques / Assess · 읽기 전
- **검증 범위**: 공식 문서 본문과 명세의 작업 취소·구독·멱등성 조항 검토. SDK 설치·실행·네트워크 장애 실험은 하지 않음

## 1. 대화 맥락과 실행 단위

`contextId`는 관련 메시지와 여러 작업을 묶고, `taskId`는 개별 작업을 가리킨다. 간단한 상호작용은 독립적인 Message로 끝날 수 있고, 추적할 실행은 Task로 관리한다.

`input-required`처럼 추가 입력을 기다리는 상태와 `completed`, `failed`, `canceled`, `rejected` 같은 종료 상태를 구분한다. 종료된 작업은 다시 시작하지 않는다. 결과를 수정하려면 같은 맥락에서 새 작업을 만들고 이전 작업을 참조한다. 산출물의 수정 관계와 어떤 버전을 채택할지는 클라이언트가 관리하며, 그 버전 이력이 프로토콜에 자동으로 포함되지는 않는다. [작업 수명주기](https://a2a-protocol.org/latest/topics/life-of-a-task/)

## 2. 결과를 받는 경로

스트리밍을 지원하는 서버는 Agent Card에 기능을 표시한다. `SendStreamingMessage`로 시작한 SSE에는 작업 상태와 산출물 갱신이 흐른다. 산출물 청크의 `append`와 `lastChunk`는 조립 의미를 전달한다.

연결을 오래 유지하기 어렵다면 push notification을 사용할 수 있다. 수신자는 알림의 진위를 확인하고 `GetTask`로 최신 작업을 조회하는 흐름을 구성한다. 웹훅 목적지 검증, 발신자 인증과 재전송 공격 방어도 필요하다. 알림 기능 자체가 안전한 전달이나 수신 처리를 대신하지 않는다. [스트리밍·비동기 가이드](https://a2a-protocol.org/latest/topics/streaming-and-async/)

## 3. 복구할 때 중요한 명세 계약

- **재구독**: `SubscribeToTask`의 첫 이벤트는 현재 Task다. 조회 후 구독 사이에 생기는 정보 공백을 줄이는 계약이다. 종료된 작업에 대한 구독은 지원되지 않는다. 이 현재 상태 스냅샷을 과거 모든 델타의 재생 보장으로 해석해서는 안 된다.
- **재전송**: Send Message의 멱등성은 MAY다. 서버가 `messageId`를 이용해 중복을 감지할 수 있지만 모든 구현이 중복 실행을 막는다는 보장은 아니다.
- **취소**: `CancelTask`는 취소를 시도하며 성공을 보장하지 않는다. 반환된 상태를 확인해야 한다. 취소 요청의 멱등성과 이미 발생한 외부 효과의 되돌림은 다른 문제다.

[명세 §3.1.5–3.1.6, §3.3.1](https://a2a-protocol.org/latest/specification/)

## 기술적 활용 맥락과 한계

다음은 문서에서 도출한 설계 검토 관점이다. 프런트엔드의 연결 상태와 백엔드의 실행 상태를 별도로 두고, 재연결 시 현재 작업을 대조할지 새 실행을 요청할지 구분하는 데 유용하다. [[에이전트-스킬/idempotent-api-retries|멱등 API 계약]]과 함께 읽으면 조회 복구와 외부 효과 재실행의 차이를 점검할 수 있다.

이 자료만으로 특정 SDK의 저장 내구성, 이벤트 보관 기간, 장애 후 복구 성능이나 운영비 절감을 판단할 수는 없다. `latest` 문서는 변할 수 있으므로 구현 시 지원 버전과 메서드 이름을 다시 맞춰야 한다. 여기서는 프로토콜 계약을 수집했으며 특정 서비스 분리나 프레임워크 채택을 권하지 않는다.

## 다음 질문과 작은 검증 제안

아래는 **미실행 제안**이다.

1. 산출물 전송 도중 연결이 끊기면 현재 Task만으로 화면을 복구할 수 있는가? 부분 청크와 완성 산출물의 우선순위를 정하고 비교한다.
2. 응답을 받지 못한 동일 `messageId`를 다시 보내면 새 작업이 생기는가? 서버의 중복 감지 범위·보존 기간을 명시한 뒤 확인한다.
3. 완료와 취소가 경합하면 어떤 상태가 남는가? UI 표시와 실제 외부 효과를 각각 대조한다.

## 결정 이력

- **2026-11-07**: 공개 공식 문서를 Techniques / Assess로 수집. 실행 검증과 기술 채택은 하지 않았으며 읽기 상태는 읽기 전이다.

[[기술-레이더/index|기술 레이더]] · [[기술-레이더/techniques|기법 목록]] · [[index|전체 목차]]
