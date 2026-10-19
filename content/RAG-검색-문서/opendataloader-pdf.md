---
title: OpenDataLoader PDF
source: https://github.com/opendataloader-project/opendataloader-pdf
type: repo
category: RAG-검색-문서
tags: [research, pdf-parsing, ocr, accessibility, rag]
researched: 2026-10-01
---
# OpenDataLoader PDF

> [!summary] 한줄요약
> Hancom 주도의 Apache-2.0 PDF 파서. 규칙 기반 Java 코어와 로컬 AI 백엔드를 결합해 문서 구조를 추출하고, Tagged PDF 자동 변환도 제공한다.

Java 코어는 veraPDF·PDFBox 기반으로 Markdown/JSON(bbox 포함)/HTML을 만든다. 복잡한 표·스캔본·수식·차트만 로컬 AI 백엔드 **Docling**으로 넘기는 hybrid 구조다.

같은 엔진으로 태그 없는 PDF를 Tagged PDF로 바꾸는 접근성 기능까지 제공한다.

## 배경: 해결하려는 문제

RAG 파이프라인에서 PDF는 가장 흔한 입력이면서 가장 자주 망가지는 입력이다. 텍스트 레이어만 긁으면 다단 레이아웃의 읽기 순서가 뒤섞이고, 표는 행/열 구조를 잃고, 스캔본은 아예 텍스트가 없다. 인용(citation)을 달고 싶어도 원문 어디에서 가져왔는지 좌표가 남아 있지 않다.

이 프로젝트는 README에서 이 문제를 세 줄로 요약한다.

1. **구조 손실:** 파싱 중 읽기 순서, 표, 좌표를 잃는다.
2. **복잡한 요소의 해석:** 복잡한 표·스캔·수식·차트에는 AI 수준의 이해가 필요하다.
3. **접근성 작업 비용:** 접근성 규제(EAA, ADA/Section 508, 한국 디지털포용법)가 요구하는 Tagged PDF를 수작업으로 만들면 문서당 50~200달러가 든다.

흥미로운 점은 두 문제를 한 코드베이스로 푼다는 것이다. 레이아웃 분석(제목, 문단, 목록, 표, 읽기 순서)을 한 번 수행하면, 그 결과를 JSON/Markdown으로 내보내 RAG에 쓸 수도 있고 PDF 구조 태그로 되써서 스크린리더용 Tagged PDF로 만들 수도 있다.

이런 이중 목적은 저장소 구조에도 드러나서, Java 코어 의존성에 PDF/UA 검증 쪽 라이브러리인 veraPDF(`validation-model`, `wcag-validation`, `wcag-algorithms`)가 들어 있다.

코드 주석의 저작권 표기는 "Copyright 2025-2026 Hancom Inc."이고, PyPI 작성자 메일도 `open.dataloader@hancom.com`이다. 한컴이 사실상 스폰서인 프로젝트다(저장소 파일 기준 사실, 내부 사정은 확인 못함).

## 동작 원리와 아키텍처

### 처리 흐름

핵심 설계는 "빠른 결정론적 경로(local) + 필요한 페이지만 AI 경로(hybrid)"다. Java 코어가 모든 PDF를 먼저 받아 콘텐츠 필터 → 텍스트/라인 처리 → 표 검출 → 제목/목록/문단 조립 → 읽기 순서 정렬 순으로 처리하고, hybrid 모드에서는 중간에 페이지별 triage가 끼어든다.

triage 결과가 "BACKEND"인 페이지만 HTTP로 Python 서버(FastAPI + Docling)에 보내고, 응답을 다시 내부 스키마로 변환해 로컬 결과와 합친다.

```mermaid
flowchart TD
    A[PDF 입력] --> B[Java 코어: PDFBox + veraPDF 파서]
    B --> C[ContentFilterProcessor<br/>숨김 텍스트·페이지 밖·tiny 텍스트 제거]
    C --> D{hybrid 모드?}
    D -- 아니오 --> E[로컬 처리<br/>표(border/cluster)·제목·목록·문단]
    D -- 예 --> F[TriageProcessor<br/>페이지별 JAVA / BACKEND 분류]
    F -- 단순 페이지 --> E
    F -- 복잡 페이지 --> G[DoclingFastServerClient<br/>HTTP → opendataloader-pdf-hybrid]
    G --> H[DoclingSchemaTransformer<br/>백엔드 응답을 내부 스키마로]
    E --> I[XYCutPlusPlusSorter<br/>읽기 순서]
    H --> I
    I --> J{출력 형식}
    J --> K[JSON(bbox)]
    J --> L[Markdown / HTML / Text]
    J --> M[annotated PDF]
    J --> N[tagged-pdf<br/>AutoTagger]
```

이 다이어그램은 README 설명과 `java/opendataloader-pdf-core/src/main/java/org/opendataloader/pdf/` 아래 패키지 구성(`processors`, `processors/readingorder`, `hybrid`, `autotagging`, `markdown`, `html`, `json`, `api`, `utils`)에서 재구성한 것이다. 각 단계의 세부 순서는 소스 전체를 추적하지 않았기 때문에 개념도로 봐야 한다.

### Triage의 성격

`TriageProcessor`의 주석에 따르면 전략은 "보수적"이다. 표를 놓치는 것(false negative)이 더 나쁘므로, 단순한 페이지를 백엔드로 보내는 것(false positive)은 감수한다.

판단 신호는 라인 객체 비율(`DEFAULT_LINE_RATIO_THRESHOLD = 0.3`), 정렬된 짧은 라인 그룹 수(기본 5, 주석에 "3에서 5로 올렸더니 정상 문서 10건의 오탐이 사라졌다"는 실험 메모가 있음), 격자 패턴, 벡터 그래픽 라인 수(표 테두리 후보 8개 이상) 같은 휴리스틱이다.

즉 "AI가 필요한 페이지"를 AI가 고르는 것이 아니라 기하학적 단서로 고른다.

`--hybrid-mode full`을 주면 triage를 건너뛰고 모든 페이지를 백엔드로 보낸다. 수식·그림 설명 같은 enrichment는 `full` 모드가 필요하다고 README가 명시한다.

### 읽기 순서: XY-Cut++

다단 문서의 순서는 `XYCutPlusPlusSorter`가 담당한다. 고전적인 XY-Cut(공백 투영으로 재귀 분할)을 확장한 알고리즘으로, 소스에는 교차 레이아웃(cross-layout) 판정을 위한 최소 겹침 수 상수와 밀도 임계값 인자(`beta`, `densityThreshold`)가 보인다. 옵션 `--reading-order`는 `off` 또는 `xycut`(기본)이다. 알고리즘의 정확한 수식이나 논문 대응은 확인하지 못했다.

### 로컬 AI 백엔드

`opendataloader-pdf-hybrid`는 `python/opendataloader-pdf/src/opendataloader_pdf/hybrid_server.py`의 엔트리 포인트로, `pip install "opendataloader-pdf[hybrid]"`로 설치되는 extra에 `docling[easyocr]>=2.126.0,<3`, `fastapi`, `uvicorn`, `python-multipart`가 들어 있다. 즉 hybrid의 "AI"는 Docling(레이아웃 모델 + TableFormer + EasyOCR 등)이며, 이 프로젝트의 독자 모델이 아니다.

README의 벤치마크 표에서도 docling이 별도 경쟁자로 나온다는 점을 고려하면, hybrid 성능의 상당 부분은 Docling 위에 로컬 Java 파이프라인(읽기 순서, bbox, triage, 후처리)을 얹은 결과로 해석하는 것이 정확하다.

## 핵심 기능 상세

### 출력 형식과 JSON 스키마

`--format`에는 `json`(기본), `text`, `html`, `pdf`(annotated), `markdown`, `tagged-pdf`를 쉼표로 조합해 줄 수 있다. JSON의 각 요소는 `type`(heading, paragraph, table, list, image, caption, formula), `id`, `page number`(1-based), `bounding box`(`[left, bottom, right, top]`, PDF point 단위), `heading level`, `font`, `font size`, `content` 등을 가진다.

RAG 관점에서 중요한 것은 모든 요소에 좌표가 있다는 점이다. 답변의 근거 chunk를 원본 PDF 위에 하이라이트하는 "click to source" UI를 만들 수 있다.

그림은 `alt`와 `alt_source`(`original` / `ai-generated` / `missing`)를 가지며, 수식은 LaTeX 문자열로 나온다.

### 옵션 체계

저장소 루트의 `options.json`이 CLI 옵션의 단일 원천이고, `scripts/generate-options.mjs`가 Python/Node 래퍼 코드(`cli_options_generated.py`, `convert_generated.py`)를 생성한다. 확인한 주요 옵션은 다음과 같다.

| 옵션 | 의미 |
|---|---|
| `--format` | json,text,html,pdf,markdown,tagged-pdf 조합 |
| `--pages "1,3,5-7"` | 페이지 범위 |
| `--table-method default|cluster` | 테두리 기반 vs 테두리+클러스터 표 검출 |
| `--reading-order off|xycut` | 읽기 순서 알고리즘 |
| `--use-struct-tree` | PDF 자체의 구조 트리(Tagged PDF)를 그대로 사용 |
| `--include-header-footer` | 머리글/바닥글 포함(기본은 제외) |
| `--content-safety-off all|hidden-text|off-page|tiny|hidden-ocg|background` | 안전 필터 해제 |
| `--sanitize` | 이메일·전화·IP·카드번호·URL을 placeholder로 치환 |
| `--image-output off|embedded|external`, `--image-format png|jpeg` | 이미지 처리 |
| `--hybrid docling-fast`, `--hybrid-mode auto|full`, `--hybrid-url`, `--hybrid-timeout`, `--hybrid-chunk-size`, `--hybrid-fallback` | hybrid 제어 |
| `--threads N` | 페이지 단위 병렬(기본 1, 1 초과는 experimental) |
| `--detect-strikethrough` | 취소선을 `~~`/`<del>`로(experimental) |
| `--markdown-with-html` | 병합 셀 표 등을 HTML 태그로 표현 |

주의할 운영 포인트는 README가 반복 강조하는 "각 `convert()` 호출은 JVM 프로세스를 띄우므로, 파일을 한 번에 배치로 넘겨라"이다. 호출을 루프로 돌리면 JVM 기동 비용이 파일 수만큼 든다.

### 스캔본 OCR과 한국어

OCR은 hybrid 서버를 `--force-ocr`로 띄워 처리한다. 기본 엔진은 EasyOCR이고 `--ocr-lang "ko,en"`처럼 언어를 지정한다. README는 엔진 선택표를 제공하는데, EasyOCR(기본), RapidOCR, Tesseract(CLI, `kor,eng`), tesserocr, Apple Vision(`ocrmac`, macOS 전용, `ko-KR,en-US`), NVIDIA Nemotron OCR(Linux x86_64 + CUDA), `auto`가 있다.

README는 "어떤 엔진도 모든 문서에 최적이 아니니 대표 페이지로 엔진을 비교하라"고 직접 권한다. 엔진마다 서버를 다른 포트로 띄워 같은 파일을 보내 비교하는 절차도 예시로 있다.

한국어 디지털 PDF는 "텍스트 추출이 기본으로 동작"한다고 FAQ에 쓰여 있지만, 한국어 표·스캔본의 실제 정확도 수치는 어디에도 없다(확인 못함).

### 수식·차트·제목 계층

`--enrich-formula`(서버)와 `--hybrid-mode full`(클라이언트)로 LaTeX 수식을 얻는다. `--enrich-picture-description`은 SmolVLM(256M)으로 그림/차트 설명을 생성한다.

README는 비용 모델도 솔직하게 적어 두었다. 비용은 그림의 크기가 아니라 개수에 비례하고, CPU에서는 그림 하나에 1분 넘게 걸릴 수 있으며 변환 요청은 직렬화된다. 외부에 노출되는 서버라면 `--picture-area-threshold 0.05`와 `--max-file-size`를 설정하라는 경고도 있다.

`--heading-hierarchy`는 레이아웃 모델이 깊이 없이 모든 제목을 level 1로 돌려주는 문제를 PDF 아웃라인 → 번호 체계(`1.` → `1.1`) → 시각 스타일 순으로 추론해 보정한다. RAG chunking 시 섹션 경로를 만들 때 직접적으로 유용하다.

### 보안 필터(AI Safety)

문서 안에 숨긴 프롬프트 인젝션을 막기 위해 기본으로 숨김 텍스트(투명, 크기 0 폰트), 페이지 밖 콘텐츠, 의심스러운 보이지 않는 레이어를 걸러낸다. 소스에는 `HiddenTextProcessor`, `ContentFilterProcessor`, `filterTinyText` 등이 있다.

`--sanitize`는 별개의 옵트인 기능으로 `ContentSanitizer`가 정규식 규칙으로 개인정보성 문자열을 치환한다. 이슈 #757("`--sanitize`가 HH:MM:SS 타임스탬프를 IPv6로 오인해 지운다")처럼 정규식 기반 치환은 오탐이 있을 수 있다.

필터가 모든 인젝션을 막는다는 보증은 없으므로, 외부 문서를 LLM에 넣는 경로라면 다른 방어층(프롬프트 격리, 출력 검증)이 여전히 필요하다.

### Tagged PDF 자동 태깅

`--format tagged-pdf`는 태그 없는 PDF에 구조 태그(제목, 문단, 목록, 표, 읽기 순서)를 써서 Tagged PDF로 출력한다. Well-Tagged PDF 사양을 따르고 veraPDF로 검증한다고 README가 밝힌다.

무료(Apache 2.0)인 범위는 "태그 생성까지"이고, PDF/UA-1/UA-2 내보내기와 접근성 스튜디오(시각 편집기)는 엔터프라이즈 add-on이다. 이 노트의 관심사는 RAG이므로 이 부분은 참고 수준이다.

다만 `--use-struct-tree`로 기존 태그가 있는 PDF의 구조를 휴리스틱 없이 그대로 쓸 수 있다는 점은 RAG에도 의미가 있다.

단, 태그 품질이 나쁜 PDF가 많으니 README도 기본 모드나 hybrid가 더 나을 수 있다고 경고하며, `--use-struct-tree`가 `--hybrid`보다 우선해서 두 옵션을 같이 주면 백엔드가 호출되지 않는다.

## 설치와 사용법

요구사항은 Java 11+와 Python 3.10+(Node.js/Java SDK도 별도)다. Python 래퍼는 의존성이 없고(`dependencies = []`), 빌드 시 JAR를 휠에 포함시킨다.

```bash
java -version                      # JDK 11+ 확인 (없으면 Adoptium 등에서 설치)
pip install -U opendataloader-pdf

# 가장 단순한 사용 (로컬, 결정론적)
opendataloader-pdf file1.pdf file2.pdf folder/ --format json,markdown -o output/

# hybrid: 복잡한 표/스캔본
pip install -U "opendataloader-pdf[hybrid]"
opendataloader-pdf-hybrid --port 5002                                   # 터미널 1
opendataloader-pdf --hybrid docling-fast file1.pdf folder/              # 터미널 2

# 한국어 스캔본 OCR
opendataloader-pdf-hybrid --port 5002 --force-ocr --ocr-lang "ko,en"
opendataloader-pdf-hybrid --port 5003 --force-ocr --ocr-engine tesseract --ocr-lang "kor,eng"

# RAG용: 제목 계층 보정 + 수식
opendataloader-pdf-hybrid --port 5002 --heading-hierarchy --enrich-formula
opendataloader-pdf --hybrid docling-fast --hybrid-mode full folder/
```

```python
import opendataloader_pdf

# JVM 기동 비용 때문에 반드시 한 번에 배치로 호출
opendataloader_pdf.convert(
    input_path=["file1.pdf", "file2.pdf", "folder/"],
    output_dir="output/",
    format="markdown,json",
    hybrid="docling-fast",   # 서버가 떠 있을 때만
)
```

Node는 `npm install @opendataloader/pdf`, Java는 Maven Central의 `org.opendataloader:opendataloader-pdf-core`다. LangChain 로더는 `pip install langchain-opendataloader-pdf` 후 `OpenDataLoaderPDFLoader`를 쓴다. MCP 서버는 `python/opendataloader-pdf-mcp`에 있고 `claude mcp add opendataloader-pdf -- uvx opendataloader-pdf-mcp`로 Claude Code에 붙인다(해당 README 기준, 실제 호출은 해 보지 않음).

저장소에는 에이전트용 `skills/odl-pdf/SKILL.md`도 있는데, 옵션 이름을 외우게 하지 않고 설치된 버전의 help를 읽어 최소 명령을 구성하고 결과를 검증하는 절차를 가르치는 스킬이다.

## 디렉터리·코드 구조에서 확인한 것

- `java/opendataloader-pdf-core`: 코어 엔진. main 소스 약 102개 Java 파일, 테스트 약 67개. 패키지는 `api`(Config, OpenDataLoaderPDF, AutoTagger), `processors`(Hidden/Header-Footer/Heading/List/Paragraph/Table*/TextLine/TableOfContents 등 처리 단계별 클래스), `processors/readingorder`(XYCutPlusPlusSorter), `hybrid`(TriageProcessor, DoclingFastServerClient, DoclingSchemaTransformer, HybridConfig), `autotagging`, `markdown`/`html`/`json`, `utils`(ContentSanitizer 등).
- `java/opendataloader-pdf-cli`: commons-cli 기반 CLI. 코어는 PDFBox 3.0.4, veraPDF 1.31.x, Jackson, okhttp를 사용한다(pom 기준).
- `python/opendataloader-pdf`: JAR를 감싼 래퍼 + `hybrid_server.py`. `python/opendataloader-pdf-mcp`: MCP 서버.
- `node/opendataloader-pdf`: Node SDK. `options.json`/`schema.json`: 옵션과 JSON 스키마의 원천 정의(생성 스크립트 `scripts/generate-*.mjs`).
- `samples/`, `examples/python`, `skills/`, `verification/`, `THIRD_PARTY/`(제3자 라이선스 고지).
- 라이선스 고지에 따르면 한컴은 veraPDF 구성요소를 이중 라이선스 중 MPL-2.0으로 선택해 배포한다(`THIRD_PARTY_LICENSES.md`). 코어 자체는 Apache-2.0이지만 MPL-2.0 컴포넌트가 포함된다는 뜻이다.

## 벤치마크: 무엇이 주장이고 무엇을 확인했나

README는 200개 실제 PDF(다단, 과학 논문 포함)에서 reading order, table, heading 정확도를 측정한 표를 싣는다. 점수는 [0, 1]로 정규화한 값이고 Apple M4에서 측정했다고 한다.

| 엔진 | Overall | Reading | Table | Heading | s/page | 라이선스 |
|---|---|---|---|---|---|---|
| opendataloader [hybrid] | 0.907 | 0.934 | 0.928 | 0.821 | 0.463 | Apache-2.0 |
| nutrient | 0.885 | 0.925 | 0.708 | 0.819 | 0.008 | 상용 |
| docling | 0.882 | 0.898 | 0.887 | 0.824 | 0.762 | MIT |
| marker | 0.861 | 0.890 | 0.808 | 0.796 | 53.932 | GPL-3.0 |
| unstructured [hi_res] | 0.841 | 0.904 | 0.588 | 0.749 | 3.008 | Apache-2.0 |
| opendataloader (local) | 0.831 | 0.902 | 0.489 | 0.739 | 0.015 | Apache-2.0 |
| mineru | 0.831 | 0.857 | 0.873 | 0.743 | 5.962 | AGPL-3.0 |
| pymupdf4llm | 0.732 | 0.885 | 0.401 | 0.412 | 0.091 | AGPL-3.0 |
| markitdown | 0.589 | 0.844 | 0.273 | 0.000 | 0.114 | MIT |

벤치마크는 다음 다섯 가지를 구분해 읽어야 한다.

1. 이 벤치마크는 프로젝트가 직접 운영하는 `opendataloader-bench` 저장소의 결과이며 독립 재현은 하지 못했다.

2. hybrid(0.907)와 docling(0.882)의 차이는 0.025로 크지 않다. 표 점수(0.928 vs 0.887)가 차이를 만드는 반면 heading은 docling이 근소하게 높다.

3. local 모드의 표 점수 0.489는 낮고, "표가 중요하면 hybrid가 사실상 필수"라는 뜻이다. FAQ가 말하는 "+90% 표 정확도 향상"은 이 0.489 → 0.928 상승을 가리킨다.

4. 대부분 영어/과학 문서일 가능성이 높고 한국어 문서 구성은 알 수 없다.

5. FAQ에는 "docling은 bbox와 AI safety 필터가 없다"는 비교 주장이 있는데 이 부분은 확인하지 못했다.

## 비교 대상

- **Docling**: hybrid의 백엔드이자 직접 경쟁자. Docling 단독은 레이아웃/표 모델 중심의 순수 Python 파이프라인이라 모든 페이지에 모델 추론 비용을 낸다(0.762s/page). ODL은 단순 페이지를 Java 경로로 처리해 평균 비용을 줄이는 구조다.
- **[[markitdown]]**: Microsoft의 다형식(Office 포함) 변환기. 벤치마크에서 표/제목 점수가 낮다(README 수치). 대신 Word/Excel/PPT를 다룰 수 있고 ODL은 못 한다. 용도가 다르다.
- **[[anydoc]]**: Firecrawl의 순수 Rust 문서 변환 라이브러리(ML 모델 없이 Office 계열 등을 Markdown으로). 스캔 PDF는 OCR 대신 에러로 돌려주는 설계라 ODL의 hybrid OCR과 역할이 갈린다. 한국어 샘플로 직접 비교 평가가 필요하다.
- **marker / MinerU / pymupdf4llm**: 라이선스가 GPL-3.0 / AGPL-3.0 / AGPL-3.0이다(README 표 기준). 사내 서비스에 넣을 때 카피레프트 검토가 필요한데, ODL은 Apache-2.0이라 법무 부담이 상대적으로 작다.
- **PageIndex([[pageindex]])**: 파싱 도구가 아니라 "트리 인덱스 + LLM 탐색" 검색 방식이다. 입력 PDF를 PageIndex가 자체 파서로 읽기 때문에 직접 경쟁하지 않고, 파싱 결과의 구조 정보(제목 계층)를 상호 보완할 여지가 있다.

## 장단점, 한계, 성숙도

장점은 분명하다. 좌표가 있는 구조화 출력, GPU 없이 CPU로 빠른 로컬 모드, 문서가 로컬을 벗어나지 않는 구조(README: 모든 처리가 로컬이고 API 호출이 없음), Apache-2.0, 릴리스 주기가 매우 빠르다(v2.5.9 9/16, v2.5.10 9/18, v2.5.11 9/22).

저장소에 에이전트 스킬과 MCP 서버까지 있어 Claude Code 같은 도구와 붙이기 쉽다.

한계도 있다. 확인한 것만 적는다.

1. Java 11+가 필수이고 호출마다 JVM을 기동한다.

2. hybrid는 서버 프로세스를 따로 운영해야 하고 의존성이 무겁다(Docling, EasyOCR 등).

3. Word/Excel/PPT는 지원하지 않는다(능력 표에 "No").

4. HWP/HWPX는 오픈소스 코어에 없다. README에서 "Hancom Data Loader 통합"이 Coming Soon/Planned(Q2–Q3 2026)로 표시되어 있고 엔터프라이즈 서비스로 안내된다. 한국 환경에서는 가장 아쉬운 지점이다.

5. 오픈 이슈에 구조 추출 품질 문제가 다수 있다. 예컨대 #755(중첩 목록이 평탄화되고 제목이 목록/문단으로 오분류), #751(제목 레벨이 폰트 크기를 따라가며 레벨을 건너뛰고 PDF/UA 7.4.2-1 검증 실패), #745(border 검출 표는 TH를 내지 않음), #740(ToUnicode 없는 Type3 폰트에서 페이지 전체가 비어 버림), #720(hybrid auto 모드에서 TableFormer가 밀집 표의 행을 합침), #725(사용자 프로필 경로에 비ASCII 문자가 있으면 Windows에서 hybrid 실패). 이는 이슈 제목 기준 확인이며 재현해 본 것은 아니다.

6. 한국어 표/스캔 정확도는 공개 수치가 없다.

성숙도 사실: GitHub 기준 Stars 29,445, Forks 2,808, 오픈 이슈+PR 92건(API의 open_issues_count), 라이선스 Apache-2.0(2.0 미만은 MPL-2.0), 생성 2025-05-13, 마지막 push 2026-10-01, 최신 릴리스 v2.5.11(2026-09-22).

1년 남짓한 프로젝트가 별 2.9만 개인 것은 홍보가 강하게 작동한 결과일 수 있으므로(README에 Trendshift 배지, "#1" 표현이 많음) 별 수보다 실제 사내 문서 PoC 결과를 우선하는 편이 안전하다.

## 보안·라이선스·운영 리스크

- **라이선스 전파**: 코어는 Apache-2.0이지만 veraPDF 구성요소는 MPL-2.0으로 배포된다(파일 단위 카피레프트). 수정 없이 의존성으로 쓰는 한 부담은 작지만, 사내에서 해당 라이브러리를 수정·재배포한다면 MPL 조건을 확인해야 한다. 구버전(2.0 미만)은 MPL-2.0이다.
- **hybrid 서버 노출**: FastAPI 서버에 인증 개념이 있다는 근거를 README에서 찾지 못했다. 사내 망에서 localhost/내부 인터페이스에만 바인딩하고, 업로드 크기(`--max-file-size`)와 그림 수 상한(`--picture-area-threshold`)을 걸어야 한다. 변환 요청이 직렬화되므로 DoS에 취약할 수 있다(README의 경고에서 도출한 추론).
- **프롬프트 인젝션 필터의 한계**: 투명/오프페이지 텍스트는 거르지만, 눈에 보이는 본문에 섞인 인젝션 문구는 파서가 막지 않는다. 파싱 결과를 LLM에 넣는 단계의 방어가 따로 필요하다.
- **개인정보**: `--sanitize`는 기본 꺼짐이며 정규식 기반이라 오탐/누락이 있다(이슈 #757). 마스킹 용도로 신뢰하지 말고 별도 PII 탐지와 병행할 것.
- **엔터프라이즈 분리**: 접근성(PDF/UA)과 일부 고급 문서 분석은 유료 영역이다. 오픈소스 범위가 앞으로도 유지될지는 README의 약속("core accessibility pipeline은 계속 무료")에 의존한다.
- **빠른 릴리스 주기**: 마이너 버전에서도 출력 스키마나 옵션이 바뀔 수 있다. `skills/odl-pdf`도 "옵션 이름은 버전마다 바뀌니 런타임에 help로 확인"하라고 전제한다. 버전을 고정하고 회귀 테스트를 두자.

## 관련 노트

[[markitdown]] [[anydoc]] [[pageindex]] [[ragas]] [[cerebras-knowledge-base-pgvector-rrf-mcp]]

## 출처

- https://github.com/opendataloader-project/opendataloader-pdf (README 전문, `options.json`, `python/*/pyproject.toml`, `java/opendataloader-pdf-core/pom.xml` 및 소스 `TriageProcessor`/`XYCutPlusPlusSorter`/`ContentSanitizer`, `THIRD_PARTY/THIRD_PARTY_LICENSES.md`, `skills/odl-pdf/SKILL.md`, `python/opendataloader-pdf-mcp/README.md`; 2026-10-01 clone 후 열람)
- GitHub REST API: repos 메타데이터, releases, 오픈 이슈 목록(2026-10-01 조회)
- 열람하지 않은 것: opendataloader.org 문서 사이트, `opendataloader-bench` 저장소(벤치 재현), 한국어 문서 실측
