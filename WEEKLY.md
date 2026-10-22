# 매주 목요일 카드뉴스 루틴

예약 작업이 매주 목요일 07:2x(KST)에 새 세션을 열고 이 문서를 따른다.
먼저 `STYLE.md`, `ANALYSIS.md`를 읽는다. 모든 시각은 한국 시간(KST, UTC+9).

## 0. 준비
- 이번 주 폴더: `weeks/YYYY-MM-DD` (오늘 목요일 날짜)
- 조사 기간: 지난주 금요일 ~ 어제(수요일)
- 폰트·렌더러는 저장소에 있음. `node render.js <slides.json> <out>`
- 이미지: Figma 파일 `lRtCcTvc26fzNugLuosbbQ` (팀 "리나의개인작업")에서 `generate_image`(gemini-3.1-flash-image, 1080×1350) → 응답의 image.url을 curl로 받아 `weeks/.../assets/`에 저장. 한 주 3~4장 이내.

## 1. 조사 (07:30~08:20, 사용자에게 알리지 않음)
- 청약홈 분양 공고 목록 `https://www.applyhome.co.kr/ai/aia/selectAPTLttotPblancListView.do`, 무순위·잔여세대 `selectAPTRemndrLttotPblancListView.do`
  → 다음 주(월~금) 접수 일정이 있는 단지 위주
- SH 주택분양 공고 `https://www.i-sh.co.kr/main/lay2/program/S1T294C296/www/brd/m_244/list.do?multi_itm_seq=1` (공고 PDF: `/main/com/file/innoFD.do?brdId=GS0401&seq=<seq>&fileTp=A&fileSeq=1`)
- 네이버 뉴스 부동산 섹션 `https://news.naver.com/breakingnews/section/101/260?date=YYYYMMDD` (날짜별 1페이지, 기사 원문은 요청 사이 3초 이상 쉬기)
- 보조금·대출 혜택: 보조금24(gov.kr), 기금e든든(nhuf.molit.go.kr), 주택금융공사(hf.go.kr)
- 지난주 게시물 성과: `python3 scripts/insights.py 5` → `weeks/.../insights.txt`에 저장

## 2. TOP 3 알림 (08:30까지)
- `STYLE.md`의 점수 기준(대상·행동·금액·타깃)으로 후보를 매겨 3개 선정 → `weeks/.../TOP3.md`
- 대화창에 TOP 3를 짧게 보여준다: 제목 한 줄, 왜 우리 독자에게 중요한지, 점수. 추천 1개 표시.
- 지난주 게시물 성과 3줄 요약도 같이.
- `send_later`로 이 세션에 3개 알림 예약:
  - **12:00** "선택 마감 확인" — 사용자가 고르지 않았으면 1순위로 진행한다고 알리고 제작 시작
  - **17:00** "시안 공유" — 시안을 아직 안 보여줬으면 보여줌
  - **19:00** "게시 시점" — 아래 5단계
- 턴을 마친다 (턴이 끝나면 푸시 알림이 감)

## 3. 제작 (사용자 선택 직후 또는 12:00 이후)
- 사실 확인: 청약·보조금은 공고문 원문으로. 원문 접근 실패 시 기사 2곳 이상 교차 확인 + 캡션에 "공고문 원문 꼭 확인" 한 줄.
- 6~8장, `STYLE.md` 디자인 규칙. 렌더 후 overview를 직접 보고 겹침·빈칸·오탈자 고치기.
- `caption.md` 작성 (존댓말·이모지, 결론 첫 줄 → 핵심 3~4줄 → 댓글 유도, `#재테크 #신혼부부` + 내용 맞춤 2개, 면책 문구 금지)
- 커밋·push (out/*.jpg 포함 — 인스타가 raw URL로 가져감)

## 4. 시안 공유 (17:00)
- `SendUserFile`로 overview + 낱장 + caption 내용을 보여주고 수정 요청 받기
- 수정 반영 → 다시 렌더·push → 다시 보여주기

## 5. 게시 (19:00)
- **사용자가 이번 주 시안을 명시적으로 승인한 경우에만** `python3 scripts/publish.py weeks/YYYY-MM-DD --publish`
- 승인이 없으면 게시하지 않고 "승인해 주시면 바로 올릴게요"라고 알림
- 게시 후 permalink를 알려주고 `weeks/.../published.txt`에 기록, 커밋·push

## 토큰 관리
- 매주 `python3 scripts/refresh_token.py`로 남은 기간 확인. 10일 이하이면 TOP 3 알림에 "인스타 토큰 재발급 필요" 경고 추가.
