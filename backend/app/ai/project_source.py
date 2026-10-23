"""V10.1: source-neutral, immutable project identity and provenance.

No filesystem reads, network calls, database writes, or execution of project code.
Private sources must never be exposed as public GitHub links.
"""
from __future__ import annotations

import hashlib
import re
from enum import Enum
from pathlib import PurePosixPath
from pydantic import BaseModel, ConfigDict, Field, model_validator

_NAME = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")


class SourceType(str, Enum):
    GITHUB_PUBLIC = "github_public"
    GITHUB_PRIVATE = "github_private"
    ZIP_UPLOAD = "zip_upload"
    LOCAL_DIRECTORY = "local_directory"


class Visibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class ProjectSource(BaseModel):
    """Stable identity + access metadata, independent of scan implementation.

    owner_id is an application identity, NOT a GitHub username authorization check.
    source_revision is a git SHA or SHA256 of uploaded content (not necessarily 64 chars).
    """
    model_config = ConfigDict(extra="forbid", frozen=True)
    project_id: str = Field(min_length=1, max_length=100)
    owner_id: str = Field(min_length=1, max_length=150)
    display_name: str = Field(min_length=1, max_length=150)
    source_type: SourceType
    visibility: Visibility
    source_revision: str | None = Field(default=None, max_length=128)
    github_owner: str | None = None
    github_repo: str | None = None
    # Opaque internal storage handle, never an arbitrary client-controlled path.
    storage_key: str | None = None

    @model_validator(mode="after")
    def check_consistency(self):
        github = self.source_type in {SourceType.GITHUB_PUBLIC, SourceType.GITHUB_PRIVATE}
        if github:
            if not self.github_owner or not self.github_repo:
                raise ValueError("GitHub sources require github_owner and github_repo")
            if not _NAME.fullmatch(self.github_owner) or not _NAME.fullmatch(self.github_repo):
                raise ValueError("Invalid GitHub repository identifier")
            if self.storage_key is not None:
                raise ValueError("GitHub sources cannot have a storage_key")
            expected = Visibility.PUBLIC if self.source_type == SourceType.GITHUB_PUBLIC else Visibility.PRIVATE
            if self.visibility != expected:
                raise ValueError("GitHub source visibility mismatch")
        else:
            if self.github_owner is not None or self.github_repo is not None:
                raise ValueError("Uploaded/local sources cannot claim a GitHub repository")
            if self.visibility != Visibility.PRIVATE:
                raise ValueError("Uploaded/local sources must default to private")
            if not self.storage_key or not _SHA.fullmatch(self.storage_key):
                raise ValueError("Uploaded/local sources require a server-generated SHA256 storage key")
        return self

    @property
    def repository_key(self) -> str:
        """Safe legacy-compatible owner/repository key for evidence pipeline.

        Private keys contain no user-provided names or paths.
        """
        if self.github_owner and self.github_repo:
            return f"{self.github_owner}/{self.github_repo}"
        return f"private/{self.project_id}"


def private_project_id(owner_id: str, storage_key: str) -> str:
    """Opaque deterministic ID; does not reveal owner or archive filename."""
    if not _SHA.fullmatch(storage_key):
        raise ValueError("storage_key must be a SHA256 hex digest")
    digest = hashlib.sha256(f"{owner_id}\0{storage_key}".encode()).hexdigest()
    return f"p-{digest[:32]}"


def validate_relative_source_path(value: str) -> str:
    """Validate portable source path before storing evidence provenance."""
    if not value or "\\" in value or "\x00" in value or value.startswith("/"):
        raise ValueError("Invalid source path")
    parts = PurePosixPath(value).parts
    if not parts or any(p in {".", ".."} for p in value.split("/")) or ":" in parts[0]:
        raise ValueError("Source path must be relative and traversal-free")
    return value
