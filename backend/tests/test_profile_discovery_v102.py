import pytest
from app.ai.profile_discovery_v102 import discover, analyze_selected

class FakeGithub:
    def get_user_repositories(self, username):
        return [
            {'name': 'alpha', 'private': False, 'fork': False, 'language': 'Python'},
            {'name': 'beta', 'private': False, 'fork': True, 'language': 'Python'},
            {'name': 'secret', 'private': True, 'fork': False},
        ]
    def get_repository_tree(self, owner, repo):
        return [{'path': 'main.py', 'type': 'blob', 'size': 35}]
    def get_repository_text_file(self, owner, repo, path):
        return 'def run():\n    return 1\n'


def test_discovery_hides_private_and_forks():
    data = discover(FakeGithub(), 'alice')
    assert [r['name'] for r in data['repositories']] == ['alpha']

def test_discovery_can_include_forks():
    data = discover(FakeGithub(), 'alice', include_forks=True)
    assert {r['name'] for r in data['repositories']} == {'alpha', 'beta'}

def test_private_selection_denied():
    with pytest.raises(ValueError, match='public discovery'):
        analyze_selected(FakeGithub(), 'alice', ['secret'])

def test_selected_analysis_no_writes():
    data = analyze_selected(FakeGithub(), 'alice', ['alpha'])
    assert data['neo4j_writes'] is False
    assert data['repositories'][0]['status'] == 'ok'
    assert any(s['name'] == 'Python' for s in data['skills'])

def test_selection_dedup():
    data = analyze_selected(FakeGithub(), 'alice', ['alpha', 'ALPHA'])
    assert len(data['repositories']) == 1

def test_invalid_names():
    with pytest.raises(ValueError): discover(FakeGithub(), '../etc')

@pytest.mark.parametrize('count', [0, 6])
def test_selection_limit(count):
    with pytest.raises(ValueError): analyze_selected(FakeGithub(), 'alice', ['alpha']*count)

def test_missing_repository_denied():
    with pytest.raises(ValueError): analyze_selected(FakeGithub(), 'alice', ['not-here'])
