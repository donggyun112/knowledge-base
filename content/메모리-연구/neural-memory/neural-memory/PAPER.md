---
title: "What a Bounded Memory Layer Can and Cannot Do Before the Query Arrives"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `neural-memory/PAPER.md` · 수집 2026-10-16 · 커밋 `fd190b18f8e4113d7f451a7108911c1f89716b24`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# What a Bounded Memory Layer Can and Cannot Do Before the Query Arrives

## Status

2026-09-14 시점의 작업용 논문 초안이자 재현 계획이다. 이때의 근거는 한 가지 현상과 두 가지 큰 부정적 결과를 뒷받침한다. 스스로 기억을 관리하는 일반 해법을 얻었다는 주장은 뒷받침하지 않는다. 실패한 분기와 대조 실험도 모두 `RESULTS.md`에 남겼으며, 세부 결과가 충돌하면 그 실험 원장을 기준으로 한다.

이 연구에서 중요한 것은 성능 수치뿐 아니라 **좋아 보이던 결과가 어떤 점검에서 철회되었는가**다. 공개 데이터의 보존 성능 주장은 길이 대조 실험(Phase 15)에서, 생성 모델을 이용한 과제 수준 성능 주장은 짝지은 검정(Phase 33)에서 철회되었다. 결과를 인용할 때는 그 주장을 마지막으로 검토한 Phase까지 확인해야 한다.

질문은 두 갈래로 바뀌었다. Track A는 미래 질문이 나오기 전에 작은 층이 **무엇을 남길지** 고를 수 있는지를 물었다. Track B는 그 선택 문제를 내려놓고, 신경망의 변화하는 상태 자체가 **연상 기억 저장소**가 될 수 있는지를 물었다. 둘 다 측정 가능한 한계에 도달했지만, 막힌 이유가 다르다. 한쪽의 성공이나 실패를 다른 쪽의 결론으로 옮겨 읽으면 안 된다.

## Track A: query-hidden capacity selection

### Research question

처음 질문은 이렇다. 동결한 인코더 옆에 작은 학습 층을 붙이면, 현재 입력만 보고 제한된 메모리에 남길 정보를 고를 수 있을까? 그리고 나중에 사용자가 평범하게 말했을 때, 별도의 검색 명령 없이 관련 기억을 활성화할 수 있을까?

여기에는 한 가지 전제가 있었다. 중요한 판단은 미래 질문이 생기기 **전**에 끝나야 하며, 대부분의 후보를 버린 뒤에는 되찾을 수 없다는 것이다. 따라서 성능을 제한하는 주된 원인을 ‘너무 일찍 버리는 일’로 예상했다.

**Phase 17은 이 전제를 직접 측정했고, 주된 병목이라는 설명은 틀렸다.** 임시 용량을 늘려 8개 중 2개를 즉시 확정하는 조건에서 8개 전부를 나중 사건까지 보유하는 조건으로 바꾸자, 정답 자료 보존률은 0.5281에서 0.6456으로 올랐다. 그러나 같은 나중 사건과의 원시 코사인 유사도만으로 후보를 정렬하면 0.9342였다. 늦게 고를 기회를 주어도 학습된 선택기가 그 정보를 충분히 쓰지 못했다. 이 비교에서는 되돌릴 수 없는 삭제보다 선택 메커니즘 자체의 비용이 더 컸다.

### Model under test

시험한 모델은 동결 인코더 위에 놓인 독립적인 106,946파라미터 층 `SelectiveWriteRecallMemory`다. 학습하는 동작은 세 가지다. 미래 질문을 보지 않은 상태에서 용량에 맞춰 후보를 확정하고, 살아남은 후보를 지속되는 64차원 흔적으로 바꾸며, 이후의 자연스러운 발화로 관련 흔적을 다시 활성화한다.

여기서 흔적(trace)은 원문 전체가 아니라 저장해 둔 작은 벡터 상태다. 이 구조에는 그래프 순회, 데이터베이스 검색, 프롬프트 수준의 기억 지시, 본체 모델 미세 조정이 없다. 따라서 결과를 전체 LLM을 재학습한 효과와 혼동하지 않고 작은 메모리 층의 효과로 좁혀 볼 수 있다.

### What Track A established

자연 Claude 말뭉치에서는 8개 중 2개만 남기는 조건으로 시험했다. 프로젝트 전체를 평가용으로 분리했을 때, 단계별 학습 모델이 미래에 필요한 발화를 남긴 비율은 0.5906 +/- 0.0121이었다. 무작위로 2개를 남기면 기대값은 0.25다. 이후 회상 top-1은 0.5627 +/- 0.0164였고, 질문을 섞으면 0.3369 +/- 0.0050으로 떨어졌다. 필요한 발화가 저장에서 살아남은 경우만 보면 top-1은 약 0.9527이었다. 즉 이 조건에서는 ‘남은 것을 찾는 일’보다 ‘필요한 것을 남기는 일’에서 더 많이 잃었다.

현재 시점에서 알 수 있는 위치, 새로움, 예측 놀라움 특징을 더하자 다섯 시드의 보존률은 0.6279 +/- 0.0097이 되었다. CPU 재현값은 0.6195 +/- 0.0101이었다.

그러나 이 개선이 의미를 이해해서 나온 것인지, 단순히 긴 발화를 골라서 나온 것인지 구분해야 했다. Phase 16에서 길이만 입력한 저장 조건은 0.4056 +/- 0.0128, 동결 임베딩 조건은 0.5920 +/- 0.0099였다. 임베딩에 길이를 명시적으로 추가해도 더 좋아지지 않았다. 이 사적 말뭉치에서의 차이는 길이만으로 설명되지 않는 의미적 여지가 있다는 근거다.

다음으로 생성 모델의 답변 점수를 보았을 때는 과제 수준 근거가 생긴 것처럼 보였지만, **Phase 33에서 철회했다**. 당시 통과 기준은 앞쪽 72개 에피소드에서 극단값의 영향을 크게 받는 점수의 평균을 비교했다. 전체 평가 202개에서는 무작위 세션 두 개가 정답 근거 세션보다 나았고, 처음 72개에서도 정답 근거 조건이 무작위보다 이긴 에피소드는 정확히 50.0%, paired t = 1.74였다. 평가 도구가 정답 근거의 이점을 안정적으로 알아보지 못한 것이다.

이후 `instrument_usable`은 평균뿐 아니라 에피소드별 짝지은 승률이 우연 수준을 넘어야 한다. 이 관문을 통과하기 전에는 이 연구의 답변 가능도 수치를 성능 증거로 인용하면 안 된다.

### Where Track A stopped, and why

공개 데이터에 대한 주장은 먼저 Phase 15에서 철회했다. LongMemEval-S에서는 학습 없이 가장 긴 두 개를 고르는 규칙이 0.4159를 기록해 학습 모델의 0.4069보다 높았다. 이 공개 벤치마크만으로는 메모리 층이 단순한 길이 규칙보다 나은지 구분할 수 없었다.

그다음 Phase 19는 작은 메모리의 용량이 문제인지 직접 확인했다. 384차원 원시 특징을 모두 쓰고, 병목도 단계별 동결도 없는 제약 없는 listwise scorer를 학습했다. 후보 목록 전체를 보고 순위를 매기는 더 자유로운 모델이다. deferred 말뭉치에서는 이 모델이 0.5044, 게이트가 0.5380이었고, Claude에서는 0.6069 대 0.5920이었다. 제약을 풀어도 큰 도약은 없었다.

반면 같은 층에 나중 사건을 보여 주면, 저장 시점에는 약 0.54를 넘지 못하던 문제가 0.9500까지 올라갔다. 결론은 **용량 부족보다 당시 이용 가능한 정보의 부족이 병목**이라는 것이다. 첫 단계의 구조를 더 복잡하게 만들 근거가 부족해져, 이 연구 갈래는 여기서 멈췄다.

## Track B: the store itself as the memory

### Redesign

Track A는 슬롯 중 무엇을 남길지 고르는 문제였다. Track B에서는 **신경망의 상태 자체가 기억**이라는 방향으로 질문을 바꾸었다. `RESEARCH.md`에는 생물학 문헌에서 가져온 측정 10개가 번호별로 있다. 버섯체의 희소 확장 부호, 시냅스 태깅과 포획, 초파리 DAN/MBON 회로의 반대 부호 조절 채널, 시간 상수가 다른 병렬 저장소, 경쟁적 할당, 재생, 재고착이 그 근거다. 각 실험은 실행 전에 출처의 발견과 가설이 틀렸다고 판단할 기준을 적었다.

저장소는 델타 규칙으로 갱신된다: `W <- λW + s·(v − W k)kᵀ`. 여기서 W는 기억 행렬, k는 단서, v는 저장할 값이다. 현재 기억이 k에서 읽어 내는 값 Wk와 목표 v의 차이만큼 상태를 고친다. λ는 이전 상태를 얼마나 남길지, s는 얼마나 강하게 쓸지를 정한다. 키는 큰 공간에 펼친 뒤 일부만 활성화하는 희소 확장 코드로 만들고, 읽은 값을 저장했던 값들과 비교한다.

이렇게 바꾼 이유는 ‘미래의 쓸모를 미리 맞히는가’와 ‘한정된 상태가 주어진 내용을 얼마나 잘 보유하는가’를 분리하기 위해서다.

### What Track B established (Phases 20–30)

열 가지 예측 중 여섯 개는 살아남았고, 세 개는 기각되었으며, 하나는 결과가 갈렸다. 기각된 세 예측은 각각 별개의 실패라기보다 오차를 수정하는 쓰기 규칙 하나로 설명되는 묶음이었다.

아래 결과에서 판별력(discrimination)은 **저장했던 단서로 읽었을 때 자기 값이 다른 모든 저장 값보다 앞서는가**를 뜻한다. 아직 새로운 질문으로 정답 문서를 찾는 시험은 아니다.

- 희소 확장 부호는 판별력을 높였다. 특히 *유사한* 문서에서 이점이 30–60x 더 커 희소화 문헌의 예측과 맞았다. 복원 충실도(fidelity)를 재면 방향이 반대로 보이지만, 이 예측이 말하는 것은 충실도가 아니라 항목 구별이다.
- 감쇠는 도움이 되지 않았다. 상수 스윕(Phase 21), 실제 단위별 적응 규칙(Phase 27), 감쇠 상수를 따로 지시하지 않았는데도 경사하강법이 0.9995와 0.9964까지 올린 결과(Phase 30)가 서로 독립적으로 이를 보였다.
- 조립한 저장소를 학습하자 평가용 판별력이 0.8774에서 0.9513으로 올랐다.

Phase 30은 Phase 29의 수동 구성요소 제거 실험 해석도 뒤집었다. 수동 설정에서는 tag 경로의 기여가 0.0007에 불과하고 병렬 저장소가 해롭다고 보았다. 그러나 상수를 학습 가능하게 돌려놓자 모두 *증가*했고, 어느 요소도 꺼지지 않았다. capture 값은 수동 0.25에서 0.9445까지 올랐다.

여기서 배운 점은 설정의 역할이다. 구성요소를 손으로 정한 값에서 제거해 보는 실험은 ‘그 설정에서 도움이 되는가’만 답한다. 요소 자체가 무용한 것인지, 처음부터 거의 작동하지 않게 설정한 것인지까지 구분하지는 못한다.

### Track B's negative result

**저장한 항목을 구별하는 능력은 대리 지표였고, 실제 질문 검색으로 이어지지 않았다.** Phase 31에서야 벤치마크가 실제로 요구하는 일을 시켰다. 질문의 후보 세션들을 저장하고, 저장한 적 없는 단서인 질문 임베딩으로 읽어서 정답 근거 세션을 돌려주게 했다. 아래 표의 projection-only 조건은 같은 키 투영만 학습하고 아무것도 저장하지 않는다. 이 대조가 있어야 표현 학습의 이득을 메모리 저장의 이득으로 잘못 세지 않을 수 있다.

| Reader | LongMemEval deferred | LongMemEval revisit |
| --- | ---: | ---: |
| Chance | 0.1250 | 0.1250 |
| Trained store | 0.5578 +/- 0.0347 | 0.6337 +/- 0.0200 |
| Trained key projection, nothing written | 0.8178 +/- 0.0401 | 0.8416 +/- 0.0245 |
| **Cosine on the frozen encoder** | **0.8622 +/- 0.0295** | **0.8465** |

세션을 실제로 저장하는 과정은 같은 학습 투영으로 직접 읽는 조건보다 약 0.21–0.26의 손해를 냈다. 이 결과를 설명할 수 있을 법한 대안 세 가지도 시험했지만 지지되지 않았다.

- **학습 부족인가?** 학습을 3천에서 1만 2천 스텝으로 늘려도 0.5741 +/- 0.0105로, 실질적인 변화가 없었다.
- **너무 희소한가?** 폭 8에서 질문 코드는 이미 정답 세션과 활성 단위의 절반을 공유했다. 폭 512에서는 구조상 완전히 겹치는 밀집 코드인데도 저장소는 0.63, 코사인은 0.86이었다. 값 병목을 넓혀도 최고는 0.7074였다.
- **저장량이 너무 적어서 장점이 안 보이는가?** 다른 질문의 세션을 후보에 추가하자 격차는 줄지 않고 커졌다. 8개에서 0.16 뒤졌고, 128개에서는 0.35 뒤졌다.

작동 원리로 보면 납득할 수 있다. 델타 규칙 저장소가 맞추는 것은 문서마다 ‘저장 키를 넣으면 저장 값이 나와야 한다’는 식이다. 희소화는 이 식들이 서로 덜 간섭하게 한다. 그래서 Track B의 판별력 개선과 Phase 30의 상수 변화는 모두 이미 쓴 것을 보존하는 방향으로 갔다. 하지만 저장한 적 없는 질문으로 일반화하는 능력은 그 식에서 자동으로 생기지 않는다. 이 검색 과제에 필요한 관계는 이미 인코더의 표현 공간에 있었다.

따라서 Track B의 측정 자체를 철회하는 것은 아니다. 주어진 내용을 보유하는 능력에 관한 결과는 유지된다. 철회해야 할 연결은 ‘문서를 잘 보관하는 저장소라면 질문에도 잘 답할 것’이라는 추론이다. 연구는 열두 Phase 동안 이 연결을 당연하게 가정하고 있었다.

Phase 34는 델타 규칙이 특히 유리할 법한 상황을 추가로 시험했다. 새 사실이 옛 사실을 대체하면, 제자리 덮어쓰기가 가능한 메모리가 단순 코사인보다 낫지 않을까? LongMemEval 지식 갱신 에피소드 78개에서 쓰기 순서만 뒤집자 현재 진술 선호가 0.7949에서 0.2128로 바뀌었다. 임베딩은 그대로였으므로 순서에 따른 덮어쓰기 효과는 인과적으로 확인되었다.

그런데 더 간단한 규칙이 여전히 이겼다. 코사인만 쓰면 hit rate 0.4487, 저장소는 0.6333이었지만, 학습 없이 ‘코사인 상위 2개 중 나중 것을 고른다’는 규칙은 **0.8974**였다. 저장소는 희소 코드의 부분 겹침으로 갱신 관계를 표현하려 했고, 후보 목록에서는 그 관계를 시간 순서로 바로 표현할 수 있었다.

## Evaluation design

Track A의 주된 결과는 미래에 필요한 항목이 용량 제한을 통과해 남고, 올바른 후속 맥락에서 활성화되는지다. Track B의 주된 결과는 실제 질문으로 정답을 찾는 hit rate이며, 같은 동결 인코더를 기준으로 비교한다. 두 갈래 모두 답변 품질은 평가 도구가 먼저 유효성을 통과해야만 읽을 수 있는 보조 결과다.

각 대조는 다른 오해를 막는다.

- 무작위 용량 선택, 미학습 모델, 무작위로 섞은 저장 교사: 학습 자체가 무엇을 더했는지 확인한다.
- 최신성, 현재까지의 새로움·놀라움, **길이** 규칙: 복잡한 모델이 단순한 지름길만 학습한 것은 아닌지 확인한다.
- 질문을 본 전체 동결 임베딩 코사인: Track B에서는 희망하는 상한이 아니라 반드시 비교해야 하는 주 기준이다.
- 같은 투영을 학습하되 아무것도 쓰지 않는 projection-only 조건: 투영 학습의 이득을 저장소의 이득과 분리한다.
- 나중 질문 섞기, 프로젝트·질문 그룹 전체 분리, 초기화 시드 최소 다섯 개: 질문 정보, 데이터 분리, 초기화에 대한 의존성을 확인한다.

동결 생성 모델에는 유효성 관문 `instrument_usable`이 있다. 정답 근거를 준 oracle이 메모리 없음과 무작위 조건을 모두 이겨야 하고, 프롬프트가 잘리지 않아야 한다. Phase 33에서 추가한 조건은 평균만이 아니라 **에피소드별로도** 무작위보다 나아야 한다는 것이다. 지금까지 이 생성 평가를 실행한 모든 경우가 이 관문을 통과하지 못했다.

실패 원인은 데이터 구성별로 다르다. deferred 에피소드는 두 번째 근거 세션을 후보에서 제외하므로, 어떤 선택기도 완전한 사실을 제공할 수 없다. revisit 에피소드는 생성 모델이 에피소드별로 정답 근거 세션을 선호하지 않았다.

따라서 **이 초안 시점에는 작동하는 과제 수준 평가가 없다**. 여기서 제시한 주장은 모두 ‘필요한 근거 세션을 끌어올렸는가’라는 메커니즘 평가에 근거한다. 이후 수리 에이전트 평가와 이 초기 생성 평가의 상태를 혼동하지 않아야 한다.

## Datasets

데이터셋마다 정답의 의미가 다르다. 특히 revisit는 한 세션 안에 완전한 근거가 있고, deferred는 근거가 둘로 나뉜다. 따라서 같은 LongMemEval 이름 아래 있어도 두 수치를 서로 바꿔 인용하면 안 된다. 원래 분할·개수·개인정보 경계는 아래와 같다.

- **Natural Claude revisit corpus.** Eight real earlier user turns precede one naturally recurring
  turn; weak label is lexical reuse; entire projects held out. 775 training / 574 evaluation
  episodes. Raw text is not persisted in the repository.
- **ContextBench issue split.** Larger and project-grouped, but synthetically separates one document,
  so it is supporting rather than decisive.
- **LongMemEval-S.** Official cleaned histories with evidence-session IDs, each mixed with seven
  deterministic distractors, question hidden until recall, question IDs held out, target position
  deterministically randomized. Two episode constructions are used and they are **not
  interchangeable**: `revisit` episodes carry complete evidence in one session (890 episodes,
  688/202 split), while `deferred` episodes split evidence across two sessions and place only the
  first in the candidate pool (300 episodes).

## Related design lineage

아래 문헌은 이 구조의 재료가 어디서 왔는지 보여 준다. 선행 구조를 빌렸다는 사실이 이번 과제에서 효과가 있다는 증거는 아니다. 각 링크 옆에는 가져온 설계와 이번 실험에서 확인한 경계를 함께 남겼다.

- The [Differentiable Neural Computer](https://www.nature.com/articles/nature20101) established a
  learned controller with read, write, allocation, and free operations over bounded external state.
- [LongMem](https://arxiv.org/abs/2306.07174) motivates keeping the backbone frozen and training a
  decoupled side network.
- [TTT layers](https://arxiv.org/abs/2407.04620) treat the hidden state as a model updated by an
  inner self-supervised objective.
- [Titans](https://arxiv.org/abs/2501.00663) prioritizes surprising inputs and combines momentum with
  adaptive decay. Our causal surprise feature is a cheap diagnostic precursor, not an implementation.
  Phases 21, 27 and 30 independently find that decay does not help in an error-correcting store,
  which is a boundary on where adaptive-decay designs apply.
- [MIRAS](https://arxiv.org/abs/2504.13173) separates memory structure, attentional-bias objective,
  retention gate, and update algorithm — the four axes of the ablation matrix here.
- [MEMORYLLM](https://arxiv.org/abs/2402.04624) studies a fixed-size self-updatable latent memory pool
  inside a transformer; this layer instead remains independently trainable and attachable.
- [LongMemEval](https://arxiv.org/abs/2410.10813) supplies the public validation source.
- Johnson–Lindenstrauss is the relevant negative prior for Track B: random projections already
  preserve the geometry the retrieval needs, which is what the projection-only control measures.

## Claims that are not supported

이 실험들은 내재적 중요도, 인간과 같은 기억 고착, 끝없는 온라인 학습, 견고한 망각, 또는 **동결 인코더보다 나은 검색**을 보여 주지 않는다. 마지막 항목은 단순한 미검증 사항이 아니라 직접 측정한 부정적 결과다. 이 연구를 어떻게 소개할지 제한하는 가장 강한 근거다.

Track A에는 두 가지 한계가 더 있다. 학습 없이 긴 항목을 고르는 규칙보다 나은 것은 예산이 빡빡할 때뿐이다. 8개 중 3개나 4개를 남기면 그 규칙을 넘지 못한다. 또한 판단 유예는 나중 사건이 질문 자체만큼 정보를 주는 환경에서 시험했다. 제한된 메모리가 명확한 후속 증거를 쓸 수 있다는 결과이지, 먼 미래의 결과를 과거 행동에 어렵게 배분하는 문제를 풀었다는 결과는 아니다.

따라서 논문은 **질문이 가려진 저장 선택의 측정된 상한, 그리고 연상 저장을 검색으로 사용했을 때의 부정적 결과**로 구성해야 한다. 생물학에서 가져온 구성요소 실험은 저장소가 무엇을 보유할 수 있는지 설명하는 보조 근거다. 질문 응답을 개선하는 메모리 시스템으로 소개해서는 안 된다.

## Next decisive experiments

다음 목록은 이 초안이 남긴 검증 순서다. 이미 실패한 설명을 설정만 바꿔 반복하기보다, 기존 측정으로 아직 구분하지 못한 질문을 겨냥한다. 특히 0번의 친숙도 판정은 정답 문서를 찾는 검색과 다른 과제이고, 1번의 합성과 비텍스트 단서는 아직 가설이다. 후속 진행 여부는 `RESULTS.md`의 더 늦은 Phase를 확인해야 한다.

0. Phase 38 tested a fixed-size familiarity gate, which asks a different question from retrieval:
   is anything stored that bears on this cue at all? On 200 matched pairs — the same question asked
   of a store holding its evidence and one with the evidence removed — a graded cell accumulator in
   O(1) state reaches a 0.9700 win rate against 0.9793 for an O(N) reader that keeps every
   embedding, a resolved loss of 0.0093, while beating maximum cosine by 0.0861. It fails the
   criterion fixed in advance and is recorded as a loss, but it is the only mechanism here that
   comes within a point of its baseline. Two things follow for the design: accumulation across many
   weak matches is worth 0.095 over reading the single best, and binarising the accumulator — the
   Bloom-filter rule that won the fly line's recognition test — costs 0.1389 on this one.

1. Establish where an associative store *does* pay, if anywhere. Phase 31 rules out retrieval against
   the same encoder at loads up to 128 sessions, and Phase 34 rules out the in-place update case that
   most favours the write rule: the overwrite is causally real, shown by a write-order reversal that
   flips preference from 0.7949 to 0.2128, and a parameter-free "cosine top-2, take the later" rule
   still beats the store 0.8974 to 0.6333. The remaining candidates are composition across several
   traces and cues that are not embeddings of text. Both are hypotheses, not defences.
2. Re-run the Track B component measurements under the Phase 30 constants rather than the hand-set
   ones. The Phase 22 rescue window in particular was measured at a tag decay of 0.9, and the learned
   value is 0.9964, which should widen it materially.
3. Find a public corpus whose evidence is not length-correlated and whose later evidence degrades
   with distance. Phase 16 shows the Claude margin is semantic and that LongMemEval-S cannot
   corroborate it; Phase 17 adds that LongMemEval-S has no measurable deferral window.
4. Test the remaining teacher correlates the way length was tested: turn position, vocabulary rarity,
   and question form each need an explicit-feature arm before the weak teacher can be called clean.
5. Extend the generator endpoint to several seeds and a second generator, keeping the activation
   metrics as the mechanistic primary endpoint and the validity gate as a precondition for reading
   any of it.
