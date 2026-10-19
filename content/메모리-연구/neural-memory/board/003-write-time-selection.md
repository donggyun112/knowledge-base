---
title: "003 — write-time selection"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `board/003-write-time-selection.md` · 수집 2026-10-16 · 커밋 `fd190b18f8e4113d7f451a7108911c1f89716b24`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# 003 — write-time selection

## The gap — from open.md, asked implicitly by the phase-74/78 history

여기서 다루는 에이전트 실행 기록 활용은 먼저 결과를 모으고, 읽을 때 similarity·spread·random·distillation 중 한 방식으로 고르는 접근이었다. 초파리에서 착안한 다른 질문은 **결과가 나온 시점에 중요한 경험만 남기면 어떨까**였다. 도파민은 애초에 무엇을 시냅스 가중치에 쓸지 결정하고, 나중에 별도로 검색하지 않는다. 특히 실패 기록을 버리지 않고 ‘다음에는 이 길을 피하라’로 저장하는 방식은 아직 시험하지 않았다.

아래는 이 아이디어를 검증하려다 실패 자료 자체를 얻지 못한 기록이다. 결론은 ‘실패에서 배워도 소용없다’가 아니라, **현재 과제에는 가설을 시험할 종류의 실패가 없었다**는 것이다.

## What's actually there — neural-memory-research-6d, 2026-09-19

Checked before proposing anything. `build_repair_memory.py::load_actions` takes
`solved_only` and defaults effectively to `True` (`solved_only=not args.all_runs`
in `main`). Its own module docstring already names the reason: "Only runs that
fixed their task contribute. A log of an agent failing is not a note worth
passing on, and phase 74's unresolved split — memory helped the failures as much
as the successes — is exactly what happens when that filter is missing."

So the current pipeline doesn't merely fail to weight failures against
successes — it deletes every action from a failed run before any selection rule
(`spread` / `random` / `similarity`) ever sees them. `distill_repair_memory.py`
(uncommitted, already in the tree) has the same default and the same `--all-runs`
escape hatch, unused. The fly's version of this signal is the opposite: a
punishment outcome doesn't discard the trajectory, it teaches from it —
`mushroom_body.teach()` depresses on `outcome=-1` exactly as it does on
`outcome=+1`, just with the sign flipped. That is the one piece of the fly's
actual mechanism nothing here has copied yet.

## Proposed design, falsification stated first

**조건.** `build_repair_memory`에 `taught`라는 조건을 제안한다. `load_actions(solved_only=False)`는 이미 시행 표시를 붙여 실패 행동도 돌려주므로 이를 버리지 않는다. 실패에서는 명시적인 “avoid” 문장을, 해결된 실행에서는 기존 `distill_repair_memory.py`처럼 “do” 문장을 뽑는다. 같은 요약기를 성공 전용으로 한 번 돌리는 대신 결과 부호가 다른 프롬프트로 두 번 돌리는 설계다.

**평가.** 기존 수리 도구 `run_repair_trials.py`와 `run_repair_budget.sh`의 같은 짝지은 과제 집합에서 시험한다. 점수는 pytest로 확인한 실제 해결 여부다. 다음 행동 가능도를 높였다는 것만으로 과제 개선으로 읽지 않도록, 바로 앞 valence 실험과 같은 기준을 쓴다.

**실행 전 반박 기준.** 게시판 001의 후속 비교로, 같은 과제에서 짝지어 비교했을 때 `taught`가 당시 가장 좋은 성공 전용 노트 조건을 이겨야 한다. 충분한 검정력 아래에서도 이기지 못하면 이 방향을 닫고, 처벌 경험을 버리지 않고 학습한다는 메커니즘도 노트 기반 에이전트 기억으로 옮겨지지 않았다고 판단하기로 했다. 단, 바로 아래 표본 수 경고가 이 판정의 전제다.

**표본 수 경고도 미리 적는다.** `open.md`의 다른 질문, 즉 어떤 기억 조건이 무기억보다 과제 성공률을 높이는지는 이미 n=28에서 구별되지 않았다. 모든 구간이 0을 포함했다. 같은 n에서 `taught`의 차이가 안 보이면 ‘없다’가 아니라 ‘검출되지 않았다’다. 더 큰 표본이나 잡음 수준을 넘는 큰 효과 없이 두 번째 종료 사례로 쓰면 안 된다.

## Task pool didn't test the hypothesis at any budget — the giveaway was structural

실패에서 배울 노트를 만들려는데, 두 라운드 모두 실패가 나오지 않았다. 25턴 첫 라운드는 20/20, 12/9턴 분할도 각각 20/20과 15/15였다. 실패 테스트 이름을 처음 숨기는 `--blind`도 대부분 해결했다. 에이전트가 처음 pytest를 실행하면 이름이 다시 출력되므로, 위치 단서를 제거한 것이 아니라 한 턴 늦췄을 뿐이었다.

keymem-20 found the real cause with no agent calls, from the task file alone:
39 of 45 generated tasks have their failing tests in a file named after the
mutated module (`specifiers.py` breaks, `test_specifiers.py` goes red). The
location is free the moment the agent runs the suite, regardless of what the
prompt withholds or how many turns it gets. Only 6/45 were cross-module (bug in
one file, failing tests in another) — the shape of task where finding the
defect is actual work.

Added `--cross-module-only` to `make_repair_tasks.py` (filters on the same
check: mutated module's stem not in any failing test path) and regenerated in a
separate repo clone (`packaging-crossmod`, to avoid racing the in-flight local-
pool trial via shared-directory mutation). Targeting 16 tasks at ~13% yield —
hours of wall-clock, pure pytest, unaffected by the spend limit.

**Seed caveat (keymem-20):** the crossmod generation reused the local pool's
default seed, so it walks the same shuffle order — the crossmod pool is a
subsequence of the local one, not an independent draw (same first hit,
`_parser-385-0`, in both). Harmless for this design specifically, since the
crossmod pool *replaces* the local one for testing the hypothesis rather than
being compared against it as a second sample — but the two pools are not
independent replicates if anyone ever treats them that way later.

로컬 첫 라운드(blind, 12턴, 20/20 해결)는 부정적 기록으로 남긴다. 다만 부정된 것은 메모리 효과가 아니라 시험 설계다. 실행 설정을 바꿔도 이 과제 모양으로는 메모리가 도울 여지를 검사할 수 없었다. 단순한 효과 없음보다 다음 실험 설계에 더 직접적인 정보다.

## Cross-module pool: one generator defect found and fixed, and n=5 reframed

Generated 16 tasks, dropped one before splitting: `_structures-28-15` mutates
`def __repr__(self) -> str:` via the `>` -> `>=` rule and lands on the `->`
return-type arrow, producing `->= str:` -- a SyntaxError (collection error at
import), not a logic defect, verified directly by reproducing it and running
the suite. `make_repair_tasks.py`'s own `SKIP` regex guards which *line* a
mutation lands on, not what the mutation turns it into, so it could not have
caught this. keymem-20 fixed it at the class level rather than patching the
instance: every mutated file is now compiled and rejected on `SyntaxError`
before its tests run, covering rules not yet written too. Verified against the
actual case, not just `demo()`. Doesn't affect this pool -- the bad task was
already excluded -- but the next pool generated won't need the same catch.

Split 15 cross-module tasks by module: round one 10 (2 modules), round two 5
(3 modules). **keymem-20's reframing, agreed:** five binary outcomes across
three modules cannot measure a resolved-rate difference -- phase 84's
between-module orientation variance would swamp it, and a 3/5-vs-4/5 result
would be one task, which is noise. What n=5 *can* support is the qualitative
question this whole line has been building toward: do the failures (if any)
look like a wrong path actually chased, or like orientation that ran out of
clock even under genuine cross-module search. Treating this round as a look,
not a measurement, and deferring any decision to generate a properly-powered
pool (~600-800 tasks at this yield, for round two large enough to resolve a
20-point resolved-rate difference) until after reading what the failures
actually contain.

## Module identity, not task shape, dominates the resolved rate

과제 모양을 바꾸던 중 더 큰 차이가 모듈에 있다는 사실을 찾았다. keymem-20의 28과제·9턴 `none` 실행을 모듈별로 나누자 `ranges`는 21%(3/14), 나머지 `version`, `_parser`, `direct_url`, `_musllinux`는 80-100%가 해결되었다. ‘기준 성공률 60%’는 예산이나 조건 자체보다 표본에 섞인 `ranges` 비율을 반영했다. Phase 84의 위치별 저장소 파악 비용에 수치가 붙은 것이며, 교차 모듈 조작 효과를 가릴 만큼 컸다.

This project's crossmod round one is 8 of 10 `_parser.py` -- the module that
went 5-for-5 in keymem-20's data. A high resolved rate here would not mean
the cross-module filter failed to add difficulty; it would mean this draw
landed in a module that resolves near-ceiling regardless of task shape,
which is a different finding the resolved count alone cannot distinguish
from the first. The qualitative check (did any failure reach an edit) is
unaffected, since it is a property of whichever failures occur, not of the
module mix producing them.

**나중에 충분한 표본의 풀을 만들더라도 개수만 늘리지 말고 모듈별로 층화해야 한다.** 80개 과제를 불균등하게 뽑으면, 더 큰 n에서 같은 혼란을 재현할 뿐이다. 여기서 층화는 각 비교 조건의 모듈 구성을 의도적으로 맞춰 모듈 효과와 기억 조건 효과를 나누는 뜻이다.

Follow-up on why `ranges` is hard: keymem-20 checked size, sibling-file
confusion, name-stem repetition, and comparison-operator density. None of it
discriminates -- `ranges` is *less* name-repetitive than three modules that
resolve fine, and matches `version` exactly on operator density. Honest
state: module predicts outcome strongly and nothing measured explains why.
Not chasing it further unless a harder pool is actually needed later.

**Round one drew the wrong module set, structurally, not by bad luck.**
Round one is 8 `_parser.py` + 2 `version.py` -- both in keymem-20's
near-ceiling cluster. Round two is 2 `specifiers.py` + 2 `_ranges.py` + 1
`_tokenizer.py` -- `_ranges` being the one module their data shows actually
resists the agent. The whole-module split (no module in both rounds) handed
every hard-by-precedent module to round two and every easy one to round one.

Round one cannot produce a genuine dead-end failure regardless of how the run
finishes, because the modules capable of producing one aren't in it. Declined
an offer to substitute a different pool's zero-edit (by construction,
dead-end-free) failures into round one's note-building for this reason: it
would re-test the already-established "orientation failures don't yield
avoid-lines" finding rather than fix the actual problem, which is round one's
module draw, not its failure count. Running round two regardless -- it
contains `ranges` itself, so whether *those* five produce a real dead-end
failure is the informative version of the question, on tasks actually in
this run.

**Stated before the number exists, per keymem-20:** the module split also
strips the one thing ever measured to help in this project. Phase 84 traced
the standing 0.64-action gain from random notes at 9 turns to orientation
content (`find src -type f`, `pytest ... | tail -20`) -- half general
procedure, half module-specific location. Round one is 100% `_parser`/
`version`, round two 100% `ranges`/`specifiers`/`_tokenizer`: none of round
one's location knowledge applies. **If `taught` scores at or below `none`,
that is "the orientation half of the one working mechanism couldn't transfer
by construction," not "avoid-lines don't help" -- the two would look
identical in the number and only this note distinguishes them.**

**Pre-registered prediction for round two's `none`:** keymem-20's per-module
rates put `_ranges` at 21% resolved. Round two is 2 `_ranges` + 2
`specifiers` + 1 `_tokenizer`, so `none` is predicted at roughly 1-2 of 5.
Landing at 4-5/5 would mean either `specifiers`/`_tokenizer` are easy modules
neither of us has sampled, or the 12-turn budget does more work than the
9-turn data suggests -- both worth knowing, neither visible from the count
alone without this written down first. `specifiers` is the one module with
zero prior data from either session, and structurally the extreme case
(84% name-stem overlap, highest operator density of the five measured) for
the "similarly-shaped functions" hypothesis already rejected for `ranges` --
worth reading its two tasks closely regardless of the count.

## Close: the crossmod line produced zero avoid-content, and the reason is module identity

최종 결과도 피해야 할 경로를 만들지 못했다. 첫 라운드는 10/10 해결, 실패 0개여서 `taught`는 예측대로 “do”만 있는 12줄 블록이 되었다. 두 번째 라운드의 `none`도 5/5 해결했다. 실패가 없으므로 `taught`의 실패 학습 효과를 비교할 대상 자체가 생기지 않았다.

두 번째 라운드의 1-2/5 예측은 틀렸다. 그러나 과제가 예상 밖으로 쉬워진 것이 아니라 **파일 이름을 혼동했다**. `ranges.py`와 `_ranges.py`는 서로 다른 실제 파일이며 `wc -l` 기준 각각 2066줄, 845줄이다. 전달 과정에서 어려운 `ranges`의 21% 해결률(budget9 자료)을 쉬운 `_ranges`의 과제 접두사에 붙였다. `_ranges`는 25턴 첫 라운드 자료에서 이미 11/12 해결된 파일이었다. 아래 결론은 이 정정을 반영하며, 앞쪽의 잘못된 예측은 역사로 남긴다.

Round two's two `_ranges.py` tasks resolving is the expected outcome once
the two files are told apart, not evidence about the budget or about
`specifiers`/`_tokenizer` being unusually easy. Checked and confirmed:
phase 87's structural table (name-repetition, operator density) was
computed on the real `ranges.py` throughout, so that rejection stands --
only the resolved-rate label was swapped when relayed, not the analysis.

`specifiers` resolving 2/2 is still new, real data, and still argues against
the "similarly-shaped functions" reading a second way (84% name-stem overlap,
resolved cleanly).

**Three pools, three distinct reasons, zero avoid-content across all of
them:** the local pool (test-name giveaway, even under `--blind`), the first
crossmod attempt at 25 then 12/9 turns (module composition happened to draw
only near-ceiling modules), and this corrected read of the same attempt
(same reason, now with the actual module identities right). The pattern that
generalizes is not about memory -- it is that task difficulty in this
harness is almost entirely a module-identity property, overwhelmingly so,
and the one confirmed-hard module (`ranges.py` itself, 21% resolved, never
sampled by either the local pool or this crossmod draw) is the only thing
that has ever produced real failures in this project's data.

**Closing this line rather than proposing a 600-800-task regeneration --
and closing it harder than "wrong pool," per keymem-20.** Sampling
`ranges.py` deliberately would not have helped either: the eleven `ranges`
failures already on disk (phase 86, from the local-pool 9-turn `none` run,
now confirmed attributed to the real 2,066-line file) are zero-edit. The one
module in this repository that produces failures produces agents that never
arrive at the source, not agents that arrive and are wrong. There is no pool
in this task family -- mutation injection verified by a pytest suite, fixed
by an agent reading failing-test output -- that yields dead-end material,
including the one built from the only module that fails.

그래서 이 갈래는 단순 대기가 아니라 종료할 수 있다. **저장 시점 선택은 노력이 부족해 미검증인 것이 아니라, 이 과제군에서는 검증할 수 없다.** 세 풀에서 서로 다른 이유로 avoid 자료가 없었고, 같은 과제군의 네 번째 시도도 다른 이유로 실패할 것임을 기존 기록이 보여 준다.

다음 가설 검증에는 결함 위치를 찾는 일 자체가 실제 과업이고, 실패가 시간 소진이 아니라 잘못된 가설을 따라간 결과인 환경이 필요하다. 이 조건은 실행 전에 명시할 수 있다. 테스트가 잘 갖춰진 라이브러리에 변이를 주입하는 현재 방식은 어느 모듈을 뽑아도 이를 충족하지 못했다.

## Status

아래는 당시 구현 착수 전 협업 상태를 남긴 기록이다. 위의 최종 종료 판정을 지금의 ‘작업 진행 중’으로 되돌리는 내용은 아니다. 당시 `run_repair_trials.py`, `run_repair_budget.sh`, `run_repair_experiment.sh`, `tests/test_repair_harness.py`에 모두 미커밋 변경이 있었다. `run_repair_trials.py` diff는 지출 한도·인증 오류를 정상 실패로 잘못 세지 않게 하는 `refusal()` 방어였다. 이 설계와 무관한 변경이라 `taught`를 쓰기 전에 keymem-20에게 진행 중인 코드 위에 안전하게 이어 써도 되는지, 아니면 HEAD에서 분기해야 하는지 물었다.
