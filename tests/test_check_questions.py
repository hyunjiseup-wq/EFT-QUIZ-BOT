import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import check_questions


class QuestionCheckTests(unittest.TestCase):
    def test_disabled_report_distinguishes_archived_and_playable_counts(self):
        output = io.StringIO()
        with patch("sys.argv", ["check_questions.py", "--disabled"]), redirect_stdout(output):
            check_questions.main()
        report = output.getvalue()
        self.assertIn("총 474문제 (활성 470 · 출제 보류 4)", report)
        self.assertIn("PVP 출제 가능: 469문제", report)
        self.assertIn("PVE 출제 가능: 457문제", report)
        for qid in (95, 102, 225, 226):
            self.assertIn(f"[id {qid} · 출제 보류]", report)
        self.assertNotIn("현재 정답:", report)

    def test_volatile_report_labels_held_answers_as_records(self):
        output = io.StringIO()
        with patch("sys.argv", ["check_questions.py", "--volatile"]), redirect_stdout(output):
            check_questions.main()
        report = output.getvalue()
        self.assertIn("상태: 출제 보류", report)
        self.assertIn("보류 사유:", report)
        self.assertIn("기록된 정답:", report)
        self.assertNotIn("현재 정답:", report)


if __name__ == "__main__":
    unittest.main()
