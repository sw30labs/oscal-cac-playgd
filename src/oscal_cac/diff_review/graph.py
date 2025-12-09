# src/oscal_cac/diff_review/graph.py
"""LangGraph graph definition for OSCAL diff review."""

from __future__ import annotations

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

from .node import diff_review_node


class DiffState(TypedDict, total=False):
    """State schema for the diff review graph."""
    path_before: str
    path_after: str
    review_markdown: str


def build_diff_graph():
    """
    Build and compile the LangGraph for diff review.
    
    The graph currently has a single node that performs the diff review,
    but can be extended with additional nodes for:
    - Schema validation
    - Semantic diffing
    - Multi-pass analysis
    - Tool-augmented review
    
    Returns:
        Compiled LangGraph ready for invocation
    """
    g = StateGraph(DiffState)
    
    # Add the diff review node
    g.add_node("diff_review", diff_review_node)
    
    # Wire up the graph: START -> diff_review -> END
    g.add_edge(START, "diff_review")
    g.add_edge("diff_review", END)
    
    return g.compile()
