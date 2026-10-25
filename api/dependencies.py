import os
from functools import lru_cache

from dotenv import load_dotenv

from agents.graph.workflow import build_workflow
from agents.services.cv_extractor import CVExtractor
from agents.services.explainable_job_matcher import (
    ExplainableJobMatcher,
)
from agents.services.extraction_cache import ExtractionCache
from agents.services.github_analyzer import GitHubAnalyzer
from agents.services.github_client import GitHubClient
from agents.services.github_evidence_extractor import (
    GitHubEvidenceExtractor,
)
from agents.services.grouped_job_requirement_extractor import (
    GroupedJobRequirementExtractor,
)
from agents.services.hybrid_job_matcher import (
    HybridJobMatcher,
)
from agents.services.llm_factory import create_llm
from agents.services.repository_research import (
    RepositoryResearchService,
)
from agents.services.research_collector import (
    RepositoryResearchCollector,
)
from agents.services.semantic_skill_matcher import (
    SemanticSkillMatcher,
)

load_dotenv(dotenv_path=".env")


@lru_cache(maxsize=1)
def get_workflow():
    llm = create_llm()

    provider = (
        os.getenv(
            "LLM_PROVIDER",
            "gemini",
        )
        .strip()
        .lower()
    )

    if provider == "ollama":
        model_name = os.getenv(
            "OLLAMA_MODEL",
            "qwen2.5-coder:7b",
        )
    else:
        model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash",
        )

    model_id = f"{provider}:{model_name}"

    # --------------------------------------------------
    # 2. Extraction cache
    # --------------------------------------------------

    cache = ExtractionCache()

    # --------------------------------------------------
    # 3. CV and job extraction
    # --------------------------------------------------

    cv_extractor = CVExtractor(
        llm,
        cache=cache,
    )

    job_extractor = GroupedJobRequirementExtractor(
        llm,
        cache=cache,
    )

    # --------------------------------------------------
    # 4. GitHub analysis
    # --------------------------------------------------

    github_client = GitHubClient(
        token=os.getenv("GITHUB_TOKEN"),
    )

    research_service = RepositoryResearchService(
        max_source_files=8,
        max_test_files=4,
    )

    collector = RepositoryResearchCollector(
        github_client=github_client,
        max_chars_per_file=12_000,
        max_total_chars=60_000,
    )

    github_extractor = GitHubEvidenceExtractor(
        llm,
    )

    github_analyzer = GitHubAnalyzer(
        github_client=github_client,
        research_service=research_service,
        collector=collector,
        extractor=github_extractor,
        max_repositories=3,
        cache=cache,
        model_id=model_id,
    )

    # --------------------------------------------------
    # 5. Semantic matching
    # --------------------------------------------------

    semantic_matcher = SemanticSkillMatcher(
        model=llm,
    )

    # --------------------------------------------------
    # 6. Hybrid matching
    # --------------------------------------------------

    hybrid_matcher = HybridJobMatcher(
        semantic_matcher=semantic_matcher,
    )

    # --------------------------------------------------
    # 7. Explainable matching
    # --------------------------------------------------

    explainable_matcher = ExplainableJobMatcher(
        job_matcher=hybrid_matcher,
    )

    # --------------------------------------------------
    # 8. LangGraph workflow
    # --------------------------------------------------

    return build_workflow(
        cv_extractor=cv_extractor,
        github_analyzer=github_analyzer,
        job_extractor=job_extractor,
        job_matcher=explainable_matcher,
    )
