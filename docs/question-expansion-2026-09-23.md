# 문제 풀 확장 — 2026-09-23

## 변경 범위

10문항(Q465~Q474)을 추가하고 기존 2문항(Q26·405)을 수정했다.
총 474, 활성 470, 보류 4문항이다. 공통 459 / PvP 전용 13 / PvE 전용 2이며
실제 출제 가능 풀은 PvP 468 / PvE 457이다. 세션은 기존 30문제·1,380점 구성을 유지한다.

추가 난이도는 중간 3 / 어려움 6 / 고난이도 1이다. 숫자 순위 암기를 더 늘리지 않고,
고장 증상·수납 품목·신체 관통과 방호층을 구분하는 문항을 보강했다.
공통 게임 규칙에 관한 문항으로 두 모드에 모두 포함했다. 시즌 모디파이어별 확률은 묻지 않는다.

| 문항 | 확인한 내용 | 근거 |
|---|---|---|
| Q465~467 | 배출 불량, 탄창과 급탄 불량, 중간 과열 효과 | [Weapon malfunctions](https://escapefromtarkov.fandom.com/wiki/Weapon_malfunctions) |
| Q468 | 인젝터 케이스의 주사기·스팀 제한 | [Injector case](https://escapefromtarkov.fandom.com/wiki/Injector_case) |
| Q469~470 | 문서 케이스와 키 툴의 수납 대상 차이 | [Documents case](https://escapefromtarkov.fandom.com/wiki/Documents_case), [Key tool](https://escapefromtarkov.fandom.com/wiki/Key_tool) |
| Q471 | S I C C의 도그태그·금 해골 반지 수납 | [S I C C](https://escapefromtarkov.fandom.com/wiki/S_I_C_C_organizational_pouch) |
| Q472~473 | 한 탄환의 신체 관통, 방호층 통과 시 피해·관통력 손실 | [Ballistics](https://escapefromtarkov.fandom.com/wiki/Ballistics) |
| Q474 | 판과 소프트 아머의 보호 부위·등급 구분 | [Ballistics](https://escapefromtarkov.fandom.com/wiki/Ballistics), [Chest rigs](https://escapefromtarkov.fandom.com/wiki/Chest_rigs) |

Q26은 Q6의 단순 보존 개념 반복에서 일반 백팩 속 문서 케이스 사례로 변경했다.
[시큐어 컨테이너](https://escapefromtarkov.fandom.com/wiki/Secure_containers)의 보존 기능과
일반 수납 용기의 공간 절약 기능을 구분하고 보험 회수와 혼동하지 않게 했다.
Q405는 Q52의 관통 실패 설명 반복에서 방탄판 뒤 소프트 아머가 둔격 피해를 줄이는 사례로 변경했다.

## 근거의 한계

위키 검색 수집본은 약 2~3개월 전 자료다. 검토일은 최신 클라이언트 실측일이 아니다.
신규 문항 모두 출처·검토일·volatile 메모를 기록했다. Q474의 3등급/5등급 조합은 보호
부위와 방호층 표를 바탕으로 만든 가상 사례이며 특정 장비의 현행 제원을 주장하지 않는다.
고장 확률·상인 판매 조건·가격·수납 수량·업적 버그 등 미확인 최신 수치는 추가하지 않았다.

Q95·102·225·226의 보류 상태와 원문은 유지한다. volatile은 주의 표시일 뿐 자동 제외가 아니다.
이 기록은 이전 검수 기록을 대체하지 않는다. 운영 DB·스키마·실행 중 봇은 변경하지 않는다.
변경된 문제 풀을 실행 중 봇에 적용하려면 재시작이 필요하다.

## 검증 범위

회귀 테스트는 추가 10문항의 정답 인덱스·근거 필드·모드·난이도 구성을 검사한다.
기존 600회 세션 추출 검사는 30문제 수량·난이도 배분·모드 격리·ID 중복·보류 제외를 검사한다.
형식 검사나 테스트 통과 자체가 게임 내용의 사실성 또는 최신성을 증명하지는 않는다.

로컬 검증 결과: 전체 unittest 226개(추가 3개), 양 모드 600회 추출,
474문항 형식 검사, Ruff, 변경 테스트 Python 컴파일, git diff --check 통과.
JSON 전후 비교에서 기존 변경 ID는 Q26·405뿐이며 새 ID는 Q465~Q474이다.
DB 부하 검사는 이번 콘텐츠 수정에서 로컬 재실행하지 않았다.
