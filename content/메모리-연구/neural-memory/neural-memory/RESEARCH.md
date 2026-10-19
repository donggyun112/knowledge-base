---
title: "Research reuse map"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `neural-memory/RESEARCH.md` · 수집 2026-10-16 · 커밋 `fd190b18f8e4113d7f451a7108911c1f89716b24`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# Research reuse map

이 문서는 ‘왜 이 메모리 구조를 선택했고, 실패한 뒤에는 왜 다른 질문으로 옮겼는가’를 기록한다. 처음부터 새 아키텍처를 제안하기보다, 이미 알려진 메커니즘을 조합해 기본 현상이 생기는지 먼저 측정하기로 했다.

출발 질문은 **나중에 도움이 된 경험만 남기려면, 지금의 쓰기 결정을 어떻게 학습시켜야 하는가**였다. 아래 표는 각 선행 연구에서 이번 실험에 필요한 부분만 가져온 내역이다. 모델 전체를 복제하지 않고 온라인 상태 갱신, 예측 오차, 기억 감쇠, 경쟁적 할당을 나누어 시험하면, 어느 메커니즘이 실제로 작동했는지 따져 볼 수 있다.

| Prior work | Mechanism reused here | Deferred from phase 0 |
| --- | --- | --- |
| [Learning to (Learn at Test Time)](https://arxiv.org/abs/2407.04620) | A model-valued hidden state updated online; slow parameters learn the update behavior | Full TTT language-model stack and optimized mini-batch scan |
| [Titans](https://arxiv.org/abs/2501.00663) | Prediction residual as surprise; explicit retention/decay | Momentum, deep memory MLP, and integration into a transformer backbone |
| [Linear Transformers Are Secretly Fast Weight Programmers](https://arxiv.org/abs/2102.11174) | Residual delta-rule update, which can replace an existing key/value association | Kernelized multi-head fast weights |
| [MIRAS](https://arxiv.org/abs/2504.13173) | Separate the choices of memory architecture, attentional objective, retention, and optimizer | Alternative objectives and retention rules |
| [Fast Weight Memory](https://arxiv.org/abs/2011.07831) | Evaluate compositional associative behavior as a learned recurrent state | Its LSTM controller and task-specific reasoning stack |
| [Synaptic plasticity-dependent competition rule influences memory formation](https://doi.org/10.1038/s41467-021-24269-4) | Treat memory allocation as competition among plastic parameter groups, not only a global write/no-write decision | Any claim that mouse fear-memory allocation is a general model of human memory |

공식 [TTT PyTorch 구현](https://github.com/test-time-training/ttt-lm-pytorch)은 식과 텐서 형태를 확인하는 데 유용하다. 다만 저자들이 느린 튜토리얼용 구현이라고 설명하며 학습용으로 권하지 않는다. 전체 언어 모델 스택을 복사하면 첫 실험의 비용은 커지지만, ‘무엇을 쓸지 학습하는가’라는 가설을 더 직접적으로 시험하지는 못한다. 그래서 첫 단계에서는 작게 분리한 메모리만 다룬다.

## Frozen design choices for phase 0

Phase 0에서는 아래 선택을 고정한다. 한 번에 여러 요소를 바꾸면 좋아진 이유가 저장 선택인지, 표현력인지, 용량인지 분리할 수 없기 때문이다.

- **기억 표현:** 에피소드마다 하나의 행렬형 fast-weight 상태를 둔다. fast weights는 전체 학습이 끝난 뒤에도 해당 에피소드의 관찰을 따라 바뀌는 가중치다.
- **쓰기 규칙:** 정규화한 residual delta update를 쓴다. 이미 읽히는 값과 이번 목표 값의 차이를 수정하는 규칙이다.
- **주의 목적 함수:** 나중에 키에서 값을 회상할 때의 교차 엔트로피다.
- **보존:** 고정된 비율을 곱해 감쇠한다.
- **쓰기 선택:** 현재 관찰, 잡음이 있는 현재 증거, 예측 놀라움을 입력으로 받는 학습 스칼라 게이트다. 게이트는 이번 관찰로 기억을 얼마나 바꿀지 정한다.
- **외부 학습 신호:** 미래 회상 결과만 사용한다. `retained`는 에피소드 구성과 평가에만 쓰며, 쓰기 게이트의 직접 정답 라벨로 주지 않는다.
- **그래프·외부 저장소 없음:** 변하는 파라미터 텐서 자체가 기억이다.

이렇게 하면 하나의 질문을 떼어 낼 수 있다. **뒤늦게 드러난 유용성이, 앞서 어느 순간 fast weights를 바꿨어야 하는지 가르칠 수 있는가?** 이 단계가 성공해도 아직 의미를 이해하는 텍스트 기억을 확립한 것은 아니다.

## Decision gates

1. **메커니즘 관문:** 학습 쓰기 게이트가, 나머지 조건을 같게 학습한 always-write 모델보다 보지 않은 무작위 연결을 잘 회상해야 한다. 유용한 사건에는 평균적으로 더 큰 게이트를 주어야 한다.
2. **동역학 관문:** 첫 관문을 통과한 다음에 수정, 지연 감쇠, 여러 시간 척도의 고착을 추가한다.
3. **언어 관문:** 상태 갱신이 통과한 다음 기호 ID를 동결 텍스트 인코더 표현으로 바꾸고 작은 디코더를 더한다.
4. **에이전트 관문:** 독립 모델이 통과한 다음 메모리 출력을 동결 LLM에 연결하고, 기억하라는 지시 없이 자발적으로 회상하는지 잰다.

순서를 이렇게 잡은 이유는 강력한 언어 디코더가 메모리의 실패를 가리지 않게 하려는 것이다. 최종 답변만 좋으면 실제로 기억이 저장되었는지 알기 어렵다. 먼저 작은 상태의 쓰기·읽기를 확인하고, 그 뒤에 언어와 실제 행동으로 넘어간다.

## Biological allocation hypothesis for phase 1

Jeong 등의 연구는 생쥐 외측 편도체의 청각 입력에서 연결 강화와 약화를 조작했다. 강화된 입력은 공포 기억 engram, 즉 해당 기억과 관련된 활성 세포 집단에 우선 포함되었고, 학습 뒤 약화시키면 그 할당을 되돌릴 수 있었다. 회상 때 활성화되는 전체 집단 크기는 대체로 일정했다. 저자들은 이를 각 뉴런이 독립적으로 참여 여부를 고르는 것보다, 제한된 가소성을 놓고 경쟁하는 할당의 근거로 해석했다.

여기서 가져온 아이디어는 ‘사람의 기억도 이렇게 동작한다’는 주장이 아니다. **전체를 하나의 게이트로 켜고 끄는 것과, 같은 쓰기 예산을 여러 블록이 나누어 갖는 것 중 어느 쪽이 나은가**라는 계산 실험이다.

```text
single global write gate              competitive block allocation
g = sigmoid(controller(x))     vs.    a = sparse competition(score_1 ... score_n)
W <- W + g * delta                    W_i <- W_i + a_i * delta_i
```

경쟁에는 고정된 가소성 예산을 둔다(`sum(a) = 1` 또는 top-k 할당). 최근 사건은 짧은 eligibility window, 즉 나중 신호로 아직 갱신할 수 있는 기간 안에서는 다시 할당할 수 있다. 한 블록을 강화하면 다른 블록과 예산을 경쟁하거나 이웃을 약화시킨다. 비교할 것은 동일한 파라미터 수와 갱신 예산에서 Phase 0의 단일 스칼라 게이트보다 용량, 수정, 기억 연결이 좋아지는지다.

이 논문은 생쥐의 특정 공포 조건화 회로에 인위적 광유전학 LTP/LTD를 가한 연구다. 같은 규칙이 인간 기억 전체를 지배한다는 근거로 쓰면 안 된다.

# Survey, 2026-09-14: should the write decision be deferred?

Phases 12–16은 현재 관찰만으로 미래의 쓸모를 예측하는 쓰기 게이트를 학습한다. 그런데 실제 로그를 쓴 Phase 7은 이미 이 발상의 한계를 보여 주었다. 관찰 시점 증거만 있으면 balanced accuracy가 0.543이었고, 지연 피드백이 도착한 뒤에는 0.980이었다. balanced accuracy는 클래스별 정답률의 평균으로, 한쪽 라벨이 많은 자료에서 단순 정확도보다 균형 있게 본다.

이 차이는 ‘더 좋은 예측기를 만들자’ 외에 **판단을 나중으로 미루자**는 선택지를 연다. 이번 조사는 그 선택지가 한 실험 이상의 근거를 갖는지, 미룬다면 어떤 구조여야 하는지 알아보기 위한 것이다.

Phase 1에서 정한 경계는 계속 적용한다. 동물 연구는 시험할 *아키텍처*의 출처이지, 인간 기억이나 이번 모델의 수치를 뒷받침하는 증거가 아니다. 예를 들어 Jeong 등의 연구에서 가져온 경쟁적 할당이 단일 행렬을 0.9243 대 0.2347로 이긴 것은 이 모델의 결과이며 생쥐에 대한 결과가 아니다.

## Deferred consolidation in biology

세 독립적인 메커니즘은 같은 설계 방향을 가리킨다. 일단 국소 신호로 값싸게 흔적을 만들고, 뒤에 도착하는 사건이 무엇을 남길지 결정하게 한다. 여기에 회상 후 다시 불안정해지는 재고착까지 함께 검토했다. 중요한 추가 조건은 **그 유예 시간이 유한하다**는 점이다. 아래 표의 시간은 동물 실험의 시간 창이며, 모델의 스텝 수와 그대로 같다고 두지 않는다.

| Mechanism | Deferral window | Source |
| --- | --- | --- |
| Excitability-biased allocation (CREB); excitability decays over hours | hours | [Josselyn & Frankland 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4262914/); [J Neurosci 2024](https://www.jneurosci.org/content/44/21/e0846232024) |
| Synaptic tagging and capture: a weak tag captures later plasticity-related proteins | classically under 3 h; one 2026 report extends capture to 9 h | [Frey & Morris, Nature 1997](https://www.nature.com/articles/385533a0); [Commun Biol 2026](https://www.nature.com/articles/s42003-025-07998-w) |
| Replay selection biased by reward prediction, consolidated across sleep | hours to overnight | [Nat Commun 2026](https://www.nature.com/articles/s41467-025-65354-2); [eLife 2015](https://elifesciences.org/articles/07903) |
| Reconsolidation: retrieval returns a trace to a labile state | about 6 h | [Nader et al., Nature 2000](https://pubmed.ncbi.nlm.nih.gov/35145138/) |

설계에서는 무한히 기다리는 버퍼를 허용하지 않는다. 모든 후보를 질문이 나올 때까지 유지하면 여기서 시험하려는 제한된 기억 대신 전체 후보 검색을 하게 되고, 위 생물학적 시간 창과도 맞지 않는다. 측정할 것은 **제한된 지연이, 즉시 판단과 질문을 본 뒤 판단 사이의 격차를 얼마나 메우는가**다. Claude 말뭉치에서 그 두 조건의 top-1은 0.5686 대 0.8206이었다.

## The mushroom body as a specified circuit

The fly connectome makes a complete memory circuit available as architecture rather than principle:
139,255 neurons and about 50 million synapses in the adult female brain
([Dorkenwald et al., Nature 2024](https://www.nature.com/articles/s41586-024-07558-y);
[Schlegel et al. 2024](https://www.nature.com/articles/s41586-024-07686-5)). Connectivity alone,
with neurotransmitter identity, already predicts behaviour in a whole-brain leaky integrate-and-fire
model ([Shiu et al., Nature 2024](https://pubmed.ncbi.nlm.nih.gov/37205514/)).

이 회로를 본 이유는 ‘뇌와 닮았다’는 인상 때문이 아니라 설계 요소를 더 구체적으로 고를 수 있기 때문이다. 아래 네 특성은 서로 다른 문제를 다룬다. 희소 확장은 비슷한 항목의 간섭을 줄이고, 도파민은 내용을 읽는 대신 결과 신호로 쓰기를 조절하며, 구획들은 시간 척도가 다른 저장소로 병렬 동작한다. 이미 나온 파생 알고리즘들이 어디까지 구현했는지도 분리해서 본다.

- **Sparse expansion.** About 50 projection neurons fan out to roughly 2,000 Kenyon cells, each
  integrating 6 to 8 inputs across 5 or 6 claws. Reciprocal inhibition through the single GABAergic
  APL neuron keeps only 5 to 10 percent of Kenyon cells active, and removing that sparsening impairs
  discrimination of similar but not dissimilar odours
  ([Lin et al., Nat Neurosci 2014](https://www.nature.com/articles/nn.3660)). Our `keep_ratio` of
  0.25 is several times denser than this.
- **The write signal does not read the content.** Kenyon cells carry odour identity; dopaminergic
  neurons carry reinforcement and gate plasticity at the Kenyon-cell-to-output-neuron synapse. The
  same dopaminergic neuron writes aversive memory when it fires within about 30 s after odour onset
  and appetitive memory when it precedes odour by 20 to 60 s, so sign comes from the modulatory
  channel alone. A second activation minutes after training, **with no odour present**, nearly
  abolishes the conditioned response ([Aso & Rubin, eLife 2016](https://elifesciences.org/articles/16135)).
  `SelectiveWriteRecallMemory` does the opposite: its gate scores the content itself. Phase 7's
  `apply_outcome()` is the component that already matches this shape and is currently unused by the
  phase 12 to 16 line.
- **Compartments are parallel, not a promotion pipeline.** Output neurons tile the lobes into 15
  compartments with their own dopaminergic input and their own decay, capacity, and flexibility.
  γ1pedc holds strong immediate memory that is largely gone by 24 h and has a capacity of one,
  retaining only the most recently trained odour, while α1 has weak immediate memory, supports
  long-term consolidation, and holds at least two. Trained with opposing signals, both traces form
  simultaneously and the expressed valence flips as the fast compartment decays. This favours
  several stores with different decay rates read as a sum, over a provisional buffer that promotes
  into a durable one.
- **Derived algorithms exist but not for this.** Fly-inspired locality-sensitive hashing
  ([Dasgupta, Stevens & Navlakha, Science 2017](https://www.science.org/doi/10.1126/science.aam9868)),
  Bloom-filter novelty detection ([PNAS 2018](https://www.pnas.org/content/115/51/13093)), and sparse
  coding against catastrophic forgetting ([arXiv:2107.07617](https://arxiv.org/pdf/2107.07617)) all
  come from this circuit. None of them learns a write gate.

## The reinforcement side of the same circuit

2026-09-14 조사. 조절 경로를 하나의 스칼라 배율로 구현했으나 두 번 실패한 뒤, 생물 회로에서 빠뜨린 구조가 있는지 다시 보았다. 단순히 모든 기억을 같은 배율로 키워서는 후보 순위가 바뀌지 않는다. 그래서 아래에서는 입력 신호가 여러 종류인지, 출력에 반대 부호가 있는지, 현재 예측이 다시 쓰기 신호에 반영되는지를 나누어 살핀다.

**The input side is genuinely multi-channel.** The hemibrain resolves 21 dopaminergic types, 6 PPL1
and 15 PAM, tiling the 15 compartments roughly one type each, about 130 neurons in total
([Li et al., eLife 2020](https://elifesciences.org/articles/62576)). The dimensions are qualitatively
distinct rather than one axis at different gains: PPL1-γ1pedc reinforces shock, heat and bitter while
separately carrying hunger-state gating, and PAM-γ5 reinforces sugar and also signals shock omission
to extinguish an aversive memory, splitting into five subtypes by input connectivity
([Otto et al., Curr Biol 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7443709/)). Tuning, sign and
time constant vary independently, and the same DAN writes opposite signs depending on its timing
against the odour.

**The output side is opponent and summed.** Twenty-two canonical output types plus fourteen atypical,
in three transmitter classes split by lobe. An output neuron's valence is opposite to its
compartment's dopaminergic valence, and the plasticity is *depression*: the reinforcement turns down
the output that signals the opposite valence rather than strengthening one that agrees
([Owald et al. 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4674068/);
[Aso et al., eLife 2014](https://elifesciences.org/articles/04580)). Behaviour follows a weighted sum
across compartments that is balanced in a naive animal, not a winner.

**The output feeds back into the signal that writes it.** The connectome shows extensive and
selective output-to-dopaminergic feedback onto DAN dendrites: MBON-γ5β′2a contacts PAM-γ5(fb)
exclusively, while MBON-γ4γ5 is the strongest input to PPL1-γ1pedc and does not touch PAM-γ5
([Li et al. 2020](https://elifesciences.org/articles/62576);
[Otto et al. 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7443709/)). Modelling reads that return
path as reinforcement prediction error computed by subtraction across the opponent pair
([Bennett, Philippides & Nowotny, Nat Commun 2021](https://doi.org/10.1038/s41467-021-22592-4)).

**Two channels reproduce the behaviour.** Bennett et al. collapse the fifteen compartments to an
approach and an avoidance channel and recover a broad range of conditioning and blocking results.
The two differ in sign alone, not in tuning or time constant.

### What this says about our failures

Phase 18과 연상 저장 시도에서는 조절 배율이 상한에 붙고 실제 기여는 없었다. 빠뜨렸던 회로 특성 두 가지가 이 실패를 설명한다.

첫째, 현재 예측을 빼지 않은 단순 이득에는 커지는 것을 멈출 이유가 없다. 반면 강화 신호에서 메모리의 예측을 뺀 **예측 오차**를 쓰면, 이미 잘 예측하는 사건에서는 갱신 신호가 0으로 줄어든다. 둘째, 양수 채널 하나는 상태 전체의 크기만 바꾸므로 순위를 보존한다. 검색 순서를 바꿀 수 없다는 뜻이다. 반대 부호 채널을 차이로 읽으면 ‘이것은 강화하고 저것은 약화하라’를 표현할 수 있어 경쟁적 할당과 맞는다.

따라서 다음에 시험할 변화는 하나의 eligibility trace를 공유하는 두 부호 채널이다. 읽기는 두 채널의 차이, 구동 신호는 강화에서 현재 기억 예측을 뺀 값으로 만든다. 그다음에는 채널 수를 늘리기보다 채널별 감쇠를 시험하는 편이 낫다. Phase 22에서 약한 기억을 뒤늦게 살리는 시간 창을 만드는 변수가 tag decay였기 때문이다.

**논쟁 중이거나 미확인인 부분도 남긴다.** 구획마다 도파민 유형이 하나라는 구조가 보편적인지는 확정되지 않았다. 두 출처에서 DAN-to-DAN 연결이 나오지 않는 것은 부재의 증거이지, 연결이 없다는 입증은 아니다. 두 채널로 충분하다는 주장 역시 조건화 검사에 대한 모델링 결과이며 기억 용량이나 수명에 대한 결과는 아니다.

## What forgetting research says about capacity

Forgetting is an active, default-on process rather than passive leakage: ongoing dopaminergic
activity erases labile memory in Drosophila unless salience marks it for retention
([Berry et al., Neuron 2012](https://www.cell.com/neuron/fulltext/S0896-6273(12)00338-8)), and
transience is argued to be functional, preventing overfitting to specific episodes
([Richards & Frankland, Neuron 2017](https://www.cell.com/fulltext/S0896-6273(17)30365-3)). Decay
rate itself appears to adapt to update frequency, existing to limit interference
([Altmann & Gray, Psych Science 2002](https://journals.sagepub.com/doi/10.1111/1467-9280.00405)).

Competition bounds *relative* excitability, not a counted slot budget, and Landauer explicitly
disclaimed his capacity estimate as a bound on storage
([Landauer, Cognitive Science 1986](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog1004_4)).

이 관점에서 저장 시점의 hard top-k는 서로 다른 세 조절값, 즉 부호화 강도·감쇠율·검색 문턱을 하나의 되돌릴 수 없는 스위치로 합쳐 버린다. Phase 14는 입력에 따른 보존 게이트를 이미 시험했다가 기각했다. 당시 해석은 발상 자체의 실패라기보다, 훈련 에피소드 775개로 더 복잡한 보존 정책을 식별하기에는 부족하다는 것이었다. 이 구분을 남겨야 이후 결과가 그 해석을 유지하는지 검토할 수 있다.

## Where our novelty now sits

| Prior work | Relation to this project |
| --- | --- |
| [Learning to Evict from Key-Value Cache](https://arxiv.org/abs/2602.10238) (KVP, ICML 2026) | Per-head reinforcement-learned agents rank tokens by predicted usefulness. This is already a learned future-utility write gate, so "learned write gating" is no longer a differentiator. Differs by acting on KV tokens inside the model rather than semantic traces beside a frozen encoder, and by being single-stage. |
| [RecMem](https://arxiv.org/abs/2605.16045) (ACL 2026 Findings) | Closest two-stage system: every interaction enters a subconscious embedding layer and an LLM consolidates only when sustained recurrence appears among semantically similar interactions, cutting construction tokens up to 87%. Promotion-only and never discards, so it does not face irreversible capacity loss. |
| [What Eviction Destroys](https://arxiv.org/abs/2609.08279) | Independent support rather than competition: a restore-counterfactual audit attributing 60 to 73 percent of corrected errors to irreversible eviction at an 80k budget, and all of them at 8k. Corroborates the phase 15 finding that the whole task-level shortfall is write selection. |
| [Agentic Memory](https://arxiv.org/abs/2601.01885) (ACL 2026) | Learns unified long- and short-term memory management with three-stage reinforcement learning and a step-wise GRPO variant for sparse memory-action rewards. Whether the backbone language model is itself updated is not stated in the abstract and was not verified. |

따라서 ‘쓰기 게이트를 학습한다’는 사실만으로는 새로운 점이 되지 않는다. 남은 차별점은 두 단계로 판단을 유예한다는 점과, 의미 흔적을 되돌릴 수 없게 버리는 용량 제한 환경이다. 아래의 논쟁 목록까지 포함해, 문헌에서 확인한 것과 이번 연구가 아직 주장할 수 없는 것을 나누어야 한다.

## Contested — do not present as settled

- Post-encoding reversal of allocation rests mainly on Jeong et al. 2021. General allocation reviews
  do not establish it.
- Human retroactive behavioural tagging has explicit null results, and reconsolidation has a direct
  failed replication ([Sci Rep 2022](https://www.nature.com/articles/s41598-022-06119-5)).
- Parallel compartments versus the older sequential consolidation model (γ to α′β′ to αβ) remains
  open; trace migration must not be presented as fact.
- Whether forgetting erases or only removes access is disputed
  ([Ryan & Frankland, Nat Rev Neurosci 2022](https://pubmed.ncbi.nlm.nih.gov/35027710/)).
- Kenyon cell connectivity is mostly but not entirely random; food-responsive projection neurons are
  a reported exception ([eLife 2022](https://elifesciences.org/articles/77578)).
- [Neuromem](https://arxiv.org/abs/2602.13967) is a streaming-memory testbed that decomposes the
  lifecycle into data structure, normalization, consolidation policy, query formulation, and context
  integration. It treats consolidation as a distinct dimension, but whether any stage carries learned
  parameters is not stated in the abstract and was not verified.

All arXiv identifiers in this survey were checked against the listing pages on 2026-09-14.

# Redesign, 2026-09-14

## Why the previous design has to be abandoned

Phases 12–19는 제한된 층에게 후보 8개 중 나중 질문이 필요로 할 것을 고르게 했다. 대조를 넣을수록 결과는 같은 한계로 모였다. deferred 말뭉치에서 같은 폭의 미학습 무작위 투영은 행렬도 학습도 없이 top-1 0.4033이었고, 학습 연상 모델은 0.4956이었다. 올바른 사건을 주면 0.4971, 빈 사건을 주어도 0.4956이었다. 서로 다른 쓰기 정책 네 개도 0.4825–0.5000에 모였다. 슬롯 모델에서 크게 보였던 사건 효과는 메모리가 계산한 것이 아니라, 사건과의 코사인 유사도를 잔차 점수로 직접 더한 데서 나왔다.

과제 모양 자체가 문제였다. 회상할 때 후보들을 다시 보여 주면 인코더 코사인이 기억을 대신할 수 있고, 그 역할을 학습 가능한 제한 상태보다 더 잘한다. 또한 ‘중요함’과 ‘미래에 쓸모 있음’은 같은 정의가 아니다. 미래 유용성 정답으로 쓰기 결정을 채점하면 무엇을 기억이라고 부르는지부터 좁혀진다. 저장 임베딩의 정확한 복원을 보상하는 점수 역시 내용을 그대로 보관하는 능력을 보상하므로, 요지는 남기고 세부는 잃는 기억을 보려는 설계와 다르다.

문헌 조사에서 가져온 현상들은 후보 목록에서 정답을 고르는 문제가 아니었다. 제한된 기억이 부하에 따라 어떻게 나빠지는지, 간섭에 맞춰 감쇠가 바뀌는지, 구획별 시간 상수가 어떤 차이를 만드는지, 희소화가 비슷한 항목에서만 도움이 되는지에 관한 것이었다. **다음 실험은 검색 순위 대신 이 보유 특성들을 직접 측정하기로 한다.**

## What the survey licenses, as constraints

아래 열 가지는 다음 모델이 만족해야 할 설계 제약이자 시험할 가설이다. 생물학을 그대로 구현했다고 선언하는 체크리스트가 아니다. 특히 논쟁 중인 항목은 반박 가능한 실험 대상으로 유지한다.

1. **The write signal must not read content.** Dopaminergic neurons carry reinforcement, not odour
   identity, and sign comes from the modulatory channel alone. Write strength may depend on the
   memory's own prediction error or on an external outcome, never on a judgement about the content.
2. **Modulation must work with the item absent.** A second activation minutes after training, with
   no odour present, nearly abolishes the response. Consolidation therefore acts on an eligibility
   trace addressed by coincidence, not by re-presenting the item.
3. **Stores run in parallel with different time constants and are read as a sum.** Compartments do
   not promote into one another; γ1pedc holds one item and is gone by 24 h while α1 is weak
   immediately and durable later, and the expressed answer flips as the fast store decays.
4. **Codes are sparse and expanded, and sparsening matters only for similar items.** Fifty inputs
   fan out to two thousand cells with 5 to 10 percent active, and removing the inhibition impairs
   discrimination of similar but not dissimilar odours.
5. **Forgetting is active and its rate adapts to interference.** Decay is a trained dynamic, not a
   constant, and encoding strength, decay rate, and retrieval threshold stay three separate knobs.
6. **Allocation is competitive under a roughly fixed budget.** Potentiated inputs are preferentially
   recruited while the recall-active population stays about constant, so strengthening one trace
   should cost others rather than being free.
7. **What is allocated depends on current excitability, which decays over hours.** Items encountered
   close together are therefore biased onto shared substrate, which predicts linking between them and
   not only interference.
8. **A weak trace can be rescued later, inside a window.** Tagging and capture give a weak event
   access to plasticity a later strong event supplies, classically under three hours. The window is
   finite, which is the part the corpora could not show us.
9. **Consolidation continues offline and selectively.** Replay is biased by reward and keeps working
   across sleep, so retention can improve with no new input.
10. **Reading a memory changes it.** Retrieval returns a trace to a labile state before it
    restabilises, so recall is not a passive operation on the state.

## The replacement task

N개 문서를 제한된 상태에 저장한 뒤 단서로 읽고, 무엇이 돌아오는지 잰다. 회상 시점에는 후보 목록을 다시 보여 주지 않는다. 따라서 단서와 후보의 유사도만으로 기억을 대신할 수 없다. 쓰기에서 읽기로 이어지는 것은 **저장 상태뿐**이다.

각 단서에서 두 점수를 구분한다.

- **gist recovery:** 되살린 내용이 문서가 담고 있던 사실·요지와 얼마나 일치하는가.
- **surface recovery:** 되살린 내용이 문서의 원래 표현 형식과 얼마나 일치하는가.

설계 가설은 저장량이 늘어날수록 표면 표현이 요지보다 먼저 손실된다는 것이다. 원문 그대로 저장하는 장치는 둘을 함께 잃고, 단순 검색기는 검색에 완전히 실패하기 전까지 둘 다 잃지 않는다는 대비를 둔다. 이 차이가 실제로 생기는지는 아래의 별도 측정으로 확인해야 한다.

## Measurements, one per mechanism the survey established

각 행은 출발한 발견, 그로부터 세운 예측, 예측이 틀렸다고 판단할 결과를 함께 적었다. 동물 연구의 시간 경과는 여기서 중간에 끼어든 쓰기 횟수로 옮긴다. 이 상태를 실제로 바꾸는 것은 시계 자체가 아니라 새 쓰기로 생기는 간섭이기 때문이다. 예를 들어 2번은 희소화가 모든 문서를 균일하게 돕는지가 아니라, **서로 비슷한 문서에서 특히 더 돕는지**를 본다. 7번은 뒤늦게 주는 강한 신호가 약한 흔적을 살릴 수 있는 유한한 시간 창을 찾는다.

| # | From | Measurement | Prediction | Fails if |
| --- | --- | --- | --- | --- |
| 1 | Transience is functional (Richards & Frankland 2017); decay adapts to interference (Altmann & Gray 2002) | Fidelity against number of documents stored, at fixed state size | Graceful degradation, and a trained decay beats a fixed one only as load rises | Flat, or a cliff, or trained decay never separates from fixed |
| 2 | Sparse expansion and APL inhibition; removing it impairs similar but not dissimilar odours (Lin et al. 2014) | The same curve for sparse expanded codes against dense low-dimensional ones, run separately on similar and dissimilar document sets | Sparse degrades more slowly, and the gap appears only for similar documents | Sparsity helps uniformly, or not at all |
| 3 | Memory is gist-preserving and detail-losing | Gist against surface recovery across the same load | Surface decays first | Both decay together |
| 4 | Compartments run in parallel with their own decay and capacity; expressed valence flips as the fast one fades (Aso & Rubin 2016) | Two stores with different decay read as a sum, probed after varying numbers of intervening writes | What is expressed changes with delay, and one store cannot reproduce the curve | A single store matches the two-store readout |
| 5 | Competitive allocation under limited plasticity; total engram population roughly constant (Jeong et al. 2021) | Whether strengthening one trace measurably costs others, at fixed state size | Gains and losses trade off; forcing that trade-off helps rather than hurts | Traces strengthen independently, or the constraint only hurts |
| 6 | Excitability biases allocation and decays over hours (Josselyn & Frankland 2015) | Whether documents written close together share substrate | Items written adjacently are recalled together more than distant ones, a linking effect distinct from interference | No difference between adjacent and distant pairs |
| 7 | Synaptic tagging and capture: a weak tag is rescued by a later strong event inside a window (Frey & Morris 1997) | Write an item weakly, apply a strong unrelated event after k intervening writes, measure rescue against k | Rescue falls off with k, giving the deferral window the corpora could not supply | Rescue is flat in k, or absent |
| 8 | Replay selection is biased by reward and consolidates offline (eLife 2015; Nat Commun 2026) | An offline phase that re-applies stored eligibility with no new input | Selected traces retain better than unselected ones after the same load | Offline replay changes nothing |
| 9 | Retrieval returns a trace to a labile state (Nader et al. 2000) | Probe an item, then re-write, and measure drift | Recalled items drift, and repeated recall compounds it | The state is unchanged by being read |
| 10 | The dopaminergic write signal never reads content, and a second activation with the item absent abolishes the response (Aso & Rubin 2016) | A modulatory signal applied after writing, with the item absent | Recall changes, and a mismatched signal does not produce that change | The signal is inert, as it was in every attempt today |

실행 순서에도 이유가 있다. 먼저 측정 2를 한다. 회로에서 나온 예측 중 가장 구체적이고, 어떤 방향으로 틀릴 수 있는지 명확하며, 아직 다른 결과가 여기에 기대고 있지 않기 때문이다. 같은 저장 부하 곡선을 쓰는 1과 3은 함께 측정한다.

측정 7은 특히 중요하다. LongMemEval-S에서는 나중 사건이 거리에 관계없이 똑같이 정보를 주어 유예 시간 창을 볼 수 없었다. 여기서는 지연을 직접 정하므로 그 창을 시험할 수 있다. 측정 10은 이미 두 번 실패했다. 1–3에서 기억이 무엇인가를 보유한다는 점을 먼저 확인하기 전에는 다시 시도하지 않는다.

확인된 생물학을 재현했다는 표현을 피해야 하는 항목도 있다. 5는 주로 Jeong 등의 연구에 기대고, 9에는 직접적인 재현 실패가 있으며, 4는 오래된 순차 고착 모델과 경쟁한다. 세 항목 모두 **논쟁 중인 주장을 시험한 결과**로 보고해야 한다.

## What has to be built

찾아낸 에피소드를 그대로 쓰기보다 통제된 문서 집합을 만들어야 한다. 측정 1과 2에서는 저장 항목 수와 항목 간 유사도를 독립적으로 바꿔야 하기 때문이다. 문서와 사실은 LongMemEval 세션에서 가져오고, 인코더 유사도로 묶어 유사도 축을 만든다.

이때 미래 유용성을 알려 주는 교사 라벨은 완전히 없앤다. 목적은 저장했던 것을 그 단서에서 복원하는 것이므로, 나중에 어느 문서가 중요할지에 대한 라벨이 학습에 들어갈 필요가 없다.

## What this design deliberately gives up

이 재설계는 미래 유용성을 미리 맞히는 문제를 내려놓는다. Phase 19에서 이미 정보 부족으로 제한된다는 결과가 나왔기 때문이다. 검색이 잘하는 후보 고르기에서 억지로 경쟁하는 것도 멈춘다. 후보 선택에서 코사인을 못 이겼다는 사실을 곧바로 기억 보유 능력의 실패로 읽지 않겠다는 뜻이다.

그 대신 얻을 수 있는 주장은 더 좁고 명확하다. **한정된 상태는 얼마나 담는가, 부하가 늘면 어떻게 실패하는가, 그 실패 양상이 문헌에서 가져온 예측과 맞는가.** 이후 `PAPER.md`와 `RESULTS.md`는 이 재설계가 무엇을 보였고, 그 성과가 다시 실제 검색으로는 왜 이어지지 않았는지를 기록한다.
