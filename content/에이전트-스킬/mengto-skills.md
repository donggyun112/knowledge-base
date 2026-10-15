---
title: Agent Skills (MengTo/Skills)
source: https://github.com/MengTo/Skills
type: repo
category: 에이전트-스킬
tags: [research, agent-skills, SKILL.md, web-design, frontend, three.js]
researched: 2026-10-01
---
# MengTo/Skills

> [!summary] 한줄요약
> 디자이너 Meng To가 만든 SKILL.md 기반 agent skill 모음(MIT, 스타 약 6.5k). 클론 기준 SKILL.md 155개 — web-design 91, codex 20, game-development 20, 3d 15, workflow 4, ui 3, media 2 — 가 "프롬프트는 자산, 스펙이 감성을 이긴다"는 철학 아래 폴더 단위로 버전 관리된다. 실행 코드보다 **지시문(절차·기본값·함정·승인 기준)의 작성 방식**을 배우기에 가치가 큰 저장소다.

## 배경 — 해결하려는 문제

UI/프론트엔드 작업을 코딩 에이전트(Codex, Claude, Cursor 등)에 맡길 때 매번 같은 말을 반복하게 된다. "레퍼런스 영상을 보고 이 모션을 재현해줘", "스크린샷 먼저 보여줘", "8점 이상 나올 때까지 고쳐줘", "변경마다 changelog 쓰고 push해줘" 같은 지시다. 이 저장소의 출발점은 그 반복 지시를 **파일로 고정**하는 것이다. README는 목적을 이렇게 요약한다: 좋은 프롬프트, 워크플로, 스타일 시스템, 캡처 레시피, 디버깅 습관을 "에이전트가 로드해서 따를 수 있는 버전 관리 파일"로 바꾼다.

README의 4대 철학은 설계 원칙으로도 읽을 수 있다.

1. **Prompts are assets** — 한 번 좋았다면 재사용 가능해야 한다. 파일로 저장하고 버전 관리하고 라이브러리/스타일카드로 만든다.
2. **Specs beat vibes** — 일관된 결과의 지름길은 명확한 제약, 명확한 위계, "한두 가지만 바꾸는" 반복이다.
3. **References beat paragraphs** — 스크린샷과 예시가 폰트, 간격, 색, 레이아웃 리듬, 아이콘 스타일을 문장보다 정확히 전달한다.
4. **Skills are operating procedures** — 좋은 skill은 언제 쓰는지, 무엇을 먼저 하는지, 어떤 기본값을 적용하는지, 어떤 실수를 피하는지를 정확히 적는다.

또한 "Portable by default" 원칙으로, 특정 사용자·레포 정보 없이 어디서나 동작해야 하며 프로젝트별 정보는 로컬 지침(`AGENTS.md` 등)에 둔다고 명시한다.

## 구조와 계약

### 디렉터리 구조 (클론에서 확인)

루트에는 `agent-skills/`, `assets/`(README용 GIF `aura-build-superprompt.gif`와 `runtime`), `scripts/`(Node 스크립트 5개, 합계 약 2,490줄), `CLAUDE.md`, `DEMOS.md`(약 28KB), `SCREENSHOTS.md`(약 55KB)/`SCREENSHOTS.html`/`SCREENSHOTS-preview.jpg`, `LICENSE`(MIT, "Copyright (c) 2026 Meng To")가 있다. 크기는 `agent-skills` 약 97MB, `.git` 약 49MB(shallow clone 기준)로, 데모의 이미지·모델·텍스처가 용량 대부분이다.

카테고리별 SKILL.md 수를 `find`로 집계하면 다음과 같다.

| 카테고리 | 개수 | 성격 |
|---|---|---|
| web-design | 91 | 라이브러리 가이드(gsap, threejs, tailwindcss, matterjs, globe-gl, vantajs, cobejs, unicorn-studio), CSS 디테일(progressive-blur, css-alpha-masking, css-border-gradient), 레이아웃·무드 스타일(`dark-glass-clean-layout`, `clean-minimal-beige-light-mode` 등), 모션·스크롤 스토리텔링 |
| codex | 20 | 에이전트 작업 절차(영상→프롬프트, 풀페이지 캡처, 일일 UI 영감, 브라우저 영상 녹화, elevenlabs-tts, GitHub 게시 등) |
| game-development | 20 | Three.js 기반 ARPG: 카메라, 전투, 적 AI, 인벤토리, VFX, 모바일, 최적화, QA, 릴리스 |
| 3d | 15 | 물·하늘·재질(나무/금속/종이/천)·텍스처·Retina 렌더링 |
| workflow | 4 | progress-screenshots, score-to-target, ship-change, threads-manager |
| ui | 3 | design-first-ui-prompting, no-ai-design-slop, audit-ai-design-slop |
| media | 2 | aura-asset-images, unsplash-asset-images |

README 본문은 "146 skills"로 적혀 있지만 실제 클론의 SKILL.md는 155개다(README 수치가 최신 커밋을 따라가지 못한 것 — web-design 81 대 91, codex 19 대 20으로 어긋남). README가 스스로 "`find agent-skills -name SKILL.md | sort`가 source of truth"라고 안내하는 이유다. 최신 커밋(2026-10-01)은 "fire paper loader, paper cinder transition, horizontal scroll scenes" skill 추가였다.

### Folder contract

```txt
agent-skills/<category>/<skill-name>/
  SKILL.md            # 필수: frontmatter(name, description) + 절차
  REFERENCES.md       # 선택: 링크만
  ARTICLE.md          # 선택: 장문 설명 (SKILL.md는 간결하게 유지)
  assets/  scripts/   # 선택
  demo/
    index.html        # 단일 파일 HTML/CSS/JS, 빌드 없음
    PROMPT.md         # 최소/재현/리믹스 프롬프트
    preview.jpg       # 1280x720 렌더 스크린샷
    source.json       # Neuform 출처·랭킹 스냅샷
    input.md / expected-output.md   # workflow skill용
```

관례도 구체적이다: "Use when..." 형태의 명시적 트리거가 모호한 설명보다 낫다, 기본값(지속시간, 간격, 위계, 명령, 수용 기준)을 적는다, 절차적(procedural)이어야 하며 백과사전식이면 안 된다. `CLAUDE.md`는 Claude Code용 레포 가이드로, "가장 구체적인 skill 폴더를 찾고 → SKILL.md 먼저 수정 → REFERENCES.md 갱신 → 작은 커밋" 순서와 "비밀·API 키·고객 정보 금지"를 적는다. 한편 `agents/openai.yaml`(84개 파일) 같은 Codex UI 메타데이터(`display_name`, `short_description`, `default_prompt`)가 skill마다 붙어 있어 사실상 **Codex 우선**으로 만들어졌고 Claude/Cursor는 "복사·참조"로 지원하는 형태다.

### 데모 파이프라인 (scripts/)

`validate-skill-demos.mjs`(232줄)는 `git ls-files`로 모든 SKILL.md를 순회해 demo 파일(html, prompt, preview 크기, workflow 입출력, source.json)의 존재와 형식을 검증하고 실패 목록을 낸다. `backfill-skill-demos.mjs`(948줄)는 빠진 demo를 채우되 손으로 다듬은 예제는 덮어쓰지 않으며, `build-demo-screenshot-gallery.mjs`는 SCREENSHOTS 갤러리를 만든다. 흥미로운 것은 `sync-neuform-skill-demos.mjs`(944줄)로, Neuform(neuform.ai)의 "skill별 인기 디자인"을 받아 demo로 동기화한다. 예컨대 `gsap/demo/source.json`에는 `provider: Neuform`, `skill.usage_count: 2827`, 랭킹 기준(`view_count desc` 등), 원본 HTML의 `sha256`이 기록돼 있다. 이 스크립트는 보안 의식이 높다: 자산 5MB 제한, DNS lookup/`isIP` 검사(SSRF 방지로 보임), 허용 CDN 호스트 화이트리스트(`cdn.tailwindcss.com`, `cdnjs.cloudflare.com`, `code.iconify.design`, 폰트 호스트), 그리고 데모를 `default-src 'none'`로 시작하는 CSP와 `postMessage`로 자산을 blob URL로 주입하는 샌드박스 래퍼로 감싼다. `test-sync-neuform-security.mjs`가 그 하드닝을 테스트한다. 즉 "외부에서 생성된 HTML을 skill 데모로 포함"하는 위험을 코드로 다뤘다는 점이 확인된다.

## 대표 skill 상세 (직접 읽은 것)

**video-to-superprompt** (플래그십). 레퍼런스 영상을 "빌더가 바로 쓸 수 있는 초상세 프롬프트"로 바꾼다. 절차는 6단계: (1) 영상 확보 — 접근 불가면 지어내지 말고 파일/URL을 요청, (2) `ffprobe`로 길이·해상도·fps·코덱, `ffmpeg -vf fps=1`로 프레임 추출, 타임라인 비트 위주 선별, (3) 층별 분석 — 스토리, 레이아웃, 모션(타이밍·easing·parallax·mask·pin·scrub), 시각 디자인, 기술 재구현(IntersectionObserver, GSAP ScrollTrigger, Lenis, Three.js, `video.currentTime` scrubbing), 접근성·성능, (4) 에셋 맵, (5) 단일 ```text 블록으로 프롬프트 작성 — "make it beautiful" 같은 모호한 표현 금지, 모든 섹션에 목적·레이아웃·애니메이션·라이브러리·reduced-motion 폴백 명시, (6) 에셋 경로 실재 검증. 품질 기준이 "원본 영상을 안 보고도 재구현 가능한 길이"라는 점이 인상적이다. `references/superprompt-template.md`를 별도 둔다.

**html-to-interaction-prompts / daily UI inspiration contract.** HTML 소스를 읽고(`mousemove`, `canvas`, `ScrollTrigger`, `requestAnimationFrame` 등 검색) 재사용 가능한 인터랙션 프롬프트로 쪼개 스크린샷과 함께 article로 낸다. "소스 동작이 진실이며 HTML이 있으면 스크린샷만으로 추론하지 말 것", "프롬프트에 색·크기·DOM id 하드코딩 금지(정확 재현 요청이 아닌 한)" 같은 규칙이 있고, 일일 영감 워크플로에는 정확히 5개, 실제 `pageUrl` 녹화 MP4, 풀페이지 한 장에서 잘라낸 섹션 크롭 등 매우 세세한 산출물 계약이 있다. 다만 이 부분은 저자의 특정 블로그/아티클 파이프라인에 묶여 있어 그대로 이식하기 어렵다.

**stitched-full-page-capture.** 브라우저의 one-shot `fullPage` 캡처가 lazy/Framer/WebGL 페이지에서 빈 화면이 되는 문제에 대한 해법: 한 번 끝까지 스크롤해 워밍업 → 뷰포트 단위(기본 1440x1100, step 950)로 내려가며 스크롤마다 2초 대기 후 캡처 → 세로로 stitch → 섹션 크롭은 stitched 이미지에서 생성. 빈/회색 밴드 등 거부 기준도 있다. `scripts/stitch_full_page_capture.mjs`가 Playwright Chromium과 ffmpeg로 이를 자동화한다.

**workflow 4종.** `workflow-score-to-target`은 "8/10까지"라는 사용자 요구를 절차화한다: 대상 항목 나열, 앵커된 rubric(10=연구 대상, 6=수용 가능 …), 항목당 3~5 기준 x 0~2점, 가능한 곳은 수치로 측정(발 미끄러짐 10% 미만, 40 seed 승률 48% 등), 실제 렌더/녹화에서 채점, 독립(블라인드) 심사 서브에이전트, "7.5는 8 기준 미달", 라운드별 개선과 테스트로 고정. `templates/critic-prompt.md`, `scorecard.md` 제공. `workflow-ship-change`는 스크린샷·changelog·테스트·own files만 stage·fast-forward push·실제 도메인 확인·크기 실측을 "완료의 정의"로 못 박고, "50MB 초과 업로드/force-push는 반드시 질문", "`git add -A` 금지", "남이 시작한 프로세스 kill 금지" 같은 가드레일을 나열한다. 이 skill은 저자의 게임 프로젝트(Supabase, Netlify, changelog 페이지)에 맞춰진 흔적이 강해 그대로 쓰기보다 *가드레일 목록의 모범*으로 보는 게 맞다. `workflow-threads-manager`는 여러 에이전트 스레드가 한 레포를 건드릴 때 merge/배포/changelog 누락을 감사하는 스크립트(`repo-status.sh`, `audit-changelog.py` 등)를 포함한다.

**no-ai-design-slop.** "슬롭은 색·폰트·그라디언트 같은 것이 아니라 *제품을 위해서가 아니라 반사적으로 한 선택*"이라고 정의하고, 선택이 의심스러운 조건(무관한 제품에 그대로 붙여도 되는가 등)을 제시한다. AI 작성 여부를 추측하지 말고 눈에 보이는 결과만 판단, 좁은 수정에서 사이트 전체 감사로 확대 금지, 공식 리뷰는 별도 `audit-ai-design-slop`(읽기 전용)로 분리. 지시문 설계 측면에서 "수동 품질 게이트"라는 모드 구분이 돋보인다.

**gsap** 같은 라이브러리 skill은 훨씬 단순하다: When to use, 핵심 API(tween/timeline/position parameter/ease/stagger), 흔한 함정(layout 속성 애니메이션 jank, ScrollTrigger 미작동, SPA 정리 누락 `gsap.context()`, 이미지 로드 후 `ScrollTrigger.refresh()`), 바로 쓰는 레시피. 이것이 저장소의 대다수 skill의 전형적 형태다.

## 설치·사용

별도 설치 명령은 없다(README의 Maintenance ideas에도 "install notes는 추후 추가" 상태). 방법은 복사/참조다.

```bash
git clone --depth 1 https://github.com/MengTo/Skills
# Claude Code: 필요한 skill만 개인 skills 디렉터리로 복사
cp -r Skills/agent-skills/web-design/gsap ~/.claude/skills/gsap
# 또는 CLAUDE.md 에서 경로 참조:  "UI 작업 전 agent-skills/ui/no-ai-design-slop/SKILL.md 를 따를 것"

# 데모 확인
python3 -m http.server 4173 -d Skills/agent-skills/web-design/gsap/demo
# 저장소 자체 검증(저자 워크플로)
node scripts/validate-skill-demos.mjs
```

Codex는 해당 SKILL.md를 로드, Cursor는 rules/컨텍스트에 폴더 지정(README). 155개를 통째로 넣으면 description이 컨텍스트를 점유하므로 **필요한 것만 선별**하는 편이 안전하다(권장 의견).

## 비교 대상

| 저장소 | 차이 |
|---|---|
| MengTo/Skills | 한 사람의 취향·작업 흐름을 담은 큐레이션. 프론트·디자인·게임·3D 편중, 데모(HTML)와 프롬프트 동봉 |
| [[agent-skills]] (일반 skill 모음) | 범용 개발 절차 중심. 이쪽은 시각적 데모와 스타일 시스템이 강점 |
| [[huashu-design]] | 프롬프트로 프로토타입·덱·모션 산출. 이쪽은 산출물 생성기가 아닌 "지시문 라이브러리" |
| [[agency-agents]] | 역할(페르소나) 프롬프트 모음. 이쪽은 절차·기본값·함정 중심의 task skill |
| [[diagram-design]] | 다이어그램 전용 skill. 이쪽은 웹 UI 전반 |

## 장단점·한계·성숙도

확인한 사실(GitHub API, 2026-10-01): 스타 6,515, fork 775, 열린 이슈 3(#1 한국어 카탈로그 claudecowork.co.kr 색인 안내, #2 "references/ missing", #5 "Good"), 라이선스 MIT, 주 언어 표기 HTML, 생성 2026-02-03, 마지막 push 2026-09-30, 최신 커밋 2026-10-01. 약 8개월 사이 155개가 쌓였으므로 업데이트 속도는 매우 빠르다.

장점: (1) 트리거·기본값·함정·수용 기준이 명시된 skill 작성의 좋은 견본. (2) 데모 HTML과 PROMPT.md로 결과를 눈으로 확인. (3) 데모 자동 검증 스크립트와 CSP 샌드박스 등 품질/보안 장치. (4) 워크플로 skill의 "측정 가능한 완료 정의".

한계: (1) 웹 디자인/게임/3D 편중으로 백엔드·RAG 업무와는 거리가 있다. (2) 일부 skill은 저자의 프로젝트(게임 changelog, Supabase/Netlify, X 계정 문체 `write-like-meng-on-x`, `build-vesperfall-review-assets`)에 종속적이라 portable 주장과 어긋난다. (3) 한 스타일 skill 수십 개는 대부분 Neuform에서 가져온 디자인을 기반으로 한 데모 중심이라 "절차 깊이"가 얕은 것도 있다(gsap은 문서 요약 수준). (4) README 수치 불일치, 설치 안내 부재. (5) README가 Aura Build, Lovable, 특정 모델 홍보와 얽혀 있다(관찰). (6) 개별 skill의 실제 산출 품질은 직접 실행해 검증하지 않았다(확인 못함).

## 보안·라이선스·운영 리스크

- MIT라 사내 수정·재배포 가능. 단 데모는 Neuform 생성 HTML과 Unsplash/외부 CDN 이미지 등을 포함하므로 **데모 자산의 별도 권리**는 확인되지 않았다(확인 못함). 사내에는 SKILL.md 본문만 가져오고 `demo/`는 제외하는 쪽이 안전.
- 스킬 문서는 곧 에이전트 지시문이므로 외부 skill을 그대로 로드하면 프롬프트 인젝션/권한 확대 경로가 된다. workflow-ship-change처럼 "push/publish는 사전 승인된 것으로 간주(standing authorization)"를 선언하는 skill은 사내 환경에서 의도치 않은 배포 권한을 주는 문구이므로 반드시 검토·수정.
- 데모 HTML은 외부 CDN 스크립트를 로드하므로 사내망에서 열 때 CSP/오프라인 번들 필요.
- 비밀 정보 금지가 문서상 규칙(`CLAUDE.md`)일 뿐 자동 검증(gitleaks 등)은 확인하지 못했다.
- 이슈 #1처럼 제3자 카탈로그가 자동 색인하는 정황이 있어 skill 내용이 외부에 복제·유통될 수 있다(opt-out 안내 이슈).

## 관련 노트

[[agent-skills]] · [[agency-agents]] · [[sanglard-agent-md]] · [[ai-engineering-from-scratch]] · [[gepa]] · [[huashu-design]] · [[diagram-design]] · [[claude-code-best-practice]]

## 출처

- https://github.com/MengTo/Skills (README 전문, CLAUDE.md, DEMOS.md 앞부분, agent-skills/workflow/README.md, `video-to-superprompt`, `stitched-full-page-capture`, `html-to-interaction-prompts`, `workflow-score-to-target`, `workflow-ship-change`, `no-ai-design-slop`, `gsap` SKILL.md, `game-development/README.md`, `scripts/sync-neuform-skill-demos.mjs`·`validate-skill-demos.mjs`, `gsap/demo/source.json`·`PROMPT.md` 직접 열람)
- GitHub API repos/MengTo/Skills, 이슈 목록 (2026-10-01 조회)
- 확인 못함: 개별 skill 실행 품질, 데모 자산(이미지·모델) 라이선스, 커밋 총수(shallow clone), 나머지 140여 개 SKILL.md의 세부 내용
