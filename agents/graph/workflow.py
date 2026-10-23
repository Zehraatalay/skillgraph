from langgraph.graph import StateGraph, START, END

from agents.graph.state import SkillGraphState
from agents.graph.routing import (
    route_after_validation,
    route_github,
)

from agents.nodes.validate_input import validate_input
from agents.nodes.cv_analysis import analyze_cv
from agents.nodes.portfolio import analyze_github
from agents.nodes.candidate_profile import build_candidate_profile


def build_workflow(checkpointer=None):
    workflow = StateGraph(SkillGraphState)

    workflow.add_node("validate_input", validate_input)
    workflow.add_node("analyze_cv", analyze_cv)
    workflow.add_node("analyze_github", analyze_github)
    workflow.add_node("build_candidate_profile", build_candidate_profile)

    workflow.add_edge(START, "validate_input")

    workflow.add_conditional_edges(
        "validate_input",
        route_after_validation,
        {
            "analyze_cv": "analyze_cv",
            "check_github": "check_github",
        },
    )

    workflow.add_node("check_github", lambda state: {})

    workflow.add_edge("analyze_cv", "check_github")

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

    workflow.add_edge(
        "build_candidate_profile",
        END,
    )

    return workflow.compile(checkpointer=checkpointer)