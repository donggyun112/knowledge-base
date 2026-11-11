---
title: 재시도 예산과 지터 — 복구가 과부하를 키우지 않게 하기
source: https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter
type: article
category: 에이전트-스킬
tags: [backend, retry, timeout, jitter, reliability, technology-radar]
researched: 2026-11-11
radar_quadrant: Techniques
radar_ring: Assess
reading_status: unread
---

# 재시도 예산과 지터 — 복구가 과부하를 키우지 않게 하기

멱등성은 같은 효과의 중복을 막는다. 하지만 안전하게 반복할 수 있는 요청도 자원을 소비한다. 이 자료는 **다시 호출해도 되는가**에 더해 **언제, 어디서, 얼마나 다시 호출할 것인가**를 검토하게 한다.

- **주 자료**: [Timeouts, retries, and backoff with jitter](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter), Amazon Builders’ Library, Marc Brooker. [기존 URL](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)은 확인 시 Builder Center로 이동했다.
- **발행·수정일**: 현재 주 자료 페이지는 둘 다 2019-12-05로 표시한다.
- **보완 자료**: [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/), Marc Brooker. 발행 2015-03-04, 본문 업데이트 표기 2023-05(일 미표기).
- **수집일**: 2026-11-11 KST
- **상태**: Techniques / Assess / 읽기 전
- **검증 범위**: 두 원문 본문 검토. SDK 설치·호출·부하 실험·시뮬레이터 실행은 하지 않았다.

## 주 자료의 핵심: 재시도는 추가 부하다

- 타임아웃은 연결과 요청을 나눠 검토한다. DNS·TLS까지 포함되는지 확인해야 한다. 같은 리전에서는 허용할 오탐 타임아웃 비율에 맞춘 지연 백분위가 출발점이지만 인터넷 지연이나 좁은 분포에는 보정이 필요하다.
- 여러 호출 계층이 독립적으로 반복하면 하위 부하가 곱해진다. 원문의 5계층·계층당 3회 시도 예시는 243배다. 저비용 작업에서는 한 계층이 재시도를 맡도록 권한다.
- 최대 대기시간만 제한하면 그 간격으로 계속 재시도할 수 있다. 횟수 제한과 로컬 토큰 버킷으로 재시도량도 제어한다.
- 지터는 동시 재호출을 시간상 분산한다. 주기 작업에는 호스트별로 일관된 분산값을 사용해 패턴을 추적하는 접근도 설명한다.

이는 [작성자의 운영 경험과 설계 지침](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter)이다. 특정 타임아웃 값이나 비용 절감률을 모든 시스템에 적용하는 규칙은 아니다.

## 보완 자료: 지터의 효과를 어떻게 읽을까

작성자는 동일 객체에 동시 쓰기하는 OCC 시뮬레이션에서 지터 없는 지수 백오프와 여러 지터 방식을 비교했다. Full Jitter는 대기 구간 전체에서 무작위 값을 선택하고, Equal Jitter는 대기의 일부를 유지한다. Decorrelated Jitter는 이전 대기값에 따라 다음 무작위 범위를 조정한다.

해당 실험에서 Full과 Decorrelated는 작업량과 완료시간의 절충이 있었다. 지터가 경쟁 작업량의 이차적 증가 자체를 없애지는 않았다. **이 결과는 특정 경쟁 모형의 시뮬레이션이며 에이전트·검색 서비스의 운영 실측이 아니다.** SDK가 이미 처리하는 재시도에 같은 로직을 겹쳐 넣으라는 권고도 아니다. [실험과 한계](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)

## 활용 맥락과 작은 검증 제안

아래는 이 노트의 제안이며 실행하지 않았다. 도구 호출을 감싸는 런타임, HTTP 클라이언트, 작업 큐가 모두 재시도할 수 있는 백엔드에서 먼저 책임을 표로 나누면 좋다.

1. 논리 작업 하나를 기준으로 각 계층의 최초 시도·재시도 횟수, 전체 deadline, 취소 전파 여부를 기록한다. 설정의 ‘3회’가 전체 시도인지 추가 재시도인지 명시한다.
2. 별도 검증에서는 같은 합성 실패열에 단일 계층 재시도와 중첩 재시도를 적용해 총 하위 호출 수, 성공률, p99 완료시간을 함께 비교한다.
3. 지터 유무 비교는 동일한 횟수·시간 예산에서 한다. 성공률만 보지 말고 초당 최대 호출과 완료 후 뒤늦은 시도도 센다.
4. 응답 소실과 과부하를 구별한다. 멱등 키·결과 조회로 효과를 확인하는 절차는 부하 분산과 별도로 둔다.

**남은 질문:** 재시도를 추가할 때 복구되는 실패보다 증폭되는 하위 호출이 더 많아지는 경계는 어디인가?

## 결정 이력

- **2026-11-11**: 두 공개 원문을 하나의 Techniques / Assess 항목으로 수집했다. 직접 검증·채택 근거가 없으므로 읽기 전 상태를 유지한다.

[[에이전트-스킬/idempotent-api-retries|멱등 API의 효과 보장]] · [[기술-레이더/techniques|기법 레이더]] · [[index|주제별 목차]]
