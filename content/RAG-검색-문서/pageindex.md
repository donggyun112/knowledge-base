---
title: PageIndex
source: https://github.com/VectifyAI/PageIndex
type: repo
category: RAG-검색-문서
tags: [research, rag, vectorless, tree-index, reasoning]
researched: 2026-10-01
---
# PageIndex

> [!summary] 한줄요약
> 문서를 chunk로 쪼개 임베딩하는 대신 "제목/섹션 계층 트리 + 노드별 요약 + 페이지 범위"로 색인하고, LLM 에이전트가 트리를 훑어 필요한 페이지만 읽어 오는 vectorless, reasoning-based RAG. 2026년 8월 SDK 개편으로 `pip install pageindex` 하나로 로컬 인덱싱·검색·채팅이 되고, 같은 클라이언트를 PageIndex Cloud에도 붙일 수 있다.

## 배경: 해결하려는 문제

벡터 RAG는 질의와 chunk의 임베딩 유사도(similarity)로 검색한다. PageIndex는 README 첫 문단에서 "유사도는 관련성(relevance)이 아니다"라는 주장으로 출발한다. 금융 보고서, 법률 문서, 규제 공시, 기술 매뉴얼처럼 길고 구조가 있는 전문 문서에서는 (1) 질의와 비슷하게 생겼지만 정작 관련 없는 chunk가 올라오고, (2) 관련 있지만 표현이 다른 부분은 놓치며, (3) chunk 경계가 표, 각주, 참조("위 3.2항 참고")를 끊어 놓는다. 사람은 이런 문서를 목차를 보고 해당 장으로 가서 읽는다. PageIndex는 이 행동을 모사한다. README는 AlphaGo에서 영감을 받았다고 표현하지만, 구현은 트리 탐색을 LLM 에이전트의 도구 호출로 푸는 것이다. AlphaGo식 탐색 알고리즘이 들어 있는 것은 아니다(소스에서 그런 구성요소를 확인하지 못함).

검색 단계는 두 가지다. (1) 문서마다 tree-structure 인덱스를 생성하고, (2) LLM이 그 트리를 에이전트 방식으로 탐색한다. 벡터 DB도, 고정 크기 chunking도 쓰지 않는다. 결과는 "어느 섹션의 어느 페이지에서 가져왔는지"가 명시적 참조로 남기 때문에 추적과 설명이 쉽다는 것이 핵심 주장이다. README의 비교표는 다음과 같다. 인덱스는 벡터 인덱스 대 트리 인덱스, 검색은 의미 유사도 검색 대 트리 위 LLM 추론, 결과는 불투명한 "vibe retrieval" 대 명시적 참조, 컨텍스트는 질의 임베딩뿐 대 대화 이력과 도메인 지식까지 포함.

## 동작 원리와 아키텍처

### 두 개의 인덱싱 경로: flash와 standard(classic)

저장소에는 트리를 만드는 경로가 둘 있다. 2026년 8월에 들어온 `pageindex/flash/`는 LLM 없이 레이아웃 통계(폰트 크기, 굵기, 정렬, 번호 체계, 임베디드 아웃라인/북마크)로 구조를 추출하는 경로이고, 로컬 모드의 기본값이다. flash README에 따르면 "트리 구조 자체는 LLM 없이 만들고, 요약을 붙이고 검색용으로 다듬는 데만 LLM이 필요하다". `page_index_classic.py`는 이전부터 있던 방식으로 LLM에게 목차(TOC)를 찾아 읽게 하고(`toc_detector_single_page`, `toc_extractor`, `toc_transformer`), 목차의 페이지 번호를 실제 물리 페이지와 대조하고(`calculate_page_offset`, `verify_toc`, `fix_incorrect_toc`), 목차가 없는 문서는 LLM이 처음부터 구조를 생성한다(`process_no_toc`, `generate_toc_init`). 큰 노드는 재귀적으로 더 쪼갠다(`process_large_node_recursively`). CLI에서는 `--mode flash|standard`로 고른다(기본 flash).

flash의 결과 스키마는 단순하다. `structure`는 노드의 트리이고 각 노드는 `title`, 4자리 `node_id`, 1-based inclusive `start_index`/`end_index`, `summary`(요약 옵션 시), `key_items`(최적화 시 합쳐진 하위 제목), `nodes`(자식)를 가진다. `toc_source`는 구조의 출처를 `detected`(레이아웃에서 추출), `bookmarks`(임베디드 아웃라인), `hybrid`, `pages`(계층을 못 찾아 페이지마다 노드 하나), `unreadable`(텍스트 없음)로 알려 준다. 페이지 수가 `FLAT_TREE_MAX_NODES`(10)를 넘는데 계층을 못 찾은 flat 트리는 요약·최적화 없이 반환되고 로컬 클라이언트와 CLI는 이를 거부한다. 즉 구조가 없는 문서(스캔본, 구조 없는 텍스트 덩어리)는 이 방식이 실패하도록 명시적으로 설계되어 있다.

### 트리 최적화: 탐색 비용을 줄이는 merge/expand

`tree_optimize.py`는 이 프로젝트에서 가장 이론적인 부분이다. 목표는 "트리를 탐색하는 비용이 불필요하게 크지 않게 하는 것"이고, 비용은 페이지 수로 잰다. 노드 v를 접어 두면(collapsed) 하위 구간 전체를 선형으로 읽어야 하므로 비용 S(v)는 부분트리가 덮는 페이지 수이고, 라우팅(제목·요약·자식 설명을 읽는 것) 비용 R(v)는 1페이지로 둔다. expand는 "펼쳤을 때 비용 R(v) + max(S_residual(v), max S(자식))이 접었을 때 S(v)보다 작을 때만" 펼치고, merge는 "병합 비용 S(v)가 트리 비용 이하이면(동률은 병합)" 부분트리를 합친다. merge는 결정론적이라 LLM이 필요 없고, expand는 `summary_model`로 하위 절을 제안한다. 합쳐서 사라진 하위 제목은 부모의 `key_items`로 보존해 라우팅 정보가 사라지지 않게 한다. 검색 단위가 페이지이므로 같은 페이지를 덮는 형제 노드들은 구별할 수 없다는 이유로 `merge_same_page()`로 합친다. 이 설계는 "에이전트가 최악의 경우에도 너무 많은 페이지를 읽지 않게 한다"는 비용 모델을 코드와 주석으로 명시했다는 점에서 인상적이다(실제로 검색 품질이 이 최적화로 얼마나 좋아지는지는 확인하지 못함).

### 검색: 에이전트 도구 4개

검색은 벡터 질의가 아니라 LLM 에이전트(OpenAI Agents SDK 기반)가 도구를 호출하는 방식이다. `agent_tools.py`의 읽기 도구는 `browse_documents`, `get_document`, `get_document_structure`, `get_page_content` 네 개이고, 관리 도구는 `remove_document` 하나다. 에이전트는 문서 목록 → 트리 구조 → 의심 구간의 페이지 본문 순으로 읽어 들어가며 답을 만든다. 트리가 너무 크면 `_split_structure`로 예산에 맞게 나누어 준다. 클라이언트는 같은 도구를 OpenAI Agents SDK, Anthropic SDK, Claude Agent SDK(MCP 형태) 어디에든 꽂을 수 있게 `as_openai_tools()`, `as_anthropic_tools()`, `as_claude_mcp()` 어댑터로 노출한다. 대화 이력과 `document_context`/`folder_context` 같은 문맥 주입 함수가 있어, "질의 임베딩 하나만으로 검색한다"는 벡터 RAG와 달리 이전 대화와 도메인 지식을 탐색 판단에 쓸 수 있다는 주장의 구현 지점으로 보인다.

```mermaid
flowchart LR
    P[PDF / Markdown] --> F[flash: 레이아웃 통계로<br/>구조 추출 (LLM 없음)]
    P --> S[standard: LLM이 TOC 탐지·검증·보정]
    F --> T[트리: title / node_id / 페이지 범위]
    S --> T
    T --> O[optimize: merge(결정론) + expand(LLM)]
    O --> Y[노드 요약 생성 (index 모델)]
    Y --> D[(로컬 디렉터리 / Cloud 저장소)]
    Q[질문 + 대화 이력] --> A[chat 모델 에이전트]
    D --> A
    A -- browse / get_document_structure --> D
    A -- get_page_content(페이지 지정) --> D
    A --> R[답변 + 페이지 단위 인용]
```

위 그림은 README, flash README, `agent_tools.py`, `tree_optimize.py`에서 재구성한 것이다.

### 모델 역할 분리

`index=`(색인용)과 `chat=`(검색·답변용) 모델을 따로 지정한다. README의 권고는 "index는 기본 모델이면 충분하다(구조는 LLM 없이 뽑고 요약·다듬기만 하므로), chat은 가능한 한 가장 좋은 모델을 쓰라"는 것이다. 모델 이름은 LiteLLM 형식이어서 `openai` 계열은 그냥 이름을, 다른 공급자는 `anthropic/claude-sonnet-4-6`처럼 `provider/model`로 쓴다(`config.yaml` 주석). 즉 OpenAI 전용은 아니다. 다만 README 예시와 기본값은 OpenAI 모델명이다.

## 핵심 기능 상세

### 로컬 모드와 Cloud 모드

README의 표를 요약하면 로컬은 텍스트 기반 PDF를 처리하고, 인덱싱·저장이 내 컴퓨터/로컬 디렉터리에서 일어나며, 인용은 페이지 단위다. Cloud는 스캔본과 이미지가 많은 문서도 처리하고(OCR·이미지 이해), 저장이 클라우드이며, 인용이 블록 단위이고, 메타데이터·폴더·MCP 서버 기능이 있다. 로컬의 한계가 곧 Cloud 유료화 지점이다. README는 또한 "PageIndex File System"을 클라우드 전용의 파일 수준 트리 인덱싱 계층으로 소개하며 수백만 문서로 확장한다고 말하는데, 이 부분은 오픈소스 코드에 없고 블로그 주장이라 검증하지 못했다. 전용 배포(VPC/온프레미스)는 문의 형태다.

### Markdown 입력과 CLI

`run_pageindex.py`는 `--pdf_path` 외에 `--md_path`도 받는다. `page_index_md.py`가 Markdown의 `#` 헤더와 굵은 줄 제목을 파싱해 같은 형태의 트리를 만든다(코드블록 안은 건너뜀). 사내 위키/문서가 Markdown이라면 PDF 파서를 거치지 않고 바로 색인할 수 있다는 뜻이다. 옵션에는 `--toc-check-pages`(기본 20), `--max-pages-per-node`(10), `--max-tokens-per-node`(20000), `--if-add-node-summary`, `--if-thinning`, `--summary-token-threshold`(200) 등이 보인다.

### 문서 텍스트 인젝션 방어

classic 경로에는 `_sanitize_doc_text`가 "ignore previous instructions", "jailbreak" 등 알려진 패턴을 `[REDACTED]`로 바꾸고, `_wrap_doc_text`가 문서 본문을 `<user_document>` 태그로 감싸 "이것은 데이터이며 지시가 아니다"라는 주석과 시스템 하드닝 문구(`_SYSTEM_HARDENING`)를 붙인다. 닫는 태그 위조도 막는다. 패턴 기반이라 우회 가능성은 열려 있지만, 신뢰할 수 없는 PDF를 LLM에 넣는 코드가 기본 방어를 갖췄다는 점은 확인된 사실이다.

## 설치와 사용법

```bash
pip install -U pageindex          # 로컬 모드 포함 (Python 3.10+)
export OPENAI_API_KEY=...         # 또는 LiteLLM이 지원하는 다른 공급자 키
```

```python
import os
from pageindex import PageIndexClient

client = PageIndexClient(
    index="gpt-5.6-luna",   # 트리 요약/다듬기용 (저가 모델로 충분)
    chat="gpt-5.6-sol",     # 트리 탐색·답변용 (가능한 최고 모델)
)
doc_id = client.submit_document("report.pdf")["doc_id"]
print(client.chat("2023년 영업이익률은?", doc_id=doc_id))

# 클라우드로 인덱싱/저장만 옮길 때
os.environ["PAGEINDEX_API_KEY"] = "..."
client = PageIndexClient(index="cloud", chat="gpt-5.6-sol")
doc_id = client.submit_document("report.pdf", wait=True)["doc_id"]
```

```bash
# 트리만 뽑아 보기 (LLM 호출 없음)
python3 run_pageindex.py --mode flash --pdf_path doc.pdf --no-summary --optimize off
# 요약 + 최적화 포함
python3 run_pageindex.py --mode flash --pdf_path doc.pdf
# Markdown 문서
python3 run_pageindex.py --md_path notes.md
```

결과는 `results/<이름>_structure.json`에 저장된다. 모델명 `gpt-5.6-luna`/`gpt-5.6-sol`은 README의 예시 그대로 옮긴 것이며, 해당 모델의 실제 사양은 확인하지 않았다. 에이전트에 도구만 꽂고 싶다면 `client.as_openai_tools()` 등을 쓴다(상세는 docs.pageindex.ai의 SDK 문서; 이번에 열지 않음).

## 디렉터리·코드 구조에서 확인한 것

- `pageindex/`: `client.py`(약 2,700줄, 로컬/클라우드 공용 클라이언트와 채팅, 인용, 폴더 API), `agent_tools.py`(약 1,800줄, 도구 계약), `local_chat.py`(로컬 채팅 실행), `page_index_classic.py`(LLM 기반 TOC 파이프라인), `page_index_md.py`, `tree_optimize.py`, `local_store.py`/`local_api.py`(로컬 저장), `cloud_api.py`, `mcp_bridge.py`(클라우드 MCP 연결), `integrations/`(OpenAI Agents, Anthropic, Claude Agent SDK).
- `pageindex/flash/`: LLM 없는 구조 추출기. `parser_pdfium_charlevel`(pdfium 문자 단위 파서, 폰트 ToUnicode/cmap 처리), `heading_detection`, `classification`(본문·머리글/바닥글·목차 보일러플레이트 판별), `clustering`, `outline`, `title`, `labels`(캡션), `embedded_toc`.
- 의존성(pyproject): `litellm`, `openai`, `openai-agents`, `mcp`, `PyPDF2`, `pypdfium2`, `sortedcontainers`, `regex`, `pyyaml`, `Pillow`; 선택 extra로 `claude-agent-sdk`, `anthropic`. 벡터 DB/임베딩 라이브러리가 없다는 점이 "vectorless" 주장과 일치한다.
- `cookbook/`: 인용, flash 데모, 멀티모달, 질의 비용, vision RAG 노트북 5종. `tests/`: client/agent_tools/flash 추출/local_chat 등 테스트 파일 10여 개.
- 메타데이터 불일치: `pyproject.toml`의 version은 0.2.10인데 GitHub 최신 릴리스 태그는 v0.2.20이다. `_version.py`는 설치된 패키지 메타데이터를 읽는 방식이라 이유는 확인하지 못했다. 릴리스 주기는 매우 빠르다(v0.2.18 9/16, v0.2.19 9/21, v0.2.20 9/28).

## 벤치마크: 주장과 확인 범위

README의 수치는 모두 자체 측정이다. 로컬 인덱싱 비용은 index 모델로 `gpt-5.6-luna`를 쓸 때 페이지당 약 \$0.001, 9~1,098페이지 문서 9개가 약 13초~4.5분에 끝났다고 한다. flash README의 표는 같은 9개 문서의 입력/출력 토큰을 제시한다(예: 1,098페이지 책은 입력 약 159만, 출력 약 65만 토큰). 질의 쪽은 네이티브 PDF 입력(문서 전체를 모델에 전달) 대비 52페이지에서 2.1배, 420페이지에서 16.6배 비싸고 805페이지에서는 컨텍스트에 들어가지 않는다는 그래프가 있다. FinanceBench 98.7% 정확도(대조: 벡터 RAG 50%로 그림에 표기)는 별도 저장소 `Mafin2.5-FinanceBench`/블로그에서 나온 결과이고 이번에 그 저장소는 열지 않았다. 그리고 2026-08 SDK 개편 이후 기준 벤치마크인 `PageIndex-OSS-Benchmark`는 MMLongBench-Doc-V2에서 뽑은 34개 PDF(1,945페이지)의 62개 사실 조회 질문으로 측정하며, 모델마다 reasoning effort 사다리를 그린 정확도-비용 그래프만 README에 이미지로 있어 수치를 읽지 못했다.

주의할 점이 있다. FinanceBench 98.7%는 특화 구성(Mafin 2.5)의 결과일 수 있고, 현재 오픈소스 로컬 모드의 flash 인덱서가 같은 성능을 낸다는 보장이 아니다. 실제로 이슈 #518("Pageindex Flash를 FinanceBench에 써 보니 coverage 50%")에서 일부 파일의 초기 페이지가 추출되지 않았다는 보고가 있다(이슈 본문 일부만 확인, 재현 안 함).

## 비교 대상

- **벡터 RAG(청크 임베딩 + 하이브리드 검색)**: 코퍼스가 크고 질문이 다양할 때 지연과 비용이 낮고 확장이 쉽다. PageIndex는 문서 단위 트리 위에서 LLM이 여러 번 호출되므로 질의당 지연·비용이 크지만, 구조가 뚜렷한 장문 한 건에서는 정확하고 설명 가능하다. 사내 [[cerebras-knowledge-base-pgvector-rrf-mcp]]의 pgvector+RRF 구성이 전자의 예다.
- **GraphRAG 계열([[ragu]], [[semantica]], [[graphify]])**: 엔티티 관계 그래프를 만들어 코퍼스 전체에 걸친 질문을 푼다. PageIndex는 문서 내부의 위계 구조를 이용할 뿐 문서 간 엔티티 연결은 만들지 않는다. 푸는 질문 유형이 다르다.
- **긴 컨텍스트 모델에 통째로 입력**: README 자체가 비교 대상으로 삼아 질의 비용 차이를 보인다. 문서가 컨텍스트에 들어가는 규모(수십 페이지)에서는 단순함이 이길 수 있다.
- **구조 파서([[opendataloader-pdf]] 등)**: 파서는 "읽기 좋은 Markdown/JSON"을 만들고 PageIndex는 "탐색 가능한 트리"를 만든다. 보완 관계로 쓸 여지가 있으나(파서의 heading hierarchy → PageIndex의 Markdown 입력) 직접 연동은 확인하지 못했다.

## 장단점, 한계, 성숙도

장점: 청킹 설계와 임베딩 모델 선택, 벡터 DB 운영이 필요 없어 구성이 단순하다. 답의 근거가 "문서명/섹션/페이지"로 남는다. 인덱싱 비용이 문서당 한 번이고 이후 질의에서 재사용된다(README 주장). 도구 계약이 명확해 OpenAI/Anthropic/Claude 에이전트에 모두 꽂을 수 있다.

한계: (1) 질의마다 LLM 에이전트가 여러 번 호출되어 지연과 비용이 크다. (2) 구조가 없는 문서(스캔본 원문, 헤더 없는 텍스트)는 flash가 실패하도록 설계되어 있고, 스캔·이미지 문서는 Cloud 전용 기능이다. (3) 로컬 인용은 페이지 단위다. (4) 코퍼스 규모 확장은 클라우드 전용 File System에 의존하고 오픈소스 쪽은 문서 단위 도구 중심이다(`browse_documents`로 목록을 훑는 방식이 수천 문서에서 어떻게 동작하는지 확인하지 못함). (5) 한국어 문서의 제목 검출 정확도, 번호 체계("제1장", "가.", "1)"), 한글 폰트 ToUnicode 처리 등은 검증하지 못했다. (6) 로컬 MCP 서버가 없다. 이슈 #540이 "로컬 라이브러리를 Claude Desktop/Cursor 같은 외부 MCP 클라이언트에 노출하는 독립 서버" 기능 요청이고, README 표도 MCP를 Cloud 전용으로 표시한다.

성숙도 사실: GitHub Stars 38,212, Forks 3,316, 오픈 이슈+PR 109건, MIT, 생성 2025-04-01, 마지막 push 2026-09-30, 최신 릴리스 v0.2.20(2026-09-28), PyPI classifier는 "Development Status :: 3 - Alpha". 별 수에 비해 버전이 0.2.x인 점과 README의 상업 서비스 안내(Cloud, App, Contact)를 함께 보면, 오픈소스 로컬 SDK가 상용 Cloud의 퍼널 역할도 한다고 읽을 수 있다(해석이며 근거는 README 구성).

## 보안·라이선스·운영 리스크

- **데이터 반출**: 로컬 모드라도 색인(요약)과 질의(페이지 본문)마다 선택한 LLM API로 문서 내용이 전송된다. 사내 기밀 문서에는 사내 호스팅 모델/LiteLLM 게이트웨이 사용이 전제되어야 한다. Cloud 모드는 문서 자체가 PageIndex 서버에 올라간다.
- **프롬프트 인젝션**: 위에서 본 패턴 치환과 데이터 래핑은 기본 방어일 뿐이다. 도구 호출 에이전트는 인젝션 시 `remove_document` 같은 관리 도구가 악용될 수 있으므로(`include_management` 기본값 false라는 점은 긍정적) 읽기 도구만 노출하는 것이 안전하다.
- **라이선스**: MIT로 상용 사용에 부담이 적다. 클라우드 서비스는 별도 약관이다.
- **의존성**: litellm을 정확히 `1.97.0`으로 고정한 requirements.txt와 `>=1.97.0` pyproject가 공존한다. 핵심 의존성(litellm, openai-agents, mcp)이 모두 빠르게 바뀌는 패키지이므로 사내 도입 시 버전 고정과 의존성 취약점 스캔을 권한다.
- **비용 통제**: 에이전트가 트리를 깊게 탐색하면 질의당 토큰이 예측하기 어렵다. 최대 턴 수와 모델 등급, 캐시 설정을 명시하고 질의당 비용 로그를 남겨야 한다.

## 관련 노트

[[ragu]] [[graphify]] [[ragas]] [[opendataloader-pdf]] [[semantica]] [[cerebras-knowledge-base-pgvector-rrf-mcp]]

## 출처

- https://github.com/VectifyAI/PageIndex (README 전문, `pyproject.toml`, `requirements.txt`, `pageindex/config.yaml`, `pageindex/flash/README.md`, `pageindex/tree_optimize.py`, `pageindex/agent_tools.py`, `pageindex/page_index_classic.py`, `pageindex/page_index_md.py`, `run_pageindex.py`, 디렉터리 구조; 2026-10-01 clone 후 열람)
- GitHub REST API: repos 메타데이터, releases, 오픈 이슈 목록 및 이슈 #518, #540 본문 일부(2026-10-01 조회)
- 열람하지 않은 것: docs.pageindex.ai, PageIndex-OSS-Benchmark 저장소와 Mafin2.5-FinanceBench 저장소, 블로그(pageindex.ai/blog/pageindex-intro 시도했으나 본문 없음), 이미지 그래프의 수치, 한국어 문서 실측
