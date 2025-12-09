# src/oscal_cac/explain.py
"""Explain OSCAL files and fragments in natural language."""

from __future__ import annotations

import json
from typing import Any, Dict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from .config import OPENAI_MODEL
from .loader import load_json


def _get_llm() -> ChatOpenAI:
    """Get a configured LLM instance."""
    return ChatOpenAI(model=OPENAI_MODEL, temperature=0)


_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an OSCAL and security compliance expert. "
            "Explain the given OSCAL JSON fragment in clear language for a security engineer. "
            "Mention relevant concepts (catalog, profile, SSP, implemented-requirements, etc.) "
            "when helpful. Be concise but thorough."
        ),
        (
            "human",
            "File path: {path}\n"
            "JSON fragment:\n```json\n{fragment}\n```\n\n"
            "Explain what this represents and how it fits in OSCAL/compliance terms."
        ),
    ]
)


def _extract_fragment(doc: Dict[str, Any], pointer: str | None) -> Any:
    """
    Simple JSON Pointer-like navigation for paths like '/system-security-plan/control-implementation'.
    Not full RFC 6901, but good enough for a playground.
    
    Args:
        doc: The full JSON document
        pointer: JSON pointer-like path (e.g., "/catalog/groups/0/controls/0")
    
    Returns:
        The extracted fragment, or None if the path is invalid
    """
    if not pointer or pointer == "/":
        return doc

    # Strip leading slash and split
    parts = [p for p in pointer.split("/") if p]
    cur: Any = doc
    
    for p in parts:
        if isinstance(cur, dict):
            cur = cur.get(p)
        elif isinstance(cur, list):
            try:
                idx = int(p)
                cur = cur[idx]
            except (ValueError, IndexError):
                return None
        else:
            return None
        
        if cur is None:
            return None
    
    return cur


def explain_oscal(path: str, pointer: str | None = None) -> str:
    """
    Explain an OSCAL file or a specific fragment within it.
    
    Args:
        path: Path to the OSCAL JSON file
        pointer: Optional JSON pointer-like path to a specific fragment
    
    Returns:
        Natural language explanation of the OSCAL content
    """
    doc = load_json(path)
    frag = _extract_fragment(doc, pointer)
    
    if frag is None:
        return f"Could not resolve pointer '{pointer}' in file {path}."

    frag_str = json.dumps(frag, indent=2, ensure_ascii=False)
    
    # Truncate if too large (to stay within context limits)
    max_chars = 50000
    if len(frag_str) > max_chars:
        frag_str = frag_str[:max_chars] + "\n... [truncated]"

    llm = _get_llm()
    messages = _PROMPT.format_messages(path=path, fragment=frag_str)
    resp = llm.invoke(messages)
    return resp.content
