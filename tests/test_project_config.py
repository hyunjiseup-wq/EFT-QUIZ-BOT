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


if __name__ == "__main__":
    unittest.main()
