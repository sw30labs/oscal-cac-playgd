[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Enabled-green.svg)](https://langchain-ai.github.io/langgraph/)
[![NIST OSCAL](https://img.shields.io/badge/Docs-NIST%20OSCAL-0a67a3.svg)](https://pages.nist.gov/OSCAL/)
[![OSCAL Content](https://img.shields.io/badge/Repo-oscal--content-ff9800.svg)](https://github.com/usnistgov/oscal-content)
[![LangGraph Docs](https://img.shields.io/badge/Docs-LangGraph-4caf50.svg)](https://langchain-ai.github.io/langgraph/)
[![OSCAL JSON Reference](https://img.shields.io/badge/Reference-OSCAL%20JSON-9c27b0.svg)](https://pages.nist.gov/OSCAL-Reference/)

# oscal-cac-playground
> **Author:** [Nic Cravino](https://github.com/ai-agents-cybersecurity)  
> **License:** Apache 2.0  
> **Created:** December 2025


> A CLI that treats OSCAL as *compliance-as-code*: explain files, suggest remediation snippets, and review diffs with an LLM, using real NIST OSCAL JSON as the source of truth.
## Available Commands

| Command | Description |
|---------|-------------|
| `oscal-cac explain <file> [-p pointer]` | Explain OSCAL file/fragment in natural language |
| `oscal-cac suggest-remediation <control-id> [-c context]` | Generate remediation + SSP snippet |
| `oscal-cac review-diff <before> <after> [-o file]` | PR-style diff review |
| `oscal-cac list-controls [-f family] [-n limit]` | Browse 800-53 controls |
| `oscal-cac show-control <id>` | Show control details |

### Quick Start -- see here: [QUICKSTART.md](QUICKSTART.md)

-----

## Overview

**OSCAL Compliance-as-Code Playground** provides AI-assisted workflows for working with [OSCAL](https://pages.nist.gov/OSCAL/) (Open Security Controls Assessment Language) documents. It uses:

- **Official NIST OSCAL examples** via [`usnistgov/oscal-content`](https://github.com/usnistgov/oscal-content)
- **NIST SP 800-53 Rev 5** as the control catalog
- **LangChain + LangGraph** for LLM-powered analysis and generation

## Commands

### 1. Explain

Explain an OSCAL file or fragment in natural language:

```bash
oscal-cac explain data/samples/demo-ssp.json

oscal-cac explain data/samples/demo-ssp.json \
  --pointer "/system-security-plan/control-implementation"
```

### 2. Suggest Remediation

Look up a control in the 800-53 OSCAL catalog and generate:
- A remediation narrative
- A draft `implemented-requirements` snippet for an SSP

```bash
oscal-cac suggest-remediation AC-2

oscal-cac suggest-remediation AC-2 \
  --context "Small SaaS app on AWS with SSO via Okta"
```

### 3. Review Diff

Compare two OSCAL files (SSPs, profiles, etc.) and produce a PR-style review:

```bash
oscal-cac review-diff ssp-before.json ssp-after.json

# Write to file for CI/GitHub Actions
oscal-cac review-diff ssp-v1.json ssp-v2.json -o review.md
```

The review includes:
- What changed
- Which controls are impacted
- Risk assessment (increase/decrease/neutral)
- Recommendations

### 4. List Controls

Browse controls in the 800-53 Rev 5 catalog:

```bash
oscal-cac list-controls
oscal-cac list-controls --family ac
oscal-cac list-controls -f si -n 20
```

### 5. Show Control

Display details of a specific control:

```bash
oscal-cac show-control AC-2
oscal-cac show-control AU-3.1
```

## Installation

### Prerequisites

- Python 3.10+
- Git
- OpenAI API key (or compatible LLM provider)

### Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/oscal-cac-playground.git
cd oscal-cac-playground

# Add OSCAL content as a submodule
git submodule add https://github.com/usnistgov/oscal-content.git data/oscal-content
git submodule update --init --recursive

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .

# Or install dependencies directly
pip install langchain langchain-openai langchain-community langgraph typer rich python-dotenv

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Environment Variables

```bash
# Required
export OPENAI_API_KEY=sk-...

# Optional: Override default model
export OPENAI_MODEL=gpt-4o  # Default: gpt-4o-mini
```

## Usage

After installation, use the CLI:

```bash
# Via console script
oscal-cac --help

# Or run as module
python -m oscal_cac.cli --help
```

## Project Structure

```
oscal-cac-playground/
├── README.md
├── pyproject.toml
├── .env.example
│
├── data/
│   ├── oscal-content/          # git submodule: usnistgov/oscal-content
│   └── samples/
│       ├── demo-ssp.json       # Sample SSP for testing
│       └── demo-profile.json   # Sample profile for testing
│
└── src/
    └── oscal_cac/
        ├── __init__.py
        ├── config.py           # Paths, model configuration
        ├── loader.py           # OSCAL JSON helpers, catalog lookup
        ├── explain.py          # explain command logic
        ├── remediation.py      # suggest-remediation logic
        ├── cli.py              # Typer-based CLI entry point
        │
        └── diff_review/
            ├── __init__.py
            ├── graph.py        # LangGraph diff reviewer
            └── node.py         # Diff node implementation
```

## Roadmap

- [ ] **GitHub Action** - Run `review-diff` on PRs and post comments automatically
- [ ] **Schema validation** - Validate OSCAL documents against official JSON schemas
- [ ] **Lint command** - Check for common OSCAL best practices and org-specific conventions
- [ ] **Multi-model support** - Azure OpenAI, Anthropic, local models via Ollama
- [ ] **Interactive mode** - Chat-based OSCAL exploration
- [ ] **Integration** - Connect with other OSCAL tooling (oscal-cli, compliance-trestle)

## Related Projects

- [usnistgov/OSCAL](https://github.com/usnistgov/OSCAL) - OSCAL specification
- [usnistgov/oscal-content](https://github.com/usnistgov/oscal-content) - Official OSCAL examples
- [oscal-compass/compliance-trestle](https://github.com/oscal-compass/compliance-trestle) - Python SDK for OSCAL


