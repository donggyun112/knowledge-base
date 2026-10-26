---
title: "Dashi PPT Skill — 브라우저에서 편집하는 프레젠테이션"
source: https://github.com/chuspeeism/dashi-ppt-skill
type: repo
category: 에이전트-스킬
tags: [research, agent-skills, presentation, html, pptx]
researched: 2026-10-26
---

# Dashi PPT Skill — 브라우저에서 편집하는 프레젠테이션

Dashi PPT Skill은 문서를 받아 프레젠테이션을 생성하고, 브라우저에서 수정한 뒤 HTML·PDF·편집 가능한 PPTX로 내보내는 AI 에이전트 스킬이다. 핵심은 **생성 결과 자체가 편집 화면**이라는 점이다.

## 무엇을 할 수 있나

[공식 README](https://github.com/chuspeeism/dashi-ppt-skill/blob/21dc7e5fc8c3a0d7f6a94948153dd1ee954f4e64/README.md)는 12개 테마와 1,020개 레이아웃을 소개한다. 텍스트를 직접 고치고 이미지를 교체하며, 페이지별 컨트롤로 배치·색상·모듈 수를 조절한다. 보고서·경쟁사 분석·프로젝트 발표처럼 일관된 초안이 필요한 작업을 대상으로 한다.

흐름은 요구사항과 청중 정하기 → 테마 선택 → 초안 생성 → 브라우저 편집 → 내보내기다. 픽셀 단위의 자유로운 디자인에는 적합하지 않으며, PPTX가 HTML의 모든 기능을 그대로 보존하지는 않는다.

## 실행 조건

로컬 파일과 셸을 다루는 에이전트가 필요하다. README는 Claude Code와 Codex 등을 지원 대상으로 안내한다.

- Node.js 20 이상과 npm
- PDF·PPTX 내보내기용 Chrome·Chromium·Edge
- 설치·업데이트 명령: `npx dashi-ppt-skill@latest`

## 도입 전에 볼 점

- **품질:** 실제 PPTX에서 글꼴·배치·편집 가능 범위를 확인해야 한다.
- **데이터:** README의 로컬 처리 설명을 이용하는 AI 에이전트의 데이터 처리 정책과 혼동하지 않아야 한다.
- **라이선스:** 본체는 AGPL-3.0이며, README는 내보내기 엔진을 별도 독점 구성요소로 명시한다. 엔진만 추출·재배포하려는 경우 특히 확인이 필요하다.

## 함께 읽기

- [[에이전트-스킬/open-design|OpenDesign]] — 에이전트와 디자인 작업공간
- [[에이전트-스킬/diagram-design|diagram-design]] — 기술 다이어그램 생성 스킬

## 출처와 확인 범위

2026년 10월 26일 [저장소 README](https://github.com/chuspeeism/dashi-ppt-skill/blob/21dc7e5fc8c3a0d7f6a94948153dd1ee954f4e64/README.md)를 확인했다. 설치·생성·내보내기는 실행하지 않았으며, 기능 설명은 프로젝트 문서 기준이다.

- [원본 저장소](https://github.com/chuspeeism/dashi-ppt-skill)
- [라이선스 원문](https://github.com/chuspeeism/dashi-ppt-skill/blob/21dc7e5fc8c3a0d7f6a94948153dd1ee954f4e64/LICENSE)
