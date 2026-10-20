import unittest
from app.ai.file_selector import select_files


def blob(path):
    return {'path': path, 'type': 'blob', 'size': 100}


class FileSelectorDiversityTests(unittest.TestCase):
    def test_core_agent_files_selected_despite_many_ordinary_files(self):
        tree = [blob(f'src/a_{i:02}.py') for i in range(40)]
        tree += [blob('src/agents/dqn_agent.py'), blob('src/agents/ppo_agent.py'), blob('README.md'), blob('pyproject.toml')]
        selected = [item['path'] for item in select_files(tree, max_files=8)]
        self.assertIn('README.md', selected)
        self.assertIn('pyproject.toml', selected)
        self.assertIn('src/agents/dqn_agent.py', selected)
        self.assertIn('src/agents/ppo_agent.py', selected)
        self.assertLessEqual(len(selected), 8)

    def test_tests_cannot_crowd_out_implementation(self):
        tree = [blob(f'tests/test_{i:02}.py') for i in range(30)] + [blob('src/agent.py'), blob('src/engine.py')]
        selected = [item['path'] for item in select_files(tree, max_files=4)]
        self.assertIn('src/agent.py', selected)
        self.assertIn('src/engine.py', selected)

    def test_existing_priority_contract(self):
        tree = [blob(x) for x in ('src/z.py', 'README.md', 'requirements.txt')]
        self.assertEqual([x['path'] for x in select_files(tree, max_files=2)], ['README.md', 'requirements.txt'])

    def test_sensitive_paths_still_excluded(self):
        tree = [blob(x) for x in ('src/agent.py', '.env', 'src/api_token.py', 'node_modules/agent.py')]
        self.assertEqual([x['path'] for x in select_files(tree)], ['src/agent.py'])


if __name__ == '__main__':
    unittest.main()
