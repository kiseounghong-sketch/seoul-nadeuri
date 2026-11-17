# 서울 나들이 (학생용 현장체험학습 안내 웹앱)

- 주소: https://seoul-nadeuri.web.app (Firebase Hosting, 프로젝트 ID `seoul-nadeuri`)
- `main`에 올리면 `.github/workflows/firebase-hosting.yml`이 자동 배포한다(1분쯤). 브라우저로 배포하지 않는다.
- 앱은 `public/index.html` 한 파일(HTML+CSS+JS). 빌드 없음. `public/sw.js`가 오프라인 저장과 '안내 내용이 바뀌었어요' 알림을 맡는다.
- 내용은 스크립트 위쪽 데이터만 고친다: `DAYS`(일정), `RULES`(지킬 것), `PACK`(준비물), `MUSEUM`(박물관 유물), `WORK`(활동지 질문), `CHECKS`(선생님 인원 확인 시점).
- 화면: 지금 / 일정 / 지킬 것 / 준비물(11. 19. 09:00부터 활동지) / 비상, 그리고 `#museum`(견학 계획서), `#teacher`(선생님 화면).
- 미리 보기: 주소 끝에 `?now=2026-11-19T13:40` (한국 시간). 확인은 `python3 -m http.server --directory public` + playwright 화면 캡처로 한다.

## 꼭 지킬 것
- 저장소와 사이트가 모두 공개다. 학생 이름, 학교 이름, 선생님 전화번호, 코드를 파일·커밋 메시지·PR에 평문으로 쓰지 않는다.
- 조·방 명단은 `TEAMS_SEALED`(학생 코드), `TEACH_SEALED`(선생님 코드)에 암호화해 넣는다. 고칠 때는 `tools/roster.py`로 꺼내고 다시 넣는다. 코드는 사용자에게 받는다.
- 학생 답(계획서, 활동지, 메모)과 선생님 체크는 각자 휴대전화 localStorage(`nadeuri:` 접두어)에만 저장한다. 서버로 보내지 않는다.
- 디자인: 서울 버스 색(파랑 1일차, 초록 2일차, 노랑 꼭 지킬 시간, 빨강 비상), 제목 글꼴 Black Han Sans. 글씨와 단추는 작고 간결하게, 설명 문장은 최소로. 다크 모드와 320px 폭에서 깨지지 않게.
- 문구는 학생이 읽는 쉬운 해요체. 규정 근거는 충북교육청 자료와 전국 공통 법령만.
