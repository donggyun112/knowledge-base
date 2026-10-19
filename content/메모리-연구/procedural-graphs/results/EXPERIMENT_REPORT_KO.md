---
title: "Grounded Semantic Memory × Procedural Graph 재현 보고서"
tags:
  - memory-research
  - research-archive
---

> [!info] 개정판 (2026-10-19)
> 원 저장소 [procedural-graphs-lab](https://github.com/donggyun112/procedural-graphs-lab)의 `results/EXPERIMENT_REPORT_KO.md`(작성 2026-09-19, 수집 커밋 `2c265f7`)를 바탕으로 한다. §1의 결합 2×2는 수정된 solver(`multiturn-v1`)로 다시 측정한 결과로 **새로 썼다**. §2~§7은 2026-09-19 본문을 그대로 보존한 것이며 다시 측정하지 않았다. 옛 2×2는 부록 A로 내렸다. 새 실행 결과 폴더는 원 저장소에서 미추적 상태이고 코드·원시 로그는 이 사이트에 포함하지 않았다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽는다.

# Grounded Semantic Memory × Procedural Graph 재현 보고서

이 보고서가 풀려던 문제는 두 가지다. 첫째, 과거 기록을 저장하는 것만으로 충분한가, 아니면 현재 환경을 다시 확인해야 유용한 기억이 되는가? 둘째, 그렇게 만든 기억에 작업 순서 안내까지 더하면 더 잘 풀리는가? 이를 분리하려고 메모리 3조건, 메모리와 PG의 2×2 비교, PG 자체의 학습 실험을 따로 실행했다.

서로 다른 러너와 solver의 점수를 한 표처럼 비교하지 않는다. §1은 2026-10-19에 `multiturn-v1` solver로 새로 측정했고, §2~§4의 수치는 그 이전 구현에서 나온 값이다.

## 결론 요약

1. **semantic memory 효과는 이 설정에서도 크다.** 새 2×2에서 stateless 30.8% → memory 62.5%(+31.7pt)다. PG가 있을 때도 +29.2pt다.
2. **PG가 정확도를 올린다는 근거는 없다.** memory 위에 PG를 얹으면 62.5% → 56.7%(−5.8pt)였고 유의하지 않다(Welch t=−1.49, 조건당 3회). 같은 비교에서 부호가 실행 묶음마다 달라진다(§1.2).
3. **PG의 일관된 효과는 SQL 호출 수 감소다.** memory 6.62회 → memory+PG 4.91회(−26%)이고 score는 거의 같다(0.349 vs 0.359). 세 묶음 모두에서 같은 방향이다.
4. **결합 효과(interaction)는 −2.5pt로 0에 가깝다.** 결합이 두 효과의 합보다 낫다는 증거는 없고, 그렇다는 반증도 아니다. stream 1개, 조건당 3회, 손으로 쓴 그래프라는 한계가 있다.
5. **결합모델의 이득은 입증되지 않았다.** 이 설정에서 관측된 것은 정확도 불변에 가까운 질의 절감뿐이다.
6. 이어받기(checkpoint resume)로 돌린 실행은 편향됐다. 같은 설정의 memory-only가 이어받기에서는 77.5%, 처음부터 돌리면 62.5%였다. 비교에는 처음부터 돌린 실행만 쓴다.

## 1. 결합 2×2 (CLBench `database_exploration/schema_drift`, stream 1, 40문항)

이 비교는 '메모리를 이미 가진 에이전트에도 PG가 보탬이 되는가'를 묻는다. 위아래 행은 기억 유무, 좌우 열은 PG 유무다. 한 행에서 좌우를 빼면 PG 효과가 나오고, 그 효과가 두 행에서 얼마나 다른지가 interaction이다.

설정: 모델 `deepseek/deepseek-v4-flash-0731`, solver reasoning `medium`, agent `multiturn-v1`(문항당 하나의 tool-use 대화), recall `required`, retriever `e5`, 그래프는 손으로 쓴 그래프(메모리가 있는 조건은 `Start`, `database_query`, `database_answer`, `memory_read` 4노드, 없는 조건은 `memory_read` 제외, `generations=0`, 진화 없음). 조건당 3회, 모두 처음부터 실행했다. 총 12 pass다.

### 1.1 결과

| | 정확도 (3회) | 평균 | 평균 SQL | score |
|---|---|---:|---:|---:|
| stateless | 32.5 / 30.0 / 30.0 | 30.8% | 10.60 | 0.092 |
| PG only | 30.0 / 27.5 / 25.0 | 27.5% | 8.60 | 0.131 |
| memory | 65.0 / 62.5 / 60.0 | 62.5% | 6.62 | 0.349 |
| memory + PG | 50.0 / 57.5 / 62.5 | 56.7% | 4.91 | 0.359 |

| 효과 | PG 없음 / 메모리 없음 | PG 있음 / 메모리 있음 |
|---|---:|---:|
| semantic memory | +31.7pt | +29.2pt |
| PG | −3.3pt | −5.8pt |

interaction은 약 −2.5pt다. 네 칸의 정확도 표준편차는 1.4~6.3pt이고, memory와 memory+PG의 차이는 Welch t=−1.49로 유의하지 않다. 문항 단위의 paired 검정은 하지 않았다. 문항이 같아도 실행 사이에 답이 달라지는 flaky 문항이 많아 3회 평균만으로 읽는다.

- **PG 조건의 활성 노드.** 새 memory+PG 3회에서 `database_query`, `Start`, `database_answer`, `memory_read`가 활성화됐다. 이 그래프는 STATUS 노드를 추가하지 않은 4노드 그래프이므로, 과거에 문제였던 'STATUS 노드가 활성 노드가 되지 못함'과는 무관하다.
- **비용.** 이 12 pass의 보고된 API 비용은 합쳐 약 $5.1이다. 이어받기로 돌려 폐기한 실행과 smoke test까지 포함한 전체 지출은 약 $8이다.

### 1.2 다른 묶음과의 교차 확인

| 묶음 | 모델 | memory | memory + PG | 차이 | SQL 변화 |
|---|---|---:|---:|---:|---:|
| 위 §1.1 (stream 1, 처음부터) | `v4-flash-0731` | 62.5% | 56.7% | −5.8pt | 6.62 → 4.91 (−26%) |
| 반복 실행 (stream 1) | `v4.1-flash` | 77.5% | 79.2% | +1.7pt | 7.26 → 5.53 (−24%) |
| 반복 실행 (stream 2) | `v4.1-flash` | 70.0% | 77.5% | +7.5pt | 6.66 → 5.60 (−16%) |

정확도 차이는 −5.8, +1.7, +7.5pt로 부호가 갈리고 어느 것도 유의 검정을 하지 않았다. SQL 절감은 세 묶음에서 −16%~−26%로 같은 방향이다. 마지막 두 줄은 [[메모리-연구/procedural-graphs/results/POKER_AND_EVOLVE_2026-10|후속 실행 정리]]의 재집계 값이다. 모델이 다르므로 한 표처럼 합산하지 않는다.

### 1.3 이어받기 실행이 결과를 바꿨다

처음 시도에서는 중단된 실행의 체크포인트에서 이어받아 memory와 memory+PG를 돌렸다. 같은 설정을 처음부터 다시 돌리자 값이 크게 달랐다.

| 조건 | 이어받기 (3회) | 처음부터 (3회) |
|---|---|---|
| memory | 80.0 / 80.0 / 72.5 = 77.5% | 65.0 / 62.5 / 60.0 = 62.5% |
| memory + PG | 17.5 / 62.5 / 80.0 = 53.3% | 50.0 / 57.5 / 62.5 = 56.7% |

- 같은 설정에서 memory가 15pt 벌어졌다. 이어받은 앞 문항이 어떤 코드·메모리로 만들어졌는지 알 수 없으므로 이어받기 값은 비교에 쓰지 않는다.
- 이어받기 memory+PG의 17.5% 실행은 처음부터 돌린 3회에서 재현되지 않았다(최저 50.0%).

### 1.4 메모리 오염 사례 (이어받기 실행 로그 추적)

17.5% 실행의 로그를 문항 순서대로 추적했다. 이 실행은 이어받기라 원인을 확정하지 못하지만, 메모리가 오답을 늘릴 수 있는 경로가 로그로 확인된다.

- Q1에서 메모리가 비어 있는 상태로 오답(`Pyle`, 정답 Fender)을 냈다.
- 직후 큐레이터가 "세 데이터셋에 걸친 질문은 반드시 모두 합산해야 한다"는 규칙을 high confidence로 저장했다. 문항 하나에서 얻은 과잉 일반화다.
- 이 레코드가 Q2~Q4에서 계속 recall됐고, Q3·Q4는 오답이었다. 이후 Q20까지 17문항이 틀렸고, 그 사이 "그 휴리스틱은 사무용품 질문에는 적용되지 않는다"는 사후 보정 레코드가 생겼다.
- 같은 문항을 맞힌 실행은 올바른 레코드(브랜드는 `attrs_g3` 계열 테이블에 있음)를 먼저 쌓았고 80%에 도달했다.

해석할 수 있는 범위는 '첫 몇 문항에서 어떤 레코드가 먼저 쌓이느냐가 이후 궤적을 좌우하는 경로 의존성이 있다'까지다. 이것이 PG 조건에서 더 잘 일어난다고는 말할 수 없다. 반사실 실험(해당 레코드를 지우고 이어 돌리기)은 하지 않았다.

### 1.5 이 절의 한계

- stream 1개, 조건당 3회다. stream 2는 이 모델로 돌리지 않았다.
- 그래프는 손으로 쓴 것이다. 학습·진화로 만든 그래프에 대한 결론이 아니다.
- 모델은 가변 alias가 아니라 `deepseek-v4-flash-0731`로 고정했지만 solver·guidance·curator가 모두 같은 모델이다.
- 기존 §2~§7의 수치와 직접 비교하지 않는다.

## 이 문서의 나머지 절에 대하여

아래 §2~§7은 2026-09-19 본문을 그대로 보존한다. §2의 3조건 러너는 `multiturn-v1`이 아니라 그 이전 구현으로 측정했고, §3의 MultiChallenge도 다시 돌리지 않았다. CLBench에서 solver 구현을 고치자 memory-only가 42.5%에서 77.5%로 올랐다는 점은, 그 이전 구현으로 얻은 절대 수치를 그대로 믿으면 안 된다는 뜻이다. 순서·방향 같은 상대적 관찰은 참고하되 수치는 역사적 기록으로 읽는다.

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

## 현재 판정 (2026-10-19)

**Grounded semantic memory: 효과 있음.** 수정된 solver와 다른 모델에서도 +30pt 안팎으로 안정적이다(§1.1). 단 §2의 `p=0.0044`와 논문 대비 비교는 옛 구현의 값이라 이 판정의 근거로 쓰지 않는다.

**Procedural Graph: 정확도 이득 미관측, SQL 절감은 일관됨.** §1.2의 세 묶음 모두 질의가 16~26% 줄었고, 정확도 차이는 −5.8, +1.7, +7.5pt로 부호가 갈렸으며 유의하지 않다. MultiChallenge(§3)에서도 test 정확도 개선은 비유의했다.

**결합 가설: 입증되지 않음.** 옛 보고서의 '기각'이나 이후의 '입증'이 아니라, 이 설정(stream 1개, 조건당 3회, 손으로 쓴 그래프)에서 결합이 단독 효과의 합을 넘는다는 증거가 없다는 뜻이다. 판정을 바꾸려면 아래가 필요하다.

- stream 2 이상에서 같은 2×2를 처음부터 반복한다.
- 학습·진화로 만든 그래프로 같은 비교를 한다.
- 정확도와 SQL·LLM 호출 비용을 함께 보고한다.
- 메모리 경로 의존성(§1.4)이 PG 조건에서 더 큰지 반사실 실험으로 확인한다.

## 새 실행 Artifact (원 저장소 `results/`, 미추적)

- 처음부터 실행한 2×2 칸: `e0731-stateless-idx1-{a,b,c}`, `e0731-pgonly-idx1-{a,b,c}`, `e0731f-memonly-idx1-{a,b,c}`, `e0731f-guided-idx1-{a,b,c}`
- 비교에서 제외한 이어받기 실행: `e0731-memonly-idx1-{a,b,c}`, `e0731-guided-idx1-{a,b,c}`
- 실행 진입점: `procedural_graphs.clbench_evolve_live`, 옵션 `--generations 0 --test-index 1 --val-index 1 --solver-reasoning medium --model deepseek/deepseek-v4-flash-0731`

## 부록 A. 옛 결합 2×2 (2026-09-19, 폐기)

아래는 개정 전 §1이다. 큐레이터 `max_tokens=450` 잘림 버그가 있던 시점의 값이고, 그 뒤 solver 구현도 바뀌었다. 같은 버그를 고친 뒤 [[메모리-연구/procedural-graphs/docs/COMBINED_DESIGN|COMBINED_DESIGN]]은 memory 있음 행을 60.0% / 62.5%로 재측정했고 옛 2×2는 폐기했다고 적는다. 보존용이며 결론에 인용하지 않는다. 당시의 판정 "결합 가설 기각"과 "Grounded semantic memory 재현 성공(`p=0.0044`)"도 같은 이유로 최종 결론이 아니다.

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
