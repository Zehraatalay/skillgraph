from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Final


class SkillCategory(StrEnum):
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    DATABASE = "database"
    CLOUD = "cloud"
    CONTAINERIZATION = "containerization"
    DEVOPS = "devops"
    VERSION_CONTROL = "version_control"
    MESSAGING = "messaging"
    CACHE = "cache"
    TESTING = "testing"
    MACHINE_LEARNING = "machine_learning"
    AI_ENGINEERING = "ai_engineering"
    DATA_ENGINEERING = "data_engineering"
    DATA_SCIENCE = "data_science"
    VISUALIZATION = "visualization"
    GAME_DEVELOPMENT = "game_development"
    MOBILE_DEVELOPMENT = "mobile_development"
    WEB_DEVELOPMENT = "web_development"
    SOFTWARE_ENGINEERING = "software_engineering"
    TOOL = "tool"
    CONCEPT = "concept"


@dataclass(frozen=True, slots=True)
class SkillDefinition:
    name: str
    category: SkillCategory
    aliases: tuple[str, ...] = ()
    github_keywords: tuple[str, ...] = ()


SKILL_REGISTRY: Final[
    tuple[SkillDefinition, ...]
] = (
    # =========================================================
    # PROGRAMMING LANGUAGES
    # =========================================================
    SkillDefinition(
        name="python",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(
            "py",
            "python3",
        ),
        github_keywords=(
            "python",
            "requirements.txt",
            "pyproject.toml",
            "pipfile",
        ),
    ),
    SkillDefinition(
        name="javascript",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(
            "js",
            "ecmascript",
        ),
        github_keywords=(
            "javascript",
            "package.json",
            ".js",
        ),
    ),
    SkillDefinition(
        name="typescript",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(
            "ts",
        ),
        github_keywords=(
            "typescript",
            "tsconfig.json",
            ".ts",
            ".tsx",
        ),
    ),
    SkillDefinition(
        name="java",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(),
        github_keywords=(
            "java",
            "pom.xml",
            "build.gradle",
        ),
    ),
    SkillDefinition(
        name="c#",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(
            "csharp",
            "c sharp",
        ),
        github_keywords=(
            "c#",
            ".cs",
            ".csproj",
        ),
    ),
    SkillDefinition(
        name="go",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(
            "golang",
        ),
        github_keywords=(
            "golang",
            "go.mod",
            ".go",
        ),
    ),
    SkillDefinition(
        name="kotlin",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(),
        github_keywords=(
            "kotlin",
            ".kt",
            "build.gradle.kts",
        ),
    ),
    SkillDefinition(
        name="swift",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(),
        github_keywords=(
            "swift",
            ".swift",
            "package.swift",
        ),
    ),
    SkillDefinition(
        name="dart",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(),
        github_keywords=(
            "dart",
            "pubspec.yaml",
            ".dart",
        ),
    ),
    SkillDefinition(
        name="sql",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(
            "structured query language",
        ),
        github_keywords=(
            "sql",
            ".sql",
        ),
    ),

    # =========================================================
    # BACKEND FRAMEWORKS
    # =========================================================
    SkillDefinition(
        name="fastapi",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "fast api",
        ),
        github_keywords=(
            "fastapi",
            "from fastapi import",
        ),
    ),
    SkillDefinition(
        name="django",
        category=SkillCategory.FRAMEWORK,
        aliases=(),
        github_keywords=(
            "django",
            "manage.py",
        ),
    ),
    SkillDefinition(
        name="django rest framework",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "drf",
            "django-rest-framework",
        ),
        github_keywords=(
            "djangorestframework",
            "rest_framework",
        ),
    ),
    SkillDefinition(
        name="spring boot",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "springboot",
            "spring-boot",
        ),
        github_keywords=(
            "spring boot",
            "spring-boot-starter",
        ),
    ),
    SkillDefinition(
        name="asp.net core",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "aspnet core",
            "asp net core",
            ".net core",
            "dotnet core",
        ),
        github_keywords=(
            "asp.net core",
            "microsoft.aspnetcore",
        ),
    ),
    SkillDefinition(
        name="node.js",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "node",
            "nodejs",
            "node js",
        ),
        github_keywords=(
            "node.js",
            "nodejs",
            "package.json",
        ),
    ),
    SkillDefinition(
        name="express.js",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "express",
            "expressjs",
            "express js",
        ),
        github_keywords=(
            "express",
            "require('express')",
            'from "express"',
        ),
    ),

    # =========================================================
    # FRONTEND FRAMEWORKS
    # =========================================================
    SkillDefinition(
        name="react",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "react.js",
            "reactjs",
        ),
        github_keywords=(
            "react",
            "react-dom",
        ),
    ),
    SkillDefinition(
        name="vue.js",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "vue",
            "vuejs",
        ),
        github_keywords=(
            "vue",
            "vue.config",
        ),
    ),
    SkillDefinition(
        name="angular",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "angularjs",
        ),
        github_keywords=(
            "@angular/core",
            "angular.json",
        ),
    ),
    SkillDefinition(
        name="next.js",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "nextjs",
            "next js",
        ),
        github_keywords=(
            "next",
            "next.config",
        ),
    ),
    SkillDefinition(
        name="flutter",
        category=SkillCategory.FRAMEWORK,
        aliases=(),
        github_keywords=(
            "flutter",
            "pubspec.yaml",
        ),
    ),
    SkillDefinition(
        name="react native",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "react-native",
            "reactnative",
        ),
        github_keywords=(
            "react-native",
            "react native",
        ),
    ),

    # =========================================================
    # DATABASES AND STORAGE
    # =========================================================
    SkillDefinition(
        name="postgresql",
        category=SkillCategory.DATABASE,
        aliases=(
            "postgres",
            "postgre sql",
            "postgres database",
        ),
        github_keywords=(
            "postgresql",
            "postgres",
            "psycopg",
        ),
    ),
    SkillDefinition(
        name="sql server",
        category=SkillCategory.DATABASE,
        aliases=(
            "mssql",
            "microsoft sql server",
        ),
        github_keywords=(
            "sql server",
            "mssql",
        ),
    ),
    SkillDefinition(
        name="mongodb",
        category=SkillCategory.DATABASE,
        aliases=(
            "mongo",
        ),
        github_keywords=(
            "mongodb",
            "mongoose",
            "pymongo",
        ),
    ),
    SkillDefinition(
        name="redis",
        category=SkillCategory.CACHE,
        aliases=(),
        github_keywords=(
            "redis",
            "redis-py",
        ),
    ),
    SkillDefinition(
        name="sqlite",
        category=SkillCategory.DATABASE,
        aliases=(
            "sqlite3",
        ),
        github_keywords=(
            "sqlite",
            "sqlite3",
        ),
    ),
    SkillDefinition(
        name="chromadb",
        category=SkillCategory.DATABASE,
        aliases=(
            "chroma",
            "chroma db",
        ),
        github_keywords=(
            "chromadb",
            "chroma",
        ),
    ),
    SkillDefinition(
        name="pinecone",
        category=SkillCategory.DATABASE,
        aliases=(
            "pinecone db",
        ),
        github_keywords=(
            "pinecone",
            "pinecone-client",
        ),
    ),
    SkillDefinition(
        name="vector databases",
        category=SkillCategory.DATABASE,
        aliases=(
            "vector database",
            "vector db",
            "vector stores",
            "vector store",
        ),
        github_keywords=(
            "vector database",
            "vector store",
        ),
    ),

    # =========================================================
    # CLOUD, DEVOPS AND INFRASTRUCTURE
    # =========================================================
    SkillDefinition(
        name="docker",
        category=SkillCategory.CONTAINERIZATION,
        aliases=(
            "docker container",
            "docker containers",
        ),
        github_keywords=(
            "dockerfile",
            "docker-compose.yml",
            "docker compose",
        ),
    ),
    SkillDefinition(
        name="kubernetes",
        category=SkillCategory.CONTAINERIZATION,
        aliases=(
            "k8s",
        ),
        github_keywords=(
            "kubernetes",
            "deployment.yaml",
            "helm chart",
        ),
    ),
    SkillDefinition(
        name="aws",
        category=SkillCategory.CLOUD,
        aliases=(
            "amazon web services",
        ),
        github_keywords=(
            "aws",
            "boto3",
            "amazon web services",
        ),
    ),
    SkillDefinition(
        name="azure",
        category=SkillCategory.CLOUD,
        aliases=(
            "microsoft azure",
        ),
        github_keywords=(
            "azure",
            "azure pipelines",
        ),
    ),
    SkillDefinition(
        name="terraform",
        category=SkillCategory.DEVOPS,
        aliases=(),
        github_keywords=(
            "terraform",
            ".tf",
        ),
    ),
    SkillDefinition(
        name="github actions",
        category=SkillCategory.DEVOPS,
        aliases=(
            "github action",
        ),
        github_keywords=(
            ".github/workflows",
            "github actions",
        ),
    ),
    SkillDefinition(
        name="ci/cd",
        category=SkillCategory.DEVOPS,
        aliases=(
            "cicd",
            "continuous integration",
            "continuous delivery",
            "continuous deployment",
        ),
        github_keywords=(
            "ci/cd",
            "continuous integration",
            "continuous deployment",
        ),
    ),
    SkillDefinition(
        name="linux",
        category=SkillCategory.TOOL,
        aliases=(
            "gnu/linux",
        ),
        github_keywords=(
            "linux",
            "ubuntu",
        ),
    ),
    SkillDefinition(
        name="git",
        category=SkillCategory.VERSION_CONTROL,
        aliases=(
            "git version control",
        ),
        github_keywords=(
            ".gitignore",
            "git",
        ),
    ),

    # =========================================================
    # DATA, ML AND AI
    # =========================================================
    SkillDefinition(
        name="pytorch",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "torch",
            "torchvision",
            "torchaudio",
        ),
        github_keywords=(
            "pytorch",
            "import torch",
            "torch==",
            "torch>=",
            "torchvision",
            "torchaudio",
        ),
    ),
    SkillDefinition(
        name="scikit-learn",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "sklearn",
            "scikit learn",
        ),
        github_keywords=(
            "scikit-learn",
            "sklearn",
        ),
    ),
    SkillDefinition(
        name="opencv",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "cv2",
            "open cv",
            "opencv-python",
            "opencv-python-headless",
        ),
        github_keywords=(
            "opencv",
            "opencv-python",
            "opencv-python-headless",
            "import cv2",
        ),
    ),
    SkillDefinition(
        name="transformers",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "huggingface transformers",
        ),
        github_keywords=(
            "transformers",
            "automodel",
            "autotokenizer",
        ),
    ),
    SkillDefinition(
        name="pandas",
        category=SkillCategory.DATA_SCIENCE,
        aliases=(),
        github_keywords=(
            "pandas",
            "import pandas",
        ),
    ),
    SkillDefinition(
        name="numpy",
        category=SkillCategory.DATA_SCIENCE,
        aliases=(
            "numpy library",
        ),
        github_keywords=(
            "numpy",
            "import numpy",
        ),
    ),
    SkillDefinition(
        name="apache spark",
        category=SkillCategory.DATA_ENGINEERING,
        aliases=(
            "spark",
            "pyspark",
        ),
        github_keywords=(
            "pyspark",
            "apache spark",
        ),
    ),
    SkillDefinition(
        name="apache kafka",
        category=SkillCategory.MESSAGING,
        aliases=(
            "kafka",
        ),
        github_keywords=(
            "apache kafka",
            "kafka-python",
        ),
    ),
    SkillDefinition(
        name="airflow",
        category=SkillCategory.DATA_ENGINEERING,
        aliases=(
            "apache airflow",
        ),
        github_keywords=(
            "apache airflow",
            "airflow",
        ),
    ),
    SkillDefinition(
        name="dbt",
        category=SkillCategory.DATA_ENGINEERING,
        aliases=(
            "data build tool",
        ),
        github_keywords=(
            "dbt",
            "dbt_project.yml",
        ),
    ),
    SkillDefinition(
        name="langchain",
        category=SkillCategory.AI_ENGINEERING,
        aliases=(
            "lang chain",
        ),
        github_keywords=(
            "langchain",
            "from langchain",
        ),
    ),
    SkillDefinition(
        name="llamaindex",
        category=SkillCategory.AI_ENGINEERING,
        aliases=(
            "llama index",
        ),
        github_keywords=(
            "llama-index",
            "llamaindex",
        ),
    ),

    # =========================================================
    # GAME AND MOBILE DEVELOPMENT
    # =========================================================
    SkillDefinition(
        name="unity",
        category=SkillCategory.GAME_DEVELOPMENT,
        aliases=(
            "unity3d",
            "unity engine",
        ),
        github_keywords=(
            "unity",
            "projectsettings",
            "assets/",
        ),
    ),
    SkillDefinition(
        name="android sdk",
        category=SkillCategory.MOBILE_DEVELOPMENT,
        aliases=(
            "android development",
        ),
        github_keywords=(
            "android sdk",
            "androidmanifest.xml",
        ),
    ),
    SkillDefinition(
        name="ios sdk",
        category=SkillCategory.MOBILE_DEVELOPMENT,
        aliases=(
            "ios development",
        ),
        github_keywords=(
            "ios sdk",
            "xcodeproj",
        ),
    ),
    SkillDefinition(
        name="firebase",
        category=SkillCategory.CLOUD,
        aliases=(
            "google firebase",
        ),
        github_keywords=(
            "firebase",
            "google-services.json",
        ),
    ),

    # =========================================================
    # WEB AND SOFTWARE CONCEPTS
    # =========================================================
    SkillDefinition(
        name="rest api",
        category=SkillCategory.WEB_DEVELOPMENT,
        aliases=(
            "rest",
            "restful api",
            "restful services",
            "restful web services",
        ),
        github_keywords=(
            "rest api",
            "restful api",
        ),
    ),
    SkillDefinition(
        name="html",
        category=SkillCategory.WEB_DEVELOPMENT,
        aliases=(
            "html5",
        ),
        github_keywords=(
            ".html",
            "<html",
        ),
    ),
    SkillDefinition(
        name="css",
        category=SkillCategory.WEB_DEVELOPMENT,
        aliases=(
            "css3",
        ),
        github_keywords=(
            ".css",
            "stylesheet",
        ),
    ),
    SkillDefinition(
        name="unit testing",
        category=SkillCategory.TESTING,
        aliases=(
            "unit tests",
            "unit test",
        ),
        github_keywords=(
            "unit testing",
            "unit tests",
        ),
    ),
    SkillDefinition(
        name="object oriented programming",
        category=SkillCategory.SOFTWARE_ENGINEERING,
        aliases=(
            "oop",
            "object-oriented programming",
        ),
        github_keywords=(
            "object oriented programming",
            "object-oriented programming",
        ),
    ),
        # =========================================================
    # EXTENDED DATA, AI AND TESTING SKILLS
    # =========================================================
    SkillDefinition(
        name="jest",
        category=SkillCategory.TESTING,
        aliases=(
            "jestjs",
            "jest.js",
        ),
        github_keywords=(
            "jest",
            "jest.config",
            "@jest",
        ),
    ),
    SkillDefinition(
        name="large language models",
        category=SkillCategory.AI_ENGINEERING,
        aliases=(
            "large language model",
            "llm",
            "llms",
        ),
        github_keywords=(
            "large language model",
            "llm",
            "openai",
        ),
    ),
    SkillDefinition(
        name="data modeling",
        category=SkillCategory.DATA_ENGINEERING,
        aliases=(
            "data modelling",
            "database modeling",
            "database modelling",
        ),
        github_keywords=(
            "data modeling",
            "data model",
            "schema design",
        ),
    ),
    SkillDefinition(
        name="statistics",
        category=SkillCategory.DATA_SCIENCE,
        aliases=(
            "statistical analysis",
        ),
        github_keywords=(
            "statistics",
            "statistical analysis",
            "scipy.stats",
        ),
    ),
    SkillDefinition(
        name="mlflow",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "ml flow",
        ),
        github_keywords=(
            "mlflow",
            "mlflow.start_run",
        ),
    ),
    SkillDefinition(
        name="cypress",
        category=SkillCategory.TESTING,
        aliases=(
            "cypress.io",
        ),
        github_keywords=(
            "cypress",
            "cypress.config",
        ),
    ),
    SkillDefinition(
        name="prompt engineering",
        category=SkillCategory.AI_ENGINEERING,
        aliases=(
            "prompt design",
            "prompting",
        ),
        github_keywords=(
            "prompt engineering",
            "prompt template",
            "prompttemplate",
        ),
    ),
    SkillDefinition(
        name="etl",
        category=SkillCategory.DATA_ENGINEERING,
        aliases=(
            "extract transform load",
            "extract-transform-load",
        ),
        github_keywords=(
            "etl",
            "extract transform load",
            "data pipeline",
        ),
    ),
    SkillDefinition(
        name="data analysis",
        category=SkillCategory.DATA_SCIENCE,
        aliases=(
            "data analytics",
            "data analysing",
        ),
        github_keywords=(
            "data analysis",
            "data analytics",
            "exploratory data analysis",
        ),
    ),
    SkillDefinition(
        name="pytest",
        category=SkillCategory.TESTING,
        aliases=(
            "py.test",
        ),
        github_keywords=(
            "pytest",
            "pytest.ini",
            "conftest.py",
        ),
    ),
    SkillDefinition(
        name="data visualization",
        category=SkillCategory.VISUALIZATION,
        aliases=(
            "data visualisation",
            "visual analytics",
        ),
        github_keywords=(
            "data visualization",
            "data visualisation",
            "visual analytics",
        ),
    ),
    SkillDefinition(
        name="tableau",
        category=SkillCategory.VISUALIZATION,
        aliases=(
            "tableau desktop",
        ),
        github_keywords=(
            "tableau",
            ".twb",
            ".twbx",
        ),
    ),
    SkillDefinition(
        name="vite",
        category=SkillCategory.TOOL,
        aliases=(
            "vitejs",
            "vite.js",
        ),
        github_keywords=(
            "vite",
            "vite.config",
        ),
    ),
    SkillDefinition(
        name="jupyter",
        category=SkillCategory.TOOL,
        aliases=(
            "jupyter notebook",
            "jupyter notebooks",
        ),
        github_keywords=(
            "jupyter",
            ".ipynb",
            "jupyter notebook",
        ),
    ),
    SkillDefinition(
        name="prometheus",
        category=SkillCategory.DEVOPS,
        aliases=(
            "prometheus monitoring",
        ),
        github_keywords=(
            "prometheus",
            "prometheus.yml",
        ),
    ),
    SkillDefinition(
        name="microservices",
        category=SkillCategory.SOFTWARE_ENGINEERING,
        aliases=(
            "microservice",
            "microservice architecture",
        ),
        github_keywords=(
            "microservices",
            "microservice architecture",
        ),
    ),
    SkillDefinition(
        name="hypothesis testing",
        category=SkillCategory.DATA_SCIENCE,
        aliases=(
            "statistical hypothesis testing",
        ),
        github_keywords=(
            "hypothesis testing",
            "statistical test",
            "p-value",
        ),
    ),
    SkillDefinition(
        name="model evaluation",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "machine learning evaluation",
            "model validation",
        ),
        github_keywords=(
            "model evaluation",
            "classification report",
            "confusion matrix",
        ),
    ),
    SkillDefinition(
        name="tailwind css",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "tailwind",
            "tailwindcss",
        ),
        github_keywords=(
            "tailwindcss",
            "tailwind.config",
        ),
    ),
    SkillDefinition(
        name="feature engineering",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "feature extraction",
        ),
        github_keywords=(
            "feature engineering",
            "feature extraction",
        ),
    ),
    SkillDefinition(
        name="responsive design",
        category=SkillCategory.WEB_DEVELOPMENT,
        aliases=(
            "responsive web design",
            "responsive ui",
        ),
        github_keywords=(
            "responsive design",
            "media query",
            "@media",
        ),
    ),
    SkillDefinition(
        name="computer vision",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "cv",
            "machine vision",
        ),
        github_keywords=(
            "computer vision",
            "opencv",
            "image classification",
        ),
    ),
    SkillDefinition(
        name="embedding models",
        category=SkillCategory.AI_ENGINEERING,
        aliases=(
            "embedding model",
            "embeddings",
            "text embeddings",
        ),
        github_keywords=(
            "embedding model",
            "embeddings",
            "sentence-transformers",
        ),
    ),
    SkillDefinition(
        name="junit",
        category=SkillCategory.TESTING,
        aliases=(
            "junit5",
            "junit 5",
        ),
        github_keywords=(
            "junit",
            "org.junit",
        ),
    ),
    SkillDefinition(
        name="jetpack compose",
        category=SkillCategory.MOBILE_DEVELOPMENT,
        aliases=(
            "compose ui",
            "android compose",
        ),
        github_keywords=(
            "jetpack compose",
            "androidx.compose",
        ),
    ),
        # =========================================================
    # EXTENDED AI, DATA, BACKEND AND TESTING SKILLS
    # =========================================================
    SkillDefinition(
        name="a/b testing",
        category=SkillCategory.DATA_SCIENCE,
        aliases=(
            "ab testing",
            "a b testing",
            "split testing",
        ),
        github_keywords=(
            "a/b testing",
            "ab testing",
            "split testing",
        ),
    ),
    SkillDefinition(
        name="agentic ai",
        category=SkillCategory.AI_ENGINEERING,
        aliases=(
            "agentic artificial intelligence",
            "ai agents",
            "autonomous ai agents",
        ),
        github_keywords=(
            "agentic ai",
            "ai agent",
            "autonomous agent",
        ),
    ),
    SkillDefinition(
        name="artificial intelligence",
        category=SkillCategory.AI_ENGINEERING,
        aliases=(
            "ai",
            "artificial-intelligence",
        ),
        github_keywords=(
            "artificial intelligence",
            "ai system",
        ),
    ),
    SkillDefinition(
        name="bigquery",
        category=SkillCategory.DATA_ENGINEERING,
        aliases=(
            "google bigquery",
            "google big query",
        ),
        github_keywords=(
            "bigquery",
            "google.cloud.bigquery",
        ),
    ),
    SkillDefinition(
        name="celery",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "celery task queue",
        ),
        github_keywords=(
            "celery",
            "from celery import",
            "celery worker",
        ),
    ),
    SkillDefinition(
        name="entity framework",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "entity framework core",
            "ef core",
            "efcore",
        ),
        github_keywords=(
            "entity framework",
            "microsoft.entityframeworkcore",
            "dbcontext",
        ),
    ),
    SkillDefinition(
        name="grafana",
        category=SkillCategory.DEVOPS,
        aliases=(
            "grafana dashboard",
        ),
        github_keywords=(
            "grafana",
            "grafana dashboard",
        ),
    ),
    SkillDefinition(
        name="grpc",
        category=SkillCategory.WEB_DEVELOPMENT,
        aliases=(
            "g-rpc",
            "google remote procedure call",
        ),
        github_keywords=(
            "grpc",
            ".proto",
            "protobuf",
        ),
    ),
    SkillDefinition(
        name="helm",
        category=SkillCategory.DEVOPS,
        aliases=(
            "helm charts",
            "helm chart",
        ),
        github_keywords=(
            "helm",
            "chart.yaml",
            "values.yaml",
        ),
    ),
    SkillDefinition(
        name="hibernate",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "hibernate orm",
        ),
        github_keywords=(
            "hibernate",
            "org.hibernate",
        ),
    ),
    SkillDefinition(
        name="hugging face",
        category=SkillCategory.AI_ENGINEERING,
        aliases=(
            "huggingface",
            "hf",
        ),
        github_keywords=(
            "huggingface",
            "hugging face",
            "huggingface_hub",
        ),
    ),
    SkillDefinition(
        name="image processing",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "digital image processing",
            "image manipulation",
        ),
        github_keywords=(
            "image processing",
            "image manipulation",
            "opencv",
        ),
    ),
    SkillDefinition(
        name="machine learning",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "machine-learning",
        ),
        github_keywords=(
            "machine learning",
            "machine-learning",
        ),
    ),
    SkillDefinition(
        name="matplotlib",
        category=SkillCategory.VISUALIZATION,
        aliases=(
            "matplotlib.pyplot",
            "pyplot",
        ),
        github_keywords=(
            "matplotlib",
            "import matplotlib",
            "import matplotlib.pyplot",
        ),
    ),
    SkillDefinition(
        name="natural language processing",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "nlp",
            "natural-language processing",
        ),
        github_keywords=(
            "natural language processing",
            "nlp",
            "text classification",
        ),
    ),
    SkillDefinition(
        name="playwright",
        category=SkillCategory.TESTING,
        aliases=(
            "playwright testing",
        ),
        github_keywords=(
            "playwright",
            "@playwright/test",
            "playwright.config",
        ),
    ),
    SkillDefinition(
        name="predictive modeling",
        category=SkillCategory.DATA_SCIENCE,
        aliases=(
            "predictive modelling",
            "predictive analytics",
        ),
        github_keywords=(
            "predictive modeling",
            "predictive modelling",
            "predictive analytics",
        ),
    ),
    SkillDefinition(
        name="redux",
        category=SkillCategory.LIBRARY,
        aliases=(
            "redux toolkit",
            "react redux",
        ),
        github_keywords=(
            "redux",
            "@reduxjs/toolkit",
            "react-redux",
        ),
    ),
    SkillDefinition(
        name="retrieval augmented generation",
        category=SkillCategory.AI_ENGINEERING,
        aliases=(
            "rag",
            "retrieval-augmented generation",
        ),
        github_keywords=(
            "retrieval augmented generation",
            "retrieval-augmented generation",
            "rag pipeline",
        ),
    ),
    SkillDefinition(
        name="rxjs",
        category=SkillCategory.LIBRARY,
        aliases=(
            "reactive extensions for javascript",
        ),
        github_keywords=(
            "rxjs",
            "from 'rxjs'",
            'from "rxjs"',
        ),
    ),
    SkillDefinition(
        name="snowflake",
        category=SkillCategory.DATA_ENGINEERING,
        aliases=(
            "snowflake data warehouse",
            "snowflake database",
        ),
        github_keywords=(
            "snowflake",
            "snowflake.connector",
        ),
    ),
    SkillDefinition(
        name="sqlalchemy",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "sql alchemy",
        ),
        github_keywords=(
            "sqlalchemy",
            "from sqlalchemy",
        ),
    ),
    SkillDefinition(
        name="time series",
        category=SkillCategory.DATA_SCIENCE,
        aliases=(
            "time-series",
            "time series analysis",
            "time series forecasting",
        ),
        github_keywords=(
            "time series",
            "time-series",
            "time series forecasting",
        ),
    ),
    SkillDefinition(
        name="xgboost",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "extreme gradient boosting",
            "xgb",
        ),
        github_keywords=(
            "xgboost",
            "xgbclassifier",
            "xgbregressor",
        ),
    ),
    SkillDefinition(
        name="xunit",
        category=SkillCategory.TESTING,
        aliases=(
            "xunit.net",
            "xunit net",
        ),
        github_keywords=(
            "xunit",
            "using Xunit",
            "xunit.runner",
        ),
    ),
)


def normalize_skill_text(value: str) -> str:
    normalized = value.strip().lower()

    normalized = normalized.replace(
        "_",
        " ",
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized


def _build_skill_lookup() -> dict[str, SkillDefinition]:
    lookup: dict[
        str,
        SkillDefinition
    ] = {}

    for definition in SKILL_REGISTRY:
        searchable_names = (
            definition.name,
            *definition.aliases,
        )

        for searchable_name in searchable_names:
            normalized_name = normalize_skill_text(
                searchable_name
            )

            existing_definition = lookup.get(
                normalized_name
            )

            if (
                existing_definition is not None
                and existing_definition.name
                != definition.name
            ):
                raise ValueError(
                    "Skill name or alias collision: "
                    f"'{normalized_name}' belongs to both "
                    f"'{existing_definition.name}' and "
                    f"'{definition.name}'."
                )

            lookup[
                normalized_name
            ] = definition

    return lookup


SKILL_LOOKUP: Final[
    dict[str, SkillDefinition]
] = _build_skill_lookup()


def get_skill_definition(
    value: str,
) -> SkillDefinition | None:
    normalized_value = normalize_skill_text(
        value
    )

    return SKILL_LOOKUP.get(
        normalized_value
    )


def normalize_skill(
    value: str,
) -> str | None:
    definition = get_skill_definition(
        value
    )

    if definition is None:
        return None

    return definition.name


def canonical_skill(
    value: str,
) -> str:
    normalized_value = normalize_skill(
        value
    )

    if normalized_value is None:
        raise ValueError(
            f"Unknown skill: {value}"
        )

    return normalized_value


def is_known_skill(
    value: str,
) -> bool:
    return (
        get_skill_definition(value)
        is not None
    )


def get_category(
    value: str,
) -> SkillCategory | None:
    definition = get_skill_definition(
        value
    )

    if definition is None:
        return None

    return definition.category


def get_skills_by_category(
    category: SkillCategory,
) -> tuple[SkillDefinition, ...]:
    return tuple(
        definition
        for definition in SKILL_REGISTRY
        if definition.category == category
    )


def validate_skill_registry() -> None:
    canonical_names: set[str] = set()

    for definition in SKILL_REGISTRY:
        normalized_name = normalize_skill_text(
            definition.name
        )

        if definition.name != normalized_name:
            raise ValueError(
                "Canonical skill names must already "
                "be normalized. Invalid value: "
                f"'{definition.name}'."
            )

        if definition.name in canonical_names:
            raise ValueError(
                "Duplicate canonical skill: "
                f"'{definition.name}'."
            )

        canonical_names.add(
            definition.name
        )

        normalized_aliases = [
            normalize_skill_text(alias)
            for alias in definition.aliases
        ]

        if len(normalized_aliases) != len(
            set(normalized_aliases)
        ):
            raise ValueError(
                "Duplicate aliases found for skill "
                f"'{definition.name}'."
            )

        if definition.name in normalized_aliases:
            raise ValueError(
                f"Skill '{definition.name}' contains "
                "its canonical name as an alias."
            )


validate_skill_registry()