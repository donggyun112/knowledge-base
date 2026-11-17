---
title: Miroir — 같은 시작 상태에서 에이전트의 실제 결과를 채점하기
source: https://github.com/raphaelDkhn/miroir
type: article
category: 논문-아티클
tags: [agent-evaluation, harness, state, technology-radar]
researched: 2026-11-17
radar_quadrant: Tools
radar_ring: Assess
reading_status: unread
---

# Miroir — 같은 시작 상태에서 에이전트의 실제 결과를 채점하기

[[논문-아티클/agent-eval-outcomes-and-trials|에이전트 평가 설계]]가 실행 기록과 실제 결과를 왜 분리해야 하는지 설명한다면, Miroir는 **시작 상태를 복원하고 결과를 채점하는 구현**을 보여준다. 모델이 “완료했다”고 답했는지가 아니라, 요청한 변화가 실제로 일어났고 요청하지 않은 변화는 없었는지를 본다.

- **원문**: [공식 저장소](https://github.com/raphaelDkhn/miroir), Apache-2.0
- **발행일**: 공식 문서 본문에 미표기. [문서 공개 커밋](https://github.com/raphaelDkhn/miroir/commit/7b963df471b5de4c5d2f56e17d321fa6678e79da)은 2026-11-16.
- **수집일 / 상태**: 2026-11-17 KST · Tools / Assess / 읽기 전
- **검증 범위**: 고정 커밋의 문서와 공개 예제 검토. 설치, 실행, 모델 호출, 결과 재현은 하지 않았다.

## 무엇을 초기화하고 무엇을 채점하는가

1. [환경 준비와 리셋](https://raphaeldkhn.github.io/miroir/introduction.html): Docker 이미지에 대상 앱과 과제 정의를 넣는다. 준비 시 앱을 띄워 시드 데이터를 만들고, 각 실행 전 앱 프로세스를 멈춘 뒤 시드 상태를 복원한다. 날짜는 상대적 나이를 유지하도록 조정한다.
2. [효과 기록](https://raphaeldkhn.github.io/miroir/features/sinks.html): 앱이 설정된 로컬 SMTP·HTTP 수신기로 보낸 요청을 기록해, 예를 들어 알림이 정확히 한 번 나갔는지 검사할 수 있다. 수신기로 향하지 않은 요청은 기록하거나 차단하지 않는다. 이 장치는 네트워크 격리를 대신하지 않는다.
3. [결과 채점](https://raphaeldkhn.github.io/miroir/make/grading.html): 앱의 DB 변경 로그를 시작과 종료 사이의 순변화로 접고, 검사 조건과 허용 변경 범위를 적용한다. 요청은 완료했어도 다른 레코드를 변경하면 별도의 위해 판정을 받을 수 있다. 기록이 깨져 채점할 수 없는 실행은 모델 실패로 세지 않고 무효로 구분한다.

## 사례와 한계

[공식 Gitea 예제](https://github.com/raphaelDkhn/miroir/blob/7b963df471b5de4c5d2f56e17d321fa6678e79da/examples/gitea/README.md)는 수정하지 않은 Gitea로 12개 과제 유형, 총 144개 과제를 구성했다고 보고한다. 세 개의 합성 환경을 사용하고 평가용 환경은 사용자를 비롯한 데이터가 분리되어 있다. 이 숫자는 과제 구성의 규모이지, 에이전트가 해결한 과제 수나 실제 업무 성능이 아니다. 예제의 입력 경로는 REST API이며, 웹 UI나 장기 작업 일반화는 검증하지 않는다.

DB 순변화만 보면 중간에 바꿨다가 되돌린 동작을 놓칠 수 있다. 반대로 외부 전송 횟수가 중요하다면 최종 DB 상태와 별도로 전송 로그를 검사해야 한다. 좋은 환경을 만드는 비용은 모델 실행뿐 아니라 시드 데이터·허용 범위·채점기가 함께 바뀔 때의 유지보수에도 있다.

## 다음 질문

작은 합성 과제 하나에서 같은 시드로 **정상 완료 / 완료 주장만 함 / 목표는 달성했지만 다른 레코드도 변경 / 같은 알림을 두 번 발송**을 비교한다. 성공, 범위 위반, 외부 효과 중복을 별도 항목으로 판정하고, 재시작 뒤 같은 과제를 돌릴 때 이전 실행의 상태가 남지 않는지도 살펴본다. 이 노트에서 그 실험을 실행한 것은 아니다.
