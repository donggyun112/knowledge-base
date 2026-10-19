---
title: "2023년을 위한 벡터 데이터베이스 선택 비교 및 안내 (jinicoding)"
source: https://www.jiniai.biz/2023/10/10/2023년을-위한-벡터-데이터베이스-선택-비교-및-안내/
type: blog
category: RAG-검색-문서
tags: [research, vector-db, 한국어, comparison]
researched: 2026-10-01
---
# 2023 벡터 DB 선택 비교

> [!summary] 한줄요약
> Pinecone, Weaviate, Milvus, Qdrant, Chroma, Elasticsearch, PGvector 7종을 비교한 2023년 가이드. 당시 수치는 현재(2026-10)의 선택 근거로 쓰기에는 낡았다.

2023-10-10 지니코딩랩(jinicoding) 게시글이며, 영문 원글("Picking a vector database: a comparison and guide for 2023")의 번역·재구성으로 보인다. 확장성·지연·비용·커뮤니티·기능을 기준으로 비교하고 **모두에게 맞는 하나는 없다**고 결론짓는다.

이 노트는 본문을 충실히 옮기고, 공식 저장소로 확인한 2026년 현황을 별도 섹션에 덧붙인다.

## 글의 성격과 출처

본문 상단에는 영문 제목 "Picking a vector database: a comparison and guide for 2023"이 링크 형태로 있고 비교표의 데이터 출처를 "ANN Benchmarks, 각 벡터 DB의 문서와 내부 벤치마크, 오픈소스 GitHub 저장소 조사"라고 밝힌다.

웹 검색 결과에서 영문 원글은 Vectorview의 Emil Fröberg가 쓴 2023년 가이드로 소개되어 있다(검색 결과 요약으로만 확인했고 원문 페이지는 열지 못했다. benchmark.vectorview.ai 주소는 렌더 시 내용이 없었다).

따라서 이 글의 일차 저자는 번역자가 아니라 원글 저자이고, 벤치마크의 조건(데이터셋 외 하드웨어, 설정)은 이 한국어 글에서 확인할 수 없다.

한국어 글은 비교표와 요약 뒤에 "2022년 기준 비교"라는 이름의 추가 목록, 동적 세그먼트 배치 대 정적 샤딩 설명, 무료 호스팅 티어 설명을 이어 붙였는데, 이 부분은 일반론 해설 성격이다(원글에 있던 내용인지는 확인 못함).

## 1. 본문 비교표 (원문 옮김)

도입부는 이렇다. 시맨틱 검색과 RAG가 온라인 상호작용을 재정의하는 시대에 핵심 구성요소인 벡터 DB는 종종 간과된다. 선택은 확장성, 지연 시간, 비용, 규정 준수에 영향을 준다. 그래서 Pinecone, Weaviate, Milvus, Qdrant, Chroma, Elasticsearch, PGvector를 비교했다.

텍스트로 복원되는 표 값은 아래와 같다(글의 오탈자 "Weviate"는 Weaviate로 적는다). 표 안의 체크 아이콘으로 표시된 행(오픈소스, 자체 호스팅, 클라우드 관리, 벡터 전용, 개발자 경험, 하이브리드 검색, 디스크 인덱스, RBAC, 무료 호스팅 티어)은 아이콘이 렌더 결과에 남지 않아 셀 단위로는 복원하지 못했고, 해당 내용은 아래 요약문에서 글이 서술한 것만 옮긴다.

| 항목 | Pinecone | Weaviate | Milvus | Qdrant | Chroma | Elasticsearch | PGvector |
|---|---|---|---|---|---|---|---|
| 커뮤니티 | 커뮤니티 페이지·이벤트 | GitHub 8k★, Slack 4k | 23k★, Slack 4k | 13k★, Discord 3k | 9k★, Discord 6k | Slack 23k | 6k★ |
| 초당 쿼리 수(nytimes-256-angular) | 150 (p2 파드 기준, 파드 추가 가능) | 791 | 2406 | 326 | ? | 700~100 (여러 보고서 기준, 표기 그대로) | 141 |
| 지연 시간 ms (Recall/95퍼센타일, nytimes-256-angular) | 1 (배치 검색, recall 0.99, 200k SBERT) | 2 | 1 | 4 | ? | ? | 8 |
| 지원 인덱스 | ? | HNSW | 다수(총 11종) | HNSW | HNSW | HNSW | HNSW/IVFFlat |
| 세그먼트 배치 방식 | ? | 정적 샤딩 | 동적 세그먼트 배치 | 정적 샤딩 | 동적 세그먼트 배치 | 정적 샤딩 | - |
| 가격(5만 벡터, 1536차원) | \$70 | $25부터 | $65부터 | 약 \$9 | 다양 | \$95 | 다양 |
| 가격(2천만 벡터, 2천만 요청, 768차원) | \$227 (고성능 구성 \$2074) | $1536부터 | \$309 (고성능 \$2291)부터 | \$281 (고성능 \$820) | 다양 | 약 \$1225 | 다양 |

가격 행의 "부터(fr.)"와 "약(est.)" 표기와 열 대응은 텍스트 순서에서 복원한 것이라 일부 셀의 대응이 어긋났을 가능성이 있다. 무료 티어 행은 "(free self-hosted)", "(varies)" 같은 일부 문구만 남아 있다.

## 2. 글의 요약 서술 (원문 옮김)

- **오픈소스와 호스팅 클라우드**: 오픈소스를 선호한다면 Weaviate, Milvus, Chroma가 주요 후보. Pinecone은 오픈소스가 아니지만 개발자 경험과 풍부한 호스팅 솔루션이 강점. (표에서 오픈소스인 Qdrant와 PGvector가 이 문장에서 빠져 있다. 서술이 표와 불일치한다.)
- **성능**: 초당 쿼리에서 Milvus가 선두, Weaviate와 Qdrant가 바로 뒤. 지연 시간에서는 Pinecone과 Milvus가 2ms 미만. Pinecone은 파드를 추가하면 QPS가 더 올라간다.
- **커뮤니티**: Milvus가 가장 크고 Weaviate와 Elasticsearch가 뒤를 잇는다. 활발한 커뮤니티는 지원, 기능, 버그 수정에 유리하다.
- **확장성, 고급 기능, 보안**: 역할 기반 접근 제어(RBAC)는 Pinecone, Milvus, Elasticsearch에서 제공. 확장성에서는 Milvus와 Chroma가 동적 세그먼트 배치를 제공해 변화하는 데이터셋에 적합. 인덱스 유형은 Milvus가 11가지로 독보적. 하이브리드 검색은 대체로 잘 지원되지만 Elasticsearch는 디스크 인덱스 지원이 약간 부족.
- **가격**: 예산이 제한된 프로젝트·스타트업에는 Qdrant의 5만 벡터 \$9 추정 가격이 매우 경쟁력 있음. 큰 규모·고성능에서는 Pinecone과 Milvus가 경쟁력 있는 가격.
- **결론**: 모든 상황에 맞는 단 하나의 선택지는 없으며 프로젝트 요구사항, 예산, 개인 선호에 따라 다르다. 저자의 선택은 높은 성능, Milvus의 강한 커뮤니티, 규모에 따른 가격 유연성 때문에 Pinecone과 Milvus를 실환경에서 테스트하는 것.

## 3. 부가 섹션 옮김

### "2022년 기준" 벡터 DB 9종 장단점

벡터 DB는 고차원 벡터를 저장·검색하며 시맨틱 검색, 추천, 머신러닝에 중요하다는 소개 뒤에 다음 목록이 이어진다.

1. **Faiss**: 대규모 유사성 검색에 매우 효율적, GPU 지원, Facebook AI가 활발히 관리. 단점은 초보자에게 학습 곡선이 가파름.
2. **Annoy**: Spotify 개발, 메모리와 속도 사이 균형 우수. 증분 업데이트를 지원하지 않아 인덱스 재구축이 필요.
3. **Milvus**: 오픈소스·클라우드 네이티브, 분산 검색·저장, 딥러닝 프레임워크 통합. 단점은 상대적으로 새로운 프로젝트.
4. **Elasticsearch(벡터 필드, HNSW 플러그인)**: 성숙한 플랫폼과 큰 커뮤니티, 전문 검색과 벡터 검색 결합, 높은 확장성. 아주 큰 고차원 데이터에서는 전용 벡터 DB만큼 효율적이지 않을 수 있음.
5. **Pinecone**: 관리형 서비스로 설치·유지 보수가 쉽고 클라우드 네이티브. 오픈소스가 아니며 서비스 제공자에 의존.
6. **Weaviate**: ML 기반 시맨틱 검색 중심, GraphQL API. 특정 아키텍처에 익숙하지 않으면 복잡.
7. **Qdrant**: 오픈소스, 대규모 벡터 저장·검색용. 상대적으로 덜 알려져 커뮤니티 지원에 영향 가능.
8. **Chroma**: 효율적이고 빠르며 여러 유사성 척도 지원. 2022년 기준 문서화가 제한적.
9. **PGvector**: PostgreSQL 통합, 성숙한 생태계, SQL 인터페이스. 특정 작업에서 전용 DB만큼 효율적이지 않을 수 있음.

선택 시 고려 요소로 규모, 통합, 비용, 지원·커뮤니티를 든다. 글은 이 목록이 2022년 스냅샷이며 최신 리뷰와 벤치마크를 항상 확인하라고 밝힌다.

### 동적 세그먼트 배치 대 정적 데이터 샤딩

동적 세그먼트 배치는 데이터 세그먼트를 노드 사이에 유동적으로 할당·재배치하는 방식으로, 크기·부하에 따른 유연성, 접근 패턴 기반 자동 최적화, 노드 장애 시 빠른 이동을 장점으로 들고 로직 복잡성과 성능 영향을 단점으로 든다.

정적 샤딩은 데이터를 샤드로 나눠 노드에 고정 할당하며, 예측 가능성, 단순함, 노드 간 이동이 적어 일관된 성능이 장점이고, 패턴 변화 시 재배치 어려움과 시간에 따른 데이터 불균형이 단점이다.

결론은 사용 사례, 성능 요구, 유연성, 복잡도에 따라 선택하라는 것.

### 무료 호스팅 티어

클라우드/SaaS가 제한된 버전을 무료 제공하는 수준을 뜻하며, 자원 제한, 기간 제약(예: 첫 12개월), 기능 감소, 자원 공유가 특성이다. 장점은 비용 없음, 학습, 프로토타이핑이고 단점은 성능 불균일, 확장성 한계, 프로덕션 부적합.

예로 AWS 프리 티어(12개월), GCP Always Free, Azure 무료 티어, Heroku 무료 dyno(30분 비활성 시 잠듦), MongoDB Atlas 512MB 무료 티어를 든다.

이 예시는 벡터 DB와 직접 관련 없는 일반 설명이며 현재 각 서비스 정책은 확인하지 않았다(Heroku의 무료 dyno는 이후 폐지된 것으로 알려져 있으나 이번에 검증하지 않음).

## 4. 글의 한계

- 2023-10 시점 값이다. 비교 기준이 된 가격, QPS, 지연은 당시 버전과 구성의 단일 데이터셋(nytimes-256-angular, ANN Benchmarks 계열) 결과이고, 하드웨어와 파라미터는 글에 없다. Chroma와 Elasticsearch의 일부 값은 "?"다.
- 내부 불일치가 있다. 오픈소스 후보 문장에 Qdrant가 빠지고, 커뮤니티 문장이 표의 별 개수(Milvus 23k, Chroma 9k, Weaviate 8k, Qdrant 13k)와 맞지 않는 부분이 있다(Elasticsearch는 별 대신 Slack 수만 적혀 있음).
- 비교 기준에 정확도(recall)와 필터링 성능, 멀티테넌시, 운영 복잡도, 라이선스 변화가 거의 없다.
- 번역 글이라 원글의 후속 수정이 반영되지 않는다.

## 5. 2026년 현재 기준 변경점 (공식 저장소·문서로 확인된 것만)

2026-10-01에 GitHub REST API와 각 저장소 README/문서로 확인한 사실이다.

| DB | 라이선스(저장소 기준) | Stars | 최신 릴리스 | 확인한 변화 |
|---|---|---|---|---|
| Milvus | Apache-2.0, LF AI & Data 소속 | 46,293 | v3.0.2 (2026-09-20) | README: Go/C++, 완전 분산·K8s 네이티브, Standalone과 `pip install`로 쓰는 Milvus Lite, 인덱스는 HNSW, IVF, FLAT, SCANN, DiskANN(양자화 변형·mmap 포함), GPU 인덱싱(CAGRA). 2023 글의 "인덱스 11종"보다 메이저 버전이 3.x로 올라갔다. |
| Qdrant | Apache-2.0 | 34,891 | v1.19.1 (2026-09-04) | README: Rust, dense·sparse·multivector(ColBERT류) 검색, 하이브리드(RRF, DBSF 융합), 페이로드 필터링, 양자화(RAM 최대 97% 절감 주장), 분산 샤딩·복제, 멀티테넌시, GPU 인덱싱, 임베디드용 Qdrant Edge, Qdrant Cloud 무료 티어. Docker 기본 실행은 인증 없는 열린 배포라는 경고가 README에 있다. |
| Weaviate | 혼합: 대부분 BSD-3-Clause, `wl` 디렉터리는 "Weaviate License" (LICENSE 파일 기준; GitHub은 NOASSERTION) | 16,860 | v1.39.7 (2026-09-25) | README: Go, BM25와 벡터를 한 질의로 하는 하이브리드, 내장 RAG·리랭킹, 멀티테넌시, 복제, RBAC, 벡터 압축, 객체 TTL, Weaviate Cloud. 2023 글은 RBAC를 Pinecone/Milvus/ES에서만 언급했는데, 현재 Weaviate README는 RBAC도 제공한다고 밝힌다. |
| Chroma | Apache-2.0 | 29,418 | 1.5.9 (2026-05-05) | README: Python/JS 클라이언트, 클라이언트-서버 모드, "Chroma Cloud"(서버리스 벡터·하이브리드·전문 검색, \$5 무료 크레딧). 2023 글의 "문서화 제한" 평가는 더는 맞지 않을 수 있으나 문서 자체는 이번에 열지 않았다. |
| Elasticsearch | 혼합: 기본이 AGPL-3.0 / SSPL-1 / Elastic License 2.0 3중 라이선스(LICENSE.txt 기준; GitHub은 NOASSERTION) | 78,169 | v9.5.4 (2026-09-15) | 공식 문서: `dense_vector`/`sparse_vector` 필드로 벡터 DB 기능, 전문 검색·필터·집계와 하이브리드 검색을 한 엔진에서 처리. 라이선스에 AGPL 선택지가 포함된 점이 2023 글과 다르다(변경 시점은 확인 못함). |
| pgvector | PostgreSQL 라이선스(LICENSE 파일 본문; GitHub은 NOASSERTION) | 23,202 | 태그 v0.8.6 (2026-07-29, CHANGELOG), GitHub Releases 항목은 없음 | CHANGELOG: HNSW 추가는 0.5.0(2023-08-28), `halfvec`/`sparsevec`/`bit` 인덱싱과 `binary_quantize`는 0.7.0(2024-04-29), 병렬 HNSW 빌드는 0.6.0(2024-01-29), 반복 인덱스 스캔(필터링 시 결과 부족 완화)은 0.8.0(2024-10-30). 차원 한도는 vector 2,000, halfvec 4,000, bit 64,000, sparsevec 비영 원소 1,000. 하이브리드는 Postgres 전문 검색과 RRF 조합을 README가 안내. Postgres 13+ 지원. |
| Pinecone | 상용 SaaS(클라이언트 SDK는 Apache-2.0, 파이썬 클라이언트 v10.0.0 2026-09-03) | 클라이언트 452 | - | 공식 문서(아키텍처): 서버리스 구조로 AWS/GCP/Azure에서 운영, 쓰기 경로(요청 로그→memtable→불변 slab 파일)와 읽기 경로 분리, 객체 스토리지 기반. 문서 목차에 전문 검색·시맨틱 검색·하이브리드·희소 벡터 검색, BYOC, 이전 파드 방식에서 서버리스로의 마이그레이션 가이드가 있다. 2023 글의 "파드(p2)" 기준 수치는 현재 주력 구조와 다르다. |

확인한 변화는 다음 네 가지로 정리된다.

1. 하이브리드·희소 벡터 검색이 대부분의 제품에서 기본 기능이 되었다(Qdrant, Weaviate, Elasticsearch, Pinecone 문서 및 pgvector의 sparsevec).

2. pgvector가 2023년 HNSW 도입 이후 반정밀·이진·희소 벡터와 반복 스캔으로 크게 보강되어 "Postgres 안에서 해결" 선택지가 현실적이 되었다.

3. Milvus는 3.x, Elasticsearch는 9.x로 세대가 바뀌었다.

4. 라이선스는 제품마다 단순 오픈소스가 아니라 혼합형(Weaviate, Elasticsearch)이 있다는 점에서 법무 확인 항목이 늘었다.

2023 글의 QPS·지연·가격 숫자는 현재 버전에서 재측정된 값이 없으므로 쓰면 안 된다.

현재의 가격 정책과 벤치마크 수치는 이번에 확인하지 못했다.

## 관련 노트

[[cerebras-knowledge-base-pgvector-rrf-mcp]] [[mongodb-crewai-ecommerce-agents]] [[splade-v3-doc]] [[ragas]] [[ragu]] [[pageindex]]

## 출처

- https://www.jiniai.biz/2023/10/10/2023년을-위한-벡터-데이터베이스-선택-비교-및-안내/ (본문 렌더 전문 열람, 2026-10-01; 표의 체크 아이콘은 렌더에 남지 않음)
- 웹 검색 결과(영문 원글 소개와 저자 Emil Fröberg/Vectorview 언급): https://discuss.pytorch.kr/t/2023-picking-a-vector-database-a-comparison-and-guide-for-2023/2625 (검색 결과 목록만 확인, 페이지 미열람)
- https://github.com/milvus-io/milvus , https://github.com/qdrant/qdrant , https://github.com/weaviate/weaviate (README, LICENSE), https://github.com/chroma-core/chroma , https://github.com/elastic/elasticsearch (LICENSE.txt), https://github.com/pgvector/pgvector (README, CHANGELOG, LICENSE), https://github.com/pinecone-io/pinecone-python-client , GitHub REST API(스타·릴리스·라이선스, 2026-10-01)
- https://docs.pinecone.io/guides/get-started/database-architecture (Pinecone 아키텍처 문서 렌더 열람)
- https://www.elastic.co/docs/solutions/search/vector (Elasticsearch 벡터 검색 문서 렌더 열람)
- 열람하지 않은 것: 영문 원글, ANN Benchmarks 원자료, 각 벤더의 현재 가격 페이지, 각 제품의 최신 벤치마크
