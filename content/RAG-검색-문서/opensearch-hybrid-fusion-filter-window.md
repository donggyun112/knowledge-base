---
title: OpenSearch 하이브리드 검색 — 필터 위치가 후보를 바꾼다
source: https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/fusion-mode/
type: implementation
category: RAG-검색-문서
tags: [research, opensearch, hybrid-search, rag, technology-radar]
researched: 2026-11-28
radar_quadrant: Tools
radar_ring: Assess
reading_status: unread
---

# OpenSearch 하이브리드 검색 — 필터 위치가 후보를 바꾼다

**같은 메타데이터 조건이라도 후보를 뽑을 때 적용하는 것과 뽑은 뒤 제거하는 것은 다르다.** OpenSearch 3.10의 쿼리 내부 fusion 모드는 중첩 하이브리드 쿼리에서 이 차이를 명시한다.

- **원문**: [Fusion mode 공식 문서](https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/fusion-mode/#nesting-a-hybrid-query), [공식 버전 이력](https://docs.opensearch.org/latest/version-history/)
- **확인된 날짜**: 3.10.0 도입 2026-11-16, 3.10.1 배포 2026-11-24.
- **수집일**: 2026-11-28 KST
- **상태**: Tools / Assess · 읽기 전
- **검증 범위**: 공식 문서 정적 검토. 검색 실행, 결과 재현, 지연 측정은 하지 않았다.

## 1. 윈도와 필터의 순서

`fusion.window_size`는 각 하위 쿼리에서 조정 노드가 결합에 쓰는 전역 후보 수를 제한한다. 벡터 하위 쿼리의 `k`는 엔진과 샤드·세그먼트별 검색 단계에서 후보를 먼저 제한할 수 있다. 윈도를 늘려도 벡터가 내놓지 않은 후보가 자동으로 채워지지는 않는다.

- **`hybrid.filter`**: 각 하위 쿼리가 적격 문서를 검색하도록 제한한다. 대상 집합 안에서 순위를 매기려는 경우 이 위치가 맞다.
- **바깥 `bool.filter`**: 중첩된 hybrid의 윈도를 정한 뒤 문서를 제거한다. 두 번째 검색이 없으면 적격 문서가 윈도 밖에 있었더라도 결과에 들어오지 않아 요청한 개수보다 적게 나올 수 있다.
- **두 번째 검색이 있는 경우**: 윈도 밖 문서가 결과에 들어올 수 있지만 hybrid 쿼리의 점수 기여는 0이다. 바깥에 별도 점수 절이 있으면 총점까지 0이라는 뜻은 아니다. `track_total_hits: true`는 두 번째 검색을 강제하고, `false`도 정렬·집계·하이라이트 등 다른 원인이 있으면 이를 막지 못한다. 공식 문서는 진단용 `profile: true`에서 조정 노드의 `FusedHybridQuery.debug.tail_built`를 확인하라고 안내한다.

## 2. 어떤 결정을 돕는가

검색 결과가 부족할 때 reranker부터 바꾸기 전에 필터가 적용된 위치와 각 검색 경로의 후보 수를 확인한다. 이 모드의 내장 `rescore`는 최상위 hybrid에서만 지원하며 후보 윈도 안을 재정렬한다. 별도의 reranker도 전달받지 않은 문서를 복구하지 못한다. 이 설명은 모든 노드가 3.10 이상인 fusion 모드를 대상으로 하며, 기존 search pipeline 방식의 동등성이나 접근 권한 강제를 뜻하지 않는다.

## 3. 작은 검증 제안

고정된 한 샤드의 합성 색인에 키워드가 모두 일치하는 세 문서를 준비한다. 필터에서 제외될 두 문서는 각 하위 쿼리 순위에서 적격 문서보다 앞에 오도록 만들고, 개별 쿼리 순위부터 확인한다. 두 요청 모두 hybrid를 `bool.must`에 같은 형태로 넣고 **메타데이터 필터 위치만** 바꾼다. `size=2`, `fusion.window_size=2`, 벡터 `k=2`, 동일 가중치 RRF를 고정한다. 다른 두 번째 검색 유발 옵션 없이 `track_total_hits: false`를 비교하고, `true`에서 문서 ID·점수를 다시 본다. `profile`은 별도 진단으로 실행한다. 검색 엔진과 세그먼트 조건도 기록해야 하며, 이 비교는 실행하지 않았다.
