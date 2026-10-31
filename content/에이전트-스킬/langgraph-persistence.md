---
title: LangGraph의 실행 상태와 장기 메모리
source: https://docs.langchain.com/oss/python/langgraph/persistence
type: docs
category: 에이전트-스킬
tags: [research, agent, persistence, memory, technology-radar]
researched: 2026-10-31
radar_quadrant: Languages and frameworks
radar_ring: Assess
reading_status: unread
---

# LangGraph의 실행 상태와 장기 메모리

에이전트가 작업을 멈췄다가 이어 가려면 실행 위치를 기억해야 한다. 여러 대화에서 얻은 사실을 재사용하려면 대화 하나보다 오래 남는 저장소도 필요하다. LangGraph의 Persistence 문서는 이 두 용도를 체크포인터와 스토어로 나눈다.

- **출처**: [LangChain 공식 Persistence 문서](https://docs.langchain.com/oss/python/langgraph/persistence)
- **발행일**: 문서에 명시 없음
- **수집일**: 2026-10-31 KST
- **레이더**: Languages and frameworks / Assess
- **읽기 상태**: 읽기 전

## 무엇을 어디에 저장하는가

체크포인터는 한 스레드의 그래프 상태를 보존한다. 대화 연속성, 사람의 개입, 상태 되돌아보기와 장애 복구에 사용한다. 스토어는 그래프 상태 바깥에서 애플리케이션이 정의한 데이터를 여러 스레드에 걸쳐 저장한다. 선호, 사실과 공유 지식이 그 예다.

메모리에만 저장하는 체크포인터는 프로세스가 재시작되면 사라진다. 중단 뒤에도 이어 가야 하는 작업이라면 영속 저장 매체와 보존 정책까지 검토해야 한다. [공식 문서](https://docs.langchain.com/oss/python/langgraph/persistence)

## 설계에 활용할 질문

실행 상태와 장기 지식의 수명·접근 범위·삭제 조건을 구분하는 데 참고할 수 있다. 다음은 이 노트의 검토 제안이다.

- 승인 대기 중 프로세스를 종료했을 때 어느 실행 위치와 승인 대상을 복구해야 하는가?
- 다른 스레드가 읽어도 되는 정보와 현재 작업에만 속하는 정보를 어떻게 구분하는가?
- 체크포인트를 삭제해도 장기 지식의 출처를 추적할 수 있는가?

## 검증 범위와 한계

이 노트는 저장 모델을 살펴본 자료 정리이며 구현을 실행한 결과가 아니다. 상태 저장만으로 외부 API 호출의 중복 실행 방지나 재개 시 승인 유효성이 보장되지는 않는다. 부수 효과의 멱등성, 실행 결과가 불확실한 경우의 복구, 권한 재검증은 따로 확인해야 한다.

**다음 실험 후보**는 승인 대기 전후에 프로세스를 재시작하고, 같은 외부 작업이 중복 실행되는지 관찰하는 것이다. 아직 실행하지 않았다.

## 관련 노트

[[agent-status-protocol|상태 보고와 실행 복구의 경계]] · [[../TECHNOLOGY-RADAR|기술 레이더 운영 기준]]
