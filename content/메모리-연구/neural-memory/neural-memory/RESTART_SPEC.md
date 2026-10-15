---
title: "Neural memory restart: falsifiable design v0"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `neural-memory/RESTART_SPEC.md` · 수집 2026-10-16 · **로컬 미커밋 문서 사본** (원격 커밋과 동일하다고 보장하지 않음)
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# Neural memory restart: falsifiable design v0

Status: research proposal, 2026-09-25. No model has passed these gates. This document
does not replace the earlier experiment ledger or erase its negative results; it
replaces the **architecture hypothesis** for the next experiment.

## Question and boundary

Can a separately trained neural memory model receive a continuing dialogue token
stream, start each new dialogue with no dialogue-specific information, change its
own state as the stream arrives, and affect later output only when that history
is useful?

The prior bounded-item model does **not** answer this. Its fixed four-token
addresses, explicit item admission/replacement, and match-triggered readout
hard-code much of the storage and retrieval strategy. The later MSC audit also
found that a whole-token gain could coexist with harm on utterance-content
tokens: format was the shortcut. Those results remain valid diagnostics of the
old model, not evidence for the new one.

Constraints for this restart:

- Input is token IDs from human dialogue, in chronological order. Only turn and
  session boundaries are supplied as structural markers; no tool syntax,
  retrieved embeddings, external vector index, or key/value facts are inputs.
- The shared, pretrained parameters `θ` may know how to learn. Episode-local
  memory `M₀` contains no information about that dialogue. "Empty" refers to
  the latter, not to an untrained network.
- Internal real-valued activations are unavoidable in a neural network. They
  are not an externally computed semantic embedding store or one key/value
  record per utterance.
- A model that always writes, always reads, or only learns formatting does not
  satisfy the question, regardless of overall token likelihood.

## Target interface versus first measurable interface

The intended final memory model takes the prefix `x₁…xₜ` and returns updated
memory plus either `NO_MEMORY` or a bounded sequence of memory text tokens.
This is a **model output**, not an application-level retrieval call. Human
dialogue alone does not label the exact text that ought to be returned at each
moment, so claiming this final interface from next-token training would be
premature.

The first experiment uses a dense, directly measurable surrogate:

```text
input:  previous memory M(t−1), recent tokens c(t) = window(x(<t))
read:   activation a(t) ∈ [0,1], memory contribution Δlogits(t) ∈ R^vocab
write:  after prediction, observed token x(t) updates M(t) with strength w(t)
output: token logits of a frozen short-context predictor + Δlogits(t)
```

At a prediction step, read from `M(t−1)` **before** writing the gold `x(t)`.
Otherwise the memory can echo the target token. At final-session evaluation,
history writes are complete and writes are disabled while the clean final
session is scored. Recent final-session tokens remain available equally to all
conditions.

Passing this surrogate proves only that a learned memory state can supply
useful information at the right time. A subsequent text-token decoder and
`NO_MEMORY` decision must pass their own evidence-grounded tests before the
final interface is claimed.

## First architecture hypothesis

Use a **memory-only, RMT-inspired recurrent latent state** as the first arm.
RMT passes learned memory-token representations across sequence segments and
trains through that recurrence; it does not require a per-fact item schema
([Bulatov et al., 2022](https://arxiv.org/html/2207.06881v2)). We borrow that
principle, not its full language-model backbone.

Let `M(t) ∈ R^(K×d)` be a bounded episode state and `M₀ = 0`. A short-context
encoder processes a token block together with `M(t−1)`; its memory positions
propose `M̃(t)`. A learned scalar or per-position write strength gives
`M(t) = M(t−1) + w(t) ⊙ (M̃(t) − M(t−1))`. This is a continuous state update,
not a slot containing a token key and token value. Test equal-capacity versions
with `w = 1` and with learned `w`; sparse writing is a hypothesis, not a
pre-imposed victory condition. Within a block, content prediction uses a causal
mask and only the memory state from *before* that block; the proposed update
is committed after those predictions, so future tokens cannot leak backward.

A read network sees `M(t−1)` and recent tokens `c(t)`. Its contribution is
zero by construction when the memory is empty:

```text
r(t) = Readθ(M(t−1), c(t)) − Readθ(M₀, c(t))
Δlogits(t) = a(t) · Projectθ(r(t))
```

The subtraction is a null-state calibration, not a retrieval rule. It keeps
an unobserved person's memory from inventing a prior fact. Read activation
`a(t)` is learned; no exact-token match forces it on.

The comparison arm is a TTT-style fast-weight state, trained and evaluated
under the **same** token stream, frozen predictor, parameter/update budget,
and controls. TTT makes an internal model's weights the changing state and
learns its inner training task through an outer next-token objective
([Sun et al., 2024/2025](https://arxiv.org/html/2407.04620v4)). Its published
multi-view reconstruction objective is not adopted by default: it can optimize
reconstruction without future conversational utility. Titans is a reference
for persistent neural updates and forgetting, but its associative key/value
loss and gradient-based surprise are not assumed to identify useful dialogue
memories ([Behrouz et al., 2025](https://arxiv.org/html/2501.00663v1)).

## Training episode and loss

One episode is one speaker pair across multiple sessions. Reset `M` between
pairs, never between that pair's sessions. Group all sessions of a pair in the
same split. The development corpus is human-human Multi-Session Chat (MSC),
which uses role-played personas and therefore is not a sample of organic
private chat ([Xu et al., 2022](https://aclanthology.org/2022.acl-long.356/)).

History sessions update memory. A later clean session supplies the delayed
learning signal. The frozen predictor sees only a fixed recent-token window;
it cannot read the old sessions directly. Its parameters are identical in
carried-memory, blank-memory, and swapped-memory conditions. Train only the
memory module and its output adapter. Every target position is strictly
causal, and only **human utterance content tokens** enter the primary loss:

```text
L_content = mean_{t∈content} −log pθ(x(t) | c(t), M(t−1))
L_train   = L_content + λread · mean a(t) + λwrite · mean w(t)
```

The penalties give the model a reason to stay silent and conserve updates,
but their weights are tuned on development data and compared against the
unpenalized arm. Neither future recurrence nor a gold "store this" label is
present at inference. Start with short cross-session gaps that fit full
backpropagation through the memory updates; lengthen gaps only after the
mechanism works. Detaching state before the relevant evidence would destroy
the delayed learning signal.

MSC has relatively sparse exact repetition. Therefore whole-session average
loss is a safety metric, not the sole success metric. A diagnostic set must
also cover references to earlier facts, paraphrases, corrections, unrelated
interleaved turns, and cases where no prior fact is relevant. Evidence labels
can define *evaluation strata*; they must not become write-time inputs. The
previously inspected MSC test set is a legacy diagnostic, not a fresh final
holdout for a new headline claim.

## Three predeclared falsification tests

Use paired comparisons by speaker pair, not by token as if tokens were
independent. Before each full run, estimate the number of pairs needed for a
cluster-bootstrap interval narrow enough to distinguish the smallest useful
effect. The provisional action threshold is **0.02 nats per content token**;
if the 95% paired interval spans both material benefit and material harm,
the result is inconclusive, not positive or negative.

1. **Causal, user-specific memory.** On the same future content tokens,
   `carried` must beat both `blank` and `other-pair swapped` memory. Report
   per-pair `NLL(blank) − NLL(carried)` and
   `NLL(swapped) − NLL(carried)`, including intervals and the fraction of pairs
   helped. A gain from any nonempty state is not personal memory. First verify
   that the frozen predictor plus adapter can use an oracle evidence signal;
   otherwise the instrument cannot judge memory quality.
2. **No format shortcut.** Score utterance content and format/boundary tokens
   separately. Randomize innocuous session/turn formatting at evaluation and
   keep the content score paired. If total-token gain disappears on content,
   or follows the formatting rather than the historical facts, the arm fails.
   This is the direct guard against the previous MSC result. NoLiMa similarly
   motivates removing easy lexical overlap in a separate paraphrase stratum
   ([Modarressi et al., 2025](https://arxiv.org/abs/2502.05167)).
3. **Write/read timing under interference.** For each history turn, compare
   later content loss with its write enabled versus causally suppressed,
   replaying the identical remaining stream. Useful interventions should be
   enriched among high `w` decisions, harmful or irrelevant turns among low
   ones. Suppress a read at the future point to check that high `a` actually
   helps then. Repeat with intact unrelated-turn distractors and with an old
   fact explicitly corrected; the model must not recover the obsolete fact
   merely because it was repeated earlier. LongMemEval's update and abstention
   categories are useful external checks, not proof of this neural mechanism
   ([Wu et al., 2024](https://arxiv.org/abs/2410.10813)).

## Decision gate

Do not add a larger state, a text decoder, or a more elaborate forgetting rule
until the first arm passes the content-only carried/blank/swapped test and the
oracle instrument check on genuinely held-out people. If it fails, report
which gate failed and compare the equally budgeted TTT arm before proposing
another architecture. A result on the already-inspected MSC test split is
exploratory; a confirmatory claim needs a new, untouched pair-level holdout.
