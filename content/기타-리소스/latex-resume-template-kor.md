---
title: latex_resume_template_kor
source: https://github.com/changh95/latex_resume_template_kor
type: repo
category: 기타-리소스
tags: [research, latex, resume, korean, template]
researched: 2026-10-01
---
# latex_resume_template_kor

> [!summary] 한줄요약
> 한국어 이력서(CV)와 "경력기술서"를 LaTeX로 쓰기 위한 MIT 템플릿. 이력서용 `resume.tex`(284줄)와 프로젝트 서술 중심의 경력기술서용 `work_experience.tex`(289줄) 두 파일이 본체다. 영문 개발자 이력서 템플릿 sb2nov/resume에 `kotex`를 얹고 한국식 경력기술서 구조를 추가한 얇은 파생물이며, 이력서 쪽은 사실상 영어 양식이고 한글 서술은 경력기술서 쪽에만 들어 있다. 이슈와 PR이 한 건도 없는 1인 유지 저장소다.

## 배경

한국 개발·연구 직군 채용에서는 이력서와 별도로 "경력기술서"를 요구하는 일이 많다. 이력서가 회사·학력·기술을 한두 장으로 요약하는 문서라면, 경력기술서는 프로젝트별로 무엇을 왜 만들었고 어떻게 했으며 어떤 성과를 냈고 어떤 기술을 썼는지 길게 쓴다. 이 저장소는 두 문서를 LaTeX 템플릿으로 나눠 제공한다. 설명문은 "[이력서/경력기술서] Beautiful CV/resume template for Koreans, in LaTeX", 토픽은 `latex`, `latex-template`, `resume`이다.

저장소를 직접 clone해 구조와 `.tex` 소스를 읽었고 GitHub API로 메타데이터를 확인했다. 저자는 changh95(Hyunggi Chang으로 소스 헤더에 표기)이고, 소스 주석에 "Original Author : Sourabh Bajaj, Adaptation : Hyunggi Chang"이라고 적혀 있다. 생성일은 2021-03-10, 마지막 푸시는 2026-07-22다. Star 569, Fork 71, 열린 이슈 0, 라이선스 MIT, 기본 브랜치 `main`이다. 커밋은 모두 15개다. 2021-03에 초기 구성과 이미지 추가, 2024-11-10에 "Enable Korean letter entries", 2026-01-29에 README의 OpenAI Prism 링크 추가, 2026-07-22에 사용법과 링크 개정이 있었다. `gh api`로 이슈(state=all)와 PR(state=all)을 조회했을 때 결과가 모두 비어 있었다. 즉 사용자 문의나 외부 기여가 없다.

## 상세 기능과 동작

### 1. 저장소 구조 (clone 확인)
```
latex_resume_template_kor/
  README.md
  LICENSE
  resume_img.png, work_experience_img.png   # README용 미리보기
  Curriculum_Vitae_Template/
    resume.tex  resume_template.pdf  LICENSE
  Work_Experiences_Template/
    work_experience.tex  Work_experiences.pdf  LICENSE
```
클래스 파일이나 폰트 번들이 없고 폴더마다 `.tex` 하나뿐이다. 각 파일은 독립적으로 컴파일된다. 샘플 PDF 두 개가 같이 들어 있으며(`resume_template.pdf` 약 102KB, `Work_experiences.pdf` 약 2.8MB), 이력서 샘플 PDF는 내가 열어 본 결과 2쪽짜리 영어 양식이다.

### 2. 기술적 뼈대
- 두 파일 모두 `\documentclass[letterpaper,11pt]{article}`이다. 한국에서 A4로 제출하려면 `a4paper`로 바꾸고 여백 보정(`\addtolength{\oddsidemargin}{-0.5in}` 등)을 다시 맞춰야 한다. 소스에서 직접 확인한 사실이다.
- 한글은 `\usepackage{kotex}`로 켠다(주석 "Enable Korean!", 경력기술서는 "한글 사용 가능!"). 그 밖의 패키지는 latexsym, fullpage, titlesec, marvosym, color, verbatim, enumitem, hyperref(`hidelinks`), fancyhdr, babel(english), tabularx, amsmath다.
- 섹션 제목은 `titlesec`으로 small caps 대문자와 가로줄을 넣는다. 레이아웃은 `\newcommand`로 정의한 매크로가 맡는다. 경력기술서 소스에는 "포맷이 마음에 들지 않으시다면 이 부분을 수정하세요!"라는 한글 주석이 있어 커스터마이징 지점을 알려 준다.
- 이 환경에는 LaTeX 엔진(pdflatex, xelatex, lualatex, tectonic, latexmk)이 없어 직접 컴파일하지 못했다. 컴파일 결과 확인은 저장소에 포함된 샘플 PDF에 의존했다.

### 3. 이력서 템플릿 (`resume.tex`)
- 섹션 구성: 헤더(이름, GitHub, SlideShare, 웹사이트, 이메일, 휴대폰) → Summary → Employment → Projects → Skills → Education → Research Experiences → Conference Talks → Papers → Community. 섹션 제목과 샘플 문구가 영어이고 소스 안에 한글이 한 글자도 없다(한글 글자 수 0 확인).
- 매크로: `\resumeItem`, `\resumeSummary`, `\resumeSubheading`(기관·지역·직위·기간 2행), `\resumeEmployment`, `\resumeProject`, `\resumeResearch`(연구실·지도교수), `\resumeTalk`, `\resumeSkills`, `\resumeCommunity`와 목록 시작/끝 매크로 쌍이 있다. 내용은 `[Company1]`, `Apr. 20XX - Present` 같은 대괄호 자리표시자로 채워져 있다.
- 특징: 프로젝트 항목에 "Major role / Key achievements 1.2.3." 틀이 있고, 학력·직장 예시 지역이 서울이다.
- 샘플 PDF 내용(직접 확인): 직장 항목은 회사명과 지역이 첫 줄, 직위와 기간(이탤릭)이 둘째 줄이다. 학력은 `[Degree name] [Course name] [Grade]` 형식이다. 쪽수는 2쪽이고 두 번째 쪽은 Research, Talks, Papers, Community만 담는다.

### 4. 경력기술서 템플릿 (`work_experience.tex`)
- 섹션이 `\section{\textbf{1. [초대형 프로젝트 이름]}}`처럼 번호 붙은 프로젝트 단위이며 5개 자리가 있다. 소스에 한글 1,063자가 들어 있다.
- 프로젝트마다 "소속: (주) [회사 이름]"과 기간, "주요 내용"(제품 목적·기술 스택·맡은 역할), "주요 성과"(1. 2. 3. 나열)를 쓴 뒤 하위 작업(1.1, 1.2, 1.3)과 기능(1.1.1, 1.1.2, 1.1.3)을 계층으로 내려간다. 각 기능은 "해당 기능은 [목적...]. [방법론...]. [결과와 임팩트...]." 문형에 "사용한 기술:" 줄로 끝난다. 구조는 목적, 방법, 임팩트, 기술 스택으로 이어지는 STAR 변형이다.
- 샘플 본문은 한국어 개조식("~하였음", "~을 목표로 둠")이고 예시 시나리오는 딥러닝 기반 동물 분류 학습(크롤러 기반 데이터 수집, Apache Spark·TFX·CUDA 분산 학습, Jenkins·GitHub Actions 모델 검증 자동화)이다. "90% 이상 정확도", "마일스톤 2달 단축", "96% 정확도" 같은 정량 문장은 템플릿 예시이지 실제 성과가 아니다. 소스에는 `96\%`처럼 `%`를 이스케이프한 정상 표기가 확인된다.
- 매크로는 `\resumeProject{...}{...}{...}`(3인자), `\resumeSubProject`(2인자)와 `...ListStart/End` 쌍이다.

### 5. 사용법 (README 원문 요약)
1. README는 먼저 "OpenAI Prism"으로 빠르게 만들어 보라며 온라인 링크를 둔다. 새 프로젝트를 만들고 템플릿 파일 내용을 복사해 붙여 넣은 뒤 Ctrl+S로 렌더링한다. 해당 서비스는 열어 보지 않았다.
2. 대안은 파일을 내려받아 TeX 에디터로 수정·렌더링하는 방법이며 TeX를 모르면 Overleaf를 권한다.
3. README에는 미리보기 이미지 두 개가 있고 "(예시는 곧 만들어서 올릴게요!)"라는 문장이 남아 있다.
4. 라이선스 문단: 모든 tex 파일은 sb2nov의 CV 템플릿을 수정해 만들었고 기존 MIT 라이선스를 유지한다. README 안의 파일 링크 일부는 옛 저장소 이름 `resume_template_kor`를 가리킨다.

### 6. 컴파일 방법과 한글 폰트
저장소 자체에는 컴파일 명령이나 폰트 설정 코드가 없다. 외부 자료로 정리하면 다음과 같다.
- kotex(ko.TeX 번들의 kotex-utf, CTAN 기준 3.0.0, 2022-06-22, LPPL 1.3c, 유지보수자 Kihwang Lee)의 README에 따르면 pdfLaTeX/LaTeX에서는 `\usepackage[utf]{kotex}`가 기본이고, XeLaTeX/LuaLaTeX에서는 옵션 없이 `kotex`를 불러오면 XeTeX-ko 또는 LuaTeX-ko를 자동으로 부른다. UTF-8 입력이 전제다. README의 샘플은 HCR Batang LVT, HCR Dotum LVT 폰트를 쓴다. 검색 결과 요약에 따르면 예제 문서에서 `\setmainhangulfont` 명령으로 한글 폰트를 지정한다(명령 이름은 직접 문서에서 확인하지 못함).
- 이 템플릿은 `kotex`만 불러오므로 엔진에 따라 기본 한글 폰트가 달라진다. 가장 안정적인 선택은 XeLaTeX 또는 LuaLaTeX와 시스템 한글 폰트 지정이다. Overleaf 공식 한국어 문서는 XeLaTeX와 `xeCJK`, `\setCJKmainfont{Noto Serif CJK KR}`, `\setCJKsansfont{Noto Sans CJK KR}`, `\setCJKmonofont{Noto Sans Mono CJK KR}` 조합을 안내하고, pdfLaTeX에서는 `CJKutf8` 패키지와 `\begin{CJK}{UTF8}{mj}`를 쓰라고 한다. 이 템플릿에 xeCJK 설정을 얹을 때 kotex와 중복될 수 있으므로 실제 컴파일로 확인이 필요하다. 아래는 검증하지 않은 제안이다.
```latex
% 제안(미검증): 프리앰블에서 kotex 다음에
\usepackage[a4paper]{geometry}   % 또는 documentclass를 a4paper로
\setmainhangulfont{Noto Serif CJK KR}   % XeLaTeX/LuaLaTeX, kotex 사용 시
```
- 빌드 명령 예: `xelatex resume.tex` 또는 `lualatex resume.tex`. 원본 sb2nov 저장소는 Docker로 `pdflatex sourabh_bajaj_resume.tex`를 실행하는 `build.sh`와 alpine 기반 Dockerfile(texlive, texlive-luatex, 추가 패키지)을 제공하지만, 한글 폰트는 별도로 필요하다. pdfLaTeX 경로에서는 TeX Live 쪽 한글 폰트가 있어야 한다는 점만 확인했고, 어떤 폰트가 기본으로 잡히는지는 컴파일하지 못해 확인하지 못했다.

### 7. 커스터마이징 포인트
- 용지: `letterpaper`를 `a4paper`로 바꾸고 여백 `\addtolength` 값을 조정.
- 섹션명 한글화: `\section{Summary}`를 `\section{요약}` 등으로 바꾸면 되지만 small caps(`\scshape`)는 한글에 적용되지 않으므로 겉보기는 평범한 글씨가 된다.
- 한국형 항목 추가: 사진, 병역, 자격증, 희망연봉 칸은 템플릿에 없다. `\resumeSubheading`을 복사해 새 매크로를 만들어 쓰는 방식이 자연스럽다.
- 직무별 버전: `\newif` 또는 `\ifdefined` 조건부 컴파일로 같은 소스에서 직무 맞춤 PDF를 뽑는 방식이 가능하다(제안이며 이 저장소에는 없음).

## 구체 수치·가격·요건
| 항목 | 값 | 출처 |
|---|---|---|
| 라이선스 | MIT (원본 sb2nov/resume도 MIT) | GitHub API |
| Star / Fork | 569 / 71 | GitHub API, 2026-10-01 |
| 커밋 수 / 이슈 / PR | 15 / 0 / 0 | git log, gh api |
| `resume.tex` | 284줄, 한글 0자 | clone |
| `work_experience.tex` | 289줄, 한글 약 1,063자 | clone |
| 용지 | letterpaper 11pt | 소스 |
| 원본 sb2nov/resume | Star 7,018, Fork 1,884, 마지막 푸시 2026-05-17, 템플릿 213줄 | GitHub API, clone |
요건은 TeX 배포판(TeX Live/MiKTeX) 또는 Overleaf와 한글 폰트다. 비용은 없다. Overleaf 무료 계정으로도 컴파일은 가능하다(무료 계정의 컴파일 시간 제한 등은 확인하지 않음).

## 비교 (유사 템플릿·도구)
- sb2nov/resume(원본, MIT): 한 쪽짜리 개발자 이력서, pdflatex 기반. 한글 지원 없음. 이 저장소가 `kotex`와 경력기술서를 얹은 파생이다.
- jakegut/resume: sb2nov 계열의 인기 파생(Star 2,821, MIT, 마지막 푸시 2024-08). 한글 지원은 확인하지 않았다.
- posquit0/Awesome-CV(Star 28,618, 라이선스 LPPL-1.3c, 마지막 푸시 2026-09-14): 독자 클래스 `awesome-cv.cls`를 쓰는 디자인 중심 템플릿. 컴파일은 `xelatex`가 기본이고 resume/cv/coverletter 예제를 제공한다. 한국어 전용 지원은 저장소에서 찾지 못했다(예제에 언어 항목으로 Korean이 등장할 뿐).
- Typst 계열: GitHub 검색에서 HyunP-dev/typst-korean-resume(Star 1, 라이선스 표기 없음, 2026-04)이 "국내에서 자주 사용되는 이력서 양식"이라는 설명으로 나왔다. 사용자가 적고 품질은 확인하지 못했다.
- 검색 범위 한계: "korean cv latex" 쿼리에서는 이 저장소만 검색되었다. 다른 한국어 LaTeX 이력서 템플릿은 GitHub 검색으로는 찾지 못했다(한글 쿼리는 API 오류로 실행되지 않음).
- LaTeX 밖의 방식(Markdown + Pandoc, JSON Resume, 워드/한글 파일)은 비교하지 않았다.

## 한계와 리스크
- 한글 조판: 저장소에 폰트 지정 코드가 없다. 엔진과 환경에 따라 한글이 다르게 나오거나 굵은 글씨(`\textbf`)에서 폰트가 없어 대체될 수 있다. 이 환경에서 컴파일하지 못했으므로 사용자의 TeX 환경에서 한 번 컴파일해 결과를 확인해야 한다.
- 용지 크기: letterpaper 기준이라 국내 A4 제출용으로 수정이 필요하다.
- 템플릿 위생: 자리표시자 오타가 있다. `resume.tex` 226행 `[Subjets]`, `work_experience.tex` 243행 `\section{\textbf{3. [프로젝트 이름}}`의 괄호 불일치, 이력서 Papers 항목의 닫힘 대괄호 누락. 샘플 PDF에서도 `[Other citation details`처럼 괄호가 닫히지 않은 모습이 확인된다.
- 한국어 현지화 범위: 이력서는 영어 섹션이고 한국 전통 이력서 항목(사진, 병역, 학점, 자격증)이 없다. 국내 대기업 공채 양식에는 맞지 않고 외국계·스타트업·개발 직군에 어울린다.
- ATS/파서: LaTeX PDF는 텍스트 추출은 대체로 되나 `tabular*` 기반 2열 배치가 자동 파서에서 순서가 섞일 수 있다. 제출 전 PDF 텍스트 복사 결과를 확인해야 한다.
- 유지보수: 기여자가 사실상 1명이고 커밋이 드물며 이슈·PR 대응 이력이 없다. 포크해서 쓰는 전제로 접근한다.
- 외부 서비스 의존과 개인정보: README 첫 안내가 OpenAI Prism이라는 온라인 서비스다. 이력서에는 이름·연락처·경력 같은 개인정보가 들어가므로, 외부 온라인 에디터에 올릴지 로컬 컴파일로 할지 결정해야 한다. 이 노트는 해당 서비스를 열지 않았고 데이터 처리 방침은 확인하지 못했다.
- 라이선스: 코드는 MIT이므로 수정·재배포가 자유롭다. 다만 sb2nov 저장소 README는 "Format is MIT but all the data is owned by Sourabh Bajaj"라고 적고 있어, 원본의 개인 이력 내용은 가져다 쓰면 안 된다. kotex는 LPPL 1.3c다.

## 관련 노트
- [[toss-ai-platform-engineer-serving]]
- [[github-donggyun112]]
- [[speechify-library]]
- [[jina-ocr-v1-threads]]

## 출처
- https://github.com/changh95/latex_resume_template_kor (clone, git log, GitHub API: repo/issues/pulls, 샘플 PDF 열람)
- https://github.com/sb2nov/resume (clone: README, build.sh, Dockerfile, 메타데이터)
- https://github.com/posquit0/Awesome-CV (clone: README, examples, 메타데이터)
- https://github.com/jakegut/resume (GitHub API 메타데이터)
- https://github.com/HyunP-dev/typst-korean-resume (GitHub 검색 결과 메타데이터)
- https://tug.ctan.org/language/korean/kotex-utf/README (WebFetch)
- https://ctan.org/pkg/kotex-utf (렌더)
- https://www.overleaf.com/learn/latex/Korean (WebFetch)
- https://ctan.org/pkg/kotex , https://ctan.org/pkg/ko.tex (404 Not Found)

## 확인하지 못한 항목
- 실제 컴파일 결과와 엔진별 한글 폰트 렌더링(이 환경에 TeX 엔진 없음), `Work_experiences.pdf` 본문 렌더(PDF 쪽수 변환 도구 없음), `\setmainhangulfont` 명령의 정확한 문서 근거.
- OpenAI Prism 서비스의 동작과 데이터 처리 방침.
- 다른 한국어 LaTeX 이력서 템플릿 존재 여부(GitHub 검색 한정), jakegut/resume의 한글 지원.
- Overleaf 무료 계정의 컴파일 제한.
