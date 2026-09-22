# 콘텐츠·운영 문서 검수 기록 — 2026-09-22~23

## 범위와 판정 기준

기존 문제 은행과 운영 문서를 공개된 배포 노트에 대조한 **패치 영향 검수**와
위키 검색 수집본에 근거한 **문항 명확성·예외 조건 검수**다.
전체 문항의 모든 보기·수치를 최신 게임 클라이언트로 검증한 전수 실측은 아니다.
구조 테스트, 검토일, 링크 존재만으로 사실 확인 완료로 판단하지 않는다.

- 출발점: `ffa276c`, 458문항. 1차: 기존 14문항 수정 + 6문항 추가 = 464문항.
- 2차: `4f7cf30` 이후 기존 14문항 추가 수정. 총 문항 수는 464개 유지.
- 3차: `6227926` 이후 19문항 대조. 16문항의 표현·조건 수정, 3문항은 내용 유지·근거 추가.
- 4차: `1520dcd` 이후 하이드아웃 19문항 대조. 16문항의 범위·예외 수정,
  3문항은 문제·보기·해설 유지. 검토 메모의 근거 수준도 정정했다.
- 5차: `dae3d02` 이후 스킬 31문항과 업적 1문항 대조. 18문항의 표현·조건을 수정하고
  14문항은 문제·보기·해설 유지 후 근거·변동형 메모를 기록했다.
- 6차: `6ea24f9` 이후 의료·식량 28문항 대조. 24문항의 효과·범위·기본값 설명을 수정하고
  4문항(Q232·382·383·388)은 문제·보기·해설 유지 후 근거를 기록했다.
- 7차: `5bdb86d` 이후 남은 의료·식량 15문항 대조. 12문항의 범위·효과 설명을 보완하고
  3문항(Q33·115·268)은 문제·보기·해설을 유지했다.
- 8차: `f62cae0` 이후 장비 27문항 대조. 20문항의 계산·조건·설명을 수정하고
  7문항은 문제·보기·해설을 유지했다. Q289는 정답 인덱스도 0에서 2로 수정했다.
- 모드(23차 기준): 공통 449 / PvP 13 / PvE 2. 공통 포함 PvP 462 / PvE 451.
- 9차: `65952d3` 이후 무기 14문항 대조. 11문항의 조건·설명을 보완하고
  3문항(Q15·21·393)은 문제·보기·해설을 유지한 채 근거를 추가했다.
- 10차: `d2a6e2c` 이후 구경·분류·공개 관련 무기 26문항 대조. 13문항을 보완하고
  13문항은 문제·보기·해설을 유지한 채 근거를 추가했다.
- 11차: `e9e7063` 이후 남은 무기 8문항의 모호한 조건·일반화와 근거를 보완했다.
- 12차: `c822fa3` 이후 탄약 19문항 대조. 17문항의 조건·설명을 보완하고
  2문항(Q238·407)은 문제·보기·해설 유지 후 근거와 변동형 메모를 기록했다.
- 13차: `4941c8f` 이후 탄약 수치 25문항의 보기·해설까지 대조하고 비교 범위·기본값 설명을 보완했다.
- 14차: `88a380e` 이후 기본 시스템·시즌 22문항 대조. 15문항의 내용을 보완하고
  7문항은 문제·보기·해설을 유지한 채 근거를 기록했다.
- 15차: `8ae586f` 이후 상인·기초 퀘스트 35문항 대조. 16문항의 내용을 보완하고
  19문항은 문제·보기·해설을 유지한 채 근거를 기록했다.
- 16차: `977725a` 이후 퀘스트 11문항 대조. 8문항의 내용을 수정하고
  3문항(Q316·319·320)은 문제·보기·해설을 유지한 채 근거·한계를 기록했다.
- 17차: `9a494f0` 이후 이벤트·해금 8문항(Q360~363·367·369·371~372)을 보완했다.
  Blackout 당시 기록과 현재 상태, 상인 해금과 판매 LL, Collector의 대상 상인을 구분했다.
- 18차: `1ce0a06` 이후 보스·AI 10문항 및 관련 맵 2문항 대조. 9문항을 보완하고,
  3문항(Q135·136·436)은 문제·보기·해설을 유지한 채 근거·한계를 기록했다.
- 19차: `ada7d66` 이후 남은 보스·AI 15문항 대조. 10문항의 내용을 보완하고,
  5문항(Q132·165·214·215·216)은 문제·보기·해설을 유지한 채 근거를 기록했다.
- 20차: `3bbdbe6` 이후 하이드아웃 9문항·기본 시스템 14문항 대조. 13문항의 내용을
  보완하고 10문항은 문제·보기·해설을 유지한 채 근거·검토 범위를 기록했다.
- 21차: `690b271` 이후 스토리 42문항 전체 대조. 28문항의 내용을 보완하고
  14문항은 문제·보기·해설을 유지한 채 근거·한계를 기록했다.
- 22차: `b094743` 이후 맵 관련 20문항 대조. 17문항의 내용을 보완하고
  3문항(Q82·84·131)은 문제·보기·해설을 유지한 채 근거를 기록했다.
- 23차(9월 23일): `19d4669` 이후 남은 맵 시간·인원 6문항 대조. 비교 범위를 수정하고
  Q441·446을 공통에서 PvP 전용으로 변경했다. 충돌하는 세부 인원 값은 확정하지 않았다.
- 근거를 기록한 문항: 460개(1차 20 + 2차 14 + 3차 19 + 4차 19 + 5차 32 + 6차 28 + 7차 15 + 8차 27 + 9차 14 + 10차 26 + 11차 8 + 12차 19 + 13차 25 + 14차 22 + 15차 35 + 16차 11 + 17차 8 + 18차 12 + 19차 15 + 20차 23 + 21차 42 + 22차 20 + 23차 6).
  그 외 4개를 확인 완료로 표시하지 않는다. 근거가 있는 문항도 충돌·미확인 사항이 남는다.
- `volatile`: 290개(2차 5개, 4차 2개, 5차 17개, 6차 9개, 7차 1개, 8차 8개, 9차 3개, 11차 1개, 12차 1개, 14차 3개, 15차 4개, 16차 1개, 18차 9개, 19차 9개, 20차 14개, 21차 2개, 22차 4개 추가). 이 표시는 **출제 제외가 아니다**.
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

## 3차 수정 — 상인·퀘스트·시즌 규칙

| 문항 | 판정·처리 | 근거 |
|---|---|---|
| Q71 | 누적 거래액 제거는 배포 노트와 일치. 부연 설명의 초기 레벨 일괄 하향 단정은 ‘재조정’으로 수정 | [1.1.0 배포 노트](https://telegra.ph/Patch-1100-08-03) |
| Q149 | 고장 확인과 해제 조작을 혼동. 순서를 분리하고 엘리트의 점검 생략 예외 명시 | [Weapon malfunctions](https://escapefromtarkov.fandom.com/wiki/Weapon_malfunctions), [Controls](https://escapefromtarkov.fandom.com/wiki/Controls) |
| Q151 | 메뉴 열람과 판매글 등록 구분. 기본 규칙·PMC 기준으로 한정 | [Trading](https://escapefromtarkov.fandom.com/wiki/Trading) |
| Q152 | 입장 레벨 상한과 매칭 구간을 혼동할 수 있는 보기 수정, 파티 최고 레벨 기준 보완 | [Ground Zero](https://escapefromtarkov.fandom.com/wiki/Ground_Zero) |
| Q153 | 카파 획득 경로와 업적 교체를 구분, 출시 예정형 설명 정리 | [Kappa](https://escapefromtarkov.fandom.com/wiki/Secure_container_Kappa), 1.1.0 |
| Q155 | DSP 단순 소지가 아닌 인코딩·장착 상태가 필요함을 보완 | [DSP transmitter](https://escapefromtarkov.fandom.com/wiki/Digital_secure_DSP_radio_transmitter) |
| Q163 | Setup의 복장 외 지정 MP 계열 산탄총 조건 누락 보완 | [Setup](https://escapefromtarkov.fandom.com/wiki/Setup) |
| Q312 | 무기를 ‘보여주기’가 아닌 사양 충족 후 제출로 수정 | [Gunsmith - Part 1](https://escapefromtarkov.fandom.com/wiki/Gunsmith_-_Part_1) |
| Q318 | FIR로 찾아야 하는 과제가 아니라 네 장소에 나이프 설치. 구매품 사용 가능 | [Small Business - Part 3](https://escapefromtarkov.fandom.com/wiki/Small_Business_-_Part_3) |
| Q322 | 위키 분류 표식과 최신 해금 조건 구분. 예고 내용의 적용 완료 단정 제거 | [Collector](https://escapefromtarkov.fandom.com/wiki/Collector) |
| Q324 | 문을 직접 열 때 필요한 열쇠와 퀘스트 제출물을 구분 | [Pharmacist](https://escapefromtarkov.fandom.com/wiki/Pharmacist) |
| Q365·366 | 개인 모디파이어 규칙을 모든 미래 시즌이 아닌 1.1.0 Kord Breach로 한정 | 1.1.0, [포인트 설명 공지](https://t.me/s/escapefromtarkovEN?before=6662) |
| Q368 | 업적 신규 획득 중단을 적용 완료 시제로 수정 | 1.1.0 |
| Q370 | 일부 구역·일부 재료의 변경을 명시하고, FIR 완화의 PvP Zone·PvE Zone 범위를 명시 | 1.1.0 |
| Q374 | 80줄을 총 창고 크기로 오해하게 하는 지문을 ‘구매 추가 줄 수’로 정정 | [Expansion Hub 공지](https://t.me/escapefromtarkovEN/6683), [본문 수록](https://t.me/s/escapefromtarkovEN?before=6701) |
| Q364·373·375 | 보험·QBZ 탄종·독립 프로필 설명은 배포 노트와 일치. 내용은 유지하고 근거만 추가 | 1.1.0 |

위키 대조 항목에는 여전히 검색 수집본의 최신성 한계가 있다. 최신 표를 확보하려고
공개 Tarkov.dev GraphQL API를 읽기 전용 조회했으나 서버가 `GraphQL server unavailable`을
반환해 데이터는 확보하지 못했다. API를 통해 현행 수치를 확인했다고 간주하지 않는다.

대조했지만 이번에 확정하지 못한 항목:

- Q225·226: 위키 검색본은 구 매입 배율과 벼룩시장 3% 수수료를 함께 싣고 있다.
  공식 1.1.0은 매입 가격 평균 20% 감소와 수수료 5%를 명시한다. 개별 상인 배율이
  일률적으로 0.8배가 되었다고 추정할 수는 없으므로 최신 배율·순위는 확인 보류다.
- Q367·369: [컬렉터 예고](https://t.me/escapefromtarkovEN/6680)와
  [T-45M1 예고](https://t.me/escapefromtarkovEN/6687)는 배포 전 설명이다.
  최종 1.1.0 노트에는 해당 개별 요구·판매 조건이 없고, Collector 위키 검색본은
  구 Kappa Path 보상을 기재한다. 출시 후 상세 조건 확정 근거로 사용하지 않는다.
  이 두 문항은 **아직 미수정·출제 가능 상태**이며 검증 완료 목록에 넣지 않았다.
- Q410·429: 검색본의 버그 설명은 확인했지만 현재도 재현되는지는 확인하지 못했다.
  특히 Q429의 일반 레벨 효과가 ‘정상 작동’한다는 부연까지 검증된 것으로 취급하지 않는다.
  **5차 후속 처리:** 두 문항을 과거 위키 기록 질문으로 한정하고 정상 작동 단정을 제거했다.
- Q315: SR-25·Hybrid 46·PM II 1-8x24·PMC 10명은 검색본과 일치하지만
  1.1.0 이후의 현행 클라이언트 대조가 아니므로 최신 검증 완료로 올리지 않았다.
- Q323: [공식 공지](https://t.me/s/escapefromtarkovEN?before=6701)는 Blackout 기간
  New Beginning 조건의 일시 조정을 명시한다. 평상시 수량과 이벤트 수량 구분이 필요하다.

## 4차 수정 — 하이드아웃·제작 조건

공식 1.1.0 노트와 약 2~3개월 전 위키 검색 수집본을 대조했다. 위키 최신 원문과
현재 게임 화면을 확인한 것은 아니다. 특히 Q417~421의 기존 메모에 있던
‘배포 후 현행 문서 재확인’ 표현은 이번에 확보한 근거 수준으로 정정했다.

| 문항 | 판정·처리 | 근거 |
|---|---|---|
| Q7 | 계정 공용 창고로 읽히지 않도록 프로필 단위 설명 | [독립 시즌 프로필](https://telegra.ph/Patch-1100-08-03), [Hideout](https://escapefromtarkov.fandom.com/wiki/Hideout) |
| Q47 | 두 보기 모두 회복 효과가 있어 의료품 제작으로 구분 | [Health system](https://escapefromtarkov.fandom.com/wiki/Health_system), [Salewa](https://escapefromtarkov.fandom.com/wiki/Salewa_first_aid_kit) |
| Q67 | 보상 증가의 종류 명시 | [Shortage 보상 표](https://escapefromtarkov.fandom.com/wiki/Shortage), [Scavs](https://escapefromtarkov.fandom.com/wiki/Scavs) |
| Q72·380 | 대상 스킬 그룹·필터·기본값과 개인 보정 구분 | [Character skills](https://escapefromtarkov.fandom.com/wiki/Character_skills), [Hideout Management](https://escapefromtarkov.fandom.com/wiki/Hideout_Management) |
| Q104 | 생산 레벨·필터 누락 보완 | [정제수](https://escapefromtarkov.fandom.com/wiki/Canister_with_purified_water) |
| Q110·160 | GPU의 용도·최대 슬롯을 묻는 시설 레벨 구체화 | Hideout |
| Q162 | 재료 조합을 부즈 제너레이터 제작으로 한정 | [Moonshine](https://escapefromtarkov.fandom.com/wiki/Bottle_of_Fierce_Hatchling_moonshine) |
| Q337 | 최소 에너지·수분 값만 비교하도록 보기 정리 | Hideout |
| Q338 | Combat 대상 명시. 구 위키의 직접 처치 요구는 공식 수정 노트를 우선 | 1.1.0, Hideout |
| Q381 | 청소 완화 전 누적값이라는 전제 추가 | Character skills |
| Q417 | 일반 제작과 지속 전력 요구 작업을 구분 | Hideout, [Getting Acquainted](https://escapefromtarkov.fandom.com/wiki/Getting_Acquainted) |
| Q418·419 | 보기 내 비교·보정 없는 기준값으로 한정 | Hideout, Hideout Management |
| Q454 | 작업대 선행 조건 해제의 범위 명시 | 1.1.0 |
| Q141·420·421 | 문제·보기·해설은 유지하고 근거 기록. Q420·421 메모의 최신성 단정 정정 | Moonshine, Hideout, Hideout Management |

Q380·381에는 변동 수치 재검토를 위한 `volatile`을 추가했다. Q160·337·380·381·417·419·420의
숫자가 검색본과 일치하더라도 9월 이후 게임 실측 검증 완료로 간주하지 않는다.
이번 검수에서는 문제 수·모드·난이도·정답 인덱스·운영 코드를 변경하지 않았다.

## 5차 수정 — 스킬 분류·효과·버그 기록

스킬 카테고리 32문항 중 2차에서 검토한 Q424를 제외한 31문항과 업적 Q410을 대조했다.
이번 근거도 약 2~3개월 전 위키 검색 수집본이다. 원문 직접 열기는 접근 제한이 있으며,
공식 사이트·배포 노트 대상 검색에서도 Q410·429의 최신 버그 상태를 확정할 근거를 확보하지 못했다.
검색 결과가 없다는 사실은 버그가 고쳐졌거나 남아 있다는 증거가 아니다.

| 문항 | 판정·처리 | 근거 |
|---|---|---|
| Q66·422 | 무게 자체 감소와 소지 한계, 개인 보정과 기본값 구분 | [Strength](https://escapefromtarkov.fandom.com/wiki/Strength) |
| Q161 | Metabolism에 Health의 소비율 감소 효과가 섞인 설명 수정 | [Metabolism](https://escapefromtarkov.fandom.com/wiki/Metabolism), [Health](https://escapefromtarkov.fandom.com/wiki/Health) |
| Q202·272·293 | 미구현 목록을 현재 사용 가능·출시 확정으로 읽지 않도록 한정 | [Character skills](https://escapefromtarkov.fandom.com/wiki/Character_skills) |
| Q331 | 삭제된 버전을 명시한 과거 변경 문항으로 구체화 | [Recoil Control](https://escapefromtarkov.fandom.com/wiki/Recoil_Control) |
| Q378·379·431 | 추가 보정과 스킬 기본값 구분 | Character skills, [Endurance](https://escapefromtarkov.fandom.com/wiki/Endurance) |
| Q394 | 검사 생략과 고장 해제 조작 생략 구분 | [Troubleshooting](https://escapefromtarkov.fandom.com/wiki/Troubleshooting) |
| Q410·429 | **과거 위키의 버그 기록**을 묻도록 변경. 현재 재현·보상·일반 효과 정상 작동을 단정하지 않음 | [Achievements](https://escapefromtarkov.fandom.com/wiki/Achievements), [Intellect](https://escapefromtarkov.fandom.com/wiki/Intellect) |
| Q430 | 제작 시간 감소에 비트코인 팜 예외 보완 | [Crafting](https://escapefromtarkov.fandom.com/wiki/Crafting) |
| Q432 | 탄창 내 탄 삽입·제거와 총기 재장전 구분. 속도·시간 부호가 혼재한 부연 수치 삭제 | [Mag Drills](https://escapefromtarkov.fandom.com/wiki/Mag_Drills) |
| Q433 | 레벨별 감소량과 엘리트 도달 시 누적값 구분 | [Stress Resistance](https://escapefromtarkov.fandom.com/wiki/Stress_Resistance) |
| Q434·435 | 면역 대상과 스태미나·부상에 따른 흔들림의 범위 구체화 | [Immunity](https://escapefromtarkov.fandom.com/wiki/Immunity), [Aim Drills](https://escapefromtarkov.fandom.com/wiki/Aim_Drills) |
| Q203~206·240·241·332·376·377 | 내용은 검색본과 일치, 근거 기록 | Character skills, [Perception](https://escapefromtarkov.fandom.com/wiki/Perception), [Weapon Maintenance](https://escapefromtarkov.fandom.com/wiki/Weapon_Maintenance) |
| Q423·425~428 | 내용은 검색본과 일치, 근거 기록 | [Vitality](https://escapefromtarkov.fandom.com/wiki/Vitality), [Light Vests](https://escapefromtarkov.fandom.com/wiki/Light_Vests), [Heavy Vests](https://escapefromtarkov.fandom.com/wiki/Heavy_Vests), [Attention](https://escapefromtarkov.fandom.com/wiki/Attention), [Search](https://escapefromtarkov.fandom.com/wiki/Search) |

Q376~379·394·422·423·425~428·430~435에 `volatile`을 추가했다.
이번 변경 후 스킬 카테고리 32문항 모두에 근거 기록이 있지만, 최신 효과 실측 완료는 아니다.
Q410은 PvE에서 보고된 과거 사례로서 `pve`를 유지하며 Q429는 `common`을 유지한다.
버그 기록을 현재 게임의 정답으로 확정한 것이 아니라 문항의 시간 범위를 바꾼 것이다.
문제 수·난이도·정답 인덱스·모드별 출제 가능 수는 바뀌지 않았다.

## 6차 수정 — 의료 효과·예외·측정 기준

의료·식량 44문항 중 28문항을 추가로 대조했다. 앞서 검토한 Q415를 포함하면 해당
카테고리의 근거 기록은 29문항이며, 나머지 15문항은 이 차수에서 검토 완료로 표시하지 않는다.
근거는 약 2~3개월 전 위키 검색 수집본이다. 9월 패치 이후 실측 수치로 단정하지 않는다.

| 문항 | 수정·판정 | 근거 |
|---|---|---|
| Q146 | 지구력 스킬 버프를 직접 스태미나 회복 효과로 적은 오류 수정 | [Adrenaline](https://escapefromtarkov.fandom.com/wiki/Adrenaline_injector), [SJ6](https://escapefromtarkov.fandom.com/wiki/SJ6_TGLabs_combat_stimulant_injector) |
| Q230·235·247·252 | Health 스킬 증감과 HP 재생·피해 구분 | [eTG-change](https://escapefromtarkov.fandom.com/wiki/ETG-change_regenerative_stimulant_injector), [AHF1-M](https://escapefromtarkov.fandom.com/wiki/AHF1-M_stimulant_injector), [Propital](https://escapefromtarkov.fandom.com/wiki/Propital_regenerative_stimulant_injector), 각 술의 개별 문서 |
| Q55·148 | 중출혈을 전용 지혈 도구만 처치한다는 오해 제거 | [Salewa](https://escapefromtarkov.fandom.com/wiki/Salewa_first_aid_kit), AHF1-M |
| Q56·116 | 대사 엘리트의 고갈 피해 면역, 수술 스킬의 최대 HP 페널티 예외 보완 | [Metabolism](https://escapefromtarkov.fandom.com/wiki/Metabolism), [Surgery](https://escapefromtarkov.fandom.com/wiki/Surgery) |
| Q147·384~387 | 진통과 치료 구분, 부위·단위·재출혈 조건 명시 | [Health system](https://escapefromtarkov.fandom.com/wiki/Health_system) |
| Q233 | 새 키트 비교임을 명시하고 머리뿐 아니라 흉부도 수술 불가임을 보완 | [CMS](https://escapefromtarkov.fandom.com/wiki/CMS_surgical_kit), [Surv12](https://escapefromtarkov.fandom.com/wiki/Surv12_field_surgical_kit), [Medical](https://escapefromtarkov.fandom.com/wiki/Medical) |
| Q236·255 | 확인되지 않은 드론 설명 삭제, 체온 변화량과 절대 온도 구분 | [SJ9](https://escapefromtarkov.fandom.com/wiki/SJ9_TGLabs_combat_stimulant_injector), [SJ12](https://escapefromtarkov.fandom.com/wiki/SJ12_TGLabs_combat_stimulant_injector) |
| Q231·294·330·414·416 | 새 아이템 자원·횟수·기본 부작용·표기 사용 시간으로 범위 한정 | Medical, [Ibuprofen](https://escapefromtarkov.fandom.com/wiki/Ibuprofen_painkillers) |
| Q245·329 | 진통 지속시간의 기본값과 개인 보정 구분 | [Morphine](https://escapefromtarkov.fandom.com/wiki/Morphine_injector), [Immunity](https://escapefromtarkov.fandom.com/wiki/Immunity) |
| Q232·382·383·388 | 내용은 검색본과 일치, 근거와 필요한 변동형 표시 추가 | Medical, Health system |

Q146·382·384~388·414·416에 `volatile`을 추가했다. 모든 검토 문항의 정확한 출처 URL은
`questions.json`에 기록했다. 구급상자의 전체 자원과 한 번에 회복하는 HP, 기본 사용 시간과
실제 조작 시간을 구분했다. 수술 횟수 9회·3회는 영어 Medical 표 기준이며 최신 실측은 아니다.
정답 인덱스·난이도·모드·문항 수는 변경하지 않았다. 운영 DB나 실행 중 봇도 변경하지 않았다.

## 7차 수정 — 남은 의료·식량 비교 조건

앞선 차수에서 남은 의료·식량 15문항을 대조했다. 이 분류 44문항 모두에 근거 기록이
생겼지만, 이번에도 약 2~3개월 전 위키 검색 수집본에 의존했으므로 최신 실측 완료는 아니다.

| 문항 | 수정·판정 | 근거 |
|---|---|---|
| Q228 | 전체 미사용 음료의 기본값 비교로 한정. 부분 섭취·개인 보정·회복 상한과 구분 | [Aquamari](https://escapefromtarkov.fandom.com/wiki/Aquamari_water_bottle_with_filter), 생수·그랜드 주스·비상용 식수 개별 문서 |
| Q229 | MRE의 지속 회복을 포함하면 동률 가능. 즉시 회복 비교임을 명시 | [MRE](https://escapefromtarkov.fandom.com/wiki/MRE_ration_pack), [마요네즈](https://escapefromtarkov.fandom.com/wiki/Jar_of_DevilDog_mayo), 이스크라·연유 개별 문서 |
| Q234·250 | 아이템 자체의 확률 효과와 개인 면역 보정 구분. 옵돌보스 2의 부작용 보완 | [Obdolbos](https://escapefromtarkov.fandom.com/wiki/Obdolbos_cocktail_injector), [Obdolbos 2](https://escapefromtarkov.fandom.com/wiki/Obdolbos_2_cocktail_injector), [Immunity](https://escapefromtarkov.fandom.com/wiki/Immunity) |
| Q246 | 하중 한계 증가와 물건 무게 감소 구분, HP 재생률 부작용 명시 | [M.U.L.E.](https://escapefromtarkov.fandom.com/wiki/M.U.L.E._stimulant_injector) |
| Q248·249 | 지혈·해독의 적용 범위와 지속성 명시 | [Zagustin](https://escapefromtarkov.fandom.com/wiki/Zagustin_hemostatic_drug_injector), [Perfotoran](https://escapefromtarkov.fandom.com/wiki/Perfotoran_%28Blue_Blood%29_stimulant_injector) |
| Q251·253·254·256 | 기본 버프, 개인 보정, 효과 종류별 시간과 부작용을 구분 | [L1](https://escapefromtarkov.fandom.com/wiki/L1_%28Norepinephrine%29_injector), [Trimadol](https://escapefromtarkov.fandom.com/wiki/Trimadol_stimulant_injector), [Meldonin](https://escapefromtarkov.fandom.com/wiki/Meldonin_injector), [3-(b-TG)](https://escapefromtarkov.fandom.com/wiki/3-%28b-TG%29_stimulant_injector) |
| Q413 | 같은 보정 전 진통 시간 비교로 명시. 방사능 제거 지속시간과 구분 | [Golden Star](https://escapefromtarkov.fandom.com/wiki/Golden_Star_balm), [Medical](https://escapefromtarkov.fandom.com/wiki/Medical), Immunity |
| Q33·115·268 | 내용은 검색본과 일치, 근거 기록 | [GP-7](https://escapefromtarkov.fandom.com/wiki/GP-7_gas_mask), [Splint](https://escapefromtarkov.fandom.com/wiki/Immobilizing_splint), [Max Energy](https://escapefromtarkov.fandom.com/wiki/Can_of_Max_Energy_energy_drink) |

Q229는 마요네즈 즉시 회복 100과 MRE 즉시 회복 70만 비교하면 정답이 하나다.
그러나 MRE의 기본 지속 회복 `0.1 × 300 = 30`까지 더하면 총 표기량 100으로 같아진다.
이는 두 문서 수치에서 계산한 비교이며 소비·상한을 포함한 게임 내 실제 순증가량 실측은 아니다.
Q254도 버프와 디버프의 시작 지연이 달라 주사기 전체를 하나의 종료 시각으로 요약할 수 없다.
Q234에 `volatile`을 추가했으며 모드·난이도·정답 인덱스·문항 수는 유지했다.

## 8차 수정 — 장비 계산·비교·획득 범위

앞서 검토한 장비 6문항을 제외한 27문항을 대조했다. 장비 33문항 모두에 출처 기록이
생겼지만 대부분 약 2~3개월 전 위키 검색 수집본이며 최신 클라이언트 실측은 아니다.
Q159는 공식 0.14.0.0 포럼 원문이 403으로 열리지 않아 당시 배포 노트를 전재한
[PCGamesN의 2023-12-27 기사](https://www.pcgamesn.com/escape-from-tarkov/0-14-patch-notes)를 근거로 기록했다.
공식 원문 직접 확인이나 현재 히트박스 검증으로 표시하지 않는다.

| 문항 | 수정·판정 | 근거 |
|---|---|---|
| Q289 | 공간 효율과 kg당 칸수 혼동. **정답을 파르티잔 가방으로 변경** | [Backpacks](https://escapefromtarkov.fandom.com/wiki/Backpacks) |
| Q396 | 키 케이스 계산 정정, 수납 제한 명시 | [Key case](https://escapefromtarkov.fandom.com/wiki/Key_case), [Dogtag case](https://escapefromtarkov.fandom.com/wiki/Dogtag_case), [Containers](https://escapefromtarkov.fandom.com/wiki/Containers) |
| Q207·208·239 | 보기 내 비교·빈 배낭 무게로 한정, 의료 전용 가방 제한 보완 | Backpacks |
| Q399·400·402·412 | 재질만의 비교, 실효 내구도와 방어 등급 구분, 명중 대상과 두 계산 요인 명시 | [Ballistics](https://escapefromtarkov.fandom.com/wiki/Ballistics), [Death Knight](https://escapefromtarkov.fandom.com/wiki/Death_Knight_mask), [CQCM Black](https://escapefromtarkov.fandom.com/wiki/Atomic_Defense_CQCM_ballistic_mask_%28Black%29) |
| Q411 | 게임 등급 대응과 실물 시험·인증 성능 구분 | [Armor vests](https://escapefromtarkov.fandom.com/wiki/Armor_vests) |
| Q6·19·26·34 | 보존·보호·수납 범위를 다른 슬롯이나 모든 품목으로 확대하지 않음 | [Secure containers](https://escapefromtarkov.fandom.com/wiki/Secure_containers), [Headwear](https://escapefromtarkov.fandom.com/wiki/Headwear), Containers |
| Q176·219·221·222·295 | 에디션·내부 용량·보상 경로 한정. 관련 없는 Omicron 최신성 단정 제거 | [Gamma](https://escapefromtarkov.fandom.com/wiki/Secure_container_Gamma), [Alpha](https://escapefromtarkov.fandom.com/wiki/Secure_container_Alpha), [Theta](https://escapefromtarkov.fandom.com/wiki/Secure_container_Theta), [Prestige](https://escapefromtarkov.fandom.com/wiki/Prestige), [Waist pouch](https://escapefromtarkov.fandom.com/wiki/Waist_pouch) |
| Q290 | 일반 시청자 보상처럼 읽히지 않도록 특별 참가 계정으로 한정 | [Tournament container](https://escapefromtarkov.fandom.com/wiki/Tournament_secured_container), [Fanny pack](https://escapefromtarkov.fandom.com/wiki/Fanny_pack_%28Loui_Peeton%29) |
| Q10·11·112·159·397·398·401 | 내용 유지, 출처와 필요한 변동형 메모 기록 | [Health system](https://escapefromtarkov.fandom.com/wiki/Health_system), [Earpieces](https://escapefromtarkov.fandom.com/wiki/Earpieces), [Eyewear](https://escapefromtarkov.fandom.com/wiki/Eyewear), Ballistics, 당시 패치 전재 기사 |

계산은 출처의 기초값에서 다시 수행했다.

- Q289: 파르티잔 `20 / 0.7 ≈ 28.57`, LBT-2670 `48 / 1.92 = 25`,
  6Sh118 `48 / 3.5 ≈ 13.71`, Blackjack 50 `42 / 3.265 ≈ 12.86`칸/kg.
  기존 2.4·1.67·1.2·1.14는 외부 점유 칸 대비 공간 효율이었다.
- Q396: Containers 표의 키 케이스 효율 13.83은 개별 페이지의 `77 / 6 ≈ 12.83`과
  맞지 않아 기초값으로 계산한 값을 채택했다. 정답 도그태그 케이스는 변하지 않는다.
- Q412: `55 / 0.1875 ≈ 293.33`, `35 / 0.3375 ≈ 103.70`.
  재질 계수뿐 아니라 표시 내구도 차이도 결과에 기여한다. 이것으로 관통 방어력 우열을 단정하지 않는다.

Q176·219·396·399~402·412에 `volatile`을 추가했다. Q221·222·295의 현재 보상·획득 조건,
Q398~402·412의 최신 수치는 별도 실측이 필요하다. 방어 성능 제거 공지의 Shattered·Death Shadow와
Q412의 Death Knight는 다른 아이템이므로 같은 마스크로 취급하지 않았다.
문항 수·ID·난이도·모드는 유지했다. 운영 DB 및 실행 중 봇은 변경하지 않았다.

## 9차 수정 — 무기 호환성·작동·효과 범위

14문항 중 11문항을 보완했다. 정답 인덱스·문항 수·난이도·모드는 변경하지 않았다.

| 문항 | 판정·수정 | 근거 |
|---|---|---|
| Q15·21 | 모딩·부착물 용어는 유지하고 출처 기록 | [Weapon mods](https://escapefromtarkov.fandom.com/wiki/Weapon_mods) |
| Q38·267 | 탄창에 담을 수 있는 것과 총기의 발사 호환성 구분. Kedr와 Klin의 PMM PstM 차이 명시 | [Kedr](https://escapefromtarkov.fandom.com/wiki/PP-91_Kedr_9x18PM_submachine_gun), [PMM PstM](https://escapefromtarkov.fandom.com/wiki/9x18mm_PMM_PstM_gzh), [0.14 노트 전재](https://www.pcgamesn.com/escape-from-tarkov/0-14-patch-notes) |
| Q57 | 에르고 효과를 ADS 속도·조준 소리·스태미나로 명시. 무게도 영향을 준다는 조건 추가 | [Performance modifiers](https://escapefromtarkov.fandom.com/wiki/Performance_modifiers) |
| Q58·73 | 부품 추가와 교체 구분, 파츠별 호환·전용 마운트 확인 | Weapon mods, [Tokarev mount](https://escapefromtarkov.fandom.com/wiki/SVT-40_Tokarev_PU_mount) |
| Q108 | 아이언사이트 정의에서 모든 총기에 기본 장착된다는 함의 제거 | [SVT rear sight](https://escapefromtarkov.fandom.com/wiki/SVT-40_rear_sight) |
| Q150 | 총구 장치의 반동 감소와 모든 빌드의 최대 감소량을 구분 | Weapon mods |
| Q335 | 분류는 돌격 카빈 유지. SVT는 반자동, AVT는 자동사격도 가능하므로 둘 다 반자동으로 묶은 해설 수정 | [SVT-40](https://escapefromtarkov.fandom.com/wiki/Tokarev_SVT-40_7.62x54R_rifle), [AVT-40](https://escapefromtarkov.fandom.com/wiki/Tokarev_AVT-40_7.62x54R_automatic_rifle) |
| Q391·392 | 과열의 이전 단계 효과가 사라지는 것처럼 읽히지 않도록 새로 추가되는 고장을 질문. 교체 버프 해설에 약실 조건 명시 | [Weapon malfunctions](https://escapefromtarkov.fandom.com/wiki/Weapon_malfunctions) |
| Q393·395 | 숙련도 3레벨 효과 근거 기록. 275 경험치가 전체 무기 최저라는 해설의 함의를 제거 | [Weapon mastery](https://escapefromtarkov.fandom.com/wiki/Weapon_mastery) |

위키 직접 접근은 차단되어 약 2~3개월 전 검색 수집본을 대조했다. Q38의 혼합 장전은
2023-12-27 PCGamesN의 0.14 패치 노트 전재로 확인했다. 해당 기사에서 연결한 공식 원문은
접근 오류가 나서 직접 확인하지 못했다. Arena 노트의 유사 기능을 본편 근거로 사용하지 않았다.
Q391·392·393은 패치에 따른 규칙 변경 가능성을 표시했고, Q395의 기존 변동형 메모도
자료 시점과 실측 미완료를 명시하도록 갱신했다. Q395의 정답은 보기 네 계열 내 비교로 유효하다.
AS VAL도 275이고 ASh-12는 175이므로 AKS-74U가 전체 무기 중 최저라고 일반화하지 않는다.

## 10차 수정 — 구경·분류·공개와 출시 구분

26문항을 대조해 13문항을 보완했다. 정답 인덱스·문항 수·난이도·모드는 유지했다.
무기 분류 53문항 중 근거 기록은 45문항이며, 나머지 8문항과 최신 게임 실측은 미완료다.

| 문항 | 판정·수정 | 근거 |
|---|---|---|
| Q121·123 | AK-74 모델 범위와 게임의 SVDS 명칭을 명시 | [Ammunition](https://escapefromtarkov.fandom.com/wiki/Ammunition), [7.62x54mmR](https://escapefromtarkov.fandom.com/wiki/7.62x54mmR) |
| Q124 | 9x39mm를 VSS·AS VAL만 사용하는 것으로 읽히지 않도록 설명 | [9x39mm](https://escapefromtarkov.fandom.com/wiki/9x39mm) |
| Q125·281 | MP-18은 게임의 산탄총 분류지만 7.62x54R을 사용. Q125를 MP-133에 한정해 오답 보기와의 범위 중첩 제거 | [MP-133](https://escapefromtarkov.fandom.com/wiki/MP-133_12ga_pump-action_shotgun), [MP-18](https://escapefromtarkov.fandom.com/wiki/MP-18_7.62x54R_single-shot_rifle) |
| Q263·277 | 게임의 MCX·SPEAR 구경을 현실의 모든 변형에 일반화하지 않도록 명시 | [MCX](https://escapefromtarkov.fandom.com/wiki/SIG_MCX_.300_Blackout_assault_rifle), [SPEAR](https://escapefromtarkov.fandom.com/wiki/SIG_MCX-SPEAR_6.8x51_assault_rifle) |
| Q276·278 | .308 Marlin Express를 구분하고 탄창 이름과 총기 구경의 차이 설명 | [AK-308](https://escapefromtarkov.fandom.com/wiki/Kalashnikov_AK-308_7.62x51_assault_rifle), [VPO-209](https://escapefromtarkov.fandom.com/wiki/Molot_Arms_VPO-209_.366_TKM_carbine) |
| Q283·284·334 | 게임 내 모델·분류로 한정. .44 Magnum의 전체 게임 미존재 단정 제거 | [Weapons](https://escapefromtarkov.fandom.com/wiki/Weapons), [L5 .357](https://escapefromtarkov.fandom.com/wiki/Magnum_Research_Desert_Eagle_L5_.357_pistol), [AK-50](https://escapefromtarkov.fandom.com/wiki/TheAKGuy_AK-50_.50_BMG_anti-materiel_rifle) |
| Q458 | 방송 자체를 검증한 것처럼 표시하지 않고 직접 확인한 공식 게시물을 질문. 공개와 출시를 구분 | [공식 FAMAS 공개](https://t.me/escapefromtarkovEN/6745), [1.1.0 노트](https://telegra.ph/Patch-1100-08-03) |

내용 유지 후 근거만 추가한 13문항은 Q122·257·258·259·260·261·262·264·274·275·282·336·456이다.
각 문항의 `sources`에는 해당 무기 또는 구경 문서 URL을 기록했다. Howa Type 20은 1.1.0의
Content 목록을 직접 열어 5.56x45mm 사용을 확인했다. 다른 보기의 QBZ-191·HK 416A5 RAL 8000도
같은 목록에 있다. 위키의 미출시 무기 목록을 현행 출시 여부의 근거로 사용하지 않았다.

FAMAS의 개별 게시물은 공식 공개 채널에서 연결한 주소를 따라 확인했다. 공개 페이지 HTML의
해당 게시물 `time` 값은 `2026-08-10T18:08:51+00:00`으로, 한국시간으로는 8월 11일이다.
퀴즈에는 게시물 날짜의 UTC 기준과 한국시간의 날짜 차이를 함께 명시했다. 게시물에 이름이 공개된 사실과
게임에 출시된 사실은 다르므로 Q458은 여전히 `volatile`이며 출시 확인은 남겨두었다.

위키 자료는 접근 제한으로 약 2~3개월 전 검색 수집본을 사용했다. 여기서 확인한 구경·분류는
최신 탄약 피해·관통력·판매 조건 검증이 아니다. 타 사이트의 TKPD 수치가 다른 사례도 있어
이번에는 무게·반동·가격 등 추가 수치를 채택하지 않았다. 변동형 수량은 242개로 유지했다.

## 11차 — 무기 상태·반동·근접 공격의 일반화 수정

대상: Q28·39·45·51·63·65·70·90. 문항 수·ID·정답 인덱스·난이도·모드는 유지했다.

- Q28: 마모와 ‘관련 있는 스탯’은 MOA도 포함할 수 있어, 수리로 회복하는 상태 수치를 묻도록 명시했다.
- Q39: PNV-10T를 지정하고, T-7처럼 헬멧에 장착하는 열상 고글도 있음을 설명했다.
- Q45: 고장이 발생하는 총기로 범위를 한정하고 배출·급탄 실패와 노리쇠 걸림을 보기로 사용했다.
  PPSh-41 예외를 명시했으며, 고장 규칙은 패치 영향이 있어 `volatile`로 추가 표시했다.
- Q51: 소음기의 소리·화염 감소와 부착물별 다른 성능을 구분했다.
- Q63: RPM만으로 서로 다른 총기의 제어 난이도를 단정하지 않도록 수정했다.
  이는 반동 지표와 부착물 효과를 함께 비교한 판단이며, 두 총기의 실사격 비교 결과가 아니다.
- Q65: 근거에서 직접 확인되는 자세별 흔들림·반동 제어 차이를 묻도록 보완했다.
  이동 속도별 산포 공식이나 스킬 효과를 검증한 것으로 간주하지 않는다.
- Q70: ‘가볍고 소음 없이’라는 단정을 없애고 탄약 없이 베기·찌르기 공격을 할 수 있다는 이점으로 정리했다.
  근접무기라는 작동 방식에서의 판단이며, 소음 반경 실측을 근거로 한 문항이 아니다.
- Q90: 취급 무기를 러시아·구소련권으로 표현하고 개별 상품의 해금·재고 검증과 분리했다.

근거:

- [Item repair](https://escapefromtarkov.fandom.com/wiki/Item_repair),
  [Performance modifiers](https://escapefromtarkov.fandom.com/wiki/Performance_modifiers),
  [Weapon malfunctions](https://escapefromtarkov.fandom.com/wiki/Weapon_malfunctions)
- [PNV-10T](https://escapefromtarkov.fandom.com/wiki/PNV-10T_night_vision_goggles),
  [T-7](https://escapefromtarkov.fandom.com/wiki/T-7_Thermal_Goggles_with_a_Night_Vision_mount)
- [PPSh-41](https://escapefromtarkov.fandom.com/wiki/PPSh-41_7.62x25_submachine_gun),
  [PB](https://escapefromtarkov.fandom.com/wiki/PB_9x18PM_silenced_pistol),
  [P90 Attenuator](https://escapefromtarkov.fandom.com/wiki/FN_P90_Attenuator_5.7x28_sound_suppressor)
- [Weapon mods](https://escapefromtarkov.fandom.com/wiki/Weapon_mods),
  [How to Play Guide — Stances](https://escapefromtarkov.fandom.com/wiki/How_to_Play_Guide_for_Escape_from_Tarkov#Stances)
- [6Kh5 Bayonet](https://escapefromtarkov.fandom.com/wiki/6Kh5_Bayonet),
  [Crash Axe](https://escapefromtarkov.fandom.com/wiki/Crash_Axe),
  [Prapor](https://escapefromtarkov.fandom.com/wiki/Prapor)

직접 접근 제한 때문에 약 2~3개월 전 위키 검색 수집본을 사용했다. Prapor 페이지에 남은
거래액 조건처럼 공식 1.1.0 변경과 맞지 않는 항목은 채택하지 않았다. 이번 검수는 해당 페이지의
모든 정보가 최신이라는 판정이 아니다. 무기 53문항의 근거 기록도 전수 실측 완료를 뜻하지 않는다.

최신 탄약 데이터 대조를 위해 공개 `api.tarkov.dev/graphql` 응답 가능 여부를 재확인했으나,
읽기 전용 최소 쿼리가 HTTP 422와 `GraphQL server unavailable. Try again later.`를 반환했다.
따라서 이번 차수에 탄약 수치를 변경하거나 최신 데이터 검증 완료로 표시하지 않았다.

## 12차 — 탄약 관통·피해 비교 범위 검수

대상: Q46·52·158·186·187·188·194·199·200·237·238·265·266·280·286·296·404·405·407.

- Q52는 관통력과 방어구 등급을 단순 수치 비교하던 조건을 관통 판정 실패로 고쳤다.
  Q46·158·404·405도 관통 확률, 기본 피해와 실제 피해, 둔격 피해의 조건을 구분했다.
- 수치 비교 12문항은 보기 안의 기본값 비교로 명시했다. Q199·237의 게임 전체 순위 단정을
  없앴다. 기존 정답 인덱스와 대조한 기본 피해·관통 수치는 유지했다.
- Q280은 펠릿 1개 기준임을 유지하면서 탄종별 펠릿 수 차이를 설명했다.
  Q296의 관통력은 투사체 개수의 합산값이 아님을 명시했다.
- Q265의 ‘아탄속탄’을 ‘아음속탄’으로 수정하고 보기 이름을 실제 탄종명으로 정리했다.
- Q238의 섬광탄 분류·피해 0은 수집본과 일치했다. Q407의 ‘거의 항상 1’도 수집본과 일치했으나
  정확한 도탄 수치는 변경 가능하므로 `volatile`로 추가 표시했다.

근거:

- [Ballistics](https://escapefromtarkov.fandom.com/wiki/Ballistics): Q46·52·158·404·405·407.
- [7.62x51mm NATO](https://escapefromtarkov.fandom.com/wiki/7.62x51mm_NATO): Q186·187;
  [M993](https://escapefromtarkov.fandom.com/wiki/7.62x51mm_M993): Q199 비교값.
- [.338 Lapua Magnum](https://escapefromtarkov.fandom.com/wiki/.338_Lapua_Magnum): Q188·199;
  [TAC-X](https://escapefromtarkov.fandom.com/wiki/.338_Lapua_Magnum_TAC-X): Q200 비교값.
- [.50 BMG](https://escapefromtarkov.fandom.com/wiki/.50_BMG): Q199·200·237;
  [12.7x108mm](https://escapefromtarkov.fandom.com/wiki/12.7x108mm): Q199 비교값.
- [12/70](https://escapefromtarkov.fandom.com/wiki/12/70): Q194·280·296;
  [RIP](https://escapefromtarkov.fandom.com/wiki/12/70_RIP),
  [SuperFormance HP](https://escapefromtarkov.fandom.com/wiki/12/70_SuperFormance_HP_slug): Q200 비교값.
- [Zvezda](https://escapefromtarkov.fandom.com/wiki/23x75mm_Zvezda_flashbang_round),
  [23x75mmR](https://escapefromtarkov.fandom.com/wiki/23x75mmR): Q238.
- [9x21mm Gyurza](https://escapefromtarkov.fandom.com/wiki/9x21mm_Gyurza): Q265;
  [.366 TKM](https://escapefromtarkov.fandom.com/wiki/.366_TKM): Q266;
  [20/70](https://escapefromtarkov.fandom.com/wiki/20/70): Q286.

영어 위키의 약 2~3개월 전 검색 수집본에 근거했다. 같은 위키의 번역본에는 M993 등 수치가
다른 경우가 있어 혼합하지 않았다. 최신 API 수치를 확보하지 못한 상태이므로 1.1.5.1 현재의
실측 검증 완료로 취급하지 않는다. 수치형 문항의 메모에도 이 한계를 명시했다.
이번 수치 확인은 피해·관통·관련 펠릿 수에 한정하며 같은 표의 판매·제작 조건까지 승인한 것이 아니다.
탄약 46문항 중 근거 기록은 기존 Q403을 포함해 20문항이며 나머지 26문항의 검수가 남는다.

## 13차 — 남은 탄약 수치·비교 문항 대조

대상: Q178~185·189~193·195~198·201·279·285·325~328·341(25문항).
기존 정답 인덱스와 대조한 피해·관통 수치는 영어 위키 수집본과 일치했다.
전체 탄종 최상위를 단정하던 비교는 보기의 기본값 비교로 명시했다.

- Q179: 낮은 관통력을 ‘방탄복에는 무력’으로 단정하지 않도록 수정.
- Q181: 관통력과 피해가 항상 반비례한다는 일반화 제거. 같은 5.45mm에서 7N40은
  BT보다 피해(55 대 54)와 관통(42 대 37)이 모두 높다는 수집본의 반례를 설명에 추가.
- Q325: 최고가 아닌 두 번째라는 질문 의도와 정답 QuakeMaker 유지.
- Q326·327: 구경 크기·기본 피해량을 실제 처치 성능과 동일시하지 않도록 보완.
- Q328·341: 각각 M855A1 관통 44, SNB 기본 피해 75를 유지하되 기본값 기준을 명시.

근거는 각 구경의 영어 위키 Types 표다. 판매·제작 열의 최신성은 승인하지 않았다.

- [.357 Magnum](https://escapefromtarkov.fandom.com/wiki/.357_Magnum): Q178.
- [.45 ACP](https://escapefromtarkov.fandom.com/wiki/.45_ACP): Q180.
- [9x19mm](https://escapefromtarkov.fandom.com/wiki/9x19mm_Parabellum): Q179·191·325·327;
  [Ballistics](https://escapefromtarkov.fandom.com/wiki/Ballistics): Q179 조건 설명.
- [5.56x45mm](https://escapefromtarkov.fandom.com/wiki/5.56x45mm_NATO): Q181·192·326·328.
- [5.45x39mm](https://escapefromtarkov.fandom.com/wiki/5.45x39mm): Q183·184 및 Q181 반례.
- [7.62x39mm](https://escapefromtarkov.fandom.com/wiki/7.62x39mm): Q182·185·326.
- [9x39mm](https://escapefromtarkov.fandom.com/wiki/9x39mm): Q189·190·326.
- [.50 AE](https://escapefromtarkov.fandom.com/wiki/.50_Action_Express): Q193.
- [5.7x28mm](https://escapefromtarkov.fandom.com/wiki/5.7x28mm_FN): Q195·327;
  [4.6x30mm](https://escapefromtarkov.fandom.com/wiki/4.6x30mm_HK): Q196.
- [7.62x54mmR](https://escapefromtarkov.fandom.com/wiki/7.62x54mmR): Q197·198·341.
- [9x18mm](https://escapefromtarkov.fandom.com/wiki/9x18mm_Makarov): Q201·285;
  [7.62x25mm](https://escapefromtarkov.fandom.com/wiki/7.62x25mm_Tokarev): Q279.
- [12.7x55mm](https://escapefromtarkov.fandom.com/wiki/12.7x55mm): Q326;
  [.366 TKM](https://escapefromtarkov.fandom.com/wiki/.366_TKM),
  [7.62x51mm](https://escapefromtarkov.fandom.com/wiki/7.62x51mm_NATO): Q327.

약 2~3개월 전 수집본 대조이며 최신 클라이언트나 API 응답의 수치 검증은 아니다.
수치형 25문항은 모두 `volatile`을 유지하고 검토 메모를 이 근거 수준에 맞췄다.
탄약 근거 기록은 45/46문항이지만 Q369는 아직 미확인이다. 공식
[1.1.0 배포 노트](https://telegra.ph/Patch-1100-08-03)를 다시 확인했으나 T-45M1 시작 판매를
명시하지 않는다. 일부 탄약의 로열티 단계 하향을 특정 탄종의 시작 판매 확정으로 추론하지 않았다.
해당 문항은 이번에 수정하거나 근거 확인 완료로 표시하지 않았으며 검증 대상으로 남긴다.

## 14차 — 기본 시스템·시즌 보상의 범위

대상: Q2·4·5·17·30·49·74·92·93·96·97·106·107·109·114·408·409·447·448·449·451·455.
문항 수·ID·정답 인덱스·난이도·모드·카테고리는 유지한다.

- Q109: LEDX를 피부 이식용으로 잘못 설명한 부분을 정맥 위치 확인 기기로 수정했다.
  [LEDX](https://escapefromtarkov.fandom.com/wiki/LEDX_Skin_Transilluminator).
- Q17·30·49: 진영은 PMC 생성 시 선택한다. 레이드 입장 선택과 분리하고, 시간대 선택은
  지원 맵으로 한정했다. 보스 스폰을 어떤 상황에서도 미리 알 수 없다는 단정도 제거했다.
  [플레이 가이드](https://escapefromtarkov.fandom.com/wiki/How_to_Play_Guide_for_Escape_from_Tarkov).
- Q4·74·106·107: Scav 용어·별도 성장·재입장 대기·생환 후 이전을 대조했다.
  PMC 장비가 안전하다는 것과 Scav의 전리품까지 사망 후 보존된다는 주장을 구분했다.
  [Scavs](https://escapefromtarkov.fandom.com/wiki/Scavs).
- Q5·97: 사망·시간 초과 손실에 보호 슬롯 예외를 명시했다. 장착 근접무기의 컬티스트 칼 예외와
  MIA 당시 장착 중인 보험 장비의 반환 제외를 설명했다. 오래된 보험료·반환시간은 채택하지 않았다.
  [보험](https://escapefromtarkov.fandom.com/wiki/Insurance).
- Q96: 런스루의 불이익을 모든 보상이 아니라 경험치 계산으로 설명했다. 세부 숫자는 추가하지 않았다.
  [경험치](https://escapefromtarkov.fandom.com/wiki/Experience).
- Q114: 확인하지 못한 AN-94 예시를 제거하고 Vector 9x19의 세 발사 모드를 기준으로 출제했다.
  [Vector 9x19](https://escapefromtarkov.fandom.com/wiki/TDI_KRISS_Vector_Gen.2_9x19_submachine_gun).
- Q2·92·93·408·409: 개발사, 도그태그 정보, 업적 표시·초기화 규칙을 대조했다.
  거주 국가와 국적을 혼용하던 설명도 맞췄다.
  [개발사](https://www.battlestategames.com/), [도그태그](https://escapefromtarkov.fandom.com/wiki/Dogtag),
  [업적](https://escapefromtarkov.fandom.com/wiki/Achievements).
- Q447·448·449·451·455: 공식 1.1.0의 시즌 초기화·보상·배틀 패스·컬렉터 업적·관전을 대조했다.
  Q448의 보상은 해금한 고유 상인 거래 상품으로 한정했다. 일반 전리품 전체의 프로필 간 이전으로
  해석하지 않는다. Q455는 관전 대상 분대원이 사망할 때까지라는 조건으로 명확히 했다.
  Q5의 시즌 보험 불가도 같은 노트를 근거로 기록했다.
  [공식 1.1.0 노트](https://telegra.ph/Patch-1100-08-03).

위키는 약 2개월 전 검색 수집본이다. Q5·97·409에 `volatile`을 추가했다.
보험 반환시간 등 패치와 충돌하는 오래된 수치와 업적 총개수의 내부 불일치는 채택하지 않았다.
근거를 기록한 22문항 중 Q4·92·408·409·447·449·451의 문제·보기·해설은 유지했다.
이번 검사 역시 최신 클라이언트 실측 완료를 뜻하지 않는다.

## 15차 — 상인 접근·거래 단계·퀘스트 회수품

대상: Q12·13·22·25·27·31·36·42·48·50·53·54·59·60·62·64·68·75·87·88·89·91·117·126·127·167·172·223·224·227·291·292·313·452·453.
문항 수·ID·정답 인덱스·난이도·모드·카테고리는 유지한다.

- Q27: 프라포르가 처음부터 열린다는 단정을 Tour의 메카닉·Factory 단계 해금 문항으로 수정했다.
  [Tour](https://escapefromtarkov.fandom.com/wiki/Tour), [Prapor](https://escapefromtarkov.fandom.com/wiki/Prapor).
- Q68·75: 예거 해금은 Introduction 완료다. 다른 보기를 모두 기본 해금 상인이라고 설명하던
  부분을 수정하고, 전갈 회수·메카닉 전달을 명시했다.
  [Introduction](https://escapefromtarkov.fandom.com/wiki/Introduction),
  [Mechanic](https://escapefromtarkov.fandom.com/wiki/Mechanic), [Skier](https://escapefromtarkov.fandom.com/wiki/Skier).
- Q13·25·36·48: 거래 단계 LL과 평판을 구분했다. 레벨만으로 모든 상인이 해금되거나 모든 가격이
  할인된다는 설명, 카르마가 펜스에만 영향을 준다는 단정은 제거했다.
  승급 조건에 누적 거래액을 다시 넣지 않았다. [공식 1.1.0 노트](https://telegra.ph/Patch-1100-08-03),
  [퀘스트](https://escapefromtarkov.fandom.com/wiki/Quests).
- Q12·22·31·62·64·117: 거래·선불 등록 수수료·재입고·바터를 대조했다.
  벼룩시장에는 상인 매물도 표시되며, 펜스의 재판매 재고는 일반 재입고 설명과 구분했다.
  [거래](https://escapefromtarkov.fandom.com/wiki/Trading), [바터](https://escapefromtarkov.fandom.com/wiki/Barter_trades).
- Q50·59: 카르마와 펜스 평판의 관계, 펜스의 재판매 재고를 확인했다. 단순 랜덤 잡화라는
  설명을 실제 판매된 물품을 취급한다는 설명으로 고쳤다.
  [Scavs](https://escapefromtarkov.fandom.com/wiki/Scavs), [Fence](https://escapefromtarkov.fandom.com/wiki/Fence).
- Q60: 별도 퀘스트 인벤토리의 전용 회수품과 일반 제출품을 구분했다.
  퀘스트에 쓰이는 모든 루팅 아이템이 거래 불가인 것은 아니다.
  [퀘스트 아이템 규칙](https://escapefromtarkov.fandom.com/wiki/Quests).
- Q42·126·127: 영구 프로필 보험·예거 보험의 상대적 특징·The Lab 반환 제외를 대조했다.
  배포 노트에 없는 ‘수 시간’ 단정은 제거했다. 사전 예고에는 해당 표현이 있었다(16차 정정 참고).
  [1.1.0 노트](https://telegra.ph/Patch-1100-08-03),
  [보험](https://escapefromtarkov.fandom.com/wiki/Insurance).
- Q53·54·87·89·91·167·223·224·227·291·292: 상인별 통화·취급품·소재지·신원을 대조했다.
  [Peacekeeper](https://escapefromtarkov.fandom.com/wiki/Peacekeeper), [Skier](https://escapefromtarkov.fandom.com/wiki/Skier),
  [Therapist](https://escapefromtarkov.fandom.com/wiki/Therapist), [Ragman](https://escapefromtarkov.fandom.com/wiki/Ragman),
  [Jaeger](https://escapefromtarkov.fandom.com/wiki/Jaeger), [Ref](https://escapefromtarkov.fandom.com/wiki/Ref),
  [Prapor](https://escapefromtarkov.fandom.com/wiki/Prapor), [Mechanic](https://escapefromtarkov.fandom.com/wiki/Mechanic).
- Q88·313: 건스미스 제공자는 메카닉, 1편 개조 대상은 MP-133으로 대조했다. 부품·수치 추가는 하지 않았다.
  [Gunsmith - Part 1](https://escapefromtarkov.fandom.com/wiki/Gunsmith_-_Part_1).
- Q172: 레이드 내 상인·안전한 접근 조건을 확인했다. 로그 지휘 관계처럼 서비스와 혼동하기 쉬운
  오답 보기를 메뉴 전용 NPC라는 명확한 오답으로 교체했다.
  [Lightkeeper](https://escapefromtarkov.fandom.com/wiki/Lightkeeper).
- Q452·453: 그룹 공유의 조건과 사이드 퀘스트의 Scav 판정을 공식 노트와 대조하고 내용을 유지했다.
  [1.1.0 노트](https://telegra.ph/Patch-1100-08-03).

위키는 약 2개월 전 검색 수집본이다. 오래된 상인 문서의 누적 거래액 조건과 보험 반환시간은
1.1.0 노트와 충돌하므로 채택하지 않았다. Q27·68·75·127에 `volatile`을 추가했다.
상인 33문항 중 31문항에 근거가 기록됐지만 Q225·226 매입 배율의 최신성은 미확인이다.
이번 기록 역시 최신 게임 화면으로 실제 거래·해금을 수행했다는 뜻은 아니다.

## 16차 — 퀘스트 개편·지정 무기·열쇠 용도

대상: Q154·209·310·311·315·316·317·319·320·321·323(11문항).
문항 수·정답 인덱스·난이도·모드·카테고리는 유지하고 Q154에 `volatile`을 추가했다.

- Q154: 엡실론 보상 단계를 The Punisher - Part 6으로 명시했다.
  [영문 위키](https://escapefromtarkov.fandom.com/wiki/The_Punisher_-_Part_6)와
  [일본어 위키의 Ver 1.1 보상 목록](https://wikiwiki.jp/eft/Prapor/The%20Punisher%20-%20Part%206)을 대조했다.
- Q209: 모든 퀘스트에서 사용하지 않는다는 부정 명제를 세 목표 방의 열쇠 구분으로 한정했다.
  118호 열쇠는 루팅 방을 열기 때문에 ‘쓰이는 곳이 없다’는 해설을 제거했다.
  [110호](https://escapefromtarkov.fandom.com/wiki/Dorm_room_110_key),
  [114호](https://escapefromtarkov.fandom.com/wiki/Dorm_room_114_key),
  [203호 목표](https://escapefromtarkov.fandom.com/wiki/Shaking_Up_the_Teller),
  [118호](https://escapefromtarkov.fandom.com/wiki/Dorm_room_118_key),
  [최근 Pharmacist 목표](https://tarkov.help/en/quest/pharmacist).
- Q310·316: Shooting Cans의 고정 화기·Ground Zero 목표를 대조했다. Q310은 ‘가장 첫 번째’
  대신 퀘스트 목표로 식별하도록 바꿨다. 1.1 배포 노트는 LL별 묶음 배포와 일부 체인 유지를
  설명하므로 오래된 선후행 목록을 그대로 현행 순서로 확정하지 않는다.
  [Shooting Cans](https://tarkov.help/en/quest/shooting-cans),
  [배포 노트](https://telegra.ph/Patch-1100-08-03).
- Q311: 1.1 Debut 목표는 지정된 네 맵에서 스캐브 합계 5명 처치다. 옛 MP-133 2정 제출을
  정답에서 제거했다. [일본어 위키 Ver 1.1](https://wikiwiki.jp/eft/Prapor/Debut),
  [Tarkov.help 목표 목록](https://tarkov.help/en/quest/debut),
  [TarkovHead 목표·가이드](https://www.tarkovhead.com/en/quest/regular/debut)가 일치한다.
  오래된 영문 위키와 6개월 전 PvE 검색 수집본에는 구 목표가 남아 있다. 이 시점 차이를
  현재 PvP/PvE의 목표 차이라고 단정해 모드를 분리하지 않았다.
- Q315: 최근 자료의 The Tarkov Import 명칭을 반영하고 이전 이름도 병기했다.
  SR-25·Hybrid 46·PM II 1-8x24 조합과 Lighthouse/Reserve 조건을 반영했다.
  [Tarkov.help](https://tarkov.help/en/quest/test-drive-part-1),
  [TarkovBox](https://www.tarkovbox.com/en/gamewiki/tasks/the-tarkov-import).
  처치 수는 [TarkovForge](https://tarkovforge.com/task-guide/the-tarkov-import)의 6명과
  Tarkov.help의 10명이 충돌해 해설에서 제거하고 미확인으로 남겼다. 원래 질문은 무기 식별이다.
- Q317: 컬티스트 처치에 필요한 MP-43-1C/소드오프 더블배럴 조건을 추가했다.
  [위키](https://escapefromtarkov.fandom.com/wiki/Hell_on_Earth_-_Part_2),
  [TarkovHead](https://www.tarkovhead.com/en/quest/regular/hell-on-earth-part-2),
  [TarkovBox](https://www.tarkovbox.com/en/gamewiki/tasks/hell-on-earth-part-2).
  위키의 3명과 [다른 집계의 2명](https://tarkovforge.web.app/task-guide/hell-on-earth-part-2)이
  충돌하므로 대상·무기 조합을 묻는다. 수량을 검증 완료한 것으로 처리하지 않는다.
- Q319·320: 로그 10명 및 Reserve 지하 지휘 벙커의 레이더 5명을 대조하고 내용을 유지했다.
  [Outcasts](https://tarkov.help/en/quest/the-huntsman-path-outcasts),
  [No Place for Renegades](https://tarkov.help/en/quest/no-place-for-renegades).
  Outcasts는 문서 안에서도 인정 지역 표현이 섞이므로 전체 지역 목록 확정은 보류했다.
- Q321: 로그 처치 외 FIR LBT 장비 제출도 있어 처치만으로 완료된다는 오해를 줄였다.
  [위키](https://escapefromtarkov.fandom.com/wiki/Drip-Out_-_Part_2)와
  [공략](https://tarkov.help/tu/quest/drip-out-part-2)의 100명·50개를 대조했다.
  [USEC 집계](https://tarkovforge.com/task-guide/drip-out-part-2-usec)는 다른 수량을 표시한다.
  해당 사이트의 단일 표기를 채택하지 않았으며, 진영별 최신 수량 검증은 완료가 아니다.
- Q323: [Prestige 6 목록](https://escapefromtarkov.fandom.com/wiki/New_Beginning_%28Prestige_6%29)의
  로그 100명 및 다른 목표를 대조했다. 불필요한 Prestige 4·5 비교를 제거하고
  [공식 Blackout 한시 조정 공지](https://t.me/escapefromtarkovEN/6691)와 구분했다.
  최신 모드별 목표와 이벤트 원복 시점 확인은 완료하지 않았다.

**자료의 최신성 한계:** 최근 수집된 페이지에도 옛 위키 가이드와 새 목표가 함께 실려 있었다.
수집일이 최근이라는 이유만으로 모든 문장을 채택하지 않았다. 공개 Tarkov API로 직접 대조하려고
했으나 `GraphQL server unavailable` 응답으로 실패했다. 게임 클라이언트 실측은 하지 않았다.
Q315·317은 불확실한 수량을 출제 내용에서 제거했지만 Q321·323의 수량은 검토 보류 상태로
현재 풀에 남는다. 이 11개는 근거 기록 추가이지 전부 최신 정답 확정이라는 뜻이 아니다.

**15차 보고 표현 정정:** 예거의 ‘수 시간’ 반환은 [공식 사전 예고](https://t.me/escapefromtarkovEN/6687)에
있었다. 배포 노트에는 구체적 시간이 없으므로 현재 문항에서 빼는 것은 유지하지만,
‘공식 근거가 전혀 없는 주장’으로 설명하면 잘못이다. 양쪽 README도 이 구분을 명시했다.

## 17차 — Blackout 당시 기록과 Collector·탄약 판매 조건

대상: Q360·361·362·363·367·369·371·372(8문항). 문항 수·정답 인덱스·난이도·모드·
카테고리·`volatile` 여부는 유지했다. 퀘스트 33문항과 탄약 46문항 모두 근거 기록이 생겼으나,
이는 모든 조건의 최신 게임 검증 완료를 의미하지 않는다.

- Q360: Blackout의 첫 과제와 제공자를 당시 기록으로 명시했다. Skier의 Wrench and
  Waterboarding은 The Lab 방문이 목표였다.
  [TarkovHead](https://www.tarkovhead.com/en/quest/regular/wrench-and-waterboarding),
  [일본어 위키](https://wikiwiki.jp/eft/Skier/Wrench%20and%20Waterboarding).
- Q361: 코드룸을 **직접 여는 열쇠**를 묻는다. Wedge도 획득 경로이며, 이미 열린 방에
  입장하는 사람까지 직접 블랙 디비전을 처치해야 하는 것은 아니다.
  [당시 공략](https://primagames.com/tips/how-to-finish-the-key-to-every-door-quest-in-escape-from-tarkov-blackout-event),
  [열쇠·코드룸 안내](https://www.tarkovhead.com/en/quest/regular/key-to-every-door),
  [공식 드롭 확률 조정 공지](https://t.me/escapefromtarkovEN/6682).
- Q362: Blackout이 시작된 뒤 도입된 첫 시즌을 묻는 연혁 문항으로 명확히 했다.
  [Blackout 개시 공지](https://t.me/escapefromtarkovEN/6670)와
  [1.1.0 배포 노트](https://telegra.ph/Patch-1100-08-03)를 대조했다.
  공식 원문에서 확인하지 못한 ‘프리시즌’ 명칭이나 최종 종료 날짜를 단정하지 않는다.
- Q363: 열화상 장비 보상과 기본 루블 보상·보너스를 구분했다. 블랙 디비전 의류가
  시즌 1 보상이라는 별도 단정은 이 퀘스트의 정답 근거가 아니므로 제거했다.
  [당시 보도](https://insider-gaming.com/tarkov-blackout-how-to-complete-labs-keycard/),
  [보너스를 구분한 보상 목록](https://wikiwiki.jp/eft/Skier/Wrench%20and%20Waterboarding).
- Q371·372: [공식 밸런스 조정 공지](https://t.me/escapefromtarkovEN/6682)의
  PvP 30분/PvE 35분을 확인했다. 이벤트 내 특정 조정 시점임을 질문에 넣었고,
  현재 상시 제한 시간 또는 종료 후 원복을 검증한 것처럼 쓰지 않는다.
  공식 공지 본문은 [채널 수집 페이지](https://t.me/s/escapefromtarkovEN?before=6697)에서 확인했다.
- Q367: ‘모든 상인 LL4’라는 과도한 범위를 주요 7명으로 바로잡았다. Prapor·Therapist·
  Skier·Peacekeeper·Mechanic·Ragman·Jaeger의 LL4와 Fence의 별도 평판 조건을 구분한다.
  [공식 사전 예고](https://t.me/escapefromtarkovEN/6680),
  [일본어 위키의 7명·평판 3.0 목록](https://wikiwiki.jp/eft/Fence/Collector),
  [Tarkov.help](https://tarkov.help/en/quest/collector),
  [9월 갱신 가이드](https://gaming-st.com/news/tarkov-kappa-requirements-relaxed-2026-jul/).
  평판 3.0은 배포 후 커뮤니티 자료에 근거하며 공식 배포 노트에 그 수치가 있는 것은 아니다.
  Tarkov.help의 Fence ‘loyalty level 3’ 문구를 LL3로 번역하지 않았다. Tarkov.help와
  [TarkovHead](https://www.tarkovhead.com/en/quest/regular/collector)의 시작 레벨
  40/42와 선행 퀘스트 목록이 달라 전체 해금 체크리스트는 확정하지 않았다.
  한편 목표의 레벨 55 표시는 시작 레벨과 다른 필드이므로 숫자가 다르다는 이유만으로
  동일 조건의 모순이라고 취급하지 않았다.
- Q369: 사전 예고만 있던 상태에서 배포 후 판매 목록을 추가 대조했다.
  [공식 예고](https://t.me/escapefromtarkovEN/6687),
  [Tarkov Market의 Prapor LL1 판매 목록](https://tarkov-market.com/item/7.62x39_mm_t45m),
  [TarkovForge 판매 목록](https://tarkovforge.com/ammo/762x39mm-t-45m1-gzh).
  T-45M1의 프라포르 LL1 판매를 반영하고 ‘시작 즉시’와 상인 해금을 구분했다.
  가격·재고·개인 구매 한도를 실측한 것은 아니다. 마켓 페이지의 예시 가격 분석 블록도
  실제 시장 측정값으로 채택하지 않았다.

Blackout 6문항은 2026년 7월 당시 기록으로 유지한다. ‘약 1개월’, ‘종료 시 원래 시간 복귀’라는
기존 메모의 미확인 단정은 삭제했다. 당시 종료 예정 공지는 연장 공지로 바뀌었고,
민간 사이트의 8월 2일/3일 표기만으로 최종 공식 종료일을 확정하지 않았다.
Collector의 시작 레벨·전체 선행 목록·모드별 조건, 현재 Labs 제한 시간 등은 계속 미확인이다.

## 18차 — 보스의 본거지·출현 예외와 Blackout 기록

검토 대상: Q133·134·135·136·137·217·218·357·358·359·436·437.
ID·정답 인덱스·보기·난이도·모드·카테고리를 유지한다.

- Q133·134·217: ‘상주 맵’을 유일한 출현 맵이나 매 레이드 출현으로 읽지 않도록
  ULTRA 쇼핑몰, 세관의 세부 거점, 리저브 군사기지라는 출제 대상을 명시했다.
  [Killa](https://escapefromtarkov.fandom.com/wiki/Killa),
  [Reshala](https://escapefromtarkov.fandom.com/wiki/Reshala),
  [Glukhar](https://escapefromtarkov.fandom.com/wiki/Glukhar)는 터미널 출현도 기록한다.
  레샬라 경호원 4명은 세관의 배치이며 터미널은 3명이다.
  글루하르도 리저브 6명과 터미널 3명을 구분한다. 현재 출현 확률은 확인하지 않았다.
- Q135·136: [Tagilla](https://escapefromtarkov.fandom.com/wiki/Tagilla)의 용접 마스크·망치와
  [Shturman](https://escapefromtarkov.fandom.com/wiki/Shturman)의 우즈 벌목장·원거리 교전을
  대조했다. 원래 지문이 다른 맵·장비의 가능성을 배제하지 않아 내용은 유지했다.
- Q137: [Sanitar](https://escapefromtarkov.fandom.com/wiki/Sanitar)의 인물 소개에 맞춰
  TerraGroup Labs 연구원 출신으로 설명하고, 교전 중 치료 및 터미널 출현을 덧붙였다.
  기존 ‘의사 출신’이 거짓이라고 확정한 것이 아니라 이번 자료에서 직접 확인한 소개를 썼다.
- Q218·436: [Kaban](https://escapefromtarkov.fandom.com/wiki/Kaban)의 LEXOS 거점,
  Gus·Basmach와 기타 경호 인원 구성을 대조했다. Q436의 내용은 유지했다.
  Q218의 비교 설명은 [Kollontay](https://escapefromtarkov.fandom.com/wiki/Kollontay)에
  기록된 내무부 아카데미와 클리모프 쇼핑몰을 반영했다.
- Q437: [Big Pipe](https://escapefromtarkov.fandom.com/wiki/Big_Pipe)의 M32A1은 장비 목록에
  있지만 FN40GL 등 대체 무장도 있다. 고정 장비나 특정 보스 전용이라는 함의를 피하고,
  다른 보스 장비를 단정하던 불필요한 비교를 제거했다.
- Q358: [Blackout 가이드](https://www.tarkovhead.com/en/event/blackout-1)와
  [당시 안내](https://www.tarkovhead.com/en/news/blackout-event-guide-new-labs-mechanics-quests-and-achievement-17)의
  랩 점거 세력·The Wedge 설명을 대조했다. 2026년 7월 기록으로 한정하고
  ‘먼저 등장’과 ‘약 1개월 한시’ 표현을 제거했다. 최종 공식 종료일은 확정하지 않았다.
- Q357·359: 같은 이벤트 가이드와
  [Key to Every Door](https://www.tarkovhead.com/en/quest/regular/key-to-every-door)를 대조했다.
  맵 정전과 매 레이드 바뀌는 비상 접근 코드를 당시 기록으로 명시했다.
  탈출 활성화와 접근 암호를 구분하고, ‘5619는 특정 레이드의 코드였다’는 미확인 일화를
  해설에서 제거했다. 고정 코드 오답 보기는 유지한다.

보스 위키 자료는 약 2개월 전 검색 수집본이다. 공식 Telegram 6670 및 1.1.5.0 노트의
이번 직접 조회는 접근 오류로 실패했으며, 새로 원문 확인에 성공했다고 간주하지 않았다.
최신 날짜의 민간 보스 가이드에도 ‘수처리장 섬’, 터미널 신규 보스 등 다른 자료와 어긋나는
내용이 있어 최신 날짜만으로 채택하지 않았다. 이번 기록은 문항 범위 보완이지 최신
모드별 배치·이벤트 상태의 실측 완료가 아니다. 18차 시점에 남겨둔 보스·AI 15문항은
아래 19차에서 대조했으며, 상인 매입 배율 Q225·226 등은 후속 검토 대상으로 유지한다.

## 19차 — 일반 AI·컬티스트 조건과 산타 이벤트 범위

검토 대상: Q18·132·139·140·165·166·210·212·213·214·215·216·243·271·340.
문항 수·ID·정답 인덱스·난이도·모드·카테고리를 유지한다. Q166·271의 정답 보기 문장은
설명의 범위를 고쳤고 정답 대상은 바꾸지 않았다. 나머지 보기는 그대로다.

- Q18·215: [Scavs](https://escapefromtarkov.fandom.com/wiki/Scavs)의 플레이어 Scav 및
  Svetloozersk/Shturman·Zavodskoy/Reshala 지휘 관계를 대조했다. Q18은 대기 중인
  플레이어가 기존 AI를 조작하는 것처럼 읽힐 수 있는 표현을 고쳤고 Q215는 유지했다.
- Q139·214: [Scav Raiders](https://escapefromtarkov.fandom.com/wiki/Scav_Raiders)의
  기본 출현 맵과 D-2 전원·기차 도착에 따른 추가 출현 가능성을 대조했다.
  Q139는 대표 배치와 이벤트 예외를 구분했다. Q214는 이미 확률적 표현이라 유지했다.
- Q140: [BTR Driver](https://escapefromtarkov.fandom.com/wiki/BTR_Driver)의 서비스 대조.
  PMC 물품 반출과 플레이어 자신의 탈출을 구분하고 차량의 무조건적인 안전을 보장하지 않는다.
- Q165·166: [Zryachiy](https://escapefromtarkov.fandom.com/wiki/Zryachiy)와
  [Partisan](https://escapefromtarkov.fandom.com/wiki/Partisan)을 대조했다.
  Q165는 유지하고 Q166은 트립와이어·매복을 중심으로 설명해 숲만의 보스라는 함의를 피했다.
- Q210·216: [Rogues](https://escapefromtarkov.fandom.com/wiki/Rogues)의 집단 소개,
  [Knight](https://escapefromtarkov.fandom.com/wiki/Knight)와
  [Big Pipe](https://escapefromtarkov.fandom.com/wiki/Big_Pipe)의 구성원을 대조했다.
  Q210은 설정상의 지휘 관계와 실제 동시 배치를 구분하고 Q216은 유지했다.
  Rogues의 옛 수처리장 배치·USEC 우대 설명은 1.1.5.0 개편과 충돌하므로 채택하지 않았다.
- Q132·212·243: [Cultists](https://escapefromtarkov.fandom.com/wiki/Cultists)의 기본 행동·
  시간대·영문 이름을 대조했다. Q132는 유지했다. Q212·243은 일반 야간 무리로 범위를
  명시해 등대 섬 경비대나 이벤트 특수 AI까지 같은 규칙으로 취급하지 않도록 했다.
  [일본어 컬티스트 문서](https://wikiwiki.jp/eft/%E3%82%AB%E3%83%AB%E3%83%88)도 22~07시를
  기록하지만, 페이지 갱신일과 달리 표 자체의 기준은 Ver 1.0.0이다. 최신 실측 근거로 간주하지 않는다.
- Q213: [xTG-12](https://escapefromtarkov.fandom.com/wiki/XTG-12_antidote_injector),
  [Perfotoran](https://escapefromtarkov.fandom.com/wiki/Perfotoran_%28Blue_Blood%29_stimulant_injector),
  [Health system](https://escapefromtarkov.fandom.com/wiki/Health_system)을 대조했다.
  컬티스트 단검의 독에 대한 레이드 중 치료로 한정하고 진통·회복과 해독을 구분했다.
  분당 140 피해도 위키 기록에 있지만 치료 아이템 판별에는 불필요해 해설에서 제외했다.
  이는 해당 수치가 틀렸다고 판정한 것이 아니다. 다른 이벤트 독까지 치료된다고 확대하지 않는다.
- Q271: Cultists 및 [레드 키카드](https://escapefromtarkov.fandom.com/wiki/TerraGroup_Labs_keycard_%28Red%29)의
  획득처를 대조했다. 희귀 열쇠·키카드 획득 가능성과 확정 드롭을 구분했다.
  위키의 ‘any key’ 표현을 모든 퀘스트·이벤트 열쇠의 전수 검증으로 간주하지 않았다.
- Q340: [Events의 Kolotun 기록](https://escapefromtarkov.fandom.com/wiki/Events#Kolotun_(24_December_2025))을
  기준으로 2025년 12월 당시 문항임을 명시했다. 더 랩·더 래버린스가 제외된다는 기록을
  이후 모든 크리스마스 이벤트에 일반화하지 않는다. 보기 중 제외 맵은 더 랩 하나다.

보스·AI 30문항 모두 출처가 기록되었지만 최신 모드별 행동·출현 확률의 전수 실측이 아니다.
위키 직접 접근은 제한되어 약 2~3개월 전 검색 수집본을 사용했다. 최근 갱신된 일본어 문서도
내부 표의 기준 버전은 별도로 확인했다. 구조 테스트는 위 자료의 사실성을 자동 판정하지 않는다.

## 20차 — 하이드아웃 보너스·방어구 기준과 제품 구분

대상 23문항: Q8·9·20·23·24·32·35·37·40·43·69·78·101·103·105·111·113·120·142~145·173.
내용 수정은 Q8·23·24·32·35·37·43·69·78·101·120·142·144의 13문항이다.
나머지 10문항은 보기까지 대조한 뒤 내용을 유지하고 근거를 기록했다.
문항 수·ID·정답 인덱스·난이도·모드·카테고리는 그대로이며, 보기 문구 수정은 Q35·78·101·142뿐이다.

| 문항 | 판단과 반영 |
| --- | --- |
| Q8·24·32 | 전력 필수 기능과 예외, 반출한 물건의 보관과 사망 시 전리품 손실, 스캐브에게 비용을 내는 수집 의뢰를 구분. |
| Q144 | 도그태그 보너스의 직접 처치·상대 진영·전투 스킬 조건을 명시. 전시품 전체에 같은 효과가 있다고 일반화하지 않음. |
| Q43·69 | 방호 등급과 무방호 캐리어 Class 0, 피탄 부위 내구도와 원래 최대치를 구분. 수리 후 표시상 가득 찬 상태를 새 제품과 동일시하지 않음. |
| Q23·35·37 | Arena는 별도 게임. 사망 결과 화면을 리플레이와 구분하고, 0 XP 캐릭터 레벨을 개별 스킬 혜택과 구분. |
| Q78·101 | ‘사전 구매’로만 한정한 에디션 설명과 ‘진영 전용 장비’라는 모호한 표현을 수정. Steam의 Unheard 일부 외형 예외를 대조하되 전 의상 공용으로 확대하지 않음. |
| Q120 | ‘사실성 최우선’이라는 내부 설계 우선순위 단정 대신 개발사의 공개 설명을 묻도록 수정. |
| Q142 | 문샤인·인텔리전스 폴더 투입을 유지하고 가격 평가 표현은 제거. |

근거와 적용 범위:

- [Hideout](https://escapefromtarkov.fandom.com/wiki/Hideout): Q8·105·143·145의 기능과 예외.
  검색 수집본이 약 2개월 전이며, 건설 비용·제작 시간·근육통 수치는 새로 확정하지 않았다.
- [일본어 Hideout](https://wikiwiki.jp/eft/HIDEOUT): Q32·142 수집 의뢰 종류.
  최근 크롤링 표기만으로 표 전체가 최신이라고 보지 않고, 비용·소요시간은 문제에 넣지 않았다.
- [Character skills](https://escapefromtarkov.fandom.com/wiki/Character_skills): Q144 보너스 대상.
- [Looting](https://escapefromtarkov.fandom.com/wiki/Looting),
  [Key case](https://escapefromtarkov.fandom.com/wiki/Key_case),
  [Currency](https://escapefromtarkov.fandom.com/wiki/Currency): Q9·20·24·40·113 기본 개념.
  루블·달러·유로만 존재한다는 주장이나 최신 스태시 최대 크기 검증은 하지 않았다.
- [Armor vests](https://escapefromtarkov.fandom.com/wiki/Armor_vests),
  [Ballistics](https://escapefromtarkov.fandom.com/wiki/Ballistics): Q43·69의 분류·비교 기준.
  검색 수집본 기준이며 최신 패치의 전체 관통 계산식을 실측한 것은 아니다.
- [Physical Bitcoin](https://escapefromtarkov.fandom.com/wiki/Physical_Bitcoin): Q111 시세 연동 설명 유지.
  현재 판매가·연동 배율·갱신 주기는 확인하지 않았다.
- [Experience](https://escapefromtarkov.fandom.com/wiki/Experience),
  [Changelog](https://escapefromtarkov.fandom.com/wiki/Changelog): Q37 레벨 표와 Q35 사망 결과 화면.
  Q35는 2026-04-21·27의 처치자 표시 수정 기록을 대조했으며 현재 버그 유무 확인은 아니다.
- [공식 Arena 소개](https://t.me/s/escapefromtarkovEN?before=4538),
  [NVIDIA의 Arena 소개](https://www.nvidia.com/en-gb/geforce/news/reflex-escape-from-tarkov-arena/):
  Q23 별도 게임이라는 제품 구분만 확인. 현재 모드 구성·계정 진행도 연동 규칙은 검증하지 않았다.
- [공식 Steam 본편](https://store.steampowered.com/app/3932890/Escape_from_Tarkov/),
  [공식 Unheard Steam 설명](https://store.steampowered.com/app/4090980/Escape_from_Tarkov__The_Unheard_Steam_Edition_Expansion_Pack/),
  [초보자 가이드](https://escapefromtarkov.fandom.com/wiki/How_to_Play_Guide_for_Escape_from_Tarkov):
  Q78·101·120의 에디션·진영·전투 묘사. 공식 웹사이트 직접 열람은 403으로 실패했고 Steam을 대조했다.
- [Unity의 Battlestate 사례](https://unity.com/made-with-unity/escape-from-tarkov): Q103·120·173의
  친구 스쿼드·사실적 전투·개발 엔진. 오래된 개발 사례이므로 Unity 6 전환 완료 근거로 쓰지 않았다.

하이드아웃 29문항 모두 근거 기록이 생겼지만 최신 클라이언트 실측 완료는 아니다.
Q95 미니맵·Q102 킬피드는 검색 결과에 Arena·제3자 오버레이·오래된 가이드가 섞여 있어
현재 본편 UI 검증 근거로 채택하지 않았다. 이번에 내용이나 검토일을 바꾸지 않았으며
본편 일반 레이드의 화면 범위와 퀘스트 진행 알림 예외를 후속 검토해야 한다.
근거가 아직 없는 72문항은 스토리 42·맵 26·시스템 2·상인 2문항이다.

## 21차 — 세계관의 근거 수준과 스토리 목표·결말 구분

대상은 스토리 카테고리 42문항 전부다. 내용 변경 28문항:
Q76·77·79·99·100·174·297·300·301·303·305~309·342·344~346·348~356.
나머지 14문항은 보기·해설을 유지했다. 보기 문구 수정은 Q76·77·174·305·309·350뿐이다.
문항 수·ID·정답 인덱스·난이도·모드·카테고리는 보존했다.

| 범위 | 수정 이유 |
| --- | --- |
| Q79·100 | 베타 유형과 BEAR 음성의 예외를 바로잡음. |
| Q76·77·99·174·305~307·342·344~346 | 기업·조직·인력의 범위와 문서상 근거 수준을 명확히 하고, 위키 추론을 공식 확정 설정과 구분. |
| Q297·300·301·303·308·309 | 본편의 챕터와 별도 모드·에디션을 구분. Q303은 다른 보기의 지역도 방문하므로 코즐로프의 방으로 질문을 특정. 챕터 목록 순서가 필수 진행 순서는 아님. |
| Q348~350·356 | 결말의 서술·선택·재진행 조건·보상 종류를 구분하고 주관적인 최선 평가를 제거. |
| Q351~355 | 초기 조사 대상과 전체 챕터를 구분. 지도 목록을 보완하고 다른 챕터에서 이미 수행한 목표의 예외를 명시. |

대조한 자료:

- [공식 1.0 스토리 출시 영상](https://www.youtube.com/watch?v=Dd3MSNfRZ68),
  [Release dates](https://escapefromtarkov.fandom.com/wiki/Release_dates): Q79.
- [Tarkov](https://escapefromtarkov.fandom.com/wiki/Tarkov),
  [Tarkov conflict](https://escapefromtarkov.fandom.com/wiki/Tarkov_conflict),
  [공식 Raid 영상](https://www.youtube.com/watch?v=q9OIT7W24V8): Q1·3·77·168·175.
- [USEC](https://escapefromtarkov.fandom.com/wiki/USEC),
  [BEAR](https://escapefromtarkov.fandom.com/wiki/BEAR),
  [초보자 가이드](https://escapefromtarkov.fandom.com/wiki/How_to_Play_Guide_for_Escape_from_Tarkov):
  Q3·99·100·169~171·174·342~346. 세계관 배경과 음성만 대조했으며 구 Rogue 적대 규칙은 채택하지 않음.
- [TerraGroup](https://escapefromtarkov.fandom.com/wiki/TerraGroup): Q76·177·302·304~307.
  Q307은 2021년 티저에 관한 위키 해석이라는 한계를 유지한다.
- [Peacekeeper](https://escapefromtarkov.fandom.com/wiki/Peacekeeper),
  [Humanitarian Supplies](https://escapefromtarkov.fandom.com/wiki/Humanitarian_Supplies): Q298.
- [Story chapters](https://escapefromtarkov.fandom.com/wiki/Story_chapters),
  [일본어 스토리 목록](https://wikiwiki.jp/eft/%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AA%E3%83%BC%E3%82%BF%E3%82%B9%E3%82%AF):
  Q297·300·308. 영어 목록은 약 3개월 전 수집본이며 일본어 목록은 2026-09-21 수정 표시.
  두 목록이 일치하지만 전체 단계의 최신성 확인과는 구분한다.
- [They Are Already Here](https://escapefromtarkov.fandom.com/wiki/They_Are_Already_Here),
  [Accidental Witness](https://escapefromtarkov.fandom.com/wiki/Accidental_Witness),
  [The Unheard](https://escapefromtarkov.fandom.com/wiki/The_Unheard),
  [공식 Steam 에디션 설명](https://store.steampowered.com/app/4090980/Escape_from_Tarkov__The_Unheard_Steam_Edition_Expansion_Pack/):
  Q177·301·303·309. 에디션의 현재 최고 등급·구매 권장 여부는 묻지 않는다.
- [Endings](https://escapefromtarkov.fandom.com/wiki/Endings),
  [The Ticket](https://escapefromtarkov.fandom.com/wiki/The_Ticket),
  [일본어 The Ticket](https://wikiwiki.jp/eft/%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AA%E3%83%BC%E3%82%BF%E3%82%B9%E3%82%AF/The%20Ticket):
  Q299·347~350·355·356. 모드별 돈·처치 수량·연락 대기시간이 다른 자료는 최신값으로 확정하지 않음.
- [Falling Skies](https://escapefromtarkov.fandom.com/wiki/Falling_Skies),
  [Batya](https://escapefromtarkov.fandom.com/wiki/Batya),
  [Boreas](https://escapefromtarkov.fandom.com/wiki/Boreas),
  [Blue Fire](https://escapefromtarkov.fandom.com/wiki/Blue_Fire): Q351~355.

영문 위키의 상당수는 약 2~3개월 전 검색 수집본이다. 구 Prestige 문서는 여전히 PvP 전용으로
설명하고 있으므로 Q350의 현재 모드 제한이나 요구조건 검증 근거로 채택하지 않았다.
모든 프로필에서 바로 초기화·프레스티지를 쓸 수 있다고 보장하지 않는다.
Q100·309에 변동형 표시를 추가했고, 스토리 42문항 모두 근거를 기록했다.
21차 시점의 미기록 30문항은 맵 26·시스템 2·상인 2문항이었다. 출처 기록이 전체 실게임 검증을 뜻하지 않는다.

## 22차 — 맵 출입·탈출·열쇠 효과와 보스 목록의 범위

대상: Q14·16·81~86·98·119·128·129·131·269·270·287·288·333·444·445.
20문항 중 17문항의 내용을 보완했다. Q82·84·131은 내용 유지 후 근거만 추가했다.

- Q14: 조건을 충족한 탈출과 다른 맵으로의 트랜짓을 구분했다. 실제 탈출 지점 이름과
  혼동할 수 있는 '국경 검문소' 오답 보기를 제거했다.
  [플레이 가이드](https://escapefromtarkov.fandom.com/wiki/How_to_Play_Guide_for_Escape_from_Tarkov),
  [맵 목록](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov).
- Q16: 여러 장르 표기가 공존하는 문제를 피하려고 전리품 확보·탈출의 핵심 진행 구조를 묻고
  MMORPG 오답 보기를 교체했다. 공식 [Steam 소개](https://store.steampowered.com/app/3932890/Escape_from_Tarkov/)의
  extraction FPS 설명을 근거로 삼았으며 사용자 태그만으로 장르를 단정하지 않았다.
- Q81·129: 2층·3층 기숙사 구역과 3층 건물 314호를 명확히 했다. 모든 마킹룸을
  일반화하지 않고 314호 문·열쇠·가능한 전리품을 묻는다. 특정 드롭은 보장하지 않는다.
  [314호 열쇠](https://escapefromtarkov.fandom.com/wiki/Dorm_room_314_marked_key).
- Q83·85·86: 팩토리의 '가장 좁고 교전이 가장 빠르다'는 비교를 화학 공장 배경으로 바꿨다.
  요양원과 해변 위치의 혼동, 그라운드 제로의 저레벨 전용이라는 오해를 피하도록
  [Factory](https://escapefromtarkov.fandom.com/wiki/Factory),
  [Shoreline](https://escapefromtarkov.fandom.com/wiki/Shoreline),
  [Ground Zero](https://escapefromtarkov.fandom.com/wiki/Ground_Zero)의 지명·시설을 사용했다.
- Q98: 모든 탈출구에 스킬 조건이 없다는 단정 대신 차량 탈출과 Sewer Manhole·D-2의
  세 가지 조건을 비교한다. [플레이 가이드](https://escapefromtarkov.fandom.com/wiki/How_to_Play_Guide_for_Escape_from_Tarkov),
  [Reserve](https://escapefromtarkov.fandom.com/wiki/Reserve).
- Q128·269·270: Tour는 맵 선택 화면의 직접 입장 해금이며 초기 트랜짓과 구분된다.
  입장 카드는 분대원마다 필요하고 연습·협동 연습에서는 소모되지 않는 예외를 명시했다.
  입장 면제 이벤트를 일반 규칙과 섞지 않는다.
  [The Lab](https://escapefromtarkov.fandom.com/wiki/The_Lab),
  [Access keycard](https://escapefromtarkov.fandom.com/wiki/TerraGroup_Labs_access_keycard).
- Q287: 주차장 탈출 방송을 꺼도 레이더가 출현할 수 있다.
  [Yellow keycard](https://escapefromtarkov.fandom.com/wiki/TerraGroup_Labs_keycard_%28Yellow%29).
- Q119·288·333: 맵·키 목록의 부재와 세계관 전체의 부재를 구분했다. 원자로 제어실
  열쇠가 목록에 없다는 사실로 랩에 원자로 자체가 없다고 단정하던 해설을 제거했다.
  [맵 목록](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov),
  [랩 열쇠 목록](https://escapefromtarkov.fandom.com/wiki/The_Lab).
- Q444·445: 인터체인지 보스 목록과 매번 동시 출현을 구분했다. 랩의 기본 NPC 배치를
  묻되 모든 모드의 적 전체가 레이더뿐이라는 오답 소지가 있는 '레이더만' 표현을 제거했다.
  [Interchange](https://escapefromtarkov.fandom.com/wiki/Interchange),
  [The Lab](https://escapefromtarkov.fandom.com/wiki/The_Lab).

Steam 소개는 당일 공개 페이지를 확인했다. 나머지 위키는 직접 접근 제한 때문에 약 2개월 전
검색 수집본을 사용했다. 이 자료만으로 9월 최신 모드별 배치·소모 규칙의 실측을 완료했다고
표시하지 않는다. Q98·119·128·129에 변동형 표시를 추가했다.
22차 시점의 미기록 10문항은 Q95·102(UI), Q225·226(매입 배율), Q439~443·446(맵 시간·인원)이었다.
맵 수치·배율은 오래된 표에 날짜만 붙여 최신 확정값처럼 취급하지 않고 추가 검증 대상으로 남긴다.

## 23차 — PMC 제한 시간과 PvP 매칭 정원 구분 (2026-09-23)

Q439~443·446의 지문·해설과 출처를 수정했다. 정답 인덱스·보기·난이도는 유지했다.
일본어 위키 공개 표를 추가 대조했으나 사이트 수집일·페이지 수정일이 최신 게임 실측일을
보장하지는 않는다. 특히 영문 위키는 약 2개월 전 검색 수집본이다.

- Q439·440·443: 기본 PMC 제한 시간으로 범위를 명시하고 이벤트·시간 변경 모디파이어와
  Scav 합류 시 남은 시간을 구분했다. 팩토리 해설의 전체 맵 최단 단정과 컬티스트 확정 출현
  소지가 있는 설명은 제거했다. 쇼어라인 45분, 팩토리 주간 20분·야간 25분, 커스텀즈 35분 및
  Q443 오답 맵의 값은 두 위키 표에서 일치했다.
- Q441·446: 실제 참가·생존 인원이 아니라 PvP PMC 매칭 정원의 상한을 비교한다.
  스트리트 16명과 주간 팩토리 8명을 각 보기 안에서 비교한다. PvE는 타 플레이어 대신
  AI PMC가 등장한다는 [게임 모드 설명](https://escapefromtarkov.fandom.com/wiki/Game_modes)에 근거해,
  이 두 문항을 PvP 전용으로 분류했다. 이는 맵 표 자체가 모든 모드의 정원을 검증했다는
  주장이 아니라 PvE 협동 인원과 혼동하지 않기 위한 문항 분류 판단이다.
- Q442: 터미널의 PMC 1~5명과 쇼어라인 트랜짓 경로로 대상을 특정했다. 다른 맵의 PvP 정원과
  터미널의 참가 규모를 한꺼번에 비교하던 해설은 제거했다. 인원은 AI·민간인의 총수를 뜻하지 않는다.
  1~5명 수치는 [영문 Terminal](https://escapefromtarkov.fandom.com/wiki/Terminal)에만 근거하며,
  [일본어 Terminal](https://wikiwiki.jp/eft/TERMINAL)은 경로의 보조 근거일 뿐 인원 독립 검증은 아니다.

교차 대조 자료:

- [Shoreline](https://wikiwiki.jp/eft/SHORELINE), [Factory](https://wikiwiki.jp/eft/FACTORY),
  [Customs](https://wikiwiki.jp/eft/CUSTOMS): 제한 시간과 주간 팩토리 정원.
- [Streets](https://wikiwiki.jp/eft/STREETS%20OF%20TARKOV),
  [Interchange](https://wikiwiki.jp/eft/INTERCHANGE), [Lighthouse](https://wikiwiki.jp/eft/LIGHTHOUSE),
  [Reserve](https://wikiwiki.jp/eft/RESERVE), [Ground Zero](https://wikiwiki.jp/eft/GROUND%20ZERO): 비교 대상 맵 표.
- [영문 맵 목록](https://escapefromtarkov.fandom.com/wiki/Map_of_Tarkov),
  [The Lab](https://escapefromtarkov.fandom.com/wiki/The_Lab): PMC 인원·시간 표.

확정하지 않은 내용:

- 인터체인지는 영문 11~15명과 일본어 10~14명이 충돌한다. 어느 쪽도 스트리트 상한 16명보다
  크지 않아 Q441 정답은 같지만 정확한 인터체인지 인원은 해설에서 제외했다.
- 팩토리는 영문 표가 주·야간 인원을 구분하지 않고 7~8명으로 표기하는 반면 일본어 표는
  주간 7~8명·야간 5~6명으로 구분한다. Q446은 두 표가 일치하는 주간만 사용했다.
- 그라운드 제로 고레벨 인원 구분은 영문에 있으나 일본어 표에는 없다. 이 세부 값도
  확정하지 않았다. 두 표의 상한 모두 주간 팩토리보다 크므로 Q446 정답은 변하지 않는다.
- 공개 Tarkov.dev GraphQL은 스키마·맵 이름 조회 모두 HTTP 422와
  `GraphQL server unavailable. Try again later.`를 반환했다. 최신 서버 설정을 받지 못했다.
- Q225·226: 일본어 상인 문서도 제거된 거래량 LL 조건을 여전히 포함하고 있어 최신 배율 근거로
  채택하지 않았다. 공식 1.1.0의 매입가 평균 20% 감소는 각 배율에 일괄 0.8을 곱할 근거가 아니다.
  두 문항은 현재 값 확인 전이며, 검토일·근거 필드를 새로 붙여 완료 처리하지 않았다.

맵 34문항 모두 근거 기록이 생겼지만 최신 모드별 클라이언트 실측 완료는 아니다.
남은 미기록 문항은 Q95·102·225·226이다. 변동형 290문항과 기존 미확인 목록은 유지한다.

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

1. Q410(PvE 업적 표시 버그), Q429(Intellect 미작동): 과거 기록 문항으로 수정했지만
   현재 재현·수정 여부는 여전히 미확인이다. 현재 상태 문항으로 되돌리려면 새 근거가 필요하다.
2. Q29·157의 기존 설명 오류는 2차에서 수정했다. 근거가 검색 수집본이라는 한계는 남으며,
   최신 클라이언트 실측 완료로 간주하지 않는다.
3. Q151·163·209·225~226·269·310~324·367·369 등 해금·상인·퀘스트 조건:
   1.1.0 재편과 Lighthouse 퀘스트 개편 이후의 게임 화면 또는 최신 자료 대조 필요.
   Q164의 세부 조건도 여기에 포함한다.
   Q314의 ‘모든 맵’ 표현은 고쳤지만 최신 대상 맵·선행 조건까지 확인한 것은 아니다.
   3차의 Q151·163·312·318·322·324 보완도 세부 최신 수치의 실측 완료는 아니다.
   16차에서 Q311의 구 목표와 Q315의 명칭을 보완했다. Q315·317의 처치 수량 충돌,
   Q319의 인정 지역, Q321의 진영별 수량, Q323의 모드·이벤트 원복은 여전히 미확인이다.
   17차에서 Q367의 상인 7명·펜스 평판 및 Q369의 프라포르 LL1 판매를 공개 자료와 대조했다.
   Q367의 전체 해금 조건이나 Q369의 가격·구매 한도까지 검증한 것은 아니다.
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
- 3차는 회귀 테스트 3개 추가 후 전체 141개 통과. 문제 형식 검사·Ruff·변경 테스트 컴파일 통과.
- 4차는 회귀 테스트 3개 추가 후 전체 144개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. 출처 기록 72개·변동형 204개와 양쪽 README 수량 일치.
- 5차는 회귀 테스트 3개 추가 후 전체 147개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. 근거 기록 104개·변동형 221개와 양쪽 README 수량 일치.
- 6차는 회귀 테스트 3개 추가 후 전체 150개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. 근거 기록 132개·변동형 230개와 양쪽 README 수량 일치.
  변경 전후 JSON 비교로 28문항만 변경됨과 ID·정답 인덱스·난이도·모드·카테고리 보존을 확인했다.
- 7차는 회귀 테스트 3개 추가 후 전체 153개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. 근거 기록 147개·변동형 231개와 양쪽 README 수량 일치.
  변경 전후 JSON 비교로 15문항만 변경됨과 ID·정답 인덱스·난이도·모드·카테고리 보존을 확인했다.
  의료·식량 44문항 모두에 근거 기록이 생겼지만 테스트는 실제 게임 사실성을 판정하지 않는다.
- 8차는 회귀 테스트 4개 추가 후 전체 157개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. 근거 기록 174개·변동형 239개와 양쪽 README 수량 일치.
  장비 27문항의 근거를 추가하고 20문항의 내용을 보완했다. Q289의 정답 인덱스는 0에서 2로 수정했다.
  의료·식량 44문항과 장비 33문항 모두 근거가 있지만 최신 게임 실측 완료를 뜻하지 않는다.
- 9차는 회귀 테스트 3개 추가 후 전체 160개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. 근거 기록 188개·변동형 242개와 양쪽 README 수량 일치.
  JSON 전후 비교로 변경 문항 14개 및 문항 수·ID·정답 인덱스·난이도·모드·카테고리 보존 확인.
  600회 세션 추출 검사는 전체 테스트에 포함되며, 별도 임시 DB 부하 검사는 이번 차수에 재실행하지 않았다.
- 10차는 회귀 테스트 3개 추가 후 전체 163개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. 근거 기록 214개·변동형 242개와 양쪽 README 수량 일치.
  JSON 전후 비교로 26문항만 변경됨과 문항 수·ID·정답 인덱스·난이도·모드·카테고리 보존 확인.
  600회 세션 추출 검사는 전체 테스트에 포함된다. 별도 임시 DB 부하 검사는 이번 차수에 재실행하지 않았다.
- 11차는 회귀 테스트 3개 추가 후 전체 166개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. 근거 기록 222개·변동형 243개와 양쪽 README 수량 일치.
  JSON 전후 비교로 8문항만 변경됨과 문항 수·ID·정답 인덱스·난이도·모드·카테고리 보존 확인.
  무기 53문항 모두 근거 기록이 생겼지만 최신 클라이언트 실측 완료를 뜻하지 않는다.
  600회 세션 추출 검사는 전체 테스트에 포함된다. 별도 임시 DB 부하 검사는 이번 차수에 재실행하지 않았다.
- 12차는 회귀 테스트 3개 추가 후 전체 169개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. 근거 기록 241개·변동형 244개와 양쪽 README 수량 일치.
  JSON 전후 비교로 19문항만 변경됨(내용 변경 17개)과 문항 수·ID·정답 인덱스·난이도·모드·카테고리 보존 확인.
  600회 세션 추출 검사는 전체 테스트에 포함된다. 별도 임시 DB 부하 검사는 이번 차수에 재실행하지 않았다.
- 13차는 회귀 테스트 3개 추가 후 전체 172개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. 근거 기록 266개·변동형 244개와 양쪽 README 수량 일치.
  JSON 전후 비교로 25문항만 변경됨과 문항 수·ID·보기·정답 인덱스·난이도·모드·카테고리·volatile 보존 확인.
  600회 세션 추출 검사는 전체 테스트에 포함된다. 별도 임시 DB 부하 검사는 이번 차수에 재실행하지 않았다.
- 14차는 회귀 테스트 3개 추가 후 전체 175개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. 근거 기록 288개·변동형 247개와 양쪽 README 수량 일치.
  JSON 전후 비교로 22문항만 변경됨(내용 변경 15개)과 문항 수·ID·정답 인덱스·난이도·모드·카테고리 보존 확인.
  600회 세션 추출 검사는 전체 테스트에 포함된다. 별도 임시 DB 부하 검사는 이번 차수에 로컬 재실행하지 않았다.
- 15차는 회귀 테스트 3개 추가 후 전체 178개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. 근거 기록 323개·변동형 251개와 양쪽 README 수량 일치.
  JSON 전후 비교로 35문항만 변경됨(내용 변경 16개)과 문항 수·ID·정답 인덱스·난이도·모드·카테고리 보존 확인.
  보기 문장의 병렬 표현을 다듬은 뒤 해당 문항 테스트와 형식 검사를 재실행했다.
  600회 세션 추출 검사는 전체 테스트에 포함된다. 별도 임시 DB 부하 검사는 이번 차수에 로컬 재실행하지 않았다.
- 16차는 회귀 테스트 3개 추가 후 전체 181개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. 근거 기록 334개·변동형 252개와 양쪽 README 수량 일치.
  JSON 전후 비교로 11문항만 변경됨(내용 변경 8개)과 문항 수·ID·정답 인덱스·난이도·모드·카테고리 보존 확인.
  600회 세션 추출 검사는 전체 테스트에 포함된다. 별도 임시 DB 부하 검사는 이번 차수에 로컬 재실행하지 않았다.
- 17차는 회귀 테스트 3개 추가 후 전체 184개 통과. 테스트 줄 길이 1곳 수정 후 Ruff·해당
  테스트 63개·컴파일을 재실행해 통과했다. 464문항 형식 검사·`git diff --check`도 통과.
  근거 기록 342개·변동형 252개와 양쪽 README 수량 일치. JSON 전후 비교로 8문항만
  변경됨과 문항 수·ID·정답 인덱스·난이도·모드·카테고리·volatile 여부 보존 확인.
  600회 세션 추출 검사는 전체 테스트에 포함된다. 별도 임시 DB 부하 검사는 이번 차수에 로컬 재실행하지 않았다.
- 18차는 회귀 테스트 3개 추가 후 전체 187개 통과. 관련 Blackout 맵 문항 2개까지 보완한
  최종 상태에서 전체 테스트·464문항 형식 검사·Ruff·변경 테스트 컴파일을 다시 실행했다.
  JSON 전후 비교로 12문항만 변경됨(내용 변경 9개)과 문항 수·ID·보기·정답 인덱스·난이도·모드·
  카테고리 보존 확인. 근거 기록 354개·변동형 261개와 양쪽 README 수량 일치.
  600회 세션 추출 검사는 전체 테스트에 포함된다. 임시 DB 합성 부하도 로컬 재실행해
  8,500명·25,500회 완주·동시 조회 200회·세션 상한 250개 및 초과 거절 검사를 통과했다.
  통계·랭킹·히든 후보 약 0.09초, 동시 랭킹 조회 약 0.20초이며 운영 성능 보장값은 아니다.
- 19차는 회귀 테스트 4개 추가 후 전체 191개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. JSON 전후 비교로 15문항만 변경됨(내용 변경 10개),
  정답 보기 문구 변경은 Q166·271뿐이며 문항 수·ID·정답 인덱스·난이도·모드·카테고리 보존 확인.
  근거 기록 369개·변동형 270개와 양쪽 README 수량 일치. 보스·AI 30문항 모두 근거 기록.
  600회 세션 추출 검사는 전체 테스트에 포함된다. 별도 임시 DB 부하 검사는 이번 차수에
  로컬 재실행하지 않았으며 18차 결과와 구분한다.
- 20차는 회귀 테스트 4개 추가 후 전체 195개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. JSON 전후 비교로 23문항만 변경됨(내용 변경 13개),
  보기 문구 수정은 Q35·78·101·142뿐이며 문항 수·ID·정답 인덱스·난이도·모드·카테고리 보존 확인.
  근거 기록 392개·변동형 284개와 양쪽 README 수량 일치. 하이드아웃 29문항 모두 근거 기록.
  보관 위치 표현과 원문 수집 시점 메모를 다듬은 뒤 문항 테스트 74개·형식 검사를 재실행했다.
  600회 세션 추출 검사는 전체 테스트에 포함된다. 별도 임시 DB 부하 검사는 이번 차수에
  로컬 재실행하지 않았으며 18차 결과와 구분한다.
- 21차는 회귀 테스트 5개 추가 후 전체 200개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. JSON 전후 비교로 스토리 42문항만 변경됨(내용 변경 28개),
  보기 문구 수정은 Q76·77·174·305·309·350뿐이며 문항 수·ID·정답 인덱스·난이도·모드·카테고리 보존 확인.
  근거 기록 434개·변동형 286개와 양쪽 README 수량 일치. 분대 표식 표현을 다듬은 뒤
  문항 테스트 79개·형식 검사를 재실행했다. 600회 세션 추출 검사는 전체 테스트에 포함된다.
  별도 임시 DB 부하 검사는 이번 차수에 로컬 재실행하지 않았다.
- 22차는 회귀 테스트 5개 추가 후 전체 205개 통과. 최초 실행에서는 README의 검토 수량이
  이전 값인 점을 기존 문서 정합성 테스트가 검출했다. 양쪽 README 갱신 후 전체를 재실행했다.
  464문항 형식 검사·Ruff·변경 테스트 컴파일·`git diff --check` 통과.
  JSON 전후 비교로 20문항만 변경됨(내용 변경 17개), 보기 문구 수정은 Q14·16·98·129·445뿐이며
  문항 수·ID·정답 인덱스·난이도·모드·카테고리 보존 확인. 근거 기록 454개·변동형 290개와
  양쪽 README 수량 일치. 600회 세션 추출 검사는 전체 테스트에 포함된다.
  별도 임시 DB 부하 검사는 이번 차수에 로컬 재실행하지 않았다.
- 23차는 회귀 테스트 3개 추가 후 전체 208개 통과. 464문항 형식 검사·Ruff·변경 테스트
  컴파일·`git diff --check` 통과. JSON 전후 비교로 6문항만 변경되고 보기·정답·난이도·
  카테고리·volatile 보존 확인. 모드 변경은 Q441·446의 common→pvp뿐이다.
  양쪽 README의 공통 449·PvP 13·PvE 2, 출제 가능 PvP 462·PvE 451, 근거 460·변동형 290과
  실제 데이터 일치 확인. 600회 세션 추출 검사도 통과했다. 별도 임시 DB 부하 검사는 이번 차수에
  로컬 재실행하지 않았다.
- Ruff·Python 컴파일·464문항 형식 검사 통과.
- PvP/PvE 각각 300회 추출에서 난이도 수량·ID 중복·모드 격리 검사 통과.
- 임시 DB의 8,500명·25,500회 응시, 동시 랭킹 조회 200회,
  동시 세션 250개와 초과 시작 거절 검사 통과.
  3차에서도 동일한 임시 DB 부하 검사를 재실행해 통과했다.
  4차 재실행도 통과했으며 통계·후보 조회 약 0.10초, 동시 랭킹 조회 약 0.22초였다.
  이 시간은 해당 로컬 실행 결과이지 운영 응답시간 보장값이 아니다.
  5차에서도 동일한 규모의 임시 DB·동시 조회·세션 상한 검사를 재실행해 통과했다.
  6차 재실행도 통과했으며 통계·후보 조회 약 0.10초, 동시 랭킹 조회 약 0.20초였다.

합성 부하는 Discord 실제 서버의 8,500명 동시 접속 검증이 아니다.
실게임 정답 검증과 소프트웨어 검증 결과는 구분한다.
