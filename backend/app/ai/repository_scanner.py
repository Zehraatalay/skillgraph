"""Read bounded, public GitHub repository evidence. No LLM required."""
from app.ai.file_selector import select_files
from app.ai.schemas import RepositoryContext, SourceFile


class RepositoryScanner:
    def __init__(self, github, *, max_files: int = 16, max_file_bytes: int = 30_000, max_total_chars: int = 100_000):
        self.github = github
        self.max_files = max_files
        self.max_file_bytes = max_file_bytes
        self.max_total_chars = max_total_chars

    def scan(self, owner: str, repository: str) -> RepositoryContext:
        tree = self.github.get_repository_tree(owner, repository)
        selected = select_files(tree, max_files=self.max_files, max_file_bytes=self.max_file_bytes)
        files: list[SourceFile] = []
        remaining = self.max_total_chars
        for item in selected:
            if remaining <= 0:
                break
            content = self.github.get_repository_text_file(owner, repository, item['path'])
            if not content or '\x00' in content:
                continue
            content = content[:remaining]
            files.append(SourceFile(path=item['path'], content=content, size=item['size']))
            remaining -= len(content)
        return RepositoryContext(owner=owner, repository=repository, files=files,
                                 skipped_files=max(0, len(tree) - len(files)),
                                 total_characters=self.max_total_chars - remaining)
