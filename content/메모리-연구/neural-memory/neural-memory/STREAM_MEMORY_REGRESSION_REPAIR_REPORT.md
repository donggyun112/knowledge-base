---
title: "Stream-memory regression repair — 2026-09-28"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `neural-memory/STREAM_MEMORY_REGRESSION_REPAIR_REPORT.md` · 수집 2026-10-16 · **로컬 미커밋 문서 사본** (원격 커밋과 동일하다고 보장하지 않음)
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# Stream-memory regression repair — 2026-09-28

## Status

Validation produced a learned candidate that preserves all 17 original
condition accuracies. Independent seed-7 testing confirms large new-wording
gains and recovery of the original revision condition, but finds five residual
accuracy regressions. Seed-17 replication rejected every learned checkpoint.
The candidate does not
yet qualify as a zero-regression replacement; original checkpoints remain
unchanged and have not been replaced.

The completed decision-margin follow-up improves simple retained recall by
one additional case, from 76.5625% to 77.34375%, but still falls below the
79.6875% original. It fails the predeclared regression adoption gate. **The
performance regression is reduced, not fully resolved.** The final eight
untouched values were not evaluated and remain available.

## Intervention

Starting from each `stream-rmt-revision-clean-seed{7,17}.pt`, preserve every
original adapter parameter bitwise and add four Q/V adapter ranks. A learned
sigmoid gate, computed from each projection's input hidden state, controls the
added branch. The successful validation candidate applies this branch to both
reading/text processing and writing. It is **not** a frozen-reader architecture.

The policy learns new future dialogue content with next-token cross entropy.
Old dialogue streams supply full-vocabulary teacher KL and history-state
distillation. Old gold-answer cross entropy has weight zero, so the objective
preserves the teacher's existing behavior, including mistakes. Neither fact
positions nor answer positions participate in the training loss. The teacher
is used only during training; inference runs one memory model.

Eight matched examples per batch share dialogue context and vary the stored
value. Both new and replay batches are sampled as complete eight-example
groups, preventing the batch from containing only one answer value for a
context. Four training cycles cover noise horizons 4, 8, 16, and 32.

The model still starts every dialogue with zero recurrent memory. Its state
remains 8 × 576 float32 values (18 KiB), with no external key/value database or
past-text cache. Added effective trainable capacity is 265,020 parameters;
original adapter capacity is 568,513 parameters.

## Selection and data boundaries

- 256 adaptation values, 32 validation values, and 32 previously untouched
  test values; all three sets have disjoint token IDs.
- Original 192 previously tested values remain regression data, not fresh data.
- Selection observes only 17 validation conditions, allowing **zero** accuracy
  decrease in each condition. Among eligible checkpoints, maximize worst
  full-vocabulary accuracy, then minimize mean answer NLL.
- Each seed has a fixed 200-step, batch-8 protocol, validation every 50 steps,
  learning rate 0.0002, KL weight 128, state weight 40, and replay-CE weight zero.
- Seed-17 replication was launched before reading seed-7 test results. Test
  results must not change the checkpoint, hyperparameters, or selection rule.
- Independent evaluation compares the selected checkpoint and matched original
  reference on exactly the same streams, without gradient updates. Fresh tests
  use two draws per value, covering both 8- and 16-turn noise horizons.

The vocabulary comes from MSC training-word frequencies. Training dialogues
are controlled synthetic dialogues, **not** real MSC conversation training.
Unseen values are unseen by adaptation, not necessarily by the pretrained LM.

## Trials that did not solve the regression

| Trial | Selected checkpoint | Outcome |
| --- | --- | --- |
| Uniform / Q/V-versus-interface delta interpolation, seeds 7 and 17 | Small deltas | Old validation preserved, but new `now` accuracy remained zero |
| Added rank, ungated shared processing | Step 0 | Learned candidates regressed; original fallback only |
| Added rank, suffix-only writing | Step 0 | Old validation regressed; original fallback only |
| Conditional suffix-only writing | Step 0 | Gating alone did not preserve old accuracy |
| Conditional writing, matched batch 8, old CE + KL/state | Step 50 | Old validation preserved, but new `now` accuracy remained zero |
| Conditional writing, matched batch 8, teacher-only old loss | Step 50 | Same zero-new-accuracy limitation |
| Keep learned gates while shrinking writing deltas | Small deltas | Preserved old validation, but new `now` accuracy remained zero |

A privileged diagnostic forced the original write gate open on annotated
source chunks. This did not fix `now`, and damaged an ordinary correction
condition. Therefore a simple always-open write gate is not a demonstrated
fix. This diagnostic is neither training supervision nor runtime routing.

## Seed-7 validation result

`stream-rmt-protected-shared-gated-seed7.pt` was selected at step 150, not the
final step 200. All 17 validation conditions preserved their original
full-vocabulary accuracy. Mean answer NLL decreased from 4.36914 to 3.09793.

| Condition | Original | Selected |
| --- | ---: | ---: |
| `now` | 0% | 71.875% |
| `now_competing` | 0% | 43.75% |
| `revision` | 75% | 75% |
| Worst condition across all 17 | 0% | 40.625% |

`stream-rmt-protected-shared-gated-seed7-training-audit.json` independently
verified all original parameter slices, regenerated input hashes, exact
sampling/token budgets, and validation-only selection. Across 200 steps,
14,240 new future-content tokens and 13,536 replay future-content tokens were
processed. Replay tokens are KL targets, not old-gold-CE optimization targets.

## Verification

### Seed-17 replication

Under the same fixed 200-step protocol, no learned checkpoint satisfied the
17-condition validation guard. Step 150 reached 78.125% on `now`, 40.625% on
`now_competing`, and preserved revision at 87.5%, but regressed
`changed_competing`. The selected checkpoint is therefore step 0, bitwise
identical to its original-reference fallback. It is not a successful learned
repair. Its training audit independently verified this fallback, old slices,
input hashes, and sampling budgets (14,616 new and 12,552 replay future tokens).

### Seed-7 independent test

Seed-7 independent evaluation used 2,272 dialogue cases per checkpoint across
33 conditions. Both reference and selected adapter tensors remained bitwise
unchanged, and training steps during evaluation were zero. The paired audit
verified identical input hashes and reports **both** all-condition and legacy
preservation as false.

| Test condition | Original | Selected |
| --- | ---: | ---: |
| Fresh `now` | 4.6875% | 82.8125% |
| Fresh `now_competing` | 0% | 62.5% |
| Legacy correction | 82.8125% | 84.375% |
| Legacy revision | 77.34375% | 78.90625% |
| Legacy other-fact recall | 73.4375% | 73.4375% |
| Legacy simple retained recall | 79.6875% | 76.5625% |

All five negative full-vocabulary accuracy differences, without omissions:

| Condition | Difference | Net fewer correct |
| --- | ---: | ---: |
| Fresh revision | −1.5625 percentage points | 1 of 64 |
| Fresh other-fact recall | −1.5625 points | 1 of 64 |
| Fresh incidental mentions | −1.5625 points | 1 of 64 |
| Legacy neutral | −0.78125 points | 1 of 128 |
| Legacy simple retained recall | −3.125 points | 4 of 128 |

Deleting memory gives 0% full-vocabulary accuracy on both fresh `now`
conditions; swapping memory gives 0% too. This supports an actual
dialogue-specific memory contribution rather than simply guessing familiar
values. Answer-group bootstrap intervals for gains are [59.375, 93.75] points
for `now` and [18.75, 93.75] for `now_competing`. These intervals have only four
independent answer groups. The retained-recall change interval includes zero,
but that does not convert an observed regression into a preservation pass.

The 32 fresh values are now consumed by this independent test. Subsequent
tuning must treat these as regression data and must reserve new untouched
values for a new independent claim.

All 711 repository tests pass, including actual AdamW preservation, causal
writer/read separation, shared-processor behavior, annotation-independent
losses, future-target exclusion from history-state loss, and bitwise recurrent
checkpoint reload parity for the selected architecture. One pre-existing
requires-grad scalar-conversion warning remains.

### Decision-boundary follow-up (completed and rejected)

KL/state preservation did not prevent a few argmax changes. The follow-up adds
a teacher-only margin loss on **all replay future content tokens**, not an
answer-position mask. For each token, preserve the teacher's argmax against
the largest competing student logit, targeting `min(teacher margin, 0.1)`.
The loss is zero at the original model, uses the same tie-breaking argmax as
evaluation, detaches teacher logits, and never consults gold answer identity.
The old model's incorrect decisions are protected too: this is retention,
not improved replay-ground-truth training.

Both seeds restart from the original clean baseline. All previous settings
and 200-step budgets are unchanged; the added decision-loss weight is 64.
Checkpoints remain validation-selected. No training occurs in inference and
no second model is required at inference.

Seed 7 completed all 200 steps and selected step 150, preserving all 17
validation conditions with worst accuracy 40.625% and mean answer NLL 3.09718.
The independent training audit passed with identical sampling/token budgets
to the preceding seed-7 trial. Running two gradient-heavy batch-8 jobs caused
memory pressure and much slower progress, so the seed-17 follow-up was stopped
and execution switched to one training job at a time. There is **no completed
seed-17 decision-margin result**, and its partial validation is not reported
as replication. Original checkpoints and completed trial artifacts were not
deleted.

`stream-rmt-decision-manifest.json` reserves the final eight untouched values
from the **same** shuffled 512-word pool, excluding all 224 earlier test values
and preserving train/validation/probe splits. This small final set cannot
support a broad generalization claim. The earlier 32-value test is regression
data for this follow-up, not a newly independent test.

Before any follow-up performance test, fix the adoption gate as follows:
the validation-selected checkpoint must contain nonzero learning, preserve
all 33 conditions on the already-seen 32-value regression suite, and improve
both `now` conditions by at least 25 percentage points over its matched
reference. Only a candidate satisfying this gate is evaluated on the final
eight untouched values. No checkpoint/alpha is selected using either suite;
a failed gate rejects the candidate rather than optimizing to that test.

The completed 2,272-case regression rerun found five negative conditions:
fresh revision, fresh other-fact recall and fresh incidental mentions each
lost 1/64; legacy neutral lost 1/128; legacy retained recall lost 3/128. Fresh
`now` and `now_competing` retained their gains at 82.8125% and 62.5%. Legacy
revision remained 78.90625%, above its original 77.34375%.

Compared with the preceding shared-gated candidate, the margin term recovered
one retained-recall case but did not eliminate the other regressions. The
paired regression audit verified read-only evaluation and identical inputs;
all-condition and legacy-preservation flags are both false. The final-eight
gate was therefore not reached. No additional seed-17 margin run or final
independent test was performed after this rejection.

Final artifacts:

- `local-data/stream-rmt-protected-decision-seed7.pt`: validation-selected
  learned candidate, **not** an adopted zero-regression replacement.
- `local-data/stream-rmt-protected-decision-seed7.json`: training/selection.
- `local-data/stream-rmt-protected-decision-seed7-training-audit.json`:
  protected slices, inputs, sampling and selection verification.
- `local-data/stream-rmt-protected-decision-seed7-regression.json`: all 33
  matched conditions, raw grouped predictions and controls.
- `local-data/stream-rmt-protected-decision-seed7-regression-audit.json`:
  paired differences and answer-group bootstrap intervals, including losses.

The lean-ctx skill kept reads and long experiment output bounded. CodeCanvas
did not index these experimental Python functions, so causal and loading
claims were checked by executable tests instead of unsupported graph claims.

## Limits

This is single-attribute token recall/update, not a complete general-purpose
memory model, real-human-dialogue E2E result, or automatic `NO_MEMORY`/return
timing decoder. Bitwise preservation of old parameters does **not** imply
preserved predictions; independent regression evaluation is required.
