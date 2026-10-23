from app.ai.evidence_verification_v1084 import verify_finding, verify_review

ENGINE = '''class Match3Engine:
    def __init__(self, max_cascades=100):
        if max_cascades <= 0:
            raise ValueError()
        self.max_cascades = max_cascades
    def step(self):
        while True:
            if self.max_cascades <= 0:
                raise RuntimeError()
'''
TESTS = '''import numpy as np

def test_valid_swap_resolves_matches():
    result = engine.step(state, action)
    assert detect_patterns(result.state.tiles) == []

def test_invalid_swap_does_not_change_state():
    result = engine.step(state, action)
    assert result.valid is False
    assert np.array_equal(result.state.tiles, state.tiles)
'''
FILES = {'engine.py': ENGINE, 'tests/test_engine.py': TESTS}
PACKET = {'target': {'file': 'engine.py', 'symbol': 'Match3Engine.step'}, 'evidence': [
    {'id': 'E1', 'file': 'engine.py', 'symbol': 'Match3Engine.step', 'complete_function': True},
    {'id': 'E2', 'file': 'tests/test_engine.py', 'symbol': 'test_valid_swap_resolves_matches', 'complete_function': True},
    {'id': 'E3', 'file': 'tests/test_engine.py', 'symbol': 'test_invalid_swap_does_not_change_state', 'complete_function': True},
    {'id': 'E4', 'file': 'engine.py', 'symbol': 'clear_board_matches', 'complete_function': True},
    {'id': 'E5', 'file': 'engine.py', 'symbol': 'apply_board_gravity', 'complete_function': True},
]}


def check(text, ids):
    return verify_finding({'explanation': text, 'evidence_ids': ids}, PACKET, FILES)


def test_constructor_default_contradicts_missing_default_claim():
    r = check('max_cascades is not set, leading to an infinite loop', ['E1'])
    assert r['status'] == 'contradicted'
    assert '100' in r['reason']
    assert r['runtime_verified'] is False


def test_detect_patterns_assertion_contradicts_test_claim():
    r = check('test_valid_swap_resolves_matches does not verify that all matches resolve', ['E1', 'E2'])
    assert r['status'] == 'contradicted'
    assert r['method'] == 'test_assertion_ast'


def test_array_equal_contradicts_no_state_comparison_claim():
    r = check('test_invalid_swap_does_not_change_state does not verify unchanged state', ['E1', 'E3'])
    assert r['status'] == 'contradicted'
    assert 'full state equality is not proven' in r['reason']


def test_empty_matches_requires_call_context():
    assert check('clear_board_matches makes a copy when matches is empty', ['E1', 'E4'])['status'] == 'insufficient_evidence'


def test_gravity_claim_not_confirmed():
    assert check('apply_board_gravity does not handle empty playable_rows', ['E1', 'E5'])['status'] == 'insufficient_evidence'


def test_unknown_claim_abstains():
    assert check('This method is hard to maintain', ['E1'])['status'] == 'not_machine_verifiable'


def test_invalid_evidence_abstains():
    assert check('max_cascades is not set', ['E99'])['status'] == 'insufficient_evidence'


def test_incomplete_evidence_abstains():
    packet = {'target': PACKET['target'], 'evidence': [{'id': 'E1', 'complete_function': False}]}
    assert verify_finding({'explanation': 'max_cascades is not set', 'evidence_ids': ['E1']}, packet, FILES)['status'] == 'insufficient_evidence'


def test_no_default_not_claimed_contradicted():
    files = {'engine.py': 'class Match3Engine:\n    def __init__(self, max_cascades):\n        pass\n'}
    r = verify_finding({'explanation': 'max_cascades is not set', 'evidence_ids': ['E1']}, PACKET, files)
    assert r['status'] == 'insufficient_evidence'


def test_report_preserves_original_findings_and_counts():
    original = {'evidence_packet': PACKET, 'findings': [
        {'evidence_ids': ['E1'], 'explanation': 'max_cascades is not set'},
        {'evidence_ids': ['E1'], 'explanation': 'Maybe too complex'},
    ], 'accepted_count': 2}
    output = verify_review(original, FILES)
    assert output['verification_counts']['contradicted'] == 1
    assert output['verification_counts']['not_machine_verifiable'] == 1
    assert 'evidence_verification' not in original['findings'][0]
    assert output['accepted_count'] == 2


def test_missing_test_is_not_proof_of_absence():
    files = dict(FILES)
    files['tests/test_engine.py'] = 'def test_valid_swap_resolves_matches():\n    assert True\n'
    r = verify_finding({'explanation': 'test_valid_swap_resolves_matches does not verify matches', 'evidence_ids': ['E2']}, PACKET, files)
    assert r['status'] == 'insufficient_evidence'
