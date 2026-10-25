import json

import pytest

from agents.schemas.evidence import (
    EvidenceSource,
    EvidenceType,
    SkillEvidence,
)
from agents.services.extraction_cache import ExtractionCache
from agents.services.github_analyzer import GitHubAnalyzer
from agents.services.research_collector import CollectedFile


class FakeGitHubClient:
    def __init__(self):
        self.repositories = [
            {
                "name": "project-a",
                "default_branch": "main",
                "fork": False,
                "archived": False,
                "html_url": "https://github.com/test/project-a",
            },
            {
                "name": "project-b",
                "default_branch": "main",
                "fork": True,
                "archived": False,
            },
            {
                "name": "project-c",
                "default_branch": "main",
                "fork": False,
                "archived": True,
            },
        ]

    def list_repositories(self, username):
        return self.repositories

    def get_repository_tree(self, owner, repo, ref):
        return {
            "tree": [
                {
                    "path": "src/main.py",
                    "type": "blob",
                }
            ]
        }


class FakeResearchService:
    def select_files(self, tree):
        return ["src/main.py"]


class FakeCollector:
    def __init__(self):
        self.content = "import numpy as np"

    def collect(
        self,
        owner,
        repo,
        ref,
        selected_files,
    ):
        return [
            CollectedFile(
                path="src/main.py",
                category="source",
                content=self.content,
            )
        ]


class FakeExtractor:
    def __init__(self):
        self.call_count = 0

    def extract(self, collected_files):
        self.call_count += 1

        return [
            SkillEvidence(
                skill="NumPy",
                source=EvidenceSource.GITHUB,
                evidence_type=EvidenceType.IMPLEMENTATION,
                reference="src/main.py",
                code_snippet="import numpy as np",
            )
        ]


def make_analyzer(
    tmp_path,
    client=None,
    collector=None,
    extractor=None,
    cache=None,
    max_repositories=3,
    model_id="test-model",
):
    return GitHubAnalyzer(
        github_client=client or FakeGitHubClient(),
        research_service=FakeResearchService(),
        collector=collector or FakeCollector(),
        extractor=extractor or FakeExtractor(),
        max_repositories=max_repositories,
        cache=cache or ExtractionCache(cache_dir=str(tmp_path / "extractions")),
        model_id=model_id,
    )


def test_analyzes_valid_repository(tmp_path):
    analyzer = make_analyzer(tmp_path)

    result = analyzer.analyze("testuser")

    assert result.username == "testuser"
    assert len(result.repositories) == 1

    repository = result.repositories[0]

    assert repository.repository_name == "project-a"
    assert repository.skills[0].skill == "NumPy"
    assert repository.analyzed_files == ["src/main.py"]


def test_skips_forks_and_archived_repositories(tmp_path):
    analyzer = make_analyzer(tmp_path)

    result = analyzer.analyze("testuser")

    names = [repo.repository_name for repo in result.repositories]

    assert names == ["project-a"]


def test_respects_repository_limit(tmp_path):
    client = FakeGitHubClient()

    client.repositories = [
        {
            "name": f"project-{i}",
            "default_branch": "main",
            "fork": False,
            "archived": False,
        }
        for i in range(5)
    ]

    analyzer = make_analyzer(
        tmp_path,
        client=client,
        max_repositories=2,
    )

    result = analyzer.analyze("testuser")

    assert len(result.repositories) == 2


def test_rejects_invalid_repository_limit(tmp_path):
    with pytest.raises(
        ValueError,
        match="max_repositories must be positive",
    ):
        make_analyzer(tmp_path, max_repositories=0)


def test_handles_empty_repositories(tmp_path):
    client = FakeGitHubClient()
    client.repositories = []

    analyzer = make_analyzer(tmp_path, client=client)

    result = analyzer.analyze("testuser")

    assert result.repositories == []


def test_github_analysis_uses_cache(tmp_path):
    extractor = FakeExtractor()

    analyzer = make_analyzer(
        tmp_path,
        extractor=extractor,
    )

    first_result = analyzer.analyze("testuser")
    second_result = analyzer.analyze("testuser")

    assert extractor.call_count == 1

    assert first_result.repositories[0].skills == second_result.repositories[0].skills


def test_github_cache_invalidates_on_source_change(tmp_path):
    collector = FakeCollector()
    extractor = FakeExtractor()

    analyzer = make_analyzer(
        tmp_path,
        collector=collector,
        extractor=extractor,
    )

    analyzer.analyze("testuser")

    assert extractor.call_count == 1

    collector.content = "import numpy as np\narray = np.array([1, 2, 3])"

    analyzer.analyze("testuser")

    assert extractor.call_count == 2


def test_github_cache_invalidates_on_model_change(tmp_path):
    cache = ExtractionCache(cache_dir=str(tmp_path / "extractions"))

    extractor = FakeExtractor()

    first_analyzer = make_analyzer(
        tmp_path,
        cache=cache,
        extractor=extractor,
        model_id="model-a",
    )

    second_analyzer = make_analyzer(
        tmp_path,
        cache=cache,
        extractor=extractor,
        model_id="model-b",
    )

    first_analyzer.analyze("testuser")
    second_analyzer.analyze("testuser")

    assert extractor.call_count == 2


def test_github_cache_recovers_from_corrupted_json(tmp_path):
    cache = ExtractionCache(cache_dir=str(tmp_path / "extractions"))

    extractor = FakeExtractor()

    analyzer = make_analyzer(
        tmp_path,
        cache=cache,
        extractor=extractor,
    )

    analyzer.analyze("testuser")

    cache_files = list((tmp_path / "extractions").glob("*.json"))

    assert len(cache_files) == 1

    cache_files[0].write_text(
        "{invalid json",
        encoding="utf-8",
    )

    analyzer.analyze("testuser")

    assert extractor.call_count == 2


def test_github_cache_recovers_from_invalid_evidence(tmp_path):
    cache = ExtractionCache(cache_dir=str(tmp_path / "extractions"))

    extractor = FakeExtractor()

    analyzer = make_analyzer(
        tmp_path,
        cache=cache,
        extractor=extractor,
    )

    analyzer.analyze("testuser")

    cache_files = list((tmp_path / "extractions").glob("*.json"))

    assert len(cache_files) == 1

    cache_files[0].write_text(
        json.dumps(
            {
                "skills": [
                    {
                        "skill": "NumPy",
                        "source": "invalid_source",
                        "evidence_type": "implementation",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    analyzer.analyze("testuser")

    assert extractor.call_count == 2


def test_failed_github_extraction_is_not_cached(tmp_path):
    class FailingExtractor:
        def __init__(self):
            self.call_count = 0

        def extract(self, collected_files):
            self.call_count += 1
            raise RuntimeError("Extraction failed")

    extractor = FailingExtractor()

    analyzer = make_analyzer(
        tmp_path,
        extractor=extractor,
    )

    with pytest.raises(
        RuntimeError,
        match="Extraction failed",
    ):
        analyzer.analyze("testuser")

    assert extractor.call_count == 1

    cache_files = list((tmp_path / "extractions").glob("*.json"))

    assert cache_files == []


def test_invalid_extracted_evidence_is_not_cached(tmp_path):
    class InvalidExtractor:
        def __init__(self):
            self.call_count = 0

        def extract(self, collected_files):
            self.call_count += 1

            return [
                SkillEvidence(
                    skill="NumPy",
                    source=EvidenceSource.GITHUB,
                    evidence_type=EvidenceType.IMPLEMENTATION,
                    reference="src/main.py",
                    code_snippet="fabricated_code()",
                )
            ]

    extractor = InvalidExtractor()

    analyzer = make_analyzer(
        tmp_path,
        extractor=extractor,
    )

    with pytest.raises(
        ValueError,
        match="Code snippet not found",
    ):
        analyzer.analyze("testuser")

    assert extractor.call_count == 1

    cache_files = list((tmp_path / "extractions").glob("*.json"))

    assert cache_files == []
