# src/oscal_cac/cli.py
"""Typer-based CLI entry point for OSCAL Compliance-as-Code Playground."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown

from .explain import explain_oscal
from .remediation import suggest_remediation
from .diff_review.graph import build_diff_graph
from .loader import list_controls, get_control_text

app = typer.Typer(
    name="oscal-cac",
    help="OSCAL Compliance-as-Code Playground CLI - AI-assisted OSCAL workflows.",
    add_completion=False,
)

console = Console()


def _print_markdown(text: str) -> None:
    """Print text as formatted Markdown."""
    md = Markdown(text)
    console.print(md)


@app.command()
def explain(
    path: str = typer.Argument(..., help="Path to an OSCAL JSON file."),
    pointer: Optional[str] = typer.Option(
        None,
        "--pointer",
        "-p",
        help="Optional JSON pointer-like path inside the file (e.g., /system-security-plan/control-implementation).",
    ),
    raw: bool = typer.Option(
        False,
        "--raw",
        "-r",
        help="Output raw text instead of formatted Markdown.",
    ),
) -> None:
    """
    Explain an OSCAL file or fragment in natural language.
    
    Examples:
        oscal-cac explain data/samples/demo-ssp.json
        oscal-cac explain data/samples/demo-ssp.json -p /system-security-plan/metadata
    """
    # Validate file exists
    if not Path(path).exists():
        console.print(f"[red]Error:[/red] File not found: {path}")
        raise typer.Exit(1)
    
    with console.status("[bold green]Analyzing OSCAL file..."):
        result = explain_oscal(path, pointer)
    
    if raw:
        typer.echo(result)
    else:
        _print_markdown(result)


@app.command("suggest-remediation")
def suggest_remediation_cmd(
    control_id: str = typer.Argument(..., help="Control ID, e.g., AC-2 or AC-2.1"),
    context: Optional[str] = typer.Option(
        None,
        "--context",
        "-c",
        help="Optional free-text context about the system/environment.",
    ),
    raw: bool = typer.Option(
        False,
        "--raw",
        "-r",
        help="Output raw text instead of formatted Markdown.",
    ),
) -> None:
    """
    Suggest remediation + draft SSP snippet for a given NIST 800-53 control.
    
    Examples:
        oscal-cac suggest-remediation AC-2
        oscal-cac suggest-remediation AC-2 -c "Small SaaS app on AWS with SSO via Okta"
    """
    with console.status(f"[bold green]Looking up {control_id} and generating remediation..."):
        result = suggest_remediation(control_id, context)
    
    if raw:
        typer.echo(result)
    else:
        _print_markdown(result)


@app.command("review-diff")
def review_diff(
    before: str = typer.Argument(..., help="Path to OSCAL JSON file (before)."),
    after: str = typer.Argument(..., help="Path to OSCAL JSON file (after)."),
    raw: bool = typer.Option(
        False,
        "--raw",
        "-r",
        help="Output raw text instead of formatted Markdown.",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Write the review to a file instead of stdout.",
    ),
) -> None:
    """
    Compare two OSCAL JSON files and produce a PR-style review (Markdown).
    
    Examples:
        oscal-cac review-diff ssp-before.json ssp-after.json
        oscal-cac review-diff ssp-v1.json ssp-v2.json -o review.md
    """
    # Validate files exist
    for path, label in [(before, "before"), (after, "after")]:
        if not Path(path).exists():
            console.print(f"[red]Error:[/red] {label.capitalize()} file not found: {path}")
            raise typer.Exit(1)
    
    with console.status("[bold green]Reviewing OSCAL diff..."):
        graph = build_diff_graph()
        state = {"path_before": before, "path_after": after}
        result = graph.invoke(state)
    
    review_md = result.get("review_markdown", "")
    
    if output:
        Path(output).write_text(review_md, encoding="utf-8")
        console.print(f"[green]Review written to:[/green] {output}")
    elif raw:
        typer.echo(review_md)
    else:
        _print_markdown(review_md)


@app.command("list-controls")
def list_controls_cmd(
    family: Optional[str] = typer.Option(
        None,
        "--family",
        "-f",
        help="Filter by control family (e.g., 'ac' for Access Control).",
    ),
    limit: int = typer.Option(
        50,
        "--limit",
        "-n",
        help="Maximum number of controls to display.",
    ),
) -> None:
    """
    List controls from the NIST 800-53 Rev 5 catalog.
    
    Examples:
        oscal-cac list-controls
        oscal-cac list-controls --family ac
        oscal-cac list-controls -f si -n 20
    """
    try:
        controls = list_controls(family_filter=family)
    except FileNotFoundError:
        console.print(
            "[red]Error:[/red] OSCAL catalog not found. "
            "Did you add the oscal-content submodule?\n"
            "Run: git submodule add https://github.com/usnistgov/oscal-content.git data/oscal-content"
        )
        raise typer.Exit(1)
    
    if not controls:
        console.print(f"[yellow]No controls found for family filter: {family}[/yellow]")
        return
    
    displayed = controls[:limit]
    console.print(f"\n[bold]NIST SP 800-53 Rev 5 Controls[/bold]")
    if family:
        console.print(f"[dim]Filtered by family: {family.upper()}[/dim]")
    console.print(f"[dim]Showing {len(displayed)} of {len(controls)} controls[/dim]\n")
    
    for ctl in displayed:
        console.print(f"  [cyan]{ctl['control_id']}[/cyan] - {ctl['title']}")
    
    if len(controls) > limit:
        console.print(f"\n[dim]... and {len(controls) - limit} more. Use --limit to see more.[/dim]")


@app.command("show-control")
def show_control_cmd(
    control_id: str = typer.Argument(..., help="Control ID, e.g., AC-2 or AC-2.1"),
) -> None:
    """
    Show details of a specific NIST 800-53 control.
    
    Examples:
        oscal-cac show-control AC-2
        oscal-cac show-control AU-3.1
    """
    try:
        ctl = get_control_text(control_id)
    except FileNotFoundError:
        console.print(
            "[red]Error:[/red] OSCAL catalog not found. "
            "Did you add the oscal-content submodule?"
        )
        raise typer.Exit(1)
    
    if ctl is None:
        console.print(f"[red]Control '{control_id}' not found in 800-53 Rev 5 catalog.[/red]")
        raise typer.Exit(1)
    
    console.print(f"\n[bold cyan]{ctl['control_id']}[/bold cyan] - [bold]{ctl['title']}[/bold]")
    console.print(f"[dim]Family: {ctl['family'].upper()}[/dim]\n")
    _print_markdown(ctl["text"])


@app.callback()
def callback() -> None:
    """
    OSCAL Compliance-as-Code Playground CLI.
    
    Use LLM-powered commands to explain, remediate, and review OSCAL documents.
    """
    pass


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
