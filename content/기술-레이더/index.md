---
title: 기술 레이더
type: radar
tags: [technology-radar]
researched: 2026-11-05
---

# 기술 레이더

새로 수집한 기술 자료와 검토 중인 선택지를 살펴보는 공간이다. **영역별로 찾아보거나 채택 단계별로 비교하고, 상세 내용은 기존 주제별 글에서 읽는다.** 읽기 상태와 채택 판단은 따로 관리한다.

[[TECHNOLOGY-RADAR|운영 기준과 단계 정의]] · [지식베이스 홈](../)

## 영역별 탐색

| 영역 | 다루는 질문 | 현재 등록 |
| --- | --- | --- |
| [기법](techniques) | 어떤 평가·설계·복구 방식을 쓸 것인가? | ParetoSaddler, 멱등 API 재시도, MCP 보안 경계, Decision Gate, 임베딩 모델 병합 |
| [플랫폼](platforms) | 어떤 실행·격리·배포 환경을 쓸 것인가? | 샌드박스의 파일과 네트워크 경계 |
| [도구](tools) | 어떤 개발·평가·운영 도구를 쓸 것인가? | LLM Architecture Gallery, DSH Superagent, stack-diagram, Agent Desktop, Lightpanda |
| [언어와 프레임워크](languages-frameworks) | 어떤 언어·SDK·런타임을 쓸 것인가? | LangGraph의 실행 상태와 장기 메모리 |

빈 영역은 검토할 자료가 생기면 채운다. 기존 자료를 읽거나 채택한 것으로 추정해 일괄 등록하지 않는다.

## 채택 단계별 탐색

[Adopt](#adopt) · [Trial](#trial) · [Assess](#assess) · [Caution](#caution)

### Adopt

직접 검증한 조건과 적용 근거가 있는 선택. 현재 등록된 항목은 없다.

### Trial

성공 기준과 되돌리기 조건을 정하고 제한적으로 실험 중인 선택. 현재 등록된 항목은 없다.

### Assess

읽고 조사하거나 실험 후보로 검토하는 단계다. 아래 항목들은 아직 직접 검증하지 않았다.

| 자료 | 영역 | 읽기 상태 | 다음 질문 |
| --- | --- | --- | --- |
| [LLM Architecture Gallery](../LLM-추론-인프라/llm-architecture-gallery) | 도구 | 읽기 전 | 가중치·KV 추정과 실제 메모리의 차이를 어떻게 설명할 것인가? |
| [ParetoSaddler](../논문-아티클/paretosaddler) | 기법 | 읽기 전 | 탐색 비용까지 포함하면 어느 실행량에서 이득인가? |
| [DSH Superagent](../에이전트-스킬/dsh-superagent-prototype) | 도구 | 읽기 전 | 상태 저장과 외부 효과 사이의 중단·재시도를 어떻게 검증할 것인가? |
| [멱등 API 재시도](../에이전트-스킬/idempotent-api-retries) | 기법 | 읽기 전 | 재시도할 작업의 정체성과 외부 효과의 성공 증거를 어디에 보관할 것인가? |
| [stack-diagram](../에이전트-스킬/stack-diagram) | 도구 | 읽기 전 | 로고 출처와 추론된 토폴로지를 어떻게 검증할 것인가? |
| [MCP 보안 경계](../에이전트-스킬/mcp-authorization-boundaries) | 기법 | 읽기 전 | 요청 주체·위임 동의·세션 소유자를 어느 계층에서 검증할 것인가? |
| [Decision Gate / JevAct](../논문-아티클/decision-gate-jevact) | 기법 | 읽기 전 | 재수정과 강제 권한 검사를 어떻게 분리하고 시뮬레이터 의존성을 검증할 것인가? |
| [임베딩 모델 병합](../RAG-검색-문서/embedding-model-merging) | 기법 | 읽기 전 | 병합 호환성과 도메인별 검색 품질을 어떻게 따로 검증할 것인가? |
| [Lightpanda](../에이전트-스킬/lightpanda-browser) | 도구 | 읽기 전 | 목표 사이트의 호환성과 HTTP 오류·세션 상태를 어떻게 검증할 것인가? |
| [Agent Desktop](../에이전트-스킬/agent-desktop) | 도구 | 읽기 전 | 오래된 ref와 전달 불확실성을 하네스에서 어떻게 처리할 것인가? |
| [LangGraph의 실행 상태와 장기 메모리](../에이전트-스킬/langgraph-persistence) | 언어와 프레임워크 | 읽기 전 | 승인 대기 뒤 재시작할 때 어떤 상태를 복구할 것인가? |
| [에이전트 샌드박스의 파일과 네트워크 경계](../LLM-추론-인프라/claude-code-sandboxing) | 플랫폼 | 읽기 전 | 하위 프로세스에도 파일·네트워크 경계가 이어지는가? |

### Caution

구체적 위험이나 요구 충돌 때문에 신규 적용을 보류하는 선택. 현재 등록된 항목은 없다.

## 최근 수집

수집일은 KST 기준이며 발행일과 다르다. 신규 자료는 먼저 Assess에 놓고, 읽었다는 확인 없이 읽기 상태를 바꾸지 않는다.

| 수집일 | 자료 | 살펴볼 점 |
| --- | --- | --- |
| 2026-11-05 | [LLM Architecture Gallery](../LLM-추론-인프라/llm-architecture-gallery) | 모델 구조·전체/활성 파라미터·KV 캐시 추정의 한계 |
| 2026-11-04 | [ParetoSaddler](../논문-아티클/paretosaddler) | 중간 후보 승격·최종 배포 선택·품질과 총비용의 분리 |
| 2026-11-04 | [DSH Superagent](../에이전트-스킬/dsh-superagent-prototype) | Ticket/Assignment·트랜잭션·영속 Effects·복구 경계 |
| 2026-11-03 | [멱등 API 재시도](../에이전트-스킬/idempotent-api-retries) | 요청 의도·원자성·의미상 동등한 응답·지연 요청 계약 |
| 2026-11-02 | [stack-diagram](../에이전트-스킬/stack-diagram) | HTML 단일 원본·좌표 설계·로고와 렌더링 신뢰 경계 |
| 2026-11-02 | [MCP 보안 경계](../에이전트-스킬/mcp-authorization-boundaries) | 토큰 대상·클라이언트별 동의·세션과 인증의 분리 |
| 2026-11-01 | [Decision Gate / JevAct](../논문-아티클/decision-gate-jevact) | 실행 전 검증·예산 소진 시 무검사 실행·혼합 평가 결과 |
| 2026-11-01 | [임베딩 모델 병합](../RAG-검색-문서/embedding-model-merging) | 공통 기반·입력 규칙·검색 회귀 평가 |
| 2026-11-01 | [Lightpanda](../에이전트-스킬/lightpanda-browser) | DOM·JavaScript 자동화와 렌더링·세션·성능 해석의 경계 |
| 2026-11-01 | [Agent Desktop](../에이전트-스킬/agent-desktop) | 접근성 트리 기반 대상 식별과 전달 증거에 따른 재시도 |
| 2026-10-31 | [LangGraph Persistence](../에이전트-스킬/langgraph-persistence) | 스레드 실행 상태와 스레드 간 장기 지식의 분리 |
| 2026-10-31 | [Claude Code sandboxing](../LLM-추론-인프라/claude-code-sandboxing) | 운영체제 수준의 파일·네트워크 경계와 자격 증명 분리 |

## 결정 이력

- **2026-11-05**: LLM Architecture Gallery를 Tools / Assess로 등록했다. 제작자 페이지·계산식 설명 검토이며 추론 실험은 하지 않았다. 읽기 상태는 읽기 전이다.

- **2026-11-04**: ParetoSaddler 논문 v1을 Techniques / Assess로 등록했다. 본문·부록 검토이며 최적화·재현 실험은 하지 않았다. 읽기 상태는 읽기 전이다.

- **2026-11-04**: DSH Superagent 공개 구현을 Tools / Assess로 등록했다. 정적 검토이며 설치·실행은 하지 않았다. 읽기 상태는 읽기 전이다.

- **2026-11-03**: AWS Builders’ Library의 멱등 API 설계를 Techniques / Assess로 등록했다. 본문 검토이며 API 호출·장애 실험은 하지 않았다. 사용자 읽기 상태는 읽기 전이다.

- **2026-11-02**: 요청받은 stack-diagram을 Tools / Assess로 등록했다. 고정 커밋의 문서·구현 검토이며 설치·생성·렌더링은 하지 않았다. 사용자 읽기 상태는 읽기 전이다.

- **2026-11-02**: MCP 공식 보안 가이드를 Techniques / Assess로 등록했다. 본문 검토이며 서버 설치·보안 실험은 하지 않았다. 사용자 읽기 상태는 읽기 전이다.

- **2026-11-01**: 요청받은 Decision Gate 논문 v1을 Techniques / Assess로 등록했다. 본문·부록 검토이며 실행·재현은 하지 않았다. 사용자 읽기 상태는 읽기 전이다.

- **2026-11-01**: 임베딩 모델 병합을 Techniques / Assess로 등록했다. 공식 문서와 예제 검토이며 병합·성능 실험은 하지 않았다. 사용자 읽기 상태는 읽기 전이다.

- **2026-11-01**: Lightpanda를 Tools / Assess로 등록했다. 공식 문서와 벤치마크 자료 검토이며 직접 실행하지 않았다. 사용자 읽기 상태는 읽기 전이다.

- **2026-11-01**: Agent Desktop을 Tools / Assess로 등록했다. 공식 문서와 구현 검토이며 직접 실행하지 않았다. 사용자 읽기 상태는 읽기 전이다.

- **2026-10-31**: 자료 두 건을 Assess로 등록했다. 읽기 상태는 모두 읽기 전이다. 기술 채택 결정은 아직 없다.

항목의 단계가 바뀌면 날짜, 적용 조건, 검증 근거와 남은 위험을 이력으로 남긴다. 상세 실험과 메모는 연결된 원래 글에 보존한다.
