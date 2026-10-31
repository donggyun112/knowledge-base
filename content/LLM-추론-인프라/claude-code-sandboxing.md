---
title: 에이전트 샌드박스의 파일과 네트워크 경계
source: https://www.anthropic.com/research/claude-code-sandboxing
type: article
category: LLM-추론-인프라
tags: [research, agent, sandbox, security, technology-radar]
researched: 2026-10-31
radar_quadrant: Platforms
radar_ring: Assess
reading_status: unread
---

# 에이전트 샌드박스의 파일과 네트워크 경계

코딩 에이전트가 명령을 실행할 때마다 승인을 요구하면 사용자는 확인을 반복해야 한다. Anthropic의 이 글은 미리 정한 실행 경계를 운영체제 수준에서 강제하고, 그 안에서 작업하도록 만드는 설계를 소개한다.

- **원문**: [Beyond permission prompts: making Claude Code more secure and autonomous](https://www.anthropic.com/research/claude-code-sandboxing)
- **발행 주체**: Anthropic Engineering
- **발행일**: 2025-10-20
- **수집일**: 2026-10-31 KST
- **레이더**: Platforms / Assess
- **읽기 상태**: 읽기 전

## 두 경계를 함께 다룬다

파일시스템 경계는 접근하거나 수정할 경로를 제한한다. 네트워크 경계는 연결할 서버를 제한한다. 글은 두 제약을 함께 적용하고, 명령에서 파생된 프로그램과 하위 프로세스에도 제약이 이어지도록 설명한다.

클라우드 실행 사례에서는 자격 증명을 실행 환경 바깥에 두고 프록시가 저장소와 브랜치 범위를 검사한 뒤 인증을 붙이는 구조를 소개한다. 실행 권한과 실제 자격 증명의 보관 위치를 분리하는 참고 사례다. [원문](https://www.anthropic.com/research/claude-code-sandboxing)

## 위임과 승인 설계에 활용할 점

아래는 원문을 바탕으로 검토할 설계 질문이다.

- 부모가 하위 프로세스나 에이전트에 위임할 때 허용 경로와 호스트를 더 좁힐 수 있는가?
- 경계 밖 작업의 승인 대상과 실행 주체를 함께 기록하는가?
- 승인한 뒤 명령이나 인자가 바뀌면 이전 승인이 그대로 사용되는가?
- 자격 증명 자체를 전달하지 않고 제한된 작업만 대행할 수 있는가?

## 검증 범위와 한계

공급자의 구현 사례이며, 이 지식베이스에서 재현하거나 보안을 검증한 결과는 아니다. 격리의 실효성은 운영체제, 설정, 허용 경로와 호스트에 따라 달라진다. 허용된 범위 안에서 잘못된 파일을 수정하는 행동은 별도 정책과 결과 검토가 필요하다.

**다음 실험 후보**는 임시 환경에서 허용 경로 쓰기, 금지 경로 접근, 비허용 호스트 연결과 하위 프로세스의 경계 상속을 확인하는 것이다. 실제 사용자 데이터나 자격 증명 대신 테스트용 자원으로 재현한다. 아직 실행하지 않았다.

## 관련 노트

[[microvm-isolation-2026|MicroVM 격리]] · [[../에이전트-스킬/agent-status-protocol|상태 보고와 권한 있는 격리 결정]] · [[../TECHNOLOGY-RADAR|기술 레이더 운영 기준]]
