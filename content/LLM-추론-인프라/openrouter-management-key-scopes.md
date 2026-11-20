---
title: OpenRouter 관리 키 — 접근 범위와 쓰기 권한은 다른 축이다
source: https://openrouter.ai/blog/announcements/scoped-management-keys/
type: documentation
category: LLM-추론-인프라
tags: [research, llm-gateway, authorization, observability, technology-radar]
researched: 2026-11-20
radar_quadrant: Platforms
radar_ring: Assess
reading_status: unread
---

# OpenRouter 관리 키 — 접근 범위와 쓰기 권한은 다른 축이다

**어느 자원에 접근할 수 있는지, 그 자원에서 무엇을 바꿀 수 있는지, 반환된 데이터가 어디까지를 대표하는지는 별도로 확인해야 한다.** OpenRouter 게이트웨이의 관리 API는 세 경계를 한꺼번에 볼 수 있는 사례다.

## 출처와 검토 범위

- **대표 원문**: [Tighter Access Controls for Management Keys](https://openrouter.ai/blog/announcements/scoped-management-keys/), OpenRouter, 2026-11-16 발행
- **세부 계약**: [Management API Keys](https://openrouter.ai/docs/guides/overview/auth/management-api-keys), 본문에 수정일 미표기
- **수집일**: 2026-11-20 KST
- **레이더 / 읽기 상태**: Platforms / Assess / 읽기 전
- **검증 범위**: 공개 공지와 공식 API 문서 본문 검토. 키 발급, API 호출, 계정 설정 변경, 사용량 대사는 하지 않았다.

## 문서에서 확인한 계약

- **범위**는 조직 전체 또는 워크스페이스 하나, **접근 수준**은 읽기 전용 또는 읽기·쓰기다. 둘 다 발급 시 정해진다. 관리 키는 일반 모델 추론용 키와 역할이 다르다. 워크스페이스 키로 해당 예산을 조회할 수 있지만, 예산을 설정하거나 삭제하려면 조직 범위의 쓰기 권한이 필요하다. 일부 워크스페이스 가드레일 정책과 키 할당은 워크스페이스 범위에서 관리할 수 있다. [범위별 경로 목록](https://openrouter.ai/docs/guides/overview/auth/management-api-keys#scope)
- **HTTP 메서드만으로 권한을 판정할 수 없다.** 분석 쿼리의 POST는 읽기 전용 키로 가능하다. 반대로 가드레일 정책의 멤버·API 키 할당을 조회하는 GET 두 개는 할당이 없을 때 이를 생성하므로 쓰기 권한이 필요하다. [읽기·쓰기 권한](https://openrouter.ai/docs/guides/overview/auth/management-api-keys#permissions)
- **정상 응답도 전체 이력을 뜻하지 않는다.** 워크스페이스 범위의 활동·분석 조회에는 해당 워크스페이스의 활동 조회 권한이 필요하고, 워크스페이스에 귀속되지 않은 이전 사용량 행은 결과에서 빠진다. 기본 워크스페이스도 예외가 아니다. [워크스페이스 범위](https://openrouter.ai/docs/guides/overview/auth/management-api-keys#workspace-scoped-keys)

## 활용 맥락과 한계

게이트웨이 운영 도구에는 자원 범위와 동작 권한을 따로 명시하고, 호출 메서드보다는 실제 효과를 기준으로 권한표를 만든다. 대시보드에 상위 관리 권한을 붙여 수치 차이를 없애기보다, 조회 결과에 포함되는 범위와 제외된 데이터를 먼저 표시한다. 범위 밖 데이터는 지출 0으로 해석하지 않는다.

이 문서는 누가 예산을 수정할 수 있는지 설명하지만, 동시 요청이 예산을 얼마나 초과할 수 있는지 또는 어느 시점에 금액이 확정되는지 보여 주지 않는다. 예산 수정 권한, 요청 허용 판단, 관측된 사용량, 확정 사용액은 다른 계약이다.

**작은 검증 제안, 미실행**: 실제 자격 증명 없이 모의 게이트웨이에 워크스페이스 두 개와 귀속 없는 과거 행 하나를 둔다. 자기 범위의 읽기 전용 분석 POST는 허용하고, 타 범위 조회와 상태 생성형 GET은 거부하는지 확인한다. 사용량 결과에는 귀속 없는 행이 빠졌다는 표시가 있는지도 별도로 검증한다.

**다음 질문**: 자동화에 필요한 최소 권한을 유지하면서도, 다루는 사용량의 범위가 바뀌면 이를 비교 전에 알아볼 수 있는가?

[플랫폼 레이더](../기술-레이더/platforms) · [[../TECHNOLOGY-RADAR|운영 기준]]
