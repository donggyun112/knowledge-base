---
title: Lightpanda — 픽셀 대신 DOM과 JavaScript에 집중한 자동화 브라우저
source: https://github.com/lightpanda-io/browser
type: repo
category: 에이전트-스킬
tags: [research, browser, automation, cdp, mcp, tools, technology-radar]
researched: 2026-11-01
source_commit: 97c67d4ba672a9d96acfcd04d6b10a7bc6a43139
radar_quadrant: Tools
radar_ring: Assess
reading_status: unread
---

# Lightpanda — 픽셀 대신 DOM과 JavaScript에 집중한 자동화 브라우저

**Lightpanda는 Chromium 포크가 아니라 Zig로 만든 별도 headless 브라우저다.** 웹페이지의 DOM과 JavaScript를 다루되 일반 브라우저의 그래픽 렌더링 파이프라인은 두지 않는다. 화면 재현보다 동적 페이지의 데이터 추출과 자동화가 중요한 작업에서 검토할 만하다. [고정 README](https://github.com/lightpanda-io/browser/blob/97c67d4ba672a9d96acfcd04d6b10a7bc6a43139/README.md)

이 노트의 판단은 **Chrome 전체를 바로 교체하기보다, 목표 사이트에서 호환성과 실패 처리를 검증한 뒤 선택적으로 쓰는 후보**라는 것이다. V8과 CDP를 사용한다는 사실만으로 Chrome과 같은 웹 호환성이나 모든 기존 스크립트의 동작이 보장되지는 않는다.

> [!info] 조사 기준
> 수집일은 **2026-11-01 KST**다. 저장소 README와 라이선스는 커밋 `97c67d4ba672`에 고정했다. 공식 웹 문서는 같은 날 열람한 내용이며 이후 바뀔 수 있다. 문서·벤치마크 자료 검토이며 Lightpanda를 설치하거나 실행하지 않았다. 레이더는 **Tools / Assess**, 사용자 읽기 상태는 **읽기 전**이다.

## 무엇을 실행하고 무엇을 생략하는가

네트워크는 libcurl, HTML 파싱은 Rust의 html5ever, JavaScript는 V8을 사용한다. 그 위에서 DOM과 Web API를 제공한다. V8은 JavaScript 엔진이고, 브라우저 전체의 API·레이아웃 구현과는 구분해야 한다. [README의 구성 요소](https://github.com/lightpanda-io/browser/blob/97c67d4ba672a9d96acfcd04d6b10a7bc6a43139/README.md#build-from-sources)

공식 아키텍처는 공유 서비스를 가진 `App` 아래에 `Browser → Session → Page → Frame`을 둔다. Browser는 V8 isolate를, Session은 쿠키와 Web Storage를, Frame은 DOM과 Web API를 소유한다. 실행 문맥과 로그인 상태의 수명을 구분하는 데 참고할 구조다. [아키텍처 설명](https://lightpanda.io/docs/core-concepts/architecture-overview)

## 기존 자동화와 에이전트는 어떻게 연결하는가

| 진입점 | 용도 |
| --- | --- |
| `fetch` | 페이지를 가져와 HTML·Markdown·구조화 데이터 등으로 출력 |
| `serve` | CDP 또는 WebDriver BiDi로 자동화 클라이언트 연결 |
| `mcp` | 외부 에이전트에 탐색·읽기·추출·조작 도구 제공 |
| `agent`와 `run` | 내장 에이전트로 작업을 구성하고 PandaScript로 저장·재실행 |

Puppeteer와 Playwright 같은 CDP 클라이언트를 연결하는 경로가 있다. Playwright는 기존 브라우저를 실행하는 대신 CDP 서버에 연결하는 방식으로 설명된다. 연결 프로토콜이 같아도 미지원 Web API나 동작 차이가 있는지는 대상 사이트에서 확인해야 한다. [공식 Playwright 문서](https://lightpanda.io/docs/usage/cdp/playwright)

현재 고정 README에는 native MCP, HTTP 세션, WebDriver BiDi와 내장 agent가 모두 있다. 과거 버전의 기능 제한을 현재 제품 전체에 적용하지 않는 것이 중요하다. PandaScript는 작업을 JavaScript와 내장 브라우저 연산으로 저장해 LLM 없이 실행하는 경로다. **모델 호출 없이 재실행한다는 것과 외부 사이트의 결과가 매번 같다는 것은 별개다.** [README의 agent와 MCP](https://github.com/lightpanda-io/browser/blob/97c67d4ba672a9d96acfcd04d6b10a7bc6a43139/README.md#agent-mode)

## screenshot이라는 이름만으로 화면 재현을 기대하면 안 된다

MCP의 `screenshot`은 **텍스트 레이아웃을 PNG로 만드는 출력**이다. 이미지·폰트·CSS 색상을 실제 브라우저처럼 재현하는 픽셀 정확한 렌더링이 아니다. CLI의 PNG/PDF 출력도 text-only로 설명된다. 이미지 출력 기능 자체가 없다는 설명도 현재 기능과 맞지 않는다. [MCP 도구 문서](https://lightpanda.io/docs/reference/mcp-tools#reading-the-page) · [고정 README](https://github.com/lightpanda-io/browser/blob/97c67d4ba672a9d96acfcd04d6b10a7bc6a43139/README.md#dump-a-url)

아키텍처 문서도 요소 위치를 DOM 깊이와 형제 순서 등으로 모사하며 실제 시각적 레이아웃과 다르다고 설명한다. 따라서 시각 회귀, 실제 배치·스타일 검증과 픽셀 기반 행동을 평가할 때는 그래픽 렌더링을 갖춘 브라우저가 필요하다. [렌더링 경계](https://lightpanda.io/docs/core-concepts/architecture-overview#why-theres-no-rendering-engine)

## 세션과 성공 응답을 어떻게 해석할까

MCP HTTP에서 초기화가 반환한 `Mcp-Session-Id`를 이후 요청에 유지해야 같은 세션에 머문다. 같은 ID를 공유하면 같은 browsing context를 공유한다. 공식 문서는 헤더 없는 일반 호출이 default 세션을 사용한다고 설명하므로, 에이전트마다 저절로 분리된다고 가정하지 말아야 한다. [세션 연결](https://lightpanda.io/docs/usage/mcp#http-transport)

또한 `goto`의 **`isError: false`만으로 원하는 페이지를 얻었다고 판단하면 안 된다.** 404·500 응답이나 로딩 timeout도 성공 형태로 반환될 수 있다. `structuredContent.httpStatus`, 최종 URL과 목표 내용을 확인해야 한다. DNS 실패나 접속 거부 같은 탐색 실패와 구분하는 계약이다. [Known behaviors](https://lightpanda.io/docs/usage/mcp#known-behaviors)

늦게 끝나는 스크립트 때문에 로딩 완료를 기다리는 작업에서는 `domcontentloaded` 뒤 목표 selector를 기다리는 전략을 공식 도구 문서가 제안한다. 계속 백그라운드 활동이 있는 페이지에 `done`을 일률적으로 적용하면 timeout까지 기다릴 수 있다. [대기 조건](https://lightpanda.io/docs/reference/mcp-tools#navigation-and-search)

**통합 설계 제안:** 세션을 사용자·작업 단위로 나누고 종료를 명시한다. 읽기 실패에는 제한된 재시도를 검토하되, 폼 제출 같은 쓰기 작업은 실제 결과를 확인하기 전에 반복하지 않는다. 프로토콜 성공, 원하는 데이터 확보, 외부 부수 효과의 완료를 별도 조건으로 기록한다.

## 9배와 16배라는 수치는 어디까지 읽어야 하나

README는 약 9배 빠른 실행과 16배 적은 메모리를 내세운다. 개발팀의 상세 crawler benchmark는 **Amiibo 데모 933 URL**, 인터넷 요청, AWS **m5.xlarge**, Go chromedp를 사용한다. Chrome `143.0.7499.169`와 Lightpanda `7b1f157cf8cc`를 비교한 측정이다. 현재 조사 커밋을 직접 비교한 결과가 아니다.

그중 Lightpanda **25프로세스**는 4.81초·메모리 peak 123.0M, Chrome **25탭**은 46.70초·2.0G로 기록돼 있다. 같은 개수라도 프로세스와 탭의 실행 구성이 다르다. 메모리는 문서에서 `smem`의 PSS로 관찰한 peak다. [고정 벤치마크 문서](https://github.com/lightpanda-io/demo/blob/24fc4dd0bd0ebddfa526db05cc609204f56bfaaa/BENCHMARKS.md#crawler-benchmark)

주의할 불일치도 있다. 조사한 README 본문은 **m5.large**, 요약 표는 **100 pages**라고 적지만, 연결된 상세 crawler 문서는 **m5.xlarge·933 URL**이다. 이 노트는 서로 다른 조건을 하나의 일반 성능 보장으로 합치지 않는다. 개발팀 측정은 후보를 고르는 근거로 삼고, 실제 도입에서는 목표 사이트의 성공률·지연·동시 실행 시 메모리를 함께 측정해야 한다. [README](https://github.com/lightpanda-io/browser/blob/97c67d4ba672a9d96acfcd04d6b10a7bc6a43139/README.md#benchmarks)

## 실행 환경과 운영 전 확인할 것

고정 README는 Linux/macOS의 x86_64·aarch64 바이너리와 Linux Docker 이미지를 안내한다. 네이티브 Windows 바이너리 대신 WSL 경로를 사용하며, Linux 배포 바이너리는 glibc 기반이다. 기본 사용량 telemetry는 `LIGHTPANDA_DISABLE_TELEMETRY=true`로 끌 수 있다. [환경과 telemetry](https://github.com/lightpanda-io/browser/blob/97c67d4ba672a9d96acfcd04d6b10a7bc6a43139/README.md)

프로젝트의 기본 라이선스 표기는 **AGPL-3.0-only**다. 배포·서비스 구성에 맞는 검토 항목으로 남긴다. [LICENSING.md](https://github.com/lightpanda-io/browser/blob/97c67d4ba672a9d96acfcd04d6b10a7bc6a43139/LICENSING.md)

다음은 아직 실행하지 않은 검증 순서다.

1. 브라우저와 클라이언트 버전을 고정하고 핵심 사이트의 로그인·리디렉트·폼·동적 데이터 작업을 정한다.
2. HTTP 오류, timeout, 미지원 API와 인증 실패를 구분해 기록한다.
3. 병렬 작업의 세션 격리와 쿠키·로그 보존 범위를 확인한다.
4. 호환성 실패에만 선택적으로 일반 브라우저를 쓰는 fallback을 평가한다. 인증 상태 전환도 검증한다.
5. 성공한 작업만 골라 속도를 비교하지 않고 실패율을 포함한 부하 결과를 비교한다.

## Agent Desktop과의 위치

[[agent-desktop|Agent Desktop]]은 OS 접근성 트리로 데스크톱 앱을 조작한다. Lightpanda는 웹 문서의 DOM과 JavaScript 실행 환경을 제공한다. 두 도구는 대상이 다른 자동화 계층이다. Lightpanda의 semantic DOM tree나 웹 AX 정보를 OS 전체의 접근성 제어로 혼동하지 않는다.

[[기술-레이더/tools|기술 레이더 도구]] · [원문 저장소](https://github.com/lightpanda-io/browser) · [조사 커밋](https://github.com/lightpanda-io/browser/commit/97c67d4ba672a9d96acfcd04d6b10a7bc6a43139)
