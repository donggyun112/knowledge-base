---
title: Semantica
source: https://github.com/semantica-agi/semantica
type: repo
category: RAG-검색-문서
tags: [research, context-graph, knowledge-graph, provenance, decision-intelligence]
researched: 2026-10-01
---
# Semantica

> [!summary] 한줄요약
> "벡터 유사도만으로는 설명이 안 되는 AI"를 위한 MIT 라이선스 Python 인프라. 데이터를 수집·추출해 지식 그래프(Context Graph)로 만들고, 그 위에 온톨로지(OWL/SHACL/SKOS), 결정적 추론(Rete·Datalog·SPARQL), W3C PROV-O 출처 추적, 에이전트 결정 기록(Decision Intelligence)을 얹는다. 범위가 매우 넓은 0.x 플랫폼이며 "RAG 검색 엔진"이라기보다 "에이전트 컨텍스트·감사 계층"에 가깝다.

## 배경: 해결하려는 문제

README의 문제 제기는 이렇다. 대부분의 AI 에이전트는 의미가 아니라 임베딩으로 돌아가며, 유사도 점수에는 구조도 관계도 "왜 이 결과가 나왔는가"에 대한 설명도 없다. 금융·의료·법률·공공처럼 규제 도메인에서는 에이전트가 내린 결정에 대해 근거, 출처, 적용된 정책, 실행 이력을 제시해야 한다. Semantica는 LLM·벡터 스토어·에이전트 프레임워크 아래에 놓이는 "시맨틱/컨텍스트 계층"으로 자신을 정의하고, 기존 스택을 대체하지 않고 결정 기록, 인과 추론, 출처, 온톨로지 거버넌스, 충돌 탐지, 감사 추적을 덧붙인다고 설명한다.

README는 범위를 분명히 한정한다. "시스템 수준의 설명 가능성"이지 "파운데이션 모델 내부의 설명 가능성"이 아니며, LLM의 내부 추론은 불투명하게 남고 Semantica는 모델 바깥의 것, 즉 모델에 들어간 컨텍스트, 산출된 결정, 출처, 관련 관계, 적용된 정책, 실행 흔적을 설명한다. 이 한정은 과대 홍보를 피한다는 점에서 신뢰할 만한 서술이다. 또한 "그래프 구축·추론·출처 추적에는 LLM이 필수가 아니다"라고 밝혀(결정적 인프라), LLM 사용은 선택·벤더 중립으로 둔다.

비교표(README "Why Semantica")는 벡터 DB+RAG, 일반 LLM 메모리와의 차이를 제시한다. 회상 방식은 임베딩 유사도 대 토큰 윈도우 대 그래프 순회+시맨틱 검색, 결정 이력은 저장 안 됨 대 일급 질의 객체, 출처는 없음 대 W3C PROV-O, 충돌은 조용히 덮어씀 대 탐지·표시·해결, 시간 여행은 불가 대 시점별 스냅샷 등이다.

## 동작 원리와 아키텍처

### 파이프라인

`ARCHITECTURE.md`와 README의 아키텍처 절을 종합하면 데이터 흐름은 다음과 같다.

```mermaid
flowchart TD
    SRC[소스<br/>파일·웹·DB·Databricks/Snowflake/SAP<br/>스트림(Kafka·Kinesis)·Git·이메일·MCP] --> ING[ingest]
    ING --> PRS[parse → normalize → split<br/>엔티티·관계·온톨로지 인식 청킹]
    PRS --> EXT[semantic_extract<br/>NER · 관계 · 이벤트 · triplet · 공참조]
    EXT --> CFT[conflicts<br/>충돌 탐지/해결]
    CFT --> DDP[deduplication<br/>블로킹+시맨틱 중복 제거]
    DDP --> KG[kg: GraphBuilder<br/>시계열(bi-temporal) 사실]
    KG --> L{지능 계층}
    L --> ONT[ontology<br/>OWL·SHACL·SKOS]
    L --> RSN[reasoning<br/>Rete·Datalog·SPARQL·abductive]
    L --> PRV[provenance<br/>PROV-O]
    L --> CTX[context<br/>ContextGraph·Decision·Policy]
    ONT & RSN & PRV & CTX --> ST[저장<br/>벡터(FAISS·Qdrant·Weaviate·Milvus·Pinecone·pgvector)<br/>LPG(Neo4j·FalkorDB·AGE·Neptune)<br/>RDF(Oxigraph·Blazegraph·Jena·RDF4J)]
    ST --> OUT[export · visualize · REST · MCP · CLI · Explorer]
```

모듈은 `semantica/` 아래 `ingest`, `parse`, `normalize`, `split`, `semantic_extract`, `conflicts`, `deduplication`, `kg`, `ontology`, `reasoning`, `provenance`, `context`, `vector_store`, `graph_store`, `triplet_store`, `embeddings`, `llms`, `pipeline`, `export`, `visualization`, `change_management`, `evals`, `explorer`, `mcp_server`, `server.py`, `cli.py`로 나뉘고, 각각 독립 import가 가능하다고 README가 설명한다. 소스 파일은 약 400개, 테스트 파일은 약 460개다(디렉터리 계수).

### Context Graph와 Decision Intelligence

중심 객체 `ContextGraph`(`semantica/context/context_graph.py`, 한 파일이 4,000줄을 넘는 큰 클래스)는 노드·엣지에 타입과 속성을 붙이고 BFS 이웃 탐색(`get_neighbors(hops=2)`)과 시점 스냅샷(`state_at("2024-01-01")`)을 제공한다. 영속화는 `save_to_file(path, format="json" | "markdown")`처럼 파일 기반이며, 스레드 락(`self._lock`)으로 보호되는 인메모리 구조라는 점을 코드에서 확인했다. 대규모 영속 저장은 별도 `graph_store`(Neo4j 등)에 맡기는 구성이다.

결정(Decision)은 "로그 한 줄"이 아니라 그래프 노드다. `record_decision(category, scenario, reasoning, outcome, confidence, metadata)`로 기록하고 `add_causal_relationship(a, b, relationship_type="CAUSED" | "INFLUENCED" | "PRECEDENT_FOR")`로 인과 연결을 만든다. 이후 `find_similar_decisions`(선례 검색), `trace_decision_chain`(인과 조상 추적), `analyze_decision_impact`(하류 영향), `check_decision_rules`(정책 게이트), `get_decision_insights`를 쓴다. README의 대출 심사 예시는 신청 → 심사 → 금리 결정이 CAUSED/INFLUENCED로 이어지는 사슬을 만들고 `trace_decision_chain(rate_id)`로 거슬러 올라간다. 감사용 내보내기는 `ProvenanceManager(storage_path="./audit.db")`로 엔티티 출처를 추적하고 `RDFExporter().export(kg, "audit_trail.ttl", format="turtle")`로 PROV-O Turtle을 만든다.

### 추출: LLM은 선택, 기본은 spaCy

`semantic_extract`의 NER은 `method` 인자로 `pattern`, `regex`, `rules`, `ml`(spaCy, **기본값**), `huggingface`, `llm`을 고르고 여러 방법을 `method=["llm","ml"], merge_strategy="consensus", min_votes=2`처럼 조합해 합의로 병합할 수도 있다(소스 docstring). 즉 "LLM 없이도 동작"한다는 말은 영어 spaCy 모델(예시가 `en_core_web_sm`)이나 규칙 기반에 기댄 구성에 해당한다. 한국어 추출은 spaCy 한국어 모델이나 LLM 방식을 별도로 붙여야 하며, 이번에 한국어 품질은 확인하지 못했다. v0.7.0에서는 `SchemaValidator`(추출 결과를 도메인 온톨로지에 대해 검사)와 `bootstrap_schema`(추출 데이터에서 초안 온톨로지 유도)가 추가됐다.

### 추론과 신뢰 계층

`semantica/reasoning/`에는 `rete_engine`, `datalog_reasoner`, `deductive_reasoner`, `abductive_reasoner`, `sparql_reasoner`, `graph_reasoner`, `temporal_reasoning`, `explanation_generator`, `truth_maintenance` 계열이 있다. v0.7.0 릴리스 노트에 따르면 `TruthMaintenanceSession`이 비재귀 규칙에 대한 사실 지지와 철회를 추적하고, `ContextRetriever`가 활성/지지되는 사실만 필터링해 컨텍스트를 줄 수 있으며, 그래프 사실에 코로보레이션 기반 신뢰 등급(quarantine/bronze/silver/gold)을 붙인다. `SPARQLReasoner.execute_query`는 이전의 no-op에서 실제 triplet store 또는 in-memory `rdflib.Graph` 질의로 바뀌었다(버전 노트 기재). 이 설명은 "이전 버전에서는 아무 일도 안 하던 함수가 있었다"는 뜻이기도 해서, 버전별 완성도 편차가 있었다는 간접 증거로 읽을 수 있다.

### 검색(GraphRAG) 기능

v0.7.0의 계층적 커뮤니티 GraphRAG는 다단계 Louvain/Leiden 탐지, LLM 요약 커뮤니티 리포트, 글로벌 Map-Reduce와 DRIFT 하이브리드 검색(`ContextRetriever(mode="global"|"drift"|"hybrid")`, CLI `semantica kg global/drift`)을 추가했다. 즉 검색 능력은 최근에 붙은 기능이고, 벡터 저장소는 FAISS/Qdrant/Weaviate/Milvus/Pinecone/pgvector를 하이브리드·필터 검색과 함께 지원한다고 README가 밝힌다. 검색 품질 수치(정확도, 지연)는 README에 없다. 유일한 성능 표는 v0.5.0 기준 11.8만 노드 그래프에서 노드 검색 24ms → 0.004ms(6,000배) 등 내부 최적화 전후 비교이며, 저자도 "자동화된 테스트가 아니라 CHANGELOG에 기록된 과거 측정"이라고 적었다.

## 설치와 사용법

```bash
pip install semantica                 # 경량 코어(직접 의존성 22개, v0.7.0에서 44→22로 축소)
pip install "semantica[all]"          # 구버전식 풀 번들
pip install "semantica[graph-neo4j,vectorstore-faiss,nlp-spacy,documents]"   # 필요한 extra만
semantica doctor                      # 설치 점검
python -m semantica.mcp_server        # MCP 서버 (또는 semantica-mcp)
python -m semantica.server            # REST 서버 (포트 8000)
```

```python
from semantica.context import ContextGraph, AgentContext
from semantica.vector_store import VectorStore

graph = ContextGraph(advanced_analytics=True)
graph.add_node("acme_corp", "Organization", name="Acme Corp")
graph.add_node("contract_001", "Contract", value=2_400_000, currency="USD")
graph.add_edge("acme_corp", "contract_001", edge_type="party_to", signed="2024-01-15")

d = graph.record_decision(category="vendor_selection",
                          scenario="HIPAA 워크로드용 클라우드 선택",
                          reasoning="BAA 제공, 기존 팀 역량", outcome="selected_aws", confidence=0.93)
print(graph.trace_decision_chain(d))
snapshot = graph.state_at("2024-01-01")

ctx = AgentContext(vector_store=VectorStore(backend="faiss"), knowledge_graph=graph)
ctx.store("Alice approved the Acme renewal in Q1 2024", conversation_id="conv_001")
print(ctx.retrieve("who approved the Acme contract?"))
```

(README 예시를 줄여 옮긴 것이며 직접 실행하지는 않았다.) MCP 설정은 `{"mcpServers": {"semantica": {"command": "python", "args": ["-m", "semantica.mcp_server"]}}}` 형태이고 노출 도구는 `extract_entities`, `extract_relations`, `record_decision`, `query_decisions`, `find_precedents`, `get_causal_chain`, `add_entity`, `add_relationship`, `run_reasoning`, `get_graph_analytics`, `export_graph`, `get_graph_summary`, `query_graph`, `update_node`, `delete_node`(README 표 기준 15개; v0.7.0에서 `store_document`/`retrieve_context`/`update_document`/`remove_document`가 추가). CLI 명령 그룹은 `ingest`, `parse`, `extract`, `kg`, `reason`, `decision`, `temporal`, `provenance`, `ontology`, `embed`, `deduplicate`, `validate`, `export`, `visualize`, `pipeline`, `server`, `explorer`, `mcp`, `doctor`, `shell`, `init`, `watch`이다.

## 디렉터리·코드 구조에서 확인한 것

- `semantica/`: 위에 나열한 모듈. `context/`에는 `context_graph`, `agent_context`, `agent_memory`, `decision_recorder`, `causal_analyzer`, `policy_engine`, `global_retriever`, `drift_search`, `truth_maintenance_filter`, `erasure`(삭제/잊혀질 권리 관련으로 보이는 모듈; 내용은 열지 않음), `tiers`가 있다. `provenance/`는 `manager`, `storage`(인메모리와 SQLite 영속 백엔드), `integrity`, `schemas`를 둔다.
- `semantica_mcp/mcp/`: tools, resources, session, schemas, server를 가진 별도 MCP 패키지 구현. 동시에 `semantica/mcp_server/`도 있어 MCP 진입점이 두 군데다(둘의 관계는 확인하지 못함).
- `explorer/`: React 19 + Sigma.js 기반 "Knowledge Explorer" 웹 UI. 백엔드 `semantica/explorer/`의 FastAPI 라우터는 `X-API-Key` 헤더 검증(`hmac.compare_digest`)을 쓰며, `SEMANTICA_API_KEY`가 없으면 503으로 거부하고 `SEMANTICA_ALLOW_ANONYMOUS=true`일 때만 익명 접근을 허용한다(코드 확인). 즉 fail-closed 기본값이다.
- `integrations/`: agno, crewai, google_adk, langchain, open_ontologies, openclaw. `plugins/`: Claude Code, Cursor, Codex, Windsurf, Cline, Continue, VS Code, OpenClaw, pi용 번들(스킬 17종 안팎, 에이전트 `kg-assistant`/`decision-advisor`/`explainability`). `cookbook/`(Jupyter), `deploy/`(AWS, GCP, Azure, Fly.io, Railway, Render, Kubernetes, Helm 설정), `Dockerfile`, `docker-compose*.yml`.
- 루트의 `GROWTH.md`는 개발 코드가 아니라 성장·배포 플레이북이다. "North star: 실제로 쓰는 개발자 1만 명", "설치 수를 부풀리는 가짜 CI 금지" 같은 지침이 적혀 있다. 프로젝트가 홍보와 배포(Colab 노트북, Docker 이미지, 블로그 등)에 의도적으로 투자하는 구조임을 보여 주는 사실이다.

## 비교 대상

- **벡터 DB + 일반 RAG**: 가장 단순하고 빠르다. Semantica는 그 위에 구조와 설명 가능성을 얹지만 복잡도와 운영 부담이 크다.
- **[[ragu]]**: 텍스트 → 그래프 → 검색 품질에 집중하는 GraphRAG 엔진. 논문에서 벤치마크로 평가했다. Semantica는 결정 기록·추론·출처·거버넌스가 중심이고 검색 품질 평가는 공개 자료에 없다. 같은 "그래프"를 쓰지만 목적이 다르다.
- **[[graphify]]**: 코드·문서를 NetworkX 그래프로 만들어 코딩 에이전트의 탐색을 돕는다. 개발 보조용이며 감사 계층은 없다.
- **Microsoft GraphRAG, Neo4j GraphRAG 등**: 이번에 직접 비교하지 않았다. Semantica의 차별점은 README상 W3C 표준(PROV-O/OWL/SHACL/SKOS/SPARQL)과 결정 객체화이며 실사용 비교 근거는 확인 못함.
- **에이전트 메모리 제품(Mem0, Zep 등)**: `AgentContext`/`AgentMemory`가 같은 영역을 겨냥하지만 비교 실험은 하지 않았다.
- **[[pageindex]]**: 문서 단위 트리 탐색. 감사·출처가 아니라 검색 방식 자체가 다르다.

## 장단점, 한계, 성숙도

장점: 표준(W3C) 기반 출처·온톨로지·추론을 한 패키지에서 다룬다. 결정 기록과 정책 게이트라는 관점이 에이전트 감사에 직접적으로 쓸모 있다. Explorer가 fail-closed 인증이다. 플러그인·MCP·REST·CLI가 모두 있어 붙이기 쉽다. MIT. Extra로 의존성을 쪼개 코어가 가볍다.

한계: (1) 범위가 지나치게 넓다. 이 정도 범위(수집, 파싱, 추출, 추론, 온톨로지, 시각화, 17개 편집기 플러그인)를 1~2년 된 프로젝트가 균일한 품질로 유지하는 것은 어렵다. v0.7.0 노트에 "40개 이상의 정합성 버그 수정(인메모리 벡터 ID 재사용으로 live 벡터 손상, CLI가 존재하지 않는 API 호출 등)"이 나올 정도다. (2) 버전이 0.x이고 v0.7.0이 breaking change를 포함한다(`Entity.confidence`가 `Optional[float]`로, `PolicyEngine.check_compliance`가 `False` 대신 `ProcessingError`를 던짐, `dev` extra 제거, `crewai` extra 제거). (3) 문서 불일치 흔적: `SECURITY.md`의 지원 버전 표가 0.1.0~0.2.3만 나열하고(현재 0.7.0) 오래 갱신되지 않았다. (4) 한국어 추출 품질과 검색 품질 수치는 확인하지 못했다. 기본 NER은 영어 spaCy 계열이다. (5) `ContextGraph`가 인메모리+파일 저장이라 프로덕션 규모에는 외부 그래프 저장소 구성이 필수다. (6) 오픈 이슈+PR 124건이며 최근 이슈에는 LLM 관계 추출이 `Relation.context`에 근거 문장이 아닌 입력 전체를 넣는 문제(#1855), `SemanticaKGTool._extract_relations`가 엔티티를 넘기지 않아 항상 빈 결과를 반환하는 문제(#1849) 등 기본 기능의 정확성 버그가 보인다. 이슈 제목 확인이며 재현하지 않았다.

성숙도 사실: Stars 13,592, Forks 1,552, MIT, 생성 2025-06-25, 마지막 push 2026-09-30, 최신 릴리스 v0.7.0(2026-09-22), 직전 v0.6.8(2026-09-05)과 v0.6.7(2026-08-28)로 거의 주 단위 릴리스. OpenSSF Scorecard 배지, 설치 매트릭스 CI(Ubuntu/macOS/Windows, Python 3.10~3.13 주간 검증)를 갖췄다(README 기재, 확인은 하지 않음). Python 3.14는 아직 미지원이라고 명시한다.

## 보안·라이선스·운영 리스크

- **API 서버 인증**: 위처럼 Explorer API는 키 없으면 거부한다. 다만 REST(`python -m semantica.server`)의 모든 엔드포인트가 같은 보호를 받는지는 전수 확인하지 못했다(`server.py`가 `require_auth`를 import하는 것까지만 확인). 외부 노출 전에 라우터별 의존성을 점검해야 한다.
- **커넥터 자격증명**: Databricks 토큰, Snowflake 비밀번호/키, SAP OAuth 등을 코드/환경변수로 받는다. v0.7.0 노트가 "Neptune 자격증명이 로그에 남는 문제를 수정"했다고 밝힌다. 자격증명 로깅 이력이 있으니 로그 레벨과 마스킹을 점검하고 비밀은 시크릿 매니저로 관리한다.
- **공급망**: v0.7.0이 `crewai` extra를 제거해 `chromadb`/`json-repair`의 미패치 CVE를 피했다고 노트에 적혀 있다. 의존성이 광범위하므로(`[all]`) 필요한 extra만 설치하고 `osv-scanner.toml`이 있는 것처럼 스캔을 CI에 포함한다.
- **개인정보·삭제권**: `context/erasure.py`가 존재하나 동작은 확인하지 못했다. 그래프·벡터·출처 저장소에 흩어진 개인정보를 삭제하는 일관성(오픈 항목 #1852가 "erasure 시 삭제된 벡터 ID를 VectorStore facade 미러에서 제거"를 다룬다)이 완전한지 별도 검증이 필요하다.
- **LLM 데이터 반출**: LLM 기반 추출/요약을 쓰면 문서가 외부 API로 간다. 결정적 모드(spaCy/규칙)나 사내 호스팅 모델을 쓰도록 구성한다.
- **엔터프라이즈 분리**: README의 "Enterprise" 절은 온프레미스·SLA·전문 서비스를 별도 상품으로 안내한다. 오픈소스 범위와 유료 범위의 경계는 앞으로 변할 수 있다.
- **프로젝트 지속성**: 거의 주 단위로 릴리스하는 0.x 프로젝트라 API 변동이 크다. 도입한다면 버전을 고정하고 필요한 모듈만 얇은 어댑터 뒤에서 쓰는 방식이 안전하다.

## 관련 노트

[[graphify]] [[ragu]] [[pageindex]] [[mongodb-crewai-ecommerce-agents]] [[cerebras-knowledge-base-pgvector-rrf-mcp]]

## 출처

- https://github.com/semantica-agi/semantica (README 전문, `ARCHITECTURE.md`, `SECURITY.md`, `GROWTH.md`, `pyproject.toml`, `semantica/context/context_graph.py`, `semantica/semantic_extract/*.py`, `semantica/explorer/dependencies.py`, `semantica/provenance/storage.py`, 디렉터리 구조; 2026-10-01 clone 후 열람)
- GitHub REST API: repos 메타데이터, releases, 오픈 이슈 목록(2026-10-01)
- 열람하지 않은 것: docs.getsemantica.ai 문서 사이트, getsemantica.ai, `RELEASE_NOTES.md` 전문과 `CHANGELOG.md`(README의 v0.7.0 요약만 확인), Knowledge Explorer 실행, 한국어/대규모 성능 실측
