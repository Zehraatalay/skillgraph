from typing import Any

from app.repositories.neo4j_repository import Neo4jRepository


class GraphRepository:
    def __init__(self) -> None:
        self._neo4j = Neo4jRepository()

    def create_constraints(self) -> None:
        queries = [
            """
            CREATE CONSTRAINT developer_login_unique IF NOT EXISTS
            FOR (developer:Developer)
            REQUIRE developer.login IS UNIQUE
            """,
            """
            CREATE CONSTRAINT repository_github_id_unique IF NOT EXISTS
            FOR (repository:Repository)
            REQUIRE repository.github_id IS UNIQUE
            """,
            """
            CREATE CONSTRAINT technology_name_unique IF NOT EXISTS
            FOR (technology:Technology)
            REQUIRE technology.name IS UNIQUE
            """,
            """
            CREATE CONSTRAINT topic_name_unique IF NOT EXISTS
            FOR (topic:Topic)
            REQUIRE topic.name IS UNIQUE
            """,
        ]

        for query in queries:
            self._neo4j.run_query(query)

    def save_developer(
        self,
        user: dict[str, Any],
    ) -> dict[str, Any]:
        result = self._neo4j.run_query(
            """
            MERGE (developer:Developer {login: $login})
            SET
                developer.name = $name,
                developer.avatar_url = $avatar_url,
                developer.html_url = $html_url,
                developer.bio = $bio,
                developer.company = $company,
                developer.location = $location,
                developer.public_repos = $public_repos,
                developer.followers = $followers,
                developer.following = $following,
                developer.github_created_at = datetime($created_at),
                developer.last_analyzed_at = datetime()
            RETURN developer {
                .login,
                .name,
                .avatar_url,
                .html_url
            } AS developer
            """,
            {
                "login": user["login"],
                "name": user.get("name"),
                "avatar_url": user["avatar_url"],
                "html_url": user["html_url"],
                "bio": user.get("bio"),
                "company": user.get("company"),
                "location": user.get("location"),
                "public_repos": user["public_repos"],
                "followers": user["followers"],
                "following": user["following"],
                "created_at": user["created_at"],
            },
        )

        return result[0]["developer"]

    def save_repository(
        self,
        developer_login: str,
        repository: dict[str, Any],
    ) -> None:
        self._neo4j.run_query(
            """
            MATCH (developer:Developer {login: $developer_login})

            MERGE (repository:Repository {github_id: $github_id})
            SET
                repository.name = $name,
                repository.full_name = $full_name,
                repository.html_url = $html_url,
                repository.description = $description,
                repository.primary_language = $primary_language,
                repository.stars = $stars,
                repository.forks = $forks,
                repository.archived = $archived,
                repository.updated_at = datetime()

            MERGE (developer)-[:OWNS]->(repository)
            """,
            {
                "developer_login": developer_login,
                "github_id": repository["id"],
                "name": repository["name"],
                "full_name": repository["full_name"],
                "html_url": repository["html_url"],
                "description": repository.get("description"),
                "primary_language": repository.get("language"),
                "stars": repository["stargazers_count"],
                "forks": repository["forks_count"],
                "archived": repository["archived"],
            },
        )

    def save_technology(
        self,
        repository_id: int,
        technology_name: str,
        byte_count: int,
    ) -> None:
        self._neo4j.run_query(
            """
            MATCH (repository:Repository {github_id: $repository_id})

            MERGE (technology:Technology {name: $technology_name})
            ON CREATE SET technology.created_at = datetime()

            MERGE (repository)-[uses:USES]->(technology)
            SET
                uses.byte_count = $byte_count,
                uses.updated_at = datetime()
            """,
            {
                "repository_id": repository_id,
                "technology_name": technology_name,
                "byte_count": byte_count,
            },
        )

    def save_topic(
        self,
        repository_id: int,
        topic_name: str,
    ) -> None:
        self._neo4j.run_query(
            """
            MATCH (repository:Repository {github_id: $repository_id})

            MERGE (topic:Topic {name: $topic_name})
            ON CREATE SET topic.created_at = datetime()

            MERGE (repository)-[:HAS_TOPIC]->(topic)
            """,
            {
                "repository_id": repository_id,
                "topic_name": topic_name,
            },
        )

    def get_developer_graph_summary(
        self,
        developer_login: str,
    ) -> dict[str, Any] | None:
        result = self._neo4j.run_query(
            """
            MATCH (developer:Developer {login: $developer_login})

            OPTIONAL MATCH (developer)-[:OWNS]->(repository:Repository)
            OPTIONAL MATCH (repository)-[:USES]->(technology:Technology)
            OPTIONAL MATCH (repository)-[:HAS_TOPIC]->(topic:Topic)

            WITH
                developer,
                count(DISTINCT repository) AS repository_count,
                collect(DISTINCT technology.name) AS technologies,
                collect(DISTINCT topic.name) AS topics

            RETURN developer {
                .login,
                .name,
                repository_count: repository_count,
                technologies: technologies,
                topics: topics
            } AS summary
            """,
            {
                "developer_login": developer_login,
            },
        )

        if not result:
            return None

        return result[0]["summary"]
    
    def close(self) -> None:
        self._neo4j.close()