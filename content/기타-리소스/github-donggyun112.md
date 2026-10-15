---
title: GitHub donggyun112 공개 레포 개요
source: https://github.com/donggyun112
type: repo
category: 기타-리소스
tags: [research, github, llm-agent, memory]
researched: 2026-10-01
---
# GitHub donggyun112 공개 레포 개요
> [!summary] 한줄요약
> 공개 레포 41개(직접 만든 것 약 30개) 중 최근 활동은 모두 "LLM agent를 장시간·위험한 환경에서 믿고 돌리기 위한 인프라"에 집중되어 있다: 연상 기억(keymem), 정적분석 MCP(codecanvas), 크래시 후 부작용 중복 방지(semora, effect-ledger), 코드를 사람이 직접 치게 하는 편집기 확장(retype), microVM 샌드박스(msbd). 각 레포의 README와 구조를 clone해 확인했고, 개인 식별 정보(프로필 소개·소속·연락처)는 적지 않는다.

## 무엇인가
GitHub 공개 계정 `donggyun112`의 레포지터리 개요다. GitHub API로 전체 목록(공개 41개, 그중 포크 아닌 것 30개)을 받아 최근 푸시 순으로 정리했고, 핵심 8개 레포(keymem, semora, msbd, codecanvas, nexora, autonomous-agent, effect-ledger, retype)는 shallow clone으로 README, 디렉터리 구조, 벤치마크 문서, CHANGELOG를 직접 읽었다. 기존 노트는 pinned 레포 6개의 한 줄 설명만 있었고 codecanvas/nexora는 "설명 미확인"이었으며 semora를 "LangGraph 기반"이라고 적었는데, 이번에 확인한 결과 semora는 0.3부터 Pydantic AI 기반으로 바뀌었다(아래).

활동 시점 기준(조회 2026-10-01): 최근 푸시가 keymem 09-29, semora 09-28, effect-ledger 09-09, codecanvas 09-12, retype 09-04, nexora 08-30, msbd 08-27로 매우 활발하다. star는 대부분 0~4개로 아직 작은 프로젝트다.

## 핵심 내용

### 1. keymem — 연상 기반 agent 메모리 (TypeScript, MIT, npm 최신 0.32.2)
- 슬로건: "The associative memory layer for LLM agents — recall by association, not just similarity." 벡터 저장소는 질의와 비슷하게 들리는 것만 찾고, 질의와 연결된 것은 놓친다는 문제의식. 예: "Newton" 검색이 Newton → apple → fruit → strawberry 경로로 "사용자가 딸기를 좋아한다"에 도달하는 것은 임베딩 거리가 아니라 key graph 경로 때문.
- 구조: Key Space(개념)와 Value Space(기억)를 분리한 N:M 그래프. 한 기억이 여러 key로, 한 key가 여러 기억으로 연결. `recall`은 key 클러스터와 가장 강한 key 아래 Top-1 기억 1개만 자동으로 컨텍스트에 넣고(`matched_key`, `validity`, `connected_keys` 포함), 이후 홉은 에이전트가 `read_key`/`read_memory`로 의도적으로 진행한다. 데모에서 세 번의 recall이 약 2.4k 토큰을 쓰는 반면 같은 12-메모리 허브를 자동 확장하면 약 8k 토큰이라고 서술.
- 기능: key 유형(concept는 유사도, name/proper_noun은 정확 일치), IDF 기반 다국어 key 병합(파이썬 ↔ Python), Hebbian 링크 학습(실제로 걸어간 경로 강화), 신선도/validity(4개 decay 프로파일, `confirm_memory`는 명시적 증거 있을 때만), 한 단계 버전 관리(correct 시 직전 값 보존), cross-encoder reranker(핵심 recall 경로, 첫 사용 시 모델 추가 다운로드), 로컬 임베딩 bge-m3(약 570MB 자동 다운로드) 또는 OpenAI 임베딩, UserPromptSubmit 훅으로 매 프롬프트마다 관련 기억을 passive로 주입.
- 설치: MCP 서버(CLI)이며 라이브러리가 아니다("npm i keymem"으로 의존성 추가 금지, `npx -y keymem` 권장). Claude Code 플러그인 마켓플레이스와 Codex 플러그인 지원. 소스 구성: autokey, daemon, decay, embedding, inject, memoryGraph, recallView, reranker, retag, server, shim, vectorStore 등.
- 벤치마크(BENCHMARKS.md): 리더보드가 아닌 ablation. HotpotQA bridge 질문에서 "독립 서브에이전트가 만든 blind key" 조건에서 두 gold 문단을 모두 가져오는 비율이 graph 63% vs flat semantic 53% vs lexical 35%(+10pp/+28pp). 저자가 직접 만든 key 조건에서는 78% vs 60% vs 49%로 부풀려졌다고 스스로 명시하고 blind 수치를 신뢰하라고 적었다. 비교(comparison) 질문에서는 오히려 약간 불리하고, 검색 recall이지 최종 정답 정확도가 아니며 mem0/Zep 등과의 head-to-head SOTA 주장이 아님을 분명히 한다. read 경로를 O(그래프)에서 O(1)로 바꿔 read_memory p50 약 45ms → 약 0.01ms(500 메모리). 자체 14메모리 합성 persona 그래프에서 assoc2 reach@10은 BM25 33%, flat 50%, graph 83%였으나, 2026-09-06 재측정(v0.27.2, reranker 기본 켬)에서는 graph 67%, reranker 끔은 50%로 내려가 변동이 있음을 기록했다.

### 2. codecanvas — Python 호출 그래프/제어 흐름 MCP (Python, MIT, PyPI `codecanvas-mcp`)
- "Understand an unfamiliar Python system before spending thousands of tokens reading it file by file." 로컬 정적분석 MCP 서버로 branches, callers, callees, side effects, change impact에 대한 인용 가능한 압축 답변을 준다. Python 3.10+, Python 전용.
- 도구: `logic_flow`(해석·분기·결과·하위 호출·효과·위치 일괄), `who_calls`, `call_tree`, `what_does`, `function_flow`, `reaching_conditions`, `list_entrypoints`, `analyze_impact`, `verify_claim`, `validate_state_schema`, `simulate_state_transition` 등. 응답에 `evidence_grade`(예: inferred)와 `safe_to_summarize: false`, `response_guidance`("추론된 호출 간선을 무조건적 주장으로 바꾸지 말 것")를 넣어 에이전트가 과신하지 않도록 한 설계가 특징.
- 벤치마크: Google ADK, LangGraph, FastAPI의 고정 리비전. Apple M4 Pro 기준 cold 분석 4.38~61.62초, warm `find_symbols` 중앙 지연 48.264~293.778ms. 54세션 통제 실험에서 기존 검색 도구는 동일하게 두고 `logic_flow` 하나만 추가했을 때 총 토큰 중앙값 22.95% 감소(3회 반복), uncached 토큰은 0.78% 증가. 정답은 아직 블라인드 채점 전이고 과제·루브릭이 독립적으로 작성·감사되지 않았다고 README가 직접 한계를 밝힌다.
- Claude Code/Codex 플러그인 마켓플레이스 제공.

### 3. semora — 크래시 후 부작용 복구 런타임 (Python, MIT, 0.3)
- 정의: "Fail-closed effect recovery and worker coordination for Pydantic AI agents." 예전 설명(LangGraph 기반 durable multi-agent runtime)과 달리 0.3부터는 Pydantic AI가 에이전트 루프·메시지·모델·도구를 소유하고 Semora는 그 위에 effect ledger, worker lease/fencing, durable approval suspension, 재개 시 정책 재검증을 얹는다. LangChain 구현은 폐기(커밋 156e4b1에 남음). 0.3.0은 breaking release.
- 핵심 계약: 시작했지만 결과가 커밋되지 않은 도구 호출은 `Indeterminate`로 남고 호스트가 `resolve_effect()`로 해소할 때까지 재실행하지 않는다. `ConfirmedEffect`는 공급자 확인 결과를 커밋하고 `RetryEffect`는 버전에 묶인 단발 재시도를 허용. 사람의 승인(`Suspend`)은 재개 시 새 정책 결정의 입력일 뿐 자동 허용이 아니다(`on_resume`이 답변과 두 정책 버전 라벨을 받음). 거절은 해당 호출의 기록 결과로 라운드를 끝내 모델이 같은 질문을 무한 반복하지 않게 한다.
- 한계를 명시: 도구 호출 키는 한 run 범위이며 run·브랜치를 넘는 중복 제거는 호스트가 안정 키를 줘야 하고, lease만으로는 외부 API 호출을 멈출 수 없다. 패키지: `semora`, `semora-store`, `semora-store-pg`. 데모: Cloud Run의 operator console(`semora-console` 레포, 결제는 시뮬레이션이며 실제 결제 공급자를 보증하지 않음).

### 4. effect-ledger — 부작용 장부 (Python, MIT)
- 카드 결제 호출 후 프로세스가 죽어 응답을 못 받으면 LangGraph가 체크포인트에서 재개하며 도구를 다시 불러 이중 결제가 일어날 수 있다는 문제. 도구를 호출하기 전에 operation 기록(claim)을 먼저 커밋하고, 결과를 모르면 `unresolved`로 두며, 재개 시 이를 발견해 멈춘다. 이후 호스트가 공급자에게 확인해 `complete` 또는 `retry`를 기록. SQLite/Postgres 저장소, LangChain/LangGraph/MCP 어댑터, 코어는 런타임 의존성 없음(Python 3.10+). "공급자 쪽 idempotency는 여전히 공급자의 몫이며 장부는 이미 일어났을 수 있는 일을 기록하고 검증 없는 재시도를 막을 뿐"이라고 범위를 정직하게 한정한다. semora의 아이디어를 LangChain 계열에 독립 패키지화한 것으로 보인다(README 비교 문장은 확인하지 못했고 개념적 유사성에 근거한 해석).

### 5. nexora — TypeScript multi-agent 런타임 (MIT, 2026-08-30부터 maintenance mode)
- "Multi-agent runtime for TypeScript. Coordinated agents, contained authority, OS-level isolation." 에이전트가 capability로 위임(delegate), 막히면 사람에게 질문(handraise), 위임된 에이전트의 권한은 호출자 권한의 부분집합으로만 가능한 authority attenuation, 승인 게이트(skip/ask/block/deny), 멀티테넌트(옵트인), OTel 트레이싱, 체크포인트/재개, 예산 추적, SKILL.md 자기 학습 등을 20개 패키지(npm 스코프 패키지)로 제공. 구조: Adapter → Gateway → Transport → Bootstrap → ContextLoader → AgentRunner(ReAct) → Tools/Skills/Store.
- README 상단 공지: 기능 동결, 보안·치명 버그만 수정. 활발한 개발은 Semora(Python)로 이전, Semora는 Nexora의 drop-in 대체가 아님. 샌드박스 원격 프로토콜(`sandbox-remote`, `sandbox-server` 패키지)은 msbd가 구현하는 쪽이다.

### 6. msbd — microVM sandbox 서버 (Go)
- Nexora의 provider-neutral 원격 샌드박스 HTTP 프로토콜 구현: 세션 생성/재부착/삭제, exec, 워크스페이스 파일시스템(읽기/쓰기/stat/readdir), tar 기반 persist/hydrate 스냅샷. Bearer 토큰 인증(`MSBD_TOKEN`), 오류 형식 `{code, message, retryable?}`.
- Firecracker 백엔드(선택적 jailer chroot), OCI 이미지를 부팅 가능한 ext4로 변환(`msbd image import python:3.12`, `msb-guest-agent`를 `/init`으로 주입), 첫 실행 시 커널(Firecracker CI 버킷, sha256 고정)과 기본 rootfs(릴리스 자산, 체크섬 검증)를 내려받아 캐시. 요구: KVM이 있는 Linux, `firecracker`, `mke2fs`, jailer 사용 시 root. 개발용 in-process 백엔드는 격리가 없으므로 신뢰할 수 없는 코드에는 금지.
- 알려진 한계 명시: 임포트된 이미지는 임포트한 사용자 소유, 게스트 프로세스는 VM 안에서 root, jailer 경로에서 공유 자산이 0644. 프로토콜 정합성은 nexora-python의 `RemoteSandboxClient`로 검증한다고 서술. 내부 패키지: api, assets, guest, image, session, vm, wire.

### 7. autonomous-agent — 자기 진화형 자율 에이전트 (TypeScript)
- Docker 컨테이너에서 계속 도는 에이전트: WAKE(행동) → REFLECT(검토) → SLEEP(기억 정리)를 반복. 수면 압력은 Borbely의 two-process 모델(항상성 + 일주기)을 따르고, WAKE는 REFLECT를 거쳐야만 SLEEP 가능(REFLECT 최소 5턴, SLEEP 최소 3턴). "Body vs Shell": 정체성·기억·일지·위키·프롬프트(`data/`)는 영속, 코드·도구·Dockerfile(`src/`와 이미지)은 "molt"(새 이미지를 빌드·테스트 후 교체)로 바뀔 수 있음. 기억 계층: raw 일지, 임베딩 기반 key graph(`memory.json`), 컴파일된 위키 개념, whoAmI, 프롬프트 4종(`base/wake/reflect/sleep.md`), 행동 로그, 세션. LLM은 로컬 MLX(Qwen3.6-35B-A3B 4bit 예시)·Anthropic·OpenAI 어댑터와 폴백. 미션은 사용자가 `base.md`에 정의("컨테이너 탈출"을 예시로 들 정도로 경계 실험적 성격).

### 8. retype — "AI가 불러주고 사람이 직접 친다" (TypeScript, VS Code 확장)
- 인지부채(자기가 짜지 않은 코드를 떠안을 때 쌓임) 문제의식. 에이전트가 MCP 툴 `propose(text, why)`를 호출하면 편집기에 회색 고스트 텍스트가 뜨고 사람이 다 칠 때까지 호출이 블로킹된다(Tab은 수락이 아니라 들여쓰기). `read_viewport()`로 에이전트가 지금 보이는 구간을 가져가고, `Cmd+K Q`로 구간 질문. 확장이 로컬 MCP 서버를 띄우고(`127.0.0.1` 랜덤 포트) LLM·API 키는 없다. Claude Code 확장/Codex 둘 다 지원.

### 9. 그 밖의 레포
최근 푸시 순으로: adk-python(포크, Google ADK; 기여용), procedural-graphs-lab, neural-memory-research, semora-console, sot-demo(Semora 기반 AG-UI 에이전트 서버, 세션 지향 합의 프로토콜 데모), OpenMausBot(포크), rhwp(포크, 아래한글 hwp 뷰어/에디터 Rust+wasm), sandbox-runtime·langgraph·langchain·openclaw 등 포크, ai-librarian(RAG 독서모임 도우미, star 4), mcp-super-memory(keymem의 전신으로 보이는 N:M 연상 기억, 해석), KoreanNLU-Intent, Voice_AI_Bot_Service, tts_server, 42 교육과정 계열 C/C++ 과제(Mini_Shell, webserv, 42born2code), Genesis-Robotics-Simulation-Guide, Ray_Tracing_MLX 등. 연도순 궤적은 시스템 프로그래밍(C/C++) → 데이터/음성 서비스(Python) → LLM agent 인프라(TS/Python/Go)다.

## 구체 사실·수치 요약
- 공개 레포 41, 비포크 30. 직접 clone해 확인한 레포 8개.
- keymem: npm 최신 0.32.2(2026-09-29 changelog), 테스트 파일 81개, HotpotQA bridge both@5 63/53/35%(blind key), 훅 대기 9초.
- codecanvas: 54세션 비교, 토큰 중앙값 -22.95%.
- msbd 내부 Go 코드 약 3,835줄(`internal/*/*.go` 합산).
- 모든 수치는 각 레포 README/벤치마크 문서의 자체 측정이며 제3자 검증은 없다.

## 비판적 평가
- 일관된 주제와 정직한 한계 서술이 강점이다: README마다 "Known limitation", "honest costs", 자기 key가 결과를 부풀렸다는 고백, 외부 공급자 idempotency 비보증 같은 단서를 직접 적는다. 이는 에이전트 인프라 레포로서는 드문 신뢰 신호다.
- 반면 star 0~4개, 단일 기여자, 빠른 방향 전환(Nexora 동결 → Semora, Semora 0.2 LangChain 폐기 → 0.3 Pydantic AI)은 장기 의존 대상으로는 위험하다. breaking release와 재구현이 짧은 주기에 이뤄졌다.
- keymem의 연상 기억이 flat 검색을 앞선 폭(+10pp)은 작은 합성/단일 데이터셋 기준이고 비교 질문에서는 손해다. 실제 에이전트 최종 과업 개선은 입증되지 않았다. 훅 지연(로컬 reranker로 프롬프트당 수 초)도 비용이다.
- codecanvas의 토큰 22.95% 절감은 한 모델·한 하네스·3회 반복의 결과이며 정답 품질은 블라인드 채점 전이다.
- msbd/Firecracker는 호스트에 KVM과 root 권한이 필요하고, 인프라 보안 제품으로 쓰려면 별도의 보안 감사가 필요하다. README도 격리 없는 in-process 백엔드를 개발 전용으로 못 박는다.
- 이 노트는 개인 레포에 대한 객관적 요약이며, 소유자의 신원·소속 정보는 의도적으로 기록하지 않았다.

## 관련 노트
- [[latex-resume-template-kor]]
- [[hada-claude-opus-5-5-prompting]]
- [[toss-ai-platform-engineer-serving]]
- [[ai-top-100]]
- [[tally-nova-2026-medical-ai-contest]]

## 출처
- https://github.com/donggyun112 (GitHub API 사용자·레포 목록, 2026-10-01)
- https://github.com/donggyun112/keymem (README, BENCHMARKS.md, CHANGELOG.md, 구조 — clone)
- https://github.com/donggyun112/codecanvas (README, benchmarks/README.md)
- https://github.com/donggyun112/semora (README)
- https://github.com/donggyun112/effect-ledger (README)
- https://github.com/donggyun112/nexora (README)
- https://github.com/donggyun112/msbd (README, 구조)
- https://github.com/donggyun112/autonomous-agent (README)
- https://github.com/donggyun112/retype (README)
- https://registry.npmjs.org/keymem/latest (최신 버전 확인)

## 확인하지 못한 항목
- 나머지 비핵심 레포(procedural-graphs-lab, neural-memory-research, sot-demo, ai-librarian 등)의 README, 코드 품질, 각 레포의 CI 상태, 사용 사례나 외부 채택 현황, semora-console 라이브 데모 동작.
