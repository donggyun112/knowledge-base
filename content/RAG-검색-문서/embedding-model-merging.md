---
title: 임베딩 모델 병합 — 호환성 검사와 검색 평가를 분리하기
source: https://www.sbert.net/examples/sentence_transformer/training/merging/README.html
type: docs
category: RAG-검색-문서
tags: [research, embeddings, retrieval, model-merging, technology-radar]
researched: 2026-11-01
source_commit: 7bfaf1ccb3dcacd613aeec668e9f0921991e366a
radar_quadrant: Techniques
radar_ring: Assess
reading_status: unread
---

# 임베딩 모델 병합 — 호환성 검사와 검색 평가를 분리하기

**모델을 병합할 수 있다는 것과 검색 품질이 좋아진다는 것은 다른 주장이다.** Sentence Transformers의 공식 문서는 공통 기반 모델에서 나온 체크포인트를 추가 학습 없이 결합하는 방법과 그 제약을 설명한다.

> [!info] 조사 기준
> 수집일: **2026-11-01 KST**. 발행일은 문서에 미표기. 공식 문서와 예제를 커밋 `7bfaf1ccb3dc` 기준으로 확인했다. **Techniques / Assess · 읽기 전**이며 설치·병합·성능 실험은 하지 않았다.

## 무엇을 합치는가

이 API는 mergekit을 통해 호환되는 모델의 **가중치**를 결합한다. 검색 결과를 합치는 방식이나 실행 시 여러 모델을 호출하는 앙상블과 구분해야 한다. 결과는 입력과 같은 아키텍처의 모델이다. 일부 과제는 개선돼도 다른 과제는 악화될 수 있다. [공식 문서](https://www.sbert.net/examples/sentence_transformer/training/merging/README.html)

## 먼저 확인할 세 가지

- **구조:** 임베딩 차원만 같아서는 부족하다. 아키텍처, 모듈 구성, tokenizer 어휘, tensor shape와 tied weights가 맞아야 한다. pooling 방식이 다르면 이 API로 병합할 수 없다.
- **계보와 입력 규칙:** 구조 검사는 공통 학습 조상이나 tokenizer 전처리 규칙까지 보장하지 않는다. 설정·프롬프트·processor는 첫 입력에서 상속되므로 입력 순서도 기록한다.
- **자원과 지원 범위:** 기본은 CPU float32이며 입력·기반·결과 모델과 임시 tensor의 메모리가 필요하다. 양자화 모델과 PEFT adapter가 붙은 모델은 지원하지 않는다. adapter는 먼저 기반 가중치에 합치고 해제해야 한다.

위 제약은 [고정 README](https://github.com/huggingface/sentence-transformers/blob/7bfaf1ccb3dcacd613aeec668e9f0921991e366a/examples/sentence_transformer/training/merging/README.md)의 설명이다. 메모리가 절약되는 추론 결과를 기대하더라도 병합 작업 자체의 peak 메모리가 작다는 뜻은 아니다.

## 예제를 읽을 때 놓치기 쉬운 점

공식 예제는 Linear, SLERP와 TIES를 비교한다. 특히 TIES 예제의 `base_model=inputs[0]`에서는 첫 입력이 기준점이고 **두 번째 입력만 task vector에 기여한다.** 두 전문가의 변화량을 모두 합친 실험으로 읽으면 안 된다. 예제가 출력하는 embedding shape도 검색 성능의 증거는 아니다. [고정 예제 코드](https://github.com/huggingface/sentence-transformers/blob/7bfaf1ccb3dcacd613aeec668e9f0921991e366a/examples/sentence_transformer/training/merging/model_merging.py)

## 검색 시스템에서 검토할 질문

다음은 문서의 성능 결과가 아니라 **후속 평가 설계 제안**이다.

1. 공통 기반과 각 입력 체크포인트를 고정하고, 병합하지 않은 각 모델을 기준선으로 둔다.
2. 병합 비율을 고르는 검증 집합과 최종 평가 집합을 분리한다. 특정 도메인의 향상뿐 아니라 기존 도메인 회귀도 함께 본다.
3. 질의·문서 전처리, 프롬프트, 정규화와 검색 설정을 같은 조건으로 비교한다. 임베딩 모델 교체 시 기존 문서 벡터와 섞어도 되는지 추정하지 말고 재색인 계획을 세운다.
4. 검색 단계의 Recall@k·nDCG와 최종 답변 품질을 별도로 평가한다. 검색 점수 상승만으로 전체 RAG 개선을 선언하지 않는다.

**다음 질문:** 어떤 도메인의 이득을 얻는 대신 어느 도메인의 손실까지 허용할 것인가? 이 기준을 먼저 정하지 않으면 병합 비율 탐색이 점수 맞추기로 끝나기 쉽다.

[[기술-레이더/techniques|기술 레이더 기법]] · [원문](https://www.sbert.net/examples/sentence_transformer/training/merging/README.html)
