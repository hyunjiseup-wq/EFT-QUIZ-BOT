import json
import random
import tempfile
import unittest
from pathlib import Path

from config import SESSION_COUNTS
from question_bank import (
    QuestionDataError,
    filter_questions_for_mode,
    group_by_difficulty,
    load_questions,
    load_validated_questions,
    select_session_questions,
    validate_questions,
)


def make_question(qid: int, difficulty: str = "general") -> dict:
    return {
        "id": qid,
        "difficulty": difficulty,
        "category": "시스템",
        "question": f"문제 {qid}",
        "choices": ["정답", "오답 1", "오답 2", "오답 3"],
        "answer": 0,
        "explanation": "해설",
    }


class QuestionBankTests(unittest.TestCase):
    def test_practical_expansion_keeps_sources_scope_and_both_modes(self):
        questions = load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        new = [q for q in questions if 465 <= q["id"] <= 474]
        self.assertEqual({q["id"] for q in new}, set(range(465, 475)))
        for q in new:
            with self.subTest(qid=q["id"]):
                self.assertEqual(q["mode"], "common")
                self.assertTrue(q.get("enabled", True))
                self.assertEqual(q["reviewed_at"], "2026-09-23")
                self.assertTrue(q["sources"])
                self.assertTrue(q["volatile"])
                self.assertIn("검색 수집본", q["volatile_note"])
                self.assertIn("실측 검증은 아님", q["volatile_note"])
        self.assertEqual(
            {d: sum(q["difficulty"] == d for q in new) for d in SESSION_COUNTS},
            {"general": 0, "medium": 3, "hard": 6, "expert": 1},
        )
        for mode in ("pvp", "pve"):
            self.assertEqual(len(filter_questions_for_mode(new, mode)), 10)

    def test_practical_expansion_answer_indices_match_reviewed_meanings(self):
        questions = {q["id"]: q for q in load_questions(
            Path(__file__).resolve().parents[1] / "questions.json"
        )}
        expected = {
            465: "배출 불량", 466: "탄창", 467: "마모가 증가",
            468: "모르핀", 469: "도그태그", 470: "키카드도 수납",
            471: "금 해골 반지", 472: "여러 부위", 473: "일부 감소", 474: "3등급이다",
        }
        for qid, fragment in expected.items():
            with self.subTest(qid=qid):
                q = questions[qid]
                self.assertIn(fragment, q["choices"][q["answer"]])
        self.assertIn("별개", questions[472]["explanation"])
        self.assertIn("예시", questions[474]["explanation"])

    def test_repeated_concepts_now_use_different_application_scenarios(self):
        questions = {q["id"]: q for q in load_questions(
            Path(__file__).resolve().parents[1] / "questions.json"
        )}
        self.assertIn("일반 백팩", questions[26]["question"])
        self.assertIn("보험 회수 여부는 별개", questions[26]["explanation"])
        self.assertIn("소프트 아머가 한 겹 더", questions[405]["question"])
        self.assertIn("항상 체력 피해 0", questions[405]["explanation"])
        for qid in (26, 405):
            self.assertEqual(questions[qid]["reviewed_at"], "2026-09-23")

    def test_real_bank_600_sessions_keep_difficulty_counts_unique_ids_and_mode_isolation(self):
        questions = load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        self.assertEqual(validate_questions(questions, SESSION_COUNTS), [])
        rng = random.Random(20260922)
        total = sum(SESSION_COUNTS.values())
        for mode in ("pvp", "pve"):
            pool = group_by_difficulty(filter_questions_for_mode(questions, mode))
            for draw in range(300):
                with self.subTest(mode=mode, draw=draw):
                    selected = select_session_questions(pool, SESSION_COUNTS, rng=rng)
                    self.assertEqual(len(selected), total)
                    self.assertEqual(len({q["id"] for q in selected}), total)
                    self.assertTrue(all(q.get("enabled", True) is True for q in selected))
                    self.assertTrue({95, 102, 225, 226}.isdisjoint(q["id"] for q in selected))
                    self.assertTrue(
                        all(q.get("mode", "common") in {"common", mode} for q in selected)
                    )
                    for difficulty, count in SESSION_COUNTS.items():
                        self.assertEqual(
                            sum(q["difficulty"] == difficulty for q in selected), count
                        )

    def test_review_metadata_is_optional_but_requires_date_and_https_sources_together(self):
        question = make_question(1)
        self.assertEqual(validate_questions([question], {"general": 1}), [])
        reviewed = {
            **question,
            "reviewed_at": "2026-09-22",
            "sources": ["https://telegra.ph/Patch-1151-09-15-2"],
        }
        self.assertEqual(validate_questions([reviewed], {"general": 1}), [])
        for field in ("reviewed_at", "sources"):
            with self.subTest(missing=field):
                incomplete = {key: value for key, value in reviewed.items() if key != field}
                self.assertTrue(validate_questions([incomplete], {"general": 1}))

    def test_review_metadata_rejects_invalid_dates_and_sources(self):
        reviewed = {
            **make_question(1),
            "reviewed_at": "2026-09-22",
            "sources": ["https://telegra.ph/Patch-1151-09-15-2"],
        }
        for value in (None, True, 20260922, "2026-02-30", "22/09/2026", "20260922"):
            with self.subTest(date=value):
                errors = validate_questions([{**reviewed, "reviewed_at": value}], {"general": 1})
                self.assertTrue(any("reviewed_at" in error for error in errors))
        for value in (
            None, [], "https://example.com", [42], [""], ["http://example.com"],
            ["https:///missing-host"], ["https://[bad"], ["https://user:secret@example.com"],
            ["https://example.com/with space"],
        ):
            with self.subTest(sources=value):
                errors = validate_questions([{**reviewed, "sources": value}], {"general": 1})
                self.assertTrue(any("sources" in error for error in errors))

    def test_september_patch_questions_keep_corrected_scope_and_provenance(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        # 회귀 검사는 원전의 사실성을 증명하지 않는다. 검토한 수정 범위만 고정한다.
        expected_answer_fragments = {
            44: "사격", 80: "대상 캐릭터", 138: "로그", 164: "볼트액션",
            211: "두 진영", 242: "가까이", 244: "거치 화기와 지뢰 제거",
            273: "12.7x108mm", 339: "타길라의 그림자", 403: "경향",
            406: "플레이트 캐리어", 450: "보상 해금", 457: "Arena에서",
            459: "시즌 캐릭터", 460: "집계에서는 제외", 461: "25명·15명·10명",
            462: "수리 키트", 463: "Fence·Ref", 464: "방어 성능 제거",
        }
        for qid, fragment in expected_answer_fragments.items():
            with self.subTest(qid=qid):
                question = questions[qid]
                self.assertIn(fragment, question["choices"][question["answer"]])
                self.assertEqual(question["reviewed_at"], "2026-09-22")
                self.assertTrue(question["sources"])
        self.assertIn("Power Station", questions[130]["question"])
        self.assertIn("전술 의상", questions[457]["explanation"])
        self.assertIn("장비 상자 교환에는 사용할 수 없습니다", questions[450]["explanation"])
        self.assertNotIn("10~15%", questions[403]["choices"][0])
        pve_ids = {q["id"] for q in filter_questions_for_mode(list(questions.values()), "pve")}
        self.assertTrue({459, 460, 461}.isdisjoint(pve_ids))
        self.assertTrue({462, 463, 464}.issubset(pve_ids))

    def test_revalidated_questions_keep_current_answer_and_bounded_scope(self):
        questions_path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {question["id"]: question for question in load_questions(questions_path)}

        painkiller = questions[413]
        self.assertEqual(painkiller["choices"][painkiller["answer"]], "골든 스타 밤")

        terminal = questions[442]
        self.assertIn("제시된 네 맵 중", terminal["explanation"])

        smallest_map = questions[446]
        self.assertTrue(smallest_map["question"].startswith("다음 네 맵 중"))
        self.assertEqual(smallest_map["choices"][smallest_map["answer"]], "팩토리")

    def test_exception_corrections_keep_scope_and_sources(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        # 원전 사실성 자동 검증이 아니라 이번에 고친 예외·범위의 회귀 방지다.
        question_scopes = {
            29: "귀", 41: "비배신자", 61: "호환 헬멧", 94: "1칸(1x1)",
            156: "팔·다리·복부", 157: "총탄의 직접 피해", 438: "매칭",
        }
        for qid, scope in question_scopes.items():
            with self.subTest(qid=qid):
                self.assertIn(scope, questions[qid]["question"])
        for qid in (29, 41, 61, 94, 118, 156, 157, 220, 314, 389, 390, 415, 424, 438):
            with self.subTest(provenance=qid):
                self.assertEqual(questions[qid]["reviewed_at"], "2026-09-22")
                self.assertTrue(questions[qid]["sources"])
        for fragment in ("은신처 제작품", "퀘스트 보상", "Run Through"):
            self.assertIn(fragment, questions[118]["explanation"])
        self.assertIn("출혈", questions[157]["explanation"])
        self.assertIn("퀘스트에 지정된", questions[314]["choices"][questions[314]["answer"]])
        self.assertNotIn("카파 필수", questions[314]["explanation"])
        self.assertIn("최고 레벨 구성원", questions[438]["explanation"])

    def test_malfunction_questions_ask_boundaries_not_overlapping_ranges(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        for qid, scope, answer in ((389, "경계값", "93"), (390, "상한", "5%")):
            with self.subTest(qid=qid):
                question = questions[qid]
                self.assertIn(scope, question["question"])
                self.assertEqual(question["choices"][question["answer"]], answer)
                self.assertTrue(question["volatile"])
                for choice in question["choices"]:
                    self.assertNotIn("초과", choice)
                    self.assertNotIn("이하", choice)

    def test_medical_questions_compare_one_measure_only(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        comparison = questions[415]
        self.assertIn("1회 사용당 최대 HP 회복량", comparison["question"])
        self.assertEqual(comparison["choices"][comparison["answer"]], "85 → 60")
        self.assertEqual(len(set(comparison["choices"])), 4)
        for choice in comparison["choices"]:
            self.assertRegex(choice, r"^\d+ → \d+$")
        surgery = questions[424]
        self.assertIn("최대 HP 감소 페널티", surgery["choices"][surgery["answer"]])
        self.assertNotIn("완전한 체력으로 복구", surgery["explanation"])

    def test_quest_actions_distinguish_equipment_planting_and_hand_over(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        expected_answers = {
            149: "확인한 뒤", 155: "인코딩된", 163: "MP 계열 산탄총",
            312: "제출하기", 318: "4개", 324: "114호",
        }
        for qid, fragment in expected_answers.items():
            with self.subTest(qid=qid):
                question = questions[qid]
                self.assertIn(fragment, question["choices"][question["answer"]])
        self.assertIn("설치", questions[318]["question"])
        self.assertIn("FIR 수집·반납 과제가 아니며", questions[318]["explanation"])
        self.assertIn("직접 열 때", questions[324]["question"])
        self.assertIn("별도 조작", questions[149]["explanation"])
        self.assertIn("장착", questions[155]["explanation"])

    def test_progression_questions_keep_baseline_and_expansion_scope(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        self.assertIn("기본 규칙", questions[151]["question"])
        self.assertIn("판매글", questions[151]["question"])
        self.assertNotIn("레벨 제한이 전혀 없다", questions[152]["choices"])
        self.assertIn("최고 레벨", questions[152]["explanation"])
        self.assertIn("추가 줄 수", questions[374]["question"])
        self.assertIn("총 크기가 80줄이라는 뜻은 아닙니다", questions[374]["explanation"])
        self.assertIn("일부 재료", questions[370]["explanation"])
        for qid in (365, 366):
            self.assertIn("Kord Breach", questions[qid]["question"])
        self.assertNotIn("상인 LL4", questions[322]["explanation"])

    def test_third_review_batch_keeps_source_records_and_modes(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        qids = (
            71, 149, 151, 152, 153, 155, 163, 312, 318, 322, 324,
            364, 365, 366, 368, 370, 373, 374, 375,
        )
        for qid in qids:
            with self.subTest(qid=qid):
                question = questions[qid]
                self.assertEqual(question["reviewed_at"], "2026-09-22")
                self.assertTrue(question["sources"])
                expected_mode = "pvp" if qid in {364, 365, 366, 375} else "common"
                self.assertEqual(question.get("mode", "common"), expected_mode)

    def test_hideout_questions_disambiguate_facilities_and_bonus_scope(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        # 검토한 문구·예외가 사라지지 않는지 검사할 뿐 웹 내용의 사실성 검사는 아니다.
        self.assertIn("프로필", questions[7]["explanation"])
        self.assertIn("의료품 제작", questions[47]["question"])
        self.assertIn("휴식 공간에도", questions[47]["explanation"])
        self.assertIn("화폐 보상", questions[67]["choices"][questions[67]["answer"]])
        self.assertIn("Physical", questions[72]["choices"][questions[72]["answer"]])
        self.assertIn("FP-100", questions[72]["explanation"])
        for qid in (104, 160):
            self.assertIn("3레벨", questions[qid]["question"])
        self.assertIn("장착해 채굴", questions[110]["question"])
        self.assertIn("부즈 제너레이터", questions[162]["question"])
        self.assertIn("최소값 조합", questions[337]["question"])
        self.assertIn("Combat", questions[338]["explanation"])
        self.assertIn("추가 보정을 제외", questions[380]["question"])
        self.assertIn("청소로 완화하지 않은", questions[381]["question"])

    def test_crafting_questions_keep_power_exceptions_and_baseline_comparison(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        crafting = questions[417]
        self.assertIn("지속 전력 요구 특수 제작", crafting["question"])
        self.assertIn("비트코인 채굴 제외", crafting["question"])
        self.assertIn("Getting Acquainted", crafting["explanation"])
        self.assertIn("중단됩니다", crafting["explanation"])
        self.assertTrue(questions[418]["question"].startswith("다음 중"))
        self.assertNotIn("유일한", questions[418]["explanation"])
        self.assertIn("다른 연료 소비 보정 없이", questions[419]["question"])
        self.assertNotIn("최대 33분 41초", questions[419]["explanation"])
        self.assertIn("접근 조건", questions[454]["question"])
        self.assertIn("작업대 건설 없이", questions[454]["choices"][questions[454]["answer"]])

    def test_fourth_review_batch_records_sources_without_claiming_live_verification(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        qids = (
            7, 47, 67, 72, 104, 110, 141, 160, 162, 337, 338,
            380, 381, 417, 418, 419, 420, 421, 454,
        )
        for qid in qids:
            with self.subTest(qid=qid):
                self.assertEqual(questions[qid]["reviewed_at"], "2026-09-22")
                self.assertTrue(questions[qid]["sources"])
                self.assertEqual(questions[qid].get("mode", "common"), "common")
        for qid in (380, 381, 417, 418, 419, 420, 421):
            with self.subTest(limited_evidence=qid):
                self.assertTrue(questions[qid]["volatile"])
                self.assertIn("검색 수집본", questions[qid]["volatile_note"])
                self.assertNotIn("배포 후 현행", questions[qid]["volatile_note"])

    def test_skill_questions_separate_effects_actions_and_baseline_bonuses(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        metabolism = questions[161]
        self.assertIn("부정 효과 지속시간", metabolism["choices"][metabolism["answer"]])
        self.assertNotIn("에너지 소모 효율", metabolism["choices"][metabolism["answer"]])
        self.assertIn("Health", metabolism["explanation"])
        self.assertIn("소지 무게 한계", questions[66]["question"])
        self.assertIn("추가 중량 보정을 제외", questions[422]["question"])
        for qid in (378, 379):
            self.assertIn("다른 성장 보정을 제외", questions[qid]["question"])
        self.assertIn("다른 스태미나 보정을 제외", questions[431]["question"])
        self.assertIn("해제 조작 자체", questions[394]["explanation"])
        self.assertIn("탄을 넣고 빼는", questions[432]["explanation"])
        self.assertNotIn("장전·해체 속도는 각각 +30%", questions[432]["explanation"])
        self.assertIn("비트코인 팜", questions[430]["explanation"])
        self.assertIn("누적값", questions[433]["explanation"])
        self.assertIn("스태미나 부족", questions[435]["question"])
        self.assertIn("완전 면역과 구분", questions[435]["explanation"])

    def test_historical_skill_and_bug_questions_do_not_claim_current_runtime_state(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        self.assertIn("미구현(Upcoming)", questions[202]["question"])
        self.assertIn("출시를 보장하지", questions[272]["explanation"])
        self.assertIn("목록에 이름이 있다는 사실", questions[293]["explanation"])
        self.assertIn("0.14.5", questions[331]["question"])
        for qid in (410, 429):
            with self.subTest(qid=qid):
                self.assertTrue(questions[qid]["question"].startswith("과거"))
                self.assertIn("위키", questions[qid]["question"])
                self.assertIn("현재 재현·수정 여부는 미확인", questions[qid]["volatile_note"])
        self.assertNotIn("정상 작동합니다", questions[429]["explanation"])
        self.assertNotIn("정상적으로 지급됩니다", questions[410]["explanation"])

    def test_fifth_review_batch_keeps_provenance_modes_and_volatile_numeric_rules(self):
        path = Path(__file__).resolve().parents[1] / "questions.json"
        questions = {q["id"]: q for q in load_questions(path)}
        qids = (
            66, 161, 202, 203, 204, 205, 206, 240, 241, 272, 293, 331, 332,
            376, 377, 378, 379, 394, 410, 422, 423, 425, 426, 427, 428,
            429, 430, 431, 432, 433, 434, 435,
        )
        for qid in qids:
            with self.subTest(qid=qid):
                self.assertEqual(questions[qid]["reviewed_at"], "2026-09-22")
                self.assertTrue(questions[qid]["sources"])
                self.assertEqual(
                    questions[qid].get("mode", "common"), "pve" if qid == 410 else "common"
                )
                if qid not in (66, 161):
                    self.assertTrue(questions[qid]["volatile"])
        # 스킬 분류의 모든 문항에 검토 기록이 있지만 최신 게임 실측 보장은 아니다.
        self.assertTrue(
            all(q.get("sources") for q in questions.values() if q["category"] == "스킬")
        )

    def test_medical_questions_separate_skill_changes_from_hp_and_stamina_effects(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        adrenaline = questions[146]
        self.assertIn("체력 재생", adrenaline["choices"][adrenaline["answer"]])
        self.assertNotIn("스태미나 회복", adrenaline["choices"][adrenaline["answer"]])
        etg = questions[252]
        self.assertIn("스킬", etg["choices"][etg["answer"]])
        self.assertNotIn("체력 감소", etg["choices"][etg["answer"]])
        self.assertIn("HP 재생이 아닙니다", questions[235]["explanation"])
        self.assertIn("직접적인 HP 감소가 아닙니다", questions[230]["explanation"])
        self.assertNotIn("드론", questions[236]["explanation"])
        self.assertIn("체온 변화량", questions[255]["explanation"])

    def test_medical_questions_keep_exceptions_units_and_baseline_conditions(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("엘리트 효과가 없는", questions[56]["question"])
        self.assertIn("엘리트", questions[116]["explanation"])
        self.assertIn("머리와 흉부", questions[233]["explanation"])
        self.assertIn("골절 치료가 아닙니다", questions[147]["explanation"])
        self.assertNotIn("전용 아이템으로만", questions[148]["explanation"])
        self.assertIn("각 신체 부위 하나당", questions[385]["question"])
        self.assertIn("재출혈 없이", questions[386]["question"])
        self.assertIn("진통 효과가 없을 때", questions[387]["question"])
        self.assertIn("추가 보정을 제외", questions[329]["question"])
        self.assertIn("아직 사용하지 않은", questions[330]["question"])
        self.assertIn("기본 사용 시간", questions[416]["question"])

    def test_sixth_review_batch_records_limited_sources_and_preserves_common_pool(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        qids = (
            55, 56, 116, 146, 147, 148, 230, 231, 232, 233, 235, 236, 245, 247,
            252, 255, 294, 329, 330, 382, 383, 384, 385, 386, 387, 388, 414, 416,
        )
        for qid in qids:
            with self.subTest(qid=qid):
                self.assertEqual(questions[qid]["reviewed_at"], "2026-09-22")
                self.assertTrue(questions[qid]["sources"])
                self.assertEqual(questions[qid].get("mode", "common"), "common")
                if questions[qid].get("volatile"):
                    self.assertIn("검색 수집본", questions[qid]["volatile_note"])
                    self.assertIn("실측 검증은 아님", questions[qid]["volatile_note"])
        for qid in (146, 382, 384, 385, 386, 387, 388, 414, 416):
            self.assertTrue(questions[qid]["volatile"])

    def test_food_comparisons_exclude_ongoing_recovery_and_personal_caps(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("미사용 아이템 전체", questions[228]["question"])
        self.assertIn("개인 보정·수분 상한 제외", questions[228]["question"])
        food = questions[229]
        self.assertIn("즉시 에너지 회복량", food["question"])
        self.assertIn("지속 회복", food["question"])
        self.assertIn("300초간 +0.1/s", food["explanation"])
        self.assertTrue(any("MRE_ration_pack" in url for url in food["sources"]))
        self.assertIn("추가 보정을 제외", questions[413]["question"])

    def test_stimulant_questions_keep_item_baselines_and_distinct_side_effects(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("아이템 자체의 기본 효과표", questions[234]["question"])
        self.assertIn("개인 스킬 보정 전", questions[250]["question"])
        self.assertIn("HP 재생률 -1/s", questions[250]["explanation"])
        self.assertIn("HP 재생률 -0.1/s", questions[246]["explanation"])
        self.assertIn("Unknown toxin", questions[249]["explanation"])
        self.assertIn("영구 면역", questions[249]["explanation"])
        self.assertIn("시작 지연이 다르므로", questions[254]["explanation"])
        self.assertIn("개인 보정", questions[253]["explanation"])

    def test_seventh_review_batch_records_sources_for_remaining_medical_questions(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        for qid in (33, 115, 228, 229, 234, 246, 248, 249, 250, 251, 253, 254,
                    256, 268, 413):
            with self.subTest(qid=qid):
                question = questions[qid]
                self.assertEqual(question["reviewed_at"], "2026-09-22")
                self.assertTrue(question["sources"])
                self.assertEqual(question.get("mode", "common"), "common")
                if question.get("volatile"):
                    self.assertIn("검색 수집본", question["volatile_note"])
                    self.assertIn("실측 검증은 아님", question["volatile_note"])
        self.assertTrue(questions[234]["volatile"])
        # Provenance coverage does not assert live-client correctness.
        self.assertTrue(all(
            q.get("sources") for q in questions.values() if q["category"] == "의료·식량"
        ))

    def test_backpack_answer_uses_slots_per_kilogram_not_storage_efficiency(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        question = questions[289]
        # Indexed source values, in choice order; arithmetic, not a live stat fetch.
        capacities_and_weights = ((48, 1.92), (48, 3.5), (20, 0.7), (42, 3.265))
        ratios = [slots / weight for slots, weight in capacities_and_weights]
        self.assertEqual(question["answer"], max(range(4), key=ratios.__getitem__))
        self.assertIn("파르티잔", question["choices"][question["answer"]])
        self.assertIn("1kg당 내부 칸수", question["question"])
        for value in ("28.57", "25", "13.71", "12.86"):
            self.assertIn(value, question["explanation"])
        self.assertNotIn("kg당 2.4칸", question["explanation"])

    def test_container_and_armor_comparisons_do_not_copy_inconsistent_efficiencies(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn(f"77÷6≈{77 / 6:.2f}", questions[396]["explanation"])
        self.assertNotIn("13.83", questions[396]["explanation"])
        self.assertIn("도그태그만", questions[396]["explanation"])
        for durability, destructibility in ((55, 0.1875), (35, 0.3375)):
            self.assertIn(f"{durability / destructibility:.2f}", questions[412]["explanation"])
        mask = questions[412]
        self.assertIn("표시 내구도", mask["choices"][mask["answer"]])
        self.assertIn("재질 파괴도", mask["choices"][mask["answer"]])
        self.assertIn("방어 등급이나 관통 방어력", questions[400]["explanation"])

    def test_gear_questions_bound_capacity_equipment_and_reward_claims(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("의료 물자만", questions[207]["explanation"])
        for qid in (208, 239):
            self.assertIn("내용물을 제외한", questions[qid]["question"])
        self.assertIn("제품과 부착물", questions[19]["explanation"])
        self.assertIn("Arena 연동 조건", questions[221]["explanation"])
        self.assertNotIn("아직 미출시", questions[222]["explanation"])
        self.assertIn("참가용 특별 계정", questions[290]["question"])
        self.assertIn("확정 지급", questions[295]["explanation"])

    def test_eighth_review_batch_records_gear_sources_and_numeric_volatility(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        qids = (
            6, 10, 11, 19, 26, 34, 112, 159, 176, 207, 208, 219, 221, 222,
            239, 289, 290, 295, 396, 397, 398, 399, 400, 401, 402, 411, 412,
        )
        for qid in qids:
            with self.subTest(qid=qid):
                reviewed_at = "2026-09-23" if qid == 26 else "2026-09-22"
                self.assertEqual(questions[qid]["reviewed_at"], reviewed_at)
                self.assertTrue(questions[qid]["sources"])
                self.assertEqual(questions[qid].get("mode", "common"), "common")
        for qid in (176, 219, 396, 399, 400, 401, 402, 412):
            self.assertTrue(questions[qid]["volatile"])
            self.assertIn("실측 검증은 아님", questions[qid]["volatile_note"])
        self.assertTrue(all(
            q.get("sources") for q in questions.values() if q["category"] == "장비"
        ))

    def test_weapon_questions_distinguish_magazine_loading_and_firing_compatibility(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        for qid in (38, 267):
            self.assertIn("PMM PstM", questions[qid]["explanation"])
            self.assertIn("발사할 수", questions[qid]["explanation"])
        self.assertIn("탄창에 들어가는", questions[38]["explanation"])
        self.assertIn("PP-9 Klin", questions[267]["explanation"])
        self.assertIn("AVT-40은 단발과 자동사격", questions[335]["explanation"])
        self.assertNotIn("반자동 소총인 SVT/AVT", questions[335]["explanation"])

    def test_weapon_effect_questions_keep_comparison_and_trigger_conditions(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("무게도 ADS 속도", questions[57]["explanation"])
        self.assertIn("제거하거나 교체하지 않고", questions[58]["question"])
        self.assertNotIn("가장 직접적으로", questions[150]["question"])
        self.assertIn("새로 추가되는", questions[391]["question"])
        self.assertIn("단계별로 누적", questions[391]["explanation"])
        self.assertIn("약실에 탄", questions[392]["question"])
        self.assertIn("약실에 탄", questions[392]["explanation"])
        self.assertIn("보기의 네 계열 중", questions[395]["explanation"])
        self.assertIn("전체 무기 중 최저라는 뜻은 아니", questions[395]["explanation"])

    def test_ninth_review_batch_records_weapon_sources_without_live_verification_claims(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        qids = (15, 21, 38, 57, 58, 73, 108, 150, 267, 335, 391, 392, 393, 395)
        for qid in qids:
            with self.subTest(qid=qid):
                self.assertEqual(questions[qid]["reviewed_at"], "2026-09-22")
                self.assertTrue(questions[qid]["sources"])
                self.assertEqual(questions[qid].get("mode", "common"), "common")
                self.assertEqual(questions[qid]["answer"], 0)
        for qid in (391, 392, 393, 395):
            self.assertTrue(questions[qid]["volatile"])
            self.assertIn("검색 수집본", questions[qid]["volatile_note"])
            self.assertIn("실측 검증은 아님", questions[qid]["volatile_note"])

    def test_shotgun_ammunition_question_excludes_mp18_classification_ambiguity(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        question = questions[125]
        self.assertIn("MP-133", question["question"])
        self.assertEqual(question["choices"][question["answer"]], "12/70 벅샷")
        self.assertIn("MP-18은 7.62x54mmR", question["explanation"])
        self.assertIn("게임에서 산탄총으로 분류", questions[281]["question"])

    def test_weapon_caliber_questions_bound_game_models_and_release_claims(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        for qid in (263, 277, 283, 284, 334):
            self.assertIn("게임", questions[qid]["question"])
        self.assertNotIn("게임에 없는 구경", questions[284]["explanation"])
        self.assertIn("총기의 사용 탄약", questions[278]["explanation"])
        self.assertIn("별도 탄약", questions[276]["explanation"])
        self.assertIn("공식 Telegram", questions[458]["question"])
        self.assertIn("8월 10일(UTC)", questions[458]["question"])
        self.assertIn("한국시간으로는 8월 11일", questions[458]["explanation"])
        self.assertIn("정식 출시를 확정하지 않습니다", questions[458]["explanation"])
        self.assertIn("https://t.me/escapefromtarkovEN/6745", questions[458]["sources"])

    def test_tenth_review_batch_records_caliber_sources_and_keeps_correct_answers(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        qids = (
            121, 122, 123, 124, 125, 257, 258, 259, 260, 261, 262, 263, 264,
            274, 275, 276, 277, 278, 281, 282, 283, 284, 334, 336, 456, 458,
        )
        for qid in qids:
            with self.subTest(qid=qid):
                self.assertEqual(questions[qid]["reviewed_at"], "2026-09-22")
                self.assertTrue(questions[qid]["sources"])
                self.assertEqual(questions[qid].get("mode", "common"), "common")
                self.assertEqual(questions[qid]["answer"], 0)
        # Source-backed caliber/classification answers; no live data fetch is implied.
        answers = {
            122: "5.56x45mm", 124: "9x39mm", 257: "12.7x55mm", 258: ".50 BMG",
            261: "4.6x30mm HK", 262: "5.7x28mm FN", 263: "6.8x51mm",
            264: "12.7x55mm", 274: "CR 200DS", 275: ".45 ACP",
            276: "7.62x51mm NATO", 277: ".300 블랙아웃", 278: ".366 TKM",
            281: "MP-18", 282: "9.3x64mm", 283: "DVL-10", 284: ".357 매그넘",
            456: "5.56x45mm", 458: "FAMAS G2",
        }
        for qid, expected in answers.items():
            self.assertEqual(questions[qid]["choices"][questions[qid]["answer"]], expected)

    def test_weapon_condition_and_optics_questions_keep_exceptions_explicit(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("수리로 회복", questions[28]["question"])
        self.assertIn("MOA", questions[28]["explanation"])
        self.assertIn("PNV-10T", questions[39]["question"])
        self.assertIn("T-7", questions[39]["explanation"])
        self.assertIn("기계적 고장이 발생하는 총기", questions[45]["question"])
        self.assertIn("PPSh-41", questions[45]["explanation"])
        self.assertTrue(questions[45]["volatile"])
        self.assertIn("실측 검증은 아님", questions[45]["volatile_note"])

    def test_weapon_handling_questions_do_not_promise_universal_effects(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("제품별", questions[51]["explanation"])
        self.assertIn("RPM)만으로", questions[63]["question"])
        self.assertIn("부착물", questions[63]["choices"][questions[63]["answer"]])
        self.assertIn("MOA는 같은 개념이 아닙니다", questions[65]["explanation"])
        self.assertIn("탄약이 없어도", questions[70]["choices"][questions[70]["answer"]])
        self.assertIn("보장한다는 뜻은 아닙니다", questions[70]["explanation"])
        self.assertNotIn("소음 없이 사용할 수", questions[70]["explanation"])

    def test_eleventh_review_batch_records_remaining_weapon_sources(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        for qid in (28, 39, 45, 51, 63, 65, 70, 90):
            with self.subTest(qid=qid):
                self.assertEqual(questions[qid]["reviewed_at"], "2026-09-22")
                self.assertTrue(questions[qid]["sources"])
                self.assertEqual(questions[qid].get("mode", "common"), "common")
                self.assertEqual(questions[qid]["answer"], 0)
        # Provenance coverage is not a claim of current in-game verification.
        self.assertTrue(all(
            q.get("sources") for q in questions.values() if q["category"] == "무기"
        ))

    def test_ammo_penetration_questions_distinguish_probability_and_blunt_damage(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("확률", questions[158]["explanation"])
        self.assertIn("관통 판정에서 실패", questions[52]["question"])
        self.assertNotIn("클래스를 넘지 못하면", questions[52]["question"])
        self.assertIn("전달될 수 있다", questions[52]["choices"][questions[52]["answer"]])
        self.assertIn("항상 체력 피해 0", questions[405]["explanation"])
        self.assertIn("실제 명중 피해", questions[404]["explanation"])
        self.assertIn("다른 수치", questions[46]["explanation"])
        self.assertIn("거의 항상", questions[407]["choices"][questions[407]["answer"]])
        self.assertTrue(questions[407]["volatile"])

    def test_ammo_comparisons_bound_base_values_and_projectile_scope(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        qids = (186, 187, 188, 194, 199, 200, 237, 265, 266, 280, 286, 296)
        for qid in qids:
            with self.subTest(qid=qid):
                self.assertIn("보기", questions[qid]["question"])
                self.assertIn("기본", questions[qid]["question"])
        self.assertNotIn("전체 1위", questions[199]["explanation"])
        self.assertNotIn("게임 전체 단일 투사체 2위", questions[237]["explanation"])
        self.assertIn("투사체 1발", questions[200]["question"])
        self.assertIn("펠릿 하나", questions[280]["question"])
        self.assertIn("8·8·8·9", questions[280]["explanation"])
        self.assertIn("곱한 값", questions[296]["explanation"])
        self.assertIn("7U4 아음속탄", questions[265]["choices"])

    def test_twelfth_review_batch_records_ammo_sources_without_live_claims(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        qids = (
            46, 52, 158, 186, 187, 188, 194, 199, 200, 237, 238, 265,
            266, 280, 286, 296, 404, 405, 407,
        )
        for qid in qids:
            with self.subTest(qid=qid):
                reviewed_at = "2026-09-23" if qid == 405 else "2026-09-22"
                self.assertEqual(questions[qid]["reviewed_at"], reviewed_at)
                self.assertTrue(questions[qid]["sources"])
                self.assertEqual(questions[qid].get("mode", "common"), "common")
                self.assertEqual(questions[qid]["answer"], 0)
                if questions[qid].get("volatile"):
                    self.assertIn("검색 수집본", questions[qid]["volatile_note"])
                    self.assertIn("실측 검증은 아님", questions[qid]["volatile_note"])

    def test_ammo_review_removes_universal_damage_and_caliber_claims(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertNotIn("방탄복에는 무력", questions[179]["explanation"])
        self.assertIn("모든 방어구", questions[179]["explanation"])
        self.assertNotIn("관통형 탄일수록", questions[181]["explanation"])
        self.assertIn("항상 반비례하는 것은 아닙니다", questions[181]["explanation"])
        self.assertIn("7N40", questions[181]["explanation"])
        self.assertIn("구경의 크기만으로", questions[326]["explanation"])
        self.assertIn("처치 성능 순위를 뜻하지는 않습니다", questions[327]["explanation"])

    def test_ammo_numeric_and_runner_up_questions_preserve_answer_meanings(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        for qid, answer in ((325, "QuakeMaker"), (328, "44"), (341, "75")):
            self.assertEqual(questions[qid]["choices"][questions[qid]["answer"]], answer)
        self.assertIn("두 번째", questions[325]["question"])
        self.assertIn("RIP 102 > QuakeMaker 85", questions[325]["explanation"])
        self.assertIn("기본 관통력", questions[328]["question"])
        self.assertIn("기본 육체 피해량", questions[341]["question"])
        self.assertIn("실제 명중 피해와는 구분", questions[341]["explanation"])

    def test_thirteenth_review_batch_records_ammo_values_as_indexed_not_live(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        qids = (
            178, 179, 180, 181, 182, 183, 184, 185, 189, 190, 191, 192, 193,
            195, 196, 197, 198, 201, 279, 285, 325, 326, 327, 328, 341,
        )
        for qid in qids:
            with self.subTest(qid=qid):
                q = questions[qid]
                self.assertIn("기본", q["question"])
                if qid not in (328, 341):
                    self.assertIn("보기", q["question"])
                self.assertEqual(q["answer"], 0)
                self.assertEqual(q.get("mode", "common"), "common")
                self.assertEqual(q["reviewed_at"], "2026-09-22")
                self.assertTrue(q["sources"])
                self.assertTrue(q["volatile"])
                self.assertIn("검색 수집본", q["volatile_note"])
                self.assertIn("실측 검증은 아님", q["volatile_note"])

    def test_basic_system_review_separates_pmc_scav_and_raid_choices(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("캐릭터 생성 시", questions[17]["explanation"])
        self.assertIn("The Lab", questions[30]["explanation"])
        self.assertIn("선택하는 정보", questions[49]["question"])
        self.assertNotIn("PMC 캐릭터가 Scav로", questions[74]["question"])
        self.assertIn("별도로 성장", questions[74]["explanation"])
        self.assertIn("PMC의 소지품", questions[107]["choices"][0])
        self.assertIn("보존된다는 뜻은 아닙니다", questions[107]["explanation"])

    def test_basic_system_review_corrects_item_and_loss_explanations(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("정맥의 위치", questions[109]["explanation"])
        self.assertNotIn("AN-94", questions[114]["explanation"])
        self.assertIn("Vector Gen.2 9x19", questions[114]["question"])
        self.assertEqual(questions[114]["choices"][0], "차지샷(모아쏘기)")
        self.assertIn("컬티스트 칼 제외", questions[5]["explanation"])
        self.assertIn("보호 예외", questions[97]["choices"][0])
        self.assertIn("장착 중이던 보험 장비", questions[97]["explanation"])
        self.assertIn("경험치", questions[96]["explanation"])
        self.assertIn("상인 거래 상품", questions[448]["question"])
        self.assertIn("모든 장비·전리품", questions[448]["explanation"])

    def test_fourteenth_review_batch_records_system_sources_and_preserves_modes(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        qids = (
            2, 4, 5, 17, 30, 49, 74, 92, 93, 96, 97, 106, 107, 109,
            114, 408, 409, 447, 448, 449, 451, 455,
        )
        for qid in qids:
            with self.subTest(qid=qid):
                q = questions[qid]
                self.assertEqual(q["reviewed_at"], "2026-09-22")
                self.assertTrue(q["sources"])
                self.assertEqual(q["answer"], 0)
                expected_mode = "pvp" if qid in (447, 448) else "common"
                self.assertEqual(q.get("mode", "common"), expected_mode)
        for qid in (5, 97, 409):
            self.assertTrue(questions[qid]["volatile"])
            self.assertIn("실측 검증은 아님", questions[qid]["volatile_note"])

    def test_trader_review_separates_story_unlocks_and_loyalty_from_reputation(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("LL1~LL4", questions[13]["question"])
        self.assertIn("구분되는 수치", questions[13]["explanation"])
        self.assertIn("Tour", questions[27]["question"])
        self.assertIn("Factory", questions[27]["question"])
        self.assertEqual(questions[27]["choices"][0], "프라포르(Prapor)")
        self.assertIn("Introduction", questions[68]["question"])
        self.assertIn("메카닉에게 전달", questions[75]["choices"][0])
        self.assertIn("평판", questions[36]["explanation"])
        self.assertNotIn("카르마는 펜스에만", questions[36]["explanation"])
        self.assertEqual(questions[48]["choices"][2], "상인 평판(Reputation) 상승")

    def test_trader_review_bounds_flea_quest_items_and_insurance_claims(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("상인 매물도", questions[12]["explanation"])
        self.assertIn("판매한 물품", questions[59]["choices"][0])
        self.assertIn("별도 퀘스트 아이템 인벤토리", questions[60]["question"])
        self.assertIn("일반 루팅 아이템 전체", questions[60]["explanation"])
        self.assertNotIn("수 시간", questions[126]["explanation"])
        self.assertIn("수령 기한", questions[126]["explanation"])
        self.assertIn("영구 프로필", questions[127]["question"])
        self.assertNotIn("로그(Rogues)", questions[172]["choices"][3])

    def test_fifteenth_review_batch_records_trader_and_quest_sources(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        qids = (
            12, 13, 22, 25, 27, 31, 36, 42, 48, 50, 53, 54, 59, 60, 62, 64,
            68, 75, 87, 88, 89, 91, 117, 126, 127, 167, 172, 223, 224, 227,
            291, 292, 313, 452, 453,
        )
        for qid in qids:
            with self.subTest(qid=qid):
                q = questions[qid]
                self.assertEqual(q["reviewed_at"], "2026-09-22")
                self.assertTrue(q["sources"])
                self.assertEqual(q["answer"], 0)
                self.assertEqual(q.get("mode", "common"), "common")
        for qid in (27, 68, 75, 127, 313):
            self.assertTrue(questions[qid]["volatile"])
            self.assertIn("실측 검증은 아님", questions[qid]["volatile_note"])

    def test_quest_review_updates_debut_and_renamed_sr25_task(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("우테스", questions[310]["question"])
        self.assertNotIn("첫 번째", questions[310]["question"])
        debut = questions[311]
        self.assertIn("1.1", debut["question"])
        self.assertIn("총 5명", debut["choices"][debut["answer"]])
        self.assertNotIn("MP-133", debut["choices"][debut["answer"]])
        for location in ("우즈", "그라운드 제로", "인터체인지", "커스텀즈"):
            self.assertIn(location, debut["choices"][debut["answer"]])
        self.assertIn("이전 목표", debut["explanation"])
        self.assertIn("The Tarkov Import", questions[315]["question"])
        self.assertIn("Test Drive - Part 1", questions[315]["question"])
        self.assertEqual(questions[315]["choices"][questions[315]["answer"]], "SR-25")
        self.assertNotIn("10명", questions[315]["explanation"])
        self.assertIn("수량 확정은 보류", questions[315]["volatile_note"])

    def test_quest_review_bounds_key_usage_and_preserves_weapon_requirements(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("The Punisher - Part 6", questions[154]["explanation"])
        for task in ("Accidental Witness", "Pharmacist", "Shaking Up the Teller"):
            self.assertIn(task, questions[209]["question"])
        self.assertIn("루팅 방", questions[209]["explanation"])
        self.assertNotIn("쓰이는 곳이 없습니다", questions[209]["explanation"])
        cultist = questions[317]
        self.assertIn("무기의 조합", cultist["question"])
        self.assertIn("더블배럴", cultist["choices"][cultist["answer"]])
        self.assertIn("MP-43-1C", cultist["explanation"])
        self.assertIn("소드오프", cultist["explanation"])
        self.assertNotIn("3명", cultist["choices"][cultist["answer"]])
        self.assertIn("수량 확정 보류", cultist["volatile_note"])
        self.assertIn("LBT", questions[321]["explanation"])
        self.assertIn("제출", questions[321]["explanation"])
        self.assertIn("한시적", questions[323]["explanation"])

    def test_sixteenth_review_batch_records_sources_without_claiming_live_validation(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        qids = (154, 209, 310, 311, 315, 316, 317, 319, 320, 321, 323)
        for qid in qids:
            with self.subTest(qid=qid):
                q = questions[qid]
                self.assertEqual(q["reviewed_at"], "2026-09-22")
                self.assertTrue(q["sources"])
                self.assertTrue(q["volatile"])
                self.assertIn("실측 검증은 아님", q["volatile_note"])
                self.assertEqual(q["answer"], 0)
                self.assertEqual(q.get("mode", "common"), "common")
        self.assertIn("모드 차이로 단정하지 않음", questions[311]["volatile_note"])
        self.assertIn("진영별 최신 수량 확인은 보류", questions[321]["volatile_note"])
        self.assertIn("원복 시점", questions[323]["volatile_note"])

    def test_blackout_review_scopes_event_history_and_direct_door_unlock(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        for qid in (360, 361, 362, 363, 371, 372):
            with self.subTest(qid=qid):
                q = questions[qid]
                self.assertIn("2026년 7월", q["question"])
                self.assertNotIn("약 1개월", q["volatile_note"])
                self.assertNotIn("복귀하므로", q["volatile_note"])
        self.assertIn("직접 열 때", questions[361]["question"])
        self.assertIn("Wedge", questions[361]["explanation"])
        self.assertIn("이미 문을 열었다면", questions[361]["explanation"])
        self.assertIn("기본 루블 보상", questions[363]["explanation"])
        self.assertNotIn("의류는 시즌 1 보상", questions[363]["explanation"])
        for qid, mode, duration in ((371, "pvp", "30분"), (372, "pve", "35분")):
            self.assertEqual(questions[qid]["mode"], mode)
            self.assertEqual(questions[qid]["choices"][questions[qid]["answer"]], duration)
            self.assertIn("밸런스 조정 공지", questions[qid]["question"])
            self.assertIn("현재 상시 제한 시간", questions[qid]["explanation"])

    def test_collector_and_ammo_review_distinguishes_trader_unlock_conditions(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        collector = questions[367]
        answer = collector["choices"][collector["answer"]]
        self.assertIn("7명", answer)
        self.assertIn("평판 3.0", answer)
        self.assertNotIn("모든 상인", answer)
        for trader in (
            "Prapor", "Therapist", "Skier", "Peacekeeper", "Mechanic", "Ragman", "Jaeger"
        ):
            self.assertIn(trader, collector["explanation"])
        self.assertIn("다른 해금 조건", collector["explanation"])
        self.assertIn("프라포르 LL1", questions[369]["question"])
        self.assertIn("프라포르를 해금", questions[369]["explanation"])
        self.assertNotIn("게임 시작 시점부터", questions[369]["question"])

    def test_seventeenth_review_batch_preserves_modes_and_marks_evidence_limits(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        for qid in (360, 361, 362, 363, 367, 369, 371, 372):
            with self.subTest(qid=qid):
                q = questions[qid]
                self.assertEqual(q["reviewed_at"], "2026-09-22")
                self.assertTrue(q["sources"])
                self.assertTrue(q["volatile"])
                self.assertEqual(q["answer"], 0)
                expected_mode = {371: "pvp", 372: "pve"}.get(qid, "common")
                self.assertEqual(q.get("mode", "common"), expected_mode)
        self.assertIn("확정 보류", questions[367]["volatile_note"])
        self.assertIn("실측 검증은 아님", questions[369]["volatile_note"])

    def test_boss_map_review_separates_home_territory_from_exclusive_spawns(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        for qid in (133, 134, 217):
            with self.subTest(qid=qid):
                self.assertNotIn("상주", questions[qid]["question"])
                self.assertIn("터미널", questions[qid]["explanation"])
        self.assertIn("ULTRA", questions[133]["question"])
        self.assertIn("기숙사", questions[134]["question"])
        self.assertIn("군사기지", questions[217]["question"])
        self.assertIn("세관에서 경호원 4명", questions[134]["explanation"])
        self.assertIn("터미널에서는 3명", questions[134]["explanation"])
        self.assertIn("리저브의 경비병 6명", questions[217]["explanation"])
        self.assertIn("터미널의 3명", questions[217]["explanation"])

    def test_boss_review_preserves_identity_and_scopes_blackout_history(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("TerraGroup Labs 연구원", questions[137]["question"])
        self.assertIn("내무부 아카데미", questions[218]["explanation"])
        self.assertIn("클리모프 쇼핑몰", questions[218]["explanation"])
        self.assertIn("Gus", questions[436]["explanation"])
        self.assertIn("Basmach", questions[436]["explanation"])
        self.assertIn("FN40GL", questions[437]["explanation"])
        self.assertIn("매번", questions[437]["explanation"])
        for qid in (357, 358, 359):
            with self.subTest(qid=qid):
                self.assertIn("2026년 7월", questions[qid]["question"])
                self.assertNotIn("약 1개월", questions[qid]["volatile_note"])
        self.assertNotIn("먼저 등장", questions[358]["explanation"])
        self.assertIn("현재 랩의 상시 배치", questions[358]["explanation"])
        self.assertIn("비상 접근 코드", questions[359]["question"])
        self.assertIn("화이트보드", questions[359]["explanation"])
        self.assertNotIn("5619", questions[359]["explanation"])

    def test_eighteenth_review_batch_records_sources_and_evidence_limits(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        for qid in (133, 134, 135, 136, 137, 217, 218, 357, 358, 359, 436, 437):
            with self.subTest(qid=qid):
                q = questions[qid]
                self.assertEqual(q["reviewed_at"], "2026-09-22")
                self.assertTrue(q["sources"])
                self.assertTrue(q["volatile"])
                self.assertIn("실측 검증은 아님", q["volatile_note"])
                self.assertEqual(q["answer"], 0)
                self.assertEqual(q.get("mode", "common"), "common")

    def test_cultist_review_separates_night_groups_and_possible_loot(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        night = questions[212]
        self.assertIn("등대 섬 경비대를 제외", night["question"])
        self.assertIn("게임 내 22:00~07:00", night["explanation"])
        self.assertIn("반드시 등장한다는 뜻은 아니며", night["explanation"])
        self.assertIn("일반 야간", questions[243]["question"])
        self.assertNotIn("항상", questions[243]["question"])
        self.assertEqual(questions[243]["choices"][questions[243]["answer"]], "즈레츠(Zhrets)")
        loot = questions[271]
        self.assertIn("확정 드롭은 아니다", loot["choices"][loot["answer"]])
        self.assertNotIn("아무 열쇠", loot["choices"][loot["answer"]])
        self.assertIn("보장하는 설명은 아닙니다", loot["explanation"])

    def test_ai_review_scopes_transport_services_and_lore(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("Scav 모드를 선택", questions[18]["explanation"])
        self.assertNotIn("대기 중", questions[18]["question"])
        self.assertIn("매 레이드 반드시", questions[139]["explanation"])
        self.assertIn("PMC의 물품 반출", questions[140]["explanation"])
        self.assertIn("적대할 수 있어", questions[140]["explanation"])
        self.assertIn("트립와이어", questions[166]["choices"][questions[166]["answer"]])
        self.assertIn("우즈 맵에서만", questions[166]["explanation"])
        self.assertIn("설정상", questions[210]["question"])
        self.assertIn("매번 같은 장소", questions[210]["explanation"])
        self.assertIn("스폰될 수 있다", questions[214]["choices"][questions[214]["answer"]])

    def test_poison_and_santa_review_bounds_raid_treatment_and_event_year(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        poison = questions[213]
        self.assertIn("보기 중, 레이드 중 컬티스트 독", poison["question"])
        self.assertEqual(poison["choices"][poison["answer"]], "xTG-12 주사기")
        self.assertIn("Perfotoran", poison["explanation"])
        self.assertNotIn("주사기로만", poison["explanation"])
        santa = questions[340]
        self.assertIn("2025년 12월 Kolotun", santa["question"])
        self.assertIn("보기 중", santa["question"])
        self.assertIn("더 랩과 더 래버린스", santa["explanation"])
        self.assertEqual(santa["choices"][santa["answer"]], "더 랩(The Lab)")

    def test_remaining_boss_review_records_sources_without_claiming_live_validation(self):
        questions = load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        bosses = [q for q in questions if q["category"] == "보스·AI"]
        self.assertEqual(len(bosses), 30)
        for q in bosses:
            with self.subTest(qid=q["id"]):
                self.assertTrue(q["sources"])
                self.assertTrue(q["reviewed_at"])
        reviewed = {18, 132, 139, 140, 165, 166, 210, 212, 213, 214, 215, 216, 243, 271, 340}
        for q in bosses:
            if q["id"] not in reviewed:
                continue
            with self.subTest(qid=q["id"]):
                self.assertEqual(q["reviewed_at"], "2026-09-22")
                self.assertEqual(q["answer"], 0)
                self.assertEqual(q.get("mode", "common"), "common")
                if q["id"] not in {18, 215, 216}:
                    self.assertTrue(q["volatile"])
                    self.assertIn("실측 검증은 아님", q["volatile_note"])

    def test_hideout_review_distinguishes_storage_power_and_dogtag_conditions(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("연료를 소모", questions[8]["question"])
        self.assertIn("라바토리 제작은 전력 없이", questions[8]["explanation"])
        self.assertIn("레이드 밖", questions[24]["question"])
        self.assertIn("모두 자동 보관", questions[24]["explanation"])
        self.assertIn("수집을 의뢰", questions[32]["question"])
        self.assertIn("이익은 보장되지", questions[32]["explanation"])
        self.assertEqual(questions[142]["choices"][0], "문샤인 또는 인텔리전스 폴더")
        self.assertIn("직접 처치한 상대 진영", questions[144]["question"])
        self.assertIn("전투 스킬 성장", questions[144]["explanation"])

    def test_armor_review_separates_carrier_class_and_original_durability(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("Class 0 표기를 제외", questions[43]["question"])
        self.assertIn("장착한 방탄판", questions[43]["explanation"])
        self.assertEqual(questions[43]["choices"][0], "1~6단계 클래스")
        self.assertIn("피탄 부위", questions[69]["question"])
        self.assertIn("원래 최대치", questions[69]["question"])
        self.assertIn("수리로 줄어든 최대치가 아니라", questions[69]["explanation"])

    def test_system_review_bounds_editions_character_level_and_product_identity(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("별도의 게임", questions[23]["explanation"])
        self.assertNotIn("스핀오프 모드", questions[23]["question"])
        self.assertEqual(questions[35]["choices"][0], "데스 스크린(사망 결과 화면)")
        self.assertIn("경험치 0", questions[37]["question"])
        self.assertIn("개별 스킬 레벨과 캐릭터 레벨", questions[37]["explanation"])
        self.assertNotIn("사전 구매", questions[78]["choices"][0])
        self.assertIn("판매 플랫폼", questions[78]["explanation"])
        self.assertIn("일부 외형 아이템", questions[101]["explanation"])
        self.assertIn("개발사", questions[120]["question"])
        self.assertNotIn("최우선으로 하는", questions[120]["explanation"])

    def test_basic_system_and_hideout_review_records_evidence_and_limits(self):
        questions = load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        reviewed = {
            8, 9, 20, 23, 24, 32, 35, 37, 40, 43, 69, 78, 101, 103, 105,
            111, 113, 120, 142, 143, 144, 145, 173,
        }
        changing = {8, 32, 35, 37, 43, 69, 78, 101, 105, 111, 142, 143, 144, 145}
        for q in questions:
            if q["id"] not in reviewed:
                continue
            with self.subTest(qid=q["id"]):
                self.assertTrue(q["sources"])
                self.assertEqual(q["reviewed_at"], "2026-09-22")
                self.assertEqual(q["answer"], 0)
                self.assertEqual(q.get("mode", "common"), "common")
                if q["id"] in changing:
                    self.assertTrue(q["volatile"])
                    self.assertIn("실측 검증은 아님", q["volatile_note"])
        for q in questions:
            if q["category"] == "하이드아웃":
                with self.subTest(hideout_qid=q["id"]):
                    self.assertTrue(q["sources"])
                    self.assertTrue(q["reviewed_at"])

    def test_story_review_corrects_release_history_and_voice_generalization(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("클로즈드 베타", questions[79]["explanation"])
        self.assertIn("2025년 11월 15일", questions[79]["explanation"])
        self.assertNotIn("오픈 베타", questions[79]["explanation"])
        self.assertIn("러시아 억양의 영어", questions[100]["explanation"])
        self.assertEqual(questions[100]["choices"][questions[100]["answer"]], "영어")
        self.assertEqual(questions[309]["choices"][0], "게임 에디션 이름")
        self.assertNotIn("최상위", questions[309]["explanation"])

    def test_lore_review_separates_documented_background_from_inference(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("지주회사", questions[76]["choices"][0])
        self.assertIn("스캔들", questions[77]["choices"][0])
        self.assertIn("기반 회사", questions[306]["question"])
        self.assertNotIn("법인 등록", questions[306]["question"])
        self.assertIn("위키가", questions[307]["question"])
        self.assertIn("공식 확정됐다는 뜻은 아닙니다", questions[307]["explanation"])
        self.assertIn("전체 인력", questions[345]["question"])
        self.assertIn("열거되지 않은", questions[346]["question"])

    def test_story_objectives_have_specific_locations_and_shared_progress_exception(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("코즐로프", questions[303]["question"])
        self.assertIn("1층 110호", questions[303]["explanation"])
        self.assertIn("인터체인지", questions[352]["explanation"])
        self.assertIn("도착·조사", questions[353]["question"])
        self.assertIn("자동 완료", questions[354]["explanation"])
        self.assertIn("Boreas", questions[354]["explanation"])
        self.assertIn("직접 이어지는", questions[355]["question"])
        self.assertIn("처치만으로 챕터 전체", questions[301]["explanation"])

    def test_ending_review_separates_choices_replay_and_reward_types(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertEqual(questions[299]["choices"][0], "4가지")
        self.assertEqual(questions[308]["choices"][0], "10개")
        self.assertIn("필수 진행 순서", questions[308]["explanation"])
        self.assertIn("처음 제안을 수락하는 것만으로", questions[348]["explanation"])
        self.assertNotIn("최선의 엔딩", questions[349]["explanation"])
        self.assertIn("조건을 충족한 프레스티지 후 재진행", questions[350]["choices"][0])
        self.assertIn("퀘스트용 컨테이너", questions[356]["explanation"])
        self.assertEqual(questions[356]["choices"][0], "시큐어 컨테이너 업그레이드")

    def test_story_review_records_all_sources_without_claiming_live_validation(self):
        questions = load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        stories = [q for q in questions if q["category"] == "스토리"]
        self.assertEqual(len(stories), 42)
        for q in stories:
            with self.subTest(qid=q["id"]):
                self.assertTrue(q["sources"])
                self.assertEqual(q["reviewed_at"], "2026-09-22")
                self.assertEqual(q["answer"], 0)
                self.assertEqual(q.get("mode", "common"), "common")
                if q.get("volatile") and q["id"] != 307:
                    self.assertIn("실측 검증은 아님", q["volatile_note"])
        theory = next(q for q in stories if q["id"] == 307)
        self.assertIn("추론 자체", theory["volatile_note"])

    def test_lab_access_review_separates_direct_access_transit_and_individual_cards(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("직접 입장", questions[269]["question"])
        self.assertIn("트랜짓", questions[269]["explanation"])
        self.assertIn("분대원 각자", questions[270]["question"])
        self.assertIn("연습·협동 연습에서는 소모되지", questions[128]["explanation"])
        self.assertEqual(questions[269]["answer"], 0)

    def test_map_review_scopes_extraction_examples_and_removes_unsupported_extremes(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertNotIn("국경 검문소", questions[14]["choices"])
        self.assertNotIn("MMORPG", " ".join(questions[16]["choices"]))
        self.assertIn("화학 공장", questions[83]["question"])
        self.assertNotIn("가장 좁", questions[83]["question"])
        self.assertIn("Sewer Manhole·D-2", questions[98]["question"])
        self.assertIn("이 사례들", questions[98]["explanation"])
        self.assertEqual(questions[98]["choices"][0], "특정 스킬 레벨 달성")

    def test_map_keys_review_distinguishes_door_loot_and_alarm_effects(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("314호", questions[129]["question"])
        self.assertIn("보장되지는", questions[129]["explanation"])
        self.assertIn("레이더는 출현할 수", questions[287]["explanation"])
        self.assertIn("목록에 없는", questions[288]["question"])
        self.assertIn("목록에 없는", questions[333]["question"])
        self.assertNotIn("랩에 원자로는 없습니다", questions[333]["explanation"])

    def test_map_enemy_review_does_not_promise_co_spawn_or_exclude_other_mode_enemies(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        self.assertIn("반드시 함께 출현한다는 뜻은 아닙니다", questions[444]["explanation"])
        self.assertIn("기본 NPC 배치", questions[445]["question"])
        self.assertNotIn("레이더만", questions[445]["choices"][0])
        self.assertIn("적 전체", questions[445]["explanation"])

    def test_map_review_records_twenty_sources_without_claiming_live_validation(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        reviewed_ids = (
            14, 16, 81, 82, 83, 84, 85, 86, 98, 119,
            128, 129, 131, 269, 270, 287, 288, 333, 444, 445,
        )
        for qid in reviewed_ids:
            with self.subTest(qid=qid):
                question = questions[qid]
                self.assertTrue(question["sources"])
                self.assertEqual(question["reviewed_at"], "2026-09-22")
                self.assertEqual(question["answer"], 0)
                self.assertEqual(question.get("mode", "common"), "common")
                if question.get("volatile"):
                    self.assertIn("실측 검증은 아님", question["volatile_note"])

    def test_map_capacity_comparisons_are_pvp_only_and_use_matching_caps(self):
        questions = load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        indexed = {q["id"]: q for q in questions}
        pvp_ids = {q["id"] for q in filter_questions_for_mode(questions, "pvp")}
        pve_ids = {q["id"] for q in filter_questions_for_mode(questions, "pve")}
        self.assertTrue({441, 446}.issubset(pvp_ids))
        self.assertTrue({441, 446}.isdisjoint(pve_ids))
        for qid in (441, 446):
            with self.subTest(qid=qid):
                self.assertEqual(indexed[qid]["mode"], "pvp")
                self.assertIn("상한", indexed[qid]["question"])
                self.assertIn("PvE", indexed[qid]["explanation"])
        self.assertIn("주간 기준", indexed[446]["question"])
        self.assertIn("충돌", indexed[441]["volatile_note"])
        self.assertIn("5~6명", indexed[446]["volatile_note"])

    def test_map_duration_review_excludes_modifiers_and_scav_remaining_time(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        for qid in (439, 440, 443):
            with self.subTest(qid=qid):
                self.assertIn("모디파이어를 제외", questions[qid]["question"])
                self.assertIn("PMC", questions[qid]["question"])
                self.assertEqual(questions[qid].get("mode", "common"), "common")
        self.assertIn("남은 시간", questions[439]["explanation"])
        self.assertIn("남은 시간", questions[443]["explanation"])
        self.assertNotIn("컬티스트도 추가로 등장", questions[440]["explanation"])
        self.assertIn("쇼어라인에서 트랜짓", questions[442]["question"])
        self.assertIn("AI나 민간인", questions[442]["explanation"])
        self.assertEqual(questions[442].get("mode", "common"), "common")

    def test_remaining_map_review_records_sources_and_live_validation_limits(self):
        questions = {
            q["id"]: q
            for q in load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        }
        for qid in (439, 440, 441, 442, 443, 446):
            with self.subTest(qid=qid):
                question = questions[qid]
                self.assertEqual(question["reviewed_at"], "2026-09-23")
                self.assertTrue(question["sources"])
                self.assertTrue(question["volatile"])
                self.assertIn("실측 검증은 아님", question["volatile_note"])
                self.assertEqual(question["answer"], 0)
        self.assertIn("독립 검증 근거는 아님", questions[442]["volatile_note"])

    def test_disabled_questions_default_on_and_require_an_explicit_boolean(self):
        for value in (None, 0, 1, "true", "false", [], {}):
            with self.subTest(value=value):
                question = {**make_question(1), "enabled": value}
                errors = validate_questions([question], {"general": 1})
                self.assertTrue(any("enabled" in error for error in errors))
        self.assertEqual(validate_questions([make_question(1)], {"general": 1}), [])
        question = {**make_question(1), "enabled": True}
        self.assertEqual(validate_questions([question], {"general": 1}), [])

    def test_disabled_questions_require_a_nonempty_reason(self):
        for reason in (None, "", "  ", 3, False):
            with self.subTest(reason=reason):
                disabled = {**make_question(2), "enabled": False, "disabled_reason": reason}
                errors = validate_questions([make_question(1), disabled], {"general": 1})
                self.assertTrue(any("disabled_reason" in error for error in errors))

    def test_disabled_questions_are_still_validated_for_structure_and_ids(self):
        disabled = {
            **make_question(1), "enabled": False, "disabled_reason": "재검증 필요", "answer": 9,
        }
        errors = validate_questions([make_question(1), disabled], {"general": 1})
        self.assertTrue(any("중복된 id" in error for error in errors))
        self.assertTrue(any("answer" in error for error in errors))

    def test_disabled_questions_do_not_satisfy_mode_difficulty_minimums(self):
        questions = [
            make_question(1),
            {**make_question(2), "mode": "pvp"},
            {**make_question(3), "mode": "pve", "enabled": False, "disabled_reason": "보류"},
        ]
        errors = validate_questions(questions, {"general": 2})
        self.assertTrue(any("PVE 모드 난이도 'general' 문제 부족" in e for e in errors))
        self.assertFalse(any("PVP 모드" in e for e in errors))
        self.assertFalse(any(e.startswith("난이도 'general'") for e in errors))

    def test_disabled_questions_do_not_satisfy_global_difficulty_minimums(self):
        disabled = {**make_question(1), "enabled": False, "disabled_reason": "보류"}
        errors = validate_questions([disabled], {"general": 1})
        self.assertTrue(any(e.startswith("난이도 'general' 문제 부족: 0개") for e in errors))

    def test_every_selection_entry_point_excludes_disabled_but_not_volatile_questions(self):
        active = {**make_question(1), "volatile": True, "volatile_note": "변경 가능"}
        disabled = {**make_question(2), "enabled": False, "disabled_reason": "보류"}
        questions = [active, disabled]
        for mode in ("pvp", "pve"):
            self.assertEqual(filter_questions_for_mode(questions, mode), [active])
        self.assertEqual(group_by_difficulty(questions), {"general": [active]})
        self.assertEqual(
            select_session_questions({"general": questions}, {"general": 1}), [active],
        )
        with self.assertRaises(QuestionDataError):
            select_session_questions({"general": [disabled]}, {"general": 1})

    def test_validated_loader_keeps_archives_out_of_the_runtime_bank(self):
        active = make_question(1)
        disabled = {**make_question(2), "enabled": False, "disabled_reason": "보류"}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "questions.json"
            path.write_text(json.dumps([active, disabled]), encoding="utf-8")
            self.assertEqual(load_questions(path), [active, disabled])
            self.assertEqual(load_validated_questions(path, {"general": 1}), [active])

    def test_unverified_questions_are_archived_without_claiming_new_sources(self):
        questions = load_questions(Path(__file__).resolve().parents[1] / "questions.json")
        disabled = [q for q in questions if q.get("enabled") is False]
        self.assertEqual({q["id"] for q in disabled}, {95, 102, 225, 226})
        for question in disabled:
            self.assertTrue(question["disabled_reason"])
            self.assertNotIn("reviewed_at", question)
            self.assertNotIn("sources", question)
        self.assertEqual(len(questions), 474)
        self.assertEqual(len(filter_questions_for_mode(questions, "pvp")), 468)
        self.assertEqual(len(filter_questions_for_mode(questions, "pve")), 457)

    def test_mode_filter_includes_common_and_requested_mode_only(self):
        common = make_question(1)
        pvp = {**make_question(2), "mode": "pvp"}
        pve = {**make_question(3), "mode": "pve"}

        self.assertEqual(
            [q["id"] for q in filter_questions_for_mode([common, pvp, pve], "pvp")],
            [1, 2],
        )
        self.assertEqual(
            [q["id"] for q in filter_questions_for_mode([common, pvp, pve], "pve")],
            [1, 3],
        )

    def test_validation_rejects_unknown_mode(self):
        question = {**make_question(1), "mode": "arena"}

        errors = validate_questions([question], {"general": 1})

        self.assertTrue(any("알 수 없는 mode" in error for error in errors))

    def test_validation_reports_shortage_in_one_mode_only(self):
        # 전체 2문제로 수량은 충족되지만, PvE 풀에는 1문제뿐이라 PvE만 부족해야 한다.
        questions = [
            {**make_question(1), "mode": "pvp"},
            {**make_question(2), "mode": "common"},
        ]

        errors = validate_questions(questions, {"general": 2})

        self.assertTrue(any("PVE 모드 난이도 'general' 문제 부족" in error for error in errors))
        self.assertFalse(any("PVP 모드" in error for error in errors))
        self.assertFalse(
            any(error.startswith("난이도 'general' 문제 부족") for error in errors)
        )

    def test_valid_questions_have_no_errors(self):
        questions = [make_question(1), make_question(2)]

        self.assertEqual(validate_questions(questions, {"general": 2}), [])

    def test_validation_finds_duplicate_id_and_shortage(self):
        questions = [make_question(1), make_question(1)]

        errors = validate_questions(questions, {"general": 2, "hard": 1})

        self.assertTrue(any("중복된 id" in error for error in errors))
        self.assertTrue(any("'hard' 문제 부족" in error for error in errors))

    def test_validation_rejects_non_positive_session_count(self):
        errors = validate_questions([make_question(1)], {"general": 0})

        self.assertTrue(any("1 이상의 정수" in error for error in errors))

    def test_selection_respects_counts_without_duplicate_ids(self):
        questions = [make_question(i) for i in range(1, 6)]
        questions += [make_question(i, "hard") for i in range(6, 10)]

        selected = select_session_questions(
            group_by_difficulty(questions),
            {"general": 3, "hard": 2},
            rng=random.Random(7),
        )

        self.assertEqual(len(selected), 5)
        self.assertEqual(len({question["id"] for question in selected}), 5)
        self.assertEqual(
            {
                difficulty: sum(q["difficulty"] == difficulty for q in selected)
                for difficulty in ("general", "hard")
            },
            {"general": 3, "hard": 2},
        )

    def test_selection_rejects_an_undersized_pool(self):
        with self.assertRaises(QuestionDataError):
            select_session_questions({"general": [make_question(1)]}, {"general": 2})

    def test_loader_rejects_non_array_root(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "questions.json"
            path.write_text(json.dumps({"id": 1}), encoding="utf-8")

            with self.assertRaises(QuestionDataError):
                load_questions(path)


if __name__ == "__main__":
    unittest.main()
