---
title: 토스 AI Platform Engineer (Serving) 채용공고
source: https://toss.im/career/job-detail?job_id=7786567003
type: job
category: 기타-리소스
tags: [research, toss, llm-serving, vllm, job]
researched: 2026-10-01
---
# 토스 AI Platform Engineer (Serving) 채용공고

> [!summary] 한줄요약
> 토스 AI Platform 팀이 LLM·embedding 모델의 실시간 serving 인프라(vLLM, Dynamo, Triton 운영·튜닝, 장애 대응, 배포 자동화)를 맡을 정규직 엔지니어를 찾는 공고. 요구의 중심은 "프레임워크 사용 경험"이 아니라 "GPU와 LLM 내부 동작을 이해하고 성능·안정성 문제를 구조화해 푼 경험"이다. 전형은 서류 → 프리 인터뷰 → 직무 인터뷰(심층 기술 + ML 시스템 설계) → 문화적합성 → 레퍼런스 → 처우 협의 → 최종 합격. 연차·학력 조건은 공고에 없다.

## 1. 배경: 이 공고가 어떤 자리인가

토스 채용 페이지의 `AI Platform Engineer (Serving)` 공고(job_id 7786567003)다. 소속 표기는 "토스", 고용 형태는 "정규직"이다. 페이지는 SPA라 headless Chrome으로 렌더링해 2026-10-01에 본문 전체를 읽었다. 같은 본문이 페이지 안에 두 번 반복 출력되는데(렌더링 구조상 모바일/데스크톱 중복으로 보임) 내용은 동일하다. 마감일, 게시일, "모집 중" 여부 표기는 본문에 없다. 하단 메뉴에 "기술 블로그", "블로그", "공고" 링크가 있어 토스는 기술 블로그(toss.tech)를 운영한다. 채용 페이지 상단 메뉴는 채용 이벤트, 계열사 소개, 합류 여정, 팀 문화, 아티클, 자주 묻는 질문, 전체 공고로 구성된다.

"Serving"이라는 괄호가 붙은 것은 같은 AI Platform 팀 안에 다른 세부 포지션이 있다는 뜻이다. 검색에서 같은 팀의 "AI Platform Engineer (Platform)"(job_id 7646941003) 공고와 Recommendation 포지션이 보였다. 이들 공고 본문은 이번에 열어 보지 않았으므로 차이는 확인하지 못했다.

## 2. 공고 전문 (원문 구조 그대로)

### 2-1. 합류하게 될 팀에 대해
- AI Platform 팀은 "AI 기술을 누구나 빠르고 안정적으로 사용할 수 있는 플랫폼으로 만든다"는 미션으로 토스 전반의 AI 활용을 기술적으로 지원한다.
- Retrieval-Augmented Generation, Agent, Assistant 등 새로운 방식의 AI 시스템이 빠르게 실험되고 안정적으로 운영될 수 있도록 필요한 도구와 플랫폼을 만든다.
- 만드는 플랫폼은 단순한 툴셋이 아니라, AI 기술이 더 많은 팀에서 실제로 쓰일 수 있게 확장성을 갖춘 구조로 설계된다.
- 아직 정답이 정해지지 않은 문제들을 다루는 만큼 기술적인 방향을 함께 고민하고 구조화해 나가는 역할이 중요하다.
- 안내 링크: 토스 데이터 조직에 대해 더 알아보려면 "토스 Data Division 위키".

### 2-2. 합류하면 함께 할 업무 (4개)
1. 다양한 서빙 프레임워크(vLLM, Dynamo, Triton 등)를 운영하고 성능을 개선한다.
2. 대규모 LLM 및 embedding 모델의 안정적인 실시간 서빙 환경을 구축하고 모니터링한다.
3. 리소스 효율성, 추론 속도, 확장성을 고려해 시스템 성능을 지속적으로 개선한다.
4. 모델 서빙 장애 대응, 배포 안정성 확보를 위한 오케스트레이션 및 자동화 작업을 함께한다.

### 2-3. 이런 분과 함께하고 싶어요 (자격 요건, 5개)
1. Triton, vLLM 등 서빙 프레임워크에 익숙하고 성능 튜닝 및 운영 안정성 확보 경험이 있는 분
2. GPU 내부에서의 동작 방식과 LLM 모델들 내부에서의 동작 방식에 대한 이해와 실전 운영 경험이 있는 분
3. 실험 및 운영 효율화를 위한 자동화, 모니터링, 오케스트레이션에 관심이 있는 분
4. 구조화되지 않은 문제를 기술적으로 정의하고 시스템적으로 해결해 본 분
5. 새로운 기술 흐름을 빠르게 따라가고 그 흐름을 팀 내에 자연스럽게 녹여낸 경험이 있는 분

원문에서 1~3번은 "함께하고 싶어요", 4~5번은 "좋아요" 어미를 쓴다. 필수와 우대의 경계가 문장 어미 수준으로만 구분되어 있다.

### 2-4. 이런 분이면 더 좋아요 (우대, 4개)
1. 대규모 LLM 또는 embedding 모델 학습/서빙을 위해 최적화하고 운영한 경험
2. LLM 모델들을 최적화해 서비스에 활용할 수 있게 성능을 이끌어낸 경험
3. AI/ML 모델들에 대해 일반화하여 플랫폼을 구축해 본 경험
4. 고성능 서빙, 대규모 트래픽 환경에서 모델 운영 경험(AI Platform 팀의 방향과 잘 맞는다고 표현)

### 2-5. 이력서는 이렇게 작성하시는 걸 추천해요
- 조직에 큰 영향을 미친 과제가 있다면 자세히. 단순히 어떤 언어·플랫폼·프레임워크·기술을 썼는지보다 어떤 목적의 과제였고, 이를 해결하기 위해 무엇을 사용했고, 어떻게 해결했는지.
- 플랫폼 운영 중 발생한 치명적 장애를 해결해 봤거나 성능/리소스 최적화를 해 본 경험.
- 오픈소스 사용 중 발생한 버그나 이슈를 해결해 봤거나, 부족한 기능을 개선하려고 오픈소스에 기여한 경험.

### 2-6. 토스로의 합류여정 (전형)
서류 접수 > 프리 인터뷰 > 직무 인터뷰 > 문화적합성 인터뷰 > 레퍼런스 체크 > 처우 협의 > 최종 합격

- 프리 인터뷰: 지원서 기반의 주요 경험과 직무 적합도 중심.
- 직무 인터뷰: 심층 기술 면접과 ML 시스템 설계.

### 2-7. 함께할 동료를 위한 한마디 (팀 소개 문단)
- 인용 문구: "빠르게 발전하고 있는 AI 모델들을 서빙하는 것에 그치지 않고, 그 모델이 안정적으로 작동하고 끊임없이 개선될 수 있는 시스템을 직접 만들어갑니다."
- AI Platform 팀은 LLM 기반 서비스, RAG 시스템, 검색 인프라 등 다양한 AI 기술이 실제 프로덕션 환경에서 원활히 동작하도록 서빙/실험/운영 인프라를 책임진다.
- GPU 자원과 클러스터를 효율적으로 운영하고, vLLM, Triton, Model Registry 등을 활용해 실험과 배포를 자동화하고 있다.
- AI 기술이 실질적인 서비스로 이어지기 위한 기술적 기반을 구축하고 안정성과 확장성을 함께 고민할 사람을 기다린다.
- "실험부터 서빙까지의 흐름을 직접 만들고 고도화해 나가는 경험, 토스에서 할 수 있습니다."

### 2-8. 더 알아보기 (공고에 링크된 콘텐츠)
- [영상] 오프더레코드 EP.4 "토스 ML Engineer가 말하는 '재밌게 일하는 법'": 머신러닝 엔지니어가 들려주는 커리어의 갈림길, 일하는 방식, 함께 일하고 싶은 동료 이야기. 영상은 열지 않았다.
- 아티클 "ML 플랫폼으로 개발 속도와 안정성 높이기": 토스가 ML 플랫폼으로 모델을 빠르고 안정적으로 개발하는 방법을 소개. 링크 URL을 렌더 텍스트에서 얻지 못해 본문은 확인하지 못했다. 대신 같은 맥락의 토스 기술 블로그 글을 아래 6절에 정리했다.
- "토스 ML Chapter, 예비 동료들의 한마디" 섹션.

## 3. 기술 해설: vLLM · Dynamo · Triton

> [!note] 구분 표시
> 2절은 공고 원문이다. 3절 이하는 공고에 없는 일반 해설로, 각 프로젝트의 공식 저장소·문서를 2026-10-01에 열람해 정리했다(출처는 문서 끝). vLLM은 클론한 저장소의 docs, Dynamo는 클론한 저장소의 README와 docs, Triton은 공식 문서와 저장소 요약을 근거로 한다. 공고에는 이 도구들을 토스가 어떤 구성으로 쓰는지에 대한 구체 설명이 없다.

### 3-1. 한 장 비교

| 항목 | vLLM | Dynamo (NVIDIA) | Triton Inference Server |
|---|---|---|---|
| 계층 | 추론 엔진(모델을 GPU에서 돌리는 쪽) | 엔진 위의 분산 오케스트레이션 계층 | 범용 모델 서버(여러 프레임워크) |
| 핵심 가치 | PagedAttention, continuous batching으로 단일 엔진 처리량 극대화 | 다중 노드 GPU를 한 시스템으로: 프리필/디코드 분리, KV 인지 라우팅, SLA 오토스케일 | 다양한 백엔드를 한 서버에서 서빙, dynamic batching, ensemble |
| 엔진과의 관계 | 자체가 엔진 | vLLM·SGLang·TensorRT-LLM을 백엔드로 사용(대체하지 않음) | vLLM을 백엔드(vllm_backend)로 올릴 수 있음 |
| 라이선스 | (확인한 문서에 명시 없음. 저장소 LICENSE 파일 별도 확인 필요) | Apache 2.0 | BSD-3-Clause |
| API | OpenAI 호환 서버, Anthropic Messages API, gRPC | OpenAI 호환 Frontend | HTTP/REST·gRPC(KServe 기반), C API |

### 3-2. vLLM

**역할.** 오픈소스 LLM 추론·서빙 엔진이다. 공식 문서 첫 화면 기준 핵심 기능은 PagedAttention, continuous batching, CUDA/HIP graph 실행, 투기적 디코딩(n-gram, suffix, EAGLE, DFlash), 광범위한 양자화(FP8, MXFP8/MXFP4, NVFP4, INT8, INT4, GPTQ/AWQ, GGUF, compressed-tensors), 텐서·파이프라인·데이터·전문가(expert)·컨텍스트 병렬, disaggregated prefill/decode, prefix caching, 구조화 출력, 도구 호출, multi-LoRA다. OpenAI 호환 API 서버와 함께 Anthropic Messages API, gRPC도 제공하고 HuggingFace 모델 아키텍처 200개 이상을 지원한다고 소개한다. 하드웨어는 NVIDIA/AMD GPU, x86/ARM/PowerPC CPU, Google TPU, Intel Gaudi, Apple Silicon 등이다.

**PagedAttention (공식 설계 문서).** KV cache를 고정 크기 블록으로 나누어 저장한다. 블록 하나는 BLOCK_SIZE개의 토큰을 담으며, 문서 예시로 block size 16, head size 128이면 블록 하나가 16 × 128 = 2,048개 원소다. 키 캐시 레이아웃은 `[num_blocks, num_kv_heads, head_size/x, block_size, x]`, 밸류 캐시는 `[num_blocks, num_kv_heads, head_size, block_size]`다. 커널은 warp(32 thread) 하나가 KV 블록 하나를 처리하고, thread block이 한 쿼리·헤드·파티션의 컨텍스트 토큰 전체를 맡으며, 메모리 coalescing을 강조한다. 요점은 연속된 큰 메모리를 미리 잡는 대신 비연속 블록을 테이블로 가리켜 단편화 낭비를 줄인다는 것이다.

**V1 프로세스 구조 (공식 아키텍처 문서).** API Server 프로세스(HTTP, 토크나이즈, 멀티모달 로드, ZMQ로 엔진과 통신) + Engine Core 프로세스(스케줄러, KV cache 관리, busy loop로 GPU worker에 작업 분배, data parallel rank당 1개) + GPU Worker 프로세스(GPU당 1개, 개수는 TP × PP) + 데이터 병렬일 때만 DP Coordinator 1개. 프로세스 수 공식은 `A + DP + N`(+1 if DP>1). 문서 예시: `vllm serve -tp=4`는 API 1 + 엔진 1 + 워커 4 = 6개, `-tp=2 -dp=4`(GPU 8장)는 API 4 + 엔진 4 + 워커 8 + 코디네이터 1 = 17개. 운영 포인트는 이 프로세스들이 CPU를 쓰므로 GPU만이 아니라 CPU 코어 사이징이 필요하다는 점이다(문서가 별도 절로 안내).

**스케줄링과 튜닝 (공식 optimization 문서).** V1은 가능한 한 chunked prefill이 기본 켜져 있고, 스케줄러는 대기 중인 decode 요청을 먼저 배치한 뒤 `max_num_batched_tokens` 예산이 남으면 prefill을 넣는다. prefill이 예산에 안 들어가면 자동으로 쪼갠다. 문서 권고: 처리량을 최적화하려면 특히 큰 GPU의 작은 모델에서 `max_num_batched_tokens > 8192`를 권장하고, `max_num_batched_tokens`가 `max_model_len`과 같으면 V0 기본 스케줄링과 거의 같아진다. chunked prefill을 끄면 `max_num_batched_tokens`가 `max_model_len`보다 커야 하고 아니면 서버 시작 시 크래시할 수 있다. 메모리가 부족할 때는 `max_num_seqs`나 `max_num_batched_tokens`를 줄여 동시 요청 수를 낮춘다.

**Prefix caching (공식 문서).** KV 블록을 "블록 안 토큰 + 앞쪽 prefix"의 해시로 식별해 같은 prefix를 가진 새 요청이 블록을 재사용한다. 가득 찬 블록만 캐시한다. v0.11부터 기본 해시는 sha256이고 `--prefix-caching-hash-algo`로 `sha256_cbor`(재현 가능, 언어 간 호환), `xxhash`, `xxhash_cbor`를 고를 수 있다. 비암호화 해시는 이론적으로 충돌 위험이 커진다고 문서가 경고한다. LoRA ID, 멀티모달 입력 해시, cache salt 같은 extra hash로 멀티 테넌트 환경의 캐시를 분리할 수 있다. 운영 포인트는 RAG처럼 공통 시스템 프롬프트·문서가 반복되는 워크로드에서 TTFT를 줄이되, 테넌트 간 캐시 공유를 salt로 막아야 한다는 점이다.

**Disaggregated prefill (공식, 실험 기능).** prefill과 decode를 서로 다른 vLLM 인스턴스에 두어 TTFT와 ITL(토큰 간 지연)을 따로 튜닝하고 tail ITL을 통제한다. 문서는 "처리량을 개선하지 않는다"고 명시한다. 커넥터는 NixlConnector, MooncakeConnector, LMCache, MoRIIOConnector(ROCm), OffloadingConnector(CPU 오프로딩), FlexKV, MultiConnector 등 9종이다. KV 전송 커넥터 쪽은 [[vllm-moriio-kv-connector]] 노트도 참고.

**관측성 (공식 metrics 문서).** `/metrics` Prometheus 엔드포인트에 `vllm:` 접두어로 `num_requests_running`, `kv_cache_usage_perc`(KV 블록 사용률 0~1), `prefix_cache_queries/hits`, `prompt_tokens_total`, `generation_tokens_total`, `time_to_first_token_seconds`, `inter_token_latency_seconds`, `request_time_per_output_token_seconds`, `e2e_request_latency_seconds`, `request_prefill_time_seconds`, `request_decode_time_seconds`, `request_queue_time_seconds` 등이 있다. TPOT는 `(end-to-end latency - TTFT) / (출력 토큰 수 - 1)`로 계산되고 출력이 1토큰 이하면 0으로 기록된다. 참고 Grafana 대시보드 예제가 저장소에 있다. 공고의 "모니터링" 업무는 이 지표로 SLO(TTFT, TPOT)와 KV 사용률 알람을 거는 일이 기본이 될 것이다(해석).

### 3-3. Dynamo (NVIDIA)

**역할.** 저장소 README의 정의로 "오픈소스 데이터센터급 추론 스택", 즉 추론 엔진 위의 오케스트레이션 계층이다. SGLang, TensorRT-LLM, vLLM을 대체하지 않고 이들을 다중 노드 추론 시스템으로 묶는다. Rust로 성능을, Python으로 확장성을 확보했다. 라이선스 Apache-2.0, 커뮤니티 기여자 160명 이상으로 표기. README 기준 "여러 GPU·노드에서 LLM을 서빙하며 조율이 필요할 때, KV 인지 라우팅으로 중복 prefill을 피하고 싶을 때, prefill/decode를 독립적으로 확장하고 싶을 때, SLA를 만족하며 TCO를 줄이는 오토스케일링이 필요할 때, 새 replica의 cold start를 빠르게 하고 싶을 때" 쓰고, 단일 GPU에서 한 모델을 돌리는 경우에는 엔진만으로 충분할 가능성이 높다고 스스로 적는다. 이 한 문장이 vLLM과 Dynamo의 역할 차이를 가장 잘 요약한다.

**구성요소 (README).**
- Frontend: OpenAI 호환 HTTP 서버(문서상 포트 8000). 요청 전처리(chat template, 토크나이즈, 검증)를 수행.
- Router: worker 부하와 KV cache 중복(overlap)을 보고 worker를 고르는 KV 인지 라우팅.
- Disaggregated Prefill/Decode: 두 단계를 독립적으로 확장 가능한 GPU 풀로 분리.
- KVBM (KV Block Manager): GPU → CPU → SSD → 원격 스토리지로 KV cache 계층 오프로딩.
- ModelExpress: NIXL/NVLink로 GPU 간 모델 가중치를 스트리밍해 새 replica cold start 단축.
- Planner: 워크로드를 프로파일링해 SLA를 만족하는 최소 비용으로 풀 크기를 조정하는 SLA 기반 오토스케일러.
- Grove: NVL72 등을 위한 토폴로지 인지 gang scheduling 쿠버네티스 오퍼레이터.
- AISimulate: 실제 GPU 클러스터 없이 서빙 동작을 예측하고 배포 구성을 탐색.
- Fault Tolerance: canary health check와 in-flight 요청 마이그레이션.

**백엔드 지원표 (README).** Disaggregated Serving, KV-Aware Routing, SLA-Based Planner, 멀티모달, 도구 호출은 SGLang·TensorRT-LLM·vLLM 모두 지원. KVBM은 TensorRT-LLM과 vLLM 지원, SGLang은 진행 중(표기 🚧).

**Disaggregated serving 동작 (저장소 docs, system-architecture).** 요청 한 건은 (1) prefill 엔진이 KV cache 계산, (2) prefill 엔진이 KV를 decode 엔진으로 전송, (3) decode 엔진이 토큰 생성의 3단계다. 예컨대 메모리 대역폭 중심인 decode에는 큰 TP, 연산 중심인 prefill에는 작은 TP를 주어 각각에 맞게 구성할 수 있다. KV 전송은 NIXL이 prefill VRAM에서 decode VRAM으로 직접 보내며 non-blocking이라 전송 중에도 GPU forward가 다른 요청을 처리한다. `PrefillRouter`가 prefill worker 선택(KV 인지 또는 부하 기반) → prefill 실행 후 `disaggregated_params` 수신 → decode worker 라우팅 → NIXL 전송 순으로 오케스트레이션한다. 백엔드별 전달 메타데이터가 다르다: SGLang은 `bootstrap_info`를 써서 prefill이 백그라운드로 돌고 decode가 즉시 시작될 수 있고, vLLM은 `kv_transfer_params`(블록 ID와 원격 worker 정보)를 쓰며 prefill이 동기식이라 decode가 prefill 완료를 기다리고, TRT-LLM은 `opaque_state`를 쓰며 역시 동기식이다. xPyD(prefill x개, decode y개)는 런타임에 worker를 추가·제거해 재구성할 수 있고, worker는 discovery 서비스에 등록·해제된다.

**분산 런타임 (저장소 docs).** Rust `DistributedRuntime`이 discovery, endpoint 등록, 요청 전송, 수명주기를 맡고 Namespace → Component → Endpoint 계층으로 서비스를 구성한다. discovery 백엔드는 쿠버네티스에서는 `DynamoWorkerMetadata` 리소스와 EndpointSlice, 베어메탈에서는 기본 etcd다. 요청 평면은 기본 `tcp`, 선택 `nats`. 라우팅된 요청이 실패하면 해당 worker를 기본 5초(`DYN_RUNTIME_INHIBITED_DURATION_SECS`) 동안 임시로 제외한다. 쿠버네티스에서는 Dynamo 자체 Frontend 라우팅과, Gateway API Inference Extension(GAIE)의 Endpoint Picker Plugin을 쓰는 방식 두 가지 토폴로지를 지원한다.

**벤더 제시 성능 수치 (README "Key Results", 전부 NVIDIA/제3자 발표 자료 인용이며 직접 재현하지 못함).**
- 처리량 7배/GPU: DeepSeek R1, GB200 NVL72 + Dynamo 대 B200 비적용 (InferenceX)
- 모델 시작 7배 빠름: ModelExpress 가중치 스트리밍, DeepSeek-V3 on H200
- TTFT 2배 빠름: KV 인지 라우팅, Qwen3-Coder 480B (Baseten 벤치마크)
- SLA 위반 80% 감소: Planner 오토스케일링, TCO 5% 절감 (Alibaba APSARA 2025 발표)
- 처리량 750배: DeepSeek-R1, GB300 NVL72 (InferenceXv2)
이 수치는 최신 NVL72급 하드웨어에서의 대형 MoE 모델 조건이라 일반 서비스용 중소형 모델 환경에 그대로 적용되지 않는다.

**운영 포인트와 주의.** (1) 설치는 컨테이너(`nvcr.io/nvidia/ai-dynamo/vllm-runtime:1.5.0` 등) 또는 `ai-dynamo[vllm]` PyPI 패키지이며 TRT-LLM만 별도 인덱스가 필요하다. 로컬에서는 `python3 -m dynamo.frontend`와 `python3 -m dynamo.vllm --model ...` 두 프로세스로 시작한다. (2) README의 "New in 1.0"에서 DGDR(모델·하드웨어·SLA를 YAML 한 장으로 지정하는 zero-config 배포)은 beta로 표기돼 있다. (3) 문서에 "disaggregation은 어느 단계도 공짜로 만들지 않는다"는 취지의 주의가 있어, 짧은 프롬프트·낮은 부하에서는 KV 전송 오버헤드 때문에 이득이 없을 수 있다. (4) 공고에서 Dynamo가 "운영하는 프레임워크"로 이름만 나올 뿐 토스가 실제 사용 중인지 평가 중인지는 알 수 없다.

### 3-4. Triton Inference Server

**역할.** 여러 딥러닝·ML 프레임워크의 모델을 한 서버에서 서빙하는 범용 모델 서버다. 공식 문서 기준 백엔드는 TensorRT, PyTorch, ONNX, OpenVINO, Python, RAPIDS FIL 등이고 NVIDIA GPU, x86/ARM CPU, AWS Inferentia에서 동작한다. 기능은 동시 모델 실행(모델별 스케줄링 알고리즘 설정), dynamic batching, 시퀀스 배칭(상태 관리), ensemble과 BLS(Business Logic Scripting)를 통한 파이프라인, 파일시스템 기반 model repository와 관리 API, KServe 기반 HTTP/REST·gRPC, C/Java API, GPU 사용률·처리량·지연 메트릭, 쿠버네티스 헬스 엔드포인트, 설정 벤치마크용 Model Analyzer다. 저장소 기준 최신 릴리스는 2.72.0(26.08 컨테이너), 라이선스 BSD-3-Clause.

**Dynamic batching (공식).** `dynamic_batching {}` 블록으로 켠다. 문서는 대부분의 모델에서 `preferred_batch_size`를 지정하지 말라고 한다(특정 배치 크기에서 성능이 크게 좋은 TensorRT 다중 프로파일 같은 경우에만). `max_queue_delay_microseconds`는 요청이 다른 요청을 기다려 배치를 키울 수 있는 최대 대기 시간이다(문서 예 100). 그 밖에 `preserve_ordering`(응답 순서 보장), `priority_levels`와 `default_priority_level`(높은 우선순위가 낮은 요청을 추월), `ModelQueuePolicy`(`max_queue_size`, `timeout_action`, `default_timeout_microseconds`)가 있다. 운영 포인트는 embedding 모델처럼 요청이 작고 많은 워크로드에서 지연 예산과 처리량의 교환을 `max_queue_delay`로 조절하는 것이다.

**Sequence batcher와 LLM.** 상태가 있는 모델은 `sequence_batching`으로 같은 시퀀스를 같은 모델 인스턴스로 보내고, `iterative_sequence: true`로 LLM 스타일의 반복 실행(연속 배칭 지원)을 쓸 수 있다고 문서가 설명한다.

**vLLM 백엔드 (vllm_backend 저장소 README).** 파이썬 기반 통합으로, 모든 요청이 받자마자 vLLM의 `AsyncEngine`에 올라가며 in-flight batching과 paged attention은 vLLM 엔진이 처리한다. 즉 Triton은 HTTP/gRPC·모델 저장소·메트릭·쿠버네티스 통합을 맡고 LLM 배칭은 vLLM에 위임하는 분업이다. 설정은 `model.json`(vLLM AsyncLLMEngine 인자: `tensor_parallel_size`, `gpu_memory_utilization` 기본 90% 등)과 `config.pbtxt`(Triton 메타데이터, 다중 GPU면 instance group `kind: KIND_MODEL`, `GPU_DEVICE_IDS`는 TP × PP 개수와 일치해야 함). Triton 24.08부터 vLLM 메트릭을 `vllm:` 접두어로 노출하며, 수집하려면 `model.json`에 `"disable_log_stats": false`, `config.pbtxt`에 `REPORT_CUSTOM_METRICS: "true"`가 필요하다. 한계로 문서가 적은 것은 vLLM 컨테이너 지원이 Triton 23.10부터라는 점, 여러 서버 인스턴스는 고유한 `shm-region-prefix-name`이 필요하다는 점, 메트릭 보고가 성능에 영향을 줄 수 있다는 점이다.

### 3-5. 세 도구를 어떻게 조합해 볼 수 있나 (해석)
- vLLM 단독: 가장 단순. OpenAI 호환 서버를 쿠버네티스 Deployment로 띄우고 Prometheus 지표로 오토스케일.
- Triton + vllm_backend: embedding·reranker·전후처리 모델과 LLM을 한 서버 규약(KServe 계열)으로 통일하고 싶을 때. 아래 6절에서 보듯 토스증권 사례가 이 조합이다.
- Dynamo + vLLM 백엔드: 대형 모델·다중 노드·prefill/decode 분리·KV 인지 라우팅이 필요할 때. 소규모에서는 오버엔지니어링일 수 있다.

## 4. 공통 개념 해설 (일반 지식, 공고에 없음)

- **serving**: 학습된 모델을 API로 받아 추론 결과를 돌려주는 운영 계층. 지표는 지연, 처리량, 가용성, 비용.
- **KV cache**: 어텐션에서 이전 토큰의 key/value를 저장해 재계산을 피하는 캐시. 컨텍스트가 길고 동시 요청이 많을수록 GPU 메모리를 크게 차지하는 병목.
- **프리필 vs 디코드**: 프롬프트를 한꺼번에 처리하는 연산 중심 단계(prefill)와 토큰을 하나씩 생성하는 메모리 대역폭 중심 단계(decode). 병목이 달라 분리하거나 chunk로 나눠 스케줄링한다(Dynamo·vLLM 문서가 같은 설명을 한다).
- **TTFT / TPOT / ITL**: 첫 토큰까지의 시간, 이후 토큰당 시간, 스트리밍 출력 사이 간격. 사용자 체감 지연의 축.
- **양자화**: 가중치·KV cache를 FP8/INT4 등으로 줄여 메모리와 속도를 개선. 품질 저하 검증 필수.
- **투기적 디코딩**: draft 모델이 여러 토큰을 제안하고 큰 모델이 한 번에 검증. 엄격한 검증이면 출력 분포가 같다.
- **Tensor/Pipeline parallelism**: 한 GPU에 안 들어가는 모델을 가중치 분할(텐서) 또는 레이어 분할(파이프라인)로 여러 GPU에 올림.
- **Model Registry**: 모델 버전·메타데이터·승인 상태를 관리하는 저장소. 실험에서 배포로 가는 경로의 중심.
- **오케스트레이션**: Kubernetes 위에서 GPU 노드 스케줄링, 오토스케일링, 롤링 배포, 헬스체크를 자동화하는 일.
- **embedding 서빙**: 출력이 한 번의 forward로 끝나므로 배치와 대량 처리량이 핵심이고, 검색/RAG의 지연 예산을 좌우한다.

## 5. 구체 수치 요약

- 공고 자체에는 연봉, 인원, 트래픽 규모, GPU 종류 수치가 없다. 확인되는 구체 사실은 업무 4개, 자격 5개, 우대 4개, 전형 7단계와 vLLM/Dynamo/Triton/Model Registry 키워드다.
- vLLM 프로세스 수 공식 `A + DP + N (+1)`, 문서 예 6개와 17개 프로세스(vLLM 공식 아키텍처 문서)
- vLLM `max_num_batched_tokens > 8192` 권고(큰 GPU·작은 모델 처리량용, vLLM optimization 문서)
- Dynamo 벤더 수치: 7배, 7배, 2배, 80%, 750배(위 3-3 상세, 재현 안 함)
- Triton 2.72.0 / 26.08 컨테이너, vllm_backend 메트릭은 24.08부터, vLLM 컨테이너 지원은 23.10부터
- 토스증권 글의 수치는 6절 참조

## 6. 토스 공개 기술 블로그 확인 결과

기술 블로그 메인(toss.tech)의 인기 글과 검색으로 관련 글을 찾았다. 아래 요약은 WebFetch의 요약 응답에 의존한 것이므로, 면접 준비에 쓰려면 원문을 직접 읽어 수치를 재확인해야 한다.

| 글 | 날짜·저자 소속 | 요지 |
|---|---|---|
| LLM 쉽고 빠르게 서빙하기 (toss.tech/article/llm-serving) | 2024-11-26, 토스증권 ML Engineer | Llama3 8B를 표준 Transformers로 돌리면 단순 질문에도 수십 초 걸린다는 문제에서 출발. vLLM, TensorRT-LLM, TGI, LMDeploy를 TPS·TTFT·사용성·모델 지원으로 비교해 vLLM 채택. 구성은 vLLM 엔진 + Triton(동적/연속 배칭) + KServe(쿠버네티스 서버리스) + ArgoCD. 공통 Docker 이미지와 YAML 한 장으로 배포하고, Triton의 표준 로그/Prometheus 메트릭으로 Grafana 대시보드에 TPS·지연을 자동 수집. 글이 든 정량 주장: KV cache로 추론 계산량 60% 이상 감소, Triton 동적 배칭으로 처리량 5배 이상 가능(내부 테스트 2024-09-05 기준). |
| 토스증권이 GPU-aware를 넘어 GPU-native 클러스터를 구축한 방법 (toss.tech/article/gpu-native-cluster) | 2026-09-15, 토스증권 Data Engineer와 ML Platform팀 | 노드가 Ready여도 개별 GPU가 오류일 수 있다는 문제. nvidia-validator, DCGM Exporter로 드라이버·Container Toolkit·Device Plugin·CUDA 상태와 사용률·VRAM·온도·전력·Xid 오류를 감시. 신규/복구 GPU 노드는 표준 스펙 → burn-in → 쿠버네티스 편입 → CUDA 런타임 → LLM 서빙까지 5단계 preflight를 통과해 `preflight=passed` 라벨이 붙은 노드만 스케줄링. MIG로 물리 GPU를 분할하고 MIG 조각을 한 GPU부터 채우는 Packed Allocation을 구현해 NVIDIA k8s-device-plugin v0.20.0에 업스트림 기여. H100 HBM 복구 불가 메모리 오류(DBE) 사례에서 Xid 48·171 → 94 → 63 → 154 신호 흐름으로 드라이버 문제와 앱 문제를 구분. DRA 표준화 시 이런 보완 로직이 코어로 흡수될 것이라는 전망. |
| 리더보드 1등 LLM, 토스에서도 1등일까? - Toss Benchmark 구축기 (toss.tech/article/toss-benchmark) | 2026-09-16, 토스 LLM Modeling 팀 | 공개 리더보드 순위가 토스 도메인 성능을 예측하지 못해 자체 벤치마크(한국어 일반 성능, 커머스·금융·고객응대·사내 개발 도메인 과제, 공통 역량 Toss IFBench·Toss Knowledge)를 구축. 영어 점수와 한국어 성능이 어긋남(Qwen3.6-27B가 더 높은 영어 점수 모델보다 한국어에서 우수). reasoning을 끄면 GLM-5.1은 30.6점 하락, gemma-4-26b는 6점 하락. Toss IFBench는 실제 과제 성능과 피어슨 r=0.87, 공개 AAII 지수는 r=0.17. |
| 토스가 다양한 ML 모델을 만드는 법: Feature Store & Trainkit (toss.tech/article/feature-store-trainkit) | 2025-08-14 | 오프라인 저장소와 온라인 저장소(Aerospike), Feature Serving API로 구성된 Feature Store와 학습 파이프라인 자동화 도구 Trainkit(Data Module, Target, Feature Service, Feature Processor, Feature Package). training-serving skew 해소와 PIT 조인. Model Registry, Inference System, Monitoring System과 함께 엔드투엔드 ML 운영 체계를 이룬다고 설명. |

이 글들이 공고와 직접 맞닿는 지점은 다음과 같다. 공고의 "GPU 자원과 클러스터를 효율적으로 운영"은 GPU-native 글(preflight, MIG, Packed Allocation, 업스트림 기여)과, "vLLM, Triton, Model Registry로 실험과 배포 자동화"는 llm-serving 글(Triton + vLLM + KServe + YAML 배포) 및 Feature Store 글(Model Registry 언급)과 연결된다. "오픈소스 기여" 권장은 k8s-device-plugin 업스트림 기여 사례가 실제 근거다. 다만 llm-serving 글은 토스증권, GPU 글도 토스증권·ML Platform팀 소속 필자의 글이며, 이 공고(토스 소속 AI Platform 팀)의 현재 스택과 동일하다고 단정할 수 없다. 또한 llm-serving 글은 2024-11 시점이고 이 공고는 Dynamo를 포함하므로 이후 구성이 바뀌었을 가능성이 크다(추정).

## 7. 비판적 평가·한계

- 직무 범위가 넓다. 운영(장애 대응·배포 자동화), 성능 엔지니어링(GPU 레벨 튜닝), 플랫폼 개발(일반화·확장)이 한 포지션에 겹쳐 있어 실제 비중(온콜 비율, 프레임워크 개발 대 운영)이 공고만으로는 보이지 않는다. 프리 인터뷰에서 확인할 항목이다.
- "정답이 정해지지 않은 문제를 구조화" 같은 서술은 매력적이지만 평가 기준으로는 모호하다. 면접이 "심층 기술 면접 + ML 시스템 설계"라고 밝힌 부분이 실질적 신호이므로 vLLM 내부(스케줄러, KV cache 관리, prefix caching, chunked prefill)와 시스템 설계(트래픽 급증, 모델 롤아웃, GPU 비용)를 준비하는 쪽이 현실적이다.
- 연차·학력 조건이 없다는 것은 진입 장벽이 낮다기보다 평가가 포트폴리오·면접에 집중된다는 의미로 읽는 편이 안전하다.
- 기술 스택이 NVIDIA 중심(Triton, Dynamo)이다. 단, vLLM 자체는 AMD GPU, TPU 등도 지원한다고 문서가 밝히므로 공고가 하드웨어 다양성을 요구하지 않을 뿐이다.
- Dynamo는 최신 하드웨어 조건의 벤더 수치가 많고 일부 기능이 beta다. 도입 근거는 자체 부하 테스트로 만들어야 한다.
- 이 노트의 3~4절 해설은 문서 버전(2026-10-01 기준 main)에 묶여 있어 버전이 바뀌면 달라질 수 있다.

## 9. 관련 노트

- [[vllm-moriio-kv-connector]]: vLLM KV 전송 커넥터(disaggregated prefill 관련)
- [[woowa-ai-platform-2-llmops]]: 다른 회사의 AI 플랫폼/LLMOps 사례
- [[inflab-ai-gateway]]: LLM 게이트웨이 사례
- [[jina-ocr-v1-threads]]
- [[latex-resume-template-kor]]
- [[github-donggyun112]]
- [[hada-claude-opus-5-5-prompting]]

## 10. 출처

- https://toss.im/career/job-detail?job_id=7786567003&company=%ED%86%A0%EC%8A%A4&sub_position_id=7786567003 (headless Chrome 렌더, 2026-10-01)
- https://docs.vllm.ai/en/latest/ 및 https://docs.vllm.ai/en/latest/design/paged_attention/
- vLLM 저장소 클론의 docs: design/arch_overview.md, design/prefix_caching.md, design/metrics.md, features/disagg_prefill.md, configuration/optimization.md (2026-10-01)
- https://github.com/ai-dynamo/dynamo 저장소 클론: README.md, docs/fern/pages/developer-guide/knowledge-base/concepts/system-architecture/disaggregated-serving.md, architecture.md (2026-10-01)
- https://github.com/triton-inference-server/server
- https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/index.html
- https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/batcher.html
- https://github.com/triton-inference-server/vllm_backend
- https://toss.tech/ , https://toss.tech/article/llm-serving , https://toss.tech/article/gpu-native-cluster , https://toss.tech/article/toss-benchmark , https://toss.tech/article/feature-store-trainkit (WebFetch 요약 응답 기반)

## 11. 확인하지 못한 항목

- 공고 마감 여부/게시일, 연봉·근무 형태 세부, 팀 규모, 토스의 실제 현재 서빙 스택 구성. 사유: 공고 본문에 없음.
- 공고 링크 영상(오프더레코드 EP.4)과 아티클 "ML 플랫폼으로 개발 속도와 안정성 높이기"의 본문. 사유: 링크 URL이 렌더 텍스트에 없어 특정하지 못함.
- 토스 기술 블로그 4건의 원문 직접 열람. 사유: WebFetch 요약 응답만 확보. 수치는 원문 재확인 필요.
- Dynamo 공식 문서 사이트(docs.nvidia.com/dynamo) 본문. 사유: WebFetch가 목차만 반환해 클론한 저장소의 docs로 대체.
- vLLM의 라이선스 표기(이번에 열람한 문서에서 확인하지 않음), Dynamo 벤더 성능 수치의 재현.
- 같은 팀의 Platform/Recommendation 포지션 본문.
