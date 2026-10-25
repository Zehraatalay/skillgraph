from dataclasses import dataclass

from agents.services.repository_research import ResearchFile


@dataclass(frozen=True)
class CollectedFile:
    path: str
    category: str
    content: str
    truncated: bool = False


class RepositoryResearchCollector:
    def __init__(
        self,
        github_client,
        max_chars_per_file: int = 12_000,
        max_total_chars: int = 60_000,
    ):
        if max_chars_per_file <= 0:
            raise ValueError("max_chars_per_file must be positive")

        if max_total_chars <= 0:
            raise ValueError("max_total_chars must be positive")

        self.github_client = github_client
        self.max_chars_per_file = max_chars_per_file
        self.max_total_chars = max_total_chars

    def collect(
        self,
        owner: str,
        repo: str,
        ref: str,
        selected_files: list[ResearchFile],
    ) -> list[CollectedFile]:
        collected = []
        remaining_budget = self.max_total_chars

        for file in selected_files:
            if remaining_budget <= 0:
                break

            content = self.github_client.get_file_content(
                owner=owner,
                repo=repo,
                path=file.path,
                ref=ref,
            )

            if not content.strip():
                continue

            allowed_chars = min(
                self.max_chars_per_file,
                remaining_budget,
            )

            selected_content = content[:allowed_chars]

            collected.append(
                CollectedFile(
                    path=file.path,
                    category=file.category,
                    content=selected_content,
                    truncated=len(content) > allowed_chars,
                )
            )

            remaining_budget -= len(selected_content)

        return collected
