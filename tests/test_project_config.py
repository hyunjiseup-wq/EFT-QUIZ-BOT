import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProjectConfigTests(unittest.TestCase):
    def test_gitignore_excludes_regenerable_packaging_output(self):
        patterns = set((ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())
        self.assertTrue({"build/", "dist/", "*.egg-info/"}.issubset(patterns))

    def test_readmes_link_full_audit_and_followup_without_claiming_completion(self):
        for filename in ("README.md", "README_EN.md"):
            with self.subTest(filename=filename):
                contents = (ROOT / filename).read_text(encoding="utf-8")
                self.assertIn("docs/full-question-audit-2026-09-23.md", contents)
                self.assertIn("Q144", contents)
                self.assertIn("Q469", contents)
                self.assertIn("Q471", contents)

    def test_requirements_match_pyproject_runtime_dependencies(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        match = re.search(r"(?ms)^dependencies\s*=\s*\[(.*?)^\]", pyproject)
        self.assertIsNotNone(match, "pyproject.toml의 dependencies 배열을 찾을 수 없습니다.")

        project_dependencies = {
            line.strip().rstrip(",").strip('"')
            for line in match.group(1).splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        requirements_dependencies = {
            line.strip()
            for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }

        self.assertEqual(requirements_dependencies, project_dependencies)

    def test_ci_does_not_duplicate_branch_push_and_pull_request_runs(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )

        self.assertRegex(workflow, r"(?m)^  push:\n    branches: \[main\]$")
        self.assertRegex(workflow, r"(?m)^  pull_request:$")

    def test_readme_question_counts_match_question_bank(self):
        questions = json.loads((ROOT / "questions.json").read_text(encoding="utf-8"))
        total_questions = len(questions)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_en = (ROOT / "README_EN.md").read_text(encoding="utf-8")

        korean_match = re.search(r"\*\*총 ([0-9,]+)문제\*\*", readme)
        english_match = re.search(r"holds \*\*([0-9,]+) questions\*\*", readme_en)
        self.assertIsNotNone(korean_match, "README.md에서 총 문제 수를 찾을 수 없습니다.")
        self.assertIsNotNone(
            english_match,
            "README_EN.md에서 총 문제 수를 찾을 수 없습니다.",
        )
        self.assertEqual(int(korean_match.group(1).replace(",", "")), total_questions)
        self.assertEqual(int(english_match.group(1).replace(",", "")), total_questions)

        mode_counts = {
            mode: sum(question.get("mode", "common") == mode for question in questions)
            for mode in ("common", "pvp", "pve")
        }
        self.assertIn(
            f"공통 {mode_counts['common']} · PvP 전용 {mode_counts['pvp']} · "
            f"PvE 전용 {mode_counts['pve']}",
            readme,
        )
        self.assertIn(
            f"{mode_counts['common']} common · {mode_counts['pvp']} PvP-only · "
            f"{mode_counts['pve']} PvE-only",
            readme_en,
        )
        for mode in ("pvp", "pve"):
            playable = sum(
                question.get("enabled", True) is True
                and question.get("mode", "common") in {"common", mode}
                for question in questions
            )
            label = "PvP" if mode == "pvp" else "PvE"
            self.assertIn(f"{label} {playable}문제", readme)
            self.assertIn(f"{label} {playable} (`common+{mode}`)", readme_en)
        enabled = sum(q.get("enabled", True) is True for q in questions)
        disabled = total_questions - enabled
        self.assertIn(f"활성 {enabled} · 출제 보류 {disabled}", readme)
        self.assertIn(f"{enabled} active · {disabled} on hold", readme_en)

    def test_readmes_report_review_coverage_without_claiming_full_verification(self):
        questions = json.loads((ROOT / "questions.json").read_text(encoding="utf-8"))
        volatile = sum(bool(q.get("volatile")) for q in questions)
        reviewed = sum(bool(q.get("reviewed_at") and q.get("sources")) for q in questions)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_en = (ROOT / "README_EN.md").read_text(encoding="utf-8")
        self.assertIn(f"**{volatile}문제가 `volatile`**", readme)
        self.assertIn(f"**근거·검토일 기록은 {reviewed}문항**", readme)
        self.assertIn(f"**{volatile} are `volatile`**", readme_en)
        self.assertIn(f"**{reviewed} questions have source/date records**", readme_en)
        for contents in (readme, readme_en):
            for link in re.findall(r"\]\((docs/[^)]+)\)", contents):
                self.assertTrue((ROOT / link).is_file(), f"문서 링크 누락: {link}")

    def test_readmes_list_every_registered_slash_command(self):
        bot_source = (ROOT / "bot.py").read_text(encoding="utf-8")
        command_names = re.findall(
            r"@bot\.tree\.command\(\s*name=\"([^\"]+)\"",
            bot_source,
        )
        self.assertEqual(len(command_names), 14)

        for readme_name in ("README.md", "README_EN.md"):
            contents = (ROOT / readme_name).read_text(encoding="utf-8")
            with self.subTest(readme=readme_name):
                missing = [name for name in command_names if f"`/{name}" not in contents]
                self.assertEqual(missing, [], f"명령어 목록에서 누락됨: {missing}")

    def test_readme_file_trees_include_all_python_modules_and_tests(self):
        readmes = {
            "README.md": (ROOT / "README.md").read_text(encoding="utf-8"),
            "README_EN.md": (ROOT / "README_EN.md").read_text(encoding="utf-8"),
        }
        expected_files = {path.name for path in ROOT.glob("*.py")}
        expected_files.update(path.name for path in (ROOT / "tests").glob("test_*.py"))

        for readme_name, contents in readmes.items():
            with self.subTest(readme=readme_name):
                missing = sorted(name for name in expected_files if name not in contents)
                self.assertEqual(missing, [], f"파일 구조에서 누락됨: {missing}")


if __name__ == "__main__":
    unittest.main()
