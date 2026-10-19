---
title: Reddit r/LocalLLaMA - Qwen 3.6 27B Q4_0 MTP GGUF
source: https://www.reddit.com/r/LocalLLaMA/comments/1t50s4i/qwen_36_27b_q40_mtp_gguf/
type: blog
category: LLM-추론-인프라
tags: [research, qwen, gguf, mtp, speculative-decoding, llama-cpp]
researched: 2026-10-01
---
# Reddit: Qwen 3.6 27B Q4_0 MTP GGUF

> [!summary] 한줄요약
> Reddit 원문은 접근 차단으로 확인하지 못했다. 아래는 같은 주제(Qwen3.6-27B MTP GGUF)의 Hugging Face 모델 카드 정리이며, 해당 게시물과 동일 자료인지는 미확인이다.

> [!warning] 확인 불가: Reddit 접근 차단
> WebFetch는 "unable to fetch from www.reddit.com", curl은 403("blocked due to a network policy"). 게시글 본문, 댓글, 작성자, 이 게시물의 Q4_0 파일 정보는 확인하지 못함. 우회 시도는 하지 않음. 아래는 검색으로 찾은 유사 대체 자료(froggeric/Qwen3.6-27B-MTP-GGUF)이며, 해당 Reddit 글과 동일 자료인지 확인되지 않음.

## 무엇인가 / 해결하는 문제 (대체 자료 기준)
- Qwen3.6-27B(dense, vision/thinking/tool use)에 MTP(Multi-Token Prediction) head를 포함한 GGUF. 모델 자체 head로 self-speculative decoding, 별도 draft 모델/VRAM 불필요.
- base_model: Qwen/Qwen3.6-27B, Apache-2.0. 이 HF repo의 quant: F16, Q8_0, Q6_K, Q5_K_M, Q4_K_M, IQ4_XS, IQ3_M, IQ2_M (Q4_0은 목록에 없음).

## 핵심 기능·구조·기술
- llama.cpp b9180(2026-05-16) 이상 필요(카드 기재). MTP 지원은 PR #22673(검색 결과 기재).
- 실행 예: `llama-server -m Qwen3.6-27B-Q5_K_M-mtp.gguf --mmproj mmproj-Qwen3.6-27B-f16.gguf --spec-type draft-mtp --spec-draft-n-max 3 -c 262144 ...`
- **카드 측정 조건**: M2 Max 96GB, N=3, 원 구현
  - Q8_0: base 11.4 tok/s → code +123%, creative +48%
  - Q4_K_M: base 15.1 tok/s → code +31%, creative -9%
  - 주류 llama.cpp에서는 약 10-17% 낮음(카드 기재).
- draft acceptance: code 79-89%, creative 39-48%. 작업 유형이 속도 향상을 좌우.
- 하이브리드 구조: 65 layer 중 16개만 KV cache 사용(카드 기재) -> KV 메모리 절감.

## 사용법·설치
1. `brew install llama.cpp`로 설치한다.
2. 위 llama-server 명령으로 실행한다. 비전이 불필요하면 `--mmproj`를 제외한다.
3. 저양자화 + 비코딩 작업은 `--spec-type none`을 권장한다(카드 기재).

## 장단점·한계·성숙도
- 4비트급 양자화에서 창작/분석류는 MTP가 오히려 느려질 수 있음(카드 데이터).
- 개인 변환본(커뮤니티). 공식 Qwen 배포 아님. 다운로드 262,869, 좋아요 81(HF API, 확인 시점).

## 관련 노트
[[qwen3-5-9b]] [[lucebox-hub]] [[qwen-ai-home]]

## 출처
- https://www.reddit.com/r/LocalLLaMA/comments/1t50s4i/qwen_36_27b_q40_mtp_gguf/ (확인 불가)
- https://huggingface.co/froggeric/Qwen3.6-27B-MTP-GGUF (대체)
