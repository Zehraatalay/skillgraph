import pytest
from app.ai.context_review_v1083 import build_context_packet, review_function_with_ollama

FILES = {
    'src/engine.py': 'def helper(x):\n    return x + 1\n\ndef step(x):\n    return helper(x)\n',
    'tests/test_engine.py': 'def test_step():\n    assert True\n',
}

def test_target_extraction():
    p = build_context_packet(FILES, file='src/engine.py', symbol='step')
    assert p['evidence'][0]['snippet'] == 'def step(x):\n    return helper(x)'
    assert p['evidence'][0]['complete_function']

def test_helper_association():
    p = build_context_packet(FILES, file='src/engine.py', symbol='step')
    assert any(e['role'] == 'called_helper_candidate' and e['symbol'] == 'helper' for e in p['evidence'])

def test_test_association_not_coverage():
    p = build_context_packet(FILES, file='src/engine.py', symbol='step')
    assert any(e['role'] == 'test_candidate' for e in p['evidence'])
    assert p['test_association'] == 'heuristic_not_coverage'

def test_missing_target():
    with pytest.raises(ValueError, match='not found'):
        build_context_packet(FILES, file='src/engine.py', symbol='absent')

def test_oversized_target_rejected():
    files = {'a.py': 'def step():\n' + '    x = 1\n' * 1600}
    with pytest.raises(ValueError, match='exceeds context budget'):
        build_context_packet(files, file='a.py', symbol='step')

def test_unsafe_path_rejected():
    with pytest.raises(ValueError, match='Unsafe path'):
        build_context_packet({'../bad.py': 'def f(): pass'}, file='../bad.py', symbol='f')

def test_no_llm_on_invalid_target(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError('should not call model')
    monkeypatch.setattr('app.ai.context_review_v1083._ask', fail)
    with pytest.raises(ValueError):
        review_function_with_ollama(FILES, file='src/engine.py', symbol='missing')

def test_valid_llm_output(monkeypatch):
    monkeypatch.setattr('app.ai.context_review_v1083._ask', lambda *a, **k: {
        'findings': [{'evidence_ids': ['E1'], 'verdict': 'needs_context', 'explanation': 'Check edge cases.'}]})
    r = review_function_with_ollama(FILES, file='src/engine.py', symbol='step')
    assert r['accepted_count'] == 1 and r['attempts'] == 1

def test_invalid_reference_rejected(monkeypatch):
    monkeypatch.setattr('app.ai.context_review_v1083._ask', lambda *a, **k: {
        'findings': [{'evidence_ids': ['E99'], 'verdict': 'needs_context', 'explanation': 'No.'}]})
    r = review_function_with_ollama(FILES, file='src/engine.py', symbol='step')
    assert r['accepted_count'] == 0 and r['rejected_count'] == 1

def test_remote_endpoint_rejected():
    with pytest.raises(ValueError, match='local Ollama'):
        review_function_with_ollama(FILES, file='src/engine.py', symbol='step', endpoint='http://example.com:11434')
