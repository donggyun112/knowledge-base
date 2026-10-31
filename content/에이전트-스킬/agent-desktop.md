---
title: Agent Desktop — 접근성 트리로 조작하고 전달 결과로 재시도를 판단하기
source: https://github.com/vercel-labs/agent-desktop
type: repo
category: 에이전트-스킬
tags: [research, agent, computer-use, accessibility, tools, technology-radar]
researched: 2026-11-01
source_commit: 5261b5287b5208e7c4bf3713df6f66faaaf2c4cc
radar_quadrant: Tools
radar_ring: Assess
reading_status: unread
---

# Agent Desktop — 접근성 트리로 조작하고 전달 결과로 재시도를 판단하기

**Agent Desktop은 에이전트가 데스크톱 앱을 관찰하고 조작하도록 만드는 Rust 기반 CLI와 C 라이브러리다.** 운영체제의 접근성 트리에서 버튼·입력란 같은 요소를 읽고, 요소에 붙인 참조로 행동한다. 계획을 세우고 다음 행동을 선택하는 에이전트 자체는 아니다.

눈여겨볼 부분은 좌표 추측을 줄이는 것뿐 아니라 **대상 식별, 명령 전달, 결과 검증을 구분하는 계약**이다. 오래된 참조를 거부하고 전달 여부가 불확실한 작업을 무작정 다시 실행하지 않도록 설계한다. 모든 앱에서 동작하거나 모든 재시도가 안전하다는 보장은 아니다. [README](https://github.com/vercel-labs/agent-desktop/blob/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc/README.md)

> [!info] 조사 기준
> 수집일은 **2026-11-01 KST**다. 원문은 커밋 `5261b5287b52`에 고정했다. 이 커밋의 시각은 2026-10-31 13:48 UTC이며 프로젝트 최초 발행일을 뜻하지 않는다. Cargo workspace 버전은 **1.0.2**, JSON 응답 계약은 **2.5**로 서로 다른 버전이다. 공식 문서와 관련 소스를 읽었으며 도구를 설치·실행하거나 OS별 동작을 재현하지 않았다. 레이더는 **Tools / Assess**, 사용자 읽기 상태는 **읽기 전**이다. [Cargo.toml](https://github.com/vercel-labs/agent-desktop/blob/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc/Cargo.toml) · [응답 계약](https://github.com/vercel-labs/agent-desktop/blob/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc/docs/json-output.md)

## 관찰과 행동은 어떻게 연결되는가

흐름은 `스냅샷 → 요소 ref 선택 → 행동 → 새 관찰로 확인`이다. 접근성 트리는 역할, 이름, 값과 가능한 행동을 제공하고, CLI는 이를 JSON으로 반환한다. 외부 에이전트가 이 출력을 읽고 다음 명령을 고른다. C ABI를 이용하면 매번 CLI 프로세스를 띄우지 않고 같은 기능을 프로그램 안에서 호출할 수 있다.

저장소는 공통 모델과 행동 계약을 맡는 `crates/core`, OS별 `macos`·`windows`·`linux` 어댑터, `ffi`, CLI인 `src`로 나뉜다. macOS AX, Windows UI Automation, Linux AT-SPI의 서로 다른 역할과 상태를 공통 어휘로 맞춘다. [workspace 구성](https://github.com/vercel-labs/agent-desktop/blob/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc/Cargo.toml) · [공통 개념](https://github.com/vercel-labs/agent-desktop/blob/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc/CONCEPTS.md)

화면이 복잡하면 전체 내용을 한 번에 소비하는 대신 `--skeleton`으로 개요를 얻고 `--root`로 필요한 부분을 더 읽는다. 스냅샷은 시간 예산 때문에 일부만 반환될 수도 있다. `ok: true`여도 `complete: false`라면 관찰하지 못한 부분이 있으며, 찾는 요소가 없다고 단정하면 안 된다. [관찰 규약](https://github.com/vercel-labs/agent-desktop/blob/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc/docs/json-output.md)

## stable ref는 영구 ID가 아니다

ref의 형태는 `@스냅샷ID:e번호`다. 번호만 있는 `@e8`은 거부된다. 스냅샷과 세션 범위 안에서 대상을 가리키며, UI가 바뀌어도 같은 번호가 같은 요소를 영원히 뜻하는 구조는 아니다.

행동 전에 저장된 식별 근거와 현재 UI를 대조한다. 경로·식별자·안정적인 텍스트 등의 근거가 부족하거나 여러 후보가 맞으면 추측해서 실행하는 대신 `STALE_REF` 또는 `AMBIGUOUS_TARGET`으로 거부한다. 새 스냅샷에서 대상을 다시 좁혀야 한다. 위치나 이름 하나만을 절대적인 신원으로 쓰지 않는 접근이다. [Refs And Identity](https://github.com/vercel-labs/agent-desktop/blob/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc/CONCEPTS.md#refs-and-identity)

따라서 통합하는 쪽도 ref를 장기 작업 ID처럼 보관하면 안 된다. 작업의 의도와 완료 조건은 별도로 남기고, 실제 조작 대상은 재관찰로 확인하는 것이 적절하다. 이 문장은 런타임 통합을 위한 설계 제안이다.

## 안전한 재시도는 전달 증거가 있을 때만

공통 코드의 `DeliverySemantics`는 전달 상태에서 재시도 판단을 도출한다. [구현](https://github.com/vercel-labs/agent-desktop/blob/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc/crates/core/src/actions/delivery_semantics.rs)

| delivery | retry | 호출자가 받아들일 의미 |
| --- | --- | --- |
| `not_delivered` | `safe` | 전달되지 않았음이 확인된 경우. 오류의 복구 조건을 따른다 |
| `delivery_uncertain` | `unsafe` | 이미 적용됐을 가능성이 있어 자동 반복하지 않는다 |
| `delivered_unverified` | `unsafe` | 전달은 됐지만 요청한 결과는 확인되지 않았다 |
| `delivered_verified` | `unsafe` | 지정된 사후 상태를 확인했다. 반복할 이유가 되지 않는다 |
| `unknown` | `unknown` | 전달에 대한 근거가 없으므로 자동 반복하지 않는다 |

`TIMEOUT` 같은 오류 이름만 보고 재시도하면 이미 눌린 제출 버튼을 다시 누를 수 있다. 재시도나 대체 행동을 선택하기 전에 `disposition.retry`를 읽고, 불확실하면 현재 상태를 관찰해 다음 판단을 내려야 한다.

소스의 `execute_verified_action`은 상태 확인이 필요한 행동을 실행한 뒤 새 관찰로 사후 조건을 검사한다. 값 쓰기 결과에는 `application_commit: not_verified`를 명시한다. **입력란에 값이 보이는 것과 서버 저장·메시지 전송 같은 업무 결과가 완료된 것은 별개다.** 정확히 한 번 실행이나 애플리케이션 트랜잭션 보장으로 해석할 수 없다. [사후 검증 구현](https://github.com/vercel-labs/agent-desktop/blob/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc/crates/core/src/actions/post_action.rs) · [행동 결과](https://github.com/vercel-labs/agent-desktop/blob/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc/crates/core/src/actions/action_result.rs)

## OS 지원과 접근 권한은 구체적으로 봐야 한다

| 환경 | 확인할 전제와 제한 |
| --- | --- |
| macOS | 접근성 권한이 필요하다. 스크린샷에는 화면 기록 권한도 필요하다 |
| Windows | 터미널과 같은 무결성 수준의 앱이 기본 범위다. 관리자 앱에 입력하려면 실행 주체도 상승 권한이 필요하다 |
| Linux | 사용자 그래픽 세션과 AT-SPI가 필요하다. 문서의 주 대상은 Ubuntu 24.04 이상·GNOME 46이다. Wayland에서는 의미 기반 동작과 별개로 앱 포인터 입력 및 네이티브 창 제어가 제한된다 |

일반 SSH 셸만으로 사용자의 앱 트리를 볼 수 있는 것은 아니다. 세션 버스와 디스플레이 등 실행 환경이 맞아야 한다. 위 표는 조사 커밋의 공식 지원 설명이며 직접 시험한 호환성 표가 아니다. [설치와 플랫폼 조건](https://github.com/vercel-labs/agent-desktop/blob/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc/docs/install.md)

ref 행동은 기본적으로 포커스를 가져오거나 마우스를 움직이지 않는 접근성 호출을 사용한다. 의미 기반 경로가 없으면 거부하고, 물리 입력은 `--headed`로 별도 허용하는 방식이다. 여기서 **headless는 GUI 세션이 필요 없다는 뜻도, 권한 샌드박스라는 뜻도 아니다.** [공식 동작 지침](https://github.com/vercel-labs/agent-desktop/blob/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc/skills/agent-desktop/SKILL.md#headless-and-headed)

## 픽셀 기반 방식과 어떻게 구분할까

이 도구는 화면에서 좌표를 추측하기보다 OS가 제공한 요소와 행동을 사용한다. 스크린샷 기능도 있으므로 이미지 관찰을 전혀 배제하는 제품은 아니다. 다만 접근성 트리가 제공하지 않는 내용까지 자동으로 이해한다는 근거는 없다. 대상 앱이 노출하는 요소·이름·행동의 품질을 먼저 확인해야 한다. [FAQ](https://github.com/vercel-labs/agent-desktop/blob/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc/docs/faq.md)

이 노트의 판단으로는 버튼·폼·메뉴가 의미 있게 노출되는 작업에서 먼저 검토할 만하다. 접근성 정보가 부족한 화면은 시각 관찰을 보완 수단으로 평가하되, 그 경로의 정확도나 안전성이 검증됐다고 가정하지 않는다. 원문만으로 픽셀 기반 도구보다 성공률이 높거나 비용이 낮다고 결론내릴 수는 없다.

## 개인정보와 다음 검증 질문

네이티브 CLI는 원격 모델 서비스를 필수로 요구하지 않는다. 하지만 스냅샷, 창 제목, 클립보드, 스크린샷과 trace에는 개인 정보가 들어갈 수 있고, 이를 외부 모델에 보내는지는 호출자가 결정한다. 별도 JEV helper는 설정된 모델 공급자에게 화면 설명 등을 보낸다. 로컬 도구라는 이유로 전체 처리 흐름이 로컬이라고 볼 수 없다. [개인정보 설명](https://github.com/vercel-labs/agent-desktop/blob/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc/docs/faq.md#what-data-can-contain-private-information)

실험한다면 다음을 분리해 관찰할 필요가 있다. **아직 실행하지 않은 검증 계획**이다.

- 행 삭제나 목록 재정렬 후 오래된 ref가 다른 대상을 조작하지 않고 거부되는가?
- 전달 뒤 timeout이 났을 때 하네스가 자동 재시도를 멈추고 실제 결과를 확인하는가?
- 값 입력 성공과 앱 저장 완료를 서로 다른 완료 조건으로 판정하는가?
- 목표 OS와 실제 앱에서 의미 기반 조작만으로 가능한 범위와 물리 입력이 필요한 범위는 어디인가?

## 관련 자료

[[agent-status-protocol|상태 보고와 실행 결과의 경계]] · [[langgraph-persistence|실행 상태의 보존]] · [[기술-레이더/tools|기술 레이더 도구]]

원문: [vercel-labs/agent-desktop](https://github.com/vercel-labs/agent-desktop) · [조사한 커밋](https://github.com/vercel-labs/agent-desktop/commit/5261b5287b5208e7c4bf3713df6f66faaaf2c4cc). 위 링크들은 변경될 수 있는 main 대신 같은 커밋의 문서와 구현을 가리킨다.
