# 콘텐츠·운영 문서 검수 기록 — 2026-09-22

## 범위와 판정 기준

기존 문제 은행과 운영 문서를 공개된 배포 노트에 대조한 **패치 영향 검수**와
위키 검색 수집본에 근거한 **문항 명확성·예외 조건 검수**다.
전체 문항의 모든 보기·수치를 최신 게임 클라이언트로 검증한 전수 실측은 아니다.
구조 테스트, 검토일, 링크 존재만으로 사실 확인 완료로 판단하지 않는다.

- 출발점: `ffa276c`, 458문항. 1차: 기존 14문항 수정 + 6문항 추가 = 464문항.
- 2차: `4f7cf30` 이후 기존 14문항 추가 수정. 총 문항 수는 464개 유지.
- 모드: 공통 451 / PvP 11 / PvE 2. 공통 포함 PvP 462 / PvE 453.
- 근거를 기록한 문항: 34개(1차 20 + 2차 14). 그 외 430개를 확인 완료로 표시하지 않는다.
- `volatile`: 202개(2차에서 수치·규칙 문항 5개 추가). 이 표시는 **출제 제외가 아니다**.
  남은 검토 항목도 현재 풀에서 출제된다.
- `reviewed_at`은 검토를 수행한 날짜다. 원전 최신성·전체 명제의 실측을 보장하지 않는다.

## 배포와 예고 구분

| 대상 | 확인 결과 | 근거 |
|---|---|---|
| 1.1.0.0 | 시즌·영구 프로필, 보험·연동의 기준 재확인 | [공식 배포 노트](https://telegra.ph/Patch-1100-08-03) |
| 1.1.5.0 | 9월 8일 설치 완료. 노트 작성일은 9월 7일 | [노트](https://telegra.ph/Patch-1150-09-07-2), [설치 완료 공지](https://t.me/escapefromtarkovEN/6823) |
| 1.1.5.1 | 9월 15일 설치 완료. 리그는 더 이상 출시 예정 기능이 아님 | [노트](https://telegra.ph/Patch-1151-09-15-2), [설치 완료 공지](https://t.me/escapefromtarkovEN/6836) |
| 9월 18일 본편 기술 업데이트 | Arena 보상 연계 및 Uley 슬롯 표시 수정 공지 확인. 퀴즈 정답을 바꾸는 근거로 쓰지 않음 | [공식 공지 모음](https://t.me/s/escapefromtarkovEN) |
| Arena 0.6.0 / Exfil Brothers | Arena 전용 변경과 본편 출시 예고를 본편 적용 완료로 섞지 않음 | [공식 공지 모음](https://t.me/s/escapefromtarkovEN) |

## 수정·추가 문항

정확한 URL은 각 문항의 `sources`에도 기록했다. 패치 문항은 지문에 버전을 명시했다.

| 문항 | 수정 이유·결과 | 근거 종류 |
|---|---|---|
| Q44 | 열쇠만 유일하다는 오답 전제 제거 | 1.1.5.0 |
| Q80 | 모든 플레이어 초기화라는 과도한 범위 수정 | 1.1.0 |
| Q138·211·244·273 | 구 라이트하우스 배치·AI 규칙과 거치 화기 설명 정리 | 1.1.5.0, [공식 개편 설명](https://t.me/escapefromtarkovEN/6807), Interchange 위키 |
| Q130·164·242 | 발전소 위치, 저격 퀘스트 조건, 레이더에게 선공하지 않으면 안전하다는 단정 수정 | 아래 위키 검색본 |
| Q339 | 할로윈 한정이라는 현재형 설명을 공식 패치 대상 문항으로 교체 | 1.1.5.0 |
| Q403 | 백분율 비교 기준을 뒤집을 때 생긴 수학적 오류 제거 | Ballistics 위키 검색본 |
| Q406 | 구 위키 설명을 전체 현행 장비에 일반화하지 않고 공식 수정 대상만 질문 | 1.1.0 |
| Q450 | 문서 사용 범위의 예외 보완 | [공식 문서 안내](https://t.me/escapefromtarkovEN/6795) |
| Q457 | 연동 대상 명시, 의상 예외 보완 | 1.1.0 |
| Q459~461 | 시즌 리그 문항 3개 추가, PvP 풀만 사용 | 1.1.5.1 |
| Q462~464 | 입장·퀘스트·장비 변경 문항 3개 추가, 공통 풀 사용 | 1.1.5.0 |

위키 원문 직접 열기는 접근 오류가 발생했다. 아래 내용은 검색으로 제공된 본문을 확인했고,
검색 시스템의 수집 시점은 약 2~3개월 전이었다. 특히 Rogues의 옛 주둔지·적대 규칙은 최신
공식 발표와 충돌하여 사용하지 않았다. 최신 원문을 열었다고 보고하지 않는다.

- [Interchange](https://escapefromtarkov.fandom.com/wiki/Interchange): Q130·273.
- [A Shooter Born in Heaven](https://escapefromtarkov.fandom.com/wiki/A_Shooter_Born_in_Heaven): Q164. 세부 맵·횟수는 이번 문항에 넣지 않았다.
- [Scavs](https://escapefromtarkov.fandom.com/wiki/Scavs): Q242.
- [Ballistics](https://escapefromtarkov.fandom.com/wiki/Ballistics): Q403. 도탄 설명 전체의 최신성 보증으로 사용하지 않았다.

## 2차 수정 — 복수 정답과 예외 조건

아래 14문항은 위키 검색 수집본과 문항의 논리 구조를 대조했다. 최신 게임 실측이나
9월 패치 후 수치 재검증으로 표시하지 않는다. 특히 숫자 정답의 최신성은 계속 확인해야 한다.

| 문항 | 문제와 수정 | 근거 |
|---|---|---|
| Q29 | 근거 없는 팔·다리 추가 슬롯 설명을 실제 헬멧 귀 보호 부품으로 교체 | [FAST Side Armor](https://escapefromtarkov.fandom.com/wiki/Ops-Core_FAST_Side_Armor) |
| Q41 | 모든 Scav 처치가 평판 하락이라는 단정을 비배신자 선공 살해로 한정 | [Scavs](https://escapefromtarkov.fandom.com/wiki/Scavs) |
| Q61 | 방탄 아이웨어도 눈을 보호하므로, 헬멧 장착 바이저를 묻도록 구체화 | [FAST face shield](https://escapefromtarkov.fandom.com/wiki/Ops-Core_FAST_multi-hit_ballistic_face_shield), [Eyewear](https://escapefromtarkov.fandom.com/wiki/Eyewear) |
| Q94 | 독스도 열쇠 보관 가능. 키툴의 외부 1x1 크기를 정답 구분 조건으로 명시 | [Key tool](https://escapefromtarkov.fandom.com/wiki/Key_tool), [Documents case](https://escapefromtarkov.fandom.com/wiki/Documents_case) |
| Q118 | FIR 설명에 은신처 제작품·퀘스트 보상과 반입품·Run Through 예외 반영 | [Found in raid](https://escapefromtarkov.fandom.com/wiki/Found_in_raid) |
| Q156·157 | 분산 피해는 팔·다리·복부로 한정. 머리·가슴 0 HP의 출혈 예외를 설명하고 총탄 직접 피해로 즉사 지문 한정 | [How to Play Guide](https://escapefromtarkov.fandom.com/wiki/How_to_Play_Guide_for_Escape_from_Tarkov) |
| Q220 | 질문과 무관한 ‘획득 가능한 것 중 최대’ 단정을 빼고 내부 용량 설명 | [Kappa](https://escapefromtarkov.fandom.com/wiki/Secure_container_Kappa) |
| Q314 | ‘모든 맵’ 대신 ‘퀘스트 지정 맵’. 최신 카파 필수 조건이라는 단정 제거 | [The Guide](https://escapefromtarkov.fandom.com/wiki/The_Guide) |
| Q389·390 | 95% 초과는 93% 초과에, 1% 이하는 5% 이하에 포함됨. 중첩 범위 대신 경계·상한값을 질문 | [Weapon malfunctions](https://escapefromtarkov.fandom.com/wiki/Weapon_malfunctions) |
| Q415 | 회복량과 방사능 제거 차이가 모두 참일 수 있었음. 1회 최대 회복량만 비교 | [Salewa](https://escapefromtarkov.fandom.com/wiki/Salewa_first_aid_kit), [AFAK](https://escapefromtarkov.fandom.com/wiki/AFAK_tactical_individual_first_aid_kit) |
| Q424 | 수술 후 최대 HP 페널티 제거와 현재 HP 완전 회복을 혼동하지 않게 구체화 | [Surgery](https://escapefromtarkov.fandom.com/wiki/Surgery) |
| Q438 | 레벨과 시간대를 경쟁 보기로 쓰지 않고 숙련자 매칭 기준만 질문. 파티 최고 레벨 기준 보완 | [Ground Zero](https://escapefromtarkov.fandom.com/wiki/Ground_Zero) |

Q389·390·415·424·438에는 `volatile`과 최신성 한계 메모를 추가했다.
회귀 테스트 3개는 위 수정 범위·선택지 형식·출처 기록의 유지 여부를 검사하며 사실성 자동 검증은 아니다.

## 운영 문서와 실제 코드

- 관전 로그: `admin_log.py`는 답변을 매번 기록하되 기본 5문제마다 Discord 편집 요청을 보낸다.
  README 양쪽의 매 문제 즉시 갱신 설명을 수정했다.
- 대시보드: `dashboard_manager.py`의 저장 ID → 고정 → 최근 기록 탐색 순서와 고정 실패 처리를 문서화했다.
- 랭킹 초기화: `ResetConfirmView`는 DB 기록을 삭제하지만 진행 중 세션은 종료하지 않는다.
  나중에 완주 결과가 다시 저장될 수 있다는 운영 주의사항을 추가했다.
- CI: `.github/workflows/ci.yml`의 `main` push / PR 트리거를 정확히 문서화했다.
- 명령어 14개, 아이콘 21종, 30문제·1,380점 구성은 변경하지 않았다.
- 운영 DB·스키마·`.env`·실행 중 봇에는 변경을 가하지 않는다.

## 남은 팩트체크 — 완료로 간주하지 않는 항목

1. Q410(PvE 업적 표시 버그), Q429(Intellect 미작동): 최신 버그 상태의 근거 확보 필요.
2. Q29·157의 기존 설명 오류는 2차에서 수정했다. 근거가 검색 수집본이라는 한계는 남으며,
   최신 클라이언트 실측 완료로 간주하지 않는다.
3. Q151·163·209·225~226·269·310~324·367·369 등 해금·상인·퀘스트 조건:
   1.1.0 재편과 Lighthouse 퀘스트 개편 이후의 게임 화면 또는 최신 자료 대조 필요.
   Q164의 세부 조건도 여기에 포함한다.
   Q314의 ‘모든 맵’ 표현은 고쳤지만 최신 대상 맵·선행 조건까지 확인한 것은 아니다.
4. 탄약 수치, 의료·하이드아웃·스킬 수치, 맵 인원·시간 등 나머지 변동형 항목:
   `python check_questions.py --volatile`의 목록을 기준으로 계속 검증해야 한다.
5. Q458(FAMAS G2): 공개 사실과 정식 출시·제원을 구분. 검토한 배포 노트만으로 출시 확정하지 않는다.
6. 공개 문서로 확인할 수 없는 실제 Discord 설치·아이콘·응시 UI는 별도 운영 확인이 필요하다.

## 검증 방법

`check_questions.py`는 형식·모드별 수량·근거 메타데이터를 검사한다. 추가한 회귀 테스트는
이번 수정 범위가 되돌아가지 않는지, 시즌 리그가 PvE 풀에 섞이지 않는지 검사한다.
이 검사는 웹 문서의 사실성을 자동 판정하지 않는다.

로컬 검증 결과:

- 1차 unittest 135개 통과. 2차는 회귀 테스트 3개 추가 후 138개 통과
  (파일별 실행, 마지막 변경이 있는 테스트 파일은 재실행).
- Ruff·Python 컴파일·464문항 형식 검사 통과.
- PvP/PvE 각각 300회 추출에서 난이도 수량·ID 중복·모드 격리 검사 통과.
- 임시 DB의 8,500명·25,500회 응시, 동시 랭킹 조회 200회,
  동시 세션 250개와 초과 시작 거절 검사 통과.

합성 부하는 Discord 실제 서버의 8,500명 동시 접속 검증이 아니다.
실게임 정답 검증과 소프트웨어 검증 결과는 구분한다.
