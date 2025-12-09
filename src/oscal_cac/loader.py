# src/oscal_cac/loader.py
"""OSCAL JSON loading and catalog lookup utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

from .config import OSCAL_80053R5_CATALOG


def load_json(path: str | Path) -> Dict[str, Any]:
    """Load a JSON file and return its contents as a dictionary."""
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str | Path, data: Dict[str, Any]) -> None:
    """Save a dictionary to a JSON file with pretty formatting."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _iter_controls_from_catalog(
    catalog_json: Dict[str, Any],
) -> Generator[Tuple[str, Dict[str, Any]], None, None]:
    """
    Iterate over all controls in a catalog, yielding (family_id, control_dict) tuples.
    Also handles nested control enhancements.
    """
    catalog = catalog_json.get("catalog", catalog_json)
    for group in catalog.get("groups", []):
        family = group.get("id", "")
        for ctl in group.get("controls", []):
            yield family, ctl
            # Also yield control enhancements (nested controls)
            for enhancement in ctl.get("controls", []):
                yield family, enhancement


def load_80053_catalog() -> Dict[str, Any]:
    """Load the NIST SP 800-53 Rev 5 OSCAL catalog."""
    return load_json(OSCAL_80053R5_CATALOG)


def get_control_text(control_id: str) -> Optional[Dict[str, Any]]:
    """
    Return a dict with control_id, family, title, and text from the 800-53 Rev 5 catalog.
    
    The control_id can be a base control (e.g., "AC-2") or an enhancement (e.g., "AC-2.1").
    Returns None if the control is not found.
    """
    # Normalize control ID (handle both AC-2 and ac-2 formats)
    control_id_lower = control_id.lower()
    
    catalog = load_80053_catalog()
    for family, ctl in _iter_controls_from_catalog(catalog):
        cid = ctl.get("id", "")
        if cid.lower() == control_id_lower:
            title = ctl.get("title", "")
            parts = ctl.get("parts", [])
            texts: List[str] = []
            if title:
                texts.append(f"**{title}**")
            
            # Extract prose from parts recursively
            _extract_prose(parts, texts)
            
            return {
                "control_id": cid,
                "family": family,
                "title": title,
                "text": "\n\n".join(texts),
            }
    return None


def _extract_prose(parts: List[Dict[str, Any]], texts: List[str], indent: int = 0) -> None:
    """Recursively extract prose from control parts."""
    for p in parts:
        prose = p.get("prose")
        if prose:
            # Add indentation for nested parts
            prefix = "  " * indent
            texts.append(f"{prefix}{prose}")
        # Handle nested parts
        sub_parts = p.get("parts", [])
        if sub_parts:
            _extract_prose(sub_parts, texts, indent + 1)


def list_controls(family_filter: Optional[str] = None) -> List[Dict[str, str]]:
    """
    List all controls in the 800-53 Rev 5 catalog.
    
    Optionally filter by family (e.g., "ac" for Access Control).
    Returns a list of dicts with control_id, family, and title.
    """
    catalog = load_80053_catalog()
    controls = []
    
    for family, ctl in _iter_controls_from_catalog(catalog):
        if family_filter and not family.lower().startswith(family_filter.lower()):
            continue
        controls.append({
            "control_id": ctl.get("id", ""),
            "family": family,
            "title": ctl.get("title", ""),
        })
    
    return controls
