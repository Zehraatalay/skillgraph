"""V8.2: compact evidence without changing coverage or ranking."""
from app.matching.evidence_matching import rank_jobs, score_job


def _job(job_id='job-1', required=None, preferred=None):
    return {'job_id': job_id, 'title': 'Engineer', 'role_family': 'engineering',
            'seniority': 'junior', 'technology_stack_id': 'test',
            'required_skills': required or [], 'preferred_skills': preferred or []}


def _row(i, quote, kind='ast_source_usage', skill='Python'):
    return {'skill': skill, 'evidence_id': f'id-{i}', 'repository': 'a/repo',
            'file': f'file_{i}.py', 'quote': quote, 'evidence_type': kind,
            'explanation': 'test'}


def test_caps_response_but_keeps_full_count():
    rows = [_row(i, f'X_{i} = {i}') for i in range(8)]
    result = rank_jobs([_job(required=[{'name': 'Python'}])], rows, 5)
    skill = result['matches'][0]['verified_required_skills'][0]
    assert skill['evidence_count'] == 8
    assert len(skill['evidence']) == 3
    assert result['matches'][0]['verified_skill_coverage_score'] == 100.0


def test_prefers_functions_over_constants():
    rows = [_row(0, 'A = 1'), _row(1, 'B = 2'), _row(2, 'C = 3'),
            _row(3, 'def calculate(x):'), _row(4, 'class Engine:')]
    result = rank_jobs([_job(required=[{'name': 'python'}])], rows, 1)
    quotes = [e['quote'] for e in result['matches'][0]['verified_required_skills'][0]['evidence']]
    assert quotes[:2] == ['def calculate(x):', 'class Engine:']


def test_prefers_ast_api_usage():
    rows = [_row(0, 'A = 1'), _row(1, 'def load():'),
            _row(2, 'torch.manual_seed(1)', 'ast_api_usage')]
    result = rank_jobs([_job(required=[{'name': 'python'}])], rows, 1)
    assert result['matches'][0]['verified_required_skills'][0]['evidence'][0]['quote'] == 'torch.manual_seed(1)'


def test_score_and_order_unchanged():
    jobs = [_job('b', required=[{'name': 'Python', 'weight': 1}, {'name': 'Docker', 'weight': 1}],
                 preferred=[{'name': 'PyTorch', 'weight': 1}]),
            _job('a', required=[{'name': 'Python', 'weight': 1}])]
    rows = [_row(0, 'def f():'), _row(1, 'torch.tensor(1)', 'ast_api_usage', 'PyTorch')]
    result = rank_jobs(jobs, rows, 2)
    assert [m['job_id'] for m in result['matches']] == ['a', 'b']
    assert result['matches'][0]['verified_skill_coverage_score'] == 100.0
    assert result['matches'][1]['verified_skill_coverage_score'] == 60.0


def test_duplicate_evidence_not_counted_twice():
    row = _row(0, 'def f():')
    result = rank_jobs([_job(required=[{'name': 'Python'}])], [row, row], 1)
    assert result['matches'][0]['verified_required_skills'][0]['evidence_count'] == 1


def test_unverified_and_empty_requirements():
    result = score_job(_job(required=[{'name': 'Docker'}]), {})
    assert result['verified_skill_coverage_score'] == 0
    assert result['unverified_required_skills'] == ['docker']
    assert result['required_coverage'] == 0
    assert result['preferred_coverage'] is None
