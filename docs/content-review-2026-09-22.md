# 콘텐츠·운영 문서 검수 기록 — 2026-09-22

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
- 모드: 공통 451 / PvP 11 / PvE 2. 공통 포함 PvP 462 / PvE 453.
- 근거를 기록한 문항: 132개(1차 20 + 2차 14 + 3차 19 + 4차 19 + 5차 32 + 6차 28).
  그 외 332개를 확인 완료로 표시하지 않는다.
- `volatile`: 230개(2차에서 5개, 4차에서 2개, 5차에서 17개, 6차에서 9개 추가). 이 표시는 **출제 제외가 아니다**.
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
