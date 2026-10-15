---
title: Donggyun의 지식베이스
---

AI 기술 조사와 직접 수행한 연구를 주제별로 모았습니다. 각 제목에서 바로 본문으로 이동할 수 있습니다.

## 주제별 목차

| 주제 | 내용 |
| --- | --- |
| [메모리 연구](#memory) | 직접 수행한 절차 그래프·신경 메모리·커넥톰 실험 |
| [RAG와 검색](#rag) | 문서 처리, 희소·벡터·그래프 검색, 평가 |
| [에이전트와 스킬](#agents) | 런타임, 도구, 스킬, 개발 워크플로 |
| [LLM과 추론 인프라](#inference) | 모델, 서빙, 로컬 추론, 운영·격리 |
| [논문과 평가](#papers) | 메모리·스킬 진화, 신뢰성, 평가 방법 |
| [기타 자료](#resources) | 기술 자료, 커뮤니티, 공개 경진대회 |

<span id="memory"></span>

## 직접 수행한 메모리 연구

| 연구 | 읽기 시작점 |
| --- | --- |
| 절차 그래프와 Grounded Memory | [구조·재현 결과·결합 실험](메모리-연구/절차-그래프-읽기) |
| 신경 메모리 | [합성 회상·사람 대화·개입 대조](메모리-연구/신경-메모리-읽기) |
| 초파리 커넥톰 | [실제 회로·용량·간섭 실험](메모리-연구/커넥톰-읽기) |

[[메모리-연구/연구-안내|연구 전체 안내와 결과 해석 기준]]

> [!example]- 절차 그래프 — 설계와 실험 보고서
> - [[메모리-연구/procedural-graphs/README|절차 그래프 재현 — 초기 README]]
> - [[메모리-연구/procedural-graphs/REVIEW|재현 및 결합 후기]]
> - [[메모리-연구/procedural-graphs/docs/BENCHMARK|Benchmark acquisition and evaluation protocol]]
> - [[메모리-연구/procedural-graphs/docs/COMBINED_DESIGN|결합 모델 재설계: 공진화하는 절차 귀속 메모리]]
> - [[메모리-연구/procedural-graphs/docs/DUAL_MEMORY|Grounded semantic memory + procedural memory]]
> - [[메모리-연구/procedural-graphs/docs/PAPER_NOTES|Two-paper claim ledger]]
> - [[메모리-연구/procedural-graphs/docs/REPRODUCTION_SPEC|Two-paper reproduction specification]]
> - [[메모리-연구/procedural-graphs/results/EXPERIMENT_REPORT_KO|Grounded Semantic Memory × Procedural Graph 재현 보고서]]

> [!example]- 신경 메모리 — 모델과 실험 보고서
> - [[메모리-연구/neural-memory/neural-memory/MEMORY_PATH_DIAGNOSTIC_REPORT|메모리 경로 원인 분리 실험 — 2026-09-26]]
> - [[메모리-연구/neural-memory/neural-memory/PAPER|What a Bounded Memory Layer Can and Cannot Do Before the Query Arrives]]
> - [[메모리-연구/neural-memory/neural-memory/README|신경 메모리 모델·실험 안내]]
> - [[메모리-연구/neural-memory/neural-memory/RESEARCH|Research reuse map]]
> - [[메모리-연구/neural-memory/neural-memory/RESTART_EXPERIMENT_REPORT|메모리 모델 재설계 실험 보고 (2026-09-25 KST)]]
> - [[메모리-연구/neural-memory/neural-memory/RESTART_SPEC|Neural memory restart: falsifiable design v0]]
> - [[메모리-연구/neural-memory/neural-memory/RESULTS|신경 메모리 실험 원장 — Phase 0–89]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_ACQUISITION_REPORT|기존 상태 이후 새 사실 획득 — 2026-09-27]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_BALANCE_REPORT|정정·반복 간섭 균형 실험 — 2026-09-27]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_COUNTERFACTUAL_LEARNING_REPORT|반사실 미래 대화 손실과 중간 구간 획득 진단 — 2026-09-28]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_EXPERIMENT_REPORT|연속 대화 메모리 파일럿 — 2026-09-27]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_GENERALIZATION_REPORT|기억 거리·잡담 위치 일반화 — 2026-09-27]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_HUMAN_E2E_REPORT|실제 사람 대화 연속성 평가 — 2026-09-28]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_HUMAN_FROZEN_REPORT|사람 대화로 기억 경로만 학습한 실험 — 2026-09-28]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_NEURAL_WRITER_REPORT|학습형 writer와 상태 소실 진단 — 2026-09-28]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_OPEN_VOCAB_REPORT|값 다양성 대조와 미학습 값 전이 — 2026-09-27]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_READ_ADAPTER_REPORT|토큰 조건부 기억 읽기 실험 — 2026-09-28]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_REGRESSION_REPAIR_REPORT|Stream-memory regression repair — 2026-09-28]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_RETENTION_REPORT|정정 표현 다양화·출력 유지 제약 실험 — 2026-09-27]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_REVISION_REPORT|신경망 기억의 정정 학습 — 2026-09-27]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_SPEC|연속 대화로 학습하는 신경망 메모리 — 2026-09-27]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_STATE_DIAGNOSTIC_REPORT|사람 대화 기억 상태의 정보·읽기 분리 진단 — 2026-09-28]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_TRANSFER_REPORT|어휘 전이·경쟁 잡담·정정 검사 — 2026-09-27]]
> - [[메모리-연구/neural-memory/neural-memory/STREAM_MEMORY_UPDATE_REPORT|기억 갱신 경로 진단 — 2026-09-27]]

> [!example]- 연구 결론과 측정 기록
> - [[메모리-연구/neural-memory/board/001-valence-to-action|001 — the valence-to-action gap]]
> - [[메모리-연구/neural-memory/board/002-data-loss|002 — 4.8GB destroyed by a cleanup, and what it costs]]
> - [[메모리-연구/neural-memory/board/003-write-time-selection|003 — write-time selection]]
> - [[메모리-연구/neural-memory/board/004-harness-hazards|004 — hazards in the repair harness that have not bitten yet]]
> - [[메모리-연구/neural-memory/board/README|board]]
> - [[메모리-연구/neural-memory/board/claims|What we believe, and what measured it]]
> - [[메모리-연구/neural-memory/board/open|Open questions]]

> [!example]- 초파리 커넥톰 — 실험 원장
> - [[메모리-연구/neural-memory/fly-connectome/README|초파리 커넥톰 연구 — 실험 기록]]

- [[메모리-연구/neural-memory/FINDINGS|What this repository knows about memory for agents]]
- [[메모리-연구/neural-memory/README|신경 메모리 연구 저장소 안내]]

<span id="rag"></span>

## RAG · 검색 · 문서 처리

희소·벡터·그래프 검색, 문서 색인과 파싱, 검색 품질 평가.

- [[RAG-검색-문서/anydoc|anydoc (Firecrawl)]]
- [[RAG-검색-문서/cerebras-knowledge-base-pgvector-rrf-mcp|Cerebras 사내 지식 베이스 설계 (PyTorchKR 해설)]]
- [[RAG-검색-문서/classifier-dev|classifier.dev]]
- [[RAG-검색-문서/graphify|Graphify]]
- [[RAG-검색-문서/inference-free-splade-blog|Inference-Free SPLADE (Kumar Shivendu 블로그)]]
- [[RAG-검색-문서/markitdown|MarkItDown]]
- [[RAG-검색-문서/mongodb-crewai-ecommerce-agents|Building E-commerce AI Agents on MongoDB with CrewAI]]
- [[RAG-검색-문서/opendataloader-pdf|OpenDataLoader PDF]]
- [[RAG-검색-문서/pageindex|PageIndex]]
- [[RAG-검색-문서/ragas|Ragas]]
- [[RAG-검색-문서/ragu|RAGU (Retrieval-Augmented Graph Utility)]]
- [[RAG-검색-문서/semantica|Semantica]]
- [[RAG-검색-문서/splade-v3-doc|naver/splade-v3-doc]]
- [[RAG-검색-문서/vector-db-comparison-2023|2023년을 위한 벡터 데이터베이스 선택 비교 및 안내 (jinicoding)]]

<span id="agents"></span>

## 에이전트 · 스킬 · 개발 도구

에이전트 런타임, 도구 실행, 스킬과 개발 워크플로.

- [[에이전트-스킬/actguard|ActGuard (binzhwang)]]
- [[에이전트-스킬/ag-ui-docs|AG-UI (Agent-User Interaction Protocol) 공식 문서]]
- [[에이전트-스킬/agency-agents|agency-agents (msitarzewski)]]
- [[에이전트-스킬/agent-skills|addyosmani/agent-skills]]
- [[에이전트-스킬/agentspace|AgentSpace (HKUDS)]]
- [[에이전트-스킬/ai-engineering-from-scratch|AI Engineering from Scratch (rohitg00)]]
- [[에이전트-스킬/claude-code-best-practice|claude-code-best-practice]]
- [[에이전트-스킬/claw-code|Claw Code]]
- [[에이전트-스킬/copilotkit-openbot|OpenBot (CopilotKit)]]
- [[에이전트-스킬/diagram-design|diagram-design]]
- [[에이전트-스킬/firecrawl-web-agent|Firecrawl Web Agent]]
- [[에이전트-스킬/generic-agent|GenericAgent]]
- [[에이전트-스킬/gepa|GEPA (gepa-ai)]]
- [[에이전트-스킬/headroom|Headroom]]
- [[에이전트-스킬/hermes-bot-mode|Hermes Bot Mode (NousResearch)]]
- [[에이전트-스킬/huashu-design|huashu-design]]
- [[에이전트-스킬/im-not-ai|im-not-ai]]
- [[에이전트-스킬/insane-search|insane-search (fivetaku)]]
- [[에이전트-스킬/k-skill|k-skill]]
- [[에이전트-스킬/mengto-skills|Agent Skills (MengTo/Skills)]]
- [[에이전트-스킬/multica|Multica]]
- [[에이전트-스킬/neurons|Neurons]]
- [[에이전트-스킬/nullclaw|NullClaw]]
- [[에이전트-스킬/onyx|Onyx]]
- [[에이전트-스킬/openviking|OpenViking (volcengine)]]
- [[에이전트-스킬/openworker|OpenWorker (Andrew Ng)]]
- [[에이전트-스킬/pytorchkr-ag-ui-copilotkit|AG-UI feat. CopilotKit (PyTorchKR 포스트)]]
- [[에이전트-스킬/sanglard-agent-md|Agent.md for LLM-assisted code quality (Fabien Sanglard)]]
- [[에이전트-스킬/weknora|WeKnora (Tencent)]]

<span id="inference"></span>

## LLM · 추론 · 운영 인프라

모델 구조, 로컬 추론, 서빙과 격리·운영 사례.

- [[LLM-추론-인프라/apertus-v1-5-70b|Apertus v1.5 70B]]
- [[LLM-추론-인프라/inflab-ai-gateway|인프랩 AI Gateway 도입기]]
- [[LLM-추론-인프라/lucebox-hub|Lucebox Hub]]
- [[LLM-추론-인프라/microvm-isolation-2026|Your Container Is Not a Sandbox - MicroVM Isolation in 2026]]
- [[LLM-추론-인프라/multi-agent-cad|Multi-Agent CAD (MAC)]]
- [[LLM-추론-인프라/openclip|OpenClip]]
- [[LLM-추론-인프라/opencut|OpenCut]]
- [[LLM-추론-인프라/qwen-ai-home|Qwen (qwen.ai) 홈]]
- [[LLM-추론-인프라/qwen3-5-9b|Qwen3.5-9B]]
- [[LLM-추론-인프라/reddit-qwen36-27b-q40-mtp-gguf|Reddit r/LocalLLaMA - Qwen 3.6 27B Q4_0 MTP GGUF]]
- [[LLM-추론-인프라/reddit-why-not-microvm|Reddit r/sysadmin - Why not use microVM?]]
- [[LLM-추론-인프라/univa-ai|UNIVA (ZEPHY)]]
- [[LLM-추론-인프라/vllm-moriio-kv-connector|vLLM MoRIIO KV Connector (단일 노드 PD Disaggregation)]]
- [[LLM-추론-인프라/woowa-ai-platform-2-llmops|우아한형제들 AI플랫폼 2.0 — LLMOps (GenAI Studio·SDK·API Gateway·Labs)]]

<span id="papers"></span>

## 논문 · 평가 · 학습 방법

메모리·스킬 진화, 신뢰성, 평가 방법과 연구 관점.

- [[논문-아티클/aces-agentic-continuous-evaluation-of-skills|Evaluating Skills, Not Just Agents: Agentic Continuous Evaluation of Skills (ACES)]]
- [[논문-아티클/algorithmically-establishing-trust-in-evaluators|Algorithmically Establishing Trust in Evaluators]]
- [[논문-아티클/context-fails-first-agent-reliability|AI Agents Do Not Fail Alone: The Context Fails First]]
- [[논문-아티클/hyperagents|Hyperagents]]
- [[논문-아티클/jev-as-a-judge-agent-evals|Jev-as-a-Judge for Agent Evals]]
- [[논문-아티클/karpathy-llm-wiki|LLM Wiki (Karpathy gist)]]
- [[논문-아티클/llm-agent-skill-memory-without-finetuning|LLM Agent Skill Memory without Finetuning (Procedural Memory)]]
- [[논문-아티클/llm-online-deanonymization|Large-scale online deanonymization with LLMs]]
- [[논문-아티클/new-sdlc-with-vibe-coding|The New SDLC with Vibe Coding]]
- [[논문-아티클/probe-process-based-hallucination-benchmark|PROBE: PROcess-Based BEnchmark for Hallucination Detection]]
- [[논문-아티클/procedural-graphs-self-evolving|Procedural Graphs: Self-Evolving Execution Structures for LLM Agents]]
- [[논문-아티클/skillzip-pro|SkillZip Pro: Execution-Aware Dynamic Compression of Progressively Loaded Skills for Self-Evolving Agents]]
- [[논문-아티클/unclejobs-llm-wiki-fork|LLM Wiki (unclejobs-ai fork, Korean addendum)]]
- [[논문-아티클/wikiskill|WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution]]
- [[논문-아티클/wisv-wireless-informed-semantic-verification|WISV: Wireless-Informed Semantic Verification for Distributed Speculative Decoding in Device-Edge LLM Inference]]

<span id="resources"></span>

## 자료 · 커뮤니티 · 경진대회

기술 자료와 공개 경진대회 안내.

- [[기타-리소스/ai-top-100|AI_TOP_100 (2026)]]
- [[기타-리소스/hada-claude-opus-5-5-prompting|GeekNews - Claude Opus 5.5 프롬프트 작성법]]
- [[기타-리소스/jina-ocr-v1-threads|Threads - Jina AI jina-ocr-v1 소개 게시물]]
- [[기타-리소스/tally-nova-2026-medical-ai-contest|N.O.V.A. 2026 대화형 의료 진단 AI 에이전트 개발 경진대회 신청 폼]]
- [[기타-리소스/wikidocs-325677|WikiDocs 325677]]

---

[[READING-GUIDE|주제별 읽기 가이드]]
