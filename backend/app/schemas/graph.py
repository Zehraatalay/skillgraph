from typing import Any

from pydantic import BaseModel, Field


class GraphNodeResponse(BaseModel):
    id: str
    label: str
    type: str
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphEdgeResponse(BaseModel):
    id: str
    source: str
    target: str
    type: str
    properties: dict[str, Any] = Field(default_factory=dict)


class DeveloperGraphResponse(BaseModel):
    developer_login: str
    node_count: int
    edge_count: int
    nodes: list[GraphNodeResponse] = Field(default_factory=list)
    edges: list[GraphEdgeResponse] = Field(default_factory=list)