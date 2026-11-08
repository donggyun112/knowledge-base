---
title: pgvector 필터 검색 — 결과 개수·정렬·recall은 다른 계약
source: https://github.com/pgvector/pgvector#iterative-index-scans
type: documentation
category: RAG-검색-문서
tags: [research, pgvector, retrieval, hnsw, backend, technology-radar]
researched: 2026-11-08
radar_quadrant: Tools
radar_ring: Assess
reading_status: unread
---

# pgvector 필터 검색 — 결과 개수·정렬·recall은 다른 계약

**검색 결과가 k개라는 것, 그 결과가 거리순이라는 것, 실제 최근접 k개를 찾았다는 것은 서로 다르다.** pgvector의 필터링·반복 스캔 문서는 이 차이를 검색 실행 계획과 자원 한도로 연결해 읽기 좋다.

- **대표 원문**: [Iterative Index Scans](https://github.com/pgvector/pgvector#iterative-index-scans)
- **고정 본문**: [README의 Filtering·Multitenancy·Iterative Index Scans·Monitoring](https://github.com/pgvector/pgvector/blob/f37c13f68b57d2c3472b2214fbcff699d6d34876/README.md#filtering)
- **확인된 날짜**: README 마지막 변경 커밋은 [2026-10-01 UTC, f37c13f](https://github.com/pgvector/pgvector/commit/f37c13f68b57d2c3472b2214fbcff699d6d34876). 버전 표기 변경이며 각 설명의 최초 발행일은 아니다. [CHANGELOG](https://github.com/pgvector/pgvector/blob/f37c13f68b57d2c3472b2214fbcff699d6d34876/CHANGELOG.md)는 반복 스캔 도입을 0.8.0, 2024-10-30으로 기록한다.
- **수집일**: 2026-11-08 KST
- **상태**: Tools / Assess · 읽기 전
- **검증 범위**: 공식 README·변경 이력과 고정 커밋의 HNSW 스캔 코드 일부를 정적으로 확인. DB 설치·질의·성능 실험은 하지 않음

## 1. 필터를 붙였는데 결과가 부족한 이유

공식 문서가 설명하는 근사 인덱스 경로에서는 인덱스를 스캔한 뒤 필터가 적용된다. 따라서 전체 데이터에서 가까운 후보를 찾았더라도 `WHERE`를 통과하는 후보가 적으면 `LIMIT k`만큼 반환되지 않을 수 있다.

README의 예시는 필터가 전체 행의 10%에 맞고 HNSW의 `hnsw.ef_search` 기본값이 40일 때 평균 4개가 일치한다는 것이다. 이는 직관을 주는 예시이지, 실제 데이터에서 통과 수가 항상 4개라는 보장은 아니다. 필터 속성과 벡터 거리의 상관관계도 따로 확인해야 한다.

문서는 적은 비율의 행에 맞는 조건이라면 필터 열의 일반 인덱스부터 검토하라고 안내한다. 좁힌 집합에서 정확 검색하는 선택과 근사 검색을 구별하는 출발점이다. 모든 `WHERE` 질의가 동일한 실행 계획을 쓰는 것으로 일반화하면 안 된다.

## 2. 반복 스캔은 후보 탐색을 더 진행한다

0.8.0부터 반복 스캔을 켜면 필요한 결과가 모이거나 스캔 한도에 도달할 때까지 더 탐색한다.

- HNSW의 `strict_order`는 반환 결과의 거리순을 보장한다. **근사 검색을 정확 검색으로 바꾸는 옵션은 아니다.**
- `relaxed_order`는 순서를 조금 허용하는 대신 recall을 높일 수 있다. HNSW와 IVFFlat에서 지원한다. 효과의 크기는 여기서 측정하지 않았다.
- 느슨한 순서의 결과를 materialized CTE로 받은 뒤 바깥에서 다시 정렬할 수 있다. README는 PostgreSQL 17 이상에서 바깥 정렬식에 `+ 0`이 필요하다고 명시한다. 이 재정렬은 이미 얻은 후보의 순서만 고치며 누락된 후보를 복원하지 않는다.
- 거리 임계값을 조건으로 쓸 때는 materialized CTE 바깥에 거리 필터를, 다른 필터는 안쪽에 두는 예제를 제시한다. PostgreSQL executor 동작에 따른 성능 조언이므로 실제 버전과 실행 계획을 확인해야 한다.

## 3. 더 찾는 데에는 자원 상한이 있다

HNSW의 `hnsw.max_scan_tuples` 기본값은 20,000이며 근사적 한도이고 초기 스캔에는 적용되지 않는다. `hnsw.scan_mem_multiplier`는 `work_mem`의 배수로 메모리 예산을 정한다. 튜플 상한을 올려도 recall이 늘지 않으면 메모리 한도를 함께 살펴보라는 안내가 있다.

[HNSW 스캔 코드](https://github.com/pgvector/pgvector/blob/f37c13f68b57d2c3472b2214fbcff699d6d34876/src/hnswscan.c#L251-L285)는 후보 목록이 비었을 때 반복 스캔 설정과 튜플·메모리 한도를 검사한다. 한도에 닿으면 보관된 나머지 후보를 반환하는 경로가 있으며, 그렇지 않으면 탐색을 재개한다. 따라서 이 값을 정확한 반환 행 수나 요청의 시간 제한으로 해석하면 안 된다.

IVFFlat은 `ivfflat.max_probes`로 반복 탐색 범위를 제어한다. 이 값이 초기 `ivfflat.probes`보다 낮으면 초기 probes가 사용된다. HNSW의 튜플 한도와 단위가 같지 않다.

## 기술적 활용 맥락

다음은 문서에서 도출한 검토 관점이다. 날짜·범주·테넌트 조건이 있는 RAG 검색에서 결과 부족을 임베딩 품질 문제로 곧바로 단정하지 않고, 실행 계획과 후보 탐색 범위를 먼저 분해하는 데 유용하다.

README는 테넌트들이 근사 인덱스를 공유하면 한 테넌트의 벡터가 다른 테넌트의 recall과 속도에도 영향을 줄 수 있다고 설명한다. list partitioning 또는 별도 테이블을 격리 선택지로 제시하지만, 이것만으로 특정 분할 구조의 총운영비가 낮다고 결론낼 수는 없다. 검색 후보 격리와 사용자 권한 검증도 별도 문제다.

[[RAG-검색-문서/vector-db-comparison-2023|기존 벡터 DB 비교]]는 제품별 기능 개요다. 이 글은 pgvector의 필터 검색 계약을 좁혀 다루며 그 비교나 기존 사용자 판단을 대체하지 않는다.

## 한계와 다음 질문

- 결과가 k개여도 exact top-k와 다를 수 있다. 반환 개수 충족률과 recall을 함께 봐야 한다.
- 엄격 정렬과 후보 누락은 별개다. 응답 결과만 재정렬해서 recall을 개선했다고 보고하면 안 된다.
- 더 넓은 탐색은 CPU·메모리·지연을 늘릴 수 있다. 문서의 기능 설명은 운영비 절감 증거가 아니다.
- 부분 인덱스·파티션·일반 인덱스 중 선택은 값의 종류와 분포, 갱신 빈도, 실행 계획에 달려 있다. 특정 선택을 채택한 상태가 아니다.

## 작은 검증 제안

아래는 **미실행 제안**이다. 임베딩을 다시 만들거나 LLM으로 데이터를 가공할 필요 없이 기존 벡터를 고정한 비교부터 설계할 수 있다.

1. 같은 데이터 스냅샷·질의·필터·거리 함수에서 exact top-k를 기준으로 삼는다. 공식 Monitoring 절의 `SET LOCAL enable_indexscan = off` 예제를 참고하되 실제 계획이 정확 검색인지 확인한다.
2. 필터 통과 비율별로 반복 스캔 꺼짐, strict, relaxed 후 재정렬을 비교한다. 조건에 맞는 전체 행이 k보다 적은 경우는 별도로 분류한다.
3. 반환 개수 충족률, exact 결과 대비 recall@k, p50/p95 지연, 버퍼 사용과 동시 요청 시 메모리를 기록한다. 충분한 결과와 높은 recall을 얻는 데 필요한 비용을 함께 판단한다.
4. 같은 테넌트 질의를 유지한 채 다른 테넌트의 벡터 분포만 바꿔 공유 인덱스의 영향을 검사한다. 파티션과 비교할 경우 인덱스 구축·유지 비용도 따로 기록한다.

## 결정 이력

- **2026-11-08**: 공개 공식 문서와 코드 일부를 Tools / Assess로 수집했다. DB 실행과 성능 검증은 하지 않았으며 읽기 상태는 읽기 전이다.

[[기술-레이더/index|기술 레이더]] · [[기술-레이더/tools|도구 목록]] · [[index|전체 목차]]
