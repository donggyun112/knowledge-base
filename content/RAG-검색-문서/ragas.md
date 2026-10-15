---
title: Ragas
source: https://github.com/vibrantlabsai/ragas
type: repo
category: RAG-검색-문서
tags: [research, rag, evaluation, llm-eval]
researched: 2026-10-01
---
# Ragas

> [!summary] 한줄요약
> RAG/LLM 애플리케이션을 "감"이 아니라 지표로 평가하는 Python 라이브러리. LLM-as-judge 기반 metric(faithfulness, context precision/recall 등)과 전통 metric(BLEU, ROUGE 등), 지식 그래프 기반 테스트셋 자동 생성, 실험(experiment) 러너를 제공한다. 현재 저장소 소유는 vibrantlabsai로 옮겨졌고(구 explodinggradients), 최신 릴리스는 2026-01의 v0.4.3로 최근 8개월은 릴리스가 없다.

## 배경: 해결하려는 문제

RAG를 만들어 놓고 "좋아졌는지" 판단할 방법이 없으면 청킹, 임베딩 모델, 검색기, 리랭커, 프롬프트를 바꿀 때마다 눈으로 몇 개 답을 보고 결정하게 된다. Ragas의 출발점은 이 평가를 자동화하되 정답 라벨을 사람이 일일이 만들지 않아도 되게 하는 것이었다. 핵심 아이디어는 질문-검색 컨텍스트-답변-(선택)참조 답변 사이의 관계를 LLM이 분해해서 검사하는 것이다. 예를 들어 답변을 "주장(claim)" 단위로 쪼개 각 주장이 검색된 컨텍스트로 뒷받침되는지 판정해 비율을 낸다. 사람이 만든 정답이 없을 때도 질문+답변+컨텍스트만으로 점수를 내는 지표가 있고, 정답이 있을 때는 참조 답변을 이용하는 지표가 있다.

README는 이를 네 가지로 소개한다. 객관적 metric(LLM 기반과 전통적 방식 모두), 테스트 데이터 자동 생성, LangChain 등 프레임워크와 관측 도구와의 연동, 프로덕션 데이터를 이용한 피드백 루프.

## 동작 원리와 아키텍처

### 평가의 기본 구성

평가는 (1) 샘플(`user_input`, `response`, `retrieved_contexts`, `reference` 등), (2) metric, (3) 판정용 LLM(필요 시 임베딩 모델)의 조합이다. 현재 문서의 권장 방식은 `ragas.metrics.collections`의 새 metric 클래스를 만들어 `await metric.ascore(...)`로 샘플 하나씩 점수를 얻는 것이고(동기 버전은 `.score()`), 반환값은 `MetricResult`(`value`, `reason`)다. 기존 `SingleTurnSample`+`evaluate(dataset, metrics, llm, embeddings, ...)` 방식은 "legacy metrics API"로 분류되어 문서에 "0.4에서 deprecated, 1.0에서 제거 예정"이라고 적혀 있다. 즉 v0.4.x는 두 API가 공존하는 과도기다. 소스에서도 `src/ragas/metrics/_faithfulness.py`(구) 와 `src/ragas/metrics/collections/faithfulness/`(신)가 나란히 있다.

새 구현은 LLM 호출을 `instructor` 라이브러리 기반의 구조화 출력(Pydantic 모델)으로 한다. `llm_factory(model, provider="openai", client=..., adapter="auto")`가 공급자별 어댑터(Instructor 기본, Gemini는 LiteLLM)를 고르고, 새 Faithfulness는 "구형 LangChain 래퍼는 거부한다"고 클래스 docstring에 적혀 있다. 이 때문에 구 코드(LangChain LLM 래퍼를 넘기던 방식)는 마이그레이션이 필요하다(`docs/howtos/migrations`에 가이드 디렉터리가 있으나 열어 보지 않음).

```mermaid
flowchart LR
    S[샘플<br/>user_input / response<br/>retrieved_contexts / reference] --> M{Metric}
    M --> L[Judge LLM<br/>instructor 구조화 출력]
    M --> E[임베딩 모델<br/>(일부 metric)]
    L --> R[MetricResult<br/>value + reason]
    E --> R
    R --> X[Experiment / 결과 저장<br/>local_csv · local_jsonl · gdrive · inmemory]
    X --> O[관측·트레이싱 연동<br/>LangSmith · Opik · Helicone · MLflow · Langfuse]
```

### 대표 metric의 계산 방식

문서에서 확인한 정의는 다음과 같다.

- **Faithfulness**: 답변을 주장들로 분해 → 각 주장이 검색 컨텍스트에서 추론 가능한지 NLI 방식으로 판정 → (뒷받침되는 주장 수) / (전체 주장 수). 문서 예시에서 "아인슈타인은 독일에서 1879년 3월 20일에 태어났다"는 두 주장 중 하나(날짜)가 틀려 0.5가 나온다. 두 번째 단계(주장 판정)를 Vectara의 HHEM-2.1-Open 분류 모델로 바꾸는 `FaithfulnesswithHHEM` 변형도 있다(문서 기재, legacy API 쪽).
- **Context Recall**: 참조 답변(`reference`)을 주장들로 분해하고, 각 주장이 검색된 컨텍스트로 귀속될 수 있는 비율. 참조 컨텍스트 라벨 대신 참조 답변을 대용으로 써서 라벨링 비용을 줄였다.
- **Context Precision**: 검색 결과 순위에서 관련 chunk가 위에 있는지를 보는 지표로, 각 순위 k의 precision@k의 평균이다.
- 그 외 문서 목록(`docs/concepts/metrics/available_metrics/index.md`): Context Entities Recall, Noise Sensitivity, Response Relevancy, Multimodal Faithfulness/Relevance, NVIDIA 계열(Answer Accuracy, Context Relevance, Response Groundedness), 에이전트용(Topic Adherence, Tool Call Accuracy, Tool Call F1, Agent Goal Accuracy), 자연어 비교(Factual Correctness, Semantic Similarity, BLEU, CHRF, ROUGE, String Presence, Exact Match), SQL(Datacompy 실행 기반 점수, SQL 의미 동등성), 범용(Aspect Critic, Simple Criteria Scoring, Rubrics 기반, Instance-specific Rubrics), 요약 점수.

범용 metric은 직접 정의도 가능하다. README 예시는 `DiscreteMetric(name="summary_accuracy", allowed_values=["accurate","inaccurate"], prompt=...)`로 판정 기준을 자연어 프롬프트로 주고 `ascore(llm=..., response=...)`를 호출하는 방식이다. 사내 도메인에 맞는 "정책 준수", "톤", "개인정보 노출 없음" 같은 기준을 이 방식으로 만들 수 있다.

### 테스트셋 자동 생성

`docs/concepts/test_data_generation/rag.md`에 방식이 설명되어 있다. 질의 유형을 단일 홉(single-hop)/다중 홉(multi-hop) × 구체(specific)/추상(abstract)으로 나누고, 이를 문서에서 만들어 내기 위해 문서를 지식 그래프로 변환한다. 변환 단계(`default_transforms`)는 문서 분할, 요약·키프레이즈·제목·헤드라인·테마·NER 추출, 요약 임베딩 생성, 코사인 유사도(임계 0.7 등)로 노드 간 관계 구축 등이다. 그 위에서 `SingleHopSpecificQuerySynthesizer`, `MultiHopAbstractQuerySynthesizer`, `MultiHopSpecificQuerySynthesizer`가 노드 군집을 골라 질의-참조 답변 쌍을 만들며, `persona.py`로 질문자 페르소나를 생성해 다양성을 준다. 이미 chunking이 된 데이터용 `default_transforms_for_prechunked`도 있다. 이 방식의 장점은 "서로 연관된 여러 문서 조각이 필요한" 다중 홉 질문을 만들 수 있다는 점이고, 단점은 생성된 질문과 정답의 품질 자체가 LLM에 달려 있어 사람의 검수가 필요하다는 점이다(문서도 judge 정렬과 데이터를 직접 보는 것의 중요성을 강조한다).

### 실험(Experiment)과 judge 정렬

`@experiment()` 데코레이터로 "데이터셋 행마다 내 애플리케이션을 실행하고 metric을 적용해 결과를 저장"하는 루프를 만든다. 문서의 원칙은 측정 가능한 metric 정의, 체계적 결과 저장, 변경 하나씩 격리, 반복이다. 결과 저장 백엔드는 `backends/`의 local_csv, local_jsonl, gdrive, inmemory다. 문서 `howtos/applications/align-llm-as-judge.md`는 LLM judge를 사람 전문가 라벨과 먼저 정렬하라고 강조한다("방향이 틀린 나침반"). 이 권고는 우리에게 중요하다. judge가 한국어/도메인에 잘 맞는지 확인하지 않고 쓰면 점수의 의미가 없다. 프롬프트를 다른 언어로 옮기는 `adapt`/`adapt_prompts` 기능이 소스(`prompt/pydantic_prompt.py`, `prompt/mixin.py`)에 있어 비영어 평가를 염두에 둔 설계로 보이지만, 한국어에서의 품질은 확인하지 못했다.

## 설치와 사용법

```bash
pip install ragas                 # Python >=3.9
ragas quickstart                  # 템플릿 목록 (CLI 코드상 9개: rag_eval, improve_rag, agent_evals, text2sql 등. README는 rag_eval만 안내하고 나머지를 Coming Soon으로 적어 둠)
ragas quickstart rag_eval -o ./my-project
uvx ragas quickstart rag_eval     # 설치 없이
```

```python
import asyncio
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import Faithfulness, ContextRecall

client = AsyncOpenAI()
llm = llm_factory("gpt-4o-mini", client=client)

async def main():
    f = await Faithfulness(llm=llm).ascore(
        user_input="When was the first super bowl?",
        response="The first superbowl was held on Jan 15, 1967",
        retrieved_contexts=["The First AFL–NFL World Championship Game was played on January 15, 1967 ..."],
    )
    print(f.value, f.reason)
    r = await ContextRecall(llm=llm).ascore(
        user_input="Where is the Eiffel Tower located?",
        retrieved_contexts=["Paris is the capital of France."],
        reference="The Eiffel Tower is located in Paris.",
    )
    print(r.value)

asyncio.run(main())
```

Anthropic을 쓰려면 문서대로 `Anthropic(api_key=...)` 클라이언트와 `llm_factory("claude-...", provider="anthropic", client=client)`를 넘긴다. 사내 OpenAI 호환 게이트웨이(vLLM 등)는 `AsyncOpenAI(base_url=...)`로 연결하는 구성이 자연스럽지만 이번에 실제 호출로 검증하지는 않았다. 선택 extra로 `ragas[tracing]`(langfuse, mlflow), `ragas[gdrive]`, `ragas[dspy]`, `ragas[oci]`, `ragas[ai-frameworks]`(haystack), `ragas[ag-ui]`, `ragas[all]`이 있다.

## 디렉터리·코드 구조에서 확인한 것

- `src/ragas/`: `metrics/`(구 metric 파일들과 `collections/` 신 구현 약 25개 디렉터리), `llms/`(base, litellm_llm, haystack/oci 래퍼, adapters), `embeddings/`, `testset/`(graph, persona, synthesizers, transforms: extractors/relationship_builders/splitters), `integrations/`(langchain, langgraph, llama_index, langsmith, opik, helicone, amazon_bedrock, griptape, swarm, r2r, ag_ui, tracing), `optimizers/`(genetic, dspy 기반 프롬프트 최적화), `backends/`, `experiment.py`, `evaluation.py`, `executor.py`(비동기 실행), `cache.py`, `cost.py`(토큰 비용), `cli.py`(typer), `_analytics.py`.
- 핵심 의존성(pyproject): `numpy`, `datasets>=4.0`, `pydantic>=2`, `openai`, `instructor`, `tiktoken`, `diskcache`, `typer`, `rich`, `networkx`, `scikit-network`, 그리고 `langchain`, `langchain-core`, `langchain-community`, `langchain_openai`. 코어 설치에 LangChain 계열이 필수로 들어와 설치가 무겁다는 점을 기억해 둘 것.
- 문서: `docs/concepts`(metrics, test_data_generation, components, experimentation, feedback), `docs/howtos`(CI 연동, 프롬프트 반복, 임베딩/LLM 비교, 멀티턴 평가, text2sql, judge 정렬 등), `docs/getstarted`.
- 테스트와 CI: `tests/` 디렉터리, `Makefile`, `CLAUDE.md`(저장소가 Claude Code 작업 지침을 포함). `SECURITY.md`는 취약점 신고용 메일을 안내하는데, 지원 버전 표에는 0.3.x만 "지원"으로 표시되어 있어 최신 0.4.x와 맞지 않는다(문서 갱신 누락으로 보이며 의미는 확인하지 못함).

## 저장소 소유 이전(explodinggradients → vibrantlabsai)

이전 노트에서 비어 있던 항목이다. GitHub API로 `explodinggradients/ragas`를 조회하면 `full_name`이 `vibrantlabsai/ragas`로 돌아오고(스타 15,894 동일), 같은 저장소로 리다이렉트된다. 즉 조직 이전/개명이다. 분석 엔드포인트 상수에 `explodinggradients.com`이 "legacy"로 남아 있다는 코드 주석도 같은 맥락이다. README는 VibrantLabs를 운영 주체로 소개하고 "AI 앱 평가 개선을 도와 드린다"는 컨설팅 연락처를 안내한다. 이전 시점과 사유는 확인하지 못했다.

## 비교 대상

- **DeepEval / TruLens / LangSmith evals 등**: 같은 LLM-as-judge 계열이다. 각 도구의 metric 구현 차이와 최신 상태는 이번에 조사하지 않았다(확인 못함). Ragas는 RAG 지표 세트와 지식 그래프 기반 테스트셋 생성이 대표 강점으로 알려져 있으나 이 비교는 문서에서 직접 확인한 것이 아니다.
- **전통적 IR 평가(nDCG, recall@k, MRR)**: 정답 문서 라벨이 있을 때는 이쪽이 더 싸고 결정론적이다. Ragas의 LLM 기반 context recall은 라벨이 없을 때의 대안이다. 두 접근을 병행하는 것이 좋다. [[splade-v3-doc]] 같은 검색 모델 자체를 비교하는 데는 BEIR 계열 IR 지표가 낫다.
- **직접 만든 pytest 회귀 세트**: 정확 일치/키워드 포함 같은 규칙 기반 체크는 비용이 0이고 안정적이다. Ragas는 의미 판단이 필요한 부분에만 쓰는 것이 경제적이다.

## 장단점, 한계, 성숙도

장점: RAG 평가 개념(faithfulness, context precision/recall, noise sensitivity)을 코드와 문서로 사실상 표준처럼 정리했다. 문서가 풍부하다(CI 연동, judge 정렬, 비용 측정 등 how-to). 에이전트, SQL, 멀티모달, 멀티턴까지 확장했다. Apache-2.0이고 분석 수집을 끌 수 있다.

한계: (1) LLM-as-judge 점수는 judge 모델의 편향·불안정성에 좌우되고 점수 간 비교는 같은 judge, 같은 프롬프트일 때만 의미가 있다. (2) 평가 호출 수가 많다. Faithfulness는 최소 두 단계(주장 추출 → NLI 판정) LLM 호출이라 데이터가 크면 비용과 시간이 든다(`cost.py`와 `howtos/applications/_cost.md`가 비용 추적을 돕는다). (3) API 이행기다. 구 `ragas.metrics`와 신 `ragas.metrics.collections`가 섞여 예제가 버전에 따라 깨질 수 있다. (4) 이슈 현황: 오픈 이슈+PR 621건(API의 open_issues_count). 최근 항목에 `answer_relevancy`가 동기 임베딩 호출 때문에 이벤트 루프를 막는다는 보고(#3040/#3043), 메타데이터 필터 검색 정확성 metric 제안(#3045), 문서 링크/CI 수정 등이 보인다. (5) 릴리스 정체: 최신 v0.4.3(2026-01-13), 마지막 push 2026-02-24, 이후 7개월간 커밋이 없고 이슈·PR만 쌓이는 상태로 보인다(clone의 마지막 커밋 날짜 2026-02-24와 일치). 유지 관리가 느려진 것인지 다른 저장소로 개발이 옮겨 간 것인지는 확인하지 못했다.

성숙도 사실: Stars 15,894, Forks 1,734, Apache-2.0, 생성 2023-05-08, 최신 릴리스 v0.4.3(2026-01-13), v0.4.2(2025-12-23), v0.4.1(2025-12-10).

## 보안·라이선스·운영 리스크

- **사용 통계 수집(opt-out)**: `src/ragas/_analytics.py`에서 확인했다. 평가/테스트셋 생성 이벤트에 metric 이름 목록, 행 수, 평가 유형(SINGLE_TURN/MULTI_TURN), 언어, 익명 user_id(로컬 사용자 데이터 디렉터리의 `uuid.json`에 저장된 난수)와 ragas 버전을 모아 `https://t.explodinggradients.com`으로 배치 전송한다(타임아웃 1초). README는 개인·회사 식별 정보가 없다고 밝히며 `RAGAS_DO_NOT_TRACK=true` 환경변수로 끈다. 사내 폐쇄망/보안 정책에서는 이 값을 반드시 설정하고, 방화벽에서 해당 도메인을 막는 것을 권한다. 송신 내용을 패킷 수준으로 검증하지는 않았다.
- **데이터 반출**: judge LLM에 질문, 컨텍스트, 답변이 전달된다. 사내 문서 기반 RAG를 외부 API judge로 평가하면 문서 내용이 외부로 나간다. 사내 호스팅 모델(OpenAI 호환 엔드포인트) judge를 쓰거나, 비식별 처리된 평가셋만 쓴다.
- **의존성 규모**: LangChain 계열이 코어 의존성이라 취약점 스캔 대상이 많다. 설치 환경은 가상환경/컨테이너로 격리한다.
- **라이선스**: Apache-2.0. 큰 부담 없음.
- **재현성**: judge 모델 버전이 바뀌면 점수가 달라진다. 평가 결과에 모델명·버전·프롬프트 해시를 같이 저장하고, 캐시(`cache.py`, diskcache)를 활용해 반복 평가 비용을 줄인다.

## 관련 노트

[[pageindex]] [[cerebras-knowledge-base-pgvector-rrf-mcp]] [[classifier-dev]] [[opendataloader-pdf]] [[ragu]] [[splade-v3-doc]]

> [!note] 2026-10-01 팩트체크
> `ragas quickstart` 템플릿: 노트는 "rag_eval만 제공"이라 썼으나 이는 README 문구이고, `src/ragas/cli.py`에는 9개 템플릿(rag_eval, improve_rag, agent_evals, llamaIndex_agent_evals, text2sql, workflow_eval, prompt_evals, judge_alignment, benchmark_llm)이 정의돼 있어 바로잡았다. 스타는 재조회 값 15,894로 갱신. 그 외(릴리스·라이선스·의존성·analytics·metric 정의·deprecated 문구)는 일치.

## 출처

- https://github.com/vibrantlabsai/ragas (README 전문, `pyproject.toml`, `SECURITY.md`, `src/ragas/` 디렉터리와 `_analytics.py`, `evaluation.py`, `llms/base.py`, `testset/` 코드, `docs/concepts/metrics/available_metrics/{index,faithfulness,context_recall,context_precision}.md`, `docs/concepts/test_data_generation/rag.md`, `docs/concepts/experimentation.md`, `docs/getstarted/quickstart.md`, `docs/howtos/applications/align-llm-as-judge.md`; 2026-10-01 clone 후 열람)
- GitHub REST API: repos 메타데이터, releases, 오픈 이슈 목록, `explodinggradients/ragas` 조회 결과(2026-10-01)
- 열람하지 않은 것: docs.ragas.io 공개 사이트, 마이그레이션 가이드, 타 평가 도구와의 실측 비교, 한국어 judge 정확도
