import hashlib
import json
import os
from pathlib import Path
from typing import Any


class ExtractionCache:
    def __init__(
        self,
        cache_dir: str = ".cache/extractions",
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _generate_key(
        self,
        namespace: str,
        content: str,
    ) -> str:
        raw = f"{namespace}:{content}"

        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(
        self,
        namespace: str,
        content: str,
    ) -> dict[str, Any] | None:
        key = self._generate_key(namespace, content)
        path = self.cache_dir / f"{key}.json"

        if not path.exists():
            return None

        try:
            with path.open("r", encoding="utf-8") as file:
                result = json.load(file)
        except (OSError, UnicodeError, json.JSONDecodeError):
            return None

        if not isinstance(result, dict):
            return None

        return result

    def set(
        self,
        namespace: str,
        content: str,
        result: dict[str, Any],
    ) -> None:
        key = self._generate_key(namespace, content)
        path = self.cache_dir / f"{key}.json"
        temporary_path = self.cache_dir / f"{key}.{os.getpid()}.tmp"

        try:
            with temporary_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    result,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            os.replace(temporary_path, path)
        finally:
            temporary_path.unlink(missing_ok=True)
