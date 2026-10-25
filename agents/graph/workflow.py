from langgraph.graph import END, START, StateGraph

from agents.graph.routing import (
    route_after_validation,
    route_github,
)
from agents.graph.state import SkillGraphState
from agents.nodes.candidate_profile import build_candidate_profile
from agents.nodes.cv_analysis import create_cv_analysis_node
from agents.nodes.github_analysis import analyze_github
from agents.nodes.job_analysis import create_job_analysis_node
from agents.nodes.job_matching import create_job_matching_node
from agents.nodes.validate_input import (
    create_validate_input_node,
)
from agents.services.cv_extractor import NoOpCVExtractor
from agents.services.explainable_job_matcher import (
    ExplainableJobMatcher,
)
from agents.services.github_analyzer import GitHubAnalyzer


def build_workflow(
    checkpointer=None,
    cv_extractor=None,
    github_analyzer: GitHubAnalyzer | None = None,
    job_extractor=None,
    job_matcher: ExplainableJobMatcher | None = None,
):
    # --------------------------------------------------
    # 1. Default dependencies
    # --------------------------------------------------

    if cv_extractor is None:
        cv_extractor = NoOpCVExtractor()

    # --------------------------------------------------
    # 2. Initialize workflow
    # --------------------------------------------------

    workflow = StateGraph(SkillGraphState)

    # --------------------------------------------------
    # 3. Candidate analysis nodes
    # --------------------------------------------------

    workflow.add_node(
        "validate_input",
        create_validate_input_node(require_job_postings=job_extractor is not None),
    )

    workflow.add_node(
        "analyze_cv",
        create_cv_analysis_node(cv_extractor),
    )

    workflow.add_node(
        "analyze_github",
        lambda state: analyze_github(
            state,
            analyzer=github_analyzer,
        ),
    )

    workflow.add_node(
        "build_candidate_profile",
        build_candidate_profile,
    )

    workflow.add_node(
        "check_github",
        lambda state: {},
    )

    # --------------------------------------------------
    # 4. Job analysis and matching nodes (optional)
    # --------------------------------------------------

    if job_extractor is not None:
        workflow.add_node(
            "analyze_jobs",
            create_job_analysis_node(job_extractor),
        )

        workflow.add_node(
            "match_jobs",
            create_job_matching_node(job_matcher),
        )

    # --------------------------------------------------
    # 5. Entry point
    # --------------------------------------------------

    workflow.add_edge(
        START,
        "validate_input",
    )

    # --------------------------------------------------
    # 6. CV routing
    # --------------------------------------------------

    workflow.add_conditional_edges(
        "validate_input",
        route_after_validation,
        {
            "analyze_cv": "analyze_cv",
            "check_github": "check_github",
        },
    )

    workflow.add_edge(
        "analyze_cv",
        "check_github",
    )

    # --------------------------------------------------
    # 7. GitHub routing
    # --------------------------------------------------

    workflow.add_conditional_edges(
        "check_github",
        route_github,
        {
            "analyze_github": "analyze_github",
            "build_candidate_profile": "build_candidate_profile",
        },
    )

    workflow.add_edge(
        "analyze_github",
        "build_candidate_profile",
    )

    # --------------------------------------------------
    # 8. Job workflow routing
    # --------------------------------------------------

    if job_extractor is not None:
        workflow.add_edge(
            "build_candidate_profile",
            "analyze_jobs",
        )

        workflow.add_edge(
            "analyze_jobs",
            "match_jobs",
        )

        workflow.add_edge(
            "match_jobs",
            END,
        )

    else:
        workflow.add_edge(
            "build_candidate_profile",
            END,
        )

    # --------------------------------------------------
    # 9. Compile workflow
    # --------------------------------------------------

    return workflow.compile(
        checkpointer=checkpointer,
    )
