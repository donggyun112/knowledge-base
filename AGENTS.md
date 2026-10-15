# Research knowledge base

- 이 저장소가 앞으로의 AI 리서치 자료 관리 위치다. 공개 문서는 `content/`에서 직접 작성·수정한다.
- Obsidian은 최초 이전 자료의 출처다. 전체 Vault를 복사하거나 `content/`를 자동 내보내기로 교체하지 않는다.
- 연구 기록에는 출처, 실험 조건, 검증 범위, 정정과 미확인 사항을 남긴다. 합성 과제·회귀 테스트·실제 과제 성능을 구분한다.
- 원시 대화, 인증 정보, 개인 업무 구상, 실행 로그, 데이터셋과 체크포인트는 공개 자료에 넣지 않는다.
- 기존 연구 사본의 출처는 `docs/research-import-2026-10-16.json`, 읽기 시작점은 `content/메모리-연구/연구-안내.md`다.
- 문서를 변경하면 `npx quartz build`로 확인한다. 내보내기 도구를 변경했다면 `python3 -m unittest discover -s tests`도 실행한다.
