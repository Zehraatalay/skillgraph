import hashlib
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.ai.project_source import ProjectSource, SourceType, Visibility, private_project_id, validate_relative_source_path
from app.ai.source_context import scan_local_directory

KEY = hashlib.sha256(b"test archive").hexdigest()


def local_source():
    return ProjectSource(project_id=private_project_id("user-1", KEY), owner_id="user-1",
                         display_name="Secret ML", source_type=SourceType.LOCAL_DIRECTORY,
                         visibility=Visibility.PRIVATE, storage_key=KEY)


def test_public_github_source():
    p = ProjectSource(project_id="gh-1", owner_id="user-1", display_name="match3",
                      source_type=SourceType.GITHUB_PUBLIC, visibility=Visibility.PUBLIC,
                      github_owner="Zehraatalay", github_repo="match3-ai-lab")
    assert p.repository_key == "Zehraatalay/match3-ai-lab"


def test_private_github_cannot_be_public():
    with pytest.raises(ValidationError):
        ProjectSource(project_id="gh-1", owner_id="u", display_name="private",
                      source_type=SourceType.GITHUB_PRIVATE, visibility=Visibility.PUBLIC,
                      github_owner="owner", github_repo="repo")


def test_zip_cannot_claim_github():
    with pytest.raises(ValidationError):
        ProjectSource(project_id="p", owner_id="u", display_name="zip",
                      source_type=SourceType.ZIP_UPLOAD, visibility=Visibility.PRIVATE,
                      storage_key=KEY, github_owner="other", github_repo="repo")


def test_private_project_key_is_opaque_and_stable():
    p = local_source()
    assert p.repository_key.startswith("private/p-")
    assert "Secret" not in p.repository_key
    assert private_project_id("user-1", KEY) != private_project_id("user-2", KEY)


@pytest.mark.parametrize("path", ["../secret", "/etc/passwd", "a/../b", "C:/windows", "a\\b", "a/./b", ""])
def test_bad_relative_paths(path):
    with pytest.raises(ValueError):
        validate_relative_source_path(path)


def test_local_adapter_and_v9_detector(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def hello():\n    return 42\n")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "ignore.py").write_text("def ignored(): pass")
    context = scan_local_directory(local_source(), tmp_path)
    assert [f.path for f in context.files] == ["src/app.py"]
    assert context.owner == "private"
    assert context.repository == local_source().project_id
    assert "def hello" in context.files[0].content


def test_local_adapter_rejects_oversize_and_symlink(tmp_path):
    (tmp_path / "large.py").write_text("x" * 500)
    outside = tmp_path.parent / "outside_secret.py"
    outside.write_text("SECRET")
    (tmp_path / "link.py").symlink_to(outside)
    context = scan_local_directory(local_source(), tmp_path, max_file_bytes=100)
    assert context.files == []


def test_no_database_or_network_calls_required(tmp_path):
    (tmp_path / "main.py").write_text("x = 1\n")
    assert scan_local_directory(local_source(), tmp_path).files
