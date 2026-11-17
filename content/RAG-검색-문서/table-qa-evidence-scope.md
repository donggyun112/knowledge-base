---
title: 큰 표의 QA — 필요한 셀과 빠짐없는 행 집합
source: https://aclanthology.org/2026.emnlp-main.1589/
category: RAG-검색-문서
type: paper
tags: [rag, table-qa, retrieval, evaluation, technology-radar]
researched: 2026-11-18
radar_quadrant: Techniques
radar_ring: Assess
reading_status: unread
---

# 큰 표의 QA — 필요한 셀과 빠짐없는 행 집합

- **원문**: [ATR (Kim et al.)](https://aclanthology.org/2026.emnlp-main.1589/) · [TRACE (Cha et al.)](https://aclanthology.org/2026.emnlp-main.2594/)
- **발행**: EMNLP 2026, 2026년 10월 (ACL Anthology 표기)
- **수집일**: 2026-11-18 KST
- **상태**: Techniques / Assess / 읽기 전
- **검증 범위**: 공개 논문과 ATR 비용 부록 정적 검토. 모델 호출·재현은 하지 않았다.

## 원문 핵심

**ATR은 작은 질문마다 읽는 방법을 선택한다.** 질문을 하위 질의로 나누고 본문 검색, 셀 검색, SQL, 또는 셀 값 연결 후 SQL 중 하나를 고른다. 검증을 통과하지 못하면 실패한 경로를 반영해 다시 선택한다. 예를 들어 질문의 표현과 표에 저장된 값이 다르면, 셀에서 실제 값을 찾은 뒤 SQL 필터로 쓸 수 있다. [ATR §3](https://aclanthology.org/2026.emnlp-main.1589.pdf#page=3)

**TRACE는 일부 행이 빠지면 답이 바뀌는 질문에 초점을 맞춘다.** 표에 연결된 본문을 키와 타입이 있는 보조 테이블로 바꾼 뒤, 질의에 필요한 열이나 빈 값을 추가로 채운다. 그 위에서 SQL로 필터·조인·집계를 수행한다. 관련도 top-k가 높은 행을 읽는 것과 조건을 만족하는 행을 모두 셌는지는 다른 문제다. [TRACE 본문](https://aclanthology.org/2026.emnlp-main.2594.pdf)

## 결과를 적용할 때

- ATR의 전체 Gemini 2.5 Flash 구성은 HybridQA 개발셋에서 질문당 LLM 호출이 평균 **14.77회**였다. 분해·실행·검증·종합 등을 포함한 해당 구성의 수치이지, 작은 셀 조회 한 건의 필수 비용은 아니다. [ATR 부록 Table 19](https://aclanthology.org/2026.emnlp-main.1589.pdf#page=22)
- TRACE의 집합 연산은 보조 테이블을 정확히 채웠다는 전제에 의존한다. SQL이 계산을 정확히 해도 본문 예외가 누락되면 집계는 틀릴 수 있다. 두 자료는 **파싱 이후**의 QA를 다루며 HWP/HWPX의 표 위치나 병합 복원 품질을 검증하지 않는다.

## 작게 확인할 방법

같은 파싱 결과를 고정하고, 행 top-k를 바로 읽는 기준선과 질문에 따라 셀 조회 또는 전체 조건 스캔으로 분기하는 안을 비교한다.

| 질문 | 읽는 범위 제안 | 별도로 채점할 것 |
| --- | --- | --- |
| 특정 부서의 특정 연도 금액 | 해당 행과 값 셀, 병합 헤더 경로, 단위 | 값·원본 셀 좌표·전체 헤더 경로 |
| 각주 예외를 제외한 해당 연도 합계 | 조건에 필요한 전체 행과 연결된 예외 근거 | 대상 행 집합의 누락·포함 오류와 최종 산술 |

**다음 질문**: 표 전체를 모델에 넣지 않고도 조회는 작은 근거로 끝내고, 집계는 조건에 맞는 행을 빠짐없이 다룰 수 있는가? 정답뿐 아니라 행 커버리지·근거 누락·호출 수·전체 지연을 함께 비교한다.
