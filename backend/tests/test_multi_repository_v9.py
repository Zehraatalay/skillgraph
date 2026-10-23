from pathlib import Path

import pytest

from app.ai.multi_repository import analyze_repositories


class FakeGitHub:
    def get_repository_tree(self, owner, repository):
        if repository == 'broken':
            raise RuntimeError('GitHub unavailable')
        return [{'path': 'src/main.py', 'type': 'blob', 'size': 80}]

    def get_repository_text_file(self, owner, repository, path):
        return 'import torch\n\ndef main():\n    return torch.zeros(2)\n'


def test_multi_repo_provenance_and_separation(tmp_path):
    report = analyze_repositories(FakeGitHub(), 'dev', ['one', 'two'], tmp_path)
    assert [r['status'] for r in report['results']] == ['ok', 'ok']
    for repo in ('one', 'two'):
        from app.ai.skill_profile import ValidatedSkillProfile
        profile = ValidatedSkillProfile.model_validate_json((tmp_path / f'dev__{repo}.json').read_text())
        assert profile.repository == f'dev/{repo}'
        assert {s.name for s in profile.skills} == {'Python', 'PyTorch'}
        assert all(e.repository == f'dev/{repo}' for s in profile.skills for e in s.evidence)


def test_failure_does_not_stop_next_repository(tmp_path):
    result = analyze_repositories(FakeGitHub(), 'dev', ['broken', 'ok'], tmp_path)
    assert [r['status'] for r in result['results']] == ['error', 'ok']


def test_existing_profile_is_not_overwritten(tmp_path):
    target = tmp_path / 'dev__one.json'
    target.write_text('existing')
    result = analyze_repositories(FakeGitHub(), 'dev', ['one'], tmp_path)
    assert result['results'][0]['status'] == 'skipped_existing'
    assert target.read_text() == 'existing'


def test_duplicate_repo_only_scanned_once(tmp_path):
    result = analyze_repositories(FakeGitHub(), 'dev', ['one', 'one'], tmp_path)
    assert len(result['results']) == 1


def test_reject_invalid_repository(tmp_path):
    with pytest.raises(ValueError):
        analyze_repositories(FakeGitHub(), 'dev', ['../escape'], tmp_path)
