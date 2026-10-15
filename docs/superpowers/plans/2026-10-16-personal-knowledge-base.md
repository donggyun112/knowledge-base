# 개인 지식베이스 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for native implementation, or superpowers:subagent-driven-development only if the user selects delegation. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Obsidian research 노트의 공개 사본을 검색·백링크·그래프로 탐색하는 GitHub Pages 사이트를 배포한다.

**Architecture:** Quartz v5의 기본 렌더러·검색·그래프를 재사용한다. 로컬 내보내기가 원본을 읽어 공개 사본만 만들고, GitHub Actions는 사본으로 정적 사이트를 빌드한다. 기존 Inception 사이트와 Obsidian 원본은 수정하지 않는다.

**Tech Stack:** Quartz 5.0.0, Node 24 LTS, npm lockfile, Python 표준 라이브러리 내보내기·unittest, GitHub Actions/Pages.

**Spec:** `docs/superpowers/specs/2026-10-16-personal-knowledge-base-design.md`

## Global Constraints

- 원본: `/Users/dongkseo/Documents/Obsidian Vault/research`.
- 로컬 작업: `/Users/dongkseo/project/research`.
- 저장소: `donggyun112/knowledge-base`; 예상 사이트: `https://donggyun112.github.io/knowledge-base/`.
- 제목: `Donggyun의 지식베이스`.
- 연구 본문·출처·조사일·미확인 사항은 보존한다.
- 회사 활용 구상 절과 `non-research-links.md`, `speechify-library.md`는 공개본에서 제외한다.
- 원본 전체나 원본이 포함된 Git 이력을 공개 저장소에 넣은 뒤 나중에 삭제하는 방식을 쓰지 않는다.
- Git push 후 Actions로 갱신하며, 무인 파일 감시나 예약 업로드는 설치하지 않는다.
- RAG·임베딩·DB·서버·로그인·분석 추적·새 도메인 구매는 하지 않는다.

## Review Focus

1. 한글 파일명·별칭·앵커와 GitHub Pages 하위 경로: 본문 이동·검색·그래프 클릭이 같은 노트에 도달해야 한다.
2. 코드 블록 안의 헤딩·위키링크: 예제 내용을 제거하거나 실제 그래프 연결로 만들지 않아야 한다.
3. 원본에서 삭제되거나 제외된 노트: HTML·검색 인덱스·그래프·커밋에서 모두 제외돼야 한다.
4. 원본 폴더 밖을 가리키는 심볼릭 링크 및 잘못된 출력 경로: 원본 변경이나 범위 밖 공개 없이 실패해야 한다.
5. 공개 제외 절의 제목 변형: 공개 사본에 회사 활용 구상이 남지 않아야 하고 일반 연구 절은 보존돼야 한다.

---

### Task 1: Quartz와 공개본 내보내기

**Files:**
- Create: `scripts/export_notes.py`, `tests/test_export_notes.py`, `publish-excludes.txt`, `.gitignore`, `UPSTREAM.md`.
- Import: Quartz upstream commit `97a2d05f80c4c50534959b1d0d41cc4b3895625e`의 소스·lockfile·라이선스. 실행 시 커밋 접근 여부를 확인한다.
- Generate: `content/`와 로컬 전용 `.local/export-report.json`.

**Interfaces:**
- Consumes: 원본 Markdown 경로와 제외 목록.
- Produces: `sanitize_note(text: str) -> str`, `export_notes(source: Path, destination: Path) -> dict` 및 `python3 scripts/export_notes.py` CLI. CLI 기본 입력은 합의된 research 경로, 출력은 이 저장소의 `content/`다.

- [ ] **Step 1: 승인 후 소스 가져오기**

원본 경로에 clone하지 않는다. 임시 폴더에 고정 커밋을 가져와 Git 이력 없이 사이트 소스만 현재 작업 폴더에 복사한다. 기존 `docs/superpowers/`를 보존하고 Quartz 예제 content/docs는 사이트에 포함하지 않는다. 새 저장소는 로컬에서 초기화하고 고정 커밋을 기록한다.

```sh
git init
git branch -M main
node --version
npm --version
```

Node가 현재 환경에서 의존성을 설치·빌드하지 못하면 기존 Node 설치 목록에서 24를 사용한다. 시스템 Node를 교체하지 않는다.

- [ ] **Step 2: 실패하는 내보내기 테스트 작성**

```python
def test_removes_private_section_and_keeps_source(self):
    text = '# Note\n## 우리 맥락(인포뱅크) 활용 아이디어\n내부 구상\n## 출처\nhttps://example.org\n'
    actual = sanitize_note(text)
    self.assertNotIn('내부 구상', actual)
    self.assertIn('## 출처', actual)

def test_fenced_heading_is_not_a_section(self):
    text = '# Note\n```md\n## 우리 맥락\nexample\n```\n## 출처\nsource\n'
    self.assertEqual(sanitize_note(text), text)
```

동일 테스트 파일에서 TemporaryDirectory로 원본 해시 불변, 제외 파일 미생성, 출력에만 있는 낡은 파일 제거, 원본 내부·외부 심볼릭 링크 거부, 출력이 원본과 같거나 원본의 조상·자손이면 거부, 제목에 숫자 접두어가 붙은 회사 절 제거를 검사한다. 미리보기에서 제외 링크를 누르지 못하도록 INDEX·READING-GUIDE의 해당 항목 제거도 검사한다.

```sh
python3 -m unittest discover -s tests -p 'test_export_notes.py' -v
```

Expected: 구현 전 import 실패. 구현 후 모두 통과.

- [ ] **Step 3: 최소 내보내기 구현**

Markdown fence와 ATX heading 깊이를 추적해 회사 활용 구상 heading부터 다음 동급·상위 heading 직전까지만 제거한다. 파일 전체를 민감 키워드로 삭제하지 않는다. 원문 source·researched frontmatter는 유지한다. JSON 내보내기 기록은 `.local/`에 두고 Git에서 제외한다. 안전 검사 후 공개본 전체를 새 staging 디렉터리에 만들고 대상 공개본만 교체한다.

공개 홈 `content/index.md`는 제목과 기존 분류·INDEX·READING-GUIDE 링크만 생성한다. 임의의 연구 설명이나 홍보 글은 추가하지 않는다. 원본 삭제와 제외 목록 변경이 다음 내보내기에 반영되게 한다.

- [ ] **Step 4: 테스트와 실데이터 검증**

```sh
python3 -m unittest discover -s tests -p 'test_export_notes.py' -v
python3 scripts/export_notes.py
```

원본 전체 Markdown의 전후 해시를 대조한다. 내보내기 보고서의 제거 절·파일 수를 확인하고 남은 `우리 맥락`, `인포뱅크` 문맥을 원문과 대조한다. 코드 예시 속 위키링크와 실제 미해결 링크를 구분한다. 다른 원본 파일은 생성·수정하지 않는다.

- [ ] **Step 5: 검토 후 첫 커밋**

`git status --short`와 staged 파일 목록에서 원본 vault, `.obsidian`, `.local`, 모델·실험 파일이 없음을 확인한 뒤 사이트 소스와 공개 사본만 커밋한다.

### Task 2: 사이트 설정·로컬 검증

**Files:**
- Create: `quartz.config.yaml`.
- Modify: `quartz/styles/custom.scss`는 한글 가독성 문제를 실제 확인한 경우에만 최소 조정.
- Generate: `quartz.lock.json`, `public/` (public은 Git 제외).

**Interfaces:**
- Consumes: Task 1의 `content/`.
- Produces: `npx quartz build` 정적 산출물과 로컬 미리보기.

- [ ] **Step 1: 기본 설정을 재사용해 필요한 값만 변경**

```yaml
configuration:
  pageTitle: Donggyun의 지식베이스
  locale: ko-KR
  baseUrl: donggyun112.github.io/knowledge-base
  analytics: null
```

v5 설정 타입에서 analytics 비활성 값을 확인하고 해당 타입에 맞춘다. 기존 search·graph·backlinks·Obsidian/GFM·LaTeX 플러그인을 유지한다. 예제 footer 링크를 개인 GitHub 저장소 링크로 바꾼다. 조사일은 `researched` 값을 공개 메타데이터에 보존하며 파일 복사 시간을 재검증 날짜로 표시하지 않는다.

- [ ] **Step 2: 잠금 파일로 설치·빌드**

```sh
npm ci
npx quartz plugin install --from-config
npx quartz build
```

플러그인 lockfile을 생성·고정하고 경고·실패를 확인한다. 설치 중의 자동 외부 배포는 실행하지 않는다. 제품 기능에 불필요한 플러그인은 기존 비활성 상태를 유지한다.

- [ ] **Step 3: 산출물 확인**

홈, RAG 분류, PageIndex 노트의 HTML을 읽고 한글 제목·출처·callout·코드·표·Mermaid가 보존되는지 확인한다. Content Index에 제외 노트와 제거 절의 문자열이 없고 그래프 노드와 페이지가 일치하는지 확인한다. 링크 오류가 코드 샘플 때문이면 샘플을 실제 문서 링크로 재작성하지 않는다.

- [ ] **Step 4: 실제 브라우저 확인**

```sh
npx quartz build --serve
```

로컬 페이지를 열어 `PageIndex` 검색→결과 이동, 위키링크→본문, backlink→연결 노트, graph 노드 클릭, 다크모드·모바일 폭을 확인한다. 미리보기를 사용자에게 열어 보여준다. 도구가 브라우저 검증을 지원하지 않으면 그 경계를 보고하고 HTTP·산출물 검사를 남긴다.

### Task 3: GitHub Pages 배포와 갱신 안내

**Files:**
- Create: `.github/workflows/deploy.yml`, `README.md`.
- Modify: `.gitignore`에 `.local/`과 출력·캐시 제외를 확인.

**Interfaces:**
- Consumes: 검증된 공개 소스·콘텐츠·잠금 파일.
- Produces: GitHub 저장소, 성공한 Pages workflow, 실제 사이트 URL.

- [ ] **Step 1: 공식 Pages workflow 구성**

main push와 workflow_dispatch에 반응하고 checkout → Node 24 → npm ci → 고정 플러그인 설치 → Quartz build → upload-pages-artifact → deploy-pages 순으로 실행한다. permissions는 contents:read, pages:write, id-token:write, deployment environment는 github-pages로 제한한다. Actions는 로컬 vault를 읽지 않고 커밋된 공개본만 빌드한다.

- [ ] **Step 2: 갱신 명령 문서화**

```sh
python3 scripts/export_notes.py
npx quartz build
git diff -- content
git add content
git commit -m "docs: update knowledge base"
git push
```

최초 설치와 Node 요구사항, 제외 목록 변경, 원본 노트 삭제 반영, source 경로가 다를 때 CLI 인자, 공개 범위, Quartz 고정 버전을 README에 적는다. 원본 변경만으로 자동 배포된다고 안내하지 않는다.

- [ ] **Step 3: 공개 파일 최종 확인 후 배포**

```sh
git status --short
git ls-files
gh repo create donggyun112/knowledge-base --public --source=. --remote=origin
git push -u origin main
gh api --method POST repos/donggyun112/knowledge-base/pages -f build_type=workflow
gh run list --repo donggyun112/knowledge-base --limit 3
```

저장소가 이미 존재하면 생성·덮어쓰기를 하지 말고 현재 상태를 확인한다. Pages 설정 API가 이미 설정됐다는 응답이면 현재 설정을 읽어 workflow 방식인지 확인한다. 인증·Pages 정책에 막히면 로컬 완성본을 보존하고 실제 오류와 남은 단계를 보고한다.

- [ ] **Step 4: 배포 검증과 완료 보고**

workflow 성공 여부와 배포 URL 응답을 확인한다. 한글 노트·검색 자산·그래프 자산의 배포 경로를 확인하고 가능하면 배포 화면에서도 검색·노드 이동을 실행한다. 로컬·원격에서 검증한 범위를 구분해 보고하고 사이트 URL과 작업 폴더를 제공한다.

## Plan self-review

- 세 task가 원본 불변·공개 사본·Quartz 설정·렌더링·검색·그래프·갱신·GitHub Pages 배포를 모두 포함한다.
- Review Focus 1은 Task 2·3, 2~5는 Task 1의 테스트와 공개본 검사로 검증한다.
- 외부 배포는 로컬 검증과 공개 파일 확인 이후 실행한다.
- 새 저장소 작업이므로 기존 프로젝트와 공유하는 코드·인터페이스 변경은 없다.
- 설계 디렉터리는 현재 Git 저장소가 아니므로, 승인 후 첫 사이트 커밋에 설계·계획을 함께 포함한다.
