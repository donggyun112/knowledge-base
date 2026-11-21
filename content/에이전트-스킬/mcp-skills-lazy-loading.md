---
title: MCP Skills — 목록 발견과 본문 로드를 분리하기
source: https://skills.extensions.modelcontextprotocol.io/specification/beta/skills
type: documentation
category: 에이전트-스킬
tags: [mcp, agent-skills, lazy-loading, technology-radar]
researched: 2026-11-21
radar_quadrant: Techniques
radar_ring: Assess
reading_status: unread
---

# MCP Skills — 목록 발견과 본문 로드를 분리하기

스킬을 찾는 데 스킬 파일을 전부 읽을 필요는 없다. MCP Skills는 호스트가 **목록에서 스킬의 설명과 파일 명세를 확인하고, 쓰기로 한 스킬의 본문과 자료만 필요할 때 가져오는** 계약이다. 실행할 환경을 언제 준비할지는 별개의 문제다.

- **수집일**: 2026-11-21 KST
- **발행일**: Beta 명세 본문에 미표기. SEP-2640의 Final 상태와 확장 자체의 Beta 상태는 별개다.
- **검증 범위**: 공개 명세 정적 검토. 클라이언트 연동, 스킬 실행, 비용·지연 측정은 하지 않았다.

## 명세가 정하는 경계

| 시점 | 호스트가 쓰는 정보 |
| --- | --- |
| 발견 | 서버가 확장을 선언하면 `skills/list`로 스킬을 발견한다. 항목은 이름·설명 등 frontmatter와 파일 명세를 담는다. 정적 스킬의 항목은 완전한 파일 목록·크기·해시를 포함하므로 항목마다 `skills/get`으로 보완할 필요가 없다. |
| 활성화와 참조 | `SKILL.md`는 로드할 때, 참조 파일은 읽을 때 `resources/read`로 가져온다. 연결·목록 조회·승인 시점에 파일을 미리 받으면 안 된다. `resources/directory/read`는 서버가 `directoryRead: true`를 선언한 경우에만 쓸 수 있다. |
| 검증과 실행 | 정적 파일은 크기와 SHA-256을, `SKILL.md`는 목록과 frontmatter의 일치까지 확인한다. 원격 스킬은 신뢰되지 않는 입력이며, 스킬이 호스트에서 코드를 실행하려면 스킬별 명시적 사용자 승인이 필요하다. |

출처가 다른 동명 스킬은 서로 바꿔 쓰지 않는다. 호스트는 스킬을 서버 출처와 URI의 조합으로 식별한다. 해시는 목록과 받은 바이트의 일관성을 보여줄 뿐, 서버의 신뢰성을 증명하지 않는다. 파일 목록 대신 `dynamic`을 선언한 스킬은 해시로 콘텐츠를 묶지 못하므로, 이전 승인을 현재 내용 전체에 적용할 수 없으며 호스트가 로드를 거부할 수 있다.

## 적용할 때 남는 질문

확장은 선택 사항이다. 이 문서는 파일 배포 계약을 정할 뿐, 모델에 어떤 후보를 먼저 노출할지, 카탈로그를 DB에 둘지, 스킬을 언제 샌드박스에 옮길지, 특정 클라이언트가 지원하는지는 정하지 않는다.

설계 후보로는 호스트 카탈로그에서 스킬을 고르고 파일을 읽는 경로와, 명시적 승인 뒤 격리 환경에서 실행하는 경로를 나눌 수 있다. 비교한다면 **스킬이 필요 없는 요청에서 본문을 가져오지 않는지**, **선택된 스킬도 안 쓴 참조 파일은 가져오지 않는지**, **동명 스킬이나 변경된 파일에 이전 승인이 적용되지 않는지**를 각각 확인하는 편이 낫다. 파일 읽기 횟수와 첫 활성화 지연은 별도로 측정해야 한다.

## 출처

- [MCP Skills Extension Beta 명세](https://skills.extensions.modelcontextprotocol.io/specification/beta/skills)
- [SEP-2640: Skills Extension](https://modelcontextprotocol.io/seps/2640-skills-extension)
- [Agent Skills 형식 명세](https://agentskills.io/specification)
