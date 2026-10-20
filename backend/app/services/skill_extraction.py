"""Conservative, evidence-based extraction from public GitHub repository files."""
from __future__ import annotations

import json
import re
from pathlib import PurePosixPath

# Explicit dependency identifiers only; no inference from arbitrary README mentions.
DEPENDENCY_SKILLS = {
    "torch": "pytorch", "torchvision": "pytorch", "tensorflow": "tensorflow",
    "keras": "keras", "scikit-learn": "scikit-learn", "sklearn": "scikit-learn",
    "xgboost": "xgboost", "lightgbm": "lightgbm", "catboost": "catboost",
    "pandas": "pandas", "numpy": "numpy", "polars": "polars",
    "transformers": "hugging face transformers", "sentence-transformers": "sentence transformers",
    "langchain": "langchain", "llama-index": "llamaindex", "llamaindex": "llamaindex",
    "faiss-cpu": "faiss", "faiss-gpu": "faiss", "chromadb": "chromadb",
    "stable-baselines3": "stable-baselines3", "gymnasium": "gymnasium",
    "ray": "ray", "opencv-python": "opencv", "opencv-contrib-python": "opencv",
    "fastapi": "fastapi", "django": "django", "flask": "flask",
    "sqlalchemy": "sqlalchemy", "neo4j": "neo4j", "psycopg2": "postgresql",
    "psycopg2-binary": "postgresql", "redis": "redis",
    "vue": "vue.js", "react": "react", "next": "next.js", "nuxt": "nuxt",
    "express": "express", "typescript": "typescript", "tailwindcss": "tailwind css",
    "vite": "vite", "vitest": "vitest", "jest": "jest", "cypress": "cypress",
    "pinia": "pinia", "axios": "axios",
}


def extract_dependencies(filename: str, content: str) -> set[str]:
    """Extract exact known dependencies; ignore comments and arbitrary prose."""
    name = PurePosixPath(filename).name.lower()
    identifiers: set[str] = set()
    if name in {"requirements.txt", "requirements-dev.txt"}:
        for line in content.splitlines():
            line = line.split("#", 1)[0].strip()
            if not line or line.startswith(("-", ".", "git+")):
                continue
            match = re.match(r"^([A-Za-z][A-Za-z0-9_.-]*)", line)
            if match:
                identifiers.add(match.group(1).lower().replace("_", "-"))
    elif name == "package.json":
        try:
            data = json.loads(content)
        except (ValueError, TypeError):
            return set()
        for key in ("dependencies", "devDependencies"):
            if isinstance(data, dict) and isinstance(data.get(key), dict):
                identifiers.update(k.lower() for k in data[key])
    elif name == "pyproject.toml":
        try:
            import tomllib
            data = tomllib.loads(content)
        except (ValueError, TypeError):
            return set()
        project = data.get("project", {})
        deps = project.get("dependencies", []) if isinstance(project, dict) else []
        if isinstance(deps, list):
            for dep in deps:
                if isinstance(dep, str):
                    match = re.match(r"^([A-Za-z][A-Za-z0-9_.-]*)", dep.strip())
                    if match:
                        identifiers.add(match.group(1).lower().replace("_", "-"))
    return {DEPENDENCY_SKILLS[identifier] for identifier in identifiers if identifier in DEPENDENCY_SKILLS}
