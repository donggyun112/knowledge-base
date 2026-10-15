---
title: Threads - Jina AI jina-ocr-v1 소개 게시물
source: https://www.threads.com/@choi.openai/post/Ddb3m3aiTXQ
type: community
category: 기타-리소스
tags: [research, ocr, jina, rag, threads]
researched: 2026-10-01
---
# Threads - Jina AI jina-ocr-v1 소개 게시물

> [!summary] 한줄요약
> 게시물의 핵심 주장(총 3.4B/활성 570M, 25개 언어, OmniDocBench v1.6 91.14, L4급 GPU, 최고 페이지 처리 속도)은 Jina 공식 모델 페이지, Hugging Face 카드, 블로그, arXiv 논문(2609.03181) 네 곳 모두에서 확인된다. 다만 게시물이 빠뜨린 점이 있다. 라이선스가 CC BY-NC 4.0(비상업)이고, 가장 약한 영역이 열화 스캔본(OldScans 42.6)이며, OmniDocBench 순위로는 PaddleOCR-VL-1.6(96.34) 같은 더 높은 모델이 있고, 한국어는 모델 페이지·논문·벤치마크 어디에도 언급이 없다.

## 배경

이 노트는 Threads 게시물(2026-09-19, 조회 약 1.4만회, 좋아요 112, 댓글 4, 리포스트 26, 공유 72, 로그인 없이 렌더링한 화면 기준)이 소개한 `jina-ocr-v1`을 다룬다. 작성자 계정 정보는 기록하지 않는다. 게시물 본문은 4문장이고, 작성자가 자기 글 아래에 단 댓글에 블로그 링크가 있다. 다른 사용자 댓글 3건은 "570M 파라미터로 이 성능이면 실무에 써볼 만하다", "PDF·스캔본에 좋을 듯", "손글씨도 가능할까요?" 정도다.

원 출처는 Jina AI(현재 Elastic 소속, 사이트 푸터에 표기)의 `jina-ocr-v1`이다. 시간순으로 정리하면 HF 모델 저장소 생성 2026-09-01, arXiv 제출 2026-09-02(저자 Alejandro Barón García, Feng Wang, Emilia Garcia Casademont, Han Xiao, 15쪽, 그림 5개, 표 8개), 모델 페이지 출시일 2026-09-14, 블로그 2026-09-15(9분 분량), HF 마지막 수정 2026-09-18이다. 이번에는 게시물이 아니라 아래 원문을 직접 열어 주장을 하나씩 대조했다. 블로그와 모델 페이지는 headless Chrome 렌더, 논문은 arXiv HTML 전문(약 5.5만 자 텍스트)과 초록 페이지, HF는 README 원문과 API 메타데이터, OmniDocBench는 저장소 clone으로 읽었다.

## 상세 기능과 동작

### 1. 게시물 주장 대 공식 자료
| 게시물의 주장 | 공식 자료 | 판정 |
|---|---|---|
| PDF·스캔본·표·차트·송장을 구조화 Markdown으로 변환 | 입력 이미지·PDF, 출력 텍스트. "단일 패스로 텍스트, 수식, 표, 읽기 순서". 디코더 출력은 Markdown이며 표는 HTML, 수식은 LaTeX(블로그). 학습 데이터에 송장(Invoices), CommonForms, RVL-CDIP가 "핵심 정보 추출" 용도로 들어 있고(논문 Table 2) 차트는 SynthChartNet 포함 | 일치. 송장 전용 평가 수치는 없음 |
| 총 3.4B, 활성 570M | 모델 페이지 3.4B, 토큰당 활성 약 570M. HF 메타데이터 총 3,372,238,080 파라미터(BF16). 논문 표기는 "디코더 약 570M/약 3B, 전체 3.4B 미만 1B 활성" | 일치 |
| 25개 언어 | 모델 페이지: "훈련된 언어 25개", "지원되는 언어 108개". 모델 페이지는 베이스 DeepSeek-OCR이 "약 100개 언어" 3천만 페이지 PDF로 사전학습됐다고 설명 | 부분 일치. 25는 훈련 언어, 지원은 더 넓게 주장. 25개 목록은 어디에도 공개되지 않음 |
| OmniDocBench v1.6 91.14 | 91.14 (모델 페이지, HF `model-index`, 블로그, 논문 모두 동일). olmOCR-Bench 83.4 | 일치 |
| L4급 GPU에서 구동 | NVIDIA L4, 배치 1, vLLM 0.20.1: eager에서 42.7 → 83.1 tok/s(K=3, 1.95배), CUDA graph에서는 158.3 → 최적 K=1 185.6 tok/s(1.17배) | 일치. 단 "L4에서 처리량이 높다"가 아니라 "L4에서 배치 1 디코딩이 빠르다"는 측정 |
| 비교 모델 중 페이지 처리 속도 최고 | A100 SXM4 40GB 1대, 동시성 32, 1,403페이지에서 2.57 pages/s. 측정한 14개 시스템 중 최고, olmOCR-2는 1.22 pages/s | 일치. 단 14개 비교군은 Jina가 선정 |

### 2. 구조와 설계
- 베이스는 DeepSeek-OCR이다. DeepEncoder(약 380M: SAM 80M → 16배 컨볼루션 압축기 → CLIP-L 300M)가 1024×1024 페이지를 256개 시각 토큰으로 만들고, 동적 해상도 "Gundam" 모드는 타일마다 100토큰을 더해 페이지당 최대 1,156토큰까지 쓴다. 논문은 4,096패치가 256토큰으로 줄어 시각 토큰당 3,887픽셀이고 28~32px 패치 인코더는 783~1,022픽셀이라고 비교한다.
- 디코더는 DeepSeek-3B-MoE: 12 레이어, hidden 1280, 라우팅 전문가 64 + 공유 2, top-6, 어휘 129,280, 위치 한도 32,768.
- 속도의 핵심은 FastMTP 투기적 디코딩이다. 단일 dense draft 블록을 K=3 스텝에 재귀 적용하고 검증기가 탐욕적으로 확인하므로 출력은 일반 자기회귀 디코딩과 같다(lossless). 검증 패스당 평균 2.7토큰(Table에서는 K=3일 때 τ=2.73)을 확정한다.
- 후학습은 지시 정렬 SFT → 열화 문서 강건성 파인튜닝 → GRPO를 외부 루프로 반복한다. GRPO 보상은 결정론적 검사의 곱이다. 내용 편집 거리, 수식 문자열 일치, 표 TEDS/TEDS-S/표 편집 거리, 구조 유효성(괄호·태그 닫힘), olmOCR식 유닛 테스트 통과율, 반복·형식 패널티로 구성되고 대부분 하한(floor)을 두지만 반복 항에는 없다. ReMax 기준선(샘플 보상에서 탐욕 보상을 뺌)을 쓴다. 매 라운드 체크포인트 병합 설정을 에이전트가 탐색한다.
- 학습 데이터(논문 Table 2): 디지털 PDF(olmOCR-mix 등), 합성 페이지(olmOCR-synthmix, HTML 렌더링), 수식·표(LaTeX-OCR, UniMER, MMTab, SynthChartNet), 역사·열화 자료(Europeana, Library of Congress, NARA, NCSE, jaWildText 일본어), 다국어(FinePDFs, 중국어 PDF), 비즈니스·양식(송장, CommonForms, RVL-CDIP), VQA·그라운딩, 보상 커버리지용 합성 JinaOCRSynth. 정리용으로 Qwen3.5-122B-A10B가 어려운 소스를 재라벨링하고 Qwen3-VL-30B-A3B가 노이즈 샘플을 감사했다. 프롬프트는 영어와 중국어 변형이 있다.

### 3. 사용법
- Reader 경유: `curl "https://r.jina.ai/<PDF URL>" -H "Authorization: Bearer $JINA_API_KEY" -H "X-Respond-With: jina-ocr-v1"`, 여러 쪽 문서는 `X-Page`(1부터)로 한 쪽씩.
- 호스팅 API: OpenAI 호환 `https://api.jina.ai/v1/chat/completions`, 모델 `jina-ocr-v1`, 이미지 URL 또는 base64. cold start는 HTTP 503이며 30~60초 후 재시도(HF 카드).
- 로컬: 같은 HF 저장소에 가중치와 커스텀 코드가 있어 `trust_remote_code=True`. Transformers 경로는 MoE 디코더만 돌리고 MTP 가중치는 무시한다(FastMTP 없음). FastMTP는 vLLM 0.21 이상에서 `deepseek_ocr_mtp.py`의 `register()`를 먼저 호출해야 한다. 측정은 vLLM 0.20.1에서 했다고 블로그 표에 적혀 있어 두 버전 표기가 어긋나는데 이유는 확인하지 못했다. 헬퍼는 FastMTP를 `method="eagle"`로 등록한다(기본 `mtp`로 두면 재귀 피드백 학습과 맞지 않아 속도 이득이 사라진다).
- 권장 프롬프트: "Transcribe the provided document image into a clean Markdown format, preserving the natural reading order." 벤치마크 점수는 더 엄격한 프롬프트(수식은 LaTeX, 표는 HTML, 헤더·푸터와 그림 제거, "Read any natural handwriting", 텍스트가 없으면 null)로 측정했다. 따라서 기본 프롬프트에서는 점수가 달라질 수 있다.

## 구체 수치·가격·요건

### 벤치마크 (Jina 공식 자료)
- olmOCR-Bench 전체 83.4(DeepSeek-OCR 대비 +7.4). 하위: Base 99.9, LongTiny 93.2, Tables 88.8, Hdr/Ftr 88.7, ArXiv 86.1, Multi-column 85.5, OldScans-Math 82.3, OldScans 42.6. 블로그의 비교표(olmOCR-Bench 전체): chandra-ocr-2 85.8, dots.mocr 83.9, jina-ocr-v1 83.4, LightOnOCR-2 83.2, olmOCR-2 82.4, DeepSeek-OCR 76.0. 모델 페이지는 olmOCR-Bench 점수 순위를 33개 중 5위로 표시한다. HF의 DeepSeek-OCR 카드는 olmOCR-bench 75.7로 적고 있어 Jina 표의 76.0과 0.3점 어긋난다(측정 조건 차이로 추정, 확인 못함).
- OmniDocBench v1.6 전체 91.14: 텍스트 편집 거리 0.046, 수식 CDM 93.28, 표 TEDS 84.68, TEDS-S 89.01, 읽기 순서 편집 거리 0.142. 블로그/논문 비교표의 다른 모델: PaddleOCR-VL-1.6(0.9B) 96.34, HunyuanOCR-1.5(1B) 94.74, Gemini 3 Flash 92.62, DeepSeek-OCR-2 90.25, Qwen3-VL-235B 89.78. 즉 jina-ocr-v1은 이 벤치마크의 1등이 아니라 "활성 570M 대비 효율"이 주장의 핵심이다. 논문은 순위 값을 OpenDataLab 공개 리더보드에서 옮겼고 HunyuanOCR-1.5만 해당 기술보고서에서 가져왔다고 적는다.
- 처리량: 2.57 pages/s(A100, 동시성 32), 페이지당 출력 1,085토큰, 초당 2,792토큰. 더 높은 품질의 모델은 느리다고 모델 페이지는 적는다. Infinity-Parser2-Pro 87.6점(H100 TP=2, 페이지당 2.13초), Infinity-Parser2-Flash 86.0점(0.95초), chandra-ocr-2 0.38 pages/s, dots.mocr 0.55 pages/s. Surya OCR 2는 초당 3,760토큰으로 토큰 속도는 더 빠르지만 페이지당 3,568토큰을 내 1.05 pages/s다. 논문은 jina-ocr-v1이 "83점을 넘는 시스템 중 가장 짧은 출력"이라고 쓴다.
- 입력 제한: 32K 토큰, 이미지 1024×1024. HF 카드 기준 `region:eu` 태그, 다운로드 7,418, 좋아요 186, 저장소 파일은 safetensors 2개와 커스텀 코드.

### 라이선스와 비용
- 가중치: CC BY-NC 4.0, 상업 이용은 별도 문의(HF 카드: "Commercial use: contact"). 블로그도 "Weights are released under CC BY-NC 4.0".
- Reader 경유 사용 시 jina.ai/reader 페이지는 `X-Respond-With: jina-ocr-v1` 옵션에 "토큰 사용량이 40배입니다!"라고 경고한다(렌더 확인). 같은 페이지의 속도 제한 표: API 키 없음 20 RPM, 무료/유료 키 500 RPM, 프리미엄 5,000 RPM. WebFetch 요약은 신규 키에 무료 토큰 1천만 개가 있다고 했으나 렌더 텍스트에서는 이 문장을 직접 확인하지 못했다.
- 온프레미스: Elastic이 2026-08-10부터 "Jina On-Prem" 상용 라이선스를 별도 SKU로 판매하며, Reader 모델은 독립형 오프라인 Docker 컨테이너로 제공된다고 FAQ에 적혀 있다. jina-ocr-v1이 이 컨테이너에 포함되는지는 확인하지 못했다. 가격은 영업 문의.
- 하드웨어: L4 급이면 단일 문서 대화형 파싱에 충분하다고 모델 페이지가 권한다. 메모리 요구량 수치는 찾지 못했다(3.4B BF16이므로 가중치만 약 6.7GB라는 계산은 추정이다).

## 비교 (다른 OCR 모델·서비스)
| 모델/서비스 | 규모 | OmniDocBench v1.6 | olmOCR-Bench | 라이선스 | 비고 |
|---|---|---|---|---|---|
| jina-ocr-v1 | 3.4B(활성 570M) | 91.14 | 83.4 | CC BY-NC 4.0 | 페이지 처리 속도 최고(자사 비교군), 한국어 언급 없음 |
| PaddleOCR-VL-1.6 | 0.9B(HF 표기 1.0B) | 96.34 | 확인 못함 | Apache 2.0 | PaddleOCR 저장소(Star 90,478)는 "100+ 언어 지원"이라고 소개. 한국어 개별 성능은 확인 못함 |
| HunyuanOCR-1.5 | 1B | 94.74 | 확인 못함 | 확인 못함 | 기술보고서 수치 |
| DeepSeek-OCR(베이스) | 3B | 확인 못함 | 76.0(Jina 표) / 75.7(HF) | MIT | DeepSeek-OCR-2는 OmniDocBench 90.25 |
| chandra-ocr-2 | 4B | 확인 못함 | 85.8 | 저장소는 Apache-2.0(가중치는 확인 못함) | 0.38 pages/s로 느림 |
| olmOCR-2 | 8B | 확인 못함 | 82.4 | 저장소 Apache-2.0 | |
| Upstage Document Parse | 상용 API | 확인 못함 | 확인 못함 | 상용 | 제품 페이지에 한국어 버전 있음, API \$0.01/페이지, 온프레미스 옵션(WebFetch 요약). TEDS 93.48 등 자사 수치 |
수치는 Jina 블로그/논문 표와 각 공식 페이지에서 가져왔고, 서로 다른 설정에서 측정된 값이 섞여 있다. 같은 조건의 독립 재현은 확인하지 못했다. 한국어 문서에 한정한 비교는 어디서도 확인하지 못했다.

## 한계와 리스크
- 한국어: 모델 페이지, HF 카드, 블로그, 논문 전문 어디에도 "Korean"이라는 단어가 없다. 훈련 데이터에 일본어(jaWildText), 중국어 PDF, 다국어 FinePDFs가 있을 뿐 한국어 데이터는 명시되지 않았다. 훈련 25개 언어 목록은 비공개다. 벤치마크도 OmniDocBench는 영어·중국어 간체·영중 혼합만 포함하고(저장소 README의 언어 속성), olmOCR-Bench의 언어 구성은 확인하지 못했다. 따라서 한국어 성능은 "근거 없음"이며 직접 시험해야 한다. 지원 108개 언어 주장은 베이스 모델에서 상속된다는 설명뿐이다.
- 라이선스: 비상업 한정. 회사 업무 파이프라인에 넣으려면 상용 계약이 필요하다. Jina API를 쓰면 데이터가 외부로 나가므로 개인정보·기밀 문서를 보내면 안 된다. 조직의 보안 정책상 개인정보와 내부 자료는 외부에 입력할 수 없으므로 자체 호스팅 또는 익명화된 샘플로만 시험한다.
- 보안: 로컬 실행은 `trust_remote_code=True`로 저장소의 임의 Python 코드를 실행한다. 검토 없이 운영 서버에 올리지 않는다. 가중치 경로는 safetensors라 직렬화 위험은 낮다.
- 벤치마크 출처 편향: 모든 수치가 Jina 자체 측정이고 비교군 14개도 Jina가 골랐다. 품질 점수와 처리량은 다른 하드웨어에서 가져온 모델이 섞여 있으며 모델 페이지 스스로 L4 수치는 A100 처리량과 비교할 수 없다고 적는다. OmniDocBench는 이후 v1.7(2026-04-30 업데이트)이 나왔고 v1.6은 MGAM 매칭과 296쪽 추가가 반영된 판이다. 표 TEDS 84.68은 상대적으로 낮아 표가 많은 재무 문서에서는 직접 검증이 필요하다.
- 헤더/푸터 삭제: RAG에는 노이즈 감소 이득이지만 계약서·법률 문서처럼 머리말·쪽번호·각주 위치가 의미를 갖는 경우엔 손실이다. 각주는 유지하라는 프롬프트 지시가 있다.
- 열화 스캔본: OldScans 42.6이라 심한 저품질 스캔은 사람 검수가 필요하다. 손글씨(댓글 질문)는 평가 프롬프트에 "Read any natural handwriting" 지시가 있을 뿐 별도 수치는 없고, OmniDocBench 문서 유형에 필기 노트가 있다는 점만 확인했다.
- 요금 함정: Reader 경유 호출은 토큰 사용량이 40배로 계산된다는 경고가 있어 대량 처리 전에 비용 시뮬레이션이 필요하다.

## 관련 노트
- [[hada-claude-opus-5-5-prompting]]

## 출처
- https://www.threads.com/@choi.openai/post/Ddb3m3aiTXQ (headless Chrome 렌더)
- https://jina.ai/models/jina-ocr-v1 (렌더, 한국어 UI)
- https://jina.ai/news/jina-ocr-v1-faster-document-parsing-on-low-budget-gpus/ (렌더)
- https://huggingface.co/jinaai/jina-ocr-v1 (README 원문) 및 https://huggingface.co/api/models/jinaai/jina-ocr-v1 (메타데이터)
- https://arxiv.org/abs/2609.03181 및 https://arxiv.org/html/2609.03181 (초록, HTML 전문)
- https://jina.ai/reader (렌더 + WebFetch: 요금·속도 제한·온프레미스)
- https://github.com/opendatalab/OmniDocBench (clone: README의 버전 이력과 언어 속성)
- https://huggingface.co/deepseek-ai/DeepSeek-OCR (WebFetch)
- https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6 (WebFetch)
- https://github.com/PaddlePaddle/PaddleOCR , https://github.com/allenai/olmocr , https://github.com/deepseek-ai/DeepSeek-OCR , https://github.com/datalab-to/chandra (GitHub API 메타데이터와 README)
- https://www.upstage.ai/products/document-parse (WebFetch)

## 확인하지 못한 항목
- 한국어가 훈련 25개 언어에 포함되는지, 한국어 문서 정확도(어떤 공식 자료에도 언급 없음).
- 25개 언어 목록, 손글씨 전용 평가, 송장 전용 평가, 독립 재현 결과.
- PaddleOCR-VL-1.6·HunyuanOCR-1.5·chandra-ocr-2 등의 olmOCR-Bench 값과 일부 라이선스, 가중치 라이선스(chandra).
- Reader 신규 키 무료 토큰 1천만 개(WebFetch 요약에만 있음), On-Prem 컨테이너에 jina-ocr-v1이 포함되는지.
- 논문 본문 속 부록 표 전체(HTML에서 주요 표와 문장만 확인), 메모리 요구량, vLLM 0.20.1 대 0.21 표기 불일치 이유.
