---
title: LangGraph tools 스트림 — 도구가 끝나기 전에 진행 이벤트를 받기
source: https://github.com/langchain-ai/langgraph/pull/9779
type: implementation
category: 에이전트-스킬
tags: [research, agent, langgraph, streaming, technology-radar]
researched: 2026-11-27
radar_quadrant: Languages and frameworks
radar_ring: Assess
reading_status: unread
---

# LangGraph tools 스트림 — 도구가 끝나기 전에 진행 이벤트를 받기

**도구가 이벤트를 내보냈다고 해서 호출자가 즉시 받는 것은 아니다.** LangGraph의 변경은 이벤트 생성이 아니라, 실행 중에도 소비자가 큐를 읽을 수 있게 하는 스케줄링을 고친다.

- **원문**: [실시간 전달 수정 #9779](https://github.com/langchain-ai/langgraph/pull/9779), [공개 v2 타입 수정 #9778](https://github.com/langchain-ai/langgraph/pull/9778), [PyPI 배포 이력](https://pypi.org/project/langgraph/#history)
- **확인된 날짜**: 두 PR은 2026-11-24 GitHub main에 병합. 수집 시점 PyPI 최신 1.2.24는 2026-11-20 UTC 배포로, 두 병합보다 앞선다.
- **수집일**: 2026-11-27 KST
- **상태**: Languages and frameworks / Assess · 읽기 전
- **검증 범위**: 공개 PR 설명·회귀 테스트와 릴리스 이력 정적 검토. SDK 실행 또는 자체 지연 측정은 하지 않았다.

## 1. 이벤트 생산과 전달은 다른 경계

수정 전에는 `stream_mode="tools"`만 켰을 때 도구가 `runtime.emit_output_delta(...)`를 호출해도 이벤트가 스텝 종료까지 묶일 수 있었다. Pregel은 메시지나 사용자 정의 스트림 등에서는 큐 대기기를 시작했지만 tools 단독 모드에서는 시작하지 않았다. 노드가 하나뿐인 스텝이 호출자 쪽에서 인라인 실행되면 도구가 반환할 때까지 호출자가 진행 청크를 읽을 기회를 얻지 못한다. 메시지 모드를 같이 켠 테스트는 이 결함을 놓칠 수 있다.

[#9779](https://github.com/langchain-ai/langgraph/pull/9779)는 동기 `stream`과 비동기 `astream` 모두에서 tools 모드도 큐 대기기를 시작하게 한다. 그 경로의 단일 노드는 동기 워커 스레드 또는 별도 비동기 태스크에서 실행된다. 새 회귀 테스트는 소비자가 첫 delta를 받은 뒤에야 도구를 반환시킨다. 고정 지연을 재는 대신 **첫 청크 관측이 도구 반환보다 앞설 수 있는지**를 검사한다.

## 2. 타입, 실시간 전달, 복구를 따로 본다

[#9778](https://github.com/langchain-ai/langgraph/pull/9778)는 기존 실행 동작은 바꾸지 않고 `StreamMode`와 v2 `StreamPart`에 tools를 추가한다. `tool-started`, `tool-output-delta`, `tool-finished`, `tool-error`는 이벤트 이름으로 구별할 수 있다. 사용 중인 패키지가 두 변경을 실제로 포함하는지 확인해야 한다. 공개 타입이 맞는 것과 청크가 실시간으로 도착하는 것은 다른 계약이다.

이 수정만으로 분산 UI까지의 지연 상한, 연결이 끊긴 뒤 재생, 병렬 도구 수 제한, 사용자 중단 이후의 실행 정지는 보장되지 않는다. 라이브 전달과 호출 식별자 보존도 별개다. 후자는 [[에이전트-스킬/dify-tool-call-identity|Dify 도구 호출 ID]], 재시작 뒤 어떤 상태를 읽을지는 [[에이전트-스킬/langgraph-persistence|LangGraph의 실행 상태와 장기 메모리]]를 참고한다.

## 3. 다음에 확인할 작은 테스트

동일한 합성 도구를 동기·비동기에서 각각 호출한다. 단일 노드와 tools 단독 모드로 첫 delta를 낸 후, 소비자 확인 신호를 받아야 반환하게 한다. 첫 delta 관측 → 신호 → 반환 → 완료 이벤트의 순서와 호출 ID를 확인한다. tools와 messages를 같이 켠 대조군을 따로 두고, 대기 제한은 교착 감지에만 쓴다. HTTP나 프록시를 포함한 전달, 연결 재생, 에러 경로는 별도 테스트로 나눈다.
