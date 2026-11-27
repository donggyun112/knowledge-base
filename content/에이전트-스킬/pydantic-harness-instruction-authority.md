---
title: Pydantic AI Harness — 지시문을 어디에 싣는가
source: https://github.com/pydantic/pydantic-ai/releases/tag/v2.75.0
type: implementation
category: 에이전트-스킬
tags: [research, agent, pydantic-ai, skills, mcp, technology-radar]
researched: 2026-11-28
radar_quadrant: Languages and frameworks
radar_ring: Assess
reading_status: unread
---

# Pydantic AI Harness — 지시문을 어디에 싣는가

**한 워크스페이스 안에 있다는 이유만으로 모든 파일이 앱의 지시가 되면 안 된다.** Pydantic AI의 변경은 운영자가 통제하지 않는 파일과 권위를 명시적으로 낮춘 capability의 텍스트를 모델에 어떤 역할과 형태로 전달할지 구분한다.

- **원문**: [v2.75.0 릴리스](https://github.com/pydantic/pydantic-ai/releases/tag/v2.75.0), [워크스페이스 변경 #11837](https://github.com/pydantic/pydantic-ai/pull/11837), [capability와 MCP 지시문 #14457](https://github.com/pydantic/pydantic-ai/pull/14457)
- **확인된 날짜**: GitHub 릴리스 기준 2026-11-25. 아래는 변경이 등장한 버전의 계약이며 최신판이라는 의미가 아니다.
- **수집일**: 2026-11-28 KST
- **상태**: Languages and frameworks / Assess · 읽기 전
- **검증 범위**: 릴리스와 PR 설명·테스트의 정적 검토. 하네스·워크스페이스·MCP 실행 및 마이그레이션 검증은 하지 않았다.

## 1. 출처에 따라 모델 요청 내 위치를 나눈다

| 입력 | 이 버전에서 낮은 권위의 텍스트를 전달하는 방식 |
| --- | --- |
| `RepoContext` 작업 디렉터리 가이드 | 파일의 위치를 안내하고 필요할 때 도구를 통해 읽는다. 상위 디렉터리에서 읽은 가이드는 출처를 붙인 데이터로 전달한다. |
| `Skills` | 운영자용 카탈로그에 넣지 않고 `list_skills`와 `load_skill`을 통해 발견·로드한다. |
| `Memory` | 이미 데이터였던 메모리 스냅샷에 파일 출처와 권위를 표시한다. |
| 권위를 낮춘 capability와 그 MCP 서버 지시문 | 시스템 지시가 아니라 사용자의 메시지 역할에 구분된 데이터 블록으로 전달한다. 기본값인 `operator` capability는 이 변경의 대상이 아니다. |

이 분리는 지시문 출처를 드러내고 앱 지시와 섞이지 않게 한다. 그러나 모델이 데이터 블록을 항상 무시하거나 올바르게 해석한다는 보장은 없다. 파일 접근, 도구 실행, 사용자 승인은 별도의 정책 검사로 결정해야 한다.

## 2. 새 요청의 배치와 기존 실행의 재생은 별도 계약이다

- **워크스페이스**: `RepoContext`와 `Skills`가 경로를 확인하는 `realpath` 호출을 추가했다. 이미 기록된 실행의 호출 순서와 달라질 수 있다. 업스트림은 진행 중 실행을 끝내거나 Temporal 워커 버전 또는 DBOS 앱 버전을 나누라고 안내한다.
- **낮춘 MCP 지시문**: 해당 MCP 뒤에 다른 서버가 오면 업그레이드 경계를 넘는 Temporal·DBOS 실행의 재생이 비결정성 오류를 낼 수 있다. Prefect의 릴리스 주의점은 별개다. 바뀐 캐시 키 때문에 업그레이드 뒤 재시도에서 이미 완료했던 모델 요청이 한 번 다시 실행될 수 있다. 이후 버전 적용 시에는 [캐시 키 후속 변경 #14599](https://github.com/pydantic/pydantic-ai/pull/14599)의 포함 여부를 따로 확인해야 한다.

## 3. 작은 검증 제안

모델을 호출하지 않는 기록용 어댑터를 두고 운영자 가이드, 낮은 권위의 작업 디렉터리 가이드, 스킬, 메모리, MCP 지시문에 서로 다른 합성 표식을 둔다. 모델 요청을 가로채 **역할, 출처, 로드 이전과 이후의 등장 위치**를 입력별로 검사한다. 실행 승인 검사는 따로 두고, 내구성 검증에서는 기존 버전으로 기록한 호출 순서가 같은지 확인한다. 이는 제안이며 실행 결과가 아니다.
