from pydantic import BaseModel, ConfigDict, Field

class GitHubRepositoryResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    full_name: str
    html_url: str
    description: str | None = None
    language: str | None = None
    stargazers_count: int
    forks_count: int
    topics: list[str] = Field(default_factory=list)
    fork: bool
    archived: bool


class GitHubUserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    login: str
    name: str | None = None
    avatar_url: str
    html_url: str
    bio: str | None = None
    company: str | None = None
    location: str | None = None
    public_repos: int
    followers: int
    following: int
    created_at: str


class GitHubAnalysisPreviewResponse(BaseModel):
    user: GitHubUserResponse
    repositories: list[GitHubRepositoryResponse]
    repository_count: int