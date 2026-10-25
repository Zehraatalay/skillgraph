import httpx


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        token: str | None = None,
        timeout: float = 15.0,
    ):
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=timeout,
        )

    def list_repositories(
        self,
        username: str,
        per_page: int = 30,
    ) -> list[dict]:
        response = self.client.get(
            f"/users/{username}/repos",
            params={
                "per_page": per_page,
                "sort": "updated",
                "direction": "desc",
            },
        )

        response.raise_for_status()

        return response.json()

    def get_repository_tree(
        self,
        owner: str,
        repo: str,
        ref: str,
    ) -> dict:
        response = self.client.get(
            f"/repos/{owner}/{repo}/git/trees/{ref}",
            params={"recursive": 1},
        )

        response.raise_for_status()

        return response.json()

    def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str,
    ) -> str:
        response = self.client.get(
            f"/repos/{owner}/{repo}/contents/{path}",
            params={"ref": ref},
            headers={
                "Accept": "application/vnd.github.raw+json",
            },
        )

        response.raise_for_status()

        return response.text

    def close(self):
        self.client.close()
