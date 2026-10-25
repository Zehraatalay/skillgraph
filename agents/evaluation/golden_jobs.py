from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.job import JobPosting
from agents.schemas.job_evaluation import JobEvaluationCase
from agents.schemas.requirement_group import RequirementGroup


def make_group(
    skills: list[str],
    evidence: str,
    priority: str = "required",
    operator: str = "all",
) -> RequirementGroup:
    return RequirementGroup(
        skills=skills,
        evidence=evidence,
        priority=priority,
        operator=operator,
    )


def make_case(
    name: str,
    job_id: str,
    title: str,
    description: str,
    groups: list[RequirementGroup],
) -> JobEvaluationCase:
    return JobEvaluationCase(
        name=name,
        job=JobPosting(
            id=job_id,
            title=title,
            description=description,
        ),
        expected=GroupedJobAnalysis(
            job_id=job_id,
            requirement_groups=groups,
        ),
    )


GOLDEN_CASES = [
    make_case(
        name="junior_ml_engineer",
        job_id="golden-001",
        title="Junior Machine Learning Engineer",
        description=(
            "Requirements:\n"
            "- Strong programming skills in Python.\n"
            "- Experience working with NumPy and Pandas.\n"
            "- Understanding of machine learning fundamentals.\n"
            "- Experience with Git version control.\n"
            "\n"
            "Nice to have:\n"
            "- Familiarity with PyTorch or TensorFlow.\n"
            "- Experience building REST APIs using FastAPI.\n"
            "- Knowledge of Docker and containerization."
        ),
        groups=[
            make_group(
                ["Python"],
                "Strong programming skills in Python.",
            ),
            make_group(
                ["NumPy", "Pandas"],
                "Experience working with NumPy and Pandas.",
            ),
            make_group(
                ["Machine Learning Fundamentals"],
                "Understanding of machine learning fundamentals.",
            ),
            make_group(
                ["Git"],
                "Experience with Git version control.",
            ),
            make_group(
                ["PyTorch", "TensorFlow"],
                "Familiarity with PyTorch or TensorFlow.",
                priority="preferred",
                operator="any",
            ),
            make_group(
                ["REST APIs", "FastAPI"],
                "Experience building REST APIs using FastAPI.",
                priority="preferred",
            ),
            make_group(
                ["Docker", "Containerization"],
                "Knowledge of Docker and containerization.",
                priority="preferred",
            ),
        ],
    ),
    make_case(
        name="junior_data_analyst",
        job_id="golden-002",
        title="Junior Data Analyst",
        description=(
            "Requirements:\n"
            "- Proficiency in SQL.\n"
            "- Strong Excel skills.\n"
            "- Experience with Power BI or Tableau.\n"
            "\n"
            "Preferred qualifications:\n"
            "- Familiarity with Python.\n"
            "- Knowledge of statistical analysis."
        ),
        groups=[
            make_group(
                ["SQL"],
                "Proficiency in SQL.",
            ),
            make_group(
                ["Excel"],
                "Strong Excel skills.",
            ),
            make_group(
                ["Power BI", "Tableau"],
                "Experience with Power BI or Tableau.",
                operator="any",
            ),
            make_group(
                ["Python"],
                "Familiarity with Python.",
                priority="preferred",
            ),
            make_group(
                ["Statistical Analysis"],
                "Knowledge of statistical analysis.",
                priority="preferred",
            ),
        ],
    ),
    make_case(
        name="ai_engineer",
        job_id="golden-003",
        title="AI Engineer",
        description=(
            "Requirements:\n"
            "- Experience developing applications with large language models.\n"
            "- Knowledge of retrieval-augmented generation (RAG).\n"
            "- Experience with vector databases such as FAISS or Chroma.\n"
            "- Strong Python programming skills.\n"
            "\n"
            "Nice to have:\n"
            "- Familiarity with LangChain or LlamaIndex."
        ),
        groups=[
            make_group(
                ["Large Language Models"],
                "Experience developing applications with large language models.",
            ),
            make_group(
                ["RAG"],
                "Knowledge of retrieval-augmented generation (RAG).",
            ),
            make_group(
                ["FAISS", "Chroma"],
                "Experience with vector databases such as FAISS or Chroma.",
                operator="any",
            ),
            make_group(
                ["Python"],
                "Strong Python programming skills.",
            ),
            make_group(
                ["LangChain", "LlamaIndex"],
                "Familiarity with LangChain or LlamaIndex.",
                priority="preferred",
                operator="any",
            ),
        ],
    ),
    make_case(
        name="backend_engineer",
        job_id="golden-004",
        title="Backend Engineer",
        description=(
            "Requirements:\n"
            "- Experience developing REST APIs with Python.\n"
            "- Knowledge of PostgreSQL.\n"
            "- Experience using Docker.\n"
            "\n"
            "Preferred:\n"
            "- Familiarity with Redis.\n"
            "- Experience with AWS or Google Cloud."
        ),
        groups=[
            make_group(
                ["Python", "REST APIs"],
                "Experience developing REST APIs with Python.",
            ),
            make_group(
                ["PostgreSQL"],
                "Knowledge of PostgreSQL.",
            ),
            make_group(
                ["Docker"],
                "Experience using Docker.",
            ),
            make_group(
                ["Redis"],
                "Familiarity with Redis.",
                priority="preferred",
            ),
            make_group(
                ["AWS", "Google Cloud"],
                "Experience with AWS or Google Cloud.",
                priority="preferred",
                operator="any",
            ),
        ],
    ),
    make_case(
        name="no_technical_requirements",
        job_id="golden-005",
        title="General Operations Assistant",
        description=(
            "We are looking for a motivated team member.\n"
            "Responsibilities include coordinating meetings, "
            "communicating with stakeholders, and supporting "
            "daily operations.\n"
            "Strong communication and organizational skills "
            "are preferred."
        ),
        groups=[],
    ),
]
