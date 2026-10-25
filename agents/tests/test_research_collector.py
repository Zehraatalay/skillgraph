from agents.services.repository_research import ResearchFile
from agents.services.research_collector import (
    RepositoryResearchCollector,
)


class FakeGitHubClient:
    def __init__(self, files):
        self.files = files
        self.calls = []

    def get_file_content(
        self,
        owner,
        repo,
        path,
        ref,
    ):
        self.calls.append(path)

        return self.files[path]


def test_collects_selected_files():
    client = FakeGitHubClient(
        {
            "src/engine.py": "class Engine: pass",
            "tests/test_engine.py": "def test_engine(): pass",
        }
    )

    collector = RepositoryResearchCollector(client)

    files = [
        ResearchFile("src/engine.py", "source"),
        ResearchFile("tests/test_engine.py", "test"),
    ]

    result = collector.collect(
        "exampleuser",
        "match3-ai-lab",
        "main",
        files,
    )

    assert len(result) == 2

    assert result[0].path == "src/engine.py"
    assert result[0].category == "source"

    assert result[1].category == "test"


def test_skips_empty_files():
    client = FakeGitHubClient(
        {
            "src/empty.py": "   ",
            "src/engine.py": "class Engine: pass",
        }
    )

    collector = RepositoryResearchCollector(client)

    files = [
        ResearchFile("src/empty.py", "source"),
        ResearchFile("src/engine.py", "source"),
    ]

    result = collector.collect(
        "exampleuser",
        "repo",
        "main",
        files,
    )

    assert len(result) == 1
    assert result[0].path == "src/engine.py"


def test_truncates_large_files():
    client = FakeGitHubClient(
        {
            "src/large.py": "A" * 100,
        }
    )

    collector = RepositoryResearchCollector(
        client,
        max_chars_per_file=20,
    )

    result = collector.collect(
        "exampleuser",
        "repo",
        "main",
        [ResearchFile("src/large.py", "source")],
    )

    assert len(result[0].content) == 20
    assert result[0].truncated is True


def test_respects_total_budget():
    client = FakeGitHubClient(
        {
            "src/a.py": "A" * 30,
            "src/b.py": "B" * 30,
            "src/c.py": "C" * 30,
        }
    )

    collector = RepositoryResearchCollector(
        client,
        max_chars_per_file=30,
        max_total_chars=50,
    )

    files = [
        ResearchFile("src/a.py", "source"),
        ResearchFile("src/b.py", "source"),
        ResearchFile("src/c.py", "source"),
    ]

    result = collector.collect(
        "exampleuser",
        "repo",
        "main",
        files,
    )

    assert len(result) == 2

    assert len(result[0].content) == 30
    assert len(result[1].content) == 20

    assert client.calls == [
        "src/a.py",
        "src/b.py",
    ]


def test_invalid_limits():
    client = FakeGitHubClient({})

    try:
        RepositoryResearchCollector(
            client,
            max_chars_per_file=0,
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass
