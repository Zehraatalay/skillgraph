import pytest
from app.ai.code_review_agent_v108 import build_review_packet, validate_model_review, review_with_ollama


def test_packet_has_source_evidence():
    packet = build_review_packet({'src/a.py': 'try:\n    pass\nexcept:\n    pass\n'})
    assert packet['evidence'][0]['signal'] == 'bare_except'
    assert 'except:' in packet['evidence'][0]['snippet']
    assert packet['llm_calls'] is False


def test_empty_project():
    assert build_review_packet({})['evidence'] == []


def test_reject_bad_paths():
    with pytest.raises(ValueError):
        build_review_packet({'../bad.py': 'pass'})


def test_reject_bad_limit():
    with pytest.raises(ValueError):
        build_review_packet({'a.py': 'pass'}, max_items=99)


def test_valid_model_review():
    packet = build_review_packet({'a.py': 'try:\n    pass\nexcept:\n    pass'})
    result = validate_model_review(packet, {'findings': [{'evidence_ids': ['E1'], 'verdict': 'needs_context', 'explanation': 'Check intent.'}]})
    assert result['findings'][0]['verification'] == 'references_exist_only'


def test_hallucinated_id_rejected():
    packet = build_review_packet({'a.py': 'try:\n    pass\nexcept:\n    pass'})
    with pytest.raises(ValueError):
        validate_model_review(packet, {'findings': [{'evidence_ids': ['E99'], 'verdict': 'review_suggested', 'explanation': 'X'}]})


def test_unstructured_response_rejected():
    with pytest.raises(ValueError):
        validate_model_review({'evidence': []}, {'findings': 'looks fine'})


def test_remote_endpoint_rejected():
    with pytest.raises(ValueError):
        review_with_ollama({'a.py': 'pass'}, model='test', endpoint='https://example.com')


def test_no_proficiency_claim():
    packet = build_review_packet({'a.py': 'eval("1")'})
    result = validate_model_review(packet, {'findings': []})
    assert result['proficiency_assessed'] is False
