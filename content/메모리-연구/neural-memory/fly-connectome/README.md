---
title: "초파리 커넥톰 연구 — 실험 기록"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `fly-connectome/README.md` · 수집 2026-10-16 · 커밋 `fd190b18f8e4113d7f451a7108911c1f89716b24`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# fly-connectome

## 읽기 길잡이

실제 초파리 mushroom body의 연결 구조를 사용한 기억 실험이다. 텍스트의 의미 표현과 회로 자체의 계산 특성을 구분해서 읽어야 한다.

1. [실제 생물학에서 가져온 부분과 그렇지 않은 부분](#kb-fly-scope), [데이터 출처](#kb-fly-data)를 먼저 확인한다.
2. [재배선 대조](#kb-fly-control)에서 실제 연결 구조가 어떤 차이를 만드는지 확인한다.
3. 메커니즘 비교는 [Phase 36의 정정](#kb-fly-revision)을 거쳐 [Phase 37의 용량 분석](#kb-fly-capacity)까지 이어서 읽는다. Phase 25의 결론만 떼어 인용하지 않는다.
4. 후속 회로 분석은 [Phase 39](#kb-fly-latest)에 있다.

아래 기록은 실험이 진행된 순서를 보존한다. 전체 연구와의 관계는 [[메모리-연구/커넥톰-읽기|커넥톰 읽기 안내]]에 정리했다.

### 실험의 출발점

이 연구는 `experiments/neural-memory`와 별개의 실험 계열이다. 질문은 **“생물학에서 착안한 규칙만 빌리는 대신 실제 초파리 회로의 연결을 그대로 쓰면, 텍스트 입력을 기억하는 장치가 될까?”**였다. neural-memory 쪽은 희소 확장 비율, 대립 도파민 채널, 구획별 감쇠 같은 메커니즘을 그래프 없는 fast-weight 모델로 추린다(`RESEARCH.md`의 "No graph or external store"). 여기서는 반대로 실제 그래프를 남기고 KC→MBON 시냅스가 경험에 따라 바뀌게 했다.

진행 순서는 텍스트 → 실제 PN 입력 뉴런 → KC의 희소 코드 → 초기 자극 점수 → KC→MBON 쓰기/읽기였다. 처음의 문장 비교 점수는 정답 기준이 없어 주 흐름에서 내려놓았다. 이후에는 ‘같은 입력을 알아보는가’, ‘다른 입력 때문에 얼마나 간섭받는가’, 마지막으로 ‘저장하지 않은 입력과도 구별되는가’로 질문을 구체화했다.

용어는 역할로 읽으면 쉽다. PN은 입력을 받는 뉴런, KC는 많은 뉴런 중 일부만 켜지는 표현 층, MBON은 그 결과를 읽는 출력 뉴런이다. 이 장치는 문서 내용을 복원하는 저장소가 아니라, 가중치가 줄어든 흔적으로 본 적 있는 입력을 구별하려는 모델이다.

## Status overview (35 phases so far)

이 제목의 ‘35 phases’는 당시 기록을 보존한 것이다. 문서 뒤에는 판단을 바꾼 Phase 36–39가 이어진다. 먼저 연구가 어떤 질문으로 갈라지고 다시 모였는지 정리한다.

- **텍스트·기억의 주 흐름(Phase 1–8, 17–28, 34, 36–39):** 실제 mushroom body 배선에 입력을 넣고 KC→MBON 시냅스를 바꿔, 본 적 있는 입력을 알아보는지 시험했다. Phase 34에서는 임의의 부호 분할을 전제로 보상/벌의 두 출력 채널이 올바른 방향으로 작동했다. 하지만 Phase 36에서 ‘덜 닳는 기억이 좋은 기억’이라는 초기 평가를 뒤집었다. 저장하지 않은 문서와의 구별을 재자, Phase 25의 habituated dual-store는 16개 초과 저장에서 가장 나빴고 `eta`가 1에 가까운 단일 저장소가 가장 좋았다. 문서 32개에서는 AUC 약 0.98, 256개에서는 0.63이었다.
- **왜 그 용량이 나오는가(Phase 37):** 전체 KC 수 `m`과 문서당 활성 수 `k`로 Bloom filter의 포화를 예측했다. 코드 간 상관을 없앤 대조는 조정 매개변수 없이 수식과 맞았다. 실제 코드의 상관은 최고 용량을 낮추면서도 완전 포화를 늦췄다. 측정한 최적 희소 비율은 0.02–0.05이며, 실제 APL 억제의 5–10%와 비교하되 텍스트 입력의 특성임을 구분한다.
- **실제 배선의 기여(Phase 38–39):** 연결 수를 보존하고 상대만 바꾼 대조를 이기지 못했다. 실제 KC는 더 적은 구획을 선택했지만, 그 구조가 이 선형 저장 과제에서 기억을 보호하지는 않았다. 해부학에서 보상/벌 구획의 부호를 읽어 낸 결과는 별도로 남는다.
- **재사용 가능한 층(Phase 19, 26):** `fly_memory_layer.py`를 numpy만 필요한 층으로 분리하고 `experiments/neural-memory`의 별도 가상환경 안에서도 실행했다. Phase 26에 옮긴 규칙은 Phase 25 기준의 최선이며, Phase 36 이후의 우승 규칙과 같지 않다.
- **시각(Phase 11–16, 27):** 실제 광수용기와 공간 배치를 사용했다. ‘커피·개·경보’ 같은 사람의 주제 라벨 대신 회로 코드의 유사도를 직접 재자, 비슷한 입력끼리 더 간섭하는 관계가 나타났다.
- **소리(Phase 9, 29–32):** 실제 Johnston's organ 경로를 사용했다. 작은 수렴 회로가 두 결함을 드러냈다. 모든 소리를 한 숫자로 넣은 입력(Phase 30), 활성 여부만 보고 세기는 버린 쓰기(Phase 31)다. 두 가지를 고친 뒤에는 간섭량이 코사인 유사도를 따랐다.
- **냄새(Phase 10, 33):** 문헌으로 특정 냄새 물질과 사구체의 대응을 확인한 7개만 다룬다. 근거 없이 일반 개념으로 확대하지 않는다.
- **외부 데이터(Phase 21, 35):** 다른 인코더가 만든 실제 LongMemEval 임베딩도 파이프라인에 들어갔다. 다만 에피소드 묶음과 `question_type`은 내용 유사도 라벨이 아니어서, 같은 범주/다른 범주의 간섭 차이를 검증하는 데 쓰기 어려웠다.

**실제인 것은 배선과 측정한 계산 특성이다.** 초파리가 텍스트·사진·임의 개념을 이해한다는 실험은 아니다. 다음 절에서 생물학적 자료와 연구자가 만든 입력 변환을 분리한다.

<span id="kb-fly-scope"></span>

## What's actually real here, and what isn't

초파리가 ‘coffee’의 뜻을 안다는 실험은 아니다. 이 파이프라인은 출처가 다른 세 부분을 잇는다.

1. **문장의 의미 유사도**는 사람의 텍스트로 학습한 `all-MiniLM-L6-v2`가 만든다. "a loud alarm"과 "the fire alarm"을 가깝게 표현하는 능력은 이 모델에서 온다.
2. **그 표현을 실제 PN 138개 중 어디에 넣을지**는 연구자가 만든 무작위 행렬 `pn_projection.npy`로 정한다. 실제 냄새 수용체→사구체 대응을 쓰지 않으므로 ‘이 PN은 커피를 나타낸다’고 말할 수 없다.
3. **MaleCNS v1.0에서 가져온 실제 생물학적 자료**는 PN→KC→MBON의 연결 구조와 가중치다. 이후 쓰기·읽기 규칙과 억제의 근사는 연구자가 구현한 모델이다.

따라서 Phase 5–7의 질문은 ‘의미 구조를 가진 임의 입력이 실제 배선을 지날 때, 비슷한 코드끼리 일반화하고 간섭하며 용량 한계를 보이는가?’다. 의미를 인코더가 이미 제공한 만큼, 실제 배선만의 기여를 알려면 연결을 바꾼 대조도 필요하다. 그 비교가 Phase 8이다.

<span id="kb-fly-data"></span>

## Data source

사용한 자료는 **MaleCNS v1.0**이다. 당시 기록의 출처는 Janelia/HHMI + Google Research + Cambridge + MRC LMB(Cell, 2026년 9월)이며, 2026년 6월 공개된 수컷 초파리의 전체 중추신경계(CNS: 뇌와 복측 신경삭) 166,700개 뉴런, 125M+ 시냅스다. `neuprint.janelia.org`에서 조회했다.

당시에는 이를 가장 완전한 공개 커넥톰으로 기술했다. 더 오래된 hemibrain(2020년, 중추 뇌 일부, 약 25k 뉴런)도 `--dataset hemibrain:v1.2.1`로 선택할 수 있다. 이 자료 설명은 수집 당시의 범위이며, 현재 공개 자료 전체의 순위를 새로 조사한 결과는 아니다.

`KC`, `MBON`, `PAM`/`PPL`, `*PN` 같은 세포 분류 패턴은 hemibrain 시기의 이름 규칙에서 왔다. 새 자료에도 같은 이름이 정확히 대응하는지 첫 fetch의 type/ROI 요약과 개수를 확인해야 한다. 실제 데이터를 받았다는 사실만으로 분류가 맞는 것은 아니기 때문이다.

## Phase 1 (this step): load and verify the real circuit

첫 단계는 기억 성능이 아니라 **사용할 회로를 제대로 받았는지** 확인하는 작업이다. `fetch_mushroom_body.py`로 오른쪽 mushroom body(`MB(R)`)에 닿는 모든 추적 뉴런과 그 사이 시냅스를 neuPrint에서 가져와, 연결 세기를 담은 희소 인접 행렬로 저장했다. 아직 동역학이나 텍스트 입력은 없다.

개수의 기준은 `experiments/neural-memory/RESEARCH.md`에 정리한 반구당 대략 PN 50개, KC 2,000개다. 받은 자료가 이와 어느 정도 맞는지 먼저 확인한다.

### Setup

1. https://neuprint.janelia.org 에서 무료 계정과 토큰을 등록한다.
2. `export NEUPRINT_TOKEN=...`
3. `uv sync`

### Run

```
uv run python fetch_mushroom_body.py
uv run pytest
```

출력은 `data/adjacency.npz`(scipy 희소 행렬)와 `data/neurons.parquet`(행렬과 같은 순서의 뉴런 메타데이터)다.

**결과(MaleCNS v1.0, MB(R)):** KC 2,053 / DAN 333 / PN 138 / MBON 75, 시냅스 엣지 1,016,354개였다. KC 수는 알려진 반구당 약 2,000개와 맞는다. 이 확인을 바탕으로 다음 단계에서 회로에 입력을 넣는다.

## Phase 2 (this step): map text onto the real PN neurons

텍스트에는 초파리 회로로 들어가는 실제 감각 경로가 없으므로, 이 단계에서 인위적인 입력 변환을 만든다. `map_text_to_pn.py`는 글을 문장으로 나누고 `all-MiniLM-L6-v2`로 임베딩한 뒤, 고정 무작위 행렬로 실제 PN 138개에 투영한다. 음수 활성은 0으로 자른다.

행렬은 `data/pn_projection.npy`에 저장해 같은 문장이 언제나 같은 PN 패턴으로 들어가게 했다. 아직 KC 전파나 ‘자극 점수’를 정의한 것은 아니며, 문장별 PN 활성 벡터를 만든 단계다.

### Run

```
uv run python map_text_to_pn.py --text "Sentence one. Sentence two."
# or: --text-file some.txt
```

출력 `data/pn_activations.npz`에는 `activations`, `pn_positions`, `pn_ids`, `sentences`가 들어간다. `pn_positions`는 bodyId 정렬 순서가 아니라 `adjacency.npz`의 행·열 위치다. Phase 3은 이 위치를 사용해 실제 그래프의 올바른 뉴런에 입력을 주입한다.

## Phase 3 (this step): propagate PN activity to the KC layer

이제 문장 입력이 실제 배선을 지나 서로 다른 코드가 되는지 본다. `kc_response.py`는 PN 활성을 전체 회로 벡터의 해당 위치에 놓고, 실제 가중 인접 행렬을 따라 한 번 전파한 뒤 KC만 읽는다.

KC 구동값 중 상위 약 10%(`keep_ratio`)만 남기고 나머지는 0으로 만든다. 이는 APL 억제를 대신하는 근사이며, Lin et al. 2014의 5–10% 희소 활성 범위를 참고했다. 회로가 모두 비슷하게 켜지는 것을 막아, 어떤 KC가 켜졌는지가 입력을 나타내게 한다.

### Run

```
uv run python kc_response.py
```

출력은 `data/kc_codes.npz`의 `kc_codes`, `sentences`다. **시험 문장 3개에서 KC 2,053개 중 각각 205개가 활성화**됐다. 활성 개수는 `keep_ratio`가 정하지만 평균 구동값은 0.457 / 0.572 / 0.594로 달랐다. 모든 문장에 상수 응답을 내는 퇴화 상태는 아니라는 것을 확인했다.

## Phase 4: a first stimulus-scoring attempt (weak, no ground truth)

처음에는 기억 대신 ‘눈에 띄는 문장’의 점수를 만들려 했다. `stimulus_points.py`는 한 문장의 활성 KC 집합과 같은 입력에 든 다른 문장들의 집합이 얼마나 겹치는지 Jaccard로 재고, 평균 겹침을 1에서 뺀다. 원시 세기의 코사인보다 희소 활성 집합의 겹침을 보는 후각 연구 방식에 맞춘 선택이다.

시험 문장 3개의 결과는 coffee 0.864 > fire alarm 0.841 > typing 0.795였다. 그러나 어느 문장이 더 중요해야 하는지 정답이 없고, 세 문장끼리만 비교하므로 이 순위에 의미를 부여하기 어렵다. ‘보통 문장’의 기준 말뭉치도 만들지 않았다.

도구 자체는 작동한다(`uv run python stimulus_points.py`, 입력 `data/kc_codes.npz`). 하지만 **검증되지 않은 자극 점수로 남겨 두고**, 다음 Phase 5부터는 실제로 쓰고 다시 읽을 수 있는 기억을 만드는 데 집중했다.

## Phase 5 (this step): real write/recall memory on KC->MBON

여기서부터 질문은 ‘중요해 보이는가?’에서 **‘한 번 경험한 입력이 회로를 바꾸고, 다시 읽을 때 그 흔적이 보이는가?’**로 바뀐다. `memory.py`는 실제 KC→MBON 가중치(이 자료에서는 KC 2,053 × MBON 75)를 잘라 사용한다.

- **쓰기(write):** 현재 활성 KC에 해당하는 가중치 행을 일정 비율 `eta`(기본 0.3)만큼 줄인다. Owald et al. 2015의 mushroom body 출력 시냅스 억압을 참고했다. MBON 이름만으로 구획의 보상/벌 부호를 알 수 없어 임의 부호를 붙이지 않고, 모든 쓰기는 일단 억압만 한다.
- **읽기(recall):** 현재 KC 활성과 현재 가중치를 곱해 MBON 구동값을 계산한다. 같은 입력을 이미 썼다면 그 행이 줄었으므로 반응도 낮아져야 한다. 낮아진 반응이 이 장치의 ‘본 적 있음’ 신호다.

검증 가능한 예측은 단순하다. 정확히 같은 KC 코드를 두 번 읽되 그 사이에 첫 쓰기를 하면 두 번째 반응이 더 낮아야 한다. 실제 데이터에서 "The fire alarm rang loudly in the empty hallway."를 다시 넣자 109,716에서 64,212로 **-41%** 줄었다. 아직 본 적 없는 다른 세 문장은 109k–136k 범위였다. 이후 단계에서는 이 감소가 입력별 기억인지 전역적인 약화인지 더 엄격히 구분한다.

### Run

```
uv run python memory.py
```

## Phase 6: does it generalize, or only recognize exact repeats?

똑같은 문자열에만 반응한다면 기억의 범위는 좁다. `generalization_probe.py`는 한 문장을 저장한 뒤, 아직 쓰지 않은 바꿔 쓴 문장(paraphrase)과 무관한 문장을 읽는다. 둘 다 새 입력이므로, 차이가 나면 정확한 반복 이외의 공통 코드가 영향을 준 것이다.

원문 "The fire alarm rang loudly in the empty hallway."와 바꿔 쓴 "A loud alarm blared through the deserted corridor."는 활성 KC 205개 중 118개를 공유했고, 무관한 대조는 34/205개만 공유했다. 원문을 쓴 뒤 반응 감소도 paraphrase는 18.1%, 대조는 5.2%였다.

즉 비슷하지만 동일하지 않은 사건이 공유 KC만큼 부분적으로 간섭했다. 다만 문장 의미의 유사도는 텍스트 인코더가 제공하고 실제 배선은 그 표현을 KC 코드로 바꾼다. 이것을 초파리의 언어 이해로 해석하지 않는다.

### Run

```
uv run python generalization_probe.py
```

## Phase 7: capacity -- does interference stay contained, or does it accumulate?

입력 하나의 흔적은 보였다. 다음 문제는 **다른 입력을 계속 쓰면 그 흔적도 무한히 약해지는가?**다. `capacity_probe.py`는 4개 주제에서 서로 가까운 표현 3개씩, 총 12문장을 순서대로 쓰며 매 쓰기 뒤 모든 문장의 반응을 기록했다.

한 문장을 쓸 때 다른 문장에 미치는 평균 간섭은 같은 주제 -10.31%(n=24), 다른 주제 -6.55%(n=108)였다. 비슷한 문장끼리 더 크게 간섭하지만, 무관한 문장도 영향을 피하지 못했다.

처음 저장한 문장은 자기 쓰기 직후 -30.0%였고, 이후 3/6/11개를 더 쓰면 **-50.1% → -61.2% → -71.2%**로 계속 내려갔다. 당시에는 이를 용량의 문제로 해석했다. 모든 활성 KC를 무조건 줄이면 어느 쓰기든 다른 기억을 조금씩 건드리고 그 효과가 누적되기 때문이다.

다음 후보는 `RESEARCH.md`가 Jeong et al. 2021에서 정리한 **대략 고정된 예산 아래의 경쟁적 할당**이었다. 일부 입력을 강화할 때 전체 활성 집단의 규모는 제한된다는 생각을 가져와, 총 가중치나 쓰기량을 제한하면 누적 간섭을 줄일 수 있는지 시험하기로 했다. 단, 이 단계의 감소 곡선은 아직 저장/미저장 항목의 구별 능력을 직접 잰 것이 아니며, Phase 36에서 그 한계가 드러난다.

### Run

```
uv run python capacity_probe.py
```

## Phase 7b: does a fixed plasticity budget fix it?

먼저 가장 단순한 예산 제한을 시험했다. `memory.write_budgeted()`는 기존처럼 억압한 다음 **전체 가중치 행렬의 총합이 유지되도록** 다시 비례 조정한다. Jeong et al.의 ‘대략 일정한 회상 활성 집단’을 전역 재조정으로 근사한 것이다. 실행은 `capacity_probe.py --write-mode budgeted`다.

처음 항목의 반응은 이후 0/3/6/11회 쓰기에서 **-27.7% → -43.7% → -52.8% → -60.6%**였다. 예산 없는 쓰기의 -30.0% / -50.1% / -61.2% / -71.2%보다 마지막 감소가 약 10pt 작지만, 여전히 계속 줄었다. 같은/다른 주제 간섭은 -7.95% / -4.09%로 비율 1.94x였고, 기존은 1.57x였다.

결론은 일부 완화이지 해결은 아니다. 전역 재조정은 건드리지 않은 시냅스를 조금씩 올려 평균 손실을 보상하지만, 특정 기억끼리 부딪히는 것을 막지는 않는다. 그래서 이후 Phase 17에서는 전체 행렬이 아니라 현재 활성 KC들 사이에서 쓰기 예산을 나누는 방식을 시험한다.

<span id="kb-fly-control"></span>

## Phase 8: real connectome vs. a matched random control

지금까지 보인 일반화가 실제 초파리 배선 덕분인지, 의미 임베딩을 희소 코드로 바꾸면 어떤 배선에서도 생기는지 분리해야 한다. `kc_response.random_rewire()`는 **엣지 수와 가중치 값은 같게 두고 각 엣지의 도착 뉴런을 균일 무작위로 바꾼** 대조를 만든다. Phase 7과 같은 시험을 `capacity_probe.py --random-control`로 돌렸다.

이 대조는 크기와 가중치를 맞춘 것이며, 각 뉴런의 연결 수까지 보존한 Phase 38의 대조와는 다르다. 아래 마지막 열은 Phase 7과 같은 11회 추가 쓰기 후의 누적 반응 감소다.

| | same-topic | diff-topic | ratio | load @ 11 writes |
| --- | --- | --- | --- | --- |
| real | -10.31% | -6.55% | 1.57x | -71.2% |
| random | -12.80% | -8.62% | 1.49x | -81.2% |

같은 주제/다른 주제의 간섭 비율은 실제 1.57x, 무작위 1.49x로 큰 차이가 없었다. ‘비슷한 문장이 더 간섭한다’는 행동의 상당 부분은 텍스트 임베딩과 희소화에서 온다고 보는 편이 맞다.

실제 배선에서 더 나았던 것은 누적 감소가 -71.2%로 무작위의 -81.2%보다 덜했다는 점이다(반올림하면 -71% 대 -81%). 이 시점의 결론은 의미 구별을 크게 더한다는 것이 아니라 **같은 시험에서 반응 감소가 조금 덜 심했다**는 것이다. 이 역시 Phase 36의 저장/미저장 구별로 재평가해야 하며, 초기 감소 지표만으로 일반적인 기억 용량 우위를 확정하지 않는다.

### Run

```
uv run python capacity_probe.py --random-control
```

## Phase 9: a circuit with a real transduction pathway (sound, not text)

Phase 8에서 확인했듯 텍스트 입력에는 실제 감각 경로가 없었다. 그래서 회로에 들어가는 변환 자체도 생물학에 근거할 수 있는 소리를 살펴봤다. 근거리 소리는 물리적 진동 → 더듬이 → Johnston's organ(JO) 기계수용 뉴런 → AMMC라는 실제 경로가 있다. 이런 입력이라면 텍스트용 무작위 투영을 대신할 근거를 찾을 수 있다.

`fetch_johnstons_organ.py`는 MaleCNS v1.0의 AMMC(R)를 가져온다. 회로 받기·인접 행렬·저장 코드는 `fetch_mushroom_body.py`와 `connectome_io.py`로 공유한다. 자료의 `type`에 실제 JO 하위 집단 이름이 있으며, Kamikouchi et al. 2009에 따르면 집단 수준에서 JO-A/B는 소리·진동, JO-C/E는 중력·바람에 반응한다. JO-B1_a와 JO-B1_b처럼 더 세부적인 조율까지 이 프로젝트에서 검증한 것은 아니다.

**AMMC(R) 결과:** JO-E 113, JO-F 32, JO-C 20, JO-B 11, JO-A 2개였다. 나머지 2,631개는 JO 구심성 뉴런이 아니라 국소/하류 AMMC 뉴런이며, 시냅스 엣지는 326,667개다. 여기서 소리 반응 집단 A+B는 **13개**뿐으로, 텍스트에 쓴 PN 138개보다 훨씬 적다. 왼쪽 AMMC(L)에 더 있는지, 새 데이터의 세부형 교정이 덜 된 것인지는 확인하지 않았다. 작은 입력 집단의 제약은 뒤의 소리 실험에서 중요해진다.

### Run

```
NEUPRINT_TOKEN=... uv run python fetch_johnstons_organ.py
```

다른 회로이므로 출력도 mushroom body의 `data/`와 분리해 `data_ammc/adjacency.npz`, `data_ammc/neurons.parquet`에 저장한다.

## Phase 10: a grounded text->PN converter (small, only for known odorants)

텍스트 전체에 생물학적 의미 대응을 만들 수는 없지만, **문장에 특정 냄새 물질이 명시될 때만** 실제 대응을 쓸 수는 있다. `odor_embedder.py`는 문헌 근거가 강한 작은 집합에 한해 무작위 투영을 바꾼다. 이 자료의 PN `type`은 `DA2_lPN`처럼 사구체 이름을 포함하므로 실제 뉴런을 찾을 수 있다.

사용한 근거는 geosmin → DA2(Stensmyr et al. 2012), acetic acid/vinegar → DM1과 ethanol → DM2(Hallem & Carlson 2006), CO2 → V(Suh et al. 2004), cVA 페로몬 → DA1(Kurtovic et al. 2007)이다. MB(R) 자료에서 해당 사구체의 PN 이름이 모두 존재함을 확인했다. 지정 물질이 없으면 `map_text_to_pn.py`의 무작위 투영으로 돌아가며 문장별 사용 방식을 표시한다.

예를 들어 "The soil smelled of geosmin after the rain."은 `grounded:DA2`로 실제 DA2_lPN 5개를, "She poured vinegar into the salad dressing."은 `grounded:DM1`로 DM1_lPN 1개를 활성화했다. fire alarm과 coffee는 그대로 `random-fallback`이다. 이는 그 물질 이름의 제한된 대응이며 문장 전체 의미의 생물학적 변환은 아니다.

### Run

```
uv run python odor_embedder.py --text "..."
uv run python kc_response.py
uv run python memory.py
```

출력은 기존과 같은 모양의 `pn_activations.npz`에 `methods` 필드만 더한다. 따라서 `kc_response.py`와 `memory.py`를 바꾸지 않고 앞단만 교체할 수 있다.

처음에는 grounded 입력의 MBON 반응이 훨씬 컸다. geosmin 242,623 / vinegar 534,798, 무작위 경로의 fire-alarm 109,716 / coffee 142,196이었다. 하지만 이는 냄새가 더 두드러진다는 발견이 아니라 **입력 크기를 맞추지 않은 문제**였다. grounded 경로는 PN 5개 또는 1개에 각각 1.0을 넣었고, 무작위 경로는 훨씬 작은 평균 세기를 65개에 나눴다.

`reference_pn_magnitude()`로 중립 문장의 무작위 경로에서 뉴런당 전형적 세기를 측정해 1.0 대신 사용했다. 보정 뒤 geosmin 9,368 / vinegar 20,650, fire-alarm 109,716 / coffee 142,196으로 grounded 쪽이 더 낮아졌다. 뉴런당 세기를 같게 맞추고 훨씬 적은 채널(1–5 대 65)에 넣었으니 총 하류 신호가 작아지는 것이 맞다. 비교 전에 입력 규모를 맞춰야 한다는 사례다.

## Phase 11: a circuit with a real transduction pathway (vision, general-purpose)

시각으로 범위를 넓힌 계기는 DOOMFLY(github.com/nftechie/doomfly, Alex Wormuth)였다. 당시 공개 기록은 같은 커넥톰의 광수용기에 ViZDoom 영상을 넣고(R1–R6 밝기 3,335개 + R8 색 입력 811개), 실제 하행 뉴런을 게임 조작에 연결했다. 피해 신호는 PPL101 도파민 세포를 통해 KC→MBON11 시냅스 4,184개에 강화 신호로 주었다. 다만 6회 반복 뒤에도 학습된 생존 향상을 입증하지 못했다고 보고했다. 실제 배선을 쓰는 것만으로 학습 성공을 기대해서는 안 된다는 참고점이다.

시각은 냄새보다 임의 입력을 넣기 쉽다. 빛의 세기에서 광수용기 반응으로 가는 경로가 있고, 개념별 대응표 없이 어떤 이미지든 받을 수 있기 때문이다. 그러나 실제 감각 변환을 쓴다고 ‘커피잔’을 알아보는 것은 아니다. 초파리 시각계가 다루는 운동·대비·색 대립과 사람의 물체 개념은 다르다. 텍스트를 이미지로 생성해 넣어도 의미를 빌리는 위치만 생성기로 옮길 뿐이다.

`fetch_optic_lobe.py`로 MaleCNS v1.0의 `LA(R)`(lamina)를 가져왔다. 약 7k 뉴런으로 mushroom body와 비슷한 규모다. 다음 단계인 `ME(R)`(medulla)는 약 43k여서 첫 실험 범위에서는 제외했다. 초기에는 광수용기 R1–R8의 경로를 함께 보려 했으나, R7/R8의 실제 종착 위치는 Phase 13에서 다시 확인한다.

**결과:** R1–R6 893개, R7/R8 세부형(색/UV/dorsal-rim) 468개, 하류 lamina 뉴런 5,384개, 시냅스 엣지 47,731개를 얻었다.

### Run

```
NEUPRINT_TOKEN=... uv run python fetch_optic_lobe.py
```

출력은 `data_optic/adjacency.npz`, `data_optic/neurons.parquet`다.

## Phase 12: real (downloaded, not generated) images through the real photoreceptors

Phase 11에서 제기한, 이미지를 생성하는 모델의 의미를 빌리는 문제를 피하기 위해 `image_to_photoreceptors.py`는 실제 사진을 받았다. Wikimedia Commons의 CC 라이선스 커피잔·달리는 개·화재 경보 사진이다. 회색조를 크기 조정해 펼친 값을 R1–R6 893개에, RGB 채널 평균을 R7/R8 집단의 색 대용값으로 넣고 실제 `LA(R)` 배선을 한 번 통과시켰다.

이때는 **망막의 실제 공간 배치(retinotopy)가 없었다.** 뉴런 표에 나온 순서대로 픽셀을 넣었으므로 모서리와 형태의 위치를 보존하지 못하고 대략적인 밝기·색 통계만 전달했다. 하류 L1–L5 등에서 사진마다 다른 반응은 나왔지만, 서로의 코사인 유사도는 0.907–0.940으로 매우 높았다(커피/개 0.907, 커피/경보 0.907, 개/경보 0.940).

따라서 이 단계에서 확인한 것은 실제 사진이 끝까지 처리된다는 점이다. 물체 구별은 약했고, 그 원인을 시험하기 위해 다음에는 사진이나 수식 대신 **입력이 놓이는 실제 위치**를 바로잡는다.

### Run

```
uv run python image_to_photoreceptors.py
```

## Phase 13: real retinotopy instead of arbitrary photoreceptor order

Phase 12의 임의 순서가 공간 정보를 버렸는지 확인했다. `fetch_retinotopy.py`는 각 R1–R6 뉴런의 실제 `LA(R)` 시냅스 위치를 받아 중심점을 구한 뒤, 3차원 중심점들을 PCA로 2차원에 투영한다. lamina가 대략 얇은 판 형태라는 점을 이용한 공간 배치 복원이며, 별도의 해부학 주석 없이 `data_optic/retinotopy.npz`에 저장했다.

R7/R8에는 같은 방법을 쓸 수 없었다. `LA(R)`의 시냅스 조회가 0건이었는데, 이들은 lamina를 지나 medulla의 `ME(R)`에 시냅스를 맺기 때문이다. 버그로 채워 넣지 않고, 아직 받지 않은 약 43k 뉴런의 medulla 경로는 남겨 두었다. R7/R8은 Phase 12의 거친 균일 색 대용값을 계속 쓴다.

R1–R6는 **893/893개 모두 실제 위치를 얻었다.** 평면성 검사인 세 번째/두 번째 PCA 특잇값 비율은 0.309로, 완전한 평면은 아니지만 복안의 굽음과 맞는 정도였다. `image_to_photoreceptors.py`는 `retinotopy.npz`가 있으면 표 순서로 펼치는 대신 실제 위치에서 쌍선형 샘플링한다.

이미지와 인코딩 수식을 그대로 두고 위치만 고친 결과, 커피/개 쌍은 거의 같지만 경보 사진과 다른 두 사진의 유사도는 낮아졌다.

| pair | phase 12 (arbitrary order) | phase 13 (real retinotopy) |
| --- | --- | --- |
| coffee vs dog | 0.907 | 0.906 |
| coffee vs fire alarm | 0.907 | 0.775 |
| dog vs fire alarm | 0.940 | 0.802 |

공간 배치를 복원한 효과는 관찰됐다. 다만 893개의 ‘픽셀’과 lamina의 한 번 전파만 쓴 작은 중계 회로다. 결론은 ‘retinotopy가 구별에 도움을 줬다’이며, 초파리가 사진 속 물체를 알아봤다는 것은 아니다.

### Run

```
NEUPRINT_TOKEN=... uv run python fetch_retinotopy.py   # once, produces retinotopy.npz
uv run python image_to_photoreceptors.py               # picks it up automatically
```

## Phase 14: write/recall memory on the vision circuit

시각에도 쓰기/읽기를 붙였지만 첫 결과는 가짜 기억이었다. R1–R6의 원시 활성으로 `memory.write()`와 `mbon_drive()`를 그대로 적용하자, 어떤 사진을 써도 커피·개·경보가 모두 정확히 -30.0% 줄었다. 실제 사진은 R1–R6를 거의 100% 켜기 때문에 행렬 전체가 함께 약해졌던 것이다. 무작위 투영의 ReLU로 약 50%가 희소한 텍스트 PN 입력과 달랐다.

그래서 텍스트 파이프라인의 구조를 맞췄다. 조밀한 R1–R6 입력을 하류 lamina의 ‘other’ 뉴런(L1–L5, amacrine 등)까지 한 번 전파한 뒤, `kc_response.sparse_code`로 상위 10%만 남긴다. 이 희소 코드를 실제 lamina의 `other → other` 순환 시냅스에 쓰고 읽는다. KC/MBON과 기능적으로 대응시킨 모델이며, medulla를 받지 않은 범위에서 쓸 수 있는 회로다.

Phase 12/13에서 보인 약한 구별과 마찬가지로, 수정 뒤 이미지 간 활성 집합의 겹침은 여전히 높았다(커피/개 0.666, 커피/경보 0.578, 개/경보 0.546). 하지만 커피를 쓰면 커피 자체 -30.0%, 더 많이 겹치는 개 -25.9%, 덜 겹치는 경보 -25.1%로 **일괄 감소가 아닌 단계적인 간섭**이 나왔다. Phase 6의 텍스트처럼 실제 겹침과 순서가 맞았다.

그렇다고 사람의 주제별로 구별되는지는 별개였다. Wikimedia Commons 사진을 주제당 2개씩, 커피·개·경보 3주제로 늘리고 `images_cache/`에 캐시했다. 같은 주제 간섭 -25.75%(n=6), 다른 주제 -25.97%(n=24)로 차이가 없었다. 겹침도 주제와 무관하게 0.55–0.74의 좁은 범위였다. 커피잔/원두는 같은 주제인데 0.673, 커피잔/연기 감지기는 다른 주제인데 더 높은 0.730이었다.

이 해상도에서는 주제 분리를 찾지 못했다. Phase 8 텍스트의 무작위 대조까지 포함한 1.49x–1.57x 같은/다른 주제 비율보다도 약했다. 당시에는 893 ‘픽셀’, 거친 비공간 색 입력, 한 번 전파의 한계로 해석했다. 이후 Phase 16·27에서는 **주제 라벨 자체가 회로가 보는 시각 유사도를 나타내는지** 다시 점검한다.

### Run

```
uv run python vision_memory_probe.py
```

## Phase 16: local contrast instead of raw brightness

앞선 입력은 원시 밝기를 사용해 배경 조명과 구도의 영향이 컸다. 실제 lamina의 L1–L5는 밝기 자체보다 대비·모서리에 반응하는 채널이라는 점에서, `contrast_map()`으로 입력을 바꿨다. 원본 회색조에서 강하게 흐린 이미지를 빼는 고역 통과 필터를 적용한 뒤 실제 위치에서 샘플링한다.

겹침의 범위는 기존 0.546–0.740에서 **0.330–0.708**로 넓어졌다. 이미지 차이를 더 잘 반영하는 코드가 됐지만, 같은/다른 주제 간섭은 -20.24% / -19.00%로 여전히 뚜렷하게 나뉘지 않았다.

직접 쌍을 확인하자 평가 라벨의 문제가 보였다. 종/연기 감지기는 같은 주제이며 겹침 0.679로 높다. 둘 다 벽에 붙은 둥근 물체 사진이다. 반면 커피잔/원두는 0.425, 서로 다른 개 사진 shaggy/golden은 0.452였다. 같은 ‘커피’나 ‘개’라는 이름이 모양·자세·구도의 유사성을 보장하지 않는다.

따라서 대비 입력이 실패했다고 단정할 수 없다. **사람의 의미 범주와 회로에 들어가는 대비·형태는 다른 기준**이었다. 공정하게 재시험하려면 비슷한 자세·구도·윤곽의 이미지를 고르거나 코드 유사도를 직접 재야 한다. 후자의 비교가 Phase 27이다.

## Phase 17: a properly localized competitive budget -- and the trade-off it exposes

Phase 7b의 전역 재조정은 누적 감소를 막지 못했다. 이번에는 `RESEARCH.md`의 `a = sparse_competition(...)`, `sum(a) = 1`에 맞춰 현재 활성 KC끼리만 고정 쓰기 예산을 나눴다. `memory.write_competitive()`는 각 KC의 활성 세기에 비례해 억압량을 배정한다. 따라서 켜진 KC가 많다고 총 억압량도 함께 커지지 않는다. `memory.py`와 `capacity_probe.py` 모두 `--write-mode`로 `unbudgeted`, `budgeted`, `competitive`를 고를 수 있다.

Phase 7과 같은 시험에서 11회 추가 쓰기 후 감소는 기존 -71.2%, 전역 예산 -60.6%, **경쟁 예산 -0.7%**였다. 이 숫자만 보면 침식 문제를 거의 해결한 듯했다.

하지만 정확히 같은 문장을 반복했을 때의 신호도 함께 사라졌다. fire-alarm 반응이 109,716에서 109,444로 **-0.25%**만 줄었다. Phase 5에서 기존 방식으로 확인한 -41%와 크게 다르다. 실행 옵션은 `--write-mode competitive`다. `eta=0.3`을 약 205개 KC에 나누니 KC당 변화가 약 0.15%에 그쳤다.

즉 기억을 잘 지켜서 덜 닳은 것인지, 애초에 거의 쓰지 않아 덜 닳은 것인지 구분해야 했다. 단일 평탄 예산에서는 누적 감소를 낮추면 항목별 재인식 신호도 약해졌다. 당시 다음 후보로 택한 것은 `RESEARCH.md`의 서로 다른 시간상수의 병렬 저장소(measurement 4)와 synaptic-tagging 구제 창(measurement 7)이었다. 이 단계에서는 아직 구현 전이며, 이후 Phase 36은 ‘감소량만으로 용량을 평가한 것’ 자체도 다시 검토한다.

### Run

```
uv run python capacity_probe.py --write-mode competitive
uv run python memory.py --write-mode competitive
```

## Phase 18: two stores, different decay, read as a sum

Phase 17의 문제는 한 저장소에서 강한 첫 흔적과 적은 누적 손실을 동시에 얻기 어렵다는 것이었다. `dual_store_probe.py`는 `RESEARCH.md` measurement 4를 따라 빠른 저장소(`eta=0.5`)와 느린 저장소(`eta=0.03`)를 함께 쓴다. 모든 사건을 양쪽에 쓰고 읽을 때 두 반응을 더한다. 빠른 쪽은 재인식 신호를, 느린 쪽은 덜 침식되는 성분을 맡기려는 설계다.

| | exact-repeat recognition | load after 11 writes |
| --- | --- | --- |
| unbudgeted (phase 5/7) | -41% | -71.2% |
| competitive (phase 17) | -0.25% | -0.7% |
| **dual (fast+slow), phase 18** | **-26.5%** | **-49.6%** |

두 극단 사이의 값이 나왔다. 같은/다른 주제 간섭도 -5.82% / -3.56%, 약 1.64x로 돌아왔고 기존 1.57x와 비슷했다. 당시에는 재인식 신호를 유지하면서 기존 쓰기보다 누적 감소를 줄인 첫 방법으로 판단했다. `eta` 0.5/0.03은 최적화한 값이 아니라 첫 시도다.

여기서의 ‘더 나은 용량’은 아직 위 표의 감소 지표에 한정된다. Phase 22에서 매개변수를 바꾸고, Phase 36에서는 저장한 항목과 안 한 항목을 구별하는 기준으로 이중 저장소의 필요성을 다시 판단한다.

### Run

```
uv run python dual_store_probe.py
```

## Phase 19: extracted as a standalone memory layer

기억 장치가 특정 데이터 수집 코드에 묶여 있으면 다른 프로젝트에서 시험하기 어렵다. 그래서 Phase 18의 빠른/느린 이중 저장소만 `fly_memory_layer.py`로 분리했다. `FlyMemoryLayer`는 numpy의 KC × MBON 가중치 행렬만 받으며, neuPrint·임베딩·문장/이미지 인코더를 알 필요가 없다. `from_mushroom_body_data_dir()`는 이미 받은 `.parquet`/`.npz`를 읽는 편의 함수여서 토큰이나 네트워크도 필요 없다.

인터페이스는 `experiments/neural-memory/neural_memory/*.py` 옆에서 쓸 수 있게 맞췄다. torch 의존성은 추가하지 않고 numpy를 유지했다. 에피소드별 가중치는 고정 dataclass `FlyMemoryState`에 담고(`MemoryState`/`FastWeightState`와 대응), `write(state, kc_code) -> FlyMemoryState`는 원본을 바꾸지 않고 새 상태를 반환한다. `read`·`write`의 `kc_code` 입력은 `[batch, n_kc]`이며 1D 입력은 batch 1로 취급한다. 이는 다른 프로젝트의 `write(...) -> State` 규약과 배치 처리에 맞춘 것이다.

독립성을 확인하려고 `demo_extracted_layer.py`에서 `fly_memory_layer.py`만 가져와 실제 캐시 가중치로 재인식을 실행했다. `kc_response.py`, `memory.py`, `generalization_probe.py`, `capacity_probe.py`는 import하지 않는다.

```
drive=219,432  (first time)   The fire alarm rang loudly in the empty hallway.
drive=256,598  (first time)   She kept typing her report, unaware of the noise.
drive=278,486  (first time)   A cup of coffee sat cold on the desk.
drive=145,060  (repeat, -33.9%)   The fire alarm rang loudly in the empty hallway.
```

같은 입력의 재등장에 -33.9% 감소가 나왔다. KC 공간의 코드 벡터만 공급하면, 그 코드를 텍스트로 만들었는지 다른 방법으로 만들었는지와 무관하게 별도 기억 층으로 쓸 수 있음을 확인한 것이다. 이것은 통합 가능성 시험이며 다른 과제의 성능 향상 시험은 아니다.

실제로 `experiments/neural-memory`의 자체 가상환경에 붙일 때는 한 번 실패했다. `from_mushroom_body_data_dir()`가 부르는 `fetch_mushroom_body.cell_class`의 모듈 수준 `from neuprint import Client`가 pandas·scipy·neuprint-python까지 끌고 왔는데, 그 환경에는 없고 기억 층 자체에도 필요하지 않았다.

해결은 수집 환경에서 `export_memory_weights.py`를 한 번 실행해 실제 KC→MBON 행렬만 `data/kc_mbon_weights.npy`로 내보내는 것이었다. 그 뒤 `experiments/neural-memory/fly_memory_integration_check.py`가 이 `.npy`를 `np.load`로 직접 읽어, numpy + torch만 있는 `.venv`에서 정확히 같은 결과를 냈다.

```
running in: experiments/neural-memory/.venv
layer: 2053 KC x 75 MBON
drive=219,432 (first time) / 256,598 (first time) / 278,486 (first time) / 145,060 (repeat, -33.9%)
```

### Run

```
uv run python demo_extracted_layer.py

# cross-project attach check:
uv run python export_memory_weights.py                                # in fly-connectome, once
cd ../neural-memory && uv run python fly_memory_integration_check.py   # in neural-memory
```

## Phase 26: extracted layer upgraded to phase 25's mechanism

Phase 19에서 분리한 `FlyMemoryLayer.write()`는 Phase 18의 단순 이중 저장소였다. 이후 Phase 25의 당시 최선인 **habituated dual-store**로 바꾸었다. 각 저장소가 자기 행의 남은 freshness에 따라 `eta`를 줄이는 방식이다.

단독 `demo_extracted_layer.py`와 `neural-memory` 자체 가상환경의 `fly_memory_integration_check.py`를 다시 실행해 재인식 감소가 계속 나오는지 확인했다. 기존 테스트는 새 habituation 검사 하나 외에 바꿀 필요가 없었다. 건드리지 않은 행의 freshness는 1.0이므로 새 상태의 첫 쓰기는 기존 고정 `eta` 규칙과 수치적으로 같기 때문이다.

이 절이 Phase 19 바로 뒤에 있는 것은 추출 층의 변경 이력을 함께 보여 주기 위해서다. **여기서 ‘최선’은 Phase 25의 옛 지표 기준**이다. Phase 36은 그 선택을 뒤집었으므로, 이 업그레이드를 최신 재인식 성능의 최적 구현이라고 읽지 않는다.

## Phase 20: the synaptic-tagging rescue window (measurement 7)

약하게 저장한 기억을 나중의 강한 사건이 살릴 수 있는지 시험한다. `experiments/neural-memory/analyze_tagging_window.py`에서 이미 확인한 설계(git log: "a fading tag produces the rescue window the corpora could not show")를 실제 KC→MBON 억압에 옮겼다.

기존 프로젝트는 연상 outer-product 저장소여서 읽은 값과 저장값의 코사인을 봤다. 여기서는 억압만 하므로 ‘더 강한 기억’은 더 큰 억압 흔적을 뜻한다. 약한 쓰기 때 실행하지 못한 억압량 `strong_eta - weak_eta`를 KC별 tag로 남기고, 이후 쓰기마다 tag를 줄인다. 나중에 강한 사건이 오면 아직 남아 있는 tag에 추가 억압을 적용하는 capture 신호를 보낸다.

강한 사건은 원래 항목과 무관해도 된다. 내용이 아니라 세기만 제공한다는 기준("the event contributes only magnitude")을 지킨다. `tagging_rescue_probe.py`는 실제 MB(R) 회로와 문장 20개에서, 약한 쓰기와 강한 사건 사이에 몇 번의 쓰기가 끼었는지 바꿨다.

| gap (intervening writes) | recovered_fraction |
| --- | --- |
| 0 | 0.665 |
| 1 | 0.465 |
| 2 | 0.326 |
| 4 | 0.160 |
| 8 | 0.038 |

강한 사건이 즉시 오면 처음부터 강하게 썼을 때까지의 차이 중 66.5%를 회복했지만, 8회가 끼면 3.8%만 회복했다. 간격이 길수록 구제 효과가 줄어드는 창이 나왔다. 강한 사건의 KC가 목표와 전혀 겹치지 않아도 구제가 된다는 단위 테스트도 통과했다. 이 결과는 tag와 capture의 설계된 시간 창을 확인하며, 의미가 같은 사건만 강화된다는 주장은 아니다.

### Run

```
uv run python tagging_rescue_probe.py
```

## Phase 21: real LongMemEval document embeddings, not our own sentences

직접 고른 문장에서만 작동하는지 확인하려고 실제 외부 문서로 입력을 바꿨다. `longmemeval_capacity_probe.py`는 `experiments/neural-memory/artifacts/longmemeval_deferred.pt`의 후보 임베딩을 Phase 7의 간섭 시험에 넣는다. 실제 대화 문서이며 `all-MiniLM-L6-v2`와 다른 인코더가 만들었지만, 384차원이라 기존 `pn_projection.npy`와 그대로 맞았다.

여기서는 `neural-memory`의 `gist_recovery`/`surface_recovery`(`analyze_load_and_gist.py`)를 계산하지 않았다. 그 지표는 delta-rule 연상 저장소가 저장한 **내용 벡터**를 복원하는지 묻는다. KC→MBON 억압 장치에는 복원할 값 벡터가 없고, 본 적 있는지와 다른 입력이 얼마나 간섭하는지만 읽는다. 서로 다른 기억 기능이므로 같은 지표의 낮은 성능으로 취급하지 않는다.

LongMemEval 자체의 에피소드당 후보 8개 묶음을 이용해, 4개와 20개 에피소드에서 같은/다른 에피소드의 간섭을 비교했다.

| episodes | same-episode | different-episode |
| --- | --- | --- |
| 4 | -6.95% (n=224) | -7.27% (n=768) |
| 20 | -2.56% (n=1120) | -2.75% (n=24320) |

두 규모 모두 구분되지 않았다. 그러나 ‘같은 에피소드’를 ‘비슷한 내용’으로 대신한 비교가 적절한지 의심해야 한다. 후보 8개는 QA를 어렵게 만드는 방해 세션 묶음이지, Phase 7에서 직접 고른 유사 주제 문장 묶음이 아니다.

확인된 결과는 더 좁다. **다른 인코더의 실제 대화 임베딩도 입력 변환부터 실제 회로까지 수정 없이 처리됐다.** 반면 이 라벨로 내용별 간섭을 검증하는 데는 실패했다. Phase 35에서는 실제 질문 유형 라벨도 대안이 되는지 확인한다.

### Run

```
uv run python longmemeval_capacity_probe.py --episodes 20
```

## Phase 22: tuning the fast/slow eta pair

Phase 18의 `eta` 0.5/0.03은 첫 추정값이었다. `dual_store_probe.py --sweep`로 fast_eta × slow_eta를 바꾸며 정확한 반복의 반응 감소, 11회 뒤 누적 감소, 같은/다른 주제 비율을 함께 측정했다. 어느 값을 고르느냐에 따라 ‘이중 저장소가 좋다’는 판단도 달라질 수 있기 때문이다.

같은/다른 주제 비율은 전체 격자에서 1.56–1.65로 거의 같고 감소량의 규모만 바뀌었다. 크게 달라진 것은 누적 감소 대비 재인식 신호였다. fast_eta를 키우고 slow_eta를 줄일수록 그 비율이 좋아져 격자 밖까지 더 시험했다.

| fast_eta | slow_eta | exact repeat | load @ 11 | recognition/damage ratio |
| --- | --- | --- | --- | --- |
| 0.50 | 0.03 (phase 18's guess) | -26.5% | -49.6% | 0.53 |
| 0.70 | 0.01 | -35.5% | -49.6% | 0.72 |
| 0.90 | 0.005 | -45.2% | -50.5% | 0.90 |
| 0.99 | 0.001 | -49.6% | -50.2% | **0.99** |

빠른 저장소의 `eta`가 1에 가까우면 첫 쓰기에 거의 0으로 포화된다. 이미 거의 0인 행은 나중에 더 써도 많이 줄어들지 않지만, 첫 쓰기의 흔적은 강하게 남는다. 따라서 재인식/감소 비율이 0.99까지 올라간다.

대가는 그 채널이 ‘건드린 적 있음/없음’에 가까워진다는 점이다. 한 번 봤는지 여러 번 봤는지의 세밀한 차이는 빠른 저장소에서 사라지고, 필요하다면 느린 저장소가 담당해야 한다. 당시에는 이 점을 절충으로 보았지만, Phase 36의 재인식 과제에서는 바로 이 포화성이 유리했고 느린 저장소를 없앤 쪽이 더 좋았다.

### Run

```
uv run python dual_store_probe.py --sweep
uv run python dual_store_probe.py --fast-eta 0.99 --slow-eta 0.001
```

## Phase 23: combining tagging/capture with the dual-store, and a metric trap caught mid-experiment

이번 질문은 강한 사건이 일찍 오면 약한 기억이 오래 남는 쪽으로 바뀌는가다. `tagged_dual_store_probe.py`는 Phase 20의 tag/capture와 Phase 18/22의 이중 저장소를 합친다. 빠른 저장소는 모든 사건에 반응하며 사라지는 tag를 남기고, 느린 저장소는 나중의 두드러진 사건이 남은 tag를 capture할 때만 바뀐다. capture는 내용과 무관하다.

처음에는 capture한 쪽이 더 나쁘게 보였다. 각 조건의 **자기 인코딩 직후 값**을 기준으로 이후 감소율을 계산했더니 captured -40.64%, uncaptured -23.18%였다. 그러나 절대값을 확인하니 출발선부터 달랐다. 강한 사건과 capture의 추가 쓰기 때문에 captured의 인코딩 직후 값은 101,438, uncaptured는 210,053으로 약 절반이었다. 같은 절대 감소도 작은 분모로 나누면 더 큰 비율이 된다.

비교를 절대 감소량으로 고치자 방향이 뒤집혔다. 이후 무관한 10회 쓰기로 captured는 40,859, uncaptured는 48,532를 잃었다. capture한 쪽의 침식이 약 16% 적었다. 효과는 크지 않지만 보호 방향이었다.

이 단계에서 얻은 교훈은 **쓰기 자체가 기준값을 바꾸면, 각자 기준값 대비 퍼센트만 비교해서는 안 된다**는 것이다. Phase 28의 결합 시험은 처음부터 이 수정된 절대 감소량을 쓴다.

### Run

```
uv run python tagged_dual_store_probe.py
```

## Phase 24: habituation -- write strength scaled by how fresh the KC still is

기억을 쓸 때마다 같은 비율을 줄이지 말고, **이미 많이 바뀐 KC는 덜 바꾸면 어떨까?** `memory.write_surprise_gated()`는 초기 커넥톰 가중치에 비해 얼마나 덜 억압됐는지(freshness)를 보고 쓰기 세기를 조절한다. 처음 보는 KC는 전체 `eta`를 받고, 많이 억압된 KC는 점점 작게 받는다. 두 번째 저장소나 tag/capture 장부가 없는 단일 규칙이다.

당시에는 가장 단순하고 깔끔한 개선으로 보였다. 같은 12문장 시험의 결과는 다음과 같다.

- 같은 문장 5회 노출의 매회 감소는 **-30.0% → -21.0% → -16.6% → -13.8% → -11.9%**로 줄었다. 반복할수록 추가 변화가 작아지는 habituation이며, Altmann & Gray 2002의 갱신 빈도에 따른 감쇠 적응을 참고했다.
- 새 상태의 freshness가 1.0이므로 첫 쓰기는 기존 `write()`와 같은 -30.0%다.
- 같은/다른 주제 간섭은 -7.14% / -4.47%, 비율 1.60x로 기존 1.57x와 비슷했다.
- 11회 뒤 누적 감소는 **-57.6%**로 기존 -71.2%보다 작았다. Phase 22의 포화처럼 이미 많이 줄어든 행에서 추가 손실이 작아지는 효과를 하나의 저장소로 얻었다.

단, 여기서도 개선은 초기 감소 지표 기준이다. ‘덜 바뀐다’와 ‘저장 여부를 더 잘 구별한다’는 다른 질문이며, 후자는 Phase 36에서 다시 잰다.

### Run

```
uv run python surprise_gated_probe.py
```

## Phase 25: habituation + dual-store together -- the best result in this line so far

Phase 24의 habituation과 Phase 18의 이중 저장소가 서로 보완하는지 시험했다. `habituated_dual_store_probe.py`는 빠른/느린 저장소가 각각 자기 초기 가중치를 기준으로 남은 freshness를 계산해 쓰기 세기를 줄인다. 둘 중 하나를 고르는 대신 같은 규칙을 양쪽에 독립적으로 적용했다.

아래는 같은 12문장/4주제 시험에 지금까지의 텍스트 기억 규칙을 모은 표다. **제목의 ‘best’는 이 시점의 옛 지표에 따른 판단**이며, Phase 36에서 정정된다.

| mechanism | exact repeat | load @ 11 writes | same/diff ratio |
| --- | --- | --- | --- |
| unbudgeted (phase 5/7) | -30.0% | -71.2% | 1.57 |
| dual-store, eta 0.5/0.03 (phase 18) | -26.5% | -49.6% | 1.63 |
| dual-store, tuned eta 0.99/0.001 (phase 22) | -49.6% | -50.2% | ~1.5 |
| habituation only (phase 24) | -30.0% | -57.6% | 1.60 |
| **habituation + dual-store (phase 25)** | -26.5% | **-41.5%** | 1.55 |

당시에는 재인식 -26.5%를 유지하면서 11회 뒤 누적 감소를 -41.5%로 줄였으므로 최선으로 골랐다. Phase 17의 `competitive`는 감소가 -0.7%로 더 작지만 재인식도 -0.25%로 거의 없어졌기에 제외했다. 같은/다른 주제 비율도 1.55로 기존 범위를 유지했다. 서로 다른 시간상수와 KC별 반복 적응이 함께 효과를 낸다고 해석한 것이다.

그러나 이 표는 저장하지 않은 항목을 한 번도 읽지 않는다. 따라서 작은 누적 감소가 실제 구별 능력을 보존했다는 증거는 아니다. Phase 36에서는 첫 쓰기와 이후 간섭을 분리하고, 저장/미저장 문서의 AUC를 재자 **이 조합이 16개 초과 저장에서 가장 낮아졌다.** 원래 결과와 선택 이유를 남겨 두되, 최종 추천으로 인용하지 않는다.

소리 연구의 Phase 32에서 크기 가중 쓰기 `memory.write_magnitude_weighted()`가 필요해진 뒤, 같은 텍스트 시험에도 한 행을 추가했다. 재인식 -15.2% / 누적 감소 -49.6% / 비율 1.55였다. Phase 25 조합보다 재인식이 약하고 누적 감소도 낫지 않았다.

이 차이는 회로 구조를 다시 보게 했다. Phase 31/32의 작은 소리 회로에서는 모든 입력이 약 164개 같은 하류 뉴런에 모여 상대적인 **활성 세기**만 내용을 구분한다. 큰 희소 KC 집단의 텍스트는 **어느 KC가 켜졌는지**부터 다르므로, 세기까지 가중하면 주로 쓰기 강도만 낮아졌다. 같은 규칙의 효과를 다른 회로에 그대로 일반화할 수 없다.

### Run

```
uv run python habituated_dual_store_probe.py
```

## Phase 27: vision -- interference tracks measured similarity, once labels stop lying about it

Phase 16은 사람이 붙인 커피/개/경보 라벨이 회로의 시각 유사도와 다르다는 문제를 드러냈다. 이번에는 라벨을 버리고 실제 코드가 가장 비슷한 쌍과 가장 다른 쌍을 비교한다. `vision_measured_similarity_probe.py`는 같은 실제 사진 6개의 모든 15쌍을 KC 활성 집합 겹침으로 순위 매겼다.

가장 비슷한 쌍은 `cup`/`smoke_detector`로 겹침 0.708, 간섭 -27.01%였다. 가장 다른 쌍은 `golden`/`smoke_detector`로 겹침 0.330, 간섭 -20.90%였다. **측정된 코드가 더 비슷하면 더 간섭한다**는 방향은 맞았다.

따라서 Phase 15/16에서 언급한 ‘구별 없음’은 정확히 말해 사람의 주제 라벨로 묶었을 때의 결과다. 간섭 메커니즘 자체가 유사도를 반영하지 못한 것은 아니었다. 다만 두 극단 쌍의 확인이며, 사진의 의미 범주나 물체 인식 능력을 입증한 것은 아니다.

### Run

```
uv run python vision_measured_similarity_probe.py
```

## Phase 28: tagging/capture combined with the habituated dual-store

`tagged_habituated_probe.py`는 Phase 20의 tag/capture를 Phase 25의 habituated dual-store에 합친다. capture가 느린 저장소에 추가 억압을 줄 때도 그 저장소의 남은 freshness를 반영한다. Phase 23에서 분모 때문에 결론이 뒤집힌 경험을 따라, 처음부터 각자 기준값 대비 퍼센트가 아닌 **절대 침식량**으로 비교한다.

무관한 10회 쓰기 뒤 captured의 감소는 24,479, uncaptured는 27,794였다. capture한 쪽이 덜 잃는 보호 방향은 유지됐다. 다만 보호 크기는 약 11.9%로, habituation이 없던 Phase 23의 15.8%보다 작았다. habituation이 이미 전체 침식을 줄였으므로 capture가 추가로 줄일 여지도 작아진 것이다.

이 지표에서는 두 규칙이 서로 취소하지 않고 함께 작동하지만, 효과를 단순히 더할 수는 없었다. 이 역시 절대 감소량의 비교이며 Phase 36의 재인식 AUC와 같은 측정으로 취급하지 않는다.

### Run

```
uv run python tagged_habituated_probe.py
```

## Phase 29: the sound line's input side -- no random projection anywhere

Phase 9에서 받은 AMMC(R)/JO-A/B 회로에 실제 감각 조율 근거로 입력을 넣는다. `audio_to_jo.py`는 합성 음을 만들고 FFT로 200–350 Hz 대역 에너지를 계산한다. Kamikouchi et al. 2009가 기술한 JO-A/B의 구애 노래 범위 조율을 이용해 실제 JO-A/B 13개에 직접 주입한다. 텍스트의 무작위 투영과 달리 생리학적 주파수 근거가 있는 경로다. 중력·바람에 조율된 JO-C/E에는 순음을 임의로 대응시키지 않고 0을 넣는다.

250 Hz는 대역 안이므로 하류 AMMC 총 반응 899.0, 2000 Hz는 밖이라 0.0이었다. 백색잡음은 에너지가 넓게 퍼져 있어 대역 안 부분에 비례한 작은 반응 28.3을 냈다. 기대한 정성적 순서는 맞았다.

하지만 이 단계는 대역에 반응한다는 확인이다. 서로 다른 소리를 구별해 기억하는지는 아직 모른다. 한 숫자인 대역 에너지를 모든 입력 뉴런에 똑같이 주는 설계의 한계가 다음 단계에서 드러난다.

### Run

```
uv run python audio_to_jo.py
```

## Phase 30: sound memory -- real recognition, but a hard limit on identity

`audio_memory_probe.py`는 Phase 29의 입력을 한 번 전파하고 상위 10%만 남겨 KC에 대응하는 희소 코드를 만든다. 실제 AMMC의 `other → other` 순환 연결에 쓰고 읽어, 텍스트·시각처럼 반복 흔적이 생기는지 봤다.

250 Hz를 반복하자 -30.0%로 깨끗한 재인식 신호처럼 보였다. 그런데 전혀 다른 백색잡음도 250 Hz를 쓴 뒤 41,154 → 28,808, 정확히 **-30.0%** 줄었다. 원인은 입력 쪽이었다. `build_stimulus`가 모든 소리에 대해 같은 JO-A/B 13개에 단일 `band_energy`만 곱하므로, 가능한 입력은 같은 방향 벡터의 크기만 바뀐 것이었다.

`propagate`는 선형이고 `sparse_code`의 top-k 선택은 전체 크기를 바꿔도 같으므로, **모든 소리가 정확히 같은 하류 KC 집합을 켠다.** 이 설계로는 크기에 따른 반응 변화만 있고 내용·정체성 구별은 원천적으로 불가능하다. 시각 Phase 15/16처럼 약한 구별과도 다른 문제다.

따라서 다음 수정은 여러 주파수 대역의 filterbank를 만들고 서로 다른 JO-A/B 부분집단 또는 더 큰 집단에 넣는 것이다. ‘반복하면 반응이 줄었다’만으로 입력별 기억을 확인했다고 말할 수 없다는 또 한 사례다.

### Run

```
uv run python audio_memory_probe.py
```

## Phase 31: fixing the input didn't fix it -- write() itself only sees a binary mask

Phase 30의 제안대로 `audio_to_jo.py`에 `build_stimulus_multichannel`을 만들었다. 로그 간격 filterbank의 서로 다른 주파수 대역 에너지를 실제 JO-A/B 13개에 나눠 넣었다. 연속값에서는 수정 효과가 있었다. 250 Hz와 2000 Hz의 전파 후 구동값 코사인 유사도는 0.0127까지 낮아져, 더는 같은 방향 벡터가 아니었다.

그런데 `audio_memory_probe.py`에서는 한 소리를 쓴 뒤 세 소리가 여전히 정확히 -30.0%씩 줄었다. 입력을 고쳤는데도 쓰기 단계가 그 차이를 버리고 있었다. 이 13개 입력에서 도달 가능한 하류 뉴런은 2,631개 중 약 164개뿐이다. 수렴하는 실제 배선 때문에 연속값은 달라도 켜진 곳을 뜻하는 이진 마스크 `code > 0`는 모든 소리에서 같았다.

`memory.write()`는 `weights[active, :] *= 1 - eta`로 **활성 여부만 보고 세기를 보지 않는다.** 같은 행에 같은 비율을 적용하므로 어느 소리든 결과가 같아진다. 입력별로 활성 집합 자체가 달랐던 큰 텍스트/KC·시각/lamina 집단에서는 숨겨졌던 결함이다.

다음 수정은 연결을 바꾸는 것이 아니라 쓰기 규칙이 각 행의 상대 세기를 보게 하는 것이다. 회로가 내용을 세기로 표현하는데 저장기가 이를 이진화하면, 앞단을 아무리 고쳐도 그 정보가 기억에 남지 않는다.

### Run

```
uv run python audio_memory_probe.py  # now uses build_stimulus_multichannel; see the printed cosine table
```

## Phase 32: magnitude-weighted write -- real content discrimination, finally

`memory.write_magnitude_weighted()`는 활성 행마다 가장 강한 행 대비 자기 활성 세기에 비례해 억압량을 준다. Phase 17의 `write_competitive`가 쓰는 정규화된 경쟁 지분과 비슷하지만, 이번 목적은 전체 예산보다 **같은 활성 집합 안의 내용 차이를 저장하는 것**이다.

같은 세 소리로 `audio_memory_probe.py`를 다시 실행했다. 250 Hz를 저장한 뒤 정확한 반복은 -17.4%, 2000 Hz는 -0.3%, 백색잡음은 -3.5%였다. 2000 Hz의 코사인 유사도는 0.0127로 거의 겹치지 않았고, 백색잡음은 0.3435로 중간이었다. 이제 간섭의 순서도 실제 유사도의 순서와 맞는다.

반복 신호가 옛 -30.0%보다 작은 것은 약하게 활성화된 행에 덜 쓰기 때문이다. 재인식은 유지하면서 무관한 소리의 일괄 감소를 피했다. Phase 29–31의 연속 수정은 이 지점, 즉 쓰기 장치가 단순 점유 여부를 넘어 내용 차이를 보게 하는 데 도달했다.

### Run

```
uv run python audio_memory_probe.py
```

## Phase 33: one more verified odorant, and why the list stays short on purpose

냄새 대응표를 넓히되, 기억에 의존해 인용을 추측하지 않고 당시 웹 검색으로 후보 근거를 확인했다. 추가한 것은 ethyl butyrate → DM2(Hallem & Carlson 2006, Or22a)다. ethanol과 같은 사구체를 쓰며, 실제 `DM2_lPN` 뉴런에 대응하는 두 번째 키워드가 된다.

반면 바나나 냄새의 isoamyl acetate는 제외했다. 문헌에서는 VC3, DM3, VM5v, DA4m, DC1, VA4의 **여섯 사구체**를 활성화한다고 한다. ‘특정 물질과 잘 확인된 단일 대응’이라는 이 도구의 설계에 맞지 않는다. 하나로 억지로 줄이면 근거 없는 단순화가 된다.

따라서 목록이 짧은 것은 단순히 구현을 덜 해서가 아니다. 근거 수준을 지키려는 범위 제한이며, 최종적으로 다룬 7개를 임의 냄새나 일반 개념까지 확장하지 않는다.

### Run

```
uv run python odor_embedder.py --text "The cocktail smelled faintly of ethyl butyrate."
```

## Phase 34: opponent-channel valence -- the mechanism works, the labels don't exist yet

지금까지는 MBON 반응을 합했지만, 보상과 벌은 반대 방향의 출력으로 읽어야 한다. `valence_probe.py`는 `RESEARCH.md`에서 정리한 구조대로 MBON을 두 대립 채널로 나누고 합이 아닌 **차이**를 읽는다. 강화는 같은 부호의 채널을 키우는 대신 반대 부호의 채널을 억압한다(Owald et al. 2015; Aso et al. 2014).

실행 전에 확인한 중요한 한계가 있다. 받은 `MBON14`, `MBON06` 등의 이름이 Aso et al. 2014의 실제 구획별 보상/회피 대응 중 무엇인지 아직 대조하지 않았다. 그래서 실제 MBON 75개를 **임의의 50/50 비율**로 나눴다. 이 시험은 부호가 주어졌을 때 규칙이 올바르게 작동하는지를 묻지, 특정 실제 뉴런의 valence를 밝혀내는 것은 아니다.

기본 점수는 +7,649였다. 보상 강화 뒤 +30,128(+22,479), 벌 강화 뒤 -17,124(-24,773)로 움직였다. 실제 KC→MBON 가중치를 쓰면서 기대한 양·음 방향이 나왔다. 기능 규칙의 확인은 됐지만 실제 부호 배정은 남았고, 해부학에서 구획 부호를 읽는 후속 검사는 Phase 38에 있다.

### Run

```
uv run python valence_probe.py
```

## Phase 35: real question-type labels for the LongMemEval same/different test

Phase 21의 에피소드당 후보 8개 묶음은 내용 유사도 라벨이 아니었다. 그래서 실제 외부 라벨인 질문 유형은 쓸 수 있는지 다시 확인했다. `neural-memory`의 `longmemeval.py`는 이미 `single-session-user`, `multi-session`, `knowledge-update`, `temporal-reasoning` 등의 `question_type`을 Phase 21이 읽은 `longmemeval_deferred.pt`에 넣고 있었다. `question_type` 정수 배열과 `question_type_names`가 있었지만 이전에는 사용하지 않았다.

`longmemeval_question_type_probe.py`로 knowledge-update/multi-session/temporal-reasoning의 실제 60개 에피소드를 시험했다. 같은 유형 간섭 -1.39%(n=79,776), 다른 유형 -1.38%(n=150,144)로 다시 구분되지 않았다.

이것도 메커니즘의 반증으로 바로 읽기 어렵다. `question_type`은 질문을 어떻게 구성했는지의 **과제 구조** 라벨이다. 두 multi-session 질문이 전혀 다른 주제를 다룰 수 있다. Phase 16/27의 시각 주제 문제와 마찬가지로, 라벨이 실제로 코드 유사도를 나타내는지 먼저 확인해야 한다.

이 시점까지 가정한 범주·에피소드 번호·질문 유형 중 어느 것도 유사도의 직접 측정을 대신하지 못했다. 양의 관계가 확인된 것은 Phase 6·27처럼 겹침을 직접 잰 비교였다. 이후 Phase 36은 이 라벨 비교와 다른 질문인 ‘저장했는가’를 정답으로 삼아 용량을 평가한다.

### Run

```
uv run python longmemeval_question_type_probe.py --episodes 60
```

<span id="kb-fly-revision"></span>

## Phase 36: the mechanism comparison was ranking the wrong number, and it inverts

Phase 25에서는 ‘같은 입력을 다시 봤을 때 반응이 얼마나 줄었나’와 ‘11번 더 쓴 뒤 반응이 얼마나 줄었나’를 나란히 놓고 habituated dual-store를 가장 좋은 방식으로 골랐다. 그런데 두 값 모두 **아무것도 쓰기 전의 가중치**를 기준으로 계산했다. 따라서 뒤의 값에는 나중 입력의 방해뿐 아니라, 그 항목을 처음 기억할 때 일부러 만든 감소도 들어 있었다.

이 구분이 중요한 이유는 이 회로가 반응을 줄여서 기억하기 때문이다. 반응이 덜 줄었다고 무조건 기억을 잘 보존한 것은 아니다. 애초에 약하게 기록했어도 같은 숫자가 나온다. 기존 표에서 첫 쓰기의 효과를 분리하면 다음과 같다.

| mechanism | exact repeat | load @ 11 | interference alone |
| --- | ---: | ---: | ---: |
| unbudgeted | -30.0% | -71.2% | -41.2% |
| dual-store 0.5/0.03 | -26.5% | -49.6% | -23.1% |
| habituation only | -30.0% | -57.6% | -27.6% |
| habituation + dual (phase 25's pick) | -26.5% | -41.5% | -15.0% |
| **dual-store 0.99/0.001 (phase 22, called worse)** | -49.6% | -50.2% | **-0.6%** |

Phase 25에서 채택한 행은 다른 입력 때문에 -15.0% 더 줄었다. 반면 Phase 22에서 뒤로 밀어 둔 강한 쓰기 방식은 -0.6%뿐이다. 후자가 다른 입력에 의한 침식을 25배 덜 겪었는데도, 처음에 강하게 썼다는 이유로 기존 지표에서는 불리했다.

더 근본적인 문제도 있다. 두 열 모두 이미 저장한 항목만 읽었다. **저장하지 않은 항목과 구별되는지 한 번도 묻지 않았으므로**, ‘기억이 살아 있다’와 ‘모든 반응이 비슷하게 덜 줄었다’를 구분할 수 없었다.

`recognition_under_load_probe.py`는 질문을 바꾼다. 문서 집합에서 무작위 절반만 저장한 뒤, 저장한 문서와 저장하지 않은 문서를 모두 읽는다. 두 집단이 얼마나 잘 구분되는지 AUC로 평가한다. 1.0이면 완전 구분, 0.5면 구분하지 못하는 수준이다. 실제 LongMemEval 문서 임베딩 512개를 사용하고 저장량별로 20회 반복했다.

| written | unbudgeted | **saturating** | dual | dual_tuned | habituation | habituated_dual | stored_codes |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 8 | 0.9023 | **1.0000** | 0.9383 | 1.0000 | 0.9273 | 0.9555 | 1.0000 |
| 16 | 0.8023 | **1.0000** | 0.8275 | 1.0000 | 0.8100 | 0.8221 | 1.0000 |
| 32 | 0.7372 | **0.9836** | 0.7131 | 0.9683 | 0.7142 | 0.7015 | 0.9999 |
| 64 | 0.6591 | **0.8684** | 0.5998 | 0.7956 | 0.6218 | 0.5980 | 1.0000 |
| 128 | 0.6055 | **0.7409** | 0.5424 | 0.6140 | 0.5636 | 0.5414 | 0.9993 |
| 256 | 0.5831 | **0.6349** | 0.5284 | 0.5319 | 0.5433 | 0.5252 | 0.9986 |

**평가 질문을 바꾸자 순위가 뒤집혔다.** Phase 25의 habituated dual-store는 16개를 넘는 모든 저장량에서 가장 낮았고, 256개에서는 0.5252로 우연 수준에 가까웠다. 가장 좋은 규칙은 더 단순했다. 하나의 저장소에서 `eta`를 1에 가깝게 두어, 활성화된 KC 행을 첫 쓰기 때 거의 0으로 만드는 `saturating`이다. ‘이 KC를 쓴 적이 있다’는 표식을 강하게 남기는 셈이다.

`saturating`은 기존 Phase 25 표에 없었다. Phase 22의 tuned dual-store에서 느린 저장소를 없앤 것이며, 없애자 모든 저장량에서 좋아졌다. 따라서 이 재인식 과제에서는 이중 저장소가 추가 이득을 주지 않았다. Phase 25의 계산 자체가 틀린 것이 아니라, 약하게 쓰는 방식을 보상하는 지표로 기억 성능을 대신 판단한 것이 잘못이었다.

이제 이 회로의 용량을 처음으로 구체적으로 말할 수 있다. KC 2,053개와 MBON 75개를 쓴 조건에서 최선의 방식은 문서 32개에 AUC 약 0.98, 64개에 0.87, 128개에 0.74, 256개에 0.63이었다. 이것은 **본 문서인지 알아보는 용량**이며 문서 내용을 복원하거나 질문에 답하는 능력은 아니다.

`stored_codes`는 손실 위치를 확인하기 위한 상한 비교다. 저장 문서마다 KC 코드를 따로 보관하고 가장 겹치는 코드를 찾으면 전 구간에서 거의 1.0을 유지한다. 따라서 이 표의 성능 저하는 코드를 애초에 구별할 수 없어서가 아니라, 그것들을 고정 크기 시냅스 상태에 합쳐 넣는 과정에서 생긴다. 다만 `stored_codes`는 문서 수만큼 메모리가 늘어나므로, 고정 용량 회로와 같은 자원을 쓰는 경쟁 조건은 아니다.

### Run

```
uv run python recognition_under_load_probe.py --trials 20 --loads 8,16,32,64,128,256
```

<span id="kb-fly-capacity"></span>

## Phase 37: the capacity follows from two integers, and correlation is what bends it

Phase 36에서 이긴 방식은 활성 KC에 거의 이진 표식을 남긴다. 그렇다면 용량 저하도 복잡한 생물학적 설명에 앞서 **표식이 얼마나 많이 찼는가**로 예측할 수 있지 않을까? 한 번도 저장하지 않은 문서가 쓰는 KC가 모두 이미 표시돼 있으면, 회로는 그 문서도 본 적 있다고 오인한다. 이는 Bloom filter의 거짓 양성과 같은 구조다.

    p   = 1 - (1 - k/m)^N        each cell marked by at least one of N writes
    AUC = 1 - 0.5 * p^k          a false positive is a tie, worth 0.5

`m`은 전체 KC 수 2,053, `k`는 문서 하나가 활성화하는 KC 수, `N`은 저장한 문서 수다. 첫 줄은 KC 하나가 한 번 이상 표시될 확률을, 두 번째 줄은 미저장 문서의 KC가 전부 표시돼 동점으로 읽힐 때의 AUC를 계산한다. 관측 곡선에 맞춰 조정한 매개변수는 없다. 다만 코드가 서로 독립적인 무작위 부분집합이라는 가정이 들어 있다.

`bloom_capacity_probe.py`는 그 가정을 분리하려고 세 가지를 비교한다. 실제 KC 코드를 반복 쓸 때마다 더 줄이는 방식(real, counting), 같은 코드를 한 번만 표시하는 방식(real, binary), 활성 KC 수는 같지만 위치를 독립적으로 섞은 방식(shuffled, binary)이다. 마지막 대조가 수식과 맞고 실제 코드만 다르면, 차이는 코드 간 겹침에서 온다고 볼 수 있다.

| keep | k | written | predicted | real, counting | real, binary | shuffled, binary |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.02 | 41 | 128 | 0.9801 | 0.7109 | 0.7438 | **0.9821** |
| 0.02 | 41 | 512 | 0.5007 | 0.5739 | 0.5958 | **0.4986** |
| 0.05 | 103 | 128 | 0.5661 | 0.7503 | 0.7794 | **0.5687** |
| 0.10 | 205 | 128 | 0.5001 | 0.7568 | 0.7687 | **0.5120** |
| 0.10 | 205 | 32 | 0.9996 | 0.9576 | 0.9705 | **0.9985** |
| 0.20 | 411 | 32 | 0.6381 | 0.9634 | 0.9672 | **0.6351** |
| 0.40 | 821 | 32 | 0.5000 | 0.8764 | 0.8875 | **0.5069** |

**독립 코드에서는 수식과 측정이 거의 일치했다.** `k`가 20배, `N`이 64배 달라지는 범위에서도 예측/측정은 0.9801/0.9821, 0.5661/0.5687, 0.6381/0.6351, 0.5007/0.4986처럼 가까웠다. 이 조건의 기억은 KC의 정체성을 표식으로 쓰는 Bloom filter로 설명된다.

한 번만 표시하는 방식과 반복해서 더 줄이는 방식의 차이는 최대 약 0.03이고 대부분 더 작았다. `eta`가 1에 가까우면 첫 쓰기에 거의 포화되므로, 반복 횟수를 더 세는 것이 큰 정보를 보태지 않는다는 설명과 맞는다.

**실제 코드의 상관은 두 방향으로 작용한다.** 같은 문서 집합과 같은 투영에서 나온 코드들은 독립 부분집합보다 특정 KC를 더 자주 함께 쓴다.

- 여유가 있는 조건에서는 손해다. `k`=41, 128회 저장 때 실제 이진 코드의 AUC는 0.7438로 예측 0.9801보다 낮다. 아직 안 본 문서도 자주 쓰이는 KC를 공유해 이미 저장한 것처럼 보이기 쉽다.
- 균일한 표식이 포화되는 조건에서는 반대로 이득이 남는다. `k`=205, 128회 저장 때 예측과 섞은 대조는 0.5001/0.5120으로 내려가지만 실제 코드는 0.7687이다. 쓰기가 인기 있는 KC에 몰리므로 다른 KC는 더 오래 미표시 상태로 남는다.

따라서 상관은 단순히 용량을 낮추기만 하지 않는다. 여유 구간의 최고 성능을 깎는 대신, 많은 항목을 넣었을 때 한꺼번에 구분 능력을 잃는 현상을 늦춘다. 이것이 이 실험에서 관찰한 두 효과이며, 모든 기억 과제에서 더 유리하다는 뜻은 아니다.

그렇다면 한 문서에 KC를 얼마나 적게 켜는 것이 좋을까? 실제 코드의 이진 저장소에서 `keep_ratio`를 바꾸었다.

| written | 0.02 | 0.05 | 0.10 | 0.20 | 0.40 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 128 | 0.7438 | **0.7794** | 0.7687 | 0.7014 | 0.6019 |
| 512 | **0.5958** | 0.5852 | 0.5699 | 0.5469 | 0.5186 |

측정한 최적 범위는 0.02–0.05였다. `RESEARCH.md`가 정리한 실제 APL 억제의 활성 비율은 **5–10%**이므로 생물학적 범위의 낮은 쪽과 일부 겹친다. 그러나 입력은 실제 냄새 반응이 아니라 텍스트 임베딩의 무작위 투영이다. 최적점을 만든 상관 구조도 이 문서 집합의 것이므로, 초파리 회로가 같은 이유로 그 비율을 택했다고 결론 내리지 않는다. 이 연구가 계속 사용한 `keep_ratio` 0.10도 측정한 각 저장량에서 최고점은 아니었다.

### Run

```
uv run python bloom_capacity_probe.py --trials 20 --keep-ratios 0.02,0.05,0.10,0.20,0.40 --loads 8,32,128,512
```

## Not built yet

이 절은 Phase 37 무렵에 남겨 둔 미구현 목록이다. 뒤의 Phase 38–39가 일부 질문을 더 조사했으므로 시간순으로 읽는다.

- 텍스트·기억: Phase 34의 MBON 부호는 임의 분할이었다. 실제 이름과 Aso et al. 2014의 구획별 valence를 대조하는 작업은 당시 하지 않았다. 뒤의 Phase 38은 PAM/PPL 시냅스 수로 구획 부호를 추정했지만, 임의 분할 시험을 소급해 실제 생물학적 검증으로 바꾸지는 않는다. LongMemEval의 진짜 내용 주제 라벨도 남은 문제다. Phase 35의 `question_type`은 대안이 아니었고, 임베딩 유사도로 군집을 만들면 이 시스템을 같은 표현으로 검증하는 순환 문제가 생길 수 있다.
- 시각: 실제 내려받은 사진을 유지할지 텍스트→이미지를 더할지는 미정이다. 생성 단계는 Phase 11의 ‘빌린 의미’ 문제를 옮길 뿐 해결하지 않는다. lamina 다음 medulla까지 전파해 R7/R8의 실제 경로를 쓰는 작업도 남았다.
- 냄새: Phase 33처럼 근거를 확인한 7개만 지원한다. 많은 실제 물질은 여러 사구체에 넓게 반응하므로 단일 대응으로 늘릴 수 없다.
- 소리: Phase 32에서 내용 차이에 따른 간섭은 확인했다. 그러나 조율된 뉴런 13개만으로 단순 음/잡음을 넘어설 수 있는지, AMMC(L)까지 받아야 하는지는 미정이다. 합성 신호 이외의 실제 구애 노래나 환경 녹음도 아직 시험하지 않았다.

## Phase 38: the wiring is not for capacity, and the valence task I built could not test it either

앞 단계는 기억 규칙과 용량을 설명했지만, **실제 연결 상대가 중요했는가**는 남아 있었다. FlyGM(arXiv 2602.17997)은 전체 초파리 커넥톰을 그래프 제어기로 써 보행 과제에서 세 baseline을 이겼다. 특히 각 뉴런의 들어오는 연결 수와 나가는 연결 수를 그대로 두고 상대만 바꾸는 재배선 대조를 썼다. 이 대조를 이겨야 단순히 연결이 많아서가 아니라 ‘누가 누구와 연결됐는가’의 이득이라고 말할 수 있다.

당시 논문 본문 검색에서는 "mushroom body"가 나오지 않았고 기억 과제도 시험하지 않았다. 따라서 보행의 성과를 기억에도 옮겨 말하지 않고, 여기서 별도로 시험했다.

### Linear associative capacity: the connectome carries no prior

`wiring_prior_probe.py`는 실제 KC→MBON 연결이 있는 위치에 연상을 저장한다. 같은 연결 수와 가중치를 쓰되 연결 상대를 바꾸는 curveball 재배선, 전체 시냅스를 균일하게 섞는 대조와 비교한다. 표의 `resolved`는 이 실험에서 차이를 구분해 냈다는 판정이며, 값의 크기와 방향도 함께 봐야 한다.

| items | real | rewired | random | real over rewired | real over random |
|---:|---:|---:|---:|---|---|
| 500 | 0.9776 | 0.9750 | 0.9976 | +0.0026 NOT resolved | **-0.0200 resolved** |
| 1000 | 0.7874 | 0.7898 | 0.8760 | -0.0023 NOT resolved | **-0.0886 resolved** |
| 2000 | 0.4050 | 0.4053 | 0.4822 | -0.0003 NOT resolved | **-0.0772 resolved** |

사전에 정한 ‘실제 배선이 차수 보존 재배선을 이겨야 한다’는 기준을 통과하지 못했다. 이 선형 연상 저장 과제에서는 실제 연결 상대가 각 뉴런의 연결 수 이상으로 보탠 이득을 찾지 못했다. 동일한 30,543개 시냅스를 균일하게 섞은 조건은 오히려 모든 저장량에서 더 높았다.

이 결과를 ‘실제 배선은 쓸모없다’로 넓히지는 않는다. 이 단계의 해석은 무작위 확장이 저장 용량에 유리할 수 있고, 생물 회로는 동물에게 중요한 입력을 선택하는 데 다른 제약과 비용을 감수할 수 있다는 것이다. **여기서 재지 않은 선택·행동 기능을 단순 저장 용량으로 대신 평가할 수는 없다.**

### What it is for, read straight off the anatomy

`compartment_valence.py`는 구획별로 들어오는 PAM과 PPL1 시냅스 수를 세고, 그 비율에서 보상/벌 방향의 부호를 계산했다. 행동 데이터에 맞춰 학습하거나 수치를 조정하지 않았다.

| reward | | punishment | |
|---|---:|---|---:|
| b'2 | +1.000 (PAM 12659 : PPL 1) | a3 | -1.000 (PAM 0 : PPL 2424) |
| g5 | +0.996 | CA | -1.000 |
| b2 | +0.996 | a2 | -0.999 |
| b1 | +0.988 | a'3 | -0.993 |
| g4 | +0.987 | a'2 | -0.969 |
| g3 | +0.907 | g1 | -0.856 |
| b'1 | +0.750 | a'1 | -0.800 |
| a1 | +0.727 | g2 | -0.448 |

원시 시냅스 수만으로 수평 엽은 보상, 수직 엽은 벌이라는 교과서적 구분과 맞는 패턴이 나왔다. 이는 Phase 34의 임의 50/50 분할보다 해부학에 근거한 결과다. 다만 이 부호를 다음 과제에 주입하는 방식이 배선의 효과를 가리지 않는지 따로 살펴야 한다.

### The valence task, and why it does not answer the question

`valence_store_probe.py`는 패턴마다 1비트의 보상/벌 값을 저장한다. 초파리식 억압 쓰기를 적용하고, MBON 출력을 구획의 부호로 가중해 합친 값으로 읽는다.

| items | real | rewired | random | real over rewired |
|---:|---:|---:|---:|---|
| 400 | 0.9427 | 0.9397 | 0.9403 | +0.0030 resolved |
| 2000 | 0.7216 | 0.7192 | 0.7224 | +0.0023 NOT resolved |
| 8000 | 0.6331 | 0.6318 | 0.6334 | +0.0013 resolved |

실제 배선은 재배선보다 일관되게 높았고 두 저장량에서는 차이가 구분됐다. 그러나 크기는 약 0.1–0.3%p에 불과했고, 균일하게 섞은 대조와는 어떤 저장량에서도 차이를 구분하지 못했다.

원인을 확인하자 과제 설계가 검증하려던 답을 미리 넣고 있었다. 보상/벌 부호를 MBON 열에 붙인 채 KC의 연결 상대만 섞었으므로, 어떤 재배선에서도 그 열의 부호는 그대로 남는다. 세 조건이 소수 셋째 자리까지 비슷한 이유다. **배선이 구획 기능을 만들어 내는지 물어야 했는데, 평가식이 구획 기능을 이미 제공했다.** 따라서 작은 승리를 실제 배선의 기능적 우위로 해석하지 않는다.

### Two defects, both caught by their own numbers

첫 용량 시험에서는 모든 배선이 정확히 우연 수준이었다. 설명문에는 delta rule로 저장한다고 적었지만 코드에는 그 쓰기가 없었다. 고정 행렬에 코드를 통과시키기만 하고 아무 연상도 저장하지 않은 것이다. 점수 옆에 우연 수준을 함께 출력했기 때문에 결함을 알아챘다.

첫 재배선도 잘못됐다. 열 인덱스를 전체적으로 섞고 충돌을 더하는 과정에서 30,543개 중 5,255개 시냅스를 잃었고 행별 연결 수도 달라졌다. 그때의 ‘실제 배선 우위’는 더 성긴 행렬을 이겼다는 뜻이었다. 양쪽 차수와 가중치 값의 집합을 정확히 보존하는 curveball 방식으로 고치자, 1000개 저장 때의 +0.0495가 -0.0023으로 바뀌었다. 대조군이 제대로 보존됐는지 확인하지 않으면 원인 해석도 뒤집힌다.

### What to measure next

새 과제를 만들기 전에 배선 자체에 활용할 구조가 있는지부터 확인하기로 했다. 같은 연결 수를 가진 재배선보다 실제 KC가 더 적은 구획의 MBON에 선택적으로 연결되는가? 이 질문을 Phase 39에서 직접 측정한다. 구조가 존재하는지와 그 구조가 기억을 돕는지는 별도 단계로 검증해야 한다.

<span id="kb-fly-latest"></span>

## Phase 39: there is block structure, and it does not protect a lesson

Phase 38의 과제는 실제 배선의 이점을 보여 주지 못했다. 다음 질문은 ‘유용할 법한 구조가 아예 없는가, 아니면 과제가 그 구조를 쓰지 못했는가?’다. `compartment_structure_probe.py`는 학습을 돌리기 전에 연결 자체를 측정한다. KC 하나가 가장 많이 연결된 구획에 얼마나 집중하는지(top-compartment share), 총 몇 구획에 닿는지(compartments reached)를 비교했다.

| wiring | top-compartment share | compartments reached |
|---|---:|---:|
| real | 0.2642 | **7.31** |
| rewired | 0.2898 | 9.90 |
| random | 0.2999 | 9.37 |
| even spread | 0.0625 | 16 |

`reach: real over rewired`는 **-2.59 [-2.59, -2.58] resolved**다. 각 뉴런의 연결 수를 같게 둬도 실제 KC는 평균 약 2.6개 적은 구획에 닿는다. 구조적 선택성은 실제로 있었다.

하지만 ‘한 구획에 몰아준다’는 구조는 아니다. 가장 큰 구획의 비중은 오히려 실제 배선에서 낮다. 적은 수의 구획을 고른 뒤 그 안에 연결을 나누는 형태이며, 한 엽을 지나는 축삭이 경로상의 구획에 시냅스를 만드는 모습과 부합한다. 이는 구조의 관찰이지, 아직 기억 보호의 증거는 아니다.

### The prediction that followed, and failed

여기서 ‘한 기억이 적은 구획에만 놓이면 다른 기억과 덜 충돌할 것’이라는 예측을 세웠다. `interference_probe.py`는 기억 A를 저장한 뒤 B를 덧쓰고 A가 얼마나 남는지 잰다. 배선마다 원래 A를 저장하는 능력이 다를 수 있으므로, 각 배선의 A 단독 점수에 대한 비율로 비교했다. 처음부터 약하게 저장해 잃을 것이 적은 조건이 유리해지는 문제를 피하려는 설계다.

| wiring | A alone | A after B | kept |
|---|---:|---:|---:|
| real | 0.9985 | 0.9521 | 0.9535 |
| rewired | 0.9977 | 0.9556 | 0.9578 |
| random | 1.0000 | 0.9871 | **0.9871** |

`kept: real over rewired`는 -0.0044 [-0.0116, +0.0033]으로 **차이를 구분하지 못했다(not resolved)**. `kept: real over random`은 -0.0336 [-0.0382, -0.0293]이며 실제 배선이 불리한 방향으로 구분됐다. 사전에 정한 기준에서 ‘적은 구획에 닿으니 기억을 더 보호한다’는 예측은 지지되지 않았다.

해석도 바뀌었다. 이 쓰기 규칙에서 두 기억의 충돌은 같은 KC가 둘 다에 활성화될 때 생긴다. 그것을 결정하는 것은 입력의 희소 코드다. KC→MBON 배선은 이미 생긴 충돌이 어느 MBON으로 전달될지를 정할 뿐이다. **구획 선택성은 존재했지만, 이 과제의 충돌 원인을 제거하지는 못했다.**

### Three angles, one answer

| task | real vs rewired | real vs random |
|---|---|---|
| linear capacity | no difference | **random wins** |
| signed valence | real wins (design fault: signs indexed by MBON column) | no difference |
| interference | no difference | **random wins** |

선형 연상 저장이라는 범위에서는 세 방향으로 물어도 실제 배선의 확실한 이득을 얻지 못했다. 부호 기억의 작은 우위에는 Phase 38의 평가 설계 결함이 있고, 용량과 간섭에서는 무작위 대조가 더 좋았다.

이 결과는 커넥톰 전체가 무용하다는 결론이 아니다. FlyGM은 같은 종류의 대조를 사용한 폐루프 감각·운동 제어에서 이득을 보고했다. 여기서 측정한 것은 저장뿐이며, 자연 냄새의 통계, 대사 비용, 발달 제약, 행동 선택은 다루지 않았다. 따라서 다음 방향을 잡을 때는 저장 과제의 점수를 올리는 것과 실제 회로가 수행하는 기능을 시험하는 것을 구분해야 한다.

독립적으로 남는 결과는 `compartment_valence.py`다. 별도 학습 없이 원시 해부학에서 계산한 부호가 수평 엽의 보상/수직 엽의 벌 구분을 되찾았다. 다만 그 사실만으로 지금의 기억 장치가 행동이나 생물학적 학습을 재현했다고 주장하지 않는다.
