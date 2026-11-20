---
title: 기술 레이더 플랫폼
type: radar-quadrant
radar_quadrant: Platforms
tags: [technology-radar]
researched: 2026-11-20
---

# 플랫폼

코드 실행, 격리와 배포의 기반이 되는 환경.

[[기술-레이더/index|기술 레이더 전체]] · [기법](techniques) · [플랫폼](platforms) · [도구](tools) · [언어와 프레임워크](languages-frameworks)

## Adopt

현재 등록된 항목이 없다.

## Trial

현재 등록된 항목이 없다.

## Assess

### [OpenRouter 관리 키](../LLM-추론-인프라/openrouter-management-key-scopes)

LLM 게이트웨이의 자원 범위, 동작 권한, 사용량 집계 범위를 나눠 보는 운영 사례.

- **수집일**: 2026-11-20 KST
- **읽기 상태**: 읽기 전
- **검증 상태**: 공식 공지와 API 문서 본문 검토. 실제 호출이나 설정 변경은 하지 않음
- **다음 질문**: 조회와 상태 변경을 어떻게 구분하고, 집계에서 빠지는 데이터는 어떻게 표시할 것인가?

[상세 노트에서 권한 경계와 검증 제안 읽기](../LLM-추론-인프라/openrouter-management-key-scopes)

### [gVisor 보안 경계](../LLM-추론-인프라/gvisor-security-boundaries)

애플리케이션 커널 격리와 파일·네트워크 접근 정책을 구분해 검토할 자료.

- **수집일**: 2026-11-10 KST
- **읽기 상태**: 읽기 전
- **검증 상태**: 공식 문서 본문 검토. 설치·실행·보안 시험은 하지 않음
- **다음 질문**: 최소 노출과 워크로드 호환성을 각각 어떤 검사로 확인할 것인가?

[상세 노트에서 구조·접근 기본값·검증 제안 읽기](../LLM-추론-인프라/gvisor-security-boundaries)

### [에이전트 샌드박스의 파일과 네트워크 경계](../LLM-추론-인프라/claude-code-sandboxing)

파일·네트워크 제한과 하위 프로세스의 경계 상속을 살펴본다.

- **수집일**: 2026-10-31 KST
- **읽기 상태**: 읽기 전
- **검증 상태**: 자료 검토 후보이며 직접 실행한 결과는 없음

원문, 요약, 한계와 다음 질문은 [상세 노트](../LLM-추론-인프라/claude-code-sandboxing)에서 읽는다.

## Caution

현재 등록된 항목이 없다.

채택 단계는 직접 검증 근거로 판단한다. 읽기 상태만으로 단계를 바꾸지 않는다. [[TECHNOLOGY-RADAR|운영 기준 보기]]
