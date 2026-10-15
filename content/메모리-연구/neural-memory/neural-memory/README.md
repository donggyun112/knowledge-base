---
title: "신경 메모리 모델·실험 안내"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `neural-memory/README.md` · 수집 2026-10-16 · **로컬 미커밋 문서 사본** (원격 커밋과 동일하다고 보장하지 않음)
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# Neural memory experiment

A graph-free test of whether a small model can learn **what to write into its own changing
parameters** from delayed recall utility.

This is intentionally not integrated with keymem's key/value graph or an LLM. Phase 0 isolates the
write-selection mechanism:

```text
observation (key, value, noisy evidence)
        │
        ├─ learned gate + surprise
        ▼
matrix-valued fast weights W(t)     ← the memory
        │
future query ───────────────────────► recalled value
```

The synthetic task supplies observations, many of which are distractors. Only a subset is queried
later. The model never receives a direct `write` label; future recall loss trains the write gate.
Because the fast-weight dimension is deliberately smaller than the number of possible bindings,
writing every distractor creates interference.

## Token-stream plastic memory prototype

`TokenPlasticMemory` receives token IDs directly. It has no vector store, memory
slots, nearest-neighbour search, or explicit retrieval call. Each observed token
transition updates one episode-local fast-weight matrix, and the current token
automatically stimulates that matrix while predicting the next token.

```bash
uv run python train_token_memory.py
```

The synthetic language task randomizes key-to-value token transitions in every
episode, so slow parameters cannot memorize the answers. Training uses only
next-token cross-entropy: pair identities, prior exposure counts, memory-write
labels, and activation targets remain outside the model. Accuracy and internal
memory activity are reported after each prior exposure, together with a
memory-disabled ablation.

Across 600-step runs with seeds 7, 17, and 29, repeat prediction accuracy was
1.000 in every run. First-exposure accuracy averaged 0.041, matching the 1/24
value-token chance rate, and disabling the fast weights reduced repeat accuracy
to 0.041. Mean internal activation rose from `0.214` with no prior exposure to
`0.433, 0.527, 0.560` after one, two, and three exposures. This establishes
online token-transition memory, not yet long-range or compositional language
memory.

### Context-conditioned token memory

`ContextualTokenPlasticMemory` adds a causal recurrent state before the same
fast-weight update. The benchmark presents raw token sequences of the form
`separator, context, key, value`; one key occurs in several contexts with
conflicting values, and every episode randomizes those values.

```bash
uv run python train_contextual_token_memory.py
```

Across 600-step runs with seeds 7, 17, and 29, repeat accuracy averaged 1.000
while first-exposure accuracy was 0.062, the 1/16 value-token chance rate.
Disabling fast weights gave 0.060 repeat accuracy; replacing every context with
one token gave 0.152. Mean internal activation rose from `0.235` with no prior
exposure to `0.456` and `0.531` after one and two exposures. This demonstrates
context-sensitive short token sequences, not yet unsegmented long-range natural
language.

### Unsegmented token stream

The next benchmark removes the separator and the reset operation. Events are
ordinary `topic, modifier, key, value` token runs concatenated into one stream;
the model receives only token IDs and carries its recurrent state continuously.
The trainable token lookup is an internal neural input layer, not a stored-memory
embedding index: there is no vector database, nearest-neighbour search, cue ID,
boundary label, or retrieval operation. The dynamic fast-weight matrix remains
the memory.

```bash
uv run python train_unsegmented_token_memory.py
```

Across 800-step runs with seeds 7, 17, and 29, repeat prediction accuracy was
1.000 in every run. First-exposure accuracy averaged 0.061, matching the 1/16
chance rate, and disabling fast weights reduced repeat accuracy to 0.061.
Replacing both context tokens with one constant reduced repeat accuracy to
0.161. Internal addresses for repeated instances of the same cue had mean cosine
similarity 0.999, versus 0.008 for different cues. Mean memory activation rose
from `0.194` before any prior exposure to `0.447` and `0.526` after one and two
exposures.

The no-reset forward path now runs the GRU, projections, and output heads over
the whole sequence, leaving only the causally dependent fast-weight update as a
token scan. On the current machine this reduced the seed-7 MPS runtime from
about 126 seconds to 58 seconds while preserving the metrics; CPU took about 51
seconds. `torch.compile` did not provide a second shortcut: `aot_eager` was
slightly slower and the installed Inductor backend failed to compile its Metal
source. MPS remains available with `--device mps`, while CPU stays the default
for this small model.

This establishes self-organized contextual recall in a continuous synthetic
token stream. It does not yet establish open-ended boundary discovery or
long-range natural-language memory: this first stream still has a fixed
four-token grammar and disjoint token classes.

### Variable-length token stream

The next task removes fixed event positions. Each occurrence is
`topic, [zero to three random fillers], key, value`; filler identity and length
change when the same cue reappears. Events are concatenated without separators,
padding, reset signals, recurrence labels, or retrieval calls.

```bash
uv run python train_variable_token_memory.py
```

Across 1,000-step runs with seeds 7, 17, and 29, repeat accuracy was 1.000 for
every seed and independently 1.000 at each filler count from zero through three.
First-exposure accuracy averaged 0.062, matching 1/16 chance, and disabling the
fast weights reduced repeat accuracy to 0.061. Replacing all topic and filler
tokens with one constant reduced it to 0.395; this ablation retains key tokens
and event length, so it is not expected to reach pure chance. Addresses for the
same cue observed at different lengths had mean cosine similarity 0.999, versus
0.010 for different cues. Mean activation rose from `0.102` before prior
exposure to `0.427` and `0.510` after one and two exposures.

This demonstrates length-invariant recall learned from next-token loss, but the
topic, modifier, key, and value vocabularies are still disjoint synthetic token
classes. Natural-language segmentation and much longer retention remain open.

### One shared token vocabulary

The shared-vocabulary task removes those role-specific token ranges. Topic,
filler, key, and value all draw from the same 24 token IDs, so one token can
serve several roles within a stream. Events retain the latent form
`topic, [zero to two fillers], key, value`, but there is no separator, padding,
reset signal, role channel, or lexical boundary marker. Unlike the earlier
benchmarks, training scores **every** next-token position; cue IDs, event roles,
and the value-position mask are used only for post-inference measurement.

```bash
uv run python train_shared_token_memory.py
```

Across 1,500-step runs with seeds 7, 17, and 29, mean value accuracy after zero,
one, two, and three prior exposures was `0.043, 0.496, 0.727, 0.804` while mean
memory activation rose `0.246, 0.325, 0.377, 0.401`. Overall repeat accuracy was
0.676, compared with 0.037 when fast weights were disabled and 0.100 when the
latent topic/filler positions were replaced by a constant. The first-exposure
result of 0.043 matches the 1/24 chance rate. Same-cue addresses across different
lengths had mean cosine similarity 0.844, versus 0.176 for different cues.

This is the first benchmark here where recall improves gradually rather than
immediately saturating. It shows latent contextual memory emerging from an
undifferentiated token vocabulary and an ordinary full-stream language-model
loss. The generator still has a synthetic event process and evaluation knows
the hidden roles; tokenized sentences, unknown episode duration, and interference
over much longer streams remain untested.

### Real BPE text stream

The next benchmark renders episode-random facts as English sentences and
tokenizes the continuous text with a cached Llama-3 BPE tokenizer. A fact appears
through four paraphrases such as `Mara's access word is copper`, `For Mara, the
access word is copper`, and `Remember that Mara uses copper`. Values are shuffled
every episode, so slow parameters cannot learn a person's answer. No pretrained
model or embedding is loaded: the external tokenizer only converts strings to
BPE IDs.

The 128K tokenizer vocabulary is reversibly compacted to the 43 raw BPE IDs that
can occur in this corpus. This avoids an irrelevant 128K output layer without
changing token boundaries or introducing role IDs. Training still scores every
next-token position; fact identities, value positions, exposure counts, and
paraphrase IDs remain evaluation-only metadata.

```bash
uv run python train_bpe_text_memory.py
# If the local cache is elsewhere:
uv run python train_bpe_text_memory.py --tokenizer-json /path/to/tokenizer.json
```

Across 1,800-step runs with seeds 7, 17, and 29, repeated fact-value prediction
was 1.000 in every run. First-exposure accuracy averaged 0.064, matching the
1/16 candidate-value chance rate; disabling fast weights reduced repeat accuracy
to 0.061, and replacing every fact prefix by a constant reduced it to 0.000.
Mean activation after zero, one, two, and three prior exposures was
`0.365, 0.535, 0.578, 0.588`. Addresses for the same fact across different
paraphrases had mean cosine similarity 0.987, compared with -0.027 for different
facts.

This verifies the mechanism on real subword tokenization and surface-level
paraphrases, not yet on an uncontrolled natural corpus. Sentence templates,
fact recurrence counts, and stream length are still generated deliberately;
only the model and full-stream loss are blind to that structure.

### Uncontrolled conversation stream

The next benchmark removes the sentence generator. It tokenizes local Claude
conversation history in memory, splits whole projects deterministically between
training and evaluation, and samples ordinary 256-token windows. Raw text is
neither printed nor persisted. The compact 2,048-token vocabulary covers 91.9%
of training tokens and 87.7% of held-out tokens across 188 training sessions and
125 evaluation sessions.

```bash
uv run python train_natural_bpe_memory.py
```

Evaluation finds exact `(four-token context, next token)` transitions that recur
inside a held-out window and excludes every transition that appeared anywhere
in training. These recurrence annotations are used only for measurement;
optimization remains full-stream next-token cross-entropy.

This stricter experiment currently gives a useful negative result. With seed 7
and 800 training steps, the untrained fast-weight mechanism reached 0.381 repeat
accuracy on 533 held-out occurrences. After training, repeat accuracy fell to
0.126, versus 0.087 with memory disabled: a net memory contribution of only
0.039. Full-stream loss improved from 7.471 to 4.452, so the model learned the
ordinary token distribution while damaging its online associative pathway. A
ten-times-lower learning rate did not preserve it (0.000 repeat accuracy).

Therefore this run does **not** demonstrate that storage timing emerged from
natural data. The fast weights start empty, but their delta-rule write behavior
is still an architectural prior, and ordinary language-model training can
overwrite the representation that makes it useful. The next architecture must
start with inactive learned write/read gates and train those gates without
letting the slow predictor dominate them.

### Initially inactive learned gates

`GatedContextualTokenMemory` addresses that failure by separating the slow
language predictor from the memory representation. Its write gate observes the
current token surprise, its read gate observes the recalled signal strength,
and both gates start at 0.05. Training first fits the slow pathway and freezes
it, then fits only the memory pathway. Both phases use every next-token target;
neither receives recurrence positions, exposure counts, or held-out labels.

```bash
uv run python train_gated_natural_bpe_memory.py
```

Across seeds 7, 17, and 29 (600 slow-path steps followed by 1,200 memory-path
steps), mean held-out repeat accuracy rose from 0.134 with the frozen slow
predictor to 0.218 with memory enabled, a consistent gain of 0.084. The mean
write gate grew from 0.050 to 0.260 and the mean read gate from 0.050 to 0.619.
Per-seed memory gains were `0.057, 0.113, 0.082`; all were positive. The gates
therefore begin effectively inactive and become useful from the ordinary token
objective on uncontrolled conversations.

This is partial rather than complete storage-timing behavior. Gate values are
not yet sharply selective between first and repeated occurrences, and some
highly repeated held-out transitions still fail under fast-weight interference.
The next target is selective allocation and collision control, not merely
stronger global gate activation.

### Competitive memory slots

The gated model can now hold several independent fast-weight matrices. A
straight-through router maps each causal token context to one slot, carries that
choice forward until the next token is observed, and spends the same single
write-gate budget in the selected slot. Retrieval routes the repeated context
back to one slot. A small label-free balance penalty on mean routing probability
prevents every context from collapsing into the same slot.

```bash
uv run python train_gated_natural_bpe_memory.py --num-slots 4
```

Under the same three seeds and `600 + 1,200` training schedule, four-slot repeat
accuracy averaged 0.301, compared with 0.218 for one slot and 0.134 for the
frozen slow predictor. The four-slot memory gain over the slow path was 0.167,
nearly twice the one-slot gain of 0.084. Effective slot use averaged 3.97 out of
4; on the two runs instrumented with recurrence routing, repeated copies of the
same transition selected the same slot 99.0% of the time.

This experiment increases fast-state capacity from `1×32×32 = 1,024` to
`4×32×32 = 4,096`, so the improvement is not a capacity-matched proof that
routing alone caused the gain. It does show that learned routing remains stable,
uses all four stores, and improves every seed without recurrence supervision.
Heavy repetition is still unreliable in sparse evaluation groups, so eviction
and capacity-matched routing remain open tests.

### Capacity-matched routing and learned eviction

The memory width can now differ from the slow predictor width. This permits a
direct fast-state capacity control: one 32×32 matrix and four 16×16 matrices
both contain 1,024 scalar state values while the slow predictor remains width
32. Under the same three-seed schedule, the capacity-matched four-slot model
reached 0.170 repeat accuracy and 0.037 memory gain, below the one-slot model's
0.218 and 0.084. It still used 3.98 of 4 slots and routed repeated contexts
consistently, but splitting each matrix too narrowly lost more associative rank
than routing recovered. The earlier four-slot improvement therefore depended
substantially on added capacity rather than routing alone.

An optional learned erase gate was also added. It observes the current context,
prediction surprise, and selected-slot norm before deciding whether to clear
that slot prior to a write:

```bash
uv run python train_gated_natural_bpe_memory.py --num-slots 4 --learned-eviction
```

On 256-token windows the mean erase gate fell from 0.010 to 0.00037 across
three seeds. On a 512-token pressure test it fell to 0.00016. Repeat accuracy
changed only slightly, and the learned operation erased less than 0.04% of a
selected slot. Thus the model rejected whole-slot eviction; this is not evidence
of learned forgetting. A useful successor needs local, association-level
replacement or a bounded item store rather than clearing an entire matrix.

### Bounded token-item memory

`BoundedItemTokenMemory` is that association-level successor. It begins with an
empty, fixed-size bank and binds a causal four-token key to the next token. Each
step can change at most one item. Empty items are used first; afterwards an
incoming association replaces an item only when its learned write priority is
higher than the stored priority. Reads attend over the occupied items and a
learned gate handles uncertain matches; when an occupied key crosses the exact
match threshold, recall activates directly. Thus the memory is inactive while
empty and becomes active only after relevant token experience accumulates. The
stored token uses a fixed codebook so training cannot silently change which
token an existing item represents.

```bash
uv run python train_gated_natural_bpe_memory.py \
  --memory-architecture bounded-items
```

The default bounded configuration uses 64 items of width 16, or 2,176 scalar
item-state values including keys, values, occupancy, and priority. The default
run trains the slow predictor but leaves the retention controller at its
empty-start initialization. Optional retention training uses 400 steps, whole
project groups for checkpoint selection, and a 0.56 write-rate budget. Future
recurrence is never an inference input, and every evaluation stream begins with
an empty item bank.

Two rejected variants are informative. A continuous 16-item update mixed new
associations into old values: its write gate rose to 0.798, same-recurrence
routing stayed near chance at 0.068, and repeat gain was only 0.003. Explicit
match reuse raised routing agreement to 0.679, but partial value mixing still
left only 0.0019 repeat gain. Discrete whole-item replacement fixed the value
corruption, while a local four-token key prevented the address from depending
on an arbitrarily long prefix.

Before match-triggered activation, three seeds produced only +0.0016 mean
repeat gain: the item bank often predicted useful tokens, but the learned read
gate stayed near 0.07. Match-triggered activation changed the result. Across
seeds 7, 17, and 29 after 600 slow-model steps, repeat accuracy averaged 0.322
versus 0.188 for the frozen slow path, a +0.133 gain. After adding causal past
match strength to the write controller, the 32-item implementation averaged
0.338 versus the same 0.188 baseline, a +0.149 gain. Individual gains were
+0.178, +0.096, and +0.174, so all three runs improved. The memory began empty
on every stream and received no memory-parameter training.

A capacity diagnostic then increased only the fixed item count from 32 to 64.
Across the same seeds, combined repeat accuracy rose from 0.403 to 0.607 and
memory-only accuracy from 0.309 to 0.657. Individual combined accuracies changed
from 0.434→0.671, 0.369→0.508, and 0.405→0.643. Accepted-source survival was
between 0.710 and 0.773 in all three runs. This robust +0.205 mean gain identifies
bounded retention capacity as the main 32-item bottleneck, so 64 items is now the
trainer default. It is still a fixed-size recurrent model state, not an external
store or a growing database.

An earlier 32-item controller-only experiment retained a positive result in
every seed but slightly reduced mean recall, which originally motivated an
untrained default. The later calibrated 64-item result below supersedes that
default without changing the empty-start inference behavior.

### Self-supervised retention experiment

The trainer now has an experimental retention-only phase. During training, an
association receives a positive delayed target when the same four-token
context and next token occur again later in that stream. The write model itself
sees only causal state: the current hidden state, prediction surprise, and how
strongly the context matched memory in the past. Future recurrence is never an
inference input.

```bash
uv run python train_gated_natural_bpe_memory.py \
  --memory-architecture bounded-items \
  --memory-steps 1200 \
  --item-training-objective retention
```

At priority decay 0.99, three seeds learned a clear ranking: mean write priority
was 0.487 for associations that would recur and 0.253 for other associations.
End-to-end repeat accuracy improved from 0.338 to 0.345 on average, but the
per-seed changes were +0.025, +0.028, and -0.031. Importance ranking therefore
learned, but its recall benefit was not robust enough to become the default.

Slower priority decay (0.995) raised seed-29 repeat accuracy from 0.335 to 0.547.
A write-budget-only control reached 0.528, however, and useful priorities were
not ranked above other priorities in that run. Most of the gain came from
globally suppressing writes and preserving items longer, not from learned
importance. At that stage retention training remained an explicit research
option rather than being presented as solved long-term storage.

### Next-recurrence survival credit

The stricter experimental objective follows every exact local association to
its immediately next occurrence. At that later point it applies memory-only
next-token loss, so gradient must pass through the intervening bounded-memory
updates back to the causal write controller. The controller still receives no
future token at inference time. This differs from the retention classifier:
the training signal now depends on whether the stored key and value actually
survive replacement and produce the right token, not merely on whether the
association appears again.

The first version exposed a frozen random memory-RNN state to the write gate.
The current version instead uses the trained slow model's causal hidden state,
the surprise of the just-observed token, and prior match strength. Zero-initial
gate weights preserve the same untrained memory behavior.

```bash
uv run python train_gated_natural_bpe_memory.py \
  --memory-architecture bounded-items \
  --memory-steps 1200 \
  --item-training-objective survival
```

Evaluation additionally reports the source-write acceptance rate, distance and
accepted writes before the next recurrence, exact-key match rate, memory-only
accuracy, and survival rate among accepted sources. A separate pressured rate
uses recurrences with at least one memory-bank capacity of intervening accepted
writes.

With 600 slow-model and 1,200 survival steps on seeds 7, 17, and 29, the direct
objective clearly learned its internal task. Mean next-recurrence memory-only
accuracy rose from 0.483 to 0.697, key-match rate from 0.429 to 0.715, and
correct survival among accepted sources from 0.630 to 0.727. Mean priority was
0.632 for associations that would recur versus 0.189 for other associations.
However, held-out repeat accuracy moved from 0.414 to 0.388; the seed changes
were -0.026, +0.008, and -0.060. Priorities became too large and favored
training-distribution recurrence at the expense of first-time held-out writes.
The delayed credit path therefore works, but its priority scale/generalization
does not.

Two follow-up controls separate scale from objective mismatch. An optional
`--item-write-priority-span` parameter confines learned priority to
`initial_gate ± span` while preserving the exact untrained value. With a 0.01
span, the seed-7 controller collapsed all priorities to the lower bound: it
preserved held-out accuracy but stopped improving next-recurrence recall. A
second `--item-write-controller-features scalar` control hid the token-specific
slow hidden state and exposed only surprise and prior match. It still improved
the internal recurrence task while reducing held-out repeat accuracy by 10.5
percentage points. Neither raw priority magnitude nor token-identity leakage is
the main failure.

The `admission` objective performs a stronger causal test. It samples one
candidate source per stream, forcibly accepts it in one rollout and rejects it
in another, then compares memory-only loss over every later recurrence. The
normal write gate is trained toward the intervention with lower downstream
loss, including its opportunity cost to other memories.

```bash
uv run python train_gated_natural_bpe_memory.py \
  --memory-architecture bounded-items \
  --memory-steps 400 \
  --item-training-objective admission
```

On seeds 7, 17, and 29, admission raised mean next-recurrence memory accuracy
from 0.439 to 0.661 and accepted-source survival from 0.563 to 0.766. Held-out
repeat accuracy nevertheless moved from 0.352 to 0.332; per-seed changes were
0.000, -0.074, and +0.012. Counterfactual credit removed the earlier failure on
seed 29 but did not generalize reliably. The untrained controller therefore
remained the default at that stage.

The next experiment adds that genuinely held-out criterion. Before memory
training, it deterministically partitions anonymized project groups: 75% train
the write controller and 25% supply controller-validation episodes. No raw
project name is retained. Associations seen in the controller-training groups
are excluded from validation scoring.
The slow predictor is pretrained on the full training corpus and then frozen, so
this is a strict holdout for controller optimization, not for base-language-model
pretraining.
At step zero and every 100 memory steps, the trainer evaluates the same held-out
windows. A checkpoint must beat step zero; an optional configurable binomial
standard-error margin can require a larger gain.
Step zero is a candidate, so an inconclusive or harmful controller is rolled back
instead of being kept. The original eval projects remain untouched for the final
measurement.

```bash
uv run python train_gated_natural_bpe_memory.py \
  --memory-architecture bounded-items \
  --memory-steps 400 \
  --item-training-objective admission \
  --item-validation-fraction 0.25 \
  --item-selection-interval 100
```

The bounded trainer now defaults to a 25% project holdout and a zero margin. The
earlier one-standard-error setting was too underpowered for its 63–139 repeated
validation positions and rejected every later cross-seed improvement. This is
model selection, not an inference feature: deployed memory still sees only the
causal token stream.

On an initial session-level MPS rerun with seeds 7, 17, and 29, 600 slow steps,
400 admission steps, and 16 evaluation batches, all three validation splits
selected step zero. Mean
controller-validation repeat accuracy was 0.284 at initialization and 0.226 at
step 400. Restoring the selected checkpoints kept final held-out repeat accuracy
exactly at its post-slow baseline (0.394 to 0.394); next-recurrence memory
accuracy likewise remained 0.445. The criterion therefore detects and rejects
the non-generalizing admission updates, including the seed-17 failure, but does
not yet learn a better storage policy. This is a safety result, not a solution to
learned long-term-memory selection.

### Direct episodic controller objective

The `episodic` objective applies the held-out criterion itself to controller
training windows instead of translating it into a retention or admission label.
Because discrete replacement decisions make ordinary gradients unreliable, it
uses a simultaneous-perturbation estimate: the same causal token episode is run
with positive and negative perturbations of the small linear write gate, and the
difference in end-to-end cross-entropy at actual repeat positions estimates the
update direction. Recurrence annotations only choose training loss positions;
they are not inputs to either perturbed model or to inference. Whole validation
project groups remain separate for checkpoint selection, and the original eval
split remains untouched.

```bash
uv run python train_gated_natural_bpe_memory.py \
  --memory-architecture bounded-items \
  --memory-steps 400 \
  --item-training-objective episodic \
  --item-episodic-perturbation 0.05 \
  --item-validation-fraction 0.25 \
  --item-selection-interval 100
```

A first session-random episodic split was misleading: all three seeds selected
trained checkpoints, while final repeat accuracy fell from 0.403 to 0.374 on
average. Sessions from the same project could occur on both sides of that split.
The current corpus therefore carries only an anonymized stable project-group ID
and holds out entire projects. It also requires a one-standard-error improvement
over step zero (`--item-selection-z-score 1.0`).

With project-heldout selection on the same seeds and training budget, seed 7
and seed 29 rolled back to step zero. Seed 17 retained step 300 after validation
repeat accuracy rose from 0.180 to 0.281. Final repeat accuracies were
respectively 0.434→0.434, 0.369→0.369, and 0.405→0.405, leaving the three-seed
mean exactly unchanged at 0.403. Mean memory-only repeat accuracy did rise from
0.309 to 0.326, but the combined predictor gained nothing. This is stronger than
universal rollback—the system accepted one statistically supported learned
controller—yet it still does not demonstrate improved end-to-end long-term
memory.

### Causal read arbitration

The bounded model also has an optional learned residual on top of exact-match
reading. At each token it observes only six current quantities: retrieval and
match strength, the slow and memory predictors' maximum probabilities, the slow
probability assigned to the memory prediction, and whether their argmax tokens
agree. The residual is initialized to zero, so enabling it initially reproduces
the exact reader. No recurrence annotation or future token is an inference
input. The `fusion` objective freezes every other parameter and minimizes
end-to-end loss at repeated positions through this residual.

```bash
uv run python train_gated_natural_bpe_memory.py \
  --memory-architecture bounded-items \
  --item-read-arbitration learned \
  --item-training-objective fusion \
  --memory-steps 200 \
  --item-validation-fraction 0.25 \
  --item-selection-interval 100
```

New diagnostics compare the combined predictor with the slow path, memory path,
and an oracle that is correct whenever either individual path is correct. They
also report how often combined prediction realizes a possible memory rescue or
destroys a correct slow prediction. On seed 17 before fusion training, repeat
accuracy was 0.205 slow-only, 0.230 memory-only, 0.369 combined, and 0.385 oracle.
The exact reader already realized 20 of 22 possible rescues and caused none of
19 possible harms. Read arbitration was therefore not the main bottleneck.

An exploratory zero-margin three-seed selection changed mean combined repeat
accuracy from 0.403 to 0.408: seed 17 improved by 0.016, while seeds 7 and 29 did
not change. Memory-only accuracy rose from 0.309 to 0.319, but the combined-to-
oracle gap did not shrink in any seed. The learned read value also updates item
usage, so the seed-17 gain came through a changed later replacement history, not
through closing the immediate arbitration gap. Under the normal one-standard-
error rule every candidate is rolled back to step zero. Learned arbitration is
therefore retained as an experimental diagnostic, while the learned residual
remains disabled by default.

The combination rule itself was a separate bottleneck once capacity increased.
The old additive rule, `slow + read × memory`, left slow logits active even when
an exact match set `read` near one. The new default interpolates instead:
`slow + read × (memory - slow)`. Empty or uncertain memory stays near the slow
predictor, while an exact match switches to the recalled token distribution.
With 64 items, this raised three-seed mean repeat accuracy from 0.607 to 0.691.
Individual changes were 0.671→0.737, 0.508→0.574, and 0.643→0.762. The oracle
mean was 0.698; interpolation realized 97.6%, 97.8%, and 100% of possible memory
rescues, with zero observed harm to a correct slow prediction. Relative to the
former 32-item additive default, the total mean gain is +0.288. No memory
parameter training was used for either the capacity or interpolation result.

### Calibrated retention controller

The earlier retention loss used a 0.10 write-rate target even though the
64-item model's untrained write rate was roughly 0.46–0.57. That objective asked
the gate to learn recurrence value while simultaneously suppressing most
replacement. Raising the budget target to 0.56 preserves overall write volume
and lets the balanced delayed-recurrence loss learn which associations deserve
higher priority.

With project-heldout raw checkpoint selection, all three seeds selected a
trained checkpoint. Final repeat accuracies rose from 0.737→0.842,
0.574→0.697, and 0.762→0.869; the mean rose from 0.691 to 0.803. Mean
memory-only accuracy increased from 0.657 to 0.755 and accepted-source survival
from 0.747 to 0.839. Useful/other priorities separated to approximately
0.170/0.119, 0.169/0.124, and 0.204/0.136. All selected checkpoints came from
project groups disjoint from final evaluation, and inference still receives no
future-recurrence annotation.

This is a robust in-distribution project-heldout storage-selection result, but a
separate codeword stress test below shows that it is not yet a general storage
policy. Retention training therefore remains opt-in through `--memory-steps 400`.
A one-standard-error margin remains available through
`--item-selection-z-score 1.0` when a larger validation set makes that test
sufficiently powerful.

### Unseen codeword stress test

`eval_real_text_memory.py` constructs eight previously unseen readable-token
associations, presents each once, inserts enough distractor tokens to exceed the
64-item capacity, and then repeats each four-token cue. It reports slow-only,
memory-only, and combined first-answer-token accuracy without exposing local
history text.

```bash
uv run python eval_real_text_memory.py --device mps
```

On seed 17, the untrained memory controller recalled 4/8 associations while the
project-heldout retention controller selected at step 100 recalled only 1/8.
Slow-only accuracy was 0/8 in both cases. Thus the trained controller learned
useful recurrence regularities of the natural corpus but actively harmed novel
arbitrary-fact retention. This falsifies the stronger claim that learned storage
selection is solved; 64-item exact storage and interpolated recall remain the
default, while out-of-distribution storage learning is the next target.

A follow-up mixed 50% randomly generated shared-prefix codeword episodes into
retention training. Prefixes, cues, and answers changed every batch, so rote
memorization could not solve the task. The same stress test remained at 1/8;
the experiment was removed rather than retained as an ineffective option. The
next design needs an online salience state that can recognize repeated cue
structure inside the current stream, not only a corpus-trained linear priority.

An experimental `salience` controller now supplies the write gate with the
recurrent memory encoder's current hidden state, surprise, and previous-match
signal, and trains that encoder jointly with the gate. With the final retention
step evaluated directly (`--keep-final-memory-step`), paired untrained→trained
codeword recall was 3/8→7/8, 4/8→5/8, and 3/8→4/8 on seeds 7, 17, and 29. Mean
accuracy therefore rose from 41.7% to 66.7%, with no regressing seed. This is a
promising out-of-distribution result, but direct final-step evaluation cannot
decide safely whether a particular run generalized.

Checkpoint selection now combines four deterministic held-out token-association
episodes (32 facts total) with a natural-session guardrail. A candidate must
recall more held-out facts than step zero while keeping held-out natural repeat
accuracy within 3 percentage points of step zero. These associations affect
selection only, never gradients, and are distinct from the readable-codeword
test. On the same three MPS seeds the selector chose steps 400/0/0. Readable
codeword recall became 6/8, 4/8, and 3/8 versus untrained 3/8, 4/8, and 3/8, so
mean accuracy rose from 41.7% to 54.2% without a regressing seed. Seed 7's
selection probe improved 12/32→19/32 while natural repeat accuracy stayed just
inside the guardrail at 0.645→0.617. Seed 17's final state degraded both the
probe (15/32→14/32) and natural repeats (0.424→0.324), so it was correctly
rejected. Seed 29 improved the probe only 12/32→13/32 but missed the natural
guardrail at 0.508→0.460, so it was also rejected.

This makes experimental training safe to evaluate automatically, but only one
of three runs produced an acceptable learned controller, so it remains opt-in.
Adding ordinary next-token loss to the retention objective was also tested on
the failing seed at weights 0.1 and 1.0. The final natural/probe results were
0.345 and 14/32, then 0.281 and 15/32; neither met both criteria, so that
ineffective option was removed.

Further seed-17 ablations tested whether the retention classifier merely used
the wrong ranking or checkpoint scale. A within-stream pairwise priority loss
raised the final association probe from 15/32 to 16/32, but natural repeat
accuracy fell from 0.424 to 0.309. Checking every 20 rather than every 100 steps
found no missed checkpoint: step 20 improved natural repeats to 0.446 while the
probe fell to 14/32. Weighting priority by next-recurrence distance finished at
0.345 and 13/32. Mixing 50% freshly generated association streams finished at
0.281 and 9/32. A controller with three-token surprise history reached 14/32
from a 12/32 initialization, but natural repeats fell from 0.446 to 0.331; a
10x lower learning rate preserved natural repeats at 0.439 but reduced the probe
to 10/32. Freezing the shared key embedding and restricting the controller to
scalar surprise/match features also failed the joint criterion. All checkpoints
were safely rolled back to step zero, and these ineffective options were removed.
The consistent failure is objective-level: natural recurrence supervision favors
training-distribution repetition rather than transferable first-write value.

A conservative counterfactual follow-up replaced the 56% write-budget target
with a trust-region anchor to the initial 5% policy. On the failing MPS seed 17,
anchor weights 1.0 and 0.1 preserved natural repeat accuracy but never improved
the 15/32 held-out association baseline (the weaker anchor fell to 14/32).
Training half the steps on fresh delayed-repeat episodes with independent random
four-token contexts also failed: natural accuracy reached 0.446 while the probe
never exceeded 15/32. Restricting each counterfactual reward to the selected
fact's immediate next recurrence finished at 0.453 natural accuracy but 14/32
probe recall. Every run therefore restored step zero, and the experimental code
was removed. This exposes a causal limit rather than another tuning issue: on a
fact's first occurrence, an arbitrary future-useful fact is indistinguishable
from an arbitrary distractor. The next design should admit broadly while space
is available and learn retention or eviction only after reuse evidence appears,
instead of trying to predict unknowable first-write value.

That successor is available as `--item-retention-policy evidence`. It fills
empty items before considering replacement, admits novel associations without
asking a first-write classifier to predict their future, initializes their
retention evidence at zero, and increments only the item reached by an exact
later recurrence. The evidence decays and enters the bounded replacement
router, so storage still has fixed size and the router can be trained through
the delayed recall loss. `eval_deferred_retention.py` separates the impossible
one-shot case from this gradual-activation case. On MPS seeds 7/17/29, the
evidence policy recalled 18/32, 15/32, and 19/32 facts after one exposure, then
28/32, 30/32, and 32/32 after one recurrence before the same capacity pressure:
mean recall rose from 54.2% to 93.8%. This does not claim clairvoyant one-shot
retention; it demonstrates that continued token input supplies causal evidence
that changes later eviction.

The evidence router receives real gradients from the recurrence loss. An E2E
MPS run over the local Claude history used 189 training sessions, split the
memory phase into 160 training and 29 validation sessions, and reserved 126
sessions for final evaluation. No raw text was persisted. On seeds 7/17/29,
all selectors chose step 300 while holding their reuse probes at 30/32, 28/32,
and 28/32. Memory-validation repeat accuracy improved from 0.505→0.579,
0.568→0.604, and 0.619→0.635. Across the 282 final held-out repeat events,
slow-only prediction was correct on 55 (19.5%), the untrained evidence memory
plus slow model on 219 (77.7%), and the selected learned router on 221 (78.4%).
Per-seed final repeat accuracy moved 0.842→0.829, 0.738→0.730, and
0.774→0.821. Accepted-source survival averaged 0.652→0.666, while survival
under capacity pressure was effectively flat at 0.424→0.423. The E2E memory
effect is large, but the learned eviction increment is only two extra correct
repeat events and is dominated by seed 29; consistent per-seed generalization
is not yet established.

The selector now partitions memory-validation project groups into three folds,
requires pooled natural-repeat improvement, and rejects a checkpoint when any
fold regresses by more than 3 percentage points. It also reports replacement
coefficients and evaluates every eviction policy on identical final windows.
The first safe learned-router run scored 218/282 (77.3%), versus 219/282
(77.7%) before router training, while usage-only eviction scored 179/282
(63.5%). Ten random draws per seed then averaged 2,290/2,820 (81.2%); all ten
cross-seed pooled draws beat the learned policy. This established that controlled
turnover, rather than stronger high-usage protection, was the missing signal.

Each item now carries a recurrent age scalar. Pure LRU and a continuous
usage-plus-LRU score raised natural-session recall to 267/282 (94.7%) and
269/282 (95.4%), but both collapsed to 0/32 on the delayed association probe:
they were excellent recent-context caches, not long-term memory. The final
`evidence_lru` policy therefore treats exact recurrence as a discrete promotion.
Unconfirmed items turn over by age; a confirmed item is protected before age is
considered. On Claude-history MPS seeds 7/17/29 it scored 72/76, 119/122, and
77/84 natural repeats, or 268/282 (95.0%) pooled, while preserving the learned
policy's delayed-probe scores exactly at 30/32, 28/32, and 28/32 (86/96,
89.6%). A 62-item capacity control used 2,170 recurrent scalars, six fewer than
the old 2,176-scalar state, and still reached 267/282 (94.7%) with the related
usage-plus-LRU policy; the gain is therefore not explained by the 64 age
scalars added to the default 64-item model. Bounded-item runs now default to
evidence retention plus `evidence_lru`. At this stage the safe selector restored
step zero, so these retention gains came from causal online memory dynamics rather
than controller fitting.

`eval_confirmed_capacity.py` now tests the point where confirmed associations
outnumber the fixed item pool. The study stream writes only each fact's
`cue -> answer` transition, repeats it causally before applying pressure, and
clones the same post-study recurrent state for every read-only query so neither
query order nor query-time writes can change the score. With 64 items, 32
interference tokens repeated twice, and MPS
seeds 7/17/29, the original 0.95 match threshold and 0.05 read temperature
recalled 77/96, 162/192, and 159/288 facts at loads of 32, 64, and 96. The loss
below capacity came from different token contexts being treated as the same
match and from soft reads mixing nearby items, not from eviction alone. A fixed
0.97 threshold and 0.02 temperature raised those scores to 94/96, 187/192, and
189/288. At 96 facts the target-only 64-item ceiling is 192/288, before accounting
for any slots occupied by the pressure stream; the model reached 189/288 overall
and 178/192 within the newest 64-fact window.

The stricter matcher was then checked on the actual Claude-history E2E path,
not selected on the synthetic probe alone. Natural-session recall stayed
exactly at 72/76, 119/122, and 77/84 (268/282 pooled), while the independent
delayed-association probe improved from 30/32, 28/32, and 28/32 to 32/32,
32/32, and 30/32 (94/96, 97.9%). The bounded-item model and CLI therefore now
default to a 0.97 match threshold and 0.02 read temperature. Evaluation also
runs the delayed probe when memory-training steps are zero, so a step-zero
model can no longer omit the long-term-recall guardrail from its report.

A remaining diagnostic isolated the collision pattern. In one 1,012-context
Claude-history batch, no distinct context exceeded the 0.97 match threshold.
But among 96 synthetic contexts sharing the first three tokens and differing
only in the fourth, 10 contexts had a wrong neighbor above 0.97. The key path
was therefore underweighting some token positions even though ordinary natural
contexts looked separated.

The bounded model now learns that key path directly from token contexts. For
each observed four-token training context, one position at a time is replaced
with another observed token; the token embedding and key projection are trained
to put the resulting different context below a 0.90 similarity margin. This is
self-supervised training on current tokens, uses no future recurrence label, and
does not add a database or persistent store. The recurrent item state still
starts empty. Storage, promotion, and eviction rules are unchanged.

After 300 MPS steps on the Claude-history training split, seeds 7/17/29 improved
the standard confirmed-capacity benchmark from 94/96 to 96/96 at 32 facts and
from 187/192 to 189/192 at 64 facts. At 96 facts, total recall stayed at 189/288
because the oldest facts are beyond the 64-item bound, while recall inside the
newest 64-fact window rose from 178/192 to 189/192. On the independent
Claude-history E2E evaluation, natural repeat recall remained exactly 72/76,
119/122, and 77/84 (268/282), and delayed association recall rose from 94/96 to
96/96.

Bounded-item training therefore now defaults to 300 matching steps. Checkpoint
selection requires a strict confirmed-capacity gain, no delayed-association
regression, and natural-repeat performance within its held-out guardrails. The
per-fold tolerance is scaled by fold sample size for this objective so a change
of a few examples in a small fold is not treated as certain regression. Across
the three default-selection runs, held-out capacity rose from 148/160, 154/160,
and 157/160 to 158/160 in every seed. Held-out delayed recall moved from
32/32, 32/32, and 30/32 to 32/32 in every seed, while pooled natural validation
was unchanged at 254/337, 326/417, and 147/224. The selector chose steps 300,
100, and 100; final natural evaluation remained 72/76, 119/122, and 77/84.

The remaining 63/64 pattern was then decomposed at the item-state level. The
evaluator now reports whether each target value physically exists after study,
the hard nearest-item prediction, soft-read-only failures, non-target occupancy,
and any target lost while querying. Across the standard three-seed probe, every
post-matching miss was already absent from state: hard and soft recall agreed,
there were zero soft failures with a present target, and read-only queries lost
zero targets. With 32 repeated distractors, one slot per trained run holds a
non-target pressure association, leaving a pressure-adjusted fact ceiling of
63/64. The trained matcher reaches that ceiling at 64 facts and in the newest-64
window at 96 facts; this is not a remaining read-temperature defect.

An experimental `evidence_admission` policy now gives the learned write
priority a narrowly scoped causal role. Empty slots and exact matches still
write automatically, and unconfirmed candidates can still turn over. Only
when the selected slot is already occupied and confirmed does a novel
association need to exceed the admission threshold. This preserves the
evidence memory's cold-start behavior while allowing the neural controller to
refuse low-value replacement after capacity is full. Capacity probes can leave
the pressure writes automatic, so this decision is measured rather than
forced.

Admission supervision predicts future recurrence from the information
available at write time. The counterfactual objective now trains the continuous
write priority instead of the hard straight-through decision. Checkpoint
selection uses the held-out gap between priorities for recurring and one-off
associations, while requiring no regression in one-off-pressure capacity,
delayed association recall, or natural-session recall. Matching and admission
can be run sequentially with `--item-admission-steps`; their parameters and
selectors remain separate.

Full Claude-history MPS runs on seeds 7/17/29 selected matching steps 300, 100,
and 100, then admission step 100 in every run. The held-out recurring-minus-
one-off priority margins increased from approximately zero to 0.0182, 0.00869,
and 0.01281 while one-off-pressure capacity stayed at 160/160, delayed recall
stayed at 32/32, and natural validation stayed at 254/337, 326/417, and 147/224.
Later admission checkpoints produced larger margins but lost between two and
four guarded capacity events, so the selector rejected them. Final natural
recall remained 72/76, 119/122, and 77/84. In every seed, read-only capacity
after both phases was 32/32 at 32 facts, 64/64 at 64 facts, and 64/64 in the
newest window at 96 facts under automatic one-off pressure. A focused
intervention test now confirms the post-admission transition itself: an
above-threshold novel item receives its learned priority as provisional usage,
then survives a following below-threshold candidate until recurrence. This
reuses the existing item state rather than adding another recurrent scalar.

The stricter held-out test now exists. It first fills all 64 slots with confirmed
items, presents 16 recurring and 16 one-off associations sampled from held-out
Claude sessions, leaves each source admission automatic, and replays the real
intervening tokens through the next recurrence. Threshold calibration maximizes
useful admission-and-survival minus one-off admission while retaining the
natural-recall, delayed-recall, per-fold, and automatic-pressure capacity
guardrails. Ordinary evaluation also reports the fraction of each class that is
actually above the active boundary, instead of relying on class means alone.

The seed-7 MPS result is informative but still negative overall. At the original
0.5 boundary, neither class entered a full confirmed memory. At a candidate
boundary of 0.277, 2/16 useful associations were admitted and both survived to
their real next recurrence, while 1/16 one-off associations entered. Natural
held-out recall remained 0.7537 and delayed recall remained 32/32, but automatic-
pressure capacity fell from 160/160 to 136/160. The guardrail therefore rejected
the candidate and restored 0.5. This is the first real-history evidence that the
learned admission transition can admit and preserve a useful replacement, but
the controller's ranking is not yet reliable enough to lower the boundary safely.
The next optimization target is full-state decision utility under pressure, not
further threshold lowering or a longer unguarded training run.

The full-state objective now fills and confirms every slot before sampling a
decision, then rolls the remaining natural stream forward twice with that item
forced accepted and rejected. Its soft target combines the candidate's real
next-recurrence gain with collateral gain or loss on other repeated
associations; one-off candidates target rejection. On seed 7 this increased the
guarded admission margin monotonically from approximately zero to 0.00459,
0.02232, and 0.05101 at steps 100/200/300 while preserving 160/160 capacity,
32/32 delayed recall, and 0.7537 natural validation at the active 0.5 boundary.
At a calibrated 0.304 boundary, 4/16 useful items entered and 3 survived while
2/16 one-offs entered, improving decision utility to 0.0625, but 35.5 mean
intervening writes reduced capacity to 140/160. The boundary was therefore
restored to 0.5. This isolates the remaining failure as cumulative false
admissions, so training also includes a direct recurring-over-one-off ranking
margin and no longer applies the old empty-state write-rate budget during the
admission-only phase.

With that ranking term enabled, the repeated seed-7 MPS run passed every
predeclared guardrail for the first time. The held-out admission margin reached
0.01567, 0.04861, and 0.07793 at steps 100/200/300, with 160/160 capacity,
32/32 delayed recall, and 0.7537 natural validation at every checkpoint.
Calibration selected a 0.34816 boundary: 1/16 useful natural associations was
admitted and survived its real next recurrence, 0/16 one-offs entered, and mean
intervening accepted writes fell from 35.5 in the unranked run to 1.625. The
selected boundary retained 160/160 automatic-pressure capacity and final
natural repeat recall remained 72/76. This is a deliberately conservative first
positive result: automatic full-memory replacement now occurs on real history,
but only where held-out survival benefit is observed without measurable recall
or capacity loss.

The unchanged configuration was then repeated on seeds 17 and 29. Seed 17 also
passed: its admission margin rose from 0.01926 to 0.04854 and 0.07281, and a
0.34738 boundary admitted 2/16 useful associations, preserved both to their next
recurrence, and admitted 1/16 one-offs. Decision utility was 0.0625 with 22.56
mean intervening accepted writes, while capacity, delayed recall, and natural
validation remained 160/160, 32/32, and 0.7818. Seed 29 exposed a calibration
failure despite an even larger final margin of 0.09479: every useful and one-off
candidate remained above the active write boundary, all 16 useful items were
later displaced before recurrence, and decision utility was -1.0. The safety
gate rejected calibration and retained the original 0.5 boundary. Thus the
current result is positive on 2/3 seeds and safely fails closed on the third, but
is not yet seed-robust; the next target is absolute admission calibration, not
additional pairwise separation.

The natural BPE experiment can now read the full Claude project-log directory in
addition to the global prompt history. Project sessions are ordered by their
first recorded timestamp, concatenated without crossing project boundaries, and
chunked into at most 65,536 tokens. The deterministic split holds out whole
projects, while only root user-authored text is tokenized and no raw text is
persisted. On the current local corpus this produced 169,245 training tokens from
15 projects and 17,782 evaluation tokens from 3 disjoint projects, with train and
evaluation compact-vocabulary coverage of 0.870 and 0.781. A zero-step MPS E2E
smoke run completed with 10 held-out repeats across 20 evaluated occurrences.
Use `--corpus-source projects`; the prior `history` source remains the default so
existing experiment results stay reproducible.

An opt-in `--project-content full` mode additionally keeps assistant text,
compact tool-call descriptions, and capped tool results in their original event
order. Hidden reasoning, images, internal metadata rows, and sidechains remain
excluded; each tool result is capped at 2,000 characters by default. This raises
the current corpus to 6,558,191 training tokens across 275 projects and 1,019,894
evaluation tokens across 82 disjoint projects (338/87 chronological sequences),
with compact-vocabulary coverage of 0.801/0.819. A zero-step MPS smoke run found
13 held-out repeats across 24 evaluated occurrences.

The first unchanged seed-7 admission run on this 7.58M-token corpus was safely
negative. Matching selected step 200 while retaining 160/160 capacity, 32/32
probe recall, and 0.78495 held-out natural repeat accuracy. Admission training,
however, changed its recurring-over-one-off margin from approximately zero to
-0.00579, -0.02040, and -0.01650 at steps 100/200/300. Every trained checkpoint
was rejected and restored to step zero; calibration also failed closed with
0/16 useful items surviving, 16/16 one-offs admitted, and decision utility -1.0.
The larger corpus therefore resolves data volume but exposes a label problem:
local repetitions of tool syntax and output boilerplate are being treated like
project-specific long-term utility. The next objective must make recurrence
supervision event-role-aware and long-range rather than merely adding data or
training steps.

The next corpus path therefore moves the language target to Meta's
[Multi-Session Chat](https://parl.ai/projects/msc/) (MSC), a human-human dataset
in which the same partners meet across multiple sessions. The loader consumes
only actual utterances. It excludes persona summaries and all agent/tool syntax,
deduplicates the previous-session copies stored in later MSC rows, and keeps an
entire pair in one group. Official `train` is used for training; `valid` and
`test` form evaluation, so no pair crosses the boundary. The external archive
is not committed. Its official ParlAI build recipe and checksum are recorded in
[`parlai/tasks/msc/build.py`](https://github.com/facebookresearch/ParlAI/blob/main/parlai/tasks/msc/build.py).

On MSC v0.1 this yields 4,000 training pairs, 13,001 sessions, 165,442 human
turns, and 4,598,657 retained BPE tokens. Evaluation contains 1,001 disjoint
pairs, 5,005 sessions, 61,743 turns, and 1,881,775 tokens. Compact-vocabulary
coverage is 0.928/0.922. Use `--corpus-source msc --msc-root
local-data/msc/msc` to select it.

Noise robustness is tested at the semantic unit that matters: a complete turn
from another pair in the same split is inserted before a real turn. The text is
left intact and receives an ordinary speaker label; there is no visible noise
marker for the model to exploit. Train and evaluation corruption are controlled
separately, so a clean-trained model can be challenged with noisy evaluation:

```bash
.venv/bin/python train_gated_natural_bpe_memory.py \
  --corpus-source msc --msc-root local-data/msc/msc \
  --dialogue-train-noise-probability 0 \
  --dialogue-eval-noise-probability 0.25 \
  --dialogue-noise-seed 90 --device mps
```

At probability 0.25 the fixed seed inserts 15,835 distractor turns into the
combined validation/test set, without train/evaluation leakage. This is the
first robustness condition; later stages should add delayed paraphrases,
corrections, topic drift, and misleading repetition while measuring
counterfactual future-token benefit rather than raw recurrence alone.

A zero-step MPS E2E run with clean training data and 25% noisy evaluation
completed successfully over all 4,000/1,001 pair groups. It found 7 held-out
exact repeats across 14 evaluated occurrences. This validates the new data and
GPU path only; the untrained model's zero repeat accuracy is not a learning
result, and the sparse exact-repeat count reinforces the need for a
paraphrase-aware human-memory objective.

A 20-step slow-model plus 20-step memory-controller MPS smoke run also reached
the real checkpoint selector. Slow-model loss fell from 7.6306 to 7.1947, but
the memory candidate reduced its controller-validation exact-repeat accuracy
from 0.125 to 0.0. The selector rejected step 20 and restored step zero, leaving
the final noisy-evaluation repeat accuracy at 0.0. This is a useful fail-closed
result, not evidence that memory cannot learn: the old exact-token recurrence
target is too sparse and brittle for longitudinal human conversation. The next
benchmark should compare future-session token loss with memory carried across
sessions versus the same model state reset, including distractor histories.

That dense longitudinal benchmark is now implemented. For each held-out pair,
the model reads every prior session in order, clears its stream-local RNN state
at each boundary while retaining only bounded memory items, and then predicts a
clean final session. Writes are forcibly disabled during the final session. A
paired control sees the identical final tokens from a completely fresh memory
state, so `reset_loss - carried_loss` measures the causal value of information
stored from the past. Distractor turns are inserted only into history, never
into the target.

The first zero-step MPS run used 32 held-out pairs with 25% history noise. It
processed 128 history sessions and 55,692 history tokens, then scored 7,565
known future-session tokens—far denser than the 14 exact-repeat occurrences.
Untrained carried memory helped 17 pairs and harmed 15: carried loss was
7.633763 versus reset loss 7.633476, for a small negative gain of -0.000287.
All eight items were occupied and the mean absolute memory-logit contribution
was 0.1105. This is the intended neutral/slightly-harmful cold-start baseline;
the next training objective can optimize future-session loss directly and use
the paired reset path for checkpoint selection.

Enable the benchmark with `--msc-session-eval-examples`; history and target
limits are controlled by `--msc-session-eval-history-tokens` and
`--msc-session-eval-target-tokens`.

Direct future-session training is now available through
`--msc-session-train-steps`. It freezes the slow language model, preserves the
autograd graph through causal history writes, disables writes on the clean
future session, and updates only the memory path from future-token NLL. The
`evidence_admission` policy retains automatic cold-start writes and capacity
protection, but now uses a straight-through priority gradient during automatic
acceptance so future utility can teach the storage controller without changing
the forward decision.

The first permissive smoke selector exposed validation overfit: step 5 improved
the mean gain on 8 validation pairs to 0.00878 but produced -0.00374 on disjoint
test pairs. A confidence-bound selector correctly rejected the same candidate.
The larger run used 128 training pairs, 32 validation pairs, 32 test pairs,
25% history noise, 16 memory items, and 30 session-training steps. Validation
gain improved from -0.03803 at step zero to -0.00143 at step 30, and ordinary
stream loss improved from 6.0570 to 6.0479, while capacity remained 8/8, 16/16,
and newest-16/16 under 24-fact pressure. However, step 30 was still harmful on
test: mean per-pair gain was -0.02748 ± 0.00595 and only 7/32 pairs improved.

This revealed one more selector bug: it could accept a statistically confident
relative improvement that remained absolutely harmful. Selection now requires
the candidate gain's confidence lower bound to exceed both the current upper
bound and zero, while also reducing absolute carried loss. Under the corrected
rule the step-30 candidate is rejected and step zero is restored. Thus the
dense objective and fail-closed training path work, but positive cross-pair
generalization has not yet been demonstrated.

Candidate-level counterfactual supervision is now available through
`--msc-counterfactual-steps`. At a sampled history token, it forks the same
pre-write state into forced-accept and forced-reject paths, replays the
identical remaining history, and labels the write gate by the difference in
clean future-session NLL. The slow model and every parameter except the write
gate remain frozen. Near-zero interventions are ignored, and checkpoint
selection uses the same strictly positive confidence-bound rule.

The first 5-step MPS smoke run found 1 useful intervention, 0 harmful
interventions, and 32 neutral interventions. The one non-neutral candidate had
future-loss utility 0.00820, but validation memory gain remained negative
(-0.00430), so the trained checkpoint was rejected and step zero restored. On
16 disjoint test pairs the restored model's mean per-pair gain was +0.00396 ±
0.01275, split evenly between 8 helped and 8 harmed pairs. This verifies the
causal labeling and fail-closed path, but also shows that an arbitrary single
token association is usually too small or too easily overwritten to affect a
distant human-conversation session. The next intervention should therefore
operate on a complete utterance/span while keeping the model token-native, not
add embeddings or tool syntax.

The next run changed only the intervention unit from one arbitrary token to one
complete human utterance (`--msc-counterfactual-unit turn`). Session examples
retain turn token spans, then the counterfactual branch forces every association
write in the chosen span on or off. The model remains token-native: turn
boundaries select a training intervention and are not embedded or supplied as a
semantic feature at inference time.

Because the current process could not initialize MPS, a controlled A/B replay
ran both units on CPU with identical data, seed, and 5-step settings. Token
interventions produced 1 useful, 0 harmful, and 32 neutral candidates. Turn
interventions produced 3 useful, 2 harmful, and 12 neutral candidates. The
neutral rate therefore fell from 32/33 (97%) for single tokens to 12/17 (71%)
for utterances. This supports the hypothesis that a token write was too small
to expose delayed utility. However, labelled turn-candidate utility averaged
-0.00433, validation gain remained -0.01044, and the selector again restored
step zero. Final evaluation on 16 disjoint pairs was -0.00446 ± 0.00860, with 6
helped and 10 harmed. The next problem is no longer finding any causal signal;
it is teaching the gate features to separate useful from harmful utterances
across people.

The utterance intervention can also be run as an offline label pass with
`--msc-counterfactual-label-candidates`. It samples unique retained turns,
stores only token IDs, controller activations, gate telemetry, and causal loss
differences in optional JSONL, and reports useful/harmful/neutral balance. Two
separability checks are included: ROC AUC for the current gate priority, and a
deterministic held-out nearest-centroid probe over the controller inputs. The
latter is diagnostic only; it does not modify the model. Use
`--msc-counterfactual-label-output local-data/msc-turn-labels.jsonl` to retain
the records for a later balanced gate-training pass. Records are flushed after
each candidate; add `--msc-counterfactual-label-resume` with the same model,
data, and seed settings to skip spans already present in that JSONL and continue
toward the requested total.

On the seed-90 CPU diagnostic, 96 unique utterances yielded 8 useful, 6
harmful, and 82 neutral labels (85.4% neutral). The untrained/current priority
ranking reached ROC AUC 0.625. A dialogue-disjoint controller-input probe used
9 train labels from 7 dialogues and 5 test labels from 5 other dialogues; its
AUC was 0.333 and balanced accuracy was 0.583. The sample is too small for a
stable estimate, but it does not support cross-dialogue generalization yet.
Batched accept/reject replay
preserved the first 48 labels exactly; its maximum utility difference from the
original two-pass implementation was `9.54e-7`.

The resumable pass was then expanded to every valid turn in 72 training
examples: 996 unique utterances produced 86 useful, 55 harmful, and 855 neutral
labels. Current gate priority was effectively random (ROC AUC 0.482). The
dialogue-disjoint controller-input probe reached ROC AUC 0.597 on 47 test
labels, which is weak but above the gate itself. A class-balanced offline gate
fit (`--msc-counterfactual-offline-steps 200`) reduced held-out label BCE from
1.524 to 0.676 and raised label AUC from 0.486 to 0.579. Nevertheless, its
32-dialogue future-session metrics were exactly unchanged at a mean gain of
0.00246 ± 0.00630, so the strict future-NLL guard rejected it and restored step
zero. This exposed an objective/action mismatch: forced counterfactual labels
currently include writes that `evidence_admission` performs automatically for
empty, unconfirmed, or matching slots. The next labels must be restricted to
write decisions the learned admission gate can actually change.

A controllability audit confirmed that diagnosis: under the old admission
semantics, none of the 996 utterance interventions contained a decision the
gate could change. `evidence_admission` now auto-fills only empty slots and
auto-updates actual matches; once the bootstrap slots are full, every
unmatched replacement is a learned decision, including replacement of an
unconfirmed slot. The model exposes that opportunity mask directly, and the
collector skips no-op interventions before replaying the future. With those
semantics all 996 utterances were controllable, with 19 useful and 977 harmful
labels. A dialogue-disjoint feature probe reached ROC AUC 0.892 and balanced
accuracy 0.852. Balanced gate training raised held-out gate AUC from 0.563 to
0.905, but the fixed threshold reduced validation session gain from 0.16947 to
0.07137. A causal-utility threshold accepted only six held-out utterances
(three useful and three harmful) yet reduced the gain further to 0.02743. Both
checkpoints were rejected and restored. The high label AUC but poor replay
result identified a second mismatch: an utterance-wide intervention was being
used to supervise token-wise runtime decisions.

The offline collector now receives `--msc-counterfactual-unit` explicitly and
persists `candidate_unit` in every record, rejecting resumes from a different
unit. On the first genuine token-level run, 1,000 samples were drawn from
20,500 available token decisions. Of these, 951 were controllable: 122 useful
and 829 harmful. The dialogue-disjoint feature probe reached only ROC AUC
0.583, and the trained gate reached 0.599. Utility calibration therefore chose
to accept none of its held-out labelled tokens. Scores on the full validation
stream still shifted enough to reduce session gain from 0.16947 to 0.12926, so
the future-NLL guard again restored the initial conservative gate. This is now
an aligned negative result: at 1,000 labels, the present controller inputs do
not generalize well enough to activate rare useful token writes safely.

Scaling the same pass to 5,000 token samples produced 4,765 controllable
decisions: 600 useful and 4,165 harmful, plus 235 automatic/no-op decisions.
The feature probe improved only from AUC 0.583 to 0.605. The raw linear gate
reached AUC 0.568 and conservatively reproduced the unchanged baseline session
gain. Fitting feature mean and scale on training dialogues only raised gate AUC
to 0.594, close to the diagnostic probe, but its validation session gain was
0.16042 versus the conservative baseline's 0.16947 and one of 32 dialogues was
harmed. The checkpoint was again rejected and all weights, normalization
buffers, and the admission threshold were restored. More public data helps
separability slightly, but this result points next to a nonlinear or temporal
token controller rather than agent traces, tool syntax, or more threshold
tuning. Equal-length token features are batched during offline training so the
larger passes do not execute one gate forward call per record.

The next A/B added an optional 32-unit GELU residual controller on top of the
normalized linear gate. Its output layer starts at zero, so the initial policy
and every legacy parameter are identical; offline fitting optimizes both the
linear and nonlinear paths, while the same future-NLL guard can restore them
together. On the exact seed-90, 5,000-token split, the nonlinear controller
overfit rather than exposing a safer boundary. Its best validation-label step
was 62, with AUC 0.578 and balanced BCE 0.698, both worse than the normalized
linear gate's AUC 0.594 and BCE 0.683. The selected threshold accepted no
held-out labelled token, but the full validation stream still shifted: mean
session gain collapsed from 0.16947 to 0.00641 and 13 of 32 dialogues were
harmed. The checkpoint was rejected and fully restored. Static nonlinear
capacity is therefore not the missing ingredient; the next controller should
carry causal temporal state across tokens and be tested against the same guard.

That temporal pass first exposed another alignment bug. Counterfactual candidates
had been evaluated as separate one-token chunks, and the first token of every
chunk was assigned zero slow-model surprise. Their accept/reject utilities remain
valid because those decisions were forced, but the stored controller feature did
not match continuous runtime. The model now derives boundary surprise from the
carried slow hidden state, making write features chunk-invariant. Existing labels
are reused by rebuilding their causal feature prefixes from the source dialogue;
all non-surprise fields must still match. On the 5,000-token dataset the mean
absolute surprise correction was 7.09 and the maximum was 8.46. Retraining the
normalized linear gate on corrected features still failed: label AUC was 0.591
and validation session gain was 0.15807 versus the 0.16947 baseline.

An optional zero-output 32-unit GRU then carried causal write-controller state.
A truncated 16-token prefix reached AUC 0.608 but reduced session gain to 0.05129,
confirming that resetting hidden state inside the training window was itself a
bad train/runtime mismatch. Replaying the complete 128-token session prefix raised
held-out label AUC to 0.765 and lowered balanced BCE to 0.511. Pointwise utility
calibration selected 25 labels, but their simultaneous runtime writes still
reduced validation gain to 0.12967. A final calibration therefore replayed whole
held-out training dialogues across candidate thresholds before touching the
independent validation split. It correctly chose reject-all; validation then
matched the baseline exactly at 0.16947 with zero harmed dialogues, and the strict
improvement rule restored step zero. Temporal context contains real predictive
signal, but independently useful writes still interfere as a set. The next target
is interaction-aware sequence credit or allocation, not a larger per-token
classifier.

Full-session future NLL was then connected directly to the temporal model. When
all non-slow memory parameters were trainable, validation selected step 120:
mean validation-session gain rose from 0.16947 to 0.35094 with no harmed
dialogues. On the untouched 32-dialogue evaluation split, mean gain rose from
0.03494 to 0.11516 and the one harmful dialogue disappeared. This establishes
that interaction-aware session loss is useful for adapting the memory system,
but it does not by itself identify the write controller as the cause. A new
`--msc-session-parameter-scope write_controller` ablation therefore froze every
other memory parameter. At learning rate 1e-3, gradients reached the temporal
controller but no hard admission decision crossed the threshold, so every
checkpoint matched step zero. At 1e-2, decisions did change, but validation
collapsed to as many as 16 harmed dialogues; the guard restored step zero.
Thus the positive full-system result came from read/fusion adaptation, while a
straight-through hard write boundary remains an unstable sequence-credit path.
The next controller experiment should train a stochastic sequence policy (or a
continuous training relaxation) and still select it using hard whole-session
replay.

That stochastic sequence-policy path is now implemented. During training only,
each controllable admission is sampled from the token controller's Bernoulli
probability. Two or more causal rollouts of the same human dialogue receive a
leave-one-out REINFORCE advantage from clean future-session NLL; automatic empty
slot fills and confirmed matches remain unchanged. Deployment and checkpoint
selection still use deterministic hard writes. The CLI exposes
`--msc-session-training-objective reinforce`, rollout/entropy controls, and an
optional report file so large experiment output does not depend on terminal
capture limits.

On the same seed-90 split, two-rollout policy training at learning rate 1e-3
produced measurable rollout reward variation (up to 0.049 NLL standard
deviation) but never changed a hard decision at threshold 0.5. At learning rate
1e-2 it did change decisions, but validation gain fell to 0.00641 with 13/32
harmful dialogues at most checkpoints; the best changed checkpoint reached only
0.10950 with 3/32 harmful dialogues, below the 0.16947 baseline. Both runs were
therefore restored to step zero.

Because a fixed 0.5 cutoff is arbitrary for a policy initialized near 0.05,
each policy checkpoint can now calibrate candidate hard thresholds by complete
session replay on training dialogues before the untouched validation guard is
applied. With 8 calibration dialogues and 6 candidate thresholds, the 1e-3 run
selected reject-all at steps 30, 90, and 120. At step 60 it selected threshold
0.0443 and improved calibration gain to 0.18846, but validation gain slipped to
0.16882 versus 0.16947. No checkpoint passed the strict guard, so independent
test remained at the restored baseline: mean gain 0.03494 with 1/32 harmful
dialogues. This rules out both the fixed cutoff and the straight-through
estimator as the immediate explanation. Under the present fixed allocation and
item representation, the automatic bootstrap items are useful, while additional
replacement writes are usually destructive. The next architectural target is
therefore joint write/allocation adaptation or a different item update rule,
not a larger write classifier or more threshold tuning.

The allocation ablation added a zero-initialized learned residual to
`evidence_lru` and a `write_allocation` scope containing the admission controller,
match threshold, item addresses, and replacement router. Its initial behavior is
identical to the fixed policy. At learning rate 1e-2, joint training reduced the
worst early damage relative to controller-only training: step 20 reached
validation gain 0.11834 with 2/32 harmful dialogues, rather than the 13--16
harmful cases seen in the unstable controller runs. It still never exceeded the
0.16947 baseline, and every checkpoint was rejected. Victim selection is
therefore part of the interference problem, but not a sufficient fix.

A projected replacement-update scalar then tested partial overwrite only for a
full, unmatched slot; empty fills and confirmed matches remain exact updates.
The apparent first run was rejected as an optimizer artifact: the raw parameter
moved above its upper bound while the effective rate stayed 1.0, and its dead
gradient altered global clipping. After outward gradients were removed and the
parameter was projected into `[0.05, 1.0]`, the learned rate stayed essentially
1.0 (`0.99998` to `1.0`). The model did not support global blending as the
missing update rule.

Parameter scopes then separated memory control from representation learning.
Early `memory_control` and 31-parameter `read_control` runs appeared to improve
the session gain, but an evaluator audit found that their fresh-state control
still used `use_memory=True`. A trained read gate could therefore worsen the
empty-memory control even though the absolute carried-loss guard prevented a
purely artificial checkpoint. The reset path now uses the identical slow model
with memory fusion completely disabled. All earlier empty-memory-control gain and
harmful-count figures are superseded by the corrected results below.

The corrected `read_representation` scope trains the read controller together
with `memory_embedding`, `memory_rnn`, and `key_projection`, while freezing the
write controller, allocation, slow LM, and fixed value codebook. It has 45,111
trainable parameters. On seed 90 the strict selector chose step 120: independent
test gain rose from 0.01517 to 0.11554, harmful dialogues fell from 8/32 to 0/32,
and absolute carried loss fell from 7.16832 to 7.07232. A seed-91 replication
also chose step 120: gain rose from -0.00219 to 0.07492, harmful dialogues fell
from 19/32 to 2/32, and carried loss fell from 7.08103 to 7.00978. Thus the
effect survives different initialization and noise.

The seed-90 checkpoint was then evaluated on 128 untouched dialogues without
changing training or validation. The zero-step memory improved 89/128 dialogues,
harmed 39/128, and achieved mean gain 0.01378 ± 0.00242. The trained
read-and-key representation improved 126/128, harmed 2/128, and achieved
0.12002 ± 0.00566; carried loss fell from 7.16946 to 7.07429 over 52,341 target
tokens. This is the first large held-out result that remains strong under a true
slow-only control. It also shows that the present useful learning signal is in
key formation and retrieval, while additional replacement writes should remain
conservative until a safer capacity mechanism is demonstrated.

A controlled capacity sweep then held the seed, data, optimizer, 120-step budget,
and 45,111 trainable parameters fixed while increasing the fast-state slots from
8 to 16 to 32. On the same 128-dialogue test set, the untrained mean gains were
0.01378, 0.00948, and 0.01853, with 39, 53, and 47 harmful dialogues. After
`read_representation` training, mean gains were 0.12002, 0.10620, and 0.03452;
carried losses were 7.07429, 7.08966, and 7.15763; and harmful counts were 2, 8,
and 39. The 16-slot selector chose step 120, while the 32-slot selector peaked at
step 100. More storage therefore does not automatically produce a stronger
memory: the current read can recover a useful 8-slot representation but
generalizes poorly as the candidate set grows.

A hard sparse-read ablation kept all 32 stored items but restricted each query
to its top eight similarities. It was effectively identical to dense 32-slot
reading: mean gain was 0.03456 instead of 0.03452, carried loss was 7.15759
instead of 7.15763, and harmful dialogues were 38 rather than 39. At the existing
0.02 temperature, attention was already functionally concentrated on its best
item. The capacity failure is therefore not dilution from averaging too many
values; false nearest-neighbor selection as more stored keys compete is the
leading hypothesis.

An optional `--item-read-abstention margin` mode now supplies the best match,
the top-one/top-two occupied-key similarity gap, and retrieval strength to a
three-parameter logit correction on the read gate. It starts at exactly zero,
preserving the original initialization and outputs. On seed 90, identical
120-step training and 128-dialogue evaluation gave mean gains of 0.23235,
0.16002, and 0.08432 for 8, 16, and 32 slots, respectively; carried losses
were 6.97244, 7.04003, and 7.11125; harmful counts were 0, 3, and 23.
Thus confidence-aware reading substantially improves each capacity, but the
8-slot model remains best under matched training conditions.

To isolate the gap signal, `--item-read-abstention match` kept the same
three-parameter correction while hiding the top-two gap. At 32 slots on seed
90, it reached gain 0.04854 with 37 harmful dialogues, versus margin mode's
0.08432 and 23 harmful dialogues. A second 32-slot seed also favored margin:
seed 91 improved from uncorrected gain 0.06948 to 0.10273, carried loss
7.00875 to 6.97782, and harmful dialogues 17 to 15. Mean absolute memory
contribution increased on both seeds, so the gain was not caused by globally
turning memory off. The remaining capacity gap calls for stronger key
discrimination or safer storage under a larger candidate set.

A follow-up ablation removed the fixed `0.1 × slot-address` term from replacement
scoring, on the hypothesis that it overwhelmed the initial 0.05 write priority.
It failed the first predeclared consistency check: on seed 7, combined repeat
accuracy fell from 0.434 to 0.408, memory-only accuracy from 0.329 to 0.289, and
accepted-source survival from 0.606 to 0.333. The address term was helping spread
allocation across items, so the ablation was stopped and not kept as an option.

## Run

The subproject uses its own environment and does not change the root TypeScript package.

```bash
cd experiments/neural-memory
uv sync --python 3.13
uv run pytest -q
uv run python train.py
uv run python train_competition.py
```

For a quick smoke run:

```bash
uv run python train.py --device cpu --steps 20 --eval-batches 2 --batch-size 8
```

The command trains two otherwise identical models:

- `learned_gate`: decides its update strength from the current input and surprise.
- `always_write`: writes every observation with strength 1.

It prints JSON containing held-out recall accuracy and the learned gate separation. Chance accuracy
is included explicitly. Do not interpret a single seed as evidence; the decision run should use at
least three seeds and report mean and standard deviation.

See [[메모리-연구/neural-memory/neural-memory/RESEARCH|RESEARCH.md]] for the prior-work mapping and staged decision gates, and
[[메모리-연구/neural-memory/neural-memory/RESULTS|RESULTS.md]] for the first three-seed run and its interpretation boundary.

## Phase 1: competitive allocation

`train_competition.py` removes the write-evidence shortcut and asks a separate question: can
delayed recall loss teach a small router to allocate colliding associations across independent
fast-weight blocks? The same local key deliberately maps to different values in four contexts.
No target block or allocation label is supplied to the learned variant.

The comparison fixes both the per-write update budget and total fast-state capacity at 576 scalars:

- `single`: one 24 x 24 matrix.
- `uniform`: four 12 x 12 matrices, every write spread equally.
- `competitive`: four 12 x 12 matrices, allocation learned only through recall loss.
- `oracle`: four 12 x 12 matrices, one block assigned to each context; a routing reference.

Besides recall accuracy, the run reports wrong-context intrusion rate and whether contexts settle
into a one-to-one block assignment. The context identifier is still an explicit synthetic feature;
this tests allocation dynamics, not discovery of latent semantic context from language.

On an M4 Pro, the default 200-step run takes roughly 25 seconds with MPS. See the phase-1 section
of [[메모리-연구/neural-memory/neural-memory/RESULTS|RESULTS.md]] for the three-seed result.

## Phase 2: frozen text cues plus joint write/allocation

Phase 2 removes categorical context from the learned path. A frozen BGE-small sentence encoder
turns held-out natural-language paraphrases into features; the memory layer sees those features,
not context IDs or write labels. Its outer-loop recall loss jointly trains:

```text
stable-vs-temporary cue embedding ──► scalar write gate
context paraphrase embedding ───────► competitive block allocation
                                      │
key/value observation ───────────────► per-episode fast weights
```

Prepare the frozen features once, then train only the memory layer:

```bash
uv sync --group text
uv run python prepare_text_embeddings.py
uv run python analyze_text_embeddings.py
uv run python train_semantic.py --summary
```

Training sentences and evaluation paraphrases are disjoint. The synthetic episodes put a
temporary, conflicting observation after every stable binding, while reusing the same local keys
across four semantic contexts. The key/value targets are randomized each episode, so slow weights
cannot memorize them. Categorical context IDs and stable/distractor flags exist only inside the
generator for metrics and the oracle control.

## Phase 3: episode-local online allocation

Phase 3 uses eight global semantic domains but samples a different subset of four in every
episode. There are only four blocks, so a fixed global domain-to-block map cannot avoid collisions.
`OnlinePrototypeMemory` instead stores episode-local context prototypes alongside its fast weights:

```text
new context ──► first empty block + new fast prototype
seen context ─► nearest occupied prototype + existing block
```

The BGE feature is compressed through a fixed random projection to 16 dimensions. Four 11 x 11
association matrices use 484 scalars and routing metadata uses 68, for 552 total runtime scalars;
the static baseline gets four 12 x 12 matrices, or 576 scalars.

```bash
uv run python prepare_online_embeddings.py
uv run python analyze_online_embeddings.py
uv run python train_online.py --summary
```

The allocation prior (novel context claims an empty block) is architectural. Delayed recall loss
learns its novelty threshold but is not yet learning the entire allocation algorithm. Context
features are held constant within an episode in this phase so the experiment isolates online block
assignment from semantic drift.

## Phase 4: utility-aware eviction

Phase 4 overfills memory with six active contexts and four blocks. Only four contexts are queried
later, and usefulness is randomized independently of arrival order. A frozen natural-language cue
describes each context as durable or temporary. The learned model receives the cue embedding but
not the retention label.

`PriorityEvictionMemory` gives each occupied block a learned scalar priority. When a novel context
arrives to a full memory, it either replaces the lowest-priority block or rejects the incoming
write. The discrete forward action has a straight-through comparison so delayed recall loss can
train the priority scorer.

```bash
uv run python train_eviction.py --summary
```

The model uses 484 association scalars plus 72 prototype/count/priority scalars, for 556 total
runtime state. The cue vocabulary is still hand-authored, context is stable within each episode,
and the eviction prior itself is architectural rather than discovered from scratch.

## Phase 5: delayed utility and eligibility traces

Phase 5 withholds every durability cue during observation. Six contexts arrive in a fully
interleaved stream and are first written to six short-lived trace slots. Only after the observation
stream ends do natural-language outcome cues arrive. The memory then scores the existing traces,
keeps the top four, and zeros the other association matrices before recall.

```bash
uv run python train_delayed.py --summary
```

Each trace uses a 9 x 9 association matrix, a 16-dimensional context prototype, a count, and a
priority: 594 transient runtime scalars in total. The forward top-k consolidation is discrete; a
straight-through mask carries future recall gradients into the linear priority scorer.

This is an explicit short-term trace, not a biological timing model. It has enough slots for all
six candidate contexts, does not decay with wall-clock time, and receives feedback paired with the
relevant context. Later work must learn that credit assignment from implicit outcomes.

## Phase 6: global feedback over real conversation traces

Phase 6 removes the explicit context pointer and replaces synthetic observations with the user's
local Claude prompt history. The loader sessionizes `~/.claude/history.jsonl` by project and idle
gap, strips tool and internal metadata, and weak-labels cases where a later user turn uniquely
reuses specific anchors from one of eight older turns. Raw text is never written to the repository
or embedding artifact.

```bash
uv run python analyze_claude_logs.py --summary
HF_HUB_OFFLINE=1 uv run python prepare_claude_log_embeddings.py
uv run python train_global_feedback.py --steps 1000 --seed 7 --summary
```

`GlobalFeedbackSelector` observes eight frozen 384-dimensional BGE features and stores only eight
learned 64-dimensional traces. A later global feedback embedding is projected into the same memory
space and scores every trace; there is no trace ID, target label, or context pointer in the forward
path. Its top-k mask is the consolidation action.

The current weak label is deliberately only a bootstrap target. It is constructed from lexical
anchor recurrence, and full-dimensional frozen cosine remains a stronger baseline. The next label
must come from outcomes independent of semantic recurrence, such as later corrections, accepted
actions, or task success, before this can support a claim that the model learns what is worth
storing rather than which old utterance resembles the present one.

## Phase 7: natural delayed strengthen/revise outcomes

Phase 7 extracts explicit acceptance and correction events from the same local history. Short
feedback such as `ㅇㅇ`, `좋아`, and `ㄱㄱ` is weak-labeled as accept/strengthen; high-precision
correction forms such as `ㄴㄴ`, `아니`, `잘못`, and `되돌려` are revise/weaken. These rules are the
teacher only. The learned gate receives frozen signed character n-gram features and never receives
the action label.

```bash
uv run python analyze_claude_outcomes.py --summary
uv run python prepare_claude_outcome_features.py
uv run python train_outcome_gate.py --steps 1000 --seed 7 --summary
```

`DelayedOutcomeGate.observe()` first writes a 64-dimensional provisional request trace. Its later
`act()` call compares three conditions: request-only, feedback-only, and request-plus-feedback.
`apply_outcome()` converts the action logits to a differentiable strength update. Accepted traces
remain strong; correction traces are weakened and marked for revision.

The immediate-previous-interaction association is still an architectural assumption, and regex
weak labels are not ground truth. Phase 6 and 7 together now implement the two halves needed for a
real memory update—select a responsible old trace and choose strengthen versus revise—but they have
not yet been trained jointly from downstream task reward.

## Phase 8: implicit tool outcomes and file-change survival

Phase 8 replaces user feedback labels with external state. `tool_outcomes.py` pairs test, build,
lint, and type-check commands with their later tool results. The observation trace contains recent
mutations plus the verification command; the delayed outcome is the actual result. The extractor
found 917 high-confidence outcomes, including 525 with preceding code mutations.

```bash
uv run python analyze_tool_outcomes.py --summary
uv run python prepare_tool_outcome_features.py
uv run python train_tool_outcome_gate.py --summary
```

The stronger survival task uses Claude's local file-history snapshots. For every consecutive
`A -> B -> C` chain, it asks whether the line delta introduced by `A -> B` is still present in `C`.
Only high-confidence retention scores at or above 0.8 or at or below 0.2 become labels. The model
must compare the old change trace with the future delta: either input alone is insufficient.

```bash
uv run python analyze_file_survival.py --summary
uv run python prepare_file_survival_features.py
uv run python train_survival_gate.py --steps 2000 --seed 7 --summary
```

`ChangeSurvivalGate` stores a fixed 64-dimensional random projection of the original change. When
the next file delta arrives it computes two relational features—cosine alignment and mean absolute
distance—and a six-parameter learned head chooses retain versus revert. Freezing the projection is
important because only 23 reverted train examples exist; learning the projection made some seeds
collapse to the majority class.

This is the first outcome in the curriculum that cannot be classified from the future event alone.
It remains a one-file, next-version proxy rather than a complete causal account of which agent
action helped a task. Reverts are rare, so the current model is useful as a ranking signal but is
not safe as an automatic deletion policy.

## Phase 9: prospective causal episodes

Phase 9 adds an observation-only Claude Code hook around real work in this repository. It records
the stable relationship that retrospective transcripts lose: a candidate action ID, workspace
state before and after it, later verification, subsequent repair, user acceptance/correction, and
exact state restoration. `tool_use_id` joins pre- and post-tool events; a bounded recent-action set
lets one global test outcome point to several eligible traces instead of assuming the immediately
preceding edit caused it. Each later prompt also carries up to 32 opaque candidate action IDs plus
its feature sketch, so later-reuse selection can be trained without storing the prompt itself.

The logger persists no prompt, path, command, source code, assistant response, or tool output.
Session/path/tool identifiers and file contents use per-installation keyed digests, and
language-bearing fields become keyed, normalized 256-dimensional signed character n-gram sketches
before the hook writes anything. Its event file, salt, and state ledger live under ignored `local-data/`.
The hook always exits successfully and never returns a permission or stop decision.

`.claude/settings.local.json` enables the observer only for this project. New Claude sessions pick
up the hook automatically. To inspect whether enough outcomes have accumulated:

```bash
uv run python analyze_prospective_events.py
uv run python analyze_prospective_events.py \
  --examples local-data/prospective-credit.jsonl
```

The derived labels are deliberately temporal actions rather than a single final class: a failing
verification or correction yields `revise`, a later pass or acceptance yields `strengthen`, and an
exact restoration of an earlier workspace state yields a separate action-specific `forget` event.
No Phase 9 model should be trained until multiple sessions contain all three labels and enough
multi-action outcomes for a whole-session holdout.

### Retrospective repair-chain bootstrap control

While the prospective stream is empty, `repair_chains.py` provides a deliberately separate weak
control from existing Claude transcripts. It finds a failed verification, the mutations before
that failure, later mutations, and a subsequent pass in the same test/build family. Older actions
become `ignore`, pre-failure actions become `revise`, and post-failure/pre-pass actions become
`strengthen`. This is a temporal teacher, not causal ground truth.

```bash
uv run python analyze_repair_chains.py
uv run python prepare_repair_features.py
uv run python train_repair_credit_cv.py --steps 600 --seed 7 --summary
uv run python train_repair_credit_cv.py \
  --architecture decoupled --steps 600 --seed 7 --summary
```

The evaluation leaves out one entire project at a time and concatenates predictions from all
held-out folds. The coupled model predicts `ignore/strengthen/revise` directly. The decoupled
control first decides whether to activate each trace, then chooses strengthen versus revise. Both
retain a 64-dimensional state per candidate and receive one shared later outcome.

Neither architecture clears the gate. The outcome adds only a small, shuffle-sensitive gain in
balanced accuracy, while overall accuracy remains below the majority class and exact episode
accuracy is approximately zero. This control therefore supports waiting for prospective causal
links rather than manufacturing more labels from transcript order.

### Claude + Codex history expansion

The user separately authorized local training use of their `~/.codex` conversation history. The
Codex adapter reads rollout `function_call`/`function_call_output` and
`custom_tool_call`/`custom_tool_call_output` pairs, including wrapped `exec` and `apply_patch`
events. Session metadata supplies the canonical working directory so the same project stays in one
holdout group across Claude and Codex formats.

The combined corpus contains 370 repair episodes from 61 sessions and 18 projects. Codex adds 251
episodes to Claude's 119. The same privacy boundary applies: source text is consumed locally to
build ignored hashed features and is not copied into git.

Adding Codex makes the outcome relation more reproducible, but does not make the weak temporal
labels causal ground truth. Both coupled and decoupled models improve when the real outcome is
available and regress when outcomes are shuffled; neither achieves reliable whole-episode action
assignment. See `RESULTS.md` for the leave-one-project-out measurements.

### Public trajectory bootstrap

`download_open_swe.py` samples resolved SWE-agent trajectories from NVIDIA's public
`Open-SWE-Traces` release through the Hugging Face dataset server. The downloader rejects truncated
rows and keeps only the explicitly listed permissive repository licenses. Raw trajectories and the
reproducibility manifest stay under ignored `local-data/`.

The adapter does not treat final success as an action label. It extracts the narrower relationship
already used by the local control: an explicit failing test, intervening editor mutations, and a
later passing test within an ultimately resolved trajectory. This gives more projects and model
behaviors without pretending that every action in a successful rollout was causal.

```bash
uv run python download_open_swe.py --rows 1000
uv run python analyze_open_swe.py
uv run python prepare_repair_features.py --skip-local \
  --open-swe-root local-data/open-swe-v1.jsonl \
  --output artifacts/open-swe-repair.pt
uv run python train_repair_credit_cv.py \
  --features artifacts/open-swe-repair.pt --architecture decoupled \
  --folds 5 --steps 600 --seed 7 --summary
```

Source: [NVIDIA Open-SWE-Traces](https://huggingface.co/datasets/nvidia/Open-SWE-Traces).
The dataset card states that source repositories use MIT, Apache-2.0, BSD-2-Clause, or
BSD-3-Clause licenses and includes the SPDX license on each row.

## Phase 11: human-annotated spontaneous context activation

ContextBench supplies 1,136 coding tasks with human-verified gold file spans. We reinterpret each
gold span as a memory trace that should activate from the natural issue statement. Gold spans from
other tasks in the same repository are hard `ignore` candidates, so repository vocabulary cannot
solve the task and the entire repository can remain held out during evaluation.

```text
candidate code span ──observe()──► persistent 64d trace
                                           │
natural issue statement ───────────────────► activate / ignore
```

The issue contains no explicit recall command. The frozen encoder is not trained; only the trace
projection and activation relation head receive gradients. Raw code and issue text remain in
ignored `local-data/`, while the checked experiment operates on frozen embeddings.

```bash
uv sync --group data --group text
uv run python download_contextbench.py
uv run python prepare_contextbench_features.py \
  --encoder bge --device mps --output artifacts/contextbench-bge.pt
uv run python train_context_activation_cv.py \
  --features artifacts/contextbench-bge.pt --steps 600 --seed 7 --summary
```

To replace the embedding model with frozen hidden states from the pretrained Gemma 3 270M
backbone while keeping the memory layer and evaluation identical:

```bash
# First accept the Gemma license and authenticate with Hugging Face.
hf auth login
uv run python prepare_contextbench_features.py \
  --encoder gemma --model google/gemma-3-270m --device mps \
  --batch-size 16 --max-length 512 --pooling mean \
  --output artifacts/contextbench-gemma-mean.pt
uv run python train_context_activation_cv.py \
  --features artifacts/contextbench-gemma-mean.pt \
  --memory-dim 128 --steps 2000 --seed 7 --summary
```

Gemma remains frozen in this comparison. Masked mean pooling is the supported default experiment;
`--pooling last` is retained as a negative ablation. The pooled state is normalized and passed to the
learned trace projection; raw text is still excluded from the artifact. Gemma runs in float32 because
float16 produced non-finite hidden states on MPS. The official Hugging Face repository is gated by
Google's Gemma terms.

The follow-up scripts test representation and lightweight adaptation without changing the memory
layer contract:

```bash
# Extract several hidden layers in one Gemma pass and inspect raw separability.
uv run python prepare_contextbench_gemma_layers.py --device mps
uv run python analyze_context_features.py \
  --features artifacts/gemma-layers/contextbench-gemma-layer-15-mean.pt

# Add the explicit trace/query alignment auxiliary objective.
uv run python train_context_activation_cv.py \
  --features artifacts/contextbench-gemma-mean.pt --memory-dim 128 \
  --steps 2000 --alignment-weight 1 --seed 7 --summary

# Optional 40,960-parameter LoRA pilot on the last four Gemma layers.
uv sync --group adapt --group data --group text
uv run python train_gemma_lora_pilot.py \
  --heldout-fold 0 --max-eval-episodes 200 --steps 50 \
  --lora-rank 4 --lora-layers 4 --lora-learning-rate 2e-4
```

The LoRA pilot first trains the independent memory layer from the frozen feature artifact using
train projects only, freezes that layer, and then updates only Gemma's adapters from raw text. The
evaluation subset switch is for quick local screening; it must be removed for a full result.

## Phase 12: explicit write capacity followed by delayed recall

The write/recall experiment splits each natural issue into an early title or summary and its later
body. A 377,730-parameter independent layer sees the early context plus candidate spans, writes only
a fixed fraction as 128-dimensional traces, and later activates stored traces from the body. The
write decision is a hard top-k action at inference, not an external graph operation.

```text
early issue + candidate ──write gate──► fixed-capacity 128d trace state
                                                │
later issue body ─────────recall head───────────► activate / ignore
```

```bash
uv run python prepare_contextbench_split_features.py \
  --device mps --batch-size 64 --max-length 256
uv run python train_context_write_recall_cv.py \
  --write-pretrain-steps 1000 --freeze-write --steps 1000 \
  --memory-dim 128 --keep-ratio 0.75 --seed 7 --summary
```

Write-gate pretraining uses human-gold utility as a weak teacher, then freezes the gate before
recall training. Neither a write label nor a recall instruction is present at inference. Use
`--write-aux-weight` to test simultaneous teacher training, or omit pretraining to reproduce the
failed pure end-to-end credit condition.

## Phase 13: real conversation write-before-revisit

Phase 13 removes the constructed title/body split. It reuses the privacy-local Phase 6 artifact:
eight actual earlier user turns are candidate traces and a naturally occurring turn at least two
steps later is the recall context. The write gate sees each old turn but no future query and stores
only two, four, or six of the eight traces.

```bash
# Uses the already ignored artifacts/claude_global_feedback.pt tensor file.
uv run python train_revisit_write_recall.py \
  --write-steps 1000 --recall-steps 1000 \
  --keep-ratio 0.25 --memory-dim 64 --seed 7

# Negative controls.
uv run python train_revisit_write_recall.py \
  --write-steps 0 --recall-steps 1000 --keep-ratio 0.25 --seed 7
uv run python train_revisit_write_recall.py \
  --shuffle-write-teacher --keep-ratio 0.25 --seed 7
```

The weak write teacher is derived from future lexical reuse during training only. At inference,
the 106,946-parameter layer receives no `write`, `recall`, trace ID, or future-utility instruction;
it executes its learned hard capacity decision and later ranks only the surviving 64d traces.

The character-hash artifact is a representation negative control:

```bash
uv run python prepare_contextbench_features.py --output artifacts/contextbench.pt
```

Source: [ContextBench](https://huggingface.co/datasets/Contextbench/ContextBench). Its accompanying
code repository is Apache-2.0; embedded code spans remain subject to their source repository
licenses and are therefore kept local.

## Phase 14: paper-grade ablations and public validation

The experiment matrix and claim boundaries are specified in [[메모리-연구/neural-memory/neural-memory/PAPER|`PAPER.md`]]. The ablation
runner compares BCE/listwise write objectives, online causal features, low-rate joint training,
random teachers, and untrained controls while reporting both ordinary and target-position-macro
metrics:

```bash
uv run python run_revisit_ablation.py \
  --variants staged_bce,staged_listwise,causal_bce,causal_listwise,causal_listwise_joint \
  --seeds 7,17,27,37,47 --keep-ratio 0.25
```

For the public cross-source test, download the official cleaned LongMemEval-S JSON, convert its
evidence sessions into query-hidden eight-way write episodes, then run the same layer:

```bash
curl -L --fail -o artifacts/longmemeval_s_cleaned.json \
  https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_s_cleaned.json
uv run --group text python prepare_longmemeval_features.py --device mps
uv run python run_revisit_ablation.py \
  --features artifacts/longmemeval_bge.pt --device mps \
  --variants staged_bce,causal_bce --seeds 7,17,27,37,47
```

This is an adaptation of LongMemEval rather than its official QA score: the question is hidden at
write time, one evidence session is mixed with seven deterministic distractors, and whole question
IDs are held out. `train_fast_weight_revisit.py` is a second architecture whose persistent memory is
an online-updated associative matrix instead of a set of trace slots.

## Phase 15: generator utility and the training-free length control

Every earlier phase scored the memory layer against its own activation metrics. This phase asks
whether the written memory changes a frozen generator's likelihood of the human-written gold answer,
and it only reports that comparison after the measurement proves it can detect a known-good memory.

```bash
uv run --group text python eval_generator_utility.py \
  --causal-features --limit 72 --device mps \
  --generator Qwen/Qwen2.5-1.5B-Instruct --generator-dtype bfloat16 \
  --output artifacts/results/longmemeval-generator-qwen-main-seed7.json
```

Every capacity-limited condition holds the same number of slots, so prompt length cannot explain a
likelihood difference. `instrument_usable` is false unless the oracle prompts survive the context
window intact, beat the no-memory reference, and beat a random selection of the same size. A
generator that fails this gate says nothing about the writer: a 270M base model and a 135M
instruction-tuned model both fail it, and an early 1,200-character session cap failed it by deleting
the evidence from the oracle prompt itself.

The second script scores selection rules that need no training at all. Candidate length is the
control the earlier heuristic sweeps missed:

```bash
uv run python analyze_length_baseline.py --source claude \
  --output artifacts/results/length-baseline-claude.json
uv run python analyze_length_baseline.py --source longmemeval \
  --output artifacts/results/length-baseline-longmemeval.json
```

The Claude run recomputes turn lengths from the local history and persists only aggregates.

## Phase 16: separating the semantic margin from the length correlate

`train_length_residual.py` holds the model, weak teacher, split, and training budget fixed while
changing only what the write gate can see. The length arm receives standardized log length and
within-episode length rank, which is exactly what a "keep the longest" rule reads.

```bash
uv run python train_length_residual.py --source claude \
  --seeds 7,17,27,37,47 --output artifacts/results/length-residual-claude.json

uv run python train_length_residual.py --source longmemeval \
  --features artifacts/longmemeval_bge.pt \
  --seeds 7,17,27,37,47 --output artifacts/results/length-residual-longmemeval.json
```

Candidate lengths are recomputed from the source and checked against the feature artifact's targets
before training, so a silent misalignment cannot produce the comparison.
