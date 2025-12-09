# src/oscal_cac/remediation.py
"""Suggest remediation narratives and SSP snippets for NIST 800-53 controls."""

from __future__ import annotations

from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from .config import OPENAI_MODEL
from .loader import get_control_text


def _get_llm() -> ChatOpenAI:
    """Get a configured LLM instance."""
    return ChatOpenAI(model=OPENAI_MODEL, temperature=0)


_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a security architect writing OSCAL SSP content. "
            "Given a NIST SP 800-53 control description and optional system context, "
            "produce:\n"
            "1) A short remediation narrative (what the org should do), and\n"
            "2) A draft OSCAL SSP 'implemented-requirements' snippet for that control "
            "   (JSON, not full SSP, just the relevant fragment).\n\n"
            "The implemented-requirements snippet should follow OSCAL SSP schema and include:\n"
            "- control-id\n"
            "- uuid (use a placeholder like '{{uuid}}')\n"
            "- statements with statement-id and prose describing implementation\n"
            "- responsible-roles if applicable"
        ),
        (
            "human",
            "Control:\nID: {control_id}\nFamily: {family}\nTitle: {title}\n\n"
            "Text:\n{control_text}\n\n"
            "System context (optional):\n{context}\n\n"
            "Respond with:\n"
            "### Remediation\n"
            "<narrative>\n\n"
            "### Implemented-Requirements Snippet (JSON)\n"
            "```json\n<json here>\n```"
        ),
    ]
)


def suggest_remediation(control_id: str, context: Optional[str] = None) -> str:
    """
    Suggest remediation narrative and draft SSP snippet for a given control.
    
    Args:
        control_id: NIST 800-53 control ID (e.g., "AC-2", "AC-2.1")
        context: Optional free-text context about the system/environment
    
    Returns:
        Markdown-formatted response with remediation narrative and JSON snippet
    """
    ctl = get_control_text(control_id)
    if ctl is None:
        return f"Control '{control_id}' not found in 800-53 Rev 5 OSCAL catalog."

    llm = _get_llm()
    msg = _PROMPT.format(
        control_id=ctl["control_id"],
        family=ctl["family"],
        title=ctl["title"],
        control_text=ctl["text"],
        context=context or "(no additional context provided)",
    )
    resp = llm.invoke(msg.to_messages())
    return resp.content
