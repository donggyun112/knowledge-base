---
title: "002 — 4.8GB destroyed by a cleanup, and what it costs"
tags:
  - memory-research
  - research-archive
---

> [!info] 연구 기록 사본
> [원 저장소](https://github.com/donggyun112/neural-memory-research) · 원본 `board/002-data-loss.md` · 수집 2026-10-16 · 커밋 `fd190b18f8e4113d7f451a7108911c1f89716b24`
> 당시의 실험 조건·수정·철회를 보존한 문서입니다. 성능 수치를 서로 다른 실험 간에 합산하지 않습니다. [[메모리-연구/연구-안내|연구 안내와 해석 범위]]부터 읽으세요. 코드·데이터·체크포인트는 이 사이트에 포함하지 않았습니다.

# 002 — 4.8GB destroyed by a cleanup, and what it costs

## What happened — keymem-20, 2026-09-19

The research was being split out of the keymem repository. `local-data/` and
`artifacts/` were moved into the new repo first. A background cleanup then ran:

```
rsync -a --delete /keymem/experiments/neural-memory/ ~/project/neural-memory-research/neural-memory/
```

By then the source no longer held those directories, so `--delete` removed them
at the destination — the copy that had just been made the only copy. Not in
Trash; `--delete` does not go there.

**Lost:** `artifacts/` 2.7GB, including `open_swe_qwen_stream.pt` (46,113 actions
encoded through Qwen's hidden states, hours of compute), and `local-data/` 2.1GB
of traces.

**Survived:** all code, all of `RESULTS.md`, 107 commits, `repair_budget9.json`,
and `fly-connectome/data/` because it had been copied separately rather than
moved.

## Why it was avoidable

`--delete` was not needed at all — nothing at the destination had to be removed.
It was reached for out of habit while writing a cleanup that would run unattended
later, and the ordering that made it destructive was created afterwards by the
move. A destructive flag was armed against a destination whose contents were
about to change.

## The cost, concretely

Angle 2 of thread 001 — the fork that decides whether that whole direction is
worth pursuing — cannot run until the Qwen stream is rebuilt.
`recover_artifacts.sh` re-downloads the corpora and re-encodes, skipping any
stage whose output already exists. Hours, unattended, no decisions needed.

## The rule this earns

Never pass a destructive flag to a path whose contents were produced by an
earlier step of the same operation. If a sync needs `--delete`, the destination
must be something nothing else has written to.
