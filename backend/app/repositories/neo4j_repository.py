from neo4j import Driver, GraphDatabase

from app.core.config import get_settings


class Neo4jRepository:
    def __init__(self) -> None:
        settings = get_settings()

        self._database = settings.neo4j_database
        self._driver: Driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(
                settings.neo4j_username,
                settings.neo4j_password,
            ),
        )

    def verify_connection(self) -> None:
        self._driver.verify_connectivity()

    def run_query(
        self,
        query: str,
        parameters: dict | None = None,
    ) -> list[dict]:
        records, _, _ = self._driver.execute_query(
            query,
            parameters_=parameters or {},
            database_=self._database,
        )

        return [record.data() for record in records]

    def close(self) -> None:
        self._driver.close()