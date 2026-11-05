---
title: LLM Architecture Gallery — 모델 구조와 추론 메모리의 비교 기준
source: https://sebastianraschka.com/llm-architecture-gallery/
type: tool
category: LLM-추론-인프라
tags: [llm, inference, kv-cache, architecture, technology-radar]
researched: 2026-11-05
radar_quadrant: Tools
radar_ring: Assess
reading_status: unread
---

# LLM Architecture Gallery — 모델 구조와 추론 메모리의 비교 기준

모델 이름과 파라미터 수만으로 서빙 자원을 판단하기 어렵다. 이 자료는 구조 차이를 확인하고, 가중치와 KV 캐시의 메모리 부담을 따로 생각하는 출발점이다. 모델 선택의 결론이나 성능 검증 결과는 아니다.

- **원문·제작자**: [LLM Architecture Gallery](https://sebastianraschka.com/llm-architecture-gallery/), Sebastian Raschka
- **관련 도구**: [LLM Memory Calculator](https://sebastianraschka.com/llm-architecture-gallery/memory-calculator/)
- **최초 발행일**: 갤러리 본문에 미표기
- **확인된 갱신일**: 갤러리 표시는 2026-11-04. 계산기의 별도 수정일은 미확인
- **수집일**: 2026-11-05 KST
- **레이더·읽기 상태**: Tools / Assess / 읽기 전
- **검증 범위**: 제작자 페이지와 계산식 설명 검토. 동적 UI 조작, 모델 설치·추론 및 메모리 실측은 하지 않았다.

## 원문이 제공하는 비교

수집 시점에 119개 모델 카드가 표시된다. 구조도, attention 방식, decoder 유형, 층 구성, 전체·활성 파라미터, 컨텍스트 길이와 출처 링크를 함께 제공한다. 검색·필터와 두 모델 나란히 비교하기가 있다. 카드마다 논문·설정 파일·직접 구현 링크의 제공 범위는 다르다.

범위는 텍스트 모델과 멀티모달 모델의 **언어 백본**이다. 비전·오디오 구성 전체를 비교하는 목록으로 읽으면 안 된다. 예를 들어 GPT-2의 MHA와 Llama 3의 GQA를 비교하거나, 같은 기본 구조를 사용하는 DeepSeek V3와 R1에서 구조와 학습법을 구별하는 데 쓸 수 있다. 이는 구조를 읽는 예시이지 우열의 실험 결과가 아니다. [갤러리 본문](https://sebastianraschka.com/llm-architecture-gallery/)

## 계산기가 세는 것

가중치와 KV 캐시 정밀도는 별도로 지정한다. 원문의 산식은 다음과 같다.

- 가중치 바이트 = 전체 파라미터 수 × 가중치 비트 수 ÷ 8
- KV 캐시 바이트 = BF16 기준 토큰당 캐시 바이트 × 시퀀스 길이 × 배치 크기 × 캐시 비트 수 ÷ 16

원문 예제의 Qwen3 8B는 BF16 캐시 144 KiB/토큰이며, 32,768토큰·배치 1에서 캐시 4.5 GiB, 16비트 가중치는 약 14.90 GiB로 계산한다. **이는 측정치가 아니라 반올림된 파라미터 수와 캐시 표현에 기반한 추정치다.**

MoE에서도 상주 가중치는 전체 expert를 포함한다. 토큰당 활성 파라미터가 적다는 사실로 상주 메모리를 그 비율만큼 줄여 계산하지 않는다. 가중치는 배치에서 공유하지만 예제의 시퀀스별 캐시는 별개다. [계산식·가정](https://sebastianraschka.com/llm-architecture-gallery/memory-calculator/)

## 한계: GPU에 들어간다는 보장이 아니다

계산기는 activation, prefill 임시 공간, allocator 여유분, 양자화 부가정보와 다중 GPU 분산·CPU offload를 포함하지 않는다. 선택한 정밀도를 실제 런타임이 지원하는지도 별도 문제다.

Sliding-window·chunked 모델도 각 층의 보존 한도가 없어 전체 토큰 보존으로 투영한다. 실제 eviction은 캐시를 줄일 수 있고, 반대로 고정 recurrent state나 별도 index buffer 등 빠진 상태가 있다. 따라서 모든 모델에서 똑같이 정확한 상한·하한으로 취급할 수 없다. [계산기의 명시적 제외 항목](https://sebastianraschka.com/llm-architecture-gallery/memory-calculator/)

## 활용 해석과 다음 질문

아래는 이 노트의 검토 제안이며 실행 결과가 아니다.

1. 후보 모델의 정확한 revision과 설정 파일을 고정하고, 층 수·KV head·head dimension을 확인한다. 카드의 요약과 다른 부분은 원문 설정을 기준으로 기록한다.
2. 비교할 입력·출력 길이, 동시 시퀀스 수와 정밀도를 먼저 고정한다. 모델 간 최대 컨텍스트 길이를 그대로 비교하면 조건이 달라진다.
3. 별도 승인된 실험에서는 동일 런타임으로 prefill 최고점과 decode 중 메모리를 따로 측정하고 추정치와의 차이를 분해한다.
4. prefix 공유, 캐시 eviction, 양자화와 tensor parallel 설정을 바꿨다면 새로운 조건으로 기록한다. 이 계산기만으로 지연·처리량·응답 품질의 개선을 주장하지 않는다.

**남은 질문:** 실제 워크로드에서 한계가 되는 것은 가중치인가, 긴 컨텍스트와 동시 요청의 캐시인가, 아니면 계산기에 빠진 임시 메모리인가?

## 결정 이력

- **2026-11-05**: 제작자 자료를 Tools / Assess로 수집했다. 서빙 자원 비교를 위한 참고 도구이며 직접 검증·채택하지 않았다. 읽기 상태는 읽기 전이다.

[[기술-레이더/tools|기술 레이더 도구]] · [[index|주제별 전체 목차]]
