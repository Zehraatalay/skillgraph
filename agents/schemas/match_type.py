from enum import Enum


class MatchType(str, Enum):
    EXACT = "exact"
    ALIAS = "alias"
    HIERARCHICAL = "hierarchical"
    SEMANTIC = "semantic"
