"""Command-line interface for ASCEND AI Sync."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.logging import RichHandler

from ascend_sync import __version__
from ascend_sync.conflict_classifier import Conflict, ConflictClassifier
from ascend_sync.drift_detector import DriftDetector
from ascend_sync.llm_resolver import LLMResolver
from ascend_sync.verifier import Verifier

console = Console()


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(console=console, show_time=False, show_path=False)],
    )


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """ASCEND AI Synchronization Module."""
    _configure_logging(verbose)
    ctx.ensure_object(dict)


@main.command("detect-drift")
@click.option("--source", required=True, type=click.Path(exists=True, path_type=Path),
              help="Source directory (e.g., production branch checkout).")
@click.option("--target", required=True, type=click.Path(exists=True, path_type=Path),
              help="Target directory (e.g., develop branch checkout).")
@click.option("--threshold", default=0.30, show_default=True, type=float,
              help="Drift risk score threshold.")
@click.option("--output", type=click.Path(path_type=Path),
              help="Write JSON report to this path (stdout if omitted).")
def detect_drift(source: Path, target: Path, threshold: float, output: Path | None) -> None:
    """Detect semantic drift between two filesystem trees."""
    detector = DriftDetector(threshold=threshold)
    report = detector.compare_trees(source, target, source_ref=str(source), target_ref=str(target))

    payload = json.dumps(report.to_dict(), indent=2)
    if output:
        output.write_text(payload, encoding="utf-8")
        console.print(f"[green]Report written to {output}[/green]")
    else:
        console.print_json(payload)

    if report.threshold_exceeded:
        console.print(f"[red]Drift risk {report.risk_score:.3f} exceeds threshold {threshold}[/red]")
        sys.exit(1)
    console.print(f"[green]Drift risk {report.risk_score:.3f} within threshold[/green]")


@main.command("classify")
@click.option("--file", "file_path", required=True, type=click.Path(exists=True, path_type=Path),
              help="Path to JSON file with {file_path, ours, theirs, base}.")
@click.option("--model", type=click.Path(exists=True, path_type=Path),
              help="Path to a trained classifier model (pickle).")
def classify_cmd(file_path: Path, model: Path | None) -> None:
    """Classify a merge conflict from a JSON description."""
    rec = json.loads(file_path.read_text(encoding="utf-8"))
    conflict = Conflict(
        file_path=rec.get("file_path", ""),
        ours=rec["ours"],
        theirs=rec["theirs"],
        base=rec.get("base", ""),
    )
    classifier = ConflictClassifier(model_path=model)
    classification = classifier.classify(conflict)
    console.print_json(json.dumps(classification.to_dict(), indent=2))


@main.command("resolve")
@click.option("--file", "file_path", required=True, type=click.Path(exists=True, path_type=Path),
              help="Path to JSON file with {file_path, ours, theirs, base}.")
@click.option("--provider", type=click.Choice(["openai", "anthropic", "local"]), default="local")
@click.option("--model", default="stub-model", help="LLM model name.")
@click.option("--candidates", default=3, type=int, help="Number of candidate resolutions.")
@click.option("--verify/--no-verify", default=True, help="Run verifier on each candidate.")
def resolve_cmd(file_path: Path, provider: str, model: str, candidates: int, verify: bool) -> None:
    """Generate candidate resolutions for a merge conflict."""
    rec = json.loads(file_path.read_text(encoding="utf-8"))
    conflict = Conflict(
        file_path=rec.get("file_path", ""),
        ours=rec["ours"],
        theirs=rec["theirs"],
        base=rec.get("base", ""),
    )

    classifier = ConflictClassifier()
    classification = classifier.classify(conflict)
    console.print(f"[cyan]Classified as:[/cyan] {classification.conflict_type.value} "
                  f"(confidence {classification.confidence:.2%})")

    resolver = LLMResolver(provider=provider, model=model, max_candidates=candidates)
    candidates_list = resolver.resolve(conflict, classification.conflict_type)
    console.print(f"[cyan]Generated {len(candidates_list)} candidate(s)[/cyan]")

    verifier = Verifier() if verify else None
    for i, resolution in enumerate(candidates_list):
        console.print(f"\n[bold]Candidate {i + 1}[/bold] "
                      f"(confidence {resolution.confidence:.2%})")
        console.print(resolution.resolved_code)
        if verifier:
            result = verifier.verify(conflict, resolution)
            console.print_json(json.dumps(result.to_dict(), indent=2))


@main.command("version")
def version_cmd() -> None:
    """Print the package version."""
    console.print(__version__)


if __name__ == "__main__":
    main()
