---
title: The New SDLC with Vibe Coding
source: https://www.kaggle.com/whitepaper-the-new-SDLC-with-vibe-coding
type: whitepaper
category: 논문-아티클
tags: [research, vibe-coding, agentic-engineering, context-engineering, harness]
researched: 2026-10-01
---
# The New SDLC with Vibe Coding

> [!summary] 한줄요약
> Google/Kaggle 5일 AI Agents 코스 자료인 이 whitepaper(Addy Osmani, Shubham Saboo, Sokratis Kartakis, 2026년 5월, 51쪽)는 "Generation is solved. Verification, judgment, and direction are the new craft."를 결론으로, vibe coding과 agentic engineering을 이분법이 아닌 스펙트럼(핵심 차이는 검증 방식)으로 보고, 에이전트를 **Agent = Model + Harness**로 정의하며, 개발자의 산출물을 코드가 아니라 "코드를 만드는 시스템(factory model)"로 재정의한다.

> [!info] 읽은 범위와 이전 노트 정정
> Kaggle 페이지는 서론만 보여 주고 본문은 Google Drive에 임베드된 PDF였다. 로그인 없이 공개로 임베드된 파일이라 내려받아 `pypdf`로 51쪽 전부의 텍스트를 추출해 끝까지 읽었다. 이전 노트는 2차 해설(DEV Community)에 의존한 "대체 정보"였고 날짜(6월)와 일부 내용이 달랐다. 표지·헤더에 적힌 날짜는 **May 2026**이다. 그림(Figure 1-9)은 텍스트로 추출되지 않아 캡션만 읽었고, "Agent = Model + Harness" 등식 자체는 그림으로 제시되어 있다(캡션: "Figure 7: Harness Anatomy | Agent = Model + Harness").

## 1. 문제의식·배경

서론은 프로그래밍을 "번역 행위"로 규정한다. 인간 언어로 문제를 이해하고, 추상 수준에서 해결을 설계하고, 기계가 실행할 문법으로 옮긴다. 각 단계에 마찰이 있었고 그 마찰이 붕괴 중이다. 개발자가 how가 아니라 what을 표현하고, 인간은 intent, architecture, judgment를 제공한다. 근거로 제시한 수치는 "2026년 초 기준 전문 개발자의 85%가 AI 코딩 에이전트를 정기적으로 사용, 51%는 매일, 신규 코드의 약 41%가 AI 생성"이다(각주 1, GetPanto와 Index.dev 블로그 인용. 학술 조사가 아닌 2차 통계 사이트다).

진화 경로는 autocomplete → 인라인 함수 제안 → 채팅 기반 구현 → 이제는 저장소를 clone하고 다중 파일 변경을 계획해 샌드박스에서 실행·테스트하고 PR을 올리는 자율 에이전트다. SDLC의 전 단계가 재편되지만 균일하지는 않다. 이 변화에서 문서의 핵심 구분이 나온다.

- **vibe coding**: 개발자가 AI에게 프롬프트하고 돌아오는 것을 그대로 받아들임.
- **agentic engineering**: AI가 "신중히 설계된 제약, 테스트, 피드백 루프의 시스템" 안에서 구현 엔진으로 일하고 인간은 architecture, correctness, quality를 감독.

저자들은 CTO에게 "결제 시스템을 vibe coding한다"고 말하면 경보가 울리는 것이 당연하지만, "인간이 설계한 제약 하에서 AI가 구현하고 테스트 커버리지가 정확성을 보장하는 agentic engineering을 한다"고 말하면 전혀 다른 대화가 된다고 설명한다. 이 문서가 그 대화의 토대를 제공한다는 선언이다. 독자는 엔지니어, 엔지니어링 매니저, 아키텍트, 기술 리더이고 AI/ML 세부 지식은 가정하지 않는다. 특정 도구의 스냅샷이 아니라 도구가 바뀌어도 쓸 수 있는 원칙과 mental model이 목표라고 한다.

## 2. 핵심 논지·구조 (챕터별 상세)

문서 목차는 Introduction → Shift from syntax to intent → The new SDLC → Harness Engineering → Developer's evolving role → Coding agents in practice → Economics → Where to start → Conclusion 순이다.

### 2.1 Agent 복습과 vibe coding 정의 (pp.10-12)

에이전트는 "목표를 인지하고, 단계를 계획하고, 도구로 행동하고, 결과를 관찰하고, 목표 달성이나 정지 조건까지 반복하는 소프트웨어 시스템"이다. 챗봇은 응답하고 다음 프롬프트를 기다리지만 에이전트는 자기 루프를 돈다. 모든 에이전트는 다섯 부분으로 구성된다고 나열한다: Model(추론 엔진), Tools(API, 코드 실행, DB, 다른 에이전트), Memory(상태: 과거 상호작용, 프로젝트 규칙, 세션 간 컨텍스트), Orchestration(루프를 돌리는 코드로 컨텍스트 조립, 도구 디스패치, 결과 수집, 계속 여부 결정), Deployment(호스팅, 신원, observability, 프로덕션 인프라). 이는 2025년 11월 Google의 "Introduction to Agents" 백서를 요약한 것이다. (본문은 이어 "these four parts"라고 쓰는데 다섯 개를 나열해 놓고 넷이라 부르는 사소한 불일치가 있다.)

Vibe coding은 Karpathy가 2025년 2월 게시물에서 "vibes에 완전히 몸을 맡기고 exponentials를 받아들이고 코드가 존재한다는 사실을 잊어라"고 쓴 방식이다. 설명한 사용 모습은 자연어로 요구를 말하고 출력을 받아들이고 에러가 나면 메시지를 프롬프트에 복붙해 고쳐 달라고 하는 것이다. 용어가 바이럴이 되면서 모든 AI 보조 개발을 가리키게 되어 의미가 희석됐고, 2026년 초 Karpathy 본인이 원래 프레임이 너무 좁았다고 인정하며 더 규율 있는 쪽을 가리키는 "agentic engineering"을 도입했다고 서술한다(각주 4, The New Stack와 Karpathy 인용).

### 2.2 스펙트럼 (Table 1, pp.12-15)

세 열로 구분한다: Vibe Coding / Structured AI-Assisted Coding / Agentic Engineering.

| 차원 | Vibe Coding | Structured AI-Assisted | Agentic Engineering |
|---|---|---|---|
| 의도 명세 | 캐주얼 자연어 프롬프트 | 예시·제약을 담은 상세 프롬프트 | 정식 spec, 아키텍처 문서, memory 파일 |
| 검증 | "작동하는 것 같은가?" | 수동 테스트, spot-check | 자동화 테스트 스위트, CI/CD 게이트, LM judges |
| 코드베이스 이해 | 최소, 생성 코드를 읽지 않을 수도 | 핵심 경로 선택적 리뷰 | 아키텍처 포괄 리뷰, 구현 세부는 AI |
| 에러 처리 | 에러 메시지를 AI에 복붙 | 개발자가 근본 원인 진단, AI가 수정 | 정의된 범위 내 에이전트 자가 진단, 아키텍처 이슈는 인간 |
| 적합 범위 | 프로토타입, 스크립트, 개인·해커톤 | 기존 코드베이스 내 기능 | 프로덕션, 팀 규모 개발 |
| 위험 | 높음(일회용 코드엔 허용) | 중간 | 낮음(모든 단계 체계적 검증) |

가장 큰 차이는 **출력이 어떻게 검증되는가**다. Agentic engineering에서는 두 메커니즘이 함께 일한다. **Tests**는 시스템의 결정론적 부분(입력→출력)을 검증하고, **Evals**는 비결정적 부분(에이전트가 올바른 궤적의 단계를 밟았는지, 올바른 도구를 골랐는지, 최종 응답이 품질 기준을 충족하는지)을 검증한다. "테스트는 코드로, eval은 라벨 데이터셋·채점 rubric·LM judge로 검사한다. 둘 다 없으면 프롬프트가 아무리 정교해도 그것은 항상 vibe coding이다." 위험에 비례해 위치를 고르라는 "Applied Tip"도 있다: 주말 프로토타입은 순수 vibe coding, 금융 거래 API는 agentic engineering, 대부분의 일은 그 사이이며 기술은 과업마다 선을 어디에 긋는가다.

### 2.3 Context engineering (pp.15-18)

프롬프트의 영리함보다 제공된 컨텍스트의 질이 AI 생성 코드의 질을 좌우한다는 통찰에서 **context engineering**이 나온다. 6가지 컨텍스트 유형을 든다.

1. Instructions: 에이전트의 역할, 목표, 운영 경계
2. Knowledge: 검색된 문서, 아키텍처 다이어그램, 도메인 데이터
3. Memory: 단기(세션 로그)와 장기(프로젝트가 무엇인가에 대한 영속 상태)
4. Examples: few-shot 행동 시연, 코드베이스 참조 패턴
5. Tools: 호출 가능한 API/스크립트/외부 서비스의 정확한 정의
6. Guardrails: 하드 제약, 형식 규칙, 안전 검증

핵심 설계 결정은 어떤 것을 처음부터 가지고 있고 어떤 것을 온디맨드로 가져올지다. **Static context**는 항상 로드된다: 시스템 지시, 규칙 파일(AGENTS.md, CLAUDE.md, GEMINI.md), 글로벌 메모리, 페르소나. "에이전트가 누구이고 어떻게 행동하는지"를 정의하지만 관련성과 무관하게 모든 상호작용에 토큰이 존재하므로 비싸다. **Dynamic context**는 온디맨드다: 작업 매칭으로 트리거되는 skill 지침, 실행 중 도구 결과, RAG로 가져온 문서, 윈도잉된 세션 이력. 필요할 때만 토큰 비용을 낸다. 너무 많은 static은 토큰을 낭비하고 신호를 희석하며 너무 적으면 중요한 규칙을 잊는다. 따라서 "이 경계를 설정 변경처럼 리뷰하고 버전 관리하는 1급 아키텍처 결정으로 취급하라".

동적 컨텍스트 관리의 가장 강력한 패턴으로 **Agent Skills**를 든다. 구조화되고 이식 가능한 절차 지식 패키지로, 에이전트는 시작 시 가벼운 메타데이터만 보고, 작업이 일치하면 전체 지침을 로드하고, 필요할 때만 깊은 참조 자료를 당겨 온다(progressive disclosure). 결과적으로 에이전트는 가벼운 generalist로 남아 필요 시 specialist로 변신하고 수십 개의 능력을 가져도 활성 스킬 하나의 토큰 비용만 낸다. 스킬이 해결하는 문제는 네 가지다: (a) 과적재 프롬프트로 인한 context rot, (b) LLM의 procedural memory 부재, (c) 다중 에이전트 아키텍처의 운영 부담, (d) 도구·벤더 간 이식성 필요. 더 자세한 내용은 코스 Day 3 백서("Context Engineering: Sessions, Skills & Memory")에 있다고 안내한다.

결론적 문장은 이렇다: "모델은 영리하게 쓴 지시보다 숙련된 인간 개발자가 필요로 할 같은 컨텍스트를 필요로 한다. 질문은 'AI를 속여 좋은 코드를 쓰게 하는 법'이 아니라 '새 팀원이 효과적으로 기여하려면 무엇을 알아야 하는가, 그 지식을 AI가 쓸 수 있는 형태로 어떻게 인코딩하는가'다."

### 2.4 새 SDLC (pp.19-24)

지난 20년간 waterfall에서 Agile, CI, DevOps로 이동하며 피드백 루프가 짧아졌다. AI는 이 사이클을 극적이지만 **불균등하게** 압축한다. 구현은 몇 주에서 몇 시간으로 줄지만 요구사항, 아키텍처, 검증은 "고집스럽게 인간 속도"로 남는다. 결과는 옛 SDLC의 가속판이 아니라 단계 경계가 흐려지고 반복 주기가 주에서 분으로 줄며 개발자의 역할이 주 구현자에서 시스템 설계자·품질 중재자로 바뀐 다른 워크플로다. 저자들은 이 그림이 2026년 중반 기준이며 12개월 안에 달라질 수 있다고 쓴다(spec에서 곧바로 review로 가는 실험 중). 변하지 않는 것은 인간의 judgment, taste, AI 출력을 검증하는 기술이다.

단계별 서술:

- **요구사항·계획**: AI가 사용자 스토리 생성, 사람이 놓치는 엣지 케이스 식별, 자연어에서 API 스키마 생성, 명세에서 인터랙티브 프로토타입 생성을 한다. 요구사항은 팀 간에 넘기는 문서가 아니라 "명세와 초기 구현을 동시에 만드는 인간-AI 대화"가 된다.
- **설계·아키텍처**: "가장 고집스럽게 인간 중심". 일관성 대 가용성, 복잡성 대 유연성, build vs buy 같은 트레이드오프는 비즈니스 맥락, 조직 제약, 장기 전략에 의존해 AI가 완전히 파악할 수 없다. 반면 결정이 내려진 후의 구현(스캐폴딩, 모듈 간 일관 패턴, 컨벤션 준수)에는 탁월. 개발자 역할은 보일러플레이트 작성에서 "그 보일러플레이트가 구현하는 구조적 결정을 내리고 문서화"하는 것으로 이동.
- **구현**: 산업 조사는 25-39% 생산성 향상을 보고한다(각주 7). 그러나 METR 연구는 숙련 개발자가 AI 보조로 특정 과업에서 **19% 더 오래 걸렸다**고 보고했고 주 원인은 검증·디버깅·AI 출력 교정에 쓴 시간이다(본문 각주 번호는 8이나 엔드노트 8은 Osmani의 Factory Model이고 METR은 10번 "Uplift Update, 2026-02-24"로 번호가 어긋난다). "AI는 구현 작업을 없애기보다 쓰기에서 리뷰·안내·검증으로 변환한다."
- **테스트·QA**: 출력 평가(컴파일, 테스트 통과)와 **trajectory 평가**(도구 호출과 중간 추론의 전체 순서)를 모두 해야 한다. "검증 단계를 건너뛴 유창한 출력은 눈에 보이는 오류가 있는 출력보다 더 위험한 실패"이기 때문이다. 에이전트는 엣지 케이스와 property-based 테스트도 생성한다. 더 중요하게 **테스트와 eval이 AI에게 의도를 전달하는 1차 수단**이 된다: 잘 쓴 eval 스위트는 AI에게 "정답"이 무엇인지 알려 준다. 이를 "지속적 품질 flywheel"로 엮으라고 한다: 벤치마크 스위트로 평가 → 실패를 근본 원인별로 클러스터링해 진단 → 원인이 된 프롬프트/도구 최적화 → 회귀 스위트로 수정 검증 → 프로덕션 트래픽에서 새 실패 모드 모니터링. 각 사이클이 복리로 쌓인다.
- **코드 리뷰·배포**: AI가 1차 리뷰어로 버그, 스타일, 보안, 성능 이슈를 사람이 보기 전에 잡는다. 사람 리뷰를 대체하지 않는다. 배포는 AI가 헬스 모니터링, 문제 릴리스 자동 롤백, 변경 규모에 근거한 위험 예측을 한다. PR 양이 에이전트 산출량에 비례할 때 사람 리뷰어가 맞는 변화는 Day 5 백서에서 다룬다고 한다(묶음 요약, 조건부 LGTM, 에이전트 기반 코드리뷰 스킬).
- **유지보수**: "가장 과소평가된 변화". 원저자만 이해하던 레거시를 AI가 탐색·이해·수정하게 하고, 프레임워크 마이그레이션, 폐기 API 갱신, 테스트 현대화처럼 너무 지루하고 위험해서 아무도 하지 않던 일을 체계적으로 한다.

### 2.5 Factory model (pp.24-26)

이 변화들을 묶는 mental model이 factory model이다. 개발자의 주 산출물은 코드가 아니라 **코드를 만드는 시스템**이다: 무엇을 만들지 정의하는 명세와 컨텍스트, 명세를 구현으로 옮기는 에이전트, 정확성을 검증하는 테스트와 품질 게이트, 실패를 에이전트로 되돌려 보내는 피드백 루프, 에이전트를 안전하고 예측 가능한 행동에 가두는 guardrails. 공장 관리자는 위젯을 손으로 조립하지 않고 조립 라인을 설계하고 품질 관리를 확인한다. "성공은 단계별 지시가 아니라 **성공 기준**을 에이전트에게 주고 반복하게 하는 데서 온다." (Figure 6: Developer designs the system → agents produce the code → tests verify the output.)

### 2.6 Harness engineering (pp.26-31)

개발자가 공장 관리자라면 모델은 "공장 바닥의 원동기"이고, 원동기 하나로 차를 만들 수 없듯 모델 주위의 장치가 필요하며 이것이 **Harness**다. 빌더들이 모델을 시스템과 동일시하는 유혹을 경계한다: 새 모델이 나오면 에이전트가 똑똑해지고 오래된 모델이면 나빠진다는 직관은 틀렸고 잘못된 투자로 이어진다. 프롬프트, 도구, 컨텍스트 정책, 훅, 샌드박스, 서브 에이전트, observability가 harness다. **Agent = Model + Harness.** 원시 모델은 harness가 상태, 도구 실행, 피드백 루프, 강제 가능한 제약을 줄 때 비로소 에이전트가 되며, Claude Code, Cursor, Codex, Antigravity, Aider, Cline에서 개발자가 경험하는 행동은 어떤 모델이 아래에 있는지만큼 harness가 하는 일에 지배된다.

Harness 구성(6가지):
1. **Instructions & Rule Files**: AGENTS.md, CLAUDE.md, GEMINI.md, skill 파일, sub-agent 프롬프트
2. **Tools**: 함수, MCP 서버, API와 언제·어떻게 호출할지 모델에게 알려주는 산문
3. **Sandboxes & execution environments**: 코드가 실제 실행되는 곳, 접근 가능·불가능 범위
4. **Orchestration logic**: sub-agent 생성, 모델 라우팅, 전문가 간 핸드오프와 발동 규칙
5. **Guardrails/Hooks**: 도구 호출 전, 파일 편집 후, 커밋 전 같은 수명주기 지점에서 도는 결정론적 코드. "에이전트가 절대 잊으면 안 되지만 자주 잊는 것을 위한 자리"
6. **Observability**: 로그, 트레이스, 평가, 비용·지연 계측. 없으면 에이전트가 잘하는지 조용히 표류하는지 알 수 없다.

"이 표면적은 모델 제공자가 아닌 **팀의 표면적**"이라고 강조한다.

SDLC 단계별 harness의 역할도 정리한다. (1) 요구사항·계획·아키텍처 = harness를 **구성**하는 단계(AGENTS.md 작성, 아키텍처 제약, 도구 접근 정의, 어길 수 없는 규칙). (2) 구현 = harness를 **실행**(샌드박스, 실행 환경, 도구). (3) 테스트·QA = **피드백 루프**(오케스트레이션과 guardrails가 샌드박스 터미널에서 테스트를 돌리고 실패 출력을 모델에 되돌려 재시도시키는 think→act→observe 루프). (4) 리뷰·배포·유지보수 = harness를 **관찰**(훅이 하드코딩된 비밀번호를 푸시하려는 커밋을 차단, observability가 토큰 비용·지연·agent drift를 추적해 에이전트가 왜 그 배포 결정을 했는지 감사).

**효과의 크기**를 보여 주는 벤치마크 두 가지가 가장 구체적인 수치다. Terminal Bench 2.0에서 한 팀이 모델 변경 없이 harness만 바꿔 코딩 에이전트를 Top 30 밖에서 **Top 5**로 올렸고, LangChain의 별도 연구는 고정 모델에서 시스템 프롬프트, 도구, 미들웨어만 조정해 같은 벤치마크 점수를 **13.7점** 올렸다(둘 다 문서가 출처를 각주로 달지 않아 직접 확인하지 못했다). 그리고 "vibe coding에서 agentic engineering으로의 이동은 쓰는 도구가 아니라 harness를 얼마나 의도적으로 구성·적용하는가로 정의된다. 같은 에이전트로 vibe coding도 agentic engineering도 할 수 있다." 에이전트가 틀렸을 때 첫 본능은 모델 탓이지만 "대부분의 에이전트 실패는 정직하게 보면 **설정(configuration) 실패**"이고 원인은 도구 누락, 모호한 규칙, 없는 guardrail, 노이즈로 가득한 컨텍스트 창이다.

### 2.7 개발자의 역할: Conductor와 Orchestrator (pp.31-35)

- **Conductor**: IDE에서 실시간으로 AI 페어 프로그래머와 일한다. 코드가 나타나는 것을 보며 프롬프트와 교정으로 안내하고 세밀한 통제를 유지한다. 복잡한 로직, 까다로운 디버깅, 낯선 코드베이스에 적합. Copilot, Gemini Code Assist, Cursor, Windsurf가 주로 지원. 위험은 모든 키 입력을 지휘하면 AI의 처리량 이득이 제한되는 병목.
- **Orchestrator**: 목표를 정의해 에이전트에 할당하고 결과를 리뷰하되 코드를 한 줄씩 보지 않는다. 에이전트는 백그라운드에서 병렬로 일한다. 버그 수정, 확립된 패턴의 기능 구현, 마이그레이션, 테스트 생성에 적합. Jules, Copilot agent mode, Cursor background agents, Claude Code가 비동기 실행을 지원. 필요한 역량은 **Specification**(모호함 없이 작업을 정의), **Decomposition**(에이전트 실행에 적절한 크기로 분해), **Evaluation**(출력의 품질 기준 충족을 빠르게 판단), **System design**(에이전트를 생산적으로 유지하는 제약·테스트·피드백 루프 설계).

**The 80% problem**: 에이전트는 기능 코드의 약 80%를 빠르게 생성하지만 나머지 20%(엣지 케이스, 에러 처리, 통합 지점, 미묘한 정확성 요구)는 현재 모델에 부족한 깊은 맥락 지식을 요구한다. AI 오류의 성격이 단순 구문 실수에서 **개념적 실패**(비즈니스 로직에 대한 잘못된 가정, 모호한 요구사항에 대한 확인 요청 실패, 엣지 케이스 누락, 장기 유지보수 부담을 만드는 아키텍처 결정)로 진화했고, 코드가 "맞아 보이고" 기본 테스트도 통과할 수 있어 발견이 더 어렵다. 가장 효과적인 개발자는 AI가 잘하는 것(명세가 잘 된 과업의 빠른 구현)에는 AI를 쓰고 자기 주의는 AI가 못하는 것(모호한 요구사항, 아키텍처 트레이드오프, 정확성 검증)에 남긴다. "모든 것을 수용해서가 아니라 전문성을 중요한 곳에 집중해서 빠르다."

### 2.8 Coding agents in practice와 production agent (pp.35-39)

코딩 에이전트는 세 곳에 나타난다. **편집기**(인라인 완성, 채팅 패널: Copilot, Cursor, Windsurf, JetBrains AI), **터미널**(목표를 평이한 언어로 주고 코드베이스 전반에서 일하게 함, 다중 파일 편집, 도구·테스트 실행: Antigravity CLI, Claude Code, Codex CLI, Open Code, Cline), **백그라운드**(클라우드 샌드박스에서 수 시간 자율 실행 후 PR: Jules, Copilot agent mode, Cursor background agents, AlphaEvolve). 올바른 시작점은 "자율성 사다리의 높은 범주"가 아니라 과업이 정한다.

이어 "에이전트를 만드는 일 자체"를 다룬다. 고객지원 봇이나 리서치 어시스턴트는 터미널의 코딩 에이전트로 푸는 과업이 아니라 자체 도구, 메모리, 평가, 배포 인프라가 필요한 제품이다. 같은 터미널 워크플로가 이제 프로덕션 에이전트(영속 메모리, 도구·데이터의 권한 범위, 회귀를 잡는 eval 커버리지, 실제 행동을 추적하는 observability)까지 닿는다. Google의 **Agents CLI**를 예로 든다: 어떤 코딩 에이전트(Claude Code, Codex 등)든 ADK 전체 수명주기(프로젝트 스캐폴딩, 에이전트 코드 작성, 평가, Agent Runtime 배포, observability 연결)를 아우르는 7개 스킬을 부여하는 작은 CLI로, 일회성 설치 후 코딩 에이전트에게 말만 하면 된다.

```bash
# One-time setup
uvx google-agents-cli setup
# Then in your coding agent:
> Build a support agent that answers questions from our docs.
> evaluate it on the FAQ dataset
> Deploy it to Agent Engine
```

이 한 지시 뒤에서 코딩 에이전트가 템플릿에서 프로젝트를 스캐폴딩하고, ADK 코드를 쓰고, evalset을 생성해 실행하고, 배포하고, 보고한다. 직접 운전하려면 `agents-cli create / playground / eval / deploy` 명령이 있다. 다중 에이전트는 ADK의 그래프 기반 워크플로, 공유 세션 상태, LLM 주도 위임, MCP(도구), A2A(에이전트 간 위임)로 조합하며, Anthropic의 2026년 초 실험(에이전트 팀이 2주간 Rust로 동작하는 C 컴파일러를 만들고 인간은 방향 설정과 출력 리뷰만 함)을 병목이 "코드 작성"에서 "무엇을 해야 하는지 명세하고 에이전트가 했는지 검증하는 것"으로 이동했다는 예로 든다. 프로덕션 규모의 spec-driven 개발, 구조적 리뷰, guardrails, sandboxing, zero-trust 개발은 Day 5 백서에 있다.

### 2.9 경제학: CapEx/OpEx (pp.39-42)

속도가 아니라 **TCO**가 리더에게 더 중요한 지표라고 말하며, AI 시대의 OpEx는 token economy가 좌우한다고 한다.

- **Vibe coding = 낮은 CapEx, 높은 OpEx**. 구독료와 몇 번의 프롬프트로 시작하므로 CapEx는 거의 0. 그러나 (1) **Token burn rate**: 구조 없는 큰 파일을 컨텍스트에 쏟고 검증되지 않은 실수를 모델에게 반복해서 고치게 하는 비싼 "프롬프팅 루프"로 첫 시도 성공률이 낮다. (2) **Maintenance tax**: 6개월 뒤 버그가 나면 비구조적 "스파게티" AI 코드를 사람이 며칠씩 역공학. (3) **Security remediation**: 자동 평가 harness가 없으면 코드의 빠른 생성이 취약점의 빠른 생성으로 이어지고, 프로덕션에서 고치는 비용이 설계 단계에서 잡는 비용보다 기하급수적으로 높다.
- **Agentic engineering = 높은 CapEx, 낮은 OpEx**. API 스키마 설계, 결정론적 테스트 스위트, 무엇보다 에이전트 컨텍스트 구조화에 선투자한다. 이후 기능을 출시·유지하는 한계 비용이 급감한다.
- **Context engineering은 재무 레버**: 10만 토큰 저장소 전체를 매 프롬프트에 넣는 것은 규모에서 재무적으로 성립하지 않는다. 정밀한 AGENTS.md와 아키텍처 guardrails 같은 밀도 높은 신호를 주면 첫 시도 성공률이 올라 시행착오 루프를 피한다. 동적 컨텍스트(skills, MCP 같은 tool calling)는 Day 3 백서가 다룬다.
- **Intelligent model routing**: vibe coding은 오타 수정이나 기본 단위 테스트 생성에도 프런티어 모델 가격을 낸다. 잘 설계된 factory는 복잡한 과업(요구사항, 아키텍처, 초기 구현)에 큰 모델을, 결정론적·저복잡도 과업(테스트 생성, 코드 리뷰, CI/CD 모니터링)에는 더 작고 빠르고 싼 모델을 자동 라우팅한다.

### 2.10 시작하기와 결론 (pp.43-48)

**개인 개발자** 6가지: (1) 프로젝트용 AGENTS.md를 만든다. 10줄(스택, 컨벤션, 하드 룰, 워크플로)로 시작하고 에이전트가 해서는 안 될 짓을 할 때마다 규칙을 추가. (2) Agents CLI 같은 스킬 묶음을 설치. (3) 반복 워크플로 하나를 골라 첫 에이전트로 만들기. (4) **코드 생성 전에 테스트와 eval을 쓴다**: 이 둘이 AI와의 계약이며 어떤 자연어 프롬프트보다 정확히 의도를 전한다. (5) 출시될 코드는 모든 줄을 리뷰: 영리해 보이는 것을 의심, import가 실제 패키지인지 확인, 에러 처리가 현실적 실패를 덮는지 확인. (6) 개발자 기술(디버깅, 시스템 설계, 성능·정확성 직관)을 유지.

**엔지니어링 리더** 5가지: (1) context engineering을 1급 실무로, AGENTS.md/시스템 프롬프트/eval 스위트/스킬 라이브러리를 코드처럼 PR 리뷰하고 버전 관리하고 담당자 지정. (2) **데모가 아닌 eval에서 기준을 세운다**: 데모는 한 번 성공을 보이고 eval은 신뢰할 만한 성공을 보인다. rubric이 불명확한 eval은 아무것도 재지 않는다. task success, tool use quality, trajectory compliance, hallucination, response quality를 정의하고 공유 워크플로에 출시하는 에이전트에 eval 커버리지를 서비스 배포의 테스트 커버리지처럼 게이트로. (3) AI 생성 코드 리뷰를 재설계: 같거나 더 큰 정밀 검토, 환각 의존성, 부족한 에러 처리, 한눈에 맞아 보이는 정확성 간극. (4) 프로토타입과 프로덕션을 팀 규범에서 구분(경계가 흐리면 "프로토타입이 우연히 출시된다"). (5) harness 구성요소를 공유 자산으로.

**조직** 5가지: (1) AI 보조 개발을 생산성 기능이 아니라 엔지니어링 투자로 취급(eval·observability·아키텍처 표준 없는 롤아웃은 "품질 없는 속도"로 기술 부채가 갚는 속도보다 빨리 쌓인다). (2) 규모 전에 프로덕션 기반(CI의 trajectory·final-response eval, 모든 에이전트 실행의 trace, 에이전트별 권한 범위, 생성 코드 실패 모드에 맞춘 보안 리뷰). (3) 도구·에이전트 간 통신의 개방 표준(MCP, A2A). (4) 인간-에이전트 하이브리드 팀 계획, 에이전트를 "도구가 아닌 참여자"로. (5) 채용과 성장을 구현이 아니라 판단 중심으로.

결론의 **세 가지 지속 원칙**: (1) **Structure scales, vibes don't.** "It seems to work"와 "모든 조건에서 올바르게 작동한다" 사이의 간극에 프로덕션 장애, 보안 취약점, 유지보수 악몽이 산다. (2) **AI amplifies your engineering culture.** 강한 테스트 관행, 명확한 아키텍처 표준, 건강한 코드 리뷰를 가진 조직이 훨씬 더 큰 가치를 얻는다. AI는 강점과 약점을 모두 증폭한다. (3) **The human role is evolving, not diminishing.** 마지막 문장: "Generation is solved. Verification, judgment, and direction are the new craft."

## 3. 구체적 예시·수치 요약 (문서 안에서 확인한 것만)

- 전문 개발자의 85%가 AI 코딩 에이전트를 정기 사용, 51% 매일, 신규 코드의 ~41%가 AI 생성(2026 초, 각주 1: 블로그 통계)
- 산업 조사의 생산성 향상 25-39%(각주 7), Deloitte 인용 30-35%(각주 9; 본문에서 직접 인용 위치는 확인 못함)
- METR 연구: 숙련 개발자가 일부 과업에서 AI 사용 시 19% 더 걸림(METR "Uplift Update", 2026-02-24)
- Terminal Bench 2.0: harness만 바꿔 Top 30 밖 → Top 5; LangChain 연구 +13.7점
- Agents CLI: 7개 스킬; `agents-cli create/playground/eval/deploy`
- 정적 컨텍스트 예: 100,000토큰 저장소 전체를 프롬프트에 넣는 것은 규모에서 비현실적
- 이 문서는 51쪽이고 PDF 본문에 "Day 1"이라는 표기는 없다(코스 내 순서는 확인 못함). 같은 코스의 후속 백서로 Day 3(Context Engineering: Sessions, Skills & Memory)과 Day 5(Spec-Driven Production Grade Development in the Age of Vibe Coding)가 후속

## 4. 한계·비판적 평가

1. **연구가 아니라 프레임워크 문서다.** 방법론, 통제 실험, 동료 심사가 없다. 수치는 대부분 2차 출처(블로그, 업계 보고)를 인용하고, 핵심 harness 효과 수치(Top 30 → Top 5, +13.7점)는 각주 없이 서술되어 검증 불가다.
2. **통계의 내적 긴장.** 서론은 85% 사용과 41% AI 코드를 앞세우는데 구현 절은 25-39% 향상과 19% 둔화(METR)를 나란히 둔다. 문서는 "그림은 헤드라인보다 복잡하다"고 인정하지만 어느 쪽이 지배적인지 결론짓지 않는다. Google/Kaggle 코스 자료이므로 Google 제품(ADK, Agents CLI, Agent Runtime, Jules, Antigravity)에 대한 편향 가능성을 감안해야 한다. 이는 내 평가다.
3. **편집상 불일치**: "five parts"를 나열하고 "four parts"라 부름; 결론의 "ambient, workflow, and autonomous agents 분류법"은 본문에 대응 절이 없음(초안 잔재로 보임); 각주 번호 어긋남(METR 인용이 엔드노트 8로 표시되나 실제는 10, Anthropic C 컴파일러 실험이 Lawfare 보안 기사를 각주로 달고 있음). 인용을 따라가 검증하려는 독자에게는 마찰이다.
4. **"모든 줄을 리뷰하라"는 이상론.** 개인 개발자 5번은 출시될 모든 줄의 리뷰를 권하지만 PR 양이 에이전트 산출량에 비례해 늘면 병목이 된다. 문서 스스로 Day 5에서 이 문제(묶음 요약, 조건부 LGTM)를 다룬다고 미룬다. 위험 기반 샘플링이 현실적이라는 2차 해설의 지적은 합리적이지만 이 문서 본문에는 없다.
5. **"대부분의 실패는 설정 실패"라는 주장은 가설이다.** harness 효과의 증거는 벤치마크 두 건이고, 반대로 모델 능력 한계로 인한 실패의 비중은 논하지 않는다. 벤치마크 최적화(harness engineering에 의한 오버피팅)와 실제 일반화의 차이도 다루지 않는다.
6. **Factory model의 위험 은폐.** "성공 기준만 주고 반복하게 하라"는 reward hacking(테스트만 통과하는 코드)을 낳을 수 있다. 문서는 eval의 rubric이 불명확하면 아무것도 재지 못한다고 말하지만 에이전트가 테스트를 우회하는 사례나 평가자 자체의 신뢰 문제는 다루지 않는다. 평가자 신뢰는 [[algorithmically-establishing-trust-in-evaluators]]가 다루는 영역이다.
7. **경제학 절은 정성적.** CapEx/OpEx 틀은 유용하지만 실제 비용 수치나 모델 라우팅의 이득 측정이 없다. 이에 대한 정량적 사례는 [[llm-agent-skill-memory-without-finetuning]]에서 소개하는 주입 토큰 계측 연구(TCA: 주입이 청구액의 약 12%)와 대조해 읽을 만하다.

## 6. 확인하지 못한 것

- Figure 1-9와 Snippet 이미지의 시각 내용(텍스트로 추출 불가, 캡션만 확인).
- Terminal Bench 2.0 Top 5 사례와 LangChain 13.7점 연구의 원 출처 및 조건.
- 각주 인용 원문(GetPanto, METR, Osmani 블로그 등)은 따라가지 않았다. METR 수치는 문서가 인용한 대로만 적었다.
- 2차 해설(DEV Community)이 제기한 다른 조사(JetBrains, DX)와의 통계 불일치 주장은 이번에 재검증하지 않았다.

## 관련 노트
[[context-fails-first-agent-reliability]] [[aces-agentic-continuous-evaluation-of-skills]] [[wikiskill]] [[llm-agent-skill-memory-without-finetuning]] [[jev-as-a-judge-agent-evals]] [[karpathy-llm-wiki]] [[algorithmically-establishing-trust-in-evaluators]]

## 출처
모두 2026-10-01에 직접 열람.
- Addy Osmani, Shubham Saboo, Sokratis Kartakis, "The New SDLC with Vibe Coding: From ad-hoc prompting to Agentic Engineering", Google/Kaggle whitepaper, May 2026, 51쪽 (PDF 전문 추출): https://www.kaggle.com/whitepaper-the-new-SDLC-with-vibe-coding (본문 PDF는 페이지에 임베드된 Google Drive 파일 https://drive.google.com/file/d/1IR7CddF_2FyQo_PdfBNTaEA50EGiVt2r/preview)
- 이전 판의 2차 자료(참고용으로만 언급, 이번에 재열람하지 않음): https://dev.to/jahanzaibai/googles-vibe-coding-whitepaper-explained-in-plain-english-2ig2
