import unittest
from app.services.skill_extraction import extract_dependencies

class SkillExtractionTests(unittest.TestCase):
    def test_requirements(self):
        self.assertEqual(extract_dependencies("requirements.txt", "torch==2.0\nlightgbm>=4\n# tensorflow\n"), {"pytorch", "lightgbm"})

    def test_package_json(self):
        self.assertEqual(extract_dependencies("package.json", '{"dependencies":{"vue":"^3", "axios":"*"}}'), {"vue.js", "axios"})

    def test_invalid_json(self):
        self.assertEqual(extract_dependencies("package.json", "invalid"), set())

    def test_pyproject(self):
        self.assertEqual(extract_dependencies("pyproject.toml", '[project]\ndependencies=["fastapi>=0.1", "pandas"]'), {"fastapi", "pandas"})

if __name__ == "__main__":
    unittest.main()
