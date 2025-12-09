# src/oscal_cac/diff_review/node.py
"""LangGraph node implementation for OSCAL diff review."""

from __future__ import annotations

import json
from typing import Any, Dict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from ..config import OPENAI_MODEL
from ..loader import load_json


def _get_llm() -> ChatOpenAI:
    """Get a configured LLM instance."""
    return ChatOpenAI(model=OPENAI_MODEL, temperature=0)


_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a compliance-as-code reviewer specializing in OSCAL documents. "
            "Given two versions of an OSCAL JSON file, produce a concise review:\n"
            "- **Summary**: Brief overview of what changed\n"
            "- **Controls Affected**: Which controls / sections are affected\n"
            "- **Risk Assessment**: Does this increase, decrease, or not materially change risk?\n"
            "- **Recommendations**: Any suggestions for the change author\n\n"
            "Output in Markdown, suitable for a PR comment. "
            "Use diff-style formatting where helpful (+ for additions, - for removals)."
        ),
        (
            "human",
            "File (before): {path_before}\n```json\n{before_json}\n```\n\n"
            "File (after): {path_after}\n```json\n{after_json}\n```\n\n"
            "Write the review."
        ),
    ]
)


def diff_review_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node that reviews differences between two OSCAL files.
    
    Expects state to contain:
        - path_before: Path to the "before" OSCAL JSON file
        - path_after: Path to the "after" OSCAL JSON file
    
    Returns state updated with:
        - review_markdown: The PR-style review in Markdown format
    """
    path_before = state["path_before"]
    path_after = state["path_after"]

    before = load_json(path_before)
    after = load_json(path_after)

    before_str = json.dumps(before, indent=2, ensure_ascii=False)
    after_str = json.dumps(after, indent=2, ensure_ascii=False)
    
    # Truncate if too large
    max_chars = 30000
    if len(before_str) > max_chars:
        before_str = before_str[:max_chars] + "\n... [truncated]"
    if len(after_str) > max_chars:
        after_str = after_str[:max_chars] + "\n... [truncated]"

    llm = _get_llm()
    msg = _PROMPT.format(
        path_before=path_before,
        path_after=path_after,
        before_json=before_str,
        after_json=after_str,
    )
    resp = llm.invoke(msg.to_messages())
    
    return {"review_markdown": resp.content}
