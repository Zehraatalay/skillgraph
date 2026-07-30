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

    def get_developer_technology_statistics(
        self,
        developer_login: str,
    ) -> list[dict[str, Any]]:
        return self._neo4j.run_query(
            """
            MATCH (developer:Developer)-[:OWNS]->
                  (repository:Repository)-[uses:USES]->
                  (technology:Technology)

            WHERE toLower(developer.login) =
                  toLower($developer_login)

            RETURN
                technology.name AS technology,
                count(DISTINCT repository) AS repository_count,
                sum(coalesce(uses.byte_count, 0)) AS total_bytes,
                sum(coalesce(repository.stars, 0)) AS total_stars,
                collect(DISTINCT repository.name) AS repositories

            ORDER BY total_bytes DESC
            """,
            {
                "developer_login": developer_login,
            },
        )
    def get_developer_graph(
        self,
        developer_login: str,
    ) -> dict[str, Any] | None:
        result = self._neo4j.run_query(
            """
            MATCH (developer:Developer)
            WHERE toLower(developer.login) =
                  toLower($developer_login)

            OPTIONAL MATCH
                (developer)-[owns:OWNS]->
                (repository:Repository)

            OPTIONAL MATCH
                (repository)-[uses:USES]->
                (technology:Technology)

            OPTIONAL MATCH
                (repository)-[has_topic:HAS_TOPIC]->
                (topic:Topic)

            RETURN
                developer {
                    .login,
                    .name,
                    .avatar_url,
                    .html_url
                } AS developer,

                collect(
                    DISTINCT CASE
                        WHEN repository IS NULL
                        THEN NULL
                        ELSE repository {
                            .github_id,
                            .name,
                            .full_name,
                            .html_url,
                            .description,
                            .primary_language,
                            .stars,
                            .forks,
                            .archived
                        }
                    END
                ) AS repositories,

                collect(
                    DISTINCT CASE
                        WHEN technology IS NULL
                        THEN NULL
                        ELSE technology {
                            .name
                        }
                    END
                ) AS technologies,

                collect(
                    DISTINCT CASE
                        WHEN topic IS NULL
                        THEN NULL
                        ELSE topic {
                            .name
                        }
                    END
                ) AS topics,

                collect(
                    DISTINCT CASE
                        WHEN repository IS NULL
                             OR technology IS NULL
                             OR uses IS NULL
                        THEN NULL
                        ELSE {
                            repository_id: repository.github_id,
                            technology_name: technology.name,
                            byte_count: uses.byte_count
                        }
                    END
                ) AS technology_edges,

                collect(
                    DISTINCT CASE
                        WHEN repository IS NULL
                             OR topic IS NULL
                             OR has_topic IS NULL
                        THEN NULL
                        ELSE {
                            repository_id: repository.github_id,
                            topic_name: topic.name
                        }
                    END
                ) AS topic_edges
            """,
            {
                "developer_login": developer_login,
            },
        )

        if not result:
            return None

        row = result[0]

        developer = row["developer"]

        repositories = [
            item
            for item in row["repositories"]
            if item is not None
        ]

        technologies = [
            item
            for item in row["technologies"]
            if item is not None
        ]

        topics = [
            item
            for item in row["topics"]
            if item is not None
        ]

        technology_edges = [
            item
            for item in row["technology_edges"]
            if item is not None
        ]

        topic_edges = [
            item
            for item in row["topic_edges"]
            if item is not None
        ]

        developer_id = f"developer:{developer['login']}"

        nodes: list[dict[str, Any]] = [
            {
                "id": developer_id,
                "label": (
                    developer.get("name")
                    or developer["login"]
                ),
                "type": "Developer",
                "properties": developer,
            }
        ]

        edges: list[dict[str, Any]] = []

        for repository in repositories:
            repository_id = (
                f"repository:{repository['github_id']}"
            )

            nodes.append(
                {
                    "id": repository_id,
                    "label": repository["name"],
                    "type": "Repository",
                    "properties": repository,
                }
            )

            edges.append(
                {
                    "id": (
                        f"owns:{developer['login']}:"
                        f"{repository['github_id']}"
                    ),
                    "source": developer_id,
                    "target": repository_id,
                    "type": "OWNS",
                    "properties": {},
                }
            )

        for technology in technologies:
            technology_id = (
                f"technology:{technology['name']}"
            )

            nodes.append(
                {
                    "id": technology_id,
                    "label": technology["name"],
                    "type": "Technology",
                    "properties": technology,
                }
            )

        for topic in topics:
            topic_id = f"topic:{topic['name']}"

            nodes.append(
                {
                    "id": topic_id,
                    "label": topic["name"],
                    "type": "Topic",
                    "properties": topic,
                }
            )

        for edge in technology_edges:
            edges.append(
                {
                    "id": (
                        f"uses:{edge['repository_id']}:"
                        f"{edge['technology_name']}"
                    ),
                    "source": (
                        f"repository:{edge['repository_id']}"
                    ),
                    "target": (
                        f"technology:{edge['technology_name']}"
                    ),
                    "type": "USES",
                    "properties": {
                        "byte_count": (
                            edge.get("byte_count") or 0
                        )
                    },
                }
            )

        for edge in topic_edges:
            edges.append(
                {
                    "id": (
                        f"topic:{edge['repository_id']}:"
                        f"{edge['topic_name']}"
                    ),
                    "source": (
                        f"repository:{edge['repository_id']}"
                    ),
                    "target": f"topic:{edge['topic_name']}",
                    "type": "HAS_TOPIC",
                    "properties": {},
                }
            )

        return {
            "developer_login": developer["login"],
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": nodes,
            "edges": edges,
        }

    def get_similar_developers(
        self,
        developer_login: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        return self._neo4j.run_query(
            """
            MATCH (target:Developer)-[:OWNS]->
                  (:Repository)-[:USES]->
                  (target_technology:Technology)

            WHERE toLower(target.login) =
                  toLower($developer_login)

            WITH
                target,
                collect(
                    DISTINCT target_technology.name
                ) AS target_technologies

            MATCH (candidate:Developer)-[:OWNS]->
                  (:Repository)-[:USES]->
                  (candidate_technology:Technology)

            WHERE candidate <> target

            WITH
                target_technologies,
                candidate,
                collect(
                    DISTINCT candidate_technology.name
                ) AS candidate_technologies

            WITH
                candidate,
                target_technologies,
                candidate_technologies,
                [
                    technology IN candidate_technologies
                    WHERE technology IN target_technologies
                ] AS shared_technologies

            WITH
                candidate,
                candidate_technologies,
                shared_technologies,
                (
                    size(target_technologies)
                    + size(candidate_technologies)
                    - size(shared_technologies)
                ) AS union_count

            WHERE size(shared_technologies) > 0
                  AND union_count > 0

            RETURN
                candidate.login AS login,
                candidate.name AS name,
                candidate.avatar_url AS avatar_url,
                candidate.html_url AS html_url,
                shared_technologies,
                candidate_technologies,
                size(
                    shared_technologies
                ) AS shared_technology_count,
                (
                    100.0
                    * size(shared_technologies)
                    / union_count
                ) AS similarity_score

            ORDER BY
                similarity_score DESC,
                shared_technology_count DESC,
                login ASC

            LIMIT $limit
            """,
            {
                "developer_login": developer_login,
                "limit": limit,
            },
        )
    def developer_exists(
        self,
        developer_login: str,
    ) -> bool:
        rows = self._neo4j.run_query(
            """
            MATCH (developer:Developer)
            WHERE toLower(developer.login) =
                toLower($developer_login)

            RETURN developer.login AS login
            LIMIT 1
            """,
            {
                "developer_login": developer_login,
            },
        )

        return bool(rows)


    def get_developer_technology_vectors(
        self,
    ) -> list[dict[str, Any]]:
        return self._neo4j.run_query(
            """
            MATCH (developer:Developer)-[:OWNS]->
                (repository:Repository)-[uses:USES]->
                (technology:Technology)

            WITH
                developer,
                technology.name AS technology,
                sum(
                    CASE
                        WHEN uses.byte_count IS NULL
                        THEN 1
                        WHEN uses.byte_count <= 0
                        THEN 1
                        ELSE uses.byte_count
                    END
                ) AS technology_weight

            WITH
                developer,
                collect(
                    {
                        technology: technology,
                        weight: toFloat(technology_weight)
                    }
                ) AS technology_vector

            RETURN
                developer.login AS login,
                developer.name AS name,
                developer.avatar_url AS avatar_url,
                developer.html_url AS html_url,
                technology_vector

            ORDER BY developer.login
            """
        )
    def close(self) -> None:
        self._neo4j.close()