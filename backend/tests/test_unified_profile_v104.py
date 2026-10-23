from app.ai.unified_profile_v104 import combine_analysis


def ev(repo, quote='x=1'):
    return {'repository': repo, 'file': 'src/a.py', 'quote': quote, 'evidence_type': 'ast_source_usage'}


def test_public_only():
    public = {'analysis_type': 'ast_technology_usage', 'repositories': [{'repository': 'u/r', 'status': 'ok'}], 'skills': [{'name': 'Python', 'evidence_samples': [ev('u/r')]}]}
    result = combine_analysis(public)
    assert result['skill_count'] == 1 and result['source_count'] == 1
    assert result['skills'][0]['source_ids'] == ['u/r']


def test_private_only():
    private = {'project_id': 'p-abc', 'source_type': 'zip_upload', 'visibility': 'private', 'analysis_type': 'ast_technology_usage', 'skills': [{'name': 'Python', 'evidence_samples': [ev('private/p-abc')]}]}
    result = combine_analysis(None, [private])
    assert result['sources'][0]['visibility'] == 'private'
    assert result['skills'][0]['source_ids'] == ['private/p-abc']


def test_shared_skill_combined():
    public = {'analysis_type': 'ast_technology_usage', 'repositories': [{'repository': 'u/r', 'status': 'ok'}], 'skills': [{'name': 'Python', 'evidence_samples': [ev('u/r')]}]}
    private = {'project_id': 'p-abc', 'source_type': 'zip_upload', 'visibility': 'private', 'analysis_type': 'ast_technology_usage', 'skills': [{'name': 'Python', 'evidence_samples': [ev('private/p-abc')]}]}
    result = combine_analysis(public, [private])
    assert result['skill_count'] == 1 and result['skills'][0]['source_count'] == 2


def test_duplicate_evidence_deduplicated():
    public = {'analysis_type': 'ast_technology_usage', 'repositories': [], 'skills': [{'name': 'Python', 'evidence_samples': [ev('u/r'), ev('u/r')]}]}
    assert combine_analysis(public)['skills'][0]['sample_count'] == 1


def test_no_full_evidence_count_claim():
    public = {'analysis_type': 'ast_technology_usage', 'repositories': [], 'skills': [{'name': 'Python', 'evidence_count': 99, 'evidence_samples': [ev('u/r')]}]}
    result = combine_analysis(public)
    assert 'evidence_count' not in result['skills'][0]
    assert result['skills'][0]['sample_count'] == 1


def test_reject_wrong_private_visibility():
    import pytest
    with pytest.raises(ValueError):
        combine_analysis(None, [{'source_type': 'zip_upload', 'visibility': 'public', 'analysis_type': 'ast_technology_usage'}])
