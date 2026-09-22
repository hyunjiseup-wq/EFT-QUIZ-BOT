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
