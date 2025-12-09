### Project Structure
```
oscal-cac-playground/
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── data/
│   ├── oscal-content/          # git submodule (NIST OSCAL examples)
│   └── samples/
│       ├── demo-ssp.json
│       ├── demo-profile.json
│       ├── ssp-before.json     # for diff testing
│       └── ssp-after.json
└── src/oscal_cac/
    ├── __init__.py
    ├── config.py
    ├── loader.py
    ├── explain.py
    ├── remediation.py
    ├── cli.py
    └── diff_review/
        ├── __init__.py
        ├── graph.py
        └── node.py
```

### Available Commands

| Command | Description |
|---------|-------------|
| `oscal-cac explain <file> [-p pointer]` | Explain OSCAL file/fragment in natural language |
| `oscal-cac suggest-remediation <control-id> [-c context]` | Generate remediation + SSP snippet |
| `oscal-cac review-diff <before> <after> [-o file]` | PR-style diff review |
| `oscal-cac list-controls [-f family] [-n limit]` | Browse 800-53 controls |
| `oscal-cac show-control <id>` | Show control details |

### Quick Start

```bash
# Set your API key
export OPENAI_API_KEY=sk-...

# Try the commands
oscal-cac list-controls --family ac -n 10
oscal-cac show-control AC-2
oscal-cac explain data/samples/demo-ssp.json
oscal-cac suggest-remediation AC-2 -c "AWS-based SaaS with Okta SSO"
oscal-cac review-diff data/samples/ssp-before.json data/samples/ssp-after.json
```

The NIST SP 800-53 Rev 5 catalog is loaded from the `oscal-content` submodule with **1000+ controls** available for lookup.