import ast
from pathlib import Path

from app.ai.validate_behaviors import _verify, review_report


def item(concept, line=1, quote='def example():'):
    return {'concept': concept, 'repository': 'user/repo', 'file': 'sample.py', 'function': 'example', 'line': line, 'quote': quote}


def test_without_source_never_verifies():
    result = review_report({'repository': 'user/repo', 'items': [item('Copy-and-update state transformation')]})
    assert result['counts'] == {'review_required': 1}


def test_cache_false_positive_rejected_with_source(tmp_path):
    src = 'def example():\n    board = [1]\n    x = board[0]\n    board[0] = x\n    return board\n'
    (tmp_path / 'sample.py').write_text(src)
    report = review_report({'repository': 'user/repo', 'items': [item('Explicit cache lookup and update')]}, tmp_path)
    assert report['counts']['rejected'] == 1


def test_copy_update_return_verified(tmp_path):
    src = 'def example(board):\n    result = board.copy()\n    result[0] = 0\n    return result\n'
    (tmp_path / 'sample.py').write_text(src)
    report = review_report({'repository': 'user/repo', 'items': [item('Copy-and-update state transformation', quote='result[0] = 0')]}, tmp_path)
    assert report['counts']['verified'] == 1
    assert report['items'][0]['implementation_depth'] == 'basic'


def test_different_object_not_verified():
    fn = ast.parse('def example(a, b):\n    result = a.copy()\n    b[0] = 0\n    return result\n').body[0]
    assert _verify('Copy-and-update state transformation', fn, 'sample.py')[0] == 'review_required'


def test_conditioned_append_verified():
    fn = ast.parse('def example(xs):\n    out = []\n    for x in xs:\n        if x > 0:\n            out.append(x)\n    return out\n').body[0]
    assert _verify('Conditional candidate enumeration', fn, 'sample.py')[0] == 'verified'


def test_unconditional_append_not_verified():
    fn = ast.parse('def example(xs):\n    out = []\n    for x in xs:\n        if x > 0:\n            pass\n        out.append(x)\n    return out\n').body[0]
    assert _verify('Conditional candidate enumeration', fn, 'sample.py')[0] == 'review_required'


def test_best_candidate_remains_review():
    fn = ast.parse('def example(xs):\n    for x in xs:\n        if x is None:\n            x = 1\n    return x\n').body[0]
    assert _verify('Iterative best-candidate selection', fn, 'sample.py')[0] == 'review_required'


def test_test_assertion_verified():
    fn = ast.parse('def example():\n    assert 1 + 1 == 2\n').body[0]
    assert _verify('Executable behavioral assertions', fn, 'tests/test_math.py')[0] == 'verified'


def test_assertion_outside_test_review():
    fn = ast.parse('def example():\n    assert True\n').body[0]
    assert _verify('Executable behavioral assertions', fn, 'src/core.py')[0] == 'review_required'


def test_path_traversal_rejected(tmp_path):
    bad = item('Executable behavioral assertions')
    bad['file'] = '../secret.py'
    result = review_report({'repository': 'user/repo', 'items': [bad]}, tmp_path)
    assert result['counts']['rejected'] == 1
