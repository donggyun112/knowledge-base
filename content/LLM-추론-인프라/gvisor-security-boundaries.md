---
title: gVisor — 커널 격리와 데이터 접근 정책의 경계
source: https://gvisor.dev/docs/architecture_guide/intro/
type: documentation
category: LLM-추론-인프라
tags: [research, agent, sandbox, gvisor, security, technology-radar]
researched: 2026-11-10
radar_quadrant: Platforms
radar_ring: Assess
reading_status: unread
---

# gVisor — 커널 격리와 데이터 접근 정책의 경계

**커널 탈출을 어렵게 만드는 격리와, 작업에 어떤 데이터를 허용할지는 서로 다른 결정이다.** 에이전트 실행 환경을 비교할 때 이 두 질문을 분리하기 위한 공식 자료다.

## 출처와 검토 범위

- **대표 원문**: [Introduction to gVisor security](https://gvisor.dev/docs/architecture_guide/intro/)
- **보조 원문**: [Security Model](https://gvisor.dev/docs/architecture_guide/security/)
- **발행 주체**: The gVisor Authors
- **발행·수정일**: 두 문서 본문에 미표기. 페이지 하단의 2026 저작권 표시는 발행일로 사용하지 않았다.
- **수집일**: 2026-11-10 KST
- **레이더 / 읽기 상태**: Platforms / Assess / 읽기 전
- **검증 범위**: 공식 문서 본문 검토. 설치·컨테이너 실행·탈출 시험·성능 측정은 하지 않았다. 특정 릴리스 구현을 감사한 결과가 아니며 문서는 이후 바뀔 수 있다.

## 구조: 애플리케이션과 호스트 사이의 Sentry

gVisor는 단순한 시스템 호출 필터나 VM 하이퍼바이저가 아니라 사용자 공간의 애플리케이션 커널이다. Sentry가 시스템 호출과 페이지 폴트를 처리하고, 필요한 경우 제한된 호스트 호출을 수행한다. 애플리케이션 호출을 그대로 호스트에 전달하는 구조가 아니다. 따라서 Linux 기능의 재구현 여부가 호환성의 조건이 된다. [Introduction](https://gvisor.dev/docs/architecture_guide/intro/)

보안 모델은 두 경계를 둔다. 애플리케이션이 호스트 API를 직접 공격하지 못하게 하고, Sentry 자체가 사용할 수 있는 호스트 API도 줄인다. Gofer는 파일 접근을 중개하는 별도 구성 요소다. 다만 `directfs`나 host networking 설정에 따라 허용되는 호스트 접근이 달라지므로 “Sentry는 파일을 절대 열지 않는다” 같은 무조건적인 설명은 피해야 한다. [Security Model](https://gvisor.dev/docs/architecture_guide/security/)

## 활용: 격리 선택과 권한 설계를 따로 검토한다

아래는 원문에서 도출한 설계 질문이며 제품의 보증이 아니다.

1. **실행 단위**: 서로 신뢰하지 않는 작업이 같은 샌드박스·마운트·자격 증명을 공유하는가? 격리 단위와 작업 소유권을 함께 정의한다.
2. **데이터 경계**: 호스트 탈출이 없어도 허용된 파일을 읽거나 외부로 보낼 수 있는가? 파일 목록과 목적지 정책을 별도로 검토한다.
3. **제어 경로**: 실행 요청이 실제로 지정 런타임을 거쳤는지 어디서 확인하는가? 컨테이너 생성 전 단계의 오류를 내부 격리만으로 해결하려 하지 않는다.

특히 공식 소개의 `runsc do`는 편의 테스트 명령으로 **기본적으로 호스트 전체 파일시스템에 읽기 전용 접근을 제공한다**. 읽기 전용은 기밀성 보장이 아니다. 운영 검토에는 OCI 설정이 노출하는 경로를 기준으로 삼아야 한다. [Introduction](https://gvisor.dev/docs/architecture_guide/intro/)

## 한계와 다음 질문

호스트 커널·하드웨어의 부채널 대응, cgroup 기반 자원 제한, 컨테이너 수준 네트워크 정책은 별도로 필요하다. gVisor가 안전한 전체 아키텍처를 대신하지 않으며, VM보다 무조건 안전하거나 빠르다는 결론도 이 자료에서 도출하지 않는다. [Security Model](https://gvisor.dev/docs/architecture_guide/security/)

**작은 검증 제안, 미실행**: 자격 증명이 없는 임시 환경에서 읽기용 합성 파일과 쓰기용 디렉터리만 명시적으로 마운트한다. 실제 런타임 선택, 허용·비허용 경로, 네트워크 차단, 자원 상한을 각각 확인한다. 같은 작업의 일반 컨테이너 실행과 비교하되 호환성 실패와 정책 거부를 다른 항목으로 기록한다. 이 검사는 설정 확인이지 샌드박스 탈출 불가능성의 증명이 아니다.

다음 질문은 **“작업에 필요한 최소 노출을 유지하면서 목표 워크로드의 호환성과 비용을 만족하는가?”**다. 아직 적용 판단을 내리지 않았다.

## 기존 자료와의 연결

[[claude-code-sandboxing|파일·네트워크 정책 경계]]와 함께 읽으면 실행 허용 정책과 커널 격리를 구분할 수 있다. [[microvm-isolation-2026|MicroVM 비교 글]]에는 gVisor의 간접 소개가 있지만, 이번 노트는 공식 보안 모델과 테스트 명령의 접근 기본값을 별도로 확인한다.

[[../기술-레이더/platforms|플랫폼 레이더]] · [[../TECHNOLOGY-RADAR|운영 기준]]
