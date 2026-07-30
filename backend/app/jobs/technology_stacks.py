from __future__ import annotations

from typing import Final, TypedDict


class TechnologyStack(TypedDict):
    stack_id: str
    role_family: str
    display_name: str
    title_options: tuple[str, ...]
    required_skills: tuple[str, ...]
    preferred_skills: tuple[str, ...]
    summary_focus: str


TECHNOLOGY_STACKS: Final[
    tuple[TechnologyStack, ...]
] = (
    # =========================================================
    # BACKEND
    # =========================================================
    {
        "stack_id": "backend_python_fastapi",
        "role_family": "backend",
        "display_name": "Python FastAPI Backend",
        "title_options": (
            "Python Backend Engineer",
            "FastAPI Developer",
            "Backend API Engineer",
        ),
        "required_skills": (
            "python",
            "fastapi",
            "rest api",
            "postgresql",
            "git",
        ),
        "preferred_skills": (
            "docker",
            "redis",
            "pytest",
            "sqlalchemy",
            "github actions",
            "celery",
        ),
        "summary_focus": (
            "Build maintainable REST APIs and backend services "
            "using Python, FastAPI, and relational databases."
        ),
    },
    {
        "stack_id": "backend_python_django",
        "role_family": "backend",
        "display_name": "Python Django Backend",
        "title_options": (
            "Django Backend Developer",
            "Python Web Engineer",
            "Backend Software Engineer",
        ),
        "required_skills": (
            "python",
            "django",
            "rest api",
            "postgresql",
            "git",
        ),
        "preferred_skills": (
            "django rest framework",
            "docker",
            "redis",
            "celery",
            "pytest",
            "aws",
        ),
        "summary_focus": (
            "Develop web services and business applications "
            "using Django, Python, and relational data models."
        ),
    },
    {
        "stack_id": "backend_java_spring",
        "role_family": "backend",
        "display_name": "Java Spring Backend",
        "title_options": (
            "Java Backend Engineer",
            "Spring Boot Developer",
            "Backend Software Engineer",
        ),
        "required_skills": (
            "java",
            "spring boot",
            "rest api",
            "postgresql",
            "git",
        ),
        "preferred_skills": (
            "docker",
            "hibernate",
            "junit",
            "redis",
            "apache kafka",
            "microservices",
        ),
        "summary_focus": (
            "Develop reliable backend services using Java, "
            "Spring Boot, relational databases, and tested APIs."
        ),
    },
    {
        "stack_id": "backend_dotnet",
        "role_family": "backend",
        "display_name": ".NET Backend",
        "title_options": (
            ".NET Backend Engineer",
            "C# Backend Developer",
            "ASP.NET Core Developer",
        ),
        "required_skills": (
            "c#",
            "asp.net core",
            "rest api",
            "sql server",
            "git",
        ),
        "preferred_skills": (
            "entity framework",
            "docker",
            "azure",
            "xunit",
            "redis",
            "microservices",
        ),
        "summary_focus": (
            "Build backend applications and APIs using C#, "
            "ASP.NET Core, SQL Server, and modern engineering practices."
        ),
    },
    {
        "stack_id": "backend_node_express",
        "role_family": "backend",
        "display_name": "Node.js Express Backend",
        "title_options": (
            "Node.js Backend Developer",
            "Backend JavaScript Engineer",
            "API Software Engineer",
        ),
        "required_skills": (
            "javascript",
            "node.js",
            "express.js",
            "rest api",
            "git",
        ),
        "preferred_skills": (
            "typescript",
            "postgresql",
            "mongodb",
            "docker",
            "jest",
            "redis",
        ),
        "summary_focus": (
            "Develop API-driven backend services using Node.js, "
            "Express, JavaScript, and modern data stores."
        ),
    },
    {
        "stack_id": "backend_go",
        "role_family": "backend",
        "display_name": "Go Backend",
        "title_options": (
            "Go Backend Engineer",
            "Golang Developer",
            "Backend Platform Engineer",
        ),
        "required_skills": (
            "go",
            "rest api",
            "postgresql",
            "git",
            "unit testing",
        ),
        "preferred_skills": (
            "docker",
            "redis",
            "grpc",
            "kubernetes",
            "microservices",
            "apache kafka",
        ),
        "summary_focus": (
            "Build efficient backend and platform services using "
            "Go, APIs, concurrency, and production-oriented tooling."
        ),
    },

    # =========================================================
    # FRONTEND
    # =========================================================
    {
        "stack_id": "frontend_react",
        "role_family": "frontend",
        "display_name": "React Frontend",
        "title_options": (
            "React Frontend Developer",
            "Frontend Software Engineer",
            "Web UI Engineer",
        ),
        "required_skills": (
            "javascript",
            "react",
            "html",
            "css",
            "git",
        ),
        "preferred_skills": (
            "typescript",
            "vite",
            "jest",
            "cypress",
            "tailwind css",
            "redux",
        ),
        "summary_focus": (
            "Build responsive and accessible web interfaces "
            "using React and reusable component architectures."
        ),
    },
    {
        "stack_id": "frontend_vue",
        "role_family": "frontend",
        "display_name": "Vue Frontend",
        "title_options": (
            "Vue Frontend Developer",
            "Frontend Web Engineer",
            "Vue.js Software Engineer",
        ),
        "required_skills": (
            "javascript",
            "vue.js",
            "html",
            "css",
            "git",
        ),
        "preferred_skills": (
            "typescript",
            "vite",
            "pinia",
            "vitest",
            "cypress",
            "tailwind css",
        ),
        "summary_focus": (
            "Develop maintainable web applications using Vue, "
            "component-based design, and modern frontend tooling."
        ),
    },
    {
        "stack_id": "frontend_angular",
        "role_family": "frontend",
        "display_name": "Angular Frontend",
        "title_options": (
            "Angular Developer",
            "Frontend Software Engineer",
            "TypeScript Frontend Engineer",
        ),
        "required_skills": (
            "typescript",
            "angular",
            "html",
            "css",
            "git",
        ),
        "preferred_skills": (
            "rxjs",
            "jest",
            "cypress",
            "sass",
            "rest api",
            "responsive design",
        ),
        "summary_focus": (
            "Build structured frontend applications using Angular, "
            "TypeScript, reactive programming, and reusable modules."
        ),
    },
    {
        "stack_id": "frontend_nextjs",
        "role_family": "frontend",
        "display_name": "Next.js Frontend",
        "title_options": (
            "Next.js Developer",
            "React Web Engineer",
            "Frontend Product Engineer",
        ),
        "required_skills": (
            "typescript",
            "react",
            "next.js",
            "html",
            "css",
        ),
        "preferred_skills": (
            "tailwind css",
            "jest",
            "playwright",
            "rest api",
            "seo",
            "vercel",
        ),
        "summary_focus": (
            "Develop modern product interfaces with React and "
            "Next.js, emphasizing performance and user experience."
        ),
    },

    # =========================================================
    # FULL STACK
    # =========================================================
    {
        "stack_id": "full_stack_react_node",
        "role_family": "full_stack",
        "display_name": "React and Node.js Full Stack",
        "title_options": (
            "React and Node.js Developer",
            "Full Stack JavaScript Engineer",
            "Full Stack Software Engineer",
        ),
        "required_skills": (
            "javascript",
            "react",
            "node.js",
            "rest api",
            "git",
        ),
        "preferred_skills": (
            "typescript",
            "express.js",
            "postgresql",
            "mongodb",
            "docker",
            "jest",
        ),
        "summary_focus": (
            "Deliver end-to-end web features using React, Node.js, "
            "APIs, and modern JavaScript engineering practices."
        ),
    },
    {
        "stack_id": "full_stack_vue_fastapi",
        "role_family": "full_stack",
        "display_name": "Vue and FastAPI Full Stack",
        "title_options": (
            "Python Full Stack Developer",
            "Vue and FastAPI Engineer",
            "Full Stack Web Developer",
        ),
        "required_skills": (
            "python",
            "fastapi",
            "vue.js",
            "rest api",
            "postgresql",
        ),
        "preferred_skills": (
            "typescript",
            "docker",
            "pytest",
            "vite",
            "redis",
            "github actions",
        ),
        "summary_focus": (
            "Build complete web features with Vue, FastAPI, "
            "Python, and relational database systems."
        ),
    },
    {
        "stack_id": "full_stack_react_django",
        "role_family": "full_stack",
        "display_name": "React and Django Full Stack",
        "title_options": (
            "React and Django Developer",
            "Python Full Stack Engineer",
            "Full Stack Software Engineer",
        ),
        "required_skills": (
            "python",
            "django",
            "react",
            "rest api",
            "git",
        ),
        "preferred_skills": (
            "typescript",
            "postgresql",
            "docker",
            "django rest framework",
            "pytest",
            "jest",
        ),
        "summary_focus": (
            "Develop product features spanning React interfaces, "
            "Django services, APIs, and relational databases."
        ),
    },
    {
        "stack_id": "full_stack_angular_spring",
        "role_family": "full_stack",
        "display_name": "Angular and Spring Full Stack",
        "title_options": (
            "Java Full Stack Developer",
            "Angular and Spring Engineer",
            "Full Stack Application Engineer",
        ),
        "required_skills": (
            "java",
            "spring boot",
            "angular",
            "typescript",
            "rest api",
        ),
        "preferred_skills": (
            "postgresql",
            "docker",
            "hibernate",
            "junit",
            "rxjs",
            "microservices",
        ),
        "summary_focus": (
            "Develop enterprise web applications using Angular, "
            "Spring Boot, TypeScript, Java, and API-based architecture."
        ),
    },

    # =========================================================
    # MACHINE LEARNING
    # =========================================================
    {
        "stack_id": "ml_computer_vision",
        "role_family": "machine_learning",
        "display_name": "Computer Vision ML",
        "title_options": (
            "Computer Vision Engineer",
            "Machine Learning Engineer",
            "Applied Computer Vision Engineer",
        ),
        "required_skills": (
            "python",
            "computer vision",
            "opencv",
            "pytorch",
            "git",
        ),
        "preferred_skills": (
            "numpy",
            "scikit-learn",
            "docker",
            "fastapi",
            "mlflow",
            "image processing",
        ),
        "summary_focus": (
            "Develop and evaluate computer vision systems using "
            "Python, OpenCV, deep learning, and reproducible experiments."
        ),
    },
    {
        "stack_id": "ml_nlp",
        "role_family": "machine_learning",
        "display_name": "Natural Language Processing ML",
        "title_options": (
            "NLP Engineer",
            "Machine Learning Engineer",
            "Applied NLP Engineer",
        ),
        "required_skills": (
            "python",
            "natural language processing",
            "transformers",
            "pytorch",
            "git",
        ),
        "preferred_skills": (
            "hugging face",
            "scikit-learn",
            "pandas",
            "docker",
            "fastapi",
            "mlflow",
        ),
        "summary_focus": (
            "Build natural language processing models and pipelines "
            "using transformers, Python, and modern ML tooling."
        ),
    },
    {
        "stack_id": "ml_tabular",
        "role_family": "machine_learning",
        "display_name": "Tabular Machine Learning",
        "title_options": (
            "Machine Learning Engineer",
            "Applied ML Engineer",
            "Predictive Modeling Engineer",
        ),
        "required_skills": (
            "python",
            "scikit-learn",
            "pandas",
            "model evaluation",
            "git",
        ),
        "preferred_skills": (
            "numpy",
            "feature engineering",
            "xgboost",
            "sql",
            "mlflow",
            "docker",
        ),
        "summary_focus": (
            "Develop predictive machine learning solutions using "
            "structured data, feature engineering, and model evaluation."
        ),
    },
    {
        "stack_id": "ml_recommendation",
        "role_family": "machine_learning",
        "display_name": "Recommendation Systems",
        "title_options": (
            "Recommendation Systems Engineer",
            "Machine Learning Engineer",
            "Personalization Engineer",
        ),
        "required_skills": (
            "python",
            "recommendation systems",
            "machine learning",
            "sql",
            "git",
        ),
        "preferred_skills": (
            "pytorch",
            "pandas",
            "apache spark",
            "redis",
            "fastapi",
            "mlflow",
        ),
        "summary_focus": (
            "Develop recommendation and personalization systems "
            "using user behavior data and machine learning methods."
        ),
    },

    # =========================================================
    # AI ENGINEERING
    # =========================================================
    {
        "stack_id": "ai_rag",
        "role_family": "ai_engineering",
        "display_name": "Retrieval-Augmented Generation",
        "title_options": (
            "Generative AI Engineer",
            "RAG Application Engineer",
            "AI Software Engineer",
        ),
        "required_skills": (
            "python",
            "large language models",
            "retrieval augmented generation",
            "embedding models",
            "rest api",
        ),
        "preferred_skills": (
            "langchain",
            "llamaindex",
            "chromadb",
            "pinecone",
            "fastapi",
            "docker",
        ),
        "summary_focus": (
            "Build retrieval-augmented AI applications combining "
            "language models, embeddings, search, and backend services."
        ),
    },
    {
        "stack_id": "ai_llm_applications",
        "role_family": "ai_engineering",
        "display_name": "LLM Applications",
        "title_options": (
            "LLM Application Developer",
            "AI Application Engineer",
            "Generative AI Developer",
        ),
        "required_skills": (
            "python",
            "large language models",
            "prompt engineering",
            "rest api",
            "git",
        ),
        "preferred_skills": (
            "transformers",
            "langchain",
            "fastapi",
            "docker",
            "postgresql",
            "redis",
        ),
        "summary_focus": (
            "Develop production-oriented applications powered by "
            "large language models, prompts, APIs, and data integrations."
        ),
    },
    {
        "stack_id": "ai_agents",
        "role_family": "ai_engineering",
        "display_name": "Agentic AI",
        "title_options": (
            "Agentic AI Engineer",
            "AI Systems Developer",
            "AI Automation Engineer",
        ),
        "required_skills": (
            "python",
            "agentic ai",
            "large language models",
            "prompt engineering",
            "rest api",
        ),
        "preferred_skills": (
            "langchain",
            "semantic search",
            "vector databases",
            "fastapi",
            "docker",
            "redis",
        ),
        "summary_focus": (
            "Develop AI agents and automated workflows that combine "
            "language models, tools, memory, and external services."
        ),
    },

    # =========================================================
    # DATA ENGINEERING
    # =========================================================
    {
        "stack_id": "data_engineering_batch",
        "role_family": "data_engineering",
        "display_name": "Batch Data Engineering",
        "title_options": (
            "Data Engineer",
            "ETL Developer",
            "Data Pipeline Engineer",
        ),
        "required_skills": (
            "python",
            "sql",
            "etl",
            "airflow",
            "git",
        ),
        "preferred_skills": (
            "apache spark",
            "postgresql",
            "docker",
            "dbt",
            "aws",
            "data modeling",
        ),
        "summary_focus": (
            "Build scheduled ingestion and transformation pipelines "
            "using Python, SQL, orchestration, and data modeling."
        ),
    },
    {
        "stack_id": "data_engineering_streaming",
        "role_family": "data_engineering",
        "display_name": "Streaming Data Engineering",
        "title_options": (
            "Streaming Data Engineer",
            "Data Platform Engineer",
            "Real-Time Data Engineer",
        ),
        "required_skills": (
            "python",
            "sql",
            "apache kafka",
            "apache spark",
            "git",
        ),
        "preferred_skills": (
            "docker",
            "kubernetes",
            "aws",
            "airflow",
            "postgresql",
            "data modeling",
        ),
        "summary_focus": (
            "Develop real-time data pipelines and distributed "
            "processing workflows using Kafka and Spark."
        ),
    },
    {
        "stack_id": "data_engineering_analytics",
        "role_family": "data_engineering",
        "display_name": "Analytics Engineering",
        "title_options": (
            "Analytics Engineer",
            "Data Transformation Engineer",
            "Data Engineer",
        ),
        "required_skills": (
            "sql",
            "dbt",
            "data modeling",
            "git",
            "etl",
        ),
        "preferred_skills": (
            "snowflake",
            "bigquery",
            "airflow",
            "python",
            "tableau",
            "github actions",
        ),
        "summary_focus": (
            "Create trusted analytical datasets and transformation "
            "models using SQL, dbt, and warehouse technologies."
        ),
    },

    # =========================================================
    # DATA SCIENCE
    # =========================================================
    {
        "stack_id": "data_science_product",
        "role_family": "data_science",
        "display_name": "Product Data Science",
        "title_options": (
            "Product Data Scientist",
            "Data Scientist",
            "Product Analytics Specialist",
        ),
        "required_skills": (
            "python",
            "sql",
            "statistics",
            "data analysis",
            "data visualization",
        ),
        "preferred_skills": (
            "pandas",
            "a/b testing",
            "hypothesis testing",
            "tableau",
            "scikit-learn",
            "jupyter",
        ),
        "summary_focus": (
            "Analyze product behavior, design experiments, and "
            "translate data into measurable product decisions."
        ),
    },
    {
        "stack_id": "data_science_predictive",
        "role_family": "data_science",
        "display_name": "Predictive Data Science",
        "title_options": (
            "Applied Data Scientist",
            "Data Scientist",
            "Predictive Analytics Specialist",
        ),
        "required_skills": (
            "python",
            "sql",
            "statistics",
            "scikit-learn",
            "predictive modeling",
        ),
        "preferred_skills": (
            "pandas",
            "feature engineering",
            "jupyter",
            "matplotlib",
            "tableau",
            "time series",
        ),
        "summary_focus": (
            "Develop statistical and predictive models that support "
            "business decisions and measurable operational outcomes."
        ),
    },

    # =========================================================
    # DEVOPS
    # =========================================================
    {
        "stack_id": "devops_aws",
        "role_family": "devops",
        "display_name": "AWS DevOps",
        "title_options": (
            "AWS DevOps Engineer",
            "Cloud Platform Engineer",
            "Infrastructure Automation Engineer",
        ),
        "required_skills": (
            "aws",
            "docker",
            "linux",
            "ci/cd",
            "git",
        ),
        "preferred_skills": (
            "terraform",
            "kubernetes",
            "github actions",
            "prometheus",
            "grafana",
            "python",
        ),
        "summary_focus": (
            "Automate AWS infrastructure, deployment pipelines, "
            "monitoring, and reliable cloud operations."
        ),
    },
    {
        "stack_id": "devops_azure",
        "role_family": "devops",
        "display_name": "Azure DevOps",
        "title_options": (
            "Azure DevOps Engineer",
            "Cloud Infrastructure Engineer",
            "Platform Engineer",
        ),
        "required_skills": (
            "azure",
            "docker",
            "linux",
            "ci/cd",
            "git",
        ),
        "preferred_skills": (
            "terraform",
            "kubernetes",
            "github actions",
            "powershell",
            "prometheus",
            "grafana",
        ),
        "summary_focus": (
            "Build and maintain Azure-based infrastructure, "
            "automated delivery pipelines, and operational tooling."
        ),
    },
    {
        "stack_id": "devops_kubernetes",
        "role_family": "devops",
        "display_name": "Kubernetes Platform Engineering",
        "title_options": (
            "Kubernetes Platform Engineer",
            "DevOps Engineer",
            "Site Reliability Engineer",
        ),
        "required_skills": (
            "kubernetes",
            "docker",
            "linux",
            "ci/cd",
            "git",
        ),
        "preferred_skills": (
            "terraform",
            "helm",
            "prometheus",
            "grafana",
            "aws",
            "python",
        ),
        "summary_focus": (
            "Operate container platforms and deployment systems "
            "using Kubernetes, automation, and observability tooling."
        ),
    },

    # =========================================================
    # MOBILE
    # =========================================================
    {
        "stack_id": "mobile_android",
        "role_family": "mobile",
        "display_name": "Native Android",
        "title_options": (
            "Android Developer",
            "Kotlin Mobile Engineer",
            "Mobile Software Engineer",
        ),
        "required_skills": (
            "kotlin",
            "android sdk",
            "rest api",
            "git",
            "unit testing",
        ),
        "preferred_skills": (
            "jetpack compose",
            "firebase",
            "sqlite",
            "github actions",
            "mobile architecture",
            "coroutines",
        ),
        "summary_focus": (
            "Develop reliable native Android applications using "
            "Kotlin, platform APIs, testing, and backend integrations."
        ),
    },
    {
        "stack_id": "mobile_ios",
        "role_family": "mobile",
        "display_name": "Native iOS",
        "title_options": (
            "iOS Developer",
            "Swift Mobile Engineer",
            "Mobile Software Engineer",
        ),
        "required_skills": (
            "swift",
            "ios sdk",
            "rest api",
            "git",
            "unit testing",
        ),
        "preferred_skills": (
            "swiftui",
            "firebase",
            "core data",
            "fastlane",
            "mobile architecture",
            "github actions",
        ),
        "summary_focus": (
            "Build native iOS features using Swift, platform "
            "frameworks, automated testing, and API integrations."
        ),
    },
    {
        "stack_id": "mobile_flutter",
        "role_family": "mobile",
        "display_name": "Flutter Mobile",
        "title_options": (
            "Flutter Developer",
            "Cross-Platform Mobile Engineer",
            "Mobile Application Developer",
        ),
        "required_skills": (
            "dart",
            "flutter",
            "rest api",
            "git",
            "unit testing",
        ),
        "preferred_skills": (
            "firebase",
            "sqlite",
            "github actions",
            "mobile architecture",
            "state management",
            "fastlane",
        ),
        "summary_focus": (
            "Develop cross-platform mobile applications using "
            "Flutter, Dart, APIs, and maintainable application architecture."
        ),
    },
    {
        "stack_id": "mobile_react_native",
        "role_family": "mobile",
        "display_name": "React Native Mobile",
        "title_options": (
            "React Native Developer",
            "Cross-Platform Mobile Engineer",
            "JavaScript Mobile Developer",
        ),
        "required_skills": (
            "javascript",
            "react native",
            "rest api",
            "git",
            "unit testing",
        ),
        "preferred_skills": (
            "typescript",
            "firebase",
            "redux",
            "github actions",
            "mobile architecture",
            "fastlane",
        ),
        "summary_focus": (
            "Develop cross-platform mobile features using React "
            "Native, JavaScript, APIs, and reusable application components."
        ),
    },

    # =========================================================
    # UNITY GAME
    # =========================================================
    {
        "stack_id": "unity_gameplay",
        "role_family": "unity_game",
        "display_name": "Unity Gameplay Programming",
        "title_options": (
            "Unity Gameplay Developer",
            "Gameplay Programmer",
            "Unity Software Engineer",
        ),
        "required_skills": (
            "unity",
            "c#",
            "gameplay programming",
            "object oriented programming",
            "git",
        ),
        "preferred_skills": (
            "unity input system",
            "physics",
            "animation systems",
            "scriptable objects",
            "profiling",
            "cinemachine",
        ),
        "summary_focus": (
            "Implement responsive gameplay systems and reusable "
            "Unity architecture using C# and modern engine tooling."
        ),
    },
    {
        "stack_id": "unity_mobile",
        "role_family": "unity_game",
        "display_name": "Unity Mobile Game Development",
        "title_options": (
            "Unity Mobile Game Developer",
            "C# Game Developer",
            "Mobile Gameplay Engineer",
        ),
        "required_skills": (
            "unity",
            "c#",
            "game development",
            "mobile optimization",
            "git",
        ),
        "preferred_skills": (
            "unity input system",
            "addressables",
            "profiling",
            "ui systems",
            "firebase",
            "git lfs",
        ),
        "summary_focus": (
            "Develop and optimize Unity-based mobile games with "
            "attention to performance, responsiveness, and maintainability."
        ),
    },
    {
        "stack_id": "unity_simulation",
        "role_family": "unity_game",
        "display_name": "Unity Simulation Development",
        "title_options": (
            "Unity Simulation Engineer",
            "Unity Software Developer",
            "Simulation Software Engineer",
        ),
        "required_skills": (
            "unity",
            "c#",
            "physics",
            "object oriented programming",
            "git",
        ),
        "preferred_skills": (
            "artificial intelligence",
            "procedural generation",
            "multiplayer networking",
            "profiling",
            "ui systems",
            "git lfs",
        ),
        "summary_focus": (
            "Build interactive Unity simulations using C#, physics, "
            "data-driven systems, and maintainable software architecture."
        ),
    },
)


def get_stacks_for_role(
    role_family: str,
) -> tuple[TechnologyStack, ...]:
    return tuple(
        stack
        for stack in TECHNOLOGY_STACKS
        if stack["role_family"] == role_family
    )


def validate_technology_stacks() -> None:
    valid_roles = {
        "backend",
        "frontend",
        "full_stack",
        "machine_learning",
        "ai_engineering",
        "data_engineering",
        "data_science",
        "devops",
        "mobile",
        "unity_game",
    }

    seen_stack_ids: set[str] = set()

    for stack in TECHNOLOGY_STACKS:
        stack_id = stack["stack_id"]
        role_family = stack["role_family"]

        if stack_id in seen_stack_ids:
            raise ValueError(
                f"Duplicate technology stack ID: {stack_id}"
            )

        seen_stack_ids.add(stack_id)

        if role_family not in valid_roles:
            raise ValueError(
                f"Invalid role family '{role_family}' "
                f"in stack '{stack_id}'."
            )

        if len(stack["title_options"]) == 0:
            raise ValueError(
                f"Stack '{stack_id}' has no title options."
            )

        if len(stack["required_skills"]) < 4:
            raise ValueError(
                f"Stack '{stack_id}' must contain "
                "at least four required skills."
            )

        if len(stack["preferred_skills"]) < 2:
            raise ValueError(
                f"Stack '{stack_id}' must contain "
                "at least two preferred skills."
            )

        required_skills = set(
            stack["required_skills"]
        )

        preferred_skills = set(
            stack["preferred_skills"]
        )

        duplicate_skills = (
            required_skills
            & preferred_skills
        )

        if duplicate_skills:
            raise ValueError(
                f"Stack '{stack_id}' contains skills "
                "as both required and preferred: "
                f"{sorted(duplicate_skills)}"
            )

    missing_roles = {
        role
        for role in valid_roles
        if not get_stacks_for_role(role)
    }

    if missing_roles:
        raise ValueError(
            "No technology stacks defined for roles: "
            f"{sorted(missing_roles)}"
        )


validate_technology_stacks()