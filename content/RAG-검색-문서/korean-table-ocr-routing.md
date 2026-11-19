---
title: 한국어 표 OCR — 언제 다시 읽을지 평가하기
source: https://huggingface.co/datasets/ONTHEIT/KDoc-OCRBench-V2/blob/main/README.md
category: RAG-검색-문서
type: research
tags: [ocr, document-parsing, tables, evaluation, technology-radar]
researched: 2026-11-19
radar_quadrant: Techniques
radar_ring: Assess
reading_status: unread
---

# 한국어 표 OCR — 언제 다시 읽을지 평가하기

- **원문**: [KDoc-OCRBench-V2](https://huggingface.co/datasets/ONTHEIT/KDoc-OCRBench-V2/blob/main/README.md#tables) · [KoOCR-Bench v1.2](https://huggingface.co/datasets/schift-io/KoOCR-Bench)
- **자료 시점**: KDoc 문서 정정 리비전 `e94ba5b` (초판 발행일 미확인) · KoOCR-Bench v1.2, 2026-10-05 (데이터셋 카드 표기)
- **수집일**: 2026-11-19 KST
- **상태**: Techniques / Assess / 읽기 전
- **검증 범위**: 공개 데이터셋 설명과 채점 규칙 검토. 엔진 실행이나 점수 재현은 하지 않았다.

## 두 자료가 확인하는 것

**KDoc-OCRBench-V2는 셀 값과 주변 관계를 검사한다.** 한국 공공기관 문서의 단일 페이지 PDF 849개 중 760개에 사람이 검수한 표 테스트 49,115개가 있다. 테스트에 지정된 경우에만 인접 셀이나 상단·왼쪽 헤더까지 확인한다. 일치하는 셀을 페이지 내 어느 표에서든 찾는 방식이라, 같은 값이 반복되는 표에서 원본 위치나 여러 층의 병합 헤더 경로까지 보장하지는 않는다.

**KoOCR-Bench는 셀 관계와 별개로 격자 구조를 본다.** 표 영역 100쪽의 기준 격자는 HWPX 원본에서 얻었다. HTML 표의 TEDS 채점은 행·열 병합을 반영하지만 헤더 셀과 일반 셀의 태그 차이는 보지 않는다. Markdown 표는 이 채점에서 0점이므로, 엔진이 확보한 셀 구조를 먼저 같은 형식으로 변환해 비교해야 한다. 카드의 bbox 점수는 좌표가 붙은 블록의 비율이지 좌표 정확도가 아니다.

## 작게 검증할 방법

1. 텍스트층이 있는 PDF와 같은 페이지를 이미지 전용 PDF로 만든 쌍을 준비한다. 쌍은 원문 문서 단위로 묶어 임계값 조정용과 평가용에 나눠 넣는다. 흐림·기울기 등 실제 스캔의 특성은 합성 이미지와 별도로 본다.
2. **네이티브 파서만 / 항상 OCR / 네이티브 파서 후 필요할 때만 OCR**을 비교한다. 뒤 두 경로에는 같은 OCR 엔진을 사용한다. 조건부 경로의 초기 신호 후보는 텍스트층 부재와, 읽은 값이 행·열 헤더에 안정적으로 연결되지 않는 경우다.
3. 값과 헤더 관계가 **복구된 경우**, OCR로 **오히려 틀어진 경우**, OCR을 생략했지만 **호출했으면 복구됐을 경우**를 나눈다. 개선이 없었던 OCR 호출과 전체 p95 지연도 따로 기록한다. 문서당 점수를 함께 보면 테스트가 많은 몇 페이지가 전체 결과를 지배하는지 알 수 있다.
4. 병합 헤더 전체 경로, 단위와 표 위치는 소량을 직접 확인한다. 자료 재사용 전에는 문서별 라이선스와 KoOCR-Bench의 평가 전용 조건을 확인한다.

**다음 질문**: 단순히 글자를 더 많이 읽는 게 아니라 올바른 헤더에 값이 연결되는 경우를, 어느 비용까지 OCR로 복구할 것인가?

관련: [[RAG-검색-문서/table-qa-evidence-scope|큰 표의 QA]]는 이 단계 이후에 필요한 셀과 집계 대상 행을 고르는 문제를 다룬다.
