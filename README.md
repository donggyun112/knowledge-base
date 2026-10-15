# Donggyun의 지식베이스

AI 리서치와 직접 수행한 메모리 실험을 관리하는 지식베이스입니다. 폴더 탐색, 검색, 백링크와 관계 그래프를 제공합니다.

사이트: https://donggyun112.github.io/knowledge-base/

## 로컬 실행

Node 24 이상, npm 10.9.2 이상, Python 3.9 이상이 필요합니다.

```sh
npm ci
npx quartz build --serve
```

GitHub에서 받은 content 폴더는 이미 정리된 공개 사본이므로 원본 Vault 없이도 빌드됩니다.

## 자료 관리와 배포

이 저장소의 `content/`가 연구 자료의 관리 원본입니다. 새 자료와 수정은 여기에서 작업합니다. Obsidian의 기존 노트는 최초 이전 자료이며, 더 이상 기본 동기화 원본으로 사용하지 않습니다.

```sh
npx quartz build
git diff -- content
git add content
git commit -m "docs: update knowledge base"
git push
```

push하면 GitHub Actions가 빌드 후 Pages를 갱신합니다. 자료 간 연결은 `[[문서 경로|제목]]`으로 작성합니다. 원시 대화·인증 정보·개인 업무 구상·데이터셋·가중치는 게시하지 않습니다.

`content/메모리-연구/`에는 procedural-graphs-lab와 neural-memory-research의 연구 문서 및 읽기 안내가 있습니다. 수집 출처·원본 SHA-256·커밋/미커밋 구분은 `docs/research-import-2026-10-16.json`에 보존했습니다. 원본 프로젝트의 코드와 문서는 수정하지 않았습니다.

### 이전 내보내기 도구

`scripts/export_notes.py`는 최초 Obsidian 이전용 도구입니다. 현재는 `--source`와 `--destination`을 모두 지정해야 하며 관리 중인 `content`로의 출력은 거부합니다. 과거 노트의 재수집이 필요하면 별도 디렉터리로 내보내고 필요한 문서만 검토해 합칩니다.

조사일(researched)·출처·미확인 항목은 원래 노트 기준입니다. 배포 날짜는 최신 사실 검증일이 아닙니다.

Quartz 소스 버전은 [UPSTREAM.md](UPSTREAM.md)에 기록했습니다. npm 플러그인과 의존성은 package-lock.json에 고정됩니다. 별도 Git 플러그인은 사용하지 않으므로 quartz.lock.json은 생성되지 않습니다.
