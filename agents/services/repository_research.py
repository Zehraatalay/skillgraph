from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class ResearchFile:
    path: str
    category: str


class RepositoryResearchService:
    SOURCE_EXTENSIONS: ClassVar[set[str]] = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".go",
        ".rs",
        ".cpp",
        ".c",
        ".cs",
        ".php",
        ".rb",
        ".vue",
    }

    EXCLUDED_DIRECTORIES: ClassVar[set[str]] = {
        "node_modules",
        "venv",
        ".venv",
        "__pycache__",
        "dist",
        "build",
        ".next",
        "coverage",
    }

    def __init__(
        self,
        max_source_files: int = 8,
        max_test_files: int = 4,
    ):
        self.max_source_files = max_source_files
        self.max_test_files = max_test_files

    def select_files(
        self,
        tree: dict,
    ) -> list[ResearchFile]:
        source_files = []
        test_files = []

        for item in tree.get("tree", []):
            if item.get("type") != "blob":
                continue

            path = item.get("path", "")

            if not self._is_relevant_file(path):
                continue

            research_file = ResearchFile(
                path=path,
                category=self._categorize(path),
            )

            if research_file.category == "test":
                test_files.append(research_file)
            else:
                source_files.append(research_file)

        source_files.sort(key=lambda file: self._source_priority(file.path))

        test_files.sort(key=lambda file: file.path)

        return source_files[: self.max_source_files] + test_files[: self.max_test_files]

    def _is_relevant_file(self, path: str) -> bool:
        parts = path.lower().split("/")

        if any(part in self.EXCLUDED_DIRECTORIES for part in parts):
            return False

        filename = parts[-1]

        if filename == "__init__.py":
            return False

        return any(filename.endswith(extension) for extension in self.SOURCE_EXTENSIONS)

    @staticmethod
    def _categorize(path: str) -> str:
        parts = path.lower().split("/")
        filename = parts[-1]

        if (
            "tests" in parts or "test" in parts or filename.startswith("test_") or filename.endswith(("_test.py", ".test.js", ".test.ts", ".spec.ts"))
        ):
            return "test"

        return "source"

    @staticmethod
    def _source_priority(path: str) -> tuple:
        filename = path.lower().split("/")[-1]

        priority_keywords = (
            "engine",
            "model",
            "train",
            "agent",
            "service",
            "algorithm",
            "environment",
            "rules",
            "board",
        )

        keyword_rank = next(
            (
                index
                for index, keyword in enumerate(priority_keywords)
                if keyword in filename
            ),
            len(priority_keywords),
        )

        return (
            keyword_rank,
            path.lower(),
        )
