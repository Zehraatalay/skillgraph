import pytest
from app.ai.project_audit_v105 import audit_project

def test_positive_signals():
    result = audit_project({'README.md':'# App\n## Installation\n## Usage', 'src/app.py':'print(1)', 'tests/test_app.py':'def test_ok(): assert True', 'pyproject.toml':'[project]', '.github/workflows/test.yml':'jobs:'})
    assert all(result['signals'].values())
    assert result['code_executed'] is False

def test_readme_not_proof():
    result = audit_project({'README.md':'# Finished and production ready'})
    assert result['signals']['readme']
    assert not result['signals']['source_files']
    assert result['assessment'] == 'static_signals_only'

def test_no_test_not_claim_broken():
    result = audit_project({'src/main.py':'print(1)'})
    assert not result['signals']['test_files']
    assert 'Runtime functionality has not been tested.' in result['limitations']

@pytest.mark.parametrize('path', ['../secret.py', '/etc/passwd', 'a\\b.py'])
def test_unsafe_paths(path):
    with pytest.raises(ValueError): audit_project({path:'secret'})

def test_excludes_dependencies():
    result = audit_project({'node_modules/a.js':'x', 'src/main.ts':'x'})
    assert result['source_file_count'] == 1

def test_size_limit():
    with pytest.raises(ValueError): audit_project({'a.py':'x' * 1_048_577})
