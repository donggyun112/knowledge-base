---
title: Research 읽기 순서 가이드
tags: [research, guide]
researched: 2026-10-01
---
# Research 읽기 순서 가이드

> [!info] 이 가이드의 기준
> 전체 목차는 [[research-index]]. 아래 우선순위는 노트의 요약을 바탕으로 한 **제 판단**이다(노트를 정독한 결과가 아니다). 기준은 사내 RAG·LLM 도입·에이전트 개발에 얼마나 직접 연결되는지다. 관심사가 바뀌면 순서도 바뀐다.
> 표기: 📖 노트만 읽어도 충분 / 🔗 노트로 윤곽을 잡고 원문(코드·논문)도 볼 가치 있음

## 1순위 — 업무에 바로 연결

### A. 사내 LLM 도입·운영 (게이트웨이, 관측, 비용, PII)
1. [[woowa-ai-platform-2-llmops]] 📖 — 운영 문제 8가지와 컴포넌트 매핑. 도입 순서를 잡는 기준점.
2. [[inflab-ai-gateway]] 📖 — 같은 문제를 Envoy AI Gateway로 푼 사례. 위 글과 게이트웨이 선택이 다르니 나란히 읽기.
3. [[microvm-isolation-2026]] 🔗 — 에이전트가 만든 코드를 어디서 돌릴지(컨테이너는 보안 경계가 아니라는 논지).
4. [[headroom]] 🔗 — 컨텍스트 압축 프록시. 단, 익명 beacon 기본 ON·평문 캐시 저장 같은 보안 사항을 먼저 확인.

### B. RAG·검색·문서 파싱 (한국어 문서 포함)
1. [[pageindex]] 🔗 — 벡터 없이 트리 색인 + LLM 탐색. 긴 규정·매뉴얼류에 적합한지가 판단 포인트.
2. [[opendataloader-pdf]] 🔗 — PDF 파서. HWP/HWPX는 오픈소스 코어에 없다는 점 주의.
3. [[onyx]] 🔗 — 사내 앱 연동 + 권한 기반 RAG 완성형. 구조 참고용으로 가장 가까운 레퍼런스.
4. [[weknora]] 🔗 — Tencent의 엔터프라이즈 지식 플랫폼. onyx와 비교해서 읽기.
5. [[cerebras-knowledge-base-pgvector-rrf-mcp]] 📖 — pgvector + RRF + MCP로 만든 사내 KB 설계.
6. [[ragas]] 📖 — 평가 지표 감 잡기. 이어서 [[jev-as-a-judge-agent-evals]].
7. 파싱 변환 계열은 훑어보기: [[markitdown]], [[anydoc]] 📖

### C. 에이전트 보안·신뢰성
1. [[actguard]] 🔗 — 도구 실행 직전 간접 프롬프트 주입 방어.
2. [[context-fails-first-agent-reliability]] 🔗 — 에이전트 실패의 원인을 컨텍스트 품질로 보는 논문.
3. [[algorithmically-establishing-trust-in-evaluators]] 🔗 — 정답 라벨 없이 LLM-judge를 검증하는 방법.
4. [[probe-process-based-hallucination-benchmark]] 🔗 — 환각 탐지 벤치마크.

## 2순위 — 개발 방식·도구를 바꿀 수 있는 것

### D. Claude Code·에이전트 개발 워크플로우
1. [[hada-claude-opus-5-5-prompting]] 📖 — Opus 5.5 프롬프트 작성법(effort 기본값 등). 지금 쓰는 모델과 직접 관련.
2. [[claude-code-best-practice]] 🔗 — 구성 요소 레퍼런스. 예시 `settings.json`의 광범위 allow는 그대로 복사하지 말 것.
3. [[agent-skills]] 🔗, [[sanglard-agent-md]] 📖 — SDLC를 skill로 옮기는 방식, agent.md로 리뷰 규칙을 고정하는 방식.
4. [[new-sdlc-with-vibe-coding]] 🔗 — Google/Kaggle 백서(51쪽). 팀에 공유하기 좋은 자료.
5. [[gepa]] 🔗 — 프롬프트·스캐폴드 자동 최적화.
6. [[k-skill]] 📖 — 한국 생활·업무용 skill 번들. AGPL 구성요소는 법무 확인 필요.

### E. 에이전트 메모리·스킬 진화 (연구 흐름)
읽는 순서: [[karpathy-llm-wiki]] 📖 → [[llm-agent-skill-memory-without-finetuning]] 📖(8편 비교, 길잡이) → [[wikiskill]] → [[skillzip-pro]] → [[procedural-graphs-self-evolving]] → [[aces-agentic-continuous-evaluation-of-skills]] → [[hyperagents]]. 앞의 두 개를 읽고 관심 가는 논문만 이어서 보면 된다. [[unclejobs-llm-wiki-fork]]는 원본과 동일하니 번역 주석에 관심 있을 때만.
- 메모리 구현 쪽: [[openviking]](AGPL 주의), [[graphify]](패키지명 `graphifyy` typosquatting 주의), [[semantica]], [[ragu]]

### F. 에이전트 UI·프로토콜
[[ag-ui-docs]] → [[pytorchkr-ag-ui-copilotkit]] → [[copilotkit-openbot]]. AG-UI 이벤트는 문서 기준으로 `RUN_*`/`STEP_*`이고, 한국어 해설글의 `LIFECYCLE_SIGNAL`은 현재 스펙에 없다.

## 3순위 — 온프렘 LLM·추론 (필요해질 때)
- [[vllm-moriio-kv-connector]] 🔗 (AMD 하드웨어 전제), [[lucebox-hub]], [[neurons]] — 소비자 GPU·Apple Silicon 추론. 지금 인프라와 맞는지 먼저 확인.
- [[qwen3-5-9b]], [[qwen-ai-home]], [[apertus-v1-5-70b]] — 모델 후보 파악용. 한국어 품질은 어느 노트에서도 검증하지 못했으니 직접 평가해야 한다.
- [[splade-v3-doc]], [[inference-free-splade-blog]] — sparse 검색. 영어 중심이고 splade-v3-doc은 비상업 라이선스.
- [[univa-ai]] — 국내 상용 에이전트(HWP 파싱) 경쟁/참고 사례.

## 4순위 — 참고·기록용
- 에이전트 플랫폼 구경: [[agentspace]](권한 우회 플래그 주의), [[multica]], [[openworker]], [[nullclaw]], [[generic-agent]](XOR 난독화 keychain·`curl | bash`), [[claw-code]], [[firecrawl-web-agent]], [[hermes-bot-mode]], [[agency-agents]], [[mengto-skills]], [[insane-search]](안티봇 우회, 정책 검토 필요)
- 디자인·콘텐츠: [[huashu-design]], [[diagram-design]], [[im-not-ai]], [[openclip]], [[opencut]], [[multi-agent-cad]]
- 학습 자료: [[ai-engineering-from-scratch]] (523개 레슨 커리큘럼, 필요한 phase만)
- 그 외 논문: [[llm-online-deanonymization]](프라이버시 위협 관점), [[wisv-wireless-informed-semantic-verification]](device-edge speculative decoding)
- 기타: [[mongodb-crewai-ecommerce-agents]], [[classifier-dev]], [[vector-db-comparison-2023]](2023년 글, 2026 변경점 절 참고), [[jina-ocr-v1-threads]]

## 개인·커리어·일정 (기한 있음)
- [[ai-top-100]] — 신청 마감 10/21 18:00.
- [[tally-nova-2026-medical-ai-contest]] — 의료 AI 에이전트 경진대회 신청서(제출은 하지 않은 상태).
- [[toss-ai-platform-engineer-serving]] — 채용공고. 서빙(vLLM, Dynamo, Triton) 관련 용어 해설 포함.

## 아직 읽지 못한 것 (본문 수동 확보 필요)
- [[reddit-why-not-microvm]], [[reddit-qwen36-27b-q40-mtp-gguf]], [[wikidocs-325677]] — 봇 차단. 본문을 붙여넣어 주면 채운다.

## 주의가 필요한 라이선스·보안 한눈에
| 대상 | 주의 |
|---|---|
| [[openviking]] | AGPL-3.0 |
| [[k-skill]] | proxy 구성요소 AGPL-3.0-only |
| [[splade-v3-doc]] | CC-BY-NC-SA-4.0, gated |
| [[multica]] | 자체 라이선스(상업·호스팅 조건) |
| [[hyperagents]] | 코드 CC BY-NC-SA 4.0 |
| [[insane-search]] | 안티봇 우회 성격 |
| [[agentspace]], [[generic-agent]], [[multica]], [[onyx]] | 권한 우회 플래그 또는 `curl \| bash` 설치 |
| [[headroom]] | 익명 beacon 기본 ON, 평문 캐시 |
