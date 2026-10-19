---
title: "재현 및 결합 후기"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/procedural-graphs-lab) · 원본 `REVIEW.md` · 수집 2026-10-16 · 커밋 `2c265f7fb194627f1b39d90207e9dca03b6cee28`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# 재현 및 결합 후기

작성일: 2026-09-14
대상: [Grounding Agent Memory](https://arxiv.org/html/2609.11060) + [Procedural Graphs](https://arxiv.org/html/2609.09153v1)

## 결론

이 후기는 결과가 좋아졌다는 이야기보다 **비교를 믿을 수 있게 만드는 과정**에 가깝다. 처음에는 PG 쪽에만 정답에 가까운 안내가 들어갔고, 다음에는 두 조건이 서로 다른 기억을 학습했으며, 이후에는 큐레이터 응답이 잘리는 버그가 결합 조건에 더 큰 손해를 주었다. 같은 ‘메모리 + PG’라는 이름 아래에서도 무엇을 고정했는지에 따라 전혀 다른 질문을 측정한 셈이다.

그래서 아래 표는 시간순 관측으로 읽는다. 2026-09-22 정정이 철회한 것은 ‘PG가 기억을 방해한다’는 원인 해석이다. 원래 실행에서 낮은 점수가 나왔다는 사실까지 지운 것은 아니다. 수정 후에는 60.0% 대 62.5%로 방향이 바뀌었지만, 차이가 1문항이어서 결합의 우위는 여전히 미입증이다.

현재 레포는 두 논문의 **방법 수준 메커니즘**을 각각 구현하고, semantic memory와 PG를 독립된
branch로 resolve하는 결합 구조를 실제 OpenRouter LLM으로 끝까지 실행한다. Grounding 논문이 쓴
공식 CLBench 40-question schema-drift task도 같은 runner/evaluator로 실행했다. 다만 비공개 GHCP
harness, GPT-5.4 xhigh, five paired runs를 복원한 exact reproduction은 아니다.

초기 실험의 `grounded semantic only 0/12`와 합성 실험의 `12.8%`는 폐기해야 한다. 전자는
semantic 조건에는 현재 상태와 절차를 숨긴 반면 PG 조건에는 사실상 정답 next action을 Python이
제공한 비대칭 비교였고, 후자는 LLM조차 쓰지 않은 seeded simulator 값이었다. 둘 다 semantic
memory의 유효성을 판정하지 못한다.

## semantic memory를 어떻게 만들었나

왜 기억을 쓰는 역할을 따로 둘까? 작업을 푸는 도중의 추측을 곧바로 장기 기억에 넣으면, 다음 작업도 같은 오류를 물려받을 수 있기 때문이다. 여기서는 작업이 끝난 뒤 Distiller가 실행 기록에서 근거를 추리고, Curator가 피드백과 필요할 경우 현재 환경을 확인한 뒤 저장·수정·삭제를 결정한다. 다음 작업의 에이전트는 완성된 기억을 읽기만 한다.

~~~text
completed raw trajectory
        ↓
non-writing Distiller LLM
  - grade를 보지 않음
  - memory/environment tool이 없음
        ↓ distilled evidence
Curator LLM + terminal feedback + nearby records
        ↔ optional read-only environment probes
        ↓ exclusive create/update/delete/skip
persistent scoped records
  category · confidence · applies_to · lemma · provenance
        ↓
next fresh task agent: memory_read only
~~~

Probing 조건에서는 Curator만 uncertain correctness, scope, freshness, counterexample,
precondition을 확인한다. 미리 만든 cue-to-answer dictionary는 사용하지 않는다. task-time agent는
memory write 권한이 없고, 다음 task에서 recall을 할지와 recalled fact를 어떻게 사용할지는
solver가 결정한다.

## PG와 결합 구조

PG는 현재 procedure를 locate하고 outgoing 2-hop subgraph를 뽑는다. 별도 Guidance LLM은 query,
최근 3-step trajectory, attributed edges만 읽어 soft guidance를 만든다. Semantic record는 이
Guidance LLM에 전달하지 않는다. Deterministic resolver가 stage-scoped facts와 PG advice를 합친 뒤
Solver가 full compact trajectory와 함께 한 action을 고른다. Python은 next action을 강제하지 않는다.

task가 끝나면 같은 trajectory가 두 갈래로 사용된다.

- Distiller와 Curator는 재사용할 semantic record를 갱신한다.
- PG Refiner는 scored traces, current graph, tool catalog, rejection memory에서 graph edit를
  제안한다.

Refiner의 edit는 graph 복사본에 delete-then-add로 적용되고 endpoint, cycle,
terminal-reachability 검사를 거친다. 독립 validation score가 기존보다 낮지 않을 때만 commit하고,
실패한 proposal은 rejection memory에 보존한다.

## 공식 CLBench adapter 검증

`~deepseek/deepseek-v4-flash-latest`, temperature 0, reasoning disabled로 공식 40문항과 두 SQLite
snapshot, migration boundary, 15-query budget, upstream evaluator를 사용했다. Provider가 named
`tool_choice`를 간헐적으로 무시했기 때문에 모든 memory 조건은 solver 전에 원 질문으로 정확히
한 번 recall하는 동일한 adapter protocol로 다시 실행했다.

| 조건 | pass | total reward | SQL/question | pre/post | reads |
|---|---:|---:|---:|---:|---:|
| stateless | 30.0% | 3.8667 | 11.750 | 35% / 25% | 0 |
| trajectory memory | 17.5% | 1.7333 | 13.375 | 15% / 20% | 40 |
| grounded memory | 62.5% | 14.2668 | 7.200 | 65% / 60% | 40 |
| fixed PG only | 22.5% | 3.2667 | 9.775 | 20% / 25% | 0 |
| fixed PG + grounded memory | 37.5% | 7.0667 | 8.225 | 35% / 40% | 40 |

Grounded와 combined의 paired 결과는 both 12, combined-only 3, grounded-only 13, neither 12다.
결합은 grounded-only보다 10개 net pass가 적고 평균 SQL도 1.025회 많았다. Grounded의 exact
duplicate SQL은 14회였지만 combined는 20회였다. 따라서 이 한 run에서 fixed PG 결합은 시너지가
아니라 guidance interference로 관찰됐다.

> **2026-09-22 정정.** 이 "guidance interference" 해석은 **철회한다.** 당시
> `grounded_curation.curate()`가 큐레이터를 `max_tokens=450`으로 호출했고, 응답이 잘리면
> tool_call 없는 응답이 되어 루프가 "의도적 종료"로 읽고 아무것도 커밋하지 않았다. 궤적이
> 긴 PG arm이 더 자주 잘렸으므로 위 표의 −25%p는 결합 구조가 아니라 버그를 잰 것이다.
> 수정 후 40문항 재측정(`results/combined-paper/factorial-v3/`)에서는 `grounded_memory`
> 60.0% vs `pg_frozen_grounded_memory` 62.5%로 부호가 뒤집힌다. 다만 +2.5%p는 1문항이라
> 단일 스트림으로는 유의하다고 말할 수 없다. 자세한 것은
> [[메모리-연구/procedural-graphs/docs/COMBINED_DESIGN|COMBINED_DESIGN §1]].

Grounded가 trajectory memory보다 18개 net pass를 더 얻은 것은 환경 probing 경로가 실제로
다르게 작동했다는 강한 신호다. 그러나 curator가 "instance answer를 저장하지 말라"는 prompt를
어기고 일부 record에 과거 문제의 구체적 count, 평균, 정답값을 남겼다. 사전 정답 주입은 아니지만
순수한 schema/procedure generalization과 answer caching이 섞였으므로 일반적 성능 증명은 아니다.
원 수치와 폐기 run 감사 기록은 CLBench report (`results/clbench_summary.md`; 원 저장소의 파일 참조)에 있다.

### sibling 구조 재실행

두 종류의 기억을 나란히 전달하는 sibling 구조를 시험했다. 그런데 이때는 두 조건이 각자 자기 실행 기록으로 메모리를 만들었다. 따라서 결과 차이에 PG의 조언뿐 아니라 ‘처음에 어떤 규칙을 배웠는가’의 차이도 함께 들어간다. 아래 오류 분석은 이후 동일 메모리 스냅샷을 재생하는 비교가 왜 필요했는지를 보여준다.

수정한 `dual_memory`와 현재 코드의 `grounded_memory`를 같은 40문항에 paired 실행했다.

| 조건 | pass | total reward | SQL/question | pre/post |
|---|---:|---:|---:|---:|
| grounded semantic memory | 37.5% | 7.267 | 9.375 | 30% / 45% |
| sibling dual memory | 32.5% | 7.267 | 8.925 | 25% / 40% |

Dual은 SQL을 18회 줄였지만 정확도는 2문항 낮았다. 둘 다 성공 8, grounded-only 7,
dual-only 5, 둘 다 실패 20이었다. 가장 큰 원인은 dual의 초기 Curator가 `items_g2` 전체가
electronics라는 benchmark mapping을 놓치고, `main_cat` 하위 목록을 반드시 필터하라는 반대
rule을 high-confidence memory로 저장한 것이다. 존재 여부만 확인한 probe를 의미 검증으로
오판했고, 이 record가 52회 읽혀 최소 5개의 퇴행에 관여했다. 반면 grounded condition의 독립
store는 같은 초기 provenance에서 정반대의 올바른 rule을 만들었다. 따라서 이 한 run은 PG의
순수 causal effect를 격리하지 못한다. 자세한 분석은
sibling CLBench report (`results/clbench_dual_summary.md`; 원 저장소의 파일 참조)에 있다.

## 작은 로컬 6조건 실행

`~deepseek/deepseek-v4-flash-latest`, temperature 0, reasoning disabled로 실행했다. memory 조건은
4개 train task를 순차 실행하며 매 task 뒤 실제 distillation과 curation을 수행했고, 그 뒤 4개
test task에서 store를 고정했다.

| 조건 | test 성공 | 평균 environment tools | memory reads | 최종 records |
|---|---:|---:|---:|---:|
| stateless ReAct | 4/4 | 7.00 | 0 | 0 |
| trajectory-only memory | 2/4 | 5.75 | 4 | 7 |
| environment-probed memory | 3/4 | 8.25 | 0 | 4 |
| PG only | 4/4 | 4.25 | 0 | 0 |
| PG + trajectory-only memory | 4/4 | 4.00 | 4 | 4 |
| PG + environment-probed memory | 4/4 | 4.25 | 4 | 1 |

API 보고 비용은 $0.016742였다. 원본 JSON에는 raw trajectory, distilled packet, curator의 probe와
CRUD, final records, task-time recall, token/cost가 모두 남아 있다.

이 결과로 grounded memory나 결합의 우위를 주장할 수 없다. stateless부터 4/4라 accuracy
ceiling이 있고, grounded-memory-only solver는 test 중 `memory_read`를 한 번도 호출하지 않았다.
따라서 그 3/4는 저장된 memory 품질의 효과를 측정한 수치가 아니다. 두 combined 조건은 모두
4/4였고 grounded 결합의 tool 효율도 더 좋지 않았다.

## 실제 self-evolution 1회

이 실험의 목표는 정확도 향상을 주장하기 전에, ‘경험 수집 → 그래프 수정 제안 → 검증 → 채택’이라는 전체 고리가 실제로 도는지 확인하는 것이었다. validation이 처음부터 4/4이므로 더 높은 정확도를 낼 여지가 없고, 동률도 채택하는 규칙이라는 점을 먼저 기억해야 한다.

minimal PG와 grounded memory로 training traces를 만든 후, 별도 Refiner LLM과 validation gate를
실행했다.

- initial validation: 4/4, 평균 environment tools 4.50
- proposal: procedure node 4개와 transition 9개 추가, premature transition 3개 삭제
- structural validation: 통과
- candidate validation: 4/4, 평균 environment tools 4.25
- gate: 논문의 non-decrease 규칙에 따라 동률 candidate commit
- retained graph unseen test: 4/4, 평균 environment tools 4.25
- API 보고 비용: $0.009640

폐루프의 실제 실행은 확인했지만 정확도 향상은 없었다. 4.50에서 4.25로 tool 수가 줄었어도 gate
metric은 binary success였으므로 이 효율 개선이 commit 원인은 아니다.

## 현재 재현 수준

달성한 것은 role separation, information boundary, curation/probing/CRUD, PG localization과
guidance, solver 실행, mutation, structural validation, validation gating, rejection memory를 한
시스템에서 작동시킨 것이다.

CLBench 공식 task를 사용한 independent adapter run까지는 완료했다. 남은 핵심은 논문의 비공개
GHCP harness, 동일 GPT-5.4 설정, five paired runs와 신뢰구간, APEX 및 PG 논문의 원 benchmark와
split을 사용한 exact reproduction이다. PG self-evolution도 CLBench test stream에서 직접 수행하지
않았다. 별도 train/validation/test split 없이 test 문항으로 graph를 고치는 것은 leakage이기
때문이다.

실행 원본은 official CLBench report (`results/clbench_summary.md`; 원 저장소의 파일 참조),
로컬 6조건 결과 (`results/faithful_latest.json`; 원 저장소의 파일 참조), self-evolution 결과 (`results/evolution_live.json`; 원 저장소의 파일 참조), 상세 매핑은
[[메모리-연구/procedural-graphs/docs/REPRODUCTION_SPEC|재현 명세]]에 있다.
