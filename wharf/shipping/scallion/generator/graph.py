from __future__ import annotations

from langgraph.graph import StateGraph, END

from generator.state import GraphState
from generator.nodes.planner import planner_node
from generator.nodes.validator import validator_node
from generator.nodes.executor import executor_node
from generator.nodes.finalizer import finalizer_node
from generator.config import settings


PLANNER = "planner"
VALIDATOR = "validator"
EXECUTOR = "executor"
FINALIZER = "finalizer"


def _route_after_validate(state: GraphState) -> str:
    err = state.get("last_error", "")
    rev = int(state.get("revision_count", 0))

    if not err:
        return EXECUTOR

    if rev < settings.max_plan_revisions:
        return PLANNER

    return FINALIZER


def build_graph():
    g = StateGraph(GraphState)

    g.add_node(PLANNER, planner_node)
    g.add_node(VALIDATOR, validator_node)
    g.add_node(EXECUTOR, executor_node)
    g.add_node(FINALIZER, finalizer_node)

    g.set_entry_point(PLANNER)
    g.add_edge(PLANNER, VALIDATOR)

    g.add_conditional_edges(
        VALIDATOR,
        _route_after_validate,
        {EXECUTOR: EXECUTOR, PLANNER: PLANNER, FINALIZER: FINALIZER},
    )

    g.add_edge(EXECUTOR, FINALIZER)
    g.add_edge(FINALIZER, END)

    return g.compile()
