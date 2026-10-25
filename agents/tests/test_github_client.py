import httpx

from agents.services.github_client import GitHubClient


def test_list_repositories():
    def handler(request):
        assert request.url.path == "/users/exampleuser/repos"

        return httpx.Response(
            200,
            json=[
                {
                    "name": "ml-project",
                    "full_name": "exampleuser/ml-project",
                    "default_branch": "main",
                }
            ],
        )

    client = GitHubClient()

    client.client.close()

    client.client = httpx.Client(
        base_url=GitHubClient.BASE_URL,
        transport=httpx.MockTransport(handler),
    )

    try:
        repositories = client.list_repositories("exampleuser")

        assert len(repositories) == 1
        assert repositories[0]["name"] == "ml-project"
    finally:
        client.close()


def test_repository_tree():
    def handler(request):
        assert request.url.path == "/repos/exampleuser/ml-project/git/trees/main"

        return httpx.Response(
            200,
            json={
                "tree": [
                    {
                        "path": "src/train.py",
                        "type": "blob",
                    },
                    {
                        "path": "tests/test_train.py",
                        "type": "blob",
                    },
                ],
                "truncated": False,
            },
        )

    client = GitHubClient()

    client.client.close()

    client.client = httpx.Client(
        base_url=GitHubClient.BASE_URL,
        transport=httpx.MockTransport(handler),
    )

    try:
        tree = client.get_repository_tree(
            "exampleuser",
            "ml-project",
            "main",
        )

        assert len(tree["tree"]) == 2
        assert tree["truncated"] is False
    finally:
        client.close()


def test_file_content():
    def handler(request):
        assert request.url.path == "/repos/exampleuser/ml-project/contents/src/train.py"

        return httpx.Response(
            200,
            text="import lightgbm as lgb",
        )

    client = GitHubClient()

    client.client.close()

    client.client = httpx.Client(
        base_url=GitHubClient.BASE_URL,
        transport=httpx.MockTransport(handler),
    )

    try:
        content = client.get_file_content(
            "exampleuser",
            "ml-project",
            "src/train.py",
            "main",
        )

        assert "lightgbm" in content
    finally:
        client.close()
