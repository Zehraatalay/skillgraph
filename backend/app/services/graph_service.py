from typing import Any

from app.repositories.graph_repository import GraphRepository


class GraphService:
    def __init__(self) -> None:
        self._graph = GraphRepository()

    def get_developer_graph(
        self,
        username: str,
    ) -> dict[str, Any]:
        normalized_username = username.strip()

        if not normalized_username:
            raise ValueError(
                "GitHub username cannot be empty."
            )

        graph = self._graph.get_developer_graph(
            normalized_username
        )

        if graph is None:
            raise ValueError(
                "No analyzed graph data was found "
                "for this developer."
            )

        return graph

    def close(self) -> None:
        self._graph.close()