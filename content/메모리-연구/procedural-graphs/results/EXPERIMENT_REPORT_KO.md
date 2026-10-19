---
title: "Grounded Semantic Memory × Procedural Graph 재현 보고서"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/procedural-graphs-lab) · 원본 `results/EXPERIMENT_REPORT_KO.md` · 수집 2026-10-16 · 커밋 `2c265f7fb194627f1b39d90207e9dca03b6cee28`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# Grounded Semantic Memory × Procedural Graph 재현 보고서

> [!warning] 위키 편집자 주 (2026-10-18)
> 이 보고서의 2×2 수치(memory 있음 행 62.5% / 57.5%, interaction −0.0%p)와 "결합 가설: 기각" 결론은 큐레이터 `max_tokens=450` 잘림 버그가 있던 시점의 값이다. [[메모리-연구/procedural-graphs/docs/COMBINED_DESIGN|COMBINED_DESIGN]]은 같은 버그를 고친 뒤 memory 있음 행을 60.0% / 62.5%(+2.5%p는 1문항 차이)로 재측정했고, 옛 2×2는 폐기했다고 적는다. [[메모리-연구/procedural-graphs/REVIEW|재현 후기]]의 2026-09-22 정정과도 같은 내용이다. 원문은 당시 기록으로 보존하되, 이 문서의 결합 가설 판정을 최종 결론으로 인용하지 않는다. 두 판정 사이를 가르는 추가 반복 실험은 하지 않았다.

이 보고서가 풀려던 문제는 두 가지다. 첫째, 과거 기록을 저장하는 것만으로 충분한가, 아니면 현재 환경을 다시 확인해야 유용한 기억이 되는가? 둘째, 그렇게 만든 기억에 작업 순서 안내까지 더하면 더 잘 풀리는가? 이를 분리하려고 메모리 3조건, 메모리와 PG의 2×2 비교, PG 자체의 학습 실험을 따로 실행했다.

결과를 읽을 때는 **서로 다른 러너의 점수를 한 표처럼 비교하지 않는 것**이 중요하다. §1의 결합 실험과 §2의 논문 계약 러너는 같은 40문항을 사용하지만 recall 정책 등이 다르다. 또한 §1의 메모리 조건은 이후 잘림 버그가 확인되어 폐기됐다. 이 문서의 가치는 성공률 하나보다, 어떤 구현 차이가 관찰을 바꾸었고 무엇을 다시 시험해야 했는지에 있다.

작성일: 2026-09-19
공통 설정: temperature 0, 단일 run

| 실험 | benchmark | 모델 |
|---|---|---|
| Grounding 3조건 | 공식 CLBench `database_exploration/schema_drift` 40문항 | `deepseek/deepseek-v4.1-flash` |
| 결합 2×2 factorial | 같은 CLBench 40문항 | 같음 |
| PG 재현 | 공개 `ScaleAI/MultiChallenge` train 100 / validation 100 / test 56 | 같음 (별도로 gemini 실행도 보존) |

## 결론 요약

다음은 **2026-09-19 당시의 판정**이다. 특히 1·3번에 사용된 결합 실험 수치는 상단 정정의 영향을 받는다. 이후에는 ‘결합 가설 기각’ 대신 ‘버그 수정 후 차이는 1문항이며, 결합의 추가 이득은 아직 입증되지 않음’으로 읽어야 한다. §2의 별도 3조건 결과와 PG의 형식 안정화 관찰까지 한꺼번에 폐기한다는 뜻은 아니다.

1. **Grounded semantic memory는 재현됐다.** baseline 30.0% → 62.5%, exact two-sided
   McNemar `p=0.0044`로 유의하다. Environment probing까지 포함한 3조건은 논문 서열
   (no memory < trajectory < probed)을 그대로 재현했고, probed는 drift 이후에 **더** 높았다.
2. **Procedural Graph의 정확도 기여는 입증되지 않았다.** 두 모델·세 차례 실행 모두 test에서
   비유의했다(`p=0.607`, `1.000`, `1.000`).
3. **결합 가설은 기각된다.** PG 효과가 semantic memory 유무와 **정확히 동일한 −5.0%p**였고
   factorial interaction은 **−0.0%p**다. 두 축은 독립적으로 작동하며 상보성의 증거가 없다.
4. PG가 실제로 재현한 것은 **형식 안정화**다. 파싱 실패가 0.27 → 0.04/샘플로 줄었다
   (논문 Appendix D.1은 45.7% 감소를 보고). 다만 우리 어댑터는 형식 실패를 재프롬프트로
   복구하므로 그 이득이 점수로 환산되지 않는다.
5. PG 진화는 **validation에 과적합했다.** 최종 후보가 validation 68%인데 test는 62.5%였다.

## 1. 결합 2×2 factorial (CLBench 40문항)

이 비교는 ‘메모리를 이미 가진 에이전트에도 PG가 보탬이 되는가’를 묻는다. 위아래 행은 기억 유무, 좌우 열은 PG 유무다. 한 행에서 좌우를 빼면 PG의 효과가 나오고, 그 효과가 두 행에서 얼마나 다른지가 interaction이다. 아래 옛 표에서는 두 행 모두 −5.0%p라 상호작용이 없다고 판단했다. 그러나 큐레이터 응답 잘림이 메모리 생성에 영향을 준 뒤에는 이 계산을 시스템의 성질로 해석할 수 없다.

| | PG 없음 | PG 있음 | semantic 효과 |
|---|---:|---:|---:|
| **memory 없음** | 30.0% (12/40) | 25.0% (10/40) | — |
| **memory 있음** | **62.5%** (25/40) | 57.5% (23/40) | — |
| **PG 효과** | −5.0%p | −5.0%p | interaction **−0.0%p** |

- Semantic effect: **+32.5%p** (논문 주장 +34%p와 근접)
- PG effect: **−5.0%p**, memory 유무와 무관하게 동일
- PG는 평균 SQL을 줄이지 못했다 (+0.43, +0.70). LLM 호출은 문항당 27회로 메모리 조건(14.7회)의 2배.

### Paired 검정 (exact two-sided McNemar)

| 비교 | A만 | B만 | p | 판정 |
|---|---:|---:|---:|---|
| Baseline vs Semantic | 3 | 16 | **0.0044** | 유의 |
| Baseline vs Combined | 2 | 13 | **0.0074** | 유의 |
| PG vs Combined | 1 | 14 | **0.0010** | 유의 |
| Baseline vs PG | 3 | 1 | 0.625 | 비유의 |
| Semantic vs Combined | 6 | 4 | 0.754 | 비유의 |

당시 집계에서는 semantic memory가 포함된 비교만 유의했고, PG 자체의 차이는 어느 방향으로도 유의하지 않았다. 다만 이 검정은 위 표의 관측치를 대상으로 한다. 통계 검정을 통과해도 실행 중 메모리 생성이 잘렸다는 결함이 사라지지는 않으므로, 폐기된 실행의 p값을 수정 후 결과에 옮겨 붙이면 안 된다.

### 공정성 검증

`analyze_combined` 기준 전부 통과했다. 결합 조건은 semantic 조건의 문항별 스냅샷과 recall을
**ID 순서까지 동일하게** replay했고, 자체 write는 차단됐으며, PG 외 core edge도 일치한다.
과거 run에서 PG가 만든 `memory_read` 쿼리가 달라 top-k가 어긋났던 오류는
`--recall-policy required`가 질문 기반 고정 recall을 강제하여 재발하지 않았다.

## 2. Grounding 논문 3조건 (논문 계약 충실 러너)

여기서는 결합 여부를 잠시 내려놓고, 기억을 만드는 방식만 바꾼다. 이전 경험이 없는 조건, 실행 기록만 정리하는 조건, 그 기록을 현재 DB에 대조하는 조건이다. DB 구조가 바뀐 뒤에도 기억이 도움이 된다면, 단순히 과거 답을 반복하는 것보다 강한 근거가 된다.

`paper_grounding_eval.py`는 공식 CLBench `ContinualLearningSystem` 인터페이스를 직접 구현하고
강제 recall 없이 논문의 on-demand memory tool 계약을 따른다. probe는 논문 제약대로 문항당 4회로
하드 캡했다.

| 조건 | 정확도 | drift 전/후 | 평균 SQL | 논문 |
|---|---:|---:|---:|---:|
| `no_memory` | 37.5% (15/40) | 35% / 40% | 11.25 | 39% |
| `trajectory_memory` | 60.0% (24/40) | 75% / 45% | 7.13 | 70% |
| `environment_probing_memory` | **87.5%** (35/40) | 85% / **90%** | 6.40 | 73% |

쿼리 감소폭도 유사하다 (11.25 → 6.40, −43%; 논문 8.8 → 4.7, −47%).

이 실행에서 가장 중요한 차이는 구조 변경(drift) 이후다. 현재 DB를 확인할 수 있는 probing 조건은 90%였고, 과거 실행 기록에만 의존한 trajectory 조건은 45%로 떨어졌다. 이는 큐레이터가 문항당 최대 4회의 조회로 낡은 레코드를 갱신한다는 설명을 뒷받침한다.

다만 drift 전후 문항이 같지는 않으므로, 85%에서 90%로 오른 사실만으로 ‘환경이 바뀔수록 더 잘한다’고 결론 내릴 수는 없다. 여기서 확인한 것은 이 단일 실행에서 현재 환경을 확인하는 조건이 높은 정확도와 적은 SQL 호출을 함께 보였다는 점이다.

## 3. Procedural Graph 재현 (MultiChallenge)

논문 3절대로 솔버를 **텍스트 ReAct**로 구현했다 (`Thought:` / `Action: name(arg=value)`).
이전 구현은 native function calling에 `tool_choice="required"`를 걸어 형식을 API로 강제했는데,
논문이 PG의 효과로 보고하는 "파싱 실패 45.7% 감소" 통로를 막는 설정이었다.

### 최종 결과 (test 56)

| 실행 | baseline | expert PG | evolved PG | p (base vs evolved) |
|---|---:|---:|---:|---:|
| gemini-3.1-flash-lite | 29/56 (51.8%) | 29/56 | 32/56 (57.1%) | 0.607 |
| deepseek v1 (`q`=마지막 턴) | 34/56 (60.7%) | 36/56 | 35/56 (62.5%) | 1.000 |
| **deepseek v2 (`q`=대화 전체)** | 34/56 (60.7%) | 32/56 | 35/56 (62.5%) | **1.000** |

두 모델, 세 차례 실행 모두 비유의하다. baseline이 두 v 실행에서 34/56으로 동일한 것은
temperature 0에서의 재현성을 확인해 준다.

### 진화는 작동했다

| 라운드 | 편집 | validation | 판정 |
|---|---|---:|---|
| scratch (2노드 1엣지) | — | 63/100 | 기준선 |
| **R1** | 노드 +5, 엣지 +6/−1 | **68/100** | ✅ 채택 |
| R2–R5 | 엣지 추가 + 속성 수정 | `null` | ❌ 구조 검증 탈락 (순환) |

최종 그래프는 **7노드 6엣지**로 논문 Table 7의 MultiChallenge 7노드 7 triplet과 거의 같다.
구조도 과제 성격에 부합한다.

```
Start → inspect_context → identify_constraints → resolve_conflicts
      → draft_response → verify_response → submit_response
```

### validation 과적합

진화는 학습용 실행 기록을 보고 그래프를 고친 뒤, validation 점수가 떨어지지 않는 후보만 남기는 방식이다. 그래서 validation에서 좋아 보이는 그래프가 마지막에 한 번 보는 test에서도 좋아지는지를 따로 확인해야 한다.

| | validation 100 | test 56 |
|---|---:|---:|
| R1 채택 그래프 | **68%** | **62.5%** |

당시에는 validation 68%와 test 62.5%의 5.5%p 격차를 validation 과적합으로 해석했다. 후보를 고르는 데 validation을 반복 사용하므로 그 위험은 실제로 있다. 다만 서로 다른 문항 집합 사이의 이 격차만으로 과적합의 원인을 확정할 수는 없다. 더 직접적인 결과는 최종 그래프의 test 정확도가 baseline 대비 유의하게 좋아지지 않았다는 것이다.

### 축별 분해 (deepseek v2, baseline → evolved)

| 축 | n | base | evolved | 차이 |
|---|---:|---:|---:|---:|
| INFERENCE_MEMORY | 22 | 12 | 14 | **+2** |
| INSTRUCTION_RETENTION | 14 | 11 | 12 | +1 |
| RELIABLE_VERSION_EDITING | 9 | 4 | 5 | +1 |
| SELF_COHERENCE | 11 | 7 | 4 | **−3** |

세 축에서 얻고 한 축에서 잃어 상쇄된다.

### rejection memory는 구조 오류를 막지 못했다

논문 `ℋrejected`의 네 요소(candidate graph, proposed edits, training trajectories,
validation outcomes)를 모두 저장하고 refiner 프롬프트에 부정 증거로 투입한다. 그럼에도
R2–R5가 **네 라운드 연속 같은 사유("graph contains a cycle")로 탈락**했다. 거절 사유가
짧은 문자열이고 **어느 엣지가 순환을 만들었는지 알려주지 않기 때문**으로 보인다.
`validate()`는 그 정보를 알고 있으나 전달하지 않는다. 개선 여지로 기록한다.

## 4. 실행 중 발견하여 수정한 결함

전부 **라이브 아티팩트를 직접 열어서** 발견했다. 단위 테스트만으로는 대부분 통과했을 것이다.

| 결함 | 증상 | 영향 |
|---|---|---|
| Distiller 무음 잘림 | reasoning이 completion 예산 4096을 전부 소모, 본문 0자. `finish_reason` 폐기로 "할 말 없음"으로 해석 | 40 에피소드 중 **39개** 메모리 파이프라인 무력화 |
| `memory_read` 설명 오용 | 큐레이터용 문구를 솔버에 재사용 | 솔버가 도구 용도를 모름 |
| 프로토콜 미고지 | "턴당 도구 하나"를 강제하면서 고지하지 않음 | 위반 6 → 2건 |
| probe 예산 미강제 | 문서는 "최대 4회"인데 코드에 제한 없음 | 실측 19회 → 하드 캡 |
| 솔버 형식 강제 | function calling + `tool_choice="required"` | PG 기여 통로 차단 |
| judge 무음 잘림 | 300토큰에서 잘려 `PARSE_ERROR` → **오답 집계** | 측정 오염 |
| **guidance `q` 오정의** | 논문의 "full initial instruction" 대신 마지막 턴 한 줄 | 조언자가 "conversation history is empty"라며 눈 가린 채 조언 |
| 타임아웃 누락 (자체 회귀) | pydantic-ai 전환 시 유실 | 좀비 커넥션에 16분 무한 대기 |
| `tool_choice` 형식 불일치 (자체 회귀) | OpenAI dict를 그대로 전달 | `AssertionError` |
| 스레드 안전성 (자체 회귀) | `AsyncOpenAI` 하나를 8스레드 공유 | `bound to a different event loop` |

### 인프라 변경

- `runtime_llm.py`를 pydantic-ai OpenRouter 모델 위로 이전. `finish_reason` 보존,
  `truncated`/`empty` 명시, malformed tool args 표면화, 비용·reasoning 토큰 수집,
  스레드별 클라이언트.
- `verify_paper_contract.py`, `scripts/check_combined_smoke.py` 게이트 신설. distiller 공백,
  큐레이터 무작동, 빈 스토어, 메모리 미전달, 답 미제출을 잡고 비정상 종료.
- PG: 라운드별 그래프 체크포인트(`evolved_graph.json`), `update_edges` 편집 연산,
  stride 반복 진화, 문항 단위 병렬(`--workers`).
- 테스트 55개 → **116개**.

## 5. 한계

**단일 run.** 논문은 GPT-5.4 / Claude Sonnet 4.6급으로 다섯 paired run을 보고한다.
이 결과는 각 조건 1 run이므로 exact replication이 아니라 독립 재현이다.

**모델 편차.** 논문의 네 모델(Claude Sonnet 4.6, Gemini 3.1 Pro, Gemini 3.5 Flash,
Grok 4.1 Fast) 중 어느 것도 쓰지 않았다. deepseek-v4.1-flash는 CLBench 베이스라인이
논문(39%)과 근접한 37.5%로 나와 대조군으로 적절했으나, MultiChallenge PG 수치
(논문 89.76% vs 우리 62.5%)의 격차 상당 부분은 모델 급 차이로 보인다.

**그래프 체크포인트 미공개.** 논문은 graph checkpoint를 공개하지 않는다. expert 그래프는
Table 7의 크기(7노드 7 triplet)에 맞춘 자체 제작이며 논문 것이 아니다.

**파싱 실패의 집계 차이.** 논문은 형식 실패를 성공률에 포함한다. 우리 어댑터는 재프롬프트로
복구하므로 56문항 중 형식 문제로 답을 못 낸 것은 1건뿐이다. PG의 형식 안정화 이득이 점수로
환산되는 경로가 구조적으로 막혀 있다.

**APEX 미재현.** task ordering과 adapter artifact가 비공개다.

## 6. Artifact

- 결합 factorial: `combined-paper/factorial-v2/clbench_latest.json`, `factorial_audit.{json,md}`
- Grounding 3조건: `paper-contract/run-0-{no_memory,trajectory_memory,environment_probing_memory}.json`
- PG (deepseek, `q` 수정 후): `pg-paper/react-deepseek-v2/`
- PG (deepseek, 수정 전): `pg-paper/react-deepseek/`
- PG (gemini): `pg-paper/react-full/`
- 게이트: `src/procedural_graphs/verify_paper_contract.py`, `scripts/check_combined_smoke.py`
- 정답 누출 감사: `scripts/audit_answer_leak.py`

## 7. 정답 누출 감사

Semantic-only의 62.5%가 정답 누출로 폐기된 2026-09-13 run과 같은 값이라 전 레코드를 검사했다.
27개 중 2개가 ground-truth 값을 포함했으나 **둘 다 절차 규칙이고 숫자는 근거로 붙어 있으며,
해당 레코드를 보유한 조건이 그 문항에서 오답을 냈다**(Q20에서 레코드가 "틀렸다"고 명시한 3783을,
Q31에서 "틀렸다"고 적힌 66.3을 답했다). 정답 캐시로 기능했다면 정반대여야 한다. 따라서 62.5%는
답 누출로 설명되지 않는다. 다만 논문 프롬프트가 금지한 "incidental values" 저장은 record
contract 위반이므로 한계로 기록한다.

## 현재 판정

이 절도 작성 당시의 판정을 보존한다. 결합 부분의 최신 해석은 상단 정정과 [[메모리-연구/procedural-graphs/docs/COMBINED_DESIGN|버그 수정 후 재설계]]를 우선한다. 다음 실험에서 필요한 것은 더 강한 결론 문구가 아니라, 수정된 구현으로 같은 조건을 반복하고 정확도와 총 호출 비용을 함께 비교하는 일이다.

**Grounded semantic memory: 재현 성공.** 효과 크기(+32.5%p)와 방향이 논문과 일치하며 40문항
단일 run에서 유의하다(`p=0.0044`). Environment probing의 추가 이득과 drift 이후 우위도 관측됐다.

**Procedural Graph: 메커니즘 재현 성공, 정확도 기여 미입증.** 진화(2→7노드), 게이트 채택·거절,
구조 검증, rejection 기록, 파싱 안정화가 모두 관측됐으나 test 정확도 개선은 두 모델 모두에서
비유의하다.

**결합 가설: 기각.** PG 효과가 semantic memory 유무와 정확히 동일하고 interaction이 −0.0%p다.
두 구성요소는 독립적으로 작동하며 상보성의 증거가 없다.
