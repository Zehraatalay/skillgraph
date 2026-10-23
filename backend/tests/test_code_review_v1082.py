import pytest
from app.ai.code_review_agent_v108 import build_review_packet
from app.ai import code_review_v1082 as module


def packet():
    return build_review_packet({'a.py': 'try:\n    pass\nexcept:\n    pass\n'})


def finding(refs, verdict='needs_context'):
    return {'evidence_ids': refs, 'verdict': verdict, 'explanation': 'Check in context.'}


def test_accept_one_reject_twelve():
    p = packet()
    out = module.validate_partial(p, {'findings': [finding(['E1']), finding(['E1'] * 12)]})
    assert out['accepted_count'] == 1 and out['rejected_count'] == 1


def test_unknown_reference_rejected():
    assert module.validate_partial(packet(), {'findings': [finding(['E99'])]})['accepted_count'] == 0


def test_invalid_verdict_rejected():
    assert module.validate_partial(packet(), {'findings': [finding(['E1'], 'perfect')]})['rejected_count'] == 1


def test_malformed_top_level_rejected():
    with pytest.raises(ValueError):
        module.validate_partial(packet(), {'findings': 'wrong'})


def test_empty_evidence_skips_model(monkeypatch):
    monkeypatch.setattr(module, '_ask', lambda *a, **kw: pytest.fail('Should not call model'))
    out = module.review_with_ollama_v1082({}, model='qwen2.5-coder:7b')
    assert out['llm_calls'] is False and out['attempts'] == 0


def test_one_attempt_when_valid(monkeypatch):
    calls = []
    def fake(*args):
        calls.append(args)
        return {'findings': [finding(['E1'])]}
    monkeypatch.setattr(module, '_ask', fake)
    out = module.review_with_ollama_v1082({'a.py': 'try:\n pass\nexcept:\n pass'}, model='qwen')
    assert out['accepted_count'] == 1 and out['attempts'] == 1 and len(calls) == 1


def test_repair_after_rejected(monkeypatch):
    responses = iter([{'findings': [finding(['E1'] * 12)]}, {'findings': [finding(['E1'])]}])
    monkeypatch.setattr(module, '_ask', lambda *args: next(responses))
    out = module.review_with_ollama_v1082({'a.py': 'try:\n pass\nexcept:\n pass'}, model='qwen')
    assert out['accepted_count'] == 1 and out['rejected_count'] == 1 and out['attempts'] == 2


def test_repair_keeps_rejections(monkeypatch):
    monkeypatch.setattr(module, '_ask', lambda *args: {'findings': [finding(['E99'])]})
    out = module.review_with_ollama_v1082({'a.py': 'try:\n pass\nexcept:\n pass'}, model='qwen')
    assert out['accepted_count'] == 0 and out['rejected_count'] == 2


def test_remote_endpoint_blocked():
    with pytest.raises(ValueError):
        module.review_with_ollama_v1082({}, model='qwen', endpoint='http://evil.com:11434')


def test_bad_timeout_blocked():
    with pytest.raises(ValueError):
        module.review_with_ollama_v1082({}, model='qwen', timeout=180)


def test_more_than_fifty_model_findings_bounded():
    out = module.validate_partial(packet(), {'findings': [finding(['E1'])] * 100})
    assert out['accepted_count'] == 12 and out['rejected_count'] == 88
