import hashlib
import json

from agents.schemas.evidence import SkillEvidence
from agents.schemas.github import (
    GitHubAnalysis,
    RepositoryAnalysis,
)
from agents.services.extraction_cache import ExtractionCache
from agents.services.github_client import GitHubClient
from agents.services.github_evidence_extractor import (
    SYSTEM_PROMPT,
    GitHubEvidenceExtractor,
)
from agents.services.github_evidence_validator import (
    validate_github_evidence,
)
from agents.services.repository_research import (
    RepositoryResearchService,
)
from agents.services.research_collector import (
    RepositoryResearchCollector,
)


class GitHubAnalyzer:
    def __init__(
        self,
        github_client: GitHubClient,
        research_service: RepositoryResearchService,
        collector: RepositoryResearchCollector,
        extractor: GitHubEvidenceExtractor,
        max_repositories: int = 3,
        cache: ExtractionCache | None = None,
        model_id: str = "unknown",
    ):
        if max_repositories < 1:
            raise ValueError("max_repositories must be positive")

        self.github_client = github_client
        self.research_service = research_service
        self.collector = collector
        self.extractor = extractor
        self.max_repositories = max_repositories
        self.cache = cache or ExtractionCache()
        self.model_id = model_id

    def _cache_content(
        self,
        username: str,
        repository_name: str,
        collected_files,
    ) -> str:

        source_files = sorted(
            (file for file in collected_files if file.category == "source"),
            key=lambda file: file.path,
        )

        files_payload = [
            {
                "path": file.path,
                "content": file.content,
                "truncated": file.truncated,
            }
            for file in source_files
        ]

        prompt_hash = hashlib.sha256(SYSTEM_PROMPT.encode("utf-8")).hexdigest()

        payload = {
            "cache_version": 1,
            "username": username,
            "repository": repository_name,
            "model": self.model_id,
            "prompt_hash": prompt_hash,
            "files": files_payload,
        }

        return json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
        )

    def analyze(
        self,
        username: str,
    ) -> GitHubAnalysis:

        repositories = self.github_client.list_repositories(username)

        selected_repositories = [
            repo
            for repo in repositories
            if not repo.get("fork", False)
            and not repo.get("archived", False)
            and repo.get("default_branch")
        ][: self.max_repositories]

        analyzed_repositories = []

        for repository in selected_repositories:
            repository_name = repository["name"]
            branch = repository["default_branch"]

            tree = self.github_client.get_repository_tree(
                owner=username,
                repo=repository_name,
                ref=branch,
            )

            selected_files = self.research_service.select_files(tree)

            collected_files = self.collector.collect(
                owner=username,
                repo=repository_name,
                ref=branch,
                selected_files=selected_files,
            )

            cache_content = self._cache_content(
                username=username,
                repository_name=repository_name,
                collected_files=collected_files,
            )

            cached = self.cache.get(
                namespace="github_evidence",
                content=cache_content,
            )

            skills = None

            if cached is not None:
                try:
                    skills = [
                        SkillEvidence.model_validate(item) for item in cached["skills"]
                    ]

                    source_files = [
                        file for file in collected_files if file.category == "source"
                    ]

                    validate_github_evidence(
                        evidence=skills,
                        collected_files=source_files,
                    )

                except (
                    KeyError,
                    TypeError,
                    ValueError,
                ):
                    skills = None

            if skills is None:
                skills = self.extractor.extract(collected_files)

                source_files = [
                    file for file in collected_files if file.category == "source"
                ]

                validate_github_evidence(
                    evidence=skills,
                    collected_files=source_files,
                )

                self.cache.set(
                    namespace="github_evidence",
                    content=cache_content,
                    result={
                        "skills": [skill.model_dump(mode="json") for skill in skills]
                    },
                )
            analyzed_repositories.append(
                RepositoryAnalysis(
                    repository_name=repository_name,
                    repository_url=repository.get("html_url"),
                    skills=skills,
                    analyzed_files=[file.path for file in collected_files],
                )
            )

        return GitHubAnalysis(
            username=username,
            repositories=analyzed_repositories,
        )
