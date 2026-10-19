---
title: "What we believe, and what measured it"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `board/claims.md` · 수집 2026-10-16 · 커밋 `fd190b18f8e4113d7f451a7108911c1f89716b24`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# What we believe, and what measured it

여기에는 논리만 그럴듯한 주장을 넣지 않는다. 각 항목은 어떤 실험이 근거인지 밝히고, 뒤집힌 주장은 아래 `Overturned`로 옮겨 뒤집은 원인도 남긴다. 특히 ‘유사도가 무작위보다 못하다’는 결과는 최근 맥락이 이미 있는 에이전트에 과거 행동을 추가한 조건에서 읽어야 한다. 아래 HotpotQA 대조처럼 과제 구조가 달라지면 방향도 달라진다.

## Standing

**Selecting memory by similarity is worse than selecting at random.**
Five measurements, two endpoints. On next-action likelihood: +0.1460 for random
over similarity in BGE space, +0.1693 in Qwen hidden-state space, +0.1808 with
the shared direction removed. On pytest-verified repairs at a 9-turn budget:
similarity costs 0.464 actions against random, resolved [-0.929, -0.036].
*(neural-memory/RESULTS.md, phases 73-76 and the budget-9 run)*

> Read the repair half narrowly. Phase 84 established that on these tasks the
> budget is consumed by orienting in an unfamiliar repository — median six of
> nine actions before the first edit — not by locating the defect, which the
> failing test name gives away on 87% of them. The ordering between conditions
> holds, since they ran on identical tasks. What it is an ordering *of* is which
> notes shorten orientation, which is a smaller thing than it reads as.
> *(phases 82, 84)*

**표현의 약함보다 내용 중복이 원인이라는 해석이다.** 현재 상황을 더 잘 표현할수록 가장 가까운 저장 항목은 프롬프트에 이미 있는 내용을 반복한다. 이 설명은 Qwen 공간 실험 전에 결과 방향을 예측했다. 따라서 유사도 검색 전반의 무용함이 아니라, 추가한 기록이 현재 맥락에 무엇을 더하는지의 문제다. *(phase 75)*

**Memory as an untrained bias on the residual stream does nothing, and not
because of the encoder.** Own-trajectory and foreign-trajectory vectors are
indistinguishable at every scale and readout (mean, associative, sparse) — and
also when the vector is a *gradient*, in the model's own coordinates by
construction, which is what phase 77's diagnosis predicted would fix it.
*(phases 77, 83)*

**이득처럼 보인 것은 저장 방향들의 공통 평균 성분이었다.** 그 성분을 빼기 전에는 자기 궤적과 다른 궤적 모두 무기억보다 약 0.09 NLL 좋았지만, 제거한 뒤에는 같은 주입이 해로웠다. 평균 쌍별 코사인 0.1651만으로 전체 효과가 설명되었다. 벡터들이 좁은 원뿔에 몰리지 않았다는 이유로 공통 성분 대조를 생략할 수 없다. *(phase 83)*

**A familiarity filter does not predict where the model will do badly.** 0.4498
AUC against the model's own output entropy at 0.8179 — it loses by 0.368 and does
not separate from chance. *(phase 79)*

**Mushroom body compartment valence is readable from raw anatomy.** Counting PAM
against PPL1 presynapses per compartment recovers the textbook split with nothing
fitted: b'2 at +1.000 on 12659:1, a3 at -1.000 on 0:2424.
*(fly-connectome/compartment_valence.py)*

**That wiring is not organised for storage capacity.** Against a curveball
rewiring holding every degree fixed it earns nothing (three loads, none
resolved), and a uniform shuffle of the same synapses beats it by up to 0.089.
Matches the literature: random expansion maximises capacity, and the fly pays
capacity for selectivity. *(fly-connectome phases 38-39)*

**Flat semantic retrieval on a small, topically-related candidate set beats a
random baseline; on a by-design-dissimilar target it loses to one.** Closed-form
random baselines computed against keymem's own fixtures (no rerun): HotpotQA
bridge (N=10, 2 gold, top-5) puts chance at both@5 22.2% / support-recall@5
50%, and DIRECT clears both by a wide margin (53-60%, 72-78%). The 14-memory
assoc2 fixture puts chance at reach@10 71.4%, and DIRECT (50%) and BM25 (33%)
both score below it — the fixture's queries are built to have low direct
similarity to the target, so cosine actively anti-ranks it rather than merely
failing to help. Confirms the standing "similarity worse than random" claim
does not generalize from one domain to the other on the strength of the domain
alone — it depends on whether similarity carries real signal for the target,
which HotpotQA support paragraphs have and injected-trajectory duplicates do
not. *(keymem/BENCHMARKS.md §1, §2; board/open.md, answered 2026-09-19)*

**Resemblance-based memory signals reduce to the model's own output distribution.**
Three mechanisms, same answer: similarity over stored actions (worse than random,
five measurements), familiarity over hidden states (0.4498 AUC against entropy's
0.8179), and mushroom-body valence (r = -0.5310 with entropy; 0.5517 against its
0.7968). Against *real* trajectory outcomes rather than next-action likelihood,
all of them including entropy sit at chance. — *keymem-20, 2026-09-19*

**현재 말뭉치 크기로 판별할 수 없는 질문도 있다.** 공통 성분 제거 뒤 자기 궤적의 우위는 독립 궤적 997개에서 +0.0210 [-0.0005, +0.0427]이었다. 997개는 확보 가능한 최대치인데, 구간이 0과 사전 기준 0.02를 모두 포함한다. 250개에서 표본을 네 배로 늘리자 추정값은 절반으로 줄어, 원 기록은 안정된 효과보다 잡음을 의심했다. 판별에는 1,500-2,500개 궤적이 필요하다. 같은 자료로 더 오래 실행할 문제가 아니다. *(phase 85)*

## Overturned

**“실제 배선이 연결 수 보존 재배선을 이긴다”(+0.0495, resolved)는 철회되었다.** 재배선 코드가 충돌을 합치며 30,543개 중 5,255개 시냅스를 잃었다. 실제로 이긴 상대는 연결 수가 같은 회로가 아니라 더 성긴 행렬이었다. 정확한 curveball 교환으로 고치면 차이는 -0.0023이며 구별되지 않는다. *(phase 38)*

**“빡빡한 예산에서 메모리가 성공을 5/15에서 13/15로 올린다”는 철회되었다.** 에이전트가 실행자의 MCP 서버를 물려받아 턴을 도구 탐색에 쓰고 있었고, 구체적 Bash 명령 노트가 그 탐색을 건너뛰게 했다. `--safe-mode`로 통제하면 효과는 사라졌다. 기억의 작업 개선과 실행 환경 탐색의 우회를 혼동한 사례다. *(phase 78)*
