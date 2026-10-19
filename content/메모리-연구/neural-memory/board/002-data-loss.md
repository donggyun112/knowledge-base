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

연구를 keymem 저장소에서 분리하는 중이었다. `local-data/`와 `artifacts/`를 먼저 새 저장소로 옮겼는데, 이후 백그라운드 정리 작업이 다음 명령을 실행했다.

```
rsync -a --delete /keymem/experiments/neural-memory/ ~/project/neural-memory-research/neural-memory/
```

그 시점에는 원본 경로에 두 디렉터리가 없었다. `--delete`는 원본에 없는 파일을 대상에서도 지우므로, 막 옮겨 유일한 사본이 된 대상 파일들이 삭제되었다. 휴지통으로 간 것도 아니다. `--delete`는 휴지통을 거치지 않는다.

**잃은 것:** `artifacts/` 2.7GB. 여기에는 Qwen 은닉 상태로 인코딩한 행동 46,113개의 `open_swe_qwen_stream.pt`가 포함되며, 재생성에 수 시간의 계산이 필요하다. 실행 기록을 담은 `local-data/` 2.1GB도 잃었다.

**남은 것:** 모든 코드, `RESULTS.md` 전체, 커밋 107개, `repair_budget9.json`, 그리고 `fly-connectome/data/`. 마지막 디렉터리는 이동이 아니라 별도 복사했기 때문에 살아남았다.

## Why it was avoidable

대상에서 지워야 할 것이 없었으므로 애초에 `--delete`가 필요하지 않았다. 나중에 무인 실행할 정리 작업을 습관적으로 작성하며 넣은 옵션이었다. 그 뒤 디렉터리를 옮기는 순서가 추가되면서 파괴적인 조건이 만들어졌다. 즉 대상 내용이 곧 바뀔 작업에 삭제 옵션을 미리 걸어 둔 것이 원인이었다.

## The cost, concretely

게시판 001의 두 번째 갈래(Angle 2)는 전체 연구 방향을 계속할지 결정하는 비교였다. Qwen 스트림이 복구되기 전에는 그 실험을 실행할 수 없다. `recover_artifacts.sh`는 말뭉치를 다시 내려받고 재인코딩하며, 결과가 이미 있는 단계는 건너뛴다. 추가 결정 없이 무인으로 복구할 수 있지만 수 시간이 든다.

## The rule this earns

같은 작업의 앞 단계에서 만든 결과 경로에 파괴적 옵션을 적용하지 않는다. 동기화에 꼭 `--delete`가 필요하다면, 대상은 다른 단계가 아무것도 쓰지 않는 경로여야 한다. 여기서 비용은 원시 자료만이 아니라 다시 계산해야 하는 파생 자료의 시간까지 포함한다.
