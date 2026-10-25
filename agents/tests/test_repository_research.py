from agents.services.repository_research import (
    RepositoryResearchService,
)


def test_selects_implementation_and_test_files():
    tree = {
        "tree": [
            {"path": "README.md", "type": "blob"},
            {"path": "src/__init__.py", "type": "blob"},
            {"path": "src/engine.py", "type": "blob"},
            {"path": "src/board.py", "type": "blob"},
            {"path": "tests/test_engine.py", "type": "blob"},
            {"path": "node_modules/package/index.js", "type": "blob"},
        ]
    }

    service = RepositoryResearchService()

    files = service.select_files(tree)

    paths = [file.path for file in files]

    assert "src/engine.py" in paths
    assert "src/board.py" in paths
    assert "tests/test_engine.py" in paths

    assert "README.md" not in paths
    assert "src/__init__.py" not in paths
    assert "node_modules/package/index.js" not in paths


def test_respects_file_limits():
    tree = {
        "tree": [{"path": f"src/module_{i}.py", "type": "blob"} for i in range(20)]
        + [{"path": f"tests/test_module_{i}.py", "type": "blob"} for i in range(10)]
    }

    service = RepositoryResearchService(
        max_source_files=5,
        max_test_files=2,
    )

    files = service.select_files(tree)

    source_files = [file for file in files if file.category == "source"]

    test_files = [file for file in files if file.category == "test"]

    assert len(source_files) == 5
    assert len(test_files) == 2


def test_prioritizes_core_implementation():
    tree = {
        "tree": [
            {"path": "src/utils.py", "type": "blob"},
            {"path": "src/engine.py", "type": "blob"},
            {"path": "src/helpers.py", "type": "blob"},
        ]
    }

    service = RepositoryResearchService(
        max_source_files=1,
    )

    files = service.select_files(tree)

    assert files[0].path == "src/engine.py"


def test_ignores_non_blob_items():
    tree = {
        "tree": [
            {"path": "src", "type": "tree"},
            {"path": "src/engine.py", "type": "blob"},
        ]
    }

    service = RepositoryResearchService()

    files = service.select_files(tree)

    assert len(files) == 1
    assert files[0].path == "src/engine.py"
