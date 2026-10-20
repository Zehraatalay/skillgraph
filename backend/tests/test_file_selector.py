import unittest
from app.ai.file_selector import is_candidate, select_files


class SelectorTests(unittest.TestCase):
    def test_sensitive_files(self):
        for path in ('.env', 'secrets.json', 'node_modules/a.py', 'keys/private_key.pem', '../oops.py'):
            self.assertFalse(is_candidate(path, 100), path)

    def test_priority(self):
        tree = [{'path': x, 'type': 'blob', 'size': 10} for x in ('src/z.py', 'README.md', 'requirements.txt')]
        self.assertEqual([x['path'] for x in select_files(tree, max_files=2)], ['README.md', 'requirements.txt'])
