from __future__ import annotations

from typer.testing import CliRunner

from oscal_cac import cli

runner = CliRunner()


def test_help_command() -> None:
    result = runner.invoke(cli.app, ["--help"])

    assert result.exit_code == 0
    assert "OSCAL Compliance-as-Code Playground CLI" in result.output


def test_list_controls_happy_path(monkeypatch) -> None:
    monkeypatch.setattr(
        cli,
        "list_controls",
        lambda family_filter=None: [
            {"control_id": "AC-2", "family": "ac", "title": "Account Management"}
        ],
    )

    result = runner.invoke(cli.app, ["list-controls", "--limit", "1"])

    assert result.exit_code == 0
    assert "AC-2" in result.output


def test_explain_missing_file() -> None:
    result = runner.invoke(cli.app, ["explain", "/tmp/this-file-does-not-exist.json"])

    assert result.exit_code == 1
    assert "File not found" in result.output
