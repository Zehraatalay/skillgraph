import pytest
from app.ai.code_quality_v107 import review_code_quality


def test_parse_and_symbols():
    result = review_code_quality({'src/a.py': 'class A: pass\ndef run() -> None: pass\n'})
    assert result['summary']['class_definitions'] == 1
    assert result['summary']['function_definitions'] == 1
    assert result['code_executed'] is False


def test_bare_except():
    result = review_code_quality({'src/a.py': 'try:\n    x = 1\nexcept:\n    pass\n'})
    assert result['finding_counts']['bare_except'] == 1


def test_eval_is_review_not_vulnerability_claim():
    result = review_code_quality({'src/a.py': 'eval("1+1")\n'})
    assert result['findings'][0]['signal'] == 'dynamic_execution_call'


def test_nested_iteration():
    result = review_code_quality({'src/a.py': 'for a in range(3):\n    for b in range(2):\n        pass\n'})
    assert result['finding_counts']['nested_iteration'] == 1


def test_test_function_count():
    result = review_code_quality({'tests/test_demo.py': 'def test_thing():\n    assert True\n'})
    assert result['summary']['test_function_definitions'] == 1


def test_syntax_error_does_not_crash():
    result = review_code_quality({'a.py': 'def broken(:\n'})
    assert result['summary']['python_parse_failures'] == 1


def test_excluded_directory():
    result = review_code_quality({'.venv/a.py': 'eval("x")', 'src/b.py': 'x=1'})
    assert result['summary']['python_files_parsed'] == 1
    assert 'dynamic_execution_call' not in result['finding_counts']


def test_reject_unsafe_path():
    with pytest.raises(ValueError):
        review_code_quality({'../escape.py': 'x=1'})


def test_deterministic():
    files = {'b.py': 'def f(): pass', 'a.py': 'with open("a") as f: pass'}
    assert review_code_quality(files) == review_code_quality(dict(reversed(list(files.items()))))


def test_no_false_completion_claim():
    result = review_code_quality({'main.py': 'print("hi")'})
    assert result['limitations']
    assert 'quality_score' not in result
