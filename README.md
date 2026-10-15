# Donggyun의 지식베이스

Obsidian research 노트 공개본입니다. 폴더 탐색, 검색, 백링크와 관계 그래프를 제공합니다.

사이트: https://donggyun112.github.io/knowledge-base/

## 로컬 실행

Node 24 이상, npm 10.9.2 이상, Python 3.9 이상이 필요합니다.

```sh
npm ci
npx quartz build --serve
```

GitHub에서 받은 content 폴더는 이미 정리된 공개 사본이므로 원본 Vault 없이도 빌드됩니다.

## Obsidian 변경 반영

```sh
python3 scripts/export_notes.py
python3 -m unittest discover -s tests -p 'test_export_notes.py' -v
npx quartz build
git diff -- content
git add content
git commit -m "docs: update knowledge base"
git push
```

기본 원본은 `/Users/dongkseo/Documents/Obsidian Vault/research`입니다. 다른 경로에서는 `python3 scripts/export_notes.py --source '/path/to/research'`로 지정합니다. 원본은 수정하지 않으며 삭제된 원본 노트는 다음 내보내기에서 공개 사본에서도 제거합니다.

`publish-excludes.txt`로 제외할 파일명 또는 research 상대 경로를 관리합니다. 회사 활용 구상 절은 공개본에서 제외하고 본문에 남은 소속 회사 이름은 일반화합니다. 개인 링크 모음·로그인 라이브러리는 제외합니다. 코드 예제는 보존합니다. 전체 Vault나 .obsidian은 업로드하지 않습니다.

INDEX.md는 대소문자 구분이 없는 파일시스템에서 홈 index.md와 충돌하므로 공개본에서 research-index.md로 내보냅니다. 관련 링크도 함께 변환합니다.

Obsidian에서 저장만 하면 사이트가 바뀌는 것은 아닙니다. 공개 사본을 검토하고 push하면 GitHub Actions가 갱신합니다. Actions는 로컬 Vault에 접근하지 않습니다.

조사일(researched)·출처·미확인 항목은 원래 노트 기준입니다. 배포 날짜는 최신 사실 검증일이 아닙니다.

Quartz 소스 버전은 [UPSTREAM.md](UPSTREAM.md)에 기록했습니다. npm 플러그인과 의존성은 package-lock.json에 고정됩니다. 별도 Git 플러그인은 사용하지 않으므로 quartz.lock.json은 생성되지 않습니다.
