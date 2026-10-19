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

## 읽기 길잡이

단계 사이의 질문과 전환을 먼저 잡으려면 [[메모리-연구/신경-메모리-실험-흐름|신경 메모리 실험 흐름]]에서 시작한다.

나중에 필요한 것을 그때 가서 처음 기억할 수는 없다. 그렇다면 작은 모델은 **지금 무엇을 저장할지, 미래의 회상 결과만으로 배울 수 있을까?** 이 문서는 그 질문을 작은 합성 과제에서 시작해 연속 토큰, 실제 대화, 제한된 저장 공간으로 옮겨 간 실험 기록이다. 저장 성공, 읽기 성공, 실제 에이전트의 과제 성공은 서로 다른 단계로 구분한다.

본문에는 두 줄기의 기록이 함께 있다. 먼저 나오는 토큰 스트림 실험은 다음 토큰을 예측하면서 기억을 쓰고 읽는 구조다. 뒤의 Phase 1–16은 키·값과 텍스트 단서를 이용해 저장·할당·후속 피드백을 따로 시험한 단계다. 두 줄기는 조건과 평가 단위가 다르므로 수치를 한 성능표처럼 이어 읽지 않는다. 실행 명령과 당시 결과·실패·수정은 아래에 보존했다.

- **연속 토큰을 기억하는 구조**: [토큰 스트림 메모리](#kb-model-token)부터 읽는다.
- **실행 환경과 초기 실험**: [실행 방법](#kb-model-run) → [경쟁적 할당](#kb-model-allocation) → [텍스트 단서](#kb-model-text) 순서로 읽는다.
- **실제 대화와 지연 피드백**: [Phase 6](#kb-model-feedback)부터 실험 조건을 확인한다.
- **용량 제한과 대조 실험**: [Phase 12](#kb-model-capacity), [Phase 16](#kb-model-controls)을 확인한다.

이 문서의 합성 기억 성능을 실제 에이전트의 과제 성능으로 해석하지 않는다. 이후 결과와 정정은 [[메모리-연구/neural-memory/neural-memory/RESULTS|실험 원장]], 사람 대화 실험의 비교 기준은 [[메모리-연구/신경-메모리-읽기|신경 메모리 읽기 안내]]에 있다.

### 실험의 출발점

핵심 아이디어는 파일이나 벡터 저장소에 기록을 쌓는 대신, **작은 모델의 계속 변하는 파라미터 자체에 기억을 쓰는 것**이다. 여기서 fast weights는 한 에피소드 안에서 관찰이 들어올 때마다 바뀌는 기억 행렬이고, slow parameters는 여러 에피소드를 학습하며 그 갱신 방법을 배우는 파라미터다.

Phase 0은 ‘무엇을 쓸지 고르는 메커니즘’만 떼어 시험한다. 그래서 의도적으로 keymem의 키/값 그래프나 LLM에 연결하지 않았다. 강한 외부 검색이나 언어 모델이 정답을 대신 만들어 주면, 작은 메모리가 실제로 학습했는지 판단하기 어렵기 때문이다.

```text
observation (key, value, noisy evidence)
        │
        ├─ learned gate + surprise
        ▼
matrix-valued fast weights W(t)     ← the memory
        │
future query ───────────────────────► recalled value
```

합성 과제에는 관찰이 많이 들어오지만, 그중 일부만 나중에 질문한다. 나머지는 저장 공간을 차지하는 방해 항목이다. 모델에게 ‘이것을 저장하라’는 직접적인 `write` 라벨은 주지 않는다. 나중에 회상을 틀린 정도가 앞선 쓰기 게이트를 학습시킨다.

기억 행렬의 차원은 가능한 키·값 연결 수보다 일부러 작게 잡았다. 모두 저장해도 충분하다면 선택을 배울 필요가 없기 때문이다. 방해 항목까지 쓰면 기존 연결을 덮거나 섞어 버리는 간섭이 생긴다. 따라서 이 실험의 성공 조건은 단순히 기억하는 것이 아니라, **같은 제한 아래 무조건 쓰는 모델보다 잘 기억하는 것**이다.

<span id="kb-model-token"></span>

## Token-stream plastic memory prototype

먼저 쓰기 대상을 따로 지정하지 않고 토큰을 계속 흘려보내도 기억이 생기는지 시험한다. `TokenPlasticMemory`는 토큰 ID를 직접 받는다. 벡터 저장소, 메모리 슬롯, 최근접 이웃 검색, 명시적 retrieval 호출은 없다. 토큰 전이가 관찰될 때마다 에피소드 안의 fast-weight 행렬 하나가 갱신되고, 현재 토큰이 그 행렬을 바로 자극해 다음 토큰을 예측한다.

```bash
uv run python train_token_memory.py
```

매 에피소드마다 키에서 값으로 이어지는 토큰 연결을 무작위로 바꾼다. slow parameters가 정답을 외우는 길을 막고, **이번 에피소드에서 실제로 본 연결을 기억해야만** 반복 예측에 성공하게 만든 것이다. 학습 신호는 다음 토큰 교차 엔트로피뿐이다. 쌍의 ID, 이전 노출 횟수, 쓰기 라벨, 활성화 목표는 모델에 주지 않는다. 이전에 몇 번 보았는지에 따른 정확도와 내부 기억 활동을 측정하고, 메모리를 끈 대조도 함께 본다.

시드 7, 17, 29로 각각 600스텝 실행했을 때 반복 예측 정확도는 모두 1.000이었다. 처음 보는 연결의 정확도는 평균 0.041로, 값 토큰을 무작위로 맞힐 확률 1/24와 같았다. fast weights를 끄면 반복 정확도도 0.041로 내려갔다. 즉 정답을 원래 아는 것이 아니라, 관찰한 연결을 온라인으로 저장한 덕분에 반복에서 맞혔다.

내부 활성화 평균도 이전 노출이 없을 때 `0.214`에서 한 번, 두 번, 세 번 뒤 `0.433, 0.527, 0.560`으로 올랐다. 여기서 확인한 것은 토큰 전이 기억이다. 장거리 문맥이나 여러 기억을 조합하는 언어 능력까지 입증한 것은 아니므로, 다음에는 같은 키가 문맥에 따라 다른 답을 갖게 만든다.

### Context-conditioned token memory

바로 앞 토큰만 외우면 되는 과제에서 한 단계 나아가, **같은 키라도 문맥이 다르면 다른 값을 읽어야 하는가**를 시험한다. `ContextualTokenPlasticMemory`는 같은 fast-weight 갱신 앞에 인과적 순환 상태를 더한다. 입력은 `separator, context, key, value` 형식의 원시 토큰열이고, 한 키가 여러 문맥에서 서로 충돌하는 값을 갖는다. 그 값은 매 에피소드 무작위로 바뀐다.

```bash
uv run python train_contextual_token_memory.py
```

시드 7, 17, 29의 600스텝 실행에서 반복 정확도 평균은 1.000, 첫 노출은 0.062로 우연 수준 1/16이었다. fast weights를 끄면 반복 정확도는 0.060, 모든 문맥을 같은 토큰으로 바꾸면 0.152였다. 따라서 기억 행렬뿐 아니라 문맥 구분도 필요했다. 내부 활성화 평균은 이전 노출이 없을 때 `0.235`, 한 번과 두 번 뒤 `0.456`, `0.531`이었다.

짧은 토큰열에서 문맥별로 다른 답을 기억한다는 결과다. 다만 구분자와 짧은 형식이 경계를 알려 주므로, 아직 경계 없는 긴 자연어를 읽는 기억은 아니다. 다음 과제에서는 그 구분자와 상태 초기화를 제거한다.

### Unsegmented token stream

앞 과제는 어디서 새 사건이 시작되는지 알려 주었다. 이번에는 구분자와 reset을 없앤다. `topic, modifier, key, value` 토큰 묶음을 이어 하나의 스트림으로 만들고, 모델은 토큰 ID만 받으면서 순환 상태를 계속 유지한다. 학습되는 토큰 lookup은 신경망 내부 입력층이지 저장 기억을 찾는 임베딩 인덱스가 아니다. 벡터 데이터베이스, 최근접 이웃 검색, cue ID, 경계 라벨, retrieval 연산은 없으며, 변하는 fast-weight 행렬이 기억으로 남는다.

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

이 결과는 연속된 합성 토큰 스트림에서 문맥에 맞는 회상이 스스로 형성된다는 근거다. 그러나 경계 신호를 없앴다고 해서 자연어의 자유로운 경계 발견을 해결한 것은 아니다. 이 스트림은 여전히 고정된 네 토큰 문법과 서로 겹치지 않는 역할별 토큰 집합을 쓴다. 다음에는 사건 길이부터 바꾸어, 고정 위치만 이용한 성공인지 확인한다.

### Variable-length token stream

고정된 네 위치를 이용하는 지름길을 없애기 위해 사건 길이를 바꾼다. 각 관찰은 `topic, [zero to three random fillers], key, value`이며, 같은 단서가 다시 나와도 filler의 종류와 길이가 바뀐다. 사건들은 구분자, 패딩, reset 신호, 반복 라벨, retrieval 호출 없이 이어진다.

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

다음 토큰 손실만으로 길이가 바뀌어도 같은 내용을 회상하는 결과다. 남은 지름길은 어휘 역할이다. topic, modifier, key, value의 토큰 집합이 아직 서로 겹치지 않으므로, 토큰 종류만 보고 역할을 알아낼 수 있다. 자연어의 경계 찾기와 훨씬 긴 보존은 미해결이며, 다음 실험은 이 역할별 어휘 구분부터 없앤다.

### One shared token vocabulary

이번에는 topic, filler, key, value를 모두 같은 24개 토큰 ID에서 뽑는다. 하나의 토큰이 여러 역할을 맡을 수 있어, 토큰 ID만으로 ‘지금은 값 위치’라고 알 수 없다. 숨은 생성 형식은 `topic, [zero to two fillers], key, value`를 유지하지만 구분자, 패딩, reset, 역할 채널, 어휘 경계 표시는 없다. 앞 과제와 달리 **모든** 다음 토큰 위치에서 학습 손실을 계산한다. cue ID, 사건 역할, 값 위치 마스크는 추론 뒤 평가에만 쓴다.

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

이 단계에서 처음으로 회상이 즉시 만점에 도달하지 않고 반복 노출에 따라 점진적으로 좋아졌다. 역할 구분 없는 토큰 어휘와 전체 스트림 언어 모델 손실에서도 숨은 문맥 기억이 나타난 것이다. 다만 생성 과정은 여전히 합성이고 평가자는 숨은 역할을 안다. 실제 문장을 토큰화한 입력, 끝나는 시점을 모르는 에피소드, 훨씬 긴 스트림의 간섭은 아직 시험하지 않았으므로 다음에는 실제 subword 토크나이저를 도입한다.

### Real BPE text stream

토큰 ID 장난감에서 실제 텍스트 표면으로 옮긴다. 에피소드마다 무작위로 정한 사실을 영어 문장으로 만들고, 캐시된 Llama-3 BPE 토크나이저로 연속 텍스트를 나눈다. 같은 사실은 `Mara's access word is copper`, `For Mara, the access word is copper`, `Remember that Mara uses copper` 같은 네 가지 바꿔쓰기 형태로 나타난다. 값은 매 에피소드 섞으므로 slow parameters가 사람별 답을 외울 수 없다. 사전학습 모델이나 임베딩은 불러오지 않는다. 외부 토크나이저는 문자열을 BPE ID로 바꾸는 데만 쓴다.

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

이 결과는 실제 subword 토큰화와 표면적인 바꿔쓰기에서도 메커니즘이 작동함을 확인한다. 하지만 실제 자연 말뭉치에서의 결과는 아니다. 문장 템플릿, 사실 반복 횟수, 스트림 길이는 실험자가 의도적으로 만든다. 모델과 전체 스트림 손실만 그 구조를 모른다. 그래서 다음에는 문장 생성기를 버리고, 통제되지 않은 대화 기록을 입력한다.

### Uncontrolled conversation stream

합성 문장에서는 반복 구조가 너무 깨끗할 수 있다. 이를 확인하려고 문장 생성기를 제거하고 로컬 Claude 대화 기록을 메모리 안에서 토큰화했다. 프로젝트 전체를 결정론적으로 훈련·평가로 나눈 뒤 일반적인 256토큰 창을 뽑는다. 원시 텍스트는 출력하거나 저장하지 않는다. 압축한 2,048토큰 어휘는 훈련 188세션의 토큰 91.9%, 평가 125세션의 87.7%를 덮는다.

```bash
uv run python train_natural_bpe_memory.py
```

Evaluation finds exact `(four-token context, next token)` transitions that recur
inside a held-out window and excludes every transition that appeared anywhere
in training. These recurrence annotations are used only for measurement;
optimization remains full-stream next-token cross-entropy.

더 엄격한 이 실험에서는 중요한 부정적 결과가 나왔다. 시드 7, 800스텝에서 미학습 fast-weight 메커니즘은 평가용 반복 533회에 대해 정확도 0.381이었다. 학습 뒤에는 0.126으로 떨어졌고, 메모리를 끈 0.087에 비해 순수 기억 기여는 0.039뿐이었다. 반면 전체 스트림 손실은 7.471에서 4.452로 좋아졌다. 즉 일반적인 토큰 분포 예측은 배웠지만, 온라인 연상 경로는 망가졌다. 학습률을 열 배 낮춰도 보존되지 않았고 반복 정확도는 0.000이었다.

따라서 이 실행은 자연 데이터에서 저장 시점이 학습되었다는 증거가 **아니다**. fast weights가 빈 상태에서 시작하더라도, 델타 규칙으로 쓰는 행동 자체는 설계자가 넣은 전제다. 일반 언어 모델 학습이 그 전제를 유용하게 만드는 표현을 덮어쓸 수도 있다. 다음 구조에서는 쓰기·읽기 게이트를 거의 비활성인 상태에서 시작하고, slow predictor가 기억 경로를 지배하지 않도록 둘을 분리한다.

### Initially inactive learned gates

앞 실패를 다루기 위해 `GatedContextualTokenMemory`는 느린 언어 예측기와 기억 표현을 분리한다. 쓰기 게이트는 현재 토큰의 예측 놀라움을 보고, 읽기 게이트는 회상 신호의 세기를 보며, 둘 다 0.05에서 시작한다. 먼저 slow 경로를 학습한 뒤 동결하고, 그다음 기억 경로만 학습한다. 두 단계 모두 모든 다음 토큰 정답을 사용하지만, 반복 위치·노출 횟수·평가 라벨은 받지 않는다.

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

게이트가 켜져 유용해진 것은 맞지만, 저장 시점 선택을 완성한 것은 아니다. 첫 관찰과 반복 관찰 사이에서 게이트가 아직 뚜렷하게 선택적이지 않고, 자주 반복된 평가 전이도 fast-weight 간섭 때문에 실패한다. 따라서 다음 목표는 전체 게이트를 더 세게 켜는 일이 아니라, **어느 기억 영역에 쓸지 나누어 충돌을 줄이는 것**이다.

### Competitive memory slots

한 행렬에 몰아쓰며 생긴 충돌을 줄이려고 여러 독립 fast-weight 행렬을 둔다. straight-through router가 현재까지의 토큰 문맥을 한 슬롯에 배정하고, 다음 토큰이 올 때까지 그 선택을 유지한 뒤 동일한 단일 쓰기 게이트 예산을 선택한 슬롯에 쓴다. 반복 문맥의 읽기도 한 슬롯으로 보낸다. 평균 라우팅 확률에 작은 무라벨 균형 벌점을 주어 모든 문맥이 한 슬롯으로 몰리는 것을 막는다. straight-through는 실제 전방 선택은 이산적으로 하되 학습 때 근사 기울기를 전달하는 방식이다.

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

네 슬롯의 개선이 라우팅 덕분인지, 단지 저장 공간이 네 배여서인지 분리해야 한다. 그래서 메모리 폭을 slow predictor 폭과 독립적으로 정하게 했다. 32×32 행렬 하나와 16×16 행렬 네 개는 모두 상태 값 1,024개를 갖고, slow predictor 폭은 32로 같다. 같은 세 시드 일정에서 용량을 맞춘 네 슬롯은 반복 정확도 0.170, 기억 기여 0.037로 단일 슬롯의 0.218, 0.084보다 낮았다. 슬롯 사용은 4개 중 3.98개였고 반복 문맥 라우팅도 안정적이었지만, 행렬을 너무 좁게 나누며 잃은 연상 rank가 라우팅 이득보다 컸다. 앞선 네 슬롯의 개선에는 추가 용량의 영향이 상당했다.

An optional learned erase gate was also added. It observes the current context,
prediction surprise, and selected-slot norm before deciding whether to clear
that slot prior to a write:

```bash
uv run python train_gated_natural_bpe_memory.py --num-slots 4 --learned-eviction
```

256토큰 창에서 세 시드의 평균 erase gate는 0.010에서 0.00037로, 512토큰 압박 시험에서는 0.00016으로 떨어졌다. 반복 정확도 변화는 작았고 선택 슬롯의 0.04%도 지우지 않았다. 모델은 슬롯 통째 비우기를 사실상 쓰지 않았다. 이를 ‘망각을 배웠다’고 부를 수는 없다. 한 행렬 전체를 지우는 대신, 개별 연결을 교체할 수 있는 제한된 항목 저장소로 옮길 이유가 여기서 생긴다.

### Bounded token-item memory

`BoundedItemTokenMemory`는 개별 연결 수준으로 교체 단위를 줄인 후속 구조다. 비어 있는 고정 크기 항목 bank에서 시작해 현재까지의 네 토큰 키를 다음 토큰과 묶는다. 매 스텝 최대 한 항목만 바꾼다. 빈 항목을 먼저 쓰고, 가득 차면 들어온 연결의 학습된 쓰기 우선순위가 기존 항목보다 높을 때만 교체한다. 읽기는 점유 항목들에 주의를 주며, 불확실한 일치는 학습 게이트로 조절한다. 점유 키가 정확 일치 문턱을 넘으면 회상이 직접 활성화된다. 따라서 빈 메모리는 비활성이고, 관련 토큰 경험이 쌓여야 작동한다. 저장 토큰은 고정 코드북을 사용해 학습 중 기존 항목의 의미가 몰래 바뀌지 않게 한다.

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

이제 항목은 깨지지 않게 저장할 수 있으므로, **무엇을 오래 남길지** 학습해 본다. 실험적인 retention-only 단계에서는 같은 네 토큰 문맥과 다음 토큰이 스트림 뒤에서 다시 나오면 해당 연결에 지연된 양성 목표를 준다. 쓰기 모델이 실제로 보는 것은 현재 은닉 상태, 예측 놀라움, 과거에 문맥이 기억과 얼마나 강하게 맞았는지뿐이다. 미래 반복 정보는 학습 목표이며 추론 입력은 아니다.

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

앞 retention 분류기는 ‘다시 나타날 것’을 맞힐 수 있어도, 그 항목이 실제로 교체 압박을 버텨 정답을 내는지는 보장하지 않는다. 더 엄격한 목적은 각 정확한 국소 연결을 바로 다음 등장까지 추적하고, 그때 메모리만의 다음 토큰 손실을 매기는 것이다. 기울기는 중간의 제한 메모리 갱신들을 거슬러 현재 시점의 쓰기 제어기까지 전달되어야 한다. 제어기는 추론 때 여전히 미래 토큰을 받지 않는다. 학습 신호는 단순 반복 여부가 아니라 **키와 값이 살아남아 맞는 토큰을 냈는가**에 달린다.

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

retention과 admission이라는 중간 라벨이 최종 회상 개선으로 이어지지 않아, `episodic` 목적은 평가하려던 기준 자체를 훈련 창에 적용한다. 이산 교체 결정에서는 일반 기울기가 불안정하므로 simultaneous perturbation을 쓴다. 작은 선형 쓰기 게이트를 양·음 방향으로 조금 바꿔 같은 인과적 토큰 에피소드를 두 번 실행하고, 실제 반복 위치의 종단 간 교차 엔트로피 차이로 갱신 방향을 추정한다. 반복 표시는 손실 위치만 고르며 모델이나 추론 입력으로 들어가지 않는다. 체크포인트 선택용 프로젝트 그룹은 별도이고 원래 평가 분할도 건드리지 않는다.

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

저장 정책을 바꿔도 최종 예측이 좋아지지 않으면, 기억이 맞는 답을 내는데 slow predictor와 합치는 단계에서 잃는지 확인해야 한다. 이를 위해 정확 일치 읽기 위에 선택적 학습 잔차를 둔다. 매 토큰에서 보는 값은 여섯 가지다. 검색 세기, 일치 세기, slow·memory 예측기의 각각 최대 확률, 기억이 고른 토큰에 slow가 준 확률, 두 argmax의 일치 여부다. 잔차를 0으로 초기화해 처음에는 원래 정확 읽기와 같다. 반복 표시와 미래 토큰은 추론에 들어가지 않는다. `fusion` 목적은 나머지를 모두 동결하고 이 잔차만으로 반복 위치의 종단 간 손실을 줄인다.

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

앞 retention 손실은 쓰기 비율을 0.10으로 요구했는데, 64항목 미학습 모델의 실제 쓰기 비율은 약 0.46–0.57이었다. 같은 목적이 ‘반복될 내용을 배워라’와 ‘대부분의 교체를 억제하라’를 동시에 시킨 셈이다. 목표 예산을 0.56으로 올려 전체 쓰기량을 유지하면, 균형 잡힌 지연 반복 손실이 어떤 연결에 더 높은 우선순위를 줄지에 집중할 수 있다.

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

자연 대화에서 좋아진 저장 제어기가 **처음 보는 임의의 사실도 지킬 수 있는지** 별도 스트레스 시험을 한다. `eval_real_text_memory.py`는 전에 본 적 없는 읽을 수 있는 토큰 연결 8개를 각 한 번 보여 주고, 64항목 용량을 넘도록 방해 토큰을 넣은 뒤 네 토큰 단서를 반복한다. 로컬 기록의 원문을 드러내지 않고 slow-only, memory-only, 결합 예측의 첫 답변 토큰 정확도를 각각 보고한다.

```bash
uv run python eval_real_text_memory.py --device mps
```

시드 17에서 미학습 제어기는 4/8을 회상했지만, 프로젝트 분리 검증으로 step 100에서 고른 학습 제어기는 1/8뿐이었다. slow-only는 둘 다 0/8이었다. 자연 말뭉치의 반복 규칙을 유용하게 배운 것이, 새 임의 사실을 잘 보존하는 정책과 같지는 않았다. 오히려 그 보존을 해쳤다.

따라서 ‘저장 선택 학습을 해결했다’는 더 강한 주장은 이 시험으로 반박된다. 기본값은 64항목 정확 저장과 보간 읽기로 남기고, 다음 목표를 학습 분포 밖 저장 정책으로 잡는다. 아래의 후속 시도들은 이 실패를 고치려다 어떤 설명을 배제했고 어디서 설계를 바꾸었는지 시간순으로 기록한 것이다.

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

여러 제거 실험이 반복해서 실패하면서 원인을 단순 설정값보다 목적 함수에서 찾게 되었다. 자연 대화의 재등장을 정답으로 주면 훈련 분포에서 흔한 반복을 우대한다. 그것이 새로운 상황에서 첫 관찰을 저장할 가치까지 일반화하지는 않는다. 그래서 다음에는 기존 정책에서 멀리 벗어나지 않게 제한하고, 실제 미래 손실을 비교하는 더 보수적인 대조를 한다.

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

이 결과에서 문턱만 더 내리면 유용한 새 사실과 함께 기존 기억을 망가뜨리는 쓰기도 늘어난다. 따라서 다음 최적화 대상은 **이미 가득 찬 상태에서 이번 교체가 전체 미래 회상에 이득인가**다. 문턱 조정이나 보호 기준 없는 장기 학습을 반복하기보다, 교체가 다른 기억에 주는 비용까지 직접 재기로 한다.

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

이 분해에서 전체 시스템의 긍정적 결과는 읽기·결합 경로 적응에서 나왔다. 반면 straight-through 방식으로 단단한 쓰기 경계를 학습하는 경로는 긴 시퀀스의 공로를 안정적으로 전달하지 못했다. 그래서 다음 제어기 실험은 훈련 중 확률적 시퀀스 정책 또는 연속 완화를 쓰되, 최종 체크포인트는 실제 배포와 같은 hard 결정으로 전체 세션을 재생해 고르도록 바꾼다.

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

자신 있는 읽기와 모호한 읽기를 구분하게 하자 모든 용량에서 성능이 크게 좋아졌다. 그러나 학습 조건을 맞추면 여전히 8슬롯이 가장 좋다. 이는 공간만 늘리면 기억이 좋아진다는 설명으로는 부족하다는 뜻이다. 다음 대조에서는 개선이 단순 일치 강도 때문인지, 최고 후보와 두 번째 후보 사이의 **격차**를 본 덕분인지 분리한다.

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

<span id="kb-model-run"></span>

## Run

이 하위 프로젝트는 자체 환경을 사용하며 루트 TypeScript 패키지를 바꾸지 않는다. 아래 명령은 초기의 작은 저장 선택 실험부터 실행한다. 사이트에 코드가 포함된 것은 아니므로 경로는 원 저장소 기준이다.

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

<span id="kb-model-allocation"></span>

## Phase 1: competitive allocation

Phase 0의 현재 쓰기 증거가 정답의 지름길일 수 있어 이를 제거하고, 별도의 질문을 한다. **같은 키가 충돌할 때, 미래 회상 손실만으로 서로 다른 기억 블록에 나누어 쓸 수 있을까?** `train_competition.py`는 같은 국소 키가 네 문맥에서 서로 다른 값을 갖게 만든다. 학습 모델에는 어느 블록이 정답인지, 어디에 할당해야 하는지 알려 주지 않는다.

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

<span id="kb-model-text"></span>

## Phase 2: frozen text cues plus joint write/allocation

Phase 1은 문맥을 명시적 범주로 주었다. Phase 2는 그 지름길을 없애고, 학습에 쓰지 않은 자연어 바꿔쓰기를 동결 BGE-small 문장 인코더로 특징화한다. 메모리 층은 그 특징만 받으며 문맥 ID나 쓰기 라벨은 받지 않는다. 바깥 회상 손실 하나로 무엇을 쓸지 정하는 스칼라 게이트와 어느 블록에 쓸지 정하는 경쟁적 할당을 함께 학습한다.

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

앞 구조가 도메인마다 블록을 고정 배정해서 성공한 것인지 확인한다. Phase 3은 전역 의미 도메인 8개 중 매 에피소드 다른 4개를 뽑지만 블록은 4개뿐이다. 고정된 전역 도메인→블록 대응으로는 충돌을 피할 수 없다. `OnlinePrototypeMemory`는 대신 해당 에피소드에서 관찰한 문맥의 대표 벡터(prototype)를 fast weights 옆에 저장해, 처음 보는 문맥은 빈 블록으로, 이미 본 문맥은 가장 가까운 점유 prototype의 블록으로 보낸다.

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

빈 블록 배정이 가능해졌으므로 이제 일부러 메모리를 넘치게 한다. Phase 4는 문맥 6개를 블록 4개에 넣지만, 나중에 질문할 것은 그중 4개뿐이다. 유용성은 도착 순서와 독립적으로 무작위화한다. 동결한 자연어 단서가 각 문맥을 오래 필요한 것 또는 일시적인 것으로 묘사하고, 학습 모델에는 그 임베딩만 주며 보존 정답 라벨은 주지 않는다. 이 조건으로 최신성 규칙과 유용성 기반 교체를 구분한다.

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

Phase 4에서는 처음 볼 때부터 오래 쓸 내용인지 단서가 있었다. Phase 5는 관찰 중 그런 단서를 모두 숨긴다. 문맥 6개가 완전히 뒤섞여 들어와 우선 짧게 유지되는 흔적 슬롯 6개에 쓰인다. 관찰 스트림이 끝난 뒤에야 자연어 결과 단서가 도착한다. 메모리는 그제서야 기존 흔적을 평가해 상위 4개를 남기고, 나머지 연상 행렬을 0으로 만든 뒤 회상한다. 즉 이번 질문은 즉시 예측이 아니라 **나중 결과로 이미 남긴 흔적을 골라 보존할 수 있는가**다.

```bash
uv run python train_delayed.py --summary
```

Each trace uses a 9 x 9 association matrix, a 16-dimensional context prototype, a count, and a
priority: 594 transient runtime scalars in total. The forward top-k consolidation is discrete; a
straight-through mask carries future recall gradients into the linear priority scorer.

This is an explicit short-term trace, not a biological timing model. It has enough slots for all
six candidate contexts, does not decay with wall-clock time, and receives feedback paired with the
relevant context. Later work must learn that credit assignment from implicit outcomes.

<span id="kb-model-feedback"></span>

## Phase 6: global feedback over real conversation traces

Phase 5의 후속 단서는 어느 문맥에 관한 것인지 연결되어 있었다. 실제 대화는 보통 그렇게 친절하지 않다. Phase 6은 명시적 문맥 포인터를 없애고 합성 관찰 대신 사용자의 로컬 Claude 프롬프트 기록을 쓴다. loader는 `~/.claude/history.jsonl`을 프로젝트와 유휴 간격으로 세션화하고, 도구·내부 메타데이터를 제거한다. 나중 사용자 발화가 앞선 8개 중 하나의 구체적 어휘 단서를 유일하게 재사용하는 경우에 약한 라벨을 붙인다. 원문은 저장소나 임베딩 산출물에 쓰지 않는다.

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

어휘가 비슷하다는 사실만으로 그 경험이 좋았는지 나빴는지는 알 수 없다. Phase 7은 같은 로컬 기록에서 명시적인 수락·수정 피드백을 뽑는다. `ㅇㅇ`, `좋아`, `ㄱㄱ` 같은 짧은 피드백은 accept/strengthen, `ㄴㄴ`, `아니`, `잘못`, `되돌려` 같은 정밀도 높은 수정 표현은 revise/weaken의 약한 라벨로 삼는다. 이 규칙은 교사에만 쓰며, 학습 게이트는 동결한 signed character n-gram 특징을 받을 뿐 행동 라벨을 받지 않는다.

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

사용자 피드백의 규칙 라벨에만 기대지 않기 위해 Phase 8은 외부 상태를 본다. `tool_outcomes.py`가 테스트·빌드·lint·타입 점검 명령을 나중 도구 결과와 짝짓는다. 관찰 흔적에는 최근 코드 변경과 검증 명령이, 지연 결과에는 실제 실행 결과가 들어간다. 추출기는 신뢰도 높은 결과 917개를 찾았고, 그중 525개에는 선행 코드 변경이 있었다.

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

과거 대화에서 순서만 복원하면 어느 수정이 어떤 결과를 만들었는지 빠질 수 있다. Phase 9는 이 저장소의 실제 작업을 관찰 전용 Claude Code hook으로 기록한다. 후보 행동 ID, 전후 작업 공간 상태, 나중 검증, 후속 수리, 사용자 수락·수정, 정확한 상태 복원 사이의 관계를 처음부터 남긴다. `tool_use_id`로 도구 전후 이벤트를 연결하고, 제한된 최근 행동 집합을 유지해 전체 테스트 결과가 여러 후보 흔적을 가리킬 수 있게 한다. 바로 전 수정 하나가 원인이라고 단정하지 않는 것이다. 나중 프롬프트도 최대 32개 불투명 후보 행동 ID와 특징 sketch를 가져, 원문 저장 없이 이후 재사용 선택을 학습할 수 있게 한다.

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

앞으로 모을 관찰 스트림이 아직 비어 있는 동안, `repair_chains.py`는 기존 Claude 대화에서 별도의 약한 대조 자료를 만든다. 실패한 검증, 그 앞의 변경, 이후 변경, 같은 테스트·빌드 계열의 통과를 찾는다. 오래된 행동은 `ignore`, 실패 전 행동은 `revise`, 실패 후 통과 전 행동은 `strengthen`으로 표시한다. 이것은 시간 순서로 만든 교사이지 인과적 정답이 아니다. 따라서 새 관찰 수집을 대체하는 확정 자료가 아니라, 약한 라벨로 어디까지 가능한지 보는 대조다.

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

자료 수를 늘리기 위해, 당시 사용자가 별도로 허용한 로컬 `~/.codex` 대화 기록 학습을 추가했다. Codex adapter는 rollout의 `function_call`/`function_call_output`, `custom_tool_call`/`custom_tool_call_output` 쌍을 읽고, 감싸진 `exec`와 `apply_patch` 이벤트도 처리한다. 세션 메타데이터의 정규 작업 디렉터리로 프로젝트를 맞추므로, 같은 프로젝트가 Claude와 Codex 형식에 걸쳐 있어도 하나의 평가 분리 그룹에 남는다. 이는 당시 데이터 구성 기록이며 현재 문서 읽기에 별도 기록 접근을 요구하는 것은 아니다.

The combined corpus contains 370 repair episodes from 61 sessions and 18 projects. Codex adds 251
episodes to Claude's 119. The same privacy boundary applies: source text is consumed locally to
build ignored hashed features and is not copied into git.

Adding Codex makes the outcome relation more reproducible, but does not make the weak temporal
labels causal ground truth. Both coupled and decoupled models improve when the real outcome is
available and regress when outcomes are shuffled; neither achieves reliable whole-episode action
assignment. See `RESULTS.md` for the leave-one-project-out measurements.

### Public trajectory bootstrap

로컬 자료의 프로젝트와 모델 행동 종류가 제한되어 있어 공개 궤적도 추가한다. `download_open_swe.py`는 Hugging Face dataset server를 통해 NVIDIA `Open-SWE-Traces`의 해결된 SWE-agent 실행을 표본으로 뽑는다. 잘린 행은 거부하고, 명시된 허용적 저장소 라이선스만 받는다. 원시 궤적과 재현 명세는 ignored `local-data/`에 둔다. 성공한 실행 전체를 곧바로 ‘모든 행동이 좋았다’고 라벨링하지 않는다는 아래의 경계가 중요하다.

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

시간 순서로 만든 약한 라벨에서 벗어나, 사람이 확인한 관련 코드로 ‘무엇을 떠올려야 하는가’를 시험한다. ContextBench는 정답 파일 구간을 사람이 검증한 코딩 과제 1,136개를 제공한다. 각 정답 구간을 자연스러운 issue 설명에서 활성화되어야 할 기억 흔적으로 해석한다. 같은 저장소의 다른 과제에서 온 정답 구간은 어려운 `ignore` 후보로 넣는다. 저장소 어휘만으로 풀 수 없게 하며 평가에서는 저장소 전체를 분리할 수 있다.

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

<span id="kb-model-capacity"></span>

## Phase 12: explicit write capacity followed by delayed recall

앞 단계는 관련 흔적을 활성화하는 문제였다. 이제 **나중 질문을 다 보기 전에 일부만 저장해야 한다**는 제약을 더한다. 자연스러운 issue를 초기 제목·요약과 나중 본문으로 나눈다. 독립적인 377,730파라미터 층이 초기 맥락과 코드 구간 후보를 보고, 고정 비율만 128차원 흔적으로 쓴다. 이후 본문이 오면 저장된 흔적을 활성화한다. 쓰기 결정은 추론 때 hard top-k로 실제 후보를 제한하는 동작이며 외부 그래프 연산이 아니다.

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

Phase 12의 제목·본문 구분은 실험자가 만든 시간 분할이었다. Phase 13은 이를 없애고 실제로 다시 등장한 대화 맥락을 쓴다. 개인정보를 로컬에 유지한 Phase 6 산출물에서 실제 과거 사용자 발화 8개를 후보로 삼고, 적어도 두 단계 뒤에 자연스럽게 나온 발화를 회상 맥락으로 삼는다. 쓰기 게이트는 미래 질문을 보지 않고 옛 발화만 보며, 8개 중 2개·4개·6개만 남긴다.

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

사적 대화에서 나온 결과가 어느 설계 선택에 의존하는지, 공개 자료에서도 유지되는지 확인한다. 실험 행렬과 주장 범위는 [[메모리-연구/neural-memory/neural-memory/PAPER|`PAPER.md`]]에 정했다. 제거 실험 runner는 BCE/listwise 쓰기 목적, 온라인 인과 특징, 낮은 학습률의 공동 학습, 무작위 교사, 미학습 대조를 비교한다. 전체 지표뿐 아니라 정답 위치별 값을 균등하게 평균한 target-position-macro 지표도 보고해, 특정 위치의 빈도에 결과가 좌우되지 않는지 본다.

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

앞 Phase들은 메모리 층 내부의 활성화 지표를 평가했다. 그러나 관련 기억이 활성화되어도 실제 답변이 좋아지는지는 별개다. 이번에는 저장된 기억이 동결 생성 모델의 사람 작성 정답 가능도를 바꾸는지 묻는다. 단, 먼저 정답 근거를 준 조건이 좋다는 사실을 측정 도구가 알아볼 수 있어야 한다. 그 유효성 확인 뒤에만 모델끼리 비교한다.

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

<span id="kb-model-controls"></span>

## Phase 16: separating the semantic margin from the length correlate

길이가 긴 후보를 고르는 단순 규칙이 경쟁력이 있었다면, 앞 모델은 의미보다 길이만 읽었을 수 있다. `train_length_residual.py`는 모델, 약한 교사, 분할, 훈련 예산을 고정하고 쓰기 게이트가 볼 수 있는 정보만 바꾼다. 길이 조건에는 표준화한 로그 길이와 에피소드 안 길이 순위를 준다. ‘가장 긴 것을 남겨라’ 규칙이 보는 정보를 명시적으로 제공해, 임베딩의 이점이 길이 이상의 것인지 분리한다.

```bash
uv run python train_length_residual.py --source claude \
  --seeds 7,17,27,37,47 --output artifacts/results/length-residual-claude.json

uv run python train_length_residual.py --source longmemeval \
  --features artifacts/longmemeval_bge.pt \
  --seeds 7,17,27,37,47 --output artifacts/results/length-residual-longmemeval.json
```

Candidate lengths are recomputed from the source and checked against the feature artifact's targets
before training, so a silent misalignment cannot produce the comparison.
