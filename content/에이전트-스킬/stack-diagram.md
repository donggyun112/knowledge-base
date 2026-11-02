---
title: stack-diagram — 로고가 있는 아키텍처 그림을 HTML로 만드는 스킬
source: https://github.com/caru-ini/stack-diagram
type: repo
category: 에이전트-스킬
tags: [research, agent-skills, diagrams, html, architecture, technology-radar]
researched: 2026-11-02
source_commit: 75dbd3e3c6fe28844322e6064d3a947b870a6c61
radar_quadrant: Tools
radar_ring: Assess
reading_status: unread
---

# stack-diagram — 로고가 있는 아키텍처 그림을 HTML로 만드는 스킬

**stack-diagram은 스택 설명을 받아 로고·그룹·연결선을 갖춘 아키텍처 다이어그램을 만드는 에이전트 스킬이다.** 핵심 결과물은 자산을 내장한 HTML이며 PNG와 React/TSX는 그 결과를 바탕으로 만든다. 독립적인 자동 배치 엔진이나 실제 인프라를 탐지하는 도구는 아니다.

> [!info] 조사 기준
> 수집일 **2026-11-02 KST**. 확인한 커밋은 [`75dbd3e3c6fe`](https://github.com/caru-ini/stack-diagram/commit/75dbd3e3c6fe28844322e6064d3a947b870a6c61), 커밋 시각은 **2026-11-01 23:17:16 KST**다. 저장소에서 확인한 첫 커밋은 같은 날 14:35:10 KST이며, 이를 별도의 제품 출시일로 단정하지 않는다. **Tools / Assess · 읽기 전**. README·SKILL·스크립트·참조 문서·라이선스를 읽었으며 설치·생성·렌더링은 실행하지 않았다.

## 1. 무엇이 자동화되고 무엇은 에이전트가 정하는가

| 단계 | 실제 역할 |
| --- | --- |
| 내용 설계 | 에이전트가 노드, 그룹과 실행·데이터·배포 관계를 정함 |
| 로고 수집 | `fetch_icons.py`가 소스별 파일과 출처 manifest를 저장 |
| 배치 | 에이전트가 geometry 규칙을 읽고 좌표·SVG 경로를 작성 |
| HTML 빌드 | `build.py`가 이미지와 폰트 토큰을 data URI로 치환 |
| 검수·PNG | `render_png.py`가 Playwright/Chromium으로 HTML을 캡처하고 에이전트가 결과를 확인 |
| TSX | 참조 문서에 따라 HTML의 내용과 배치를 React 컴포넌트로 변환 |

기본 캔버스는 고정 크기의 절대 좌표계다. 노드는 HTML 요소, 연결선은 SVG overlay이며, 라벨과 선이 충돌하지 않도록 간격과 경계 규칙을 제공한다. **충돌 회피 알고리즘이 모든 레이아웃을 자동으로 증명하는 구조가 아니라, 에이전트의 배치와 시각 검수에 의존한다.** [SKILL](https://github.com/caru-ini/stack-diagram/blob/75dbd3e3c6fe28844322e6064d3a947b870a6c61/skills/stack-diagram/SKILL.md) · [geometry](https://github.com/caru-ini/stack-diagram/blob/75dbd3e3c6fe28844322e6064d3a947b870a6c61/skills/stack-diagram/references/geometry.md)

스킬은 도구 목록만 주어졌을 때 그룹과 흐름을 추론하도록 안내한다. 따라서 예쁜 결과가 실제 배포 구조를 증명하지 않는다. 특히 public/private subnet, 서비스 간 호출 방향과 CI 배포선을 추정으로 그렸는지 따로 확인해야 한다.

## 2. '공식 로고'의 출처와 정확성 경계

일반 브랜드는 **svgl → devicon → gilbarbara/logos** 순서로 찾는다. svgl은 정규화된 제목을 정확히 맞추고, 실패하면 다음 출처로 넘어간다. 명시적 `name=URL` 입력도 허용한다. 수집 결과의 `manifest.json`에는 소스, URL, 파일과 바이트 수가 들어간다.

AWS는 별도 경로다. `aws/<이름>`과 일부 AWS 접두사 입력은 [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/)에서 현재 패키지 URL을 찾아 ZIP을 메모리에 받아 읽는다. 공식 패키지에서 못 찾으면 제3자 복사본으로 우회하지 않는다. 반면 접두사 없는 일반 이름은 제3자 체인으로 갈 수 있다. 개념 노드에는 Lucide나 번들 generic 아이콘을 사용한다. [수집 구현](https://github.com/caru-ini/stack-diagram/blob/75dbd3e3c6fe28844322e6064d3a947b870a6c61/skills/stack-diagram/scripts/fetch_icons.py)

**프로젝트의 '공식 로고' 지향과 각 파일에 대한 브랜드 소유자의 검증은 다르다.** 일반 체인의 저장소는 브랜드 자체 저장소가 아니며, 코드가 소유권·최신 브랜드 가이드·파일 진위를 인증하지는 않는다. 명칭이 맞아도 서비스 변형이나 오래된 로고인지 사람이 확인해야 한다. URL이 가변이므로 스킬 커밋만 고정해도 내려받는 자산까지 동일해지는 것은 아니다.

브랜드 로고는 재색칠하지 않는 방침이다. 다만 개념용 Lucide 아이콘의 stroke 색·굵기는 코드에서 변경한다. 흰색 로고 판별도 휴리스틱이므로 밝은/어두운 배경 모두 검수할 필요가 있다.

## 3. 출력 형식과 실행 요구사항

- **HTML:** 이미지·폰트를 내장한다. 제공 템플릿 기준으로 열람 시 로고 다운로드가 필요하지 않다. 임의로 수정한 HTML의 외부 참조까지 제거하는 보장은 아니다.
- **PNG:** HTML을 Chromium으로 촬영한다. 기본은 밝은·어두운 테마 두 장이며, 별도의 이미지 생성 모델을 호출하는 방식이 아니다.
- **TSX:** 별도 다이어그램 라이브러리 없이 쓸 수 있는 React 컴포넌트 형태를 안내한다. React/TSX 실행 환경까지 불필요하다는 뜻은 아니다. 폰트는 HTML과 달리 내장하지 않고 앱의 폰트 파이프라인을 따른다.

아이콘 fetch와 build에는 Python **3.9+ 표준 라이브러리**, PNG에는 **Playwright와 Chromium**이 필요하다. 스킬의 전체 검수 절차는 PNG를 렌더링해 보도록 요구하므로 HTML만 납품해도 검수 환경이 필요할 수 있다. 번들 폰트는 Latin subset이어서 한국어 표시는 시스템 fallback과 렌더 호스트의 글꼴을 별도로 확인해야 한다. [README](https://github.com/caru-ini/stack-diagram/blob/75dbd3e3c6fe28844322e6064d3a947b870a6c61/README.md) · [TSX](https://github.com/caru-ini/stack-diagram/blob/75dbd3e3c6fe28844322e6064d3a947b870a6c61/skills/stack-diagram/references/tsx.md) · [폰트](https://github.com/caru-ini/stack-diagram/blob/75dbd3e3c6fe28844322e6064d3a947b870a6c61/skills/stack-diagram/assets/fonts/README.md)

## 4. 외부 요청과 신뢰 경계

다음은 코드 읽기로 확인한 동작과 검토 의견이다. 취약점 재현 결과가 아니다.

- 로고 수집은 svgl API, GitHub raw, jsDelivr, AWS 및 명시한 URL에 요청한다. 검색 slug와 요청 메타데이터가 해당 제공자에게 전달될 수 있다. 기본 코드에서 다이어그램 본문을 외부 모델로 보내는 호출은 보지 못했지만, 스킬을 수행하는 호스트 에이전트의 데이터 처리는 별개다.
- `name=URL`은 `urllib.request.urlopen`으로 전달된다. 별도의 URL allowlist·사설망 차단·리디렉션 목적지 검증을 구현한 코드는 보이지 않는다. 비신뢰 입력을 그대로 fetch 인자로 넘기는 서버 서비스로 노출하지 않는 편이 적절하다.
- `build.py`는 누락된 자산 토큰을 검사하지만 HTML/SVG 정제기나 외부 요청 차단기가 아니다. 작성한 HTML의 다른 내용은 그대로 남는다.
- PNG 스크립트는 Chromium을 **`--no-sandbox`** 옵션으로 시작한다. 브라우저 자체를 보안 격리 경계로 가정하지 말고, 신뢰할 수 있는 HTML과 제한된 별도 실행 환경을 검토해야 한다.

출처: [fetch_icons.py](https://github.com/caru-ini/stack-diagram/blob/75dbd3e3c6fe28844322e6064d3a947b870a6c61/skills/stack-diagram/scripts/fetch_icons.py), [build.py](https://github.com/caru-ini/stack-diagram/blob/75dbd3e3c6fe28844322e6064d3a947b870a6c61/skills/stack-diagram/scripts/build.py), [render_png.py](https://github.com/caru-ini/stack-diagram/blob/75dbd3e3c6fe28844322e6064d3a947b870a6c61/skills/stack-diagram/scripts/render_png.py).

## 5. 코드 라이선스와 로고 사용조건은 따로 본다

코드·문서는 MIT, 번들 폰트는 SIL OFL 1.1이다. 로고까지 저장소의 MIT가 일괄 적용되는 것은 아니다. README는 출처별 라이선스와 브랜드 상표가 별개임을 알리고, SKILL은 실제 사용한 로고 출처를 footer에 표시하도록 안내한다. [LICENSE](https://github.com/caru-ini/stack-diagram/blob/75dbd3e3c6fe28844322e6064d3a947b870a6c61/LICENSE)

AWS 공식 페이지는 고객과 파트너의 아키텍처 다이어그램 제작 및 자료 내 아이콘 사용을 설명한다. 이를 아이콘 원본 묶음의 자유로운 재배포 허가로 확대하지 않는다. 스킬 자체도 AWS 패키지와 낱개 파일의 저장소 재배포는 확인되지 않았다며 제외하도록 안내한다. 실제 공개물에는 해당 브랜드와 자산의 사용조건을 따로 확인해야 한다. [AWS 공식 안내](https://aws.amazon.com/architecture/icons/)

## 6. 어디에 유용하고 어떻게 작게 검토할까

공개 README용 스택 개요, 온보딩 문서, 서비스 간 데이터 흐름 설명처럼 **사람이 검토할 문서 그림**에 잘 맞는 후보다. 인프라 상태의 자동 수집, 토폴로지 검증, 보안 검토를 대체하지는 않는다.

**미실행 검토 제안:** 공개 예제 수준의 5개 노드만 정하고, 연결 방향·그룹·배포선의 정답 표를 먼저 만든다. 이후 생성물을 평가할 때 다음을 분리한다.

1. 명시한 관계와 추론해 추가한 관계를 구분했는가?
2. 각 로고의 manifest URL·다운로드 시점·파일 해시를 남길 수 있는가?
3. 긴 한국어 이름, 양방향 연결, 밝은/어두운 테마에서 라벨이 읽히는가?
4. HTML의 외부 참조와 스크립트를 검토하고, PNG를 만들 실행 환경의 권한을 제한할 수 있는가?

**다음 질문:** 편집하기 좋은 HTML이라는 장점을 유지하면서, 사람이 승인한 토폴로지와 에이전트가 추정한 표현을 어떻게 구분해 남길 것인가?

[원문 저장소](https://github.com/caru-ini/stack-diagram) · [[기술-레이더/tools|기술 레이더 도구]]
