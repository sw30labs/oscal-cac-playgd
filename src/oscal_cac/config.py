# src/oscal_cac/config.py
"""Configuration for OSCAL CaC Playground."""

from pathlib import Path
import os

from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]

OSCAL_CONTENT_DIR = BASE_DIR / "data" / "oscal-content"

# NIST SP 800-53 Rev 5 OSCAL catalog
# Path based on oscal-content repo structure
OSCAL_80053R5_CATALOG = (
    OSCAL_CONTENT_DIR
    / "nist.gov"
    / "SP800-53"
    / "rev5"
    / "json"
    / "NIST_SP-800-53_rev5_catalog.json"
)

# LLM configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
