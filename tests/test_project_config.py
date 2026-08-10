import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProjectConfigTests(unittest.TestCase):
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
        total_questions = len(
            json.loads((ROOT / "questions.json").read_text(encoding="utf-8"))
        )
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
