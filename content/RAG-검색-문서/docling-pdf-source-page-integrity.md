---
title: Docling PDF — 페이지 누락과 인용 위치 오류 구분하기
source: https://github.com/docling-project/docling/pull/5554
type: implementation
category: RAG-검색-문서
tags: [research, docling, pdf, provenance, rag, technology-radar]
researched: 2026-11-28
radar_quadrant: Tools
radar_ring: Assess
reading_status: unread
---

# Docling PDF — 페이지 누락과 인용 위치 오류 구분하기

**텍스트가 그럴듯해도 요청한 페이지가 전부 처리됐거나 인용이 맞다는 뜻은 아니다.** Docling의 두 수정은 누락된 페이지와 잘못 가리키는 페이지를 서로 다른 단계에서 다룬다.

- **원문**: [Native 페이지 누락 #5554](https://github.com/docling-project/docling/pull/5554)와 [2.153.0](https://github.com/docling-project/docling/releases/tag/v2.153.0), [VLM 범위 조립 #4498](https://github.com/docling-project/docling/pull/4498)과 [2.151.1](https://github.com/docling-project/docling/releases/tag/v2.151.1)
- **확인된 날짜**: GitHub 릴리스 기준 2.153.0은 2026-11-25, 2.151.1은 2026-11-19.
- **수집일**: 2026-11-28 KST
- **상태**: Tools / Assess · 읽기 전
- **검증 범위**: 공개 릴리스·PR과 테스트 설명의 정적 검토. PDF 변환, OCR 또는 VLM 로컬 검증은 하지 않았다.

## 1. Native: 요청 집합과 출력 집합

Native 백엔드의 페이지 반복자가 일찍 끝나면, 해당 범위에 있었지만 전달되지 않은 페이지마다 구조화된 백엔드 오류를 남긴다. 일부 페이지가 있으면 변환한 페이지와 출처를 보존하고 부분 성공으로 분류한다. PR 작성자 검증에서는 일반 실패 정책에서 **부분 출력과 종료 코드 0**이 함께 나올 수 있었고, `--fail-on partial`에서는 부분 파일을 쓰되 종료 코드가 1이었다. 0페이지는 실패로 처리하고 CLI 출력을 쓰지 않았다. 이는 해당 조기 종료 경로에 대한 관찰이지 모든 파서 실패가 같은 형태로 기록된다는 뜻은 아니다.

## 2. VLM: 조립 후 원본 페이지 인용

VLM 범위 조립은 최상위 항목의 페이지를 원본 기준으로 바꾸면서, 키·값과 양식의 그래프 셀에 있는 중첩 출처는 조각 기준 번호로 남길 수 있었다. 2.151.1은 기존 페이지 매핑을 **이미 출처가 붙은** 중첩 셀에도 적용한다. 출처가 원래 없는 셀에 새로 만들어 주지는 않는다. 업스트림은 정해진 모델 응답으로 통째 변환과 범위 변환을 비교했다. 빈 범위, 겹침, 누락을 거부하는 별도 예제는 기본 변환 경로 전체의 보장이 아니다.

## 3. 작은 검증 제안

1. **Native 누락**: 페이지마다 다른 식별자가 있는 합성 4쪽을 만들고 2–3쪽을 요청한다. 모두 전달되는 경우, 2쪽만 전달되는 경우, 빈 응답을 비교한다. 페이지 ID 집합, 변환 상태, 오류의 원본 페이지 번호, CLI 종료 코드를 각각 기록한다.
2. **VLM 인용**: 뒤쪽 페이지의 중첩 양식에만 고유 값이 있는 합성 PDF를 사용한다. 고정 모델 응답으로 전체 변환과 범위 조립을 비교하고, 마지막으로 검색 색인에 실제 넘기는 레코드의 원본 페이지를 확인한다.

첫 번째는 빠진 증거를 찾고, 두 번째는 존재하는 증거가 잘못 연결됐는지 본다. OCR 재실행을 결정하기 전에 둘을 구분하면 원인을 좁힐 수 있다. 위 검증은 제안이며 결과는 아니다.
