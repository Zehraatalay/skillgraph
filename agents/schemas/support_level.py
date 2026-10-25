from enum import Enum


class SupportLevel(str, Enum):
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"
