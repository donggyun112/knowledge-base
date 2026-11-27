---
title: 기술 레이더 언어와 프레임워크
type: radar-quadrant
radar_quadrant: Languages and frameworks
tags: [technology-radar]
researched: 2026-11-28
---

# 언어와 프레임워크

언어, SDK와 에이전트 런타임 프레임워크.

[[기술-레이더/index|기술 레이더 전체]] · [기법](techniques) · [플랫폼](platforms) · [도구](tools) · [언어와 프레임워크](languages-frameworks)

## Adopt

현재 등록된 항목이 없다.

## Trial

현재 등록된 항목이 없다.

## Assess

### [Pydantic AI Harness](../에이전트-스킬/pydantic-harness-instruction-authority)

운영자 지시와 파일·MCP 데이터의 출처, 로드와 재생의 구분을 살펴볼 자료.

- **수집일**: 2026-11-28 KST
- **읽기 상태**: 읽기 전
- **검증 상태**: 공개 1차 자료 정적 검토. 실행은 하지 않음
- **다음 질문**: 모델 요청에서 지시 역할과 출처를 어떻게 독립 확인할 것인가?

[상세 노트에서 원문과 한계 읽기](../에이전트-스킬/pydantic-harness-instruction-authority)

### [LangGraph tools 스트림](../에이전트-스킬/langgraph-live-tool-events)

도구 이벤트의 생산과 실행 중 소비를 구분하는 프레임워크 변경.

- **수집일**: 2026-11-27 KST
- **읽기 상태**: 읽기 전
- **검증 상태**: 병합 PR·회귀 테스트와 릴리스 이력 정적 검토. 실행·지연 측정은 하지 않음
- **다음 질문**: 실행 중 청크 전달과 종료 후 일괄 전달을 어떻게 구분할 것인가?

원문, 요약, 한계와 다음 질문은 [상세 노트](../에이전트-스킬/langgraph-live-tool-events)에서 읽는다.

### [Univer Worktree와 Compare](../에이전트-스킬/univer-worktree-review)

Office 문서 작업본의 동결, 구조화 diff, 원본 병합과 최종 파일 검사를 구분한다.

- **수집일**: 2026-11-26 KST
- **읽기 상태**: 읽기 전
- **검증 상태**: 공식 문서·고정 CLI 계약·검사 코드 정적 검토이며 병합·변환 실험은 하지 않음

원문, 요약, 한계와 다음 질문은 [상세 노트](../에이전트-스킬/univer-worktree-review)에서 읽는다.

### [A2A Python 클러스터](../에이전트-스킬/a2a-python-cluster-recovery)

출시된 상태 공유와 미병합 장애 복구 제안의 경계를 살펴본다.

- **수집일**: 2026-11-15 KST
- **읽기 상태**: 읽기 전
- **검증 상태**: 공식 릴리즈·PR·이슈 정적 검토이며 SDK 실행·장애 실험은 하지 않음

원문, 요약, 한계와 다음 질문은 [상세 노트](../에이전트-스킬/a2a-python-cluster-recovery)에서 읽는다.

### [txtai](../RAG-검색-문서/txtai-search-workflows)

유사도 후보와 SQL 필터의 결합, 문서 추출 접근 경계와 워크플로 완료 조건을 살펴본다.

- **수집일**: 2026-11-09 KST
- **읽기 상태**: 읽기 전
- **검증 상태**: 공식 자료 정적 검토이며 설치·모델 호출·검색 실험은 하지 않음

원문, 요약, 한계와 다음 질문은 [상세 노트](../RAG-검색-문서/txtai-search-workflows)에서 읽는다.

### [LangGraph의 실행 상태와 장기 메모리](../에이전트-스킬/langgraph-persistence)

체크포인터와 스토어의 수명·스코프 구분을 살펴본다.

- **수집일**: 2026-10-31 KST
- **읽기 상태**: 읽기 전
- **검증 상태**: 자료 검토 후보이며 직접 실행한 결과는 없음

원문, 요약, 한계와 다음 질문은 [상세 노트](../에이전트-스킬/langgraph-persistence)에서 읽는다.

## Caution

현재 등록된 항목이 없다.

채택 단계는 직접 검증 근거로 판단한다. 읽기 상태만으로 단계를 바꾸지 않는다. [[TECHNOLOGY-RADAR|운영 기준 보기]]
