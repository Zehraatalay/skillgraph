import unittest
from app.ai.repository_scanner import RepositoryScanner


class FakeGithub:
    def get_repository_tree(self, owner, repo):
        return [
            {'path': 'README.md', 'type': 'blob', 'size': 20},
            {'path': 'src/train.py', 'type': 'blob', 'size': 40},
            {'path': '.env', 'type': 'blob', 'size': 20},
            {'path': 'node_modules/foo.py', 'type': 'blob', 'size': 20},
        ]

    def get_repository_text_file(self, owner, repo, path):
        return {'README.md': '# Example', 'src/train.py': 'import torch'}.get(path)


class ScannerTests(unittest.TestCase):
    def test_excludes_secrets_and_dependencies(self):
        result = RepositoryScanner(FakeGithub()).scan('owner', 'repo')
        self.assertEqual([f.path for f in result.files], ['README.md', 'src/train.py'])

    def test_total_character_budget(self):
        result = RepositoryScanner(FakeGithub(), max_total_chars=12).scan('owner', 'repo')
        self.assertLessEqual(result.total_characters, 12)
