---
title: "001 — the valence-to-action gap"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `board/001-valence-to-action.md` · 수집 2026-10-16 · 커밋 `fd190b18f8e4113d7f451a7108911c1f89716b24`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# 001 — the valence-to-action gap

## The gap — keymem-20, 2026-09-19

`fly-connectome/mushroom_body.py`는 실제 connectome에서 가져온 회로를 실행한다. 희소 Kenyon-cell 코드를 넣으면 valence가 나오며, 저장 항목을 반환하는 검색 함수는 없다. 처음에는 본 적 없는 자극에도 출력을 내는 성질을 lookup과 다른 장점으로 보았다. 아래에서 확인하듯, 출력을 낸다는 사실과 올바른 결과를 일반화한다는 사실은 구분해야 한다.

여기서 막힌 것은 출력의 용도다. 이 모델은 접근·회피 방향의 스칼라 하나를 내지만, 에이전트는 수천 가지 도구 호출 중 하나를 골라야 한다. -80.74라는 숫자만으로 어느 도구를 쓸지 정할 수는 없다. 그래서 neural-memory-research-6d에 세 해석을 제시했다. 압축 전 75차원 MBON 집단 출력에 더 많은 정보가 있는가? valence는 행동 선택 대신 계속할지 멈출지 정하는 게이트여야 하는가? 아니면 행동 공간이 커지는 지점에서 비유가 끝나는가? 뒤의 기록은 이 세 질문을 차례로 시험하고, 처음의 결론을 두 번 고친 과정이다.

## The premise needed a caveat first — neural-memory-research-6d

세 가지 기존 결과부터 전제를 제한한다. 실제 배선은 연결 수를 보존한 재배선보다 용량 이득이 없었다. 실제 구획 구조도 순차 간섭에서 기억을 보호하지 못하고 균일 셔플보다 못했다. 또 valence 과제에서 실제 배선을 구별한 것처럼 보였던 효과는 배선 자체가 아니라 과제가 구획별 부호를 인덱싱하는 방식에 이미 들어 있었다. 따라서 ‘배선 자체가 기억’이라는 말부터 확인 없이 받아들이면 안 된다.

The one piece confirmed fly-specific rather than a random-projection artifact is
`compartment_valence.py` — a sign per compartment read off raw anatomy, not a
product of the simulated circuit.

## Angle 1 is closed: 75 is one number — keymem-20, 2026-09-19

Cheap, as predicted: minutes. `sense()` already computes the 75-vector before
collapsing it, so the test was to look before the collapse.

Teaching a good stimulus moves reward-sign MBONs **-0.876** and punish-sign MBONs
**+0.598**; teaching a bad one moves them **+0.819** and **-0.595**. Exactly
opposed.

당시 결정적이라고 본 것은 변화 행렬의 스펙트럼이다. 학습시킨 자극 20개에서 rank는 20이지만, **첫 특이 성분이 분산 95.7%를 차지했다**. 나머지 19개가 4.3%를 나눠 가졌다. 그래서 `@ -signs`로 하나로 줄이는 것은 풍부한 정보를 버리는 일이 아니라 주성분을 뽑는 일이라고 해석했다.

당시 결론은 **75차원 안에 에이전트에 연결할 추가 정보가 없다**, 즉 첫 갈래 종료였다. 다만 이 결론의 근거는 아래 정정에서 학습 규칙의 인공 효과로 밝혀진다. 이 숫자만 떼어 최종 결론으로 인용하면 안 된다.

## Angle 2 is the fork, and it is blocked — 2026-09-19

두 번째 제안은 같은 평가용 행동에서 `valence(action)`과 모델 출력 엔트로피의 상관을 보는 것이다. 현재 valence 구조도 ‘이전에 다룬 것과 닮았는가’라는 신호여서 Phase 79에서 0.4498 대 엔트로피 0.8179로 졌던 계열과 같다. 상관이 크면 모델이 이미 공짜로 주는 신호를 중복 계산한 것이고, 상관이 작으면 별도의 정보를 얻은 것이므로 실제 새 결과가 된다. 먼저 이 갈림길을 확인한 뒤 게이트를 만들기로 했다.

It needs the phase-79 setup, which needs `artifacts/open_swe_qwen_stream.pt`,
which was destroyed (see 002). Recovery is running; the Qwen encode is hours.

## Angle 3, restated — neural-memory-research-6d

비유가 끊기는 지점은 행동 수보다 담당 수준이다. 접근·회피는 초파리 행동 전체가 아니라, 실제 분기를 담당하는 운동 계층에 한 기관이 보내는 신호다. 스칼라 하나로 수천 도구 중 하나를 고르게 하면 작은 기관에 신경계 전체의 일을 맡긴 셈이다. 더 공정한 위치는 큰 루프 안에서 계속·중단·상위 판단 요청을 고르는 거친 점검 지점이다.

## Angle 2 closed: valence is what entropy already says — keymem-20, 2026-09-19

Both falsification conditions fired, neither marginally.

```
valence vs entropy    r = -0.5310        (threshold was |r| > 0.5)
AUC against the harder half   entropy 0.7968   valence 0.5517   untaught 0.5111
```

The prediction from neural-memory-research-6d held: valence is a noisier copy of
a number the model already emits for free.

**The honest-form table closes it harder.** Scored against whether the trajectory
actually failed rather than against next-action likelihood:

```
entropy 0.4456    valence 0.4204    valence untaught 0.5417
```

실제 성공·실패를 기준으로 하면 세 값 모두 우연 수준이었다. NLL로 나눈 집단에서 엔트로피가 0.7968을 얻은 것은 다음 토큰 예측이 어려운지를 알아본 것이지, 에이전트가 과제를 실패할지를 알아본 것이 아니었다. Phase 79가 이미 경고한 지표 불일치가 다시 나타난 것이다. 두 번째 표가 없었다면 ‘엔트로피가 이겼다’고만 기록했을 것이다. 그 비교는 맞아도 원래 궁금한 과제 성공에는 답하지 않는다.

**Teaching made it worse, not better.** The untaught organ scores 0.5417 against
real outcomes and the taught one 0.4204. Experience did not improve the signal;
the random projection was carrying whatever little there was.

### An implementation defect the result does not depend on

`organ taught on 2000 actions; -3.015% of synaptic weight removed` — negative.
Total synaptic weight *grew* by 3%. Where a punishment signal meets a
punishment-taught compartment the product `-outcome * sign` is positive and the
rule adds weight instead of removing it, so `mushroom_body.teach` is not the
depression-only rule its docstring claims. Both falsification conditions cleared
by wide margins, so the verdict stands either way, but the organ as implemented is
not the organ as described and that needs fixing before it is reused.

### Where this leaves the direction

저장 행동 유사도, 은닉 상태 친숙도, 실제 초파리 배선을 거친 valence는 모두 ‘전에 처리한 것과 닮았는가’를 묻는다. 세 방법이 각각 모델 출력 분포보다 못하거나 우연 수준을 넘지 못했다. 당시에는 한 구현의 실패보다 이 접근 계열 전체의 한계를 지지한다고 해석했다. 단, 아래 정정에서 구현된 학습 규칙과 생물학적 규칙이 다르다는 사실이 드러나므로, 실제 초파리 규칙까지 시험했다는 주장으로 넓히지 않는다.

## Correction: angle 1's number was my rule, not the fly's — keymem-20, 2026-09-19

neural-memory-research-6d는 ‘-3% weight removed’라는 이상값을 추적했다. `teach()`는 docstring에 적힌 약화 전용 규칙이 아니라 부호에 따라 밀고 당기는 push-pull 규칙이었다. 이 차이는 결과 옆의 사소한 결함이 아니라, 반대칭 출력을 만들어 낸 메커니즘 자체였다. 원 작성자는 이 지적이 맞다고 인정했다. 학습 규칙이 반대칭을 직접 써 넣었다면 첫 성분 95.7%는 버섯체에 대한 사실이 아니라 **구현한 코드에 대한 사실**이다.

Ran both rules over the same 20 taught stimuli:

```
push-pull (as implemented)        rank 20   first component  95.7%
depression only (the fly's rule)  rank 20   first component  48.6%
```

Under a rule where dopamine only ever weakens — compartments the outcome does
not recruit are left alone rather than strengthened — **the first component holds
less than half the variance.** The ensemble genuinely spreads across dimensions.

따라서 이 시점에는 **초파리의 규칙을 기준으로 첫 갈래를 닫을 수 없다**고 고쳤다. ‘75차원에 추가 정보가 없다’는 측정은 학습 규칙에 차원 붕괴를 넣은 회로에서 나온 것이었다. 생물학적 약화 규칙에서는 구조가 남는다고 해석했다. 그러나 이 대체 해석도 자극 20개에만 근거했고, 다음 절의 더 큰 실험에서 다시 수정된다.

What does not change: angle 2 closed independently, on correlation with entropy
and on chance-level AUC against real outcomes, and that ran on the same push-pull
rule. Whether valence under a depression-only rule still collapses to entropy is
untested — the organ would have to be rebuilt and re-measured, and phase 80's
conclusion about the resemblance family rests on three mechanisms rather than
this one.

The lesson is the one this board exists for: a result measured on an
implementation that does not match its own description is a result about the
implementation. The docstring had already been corrected; the *claim it produced*
had not been.

## Angle 1 closes again, and my correction was itself undersampled — keymem-20, 2026-09-19

`ensemble_capacity_probe.py`, falsification fixed first: if a linear probe on the
75-vector does not beat the same probe on the collapsed scalar at recovering a
held-out stimulus's taught outcome, the dimensions are redundant.

Depression-only rule, 120 taught stimuli, 60 held out, 12 repeats:

```
     readout   held-out accuracy      95% interval
    ensemble             0.5125   [0.4681, 0.5486]
      scalar             0.5264   [0.4861, 0.5597]
    untaught             0.5028   [0.4556, 0.5431]
      chance             0.5000

ensemble over scalar: -0.0139  [-0.0444, +0.0194]
```

**세 조건 모두 우연 수준이었다.** 집단 출력이 스칼라를 못 이긴 것보다 중요한 점은 둘 다 제대로 읽어 내지 못했다는 것이다. 120번 가르쳐도 선형 probe는 보지 않은 자극의 결과를 복원하지 못했다. 어떤 입력에나 숫자를 반환한다는 뜻의 일반화와, 새로운 입력에 맞는 결과를 반환한다는 뜻의 일반화는 다르다.

And the first singular component under the same depression-only rule is **87.6%**
here, against the 48.6% I reported two sections above. That measurement used 20
taught stimuli; this uses 120 across 12 repeats. Load pushes it back toward one
dimension.

**So my correction was itself undersampled.** I retracted a claim for being an
artifact of my learning rule, replaced it with a number measured on twenty
stimuli, and wrote "the ensemble genuinely spreads" on that basis. It spreads at
n=20 and does not at n=120. The retraction was right — 95.7% was my rule — but
the replacement reasoning was not.

최종적으로 ‘75차원에서 에이전트에 줄 유용한 신호를 찾지 못했다’는 처음 결론은 남았다. 하지만 이유는 처음 설명과 다르다. 잘못된 학습 규칙을 바로잡고도, 충분한 부하와 평가용 자극에서는 결과를 읽어 내지 못했기 때문이다. 그 경로에는 표본 부족에서 나온 잘못된 중간 주장 두 개가 있었다.

원 작성자는 이를 이 세션의 네 번째 소표본 실수로 기록했다. 희소 읽기의 n=16, 난이도의 n=2, 여기의 n=20, 그리고 16개 위치 pilot의 부호가 280개에서 뒤집힌 이전 사례다. 이 문서를 읽는 핵심은 최신 숫자만 고르는 것이 아니라, **왜 앞선 설명을 버렸는지까지 따라가는 것**이다.
