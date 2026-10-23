import pytest
from app.ai.readme_code_review_v106 import review_readme_against_code


def test_explicit_symbol_supported_by_ast():
    result = review_readme_against_code({'README.md': 'Use `find_valid_moves`.', 'src/moves.py': 'def find_valid_moves():\n    return []\n'})
    assert result['findings'][0]['status'] == 'source_present'
    assert result['findings'][0]['evidence'][0]['file'] == 'src/moves.py'


def test_symbol_in_comment_is_not_verified():
    result = review_readme_against_code({'README.md': 'Use `find_valid_moves`.', 'src/moves.py': '# find_valid_moves\npass\n'})
    assert result['findings'][0]['status'] == 'not_found_in_scanned_files'


def test_file_link_present():
    result = review_readme_against_code({'README.md': '[engine](src/engine.py)', 'src/engine.py': 'pass'})
    assert result['findings'][0]['status'] == 'source_present'


def test_missing_file_not_present():
    result = review_readme_against_code({'README.md': '[engine](src/engine.py)'})
    assert result['findings'][0]['status'] == 'not_found_in_scanned_files'


def test_external_link_ignored():
    result = review_readme_against_code({'README.md': '[website](https://example.org/code.py)'})
    assert result['findings'] == []


def test_traversal_link_ignored():
    result = review_readme_against_code({'README.md': '[secret](../../secret.py)'})
    assert result['findings'] == []


def test_relative_link_from_nested_readme():
    result = review_readme_against_code({'docs/README.md': '[engine](../src/engine.py)', 'src/engine.py': 'pass'})
    assert result['findings'][0]['status'] == 'source_present'


def test_readme_production_ready_not_verified():
    result = review_readme_against_code({'README.md': '# Production ready\nFully working!', 'src/main.py': 'print(1)'})
    assert result['findings'] == []
    assert result['assessment'] == 'readme_source_traceability_only'


def test_does_not_execute_code():
    result = review_readme_against_code({'README.md': '`danger`', 'src/x.py': 'def danger():\n    raise RuntimeError()'})
    assert result['code_executed'] is False


@pytest.mark.parametrize('path', ['../bad.py', '/root/bad.py'])
def test_reject_unsafe_input(path):
    with pytest.raises(ValueError):
        review_readme_against_code({path: 'secret'})
