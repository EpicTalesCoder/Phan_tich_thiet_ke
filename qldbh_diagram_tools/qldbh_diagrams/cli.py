"""Command-line interface for automatic diagram generation."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .generator import generate_plantuml, generate_scenario_markdown
from .validate import DefinitionError, validate_definition


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as error:
        raise DefinitionError(f"File not found: {path}") from error
    except json.JSONDecodeError as error:
        raise DefinitionError(f"Invalid JSON in {path}: line {error.lineno}, column {error.colno}") from error


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def ensure_valid_output_path(path: Path, output_format: str) -> Path:
    if path.suffix.lower() != f".{output_format.lower()}":
        return path.with_suffix(f".{output_format.lower()}")
    return path


def detect_java_command() -> str:
    bundled_java = Path(__file__).resolve().parent.parent / "vendor" / "jre" / "Contents" / "Home" / "bin" / "java"
    if bundled_java.exists():
        return str(bundled_java)
    return "java"


def render_file(plantuml_file: Path, output_file: Path, *, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    command = [
        detect_java_command(),
        "-Djava.awt.headless=true",
        "-Djava.locale.providers=HOST",
        "-jar",
        str(PLANTUML_JAR),
        "-charset",
        "UTF-8",
        "-t" + output_file.suffix[1:],
        "-o",
        str(output_file.parent.resolve()),
        str(plantuml_file.resolve()),
    ]
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as error:
        raise DefinitionError(
            "Cannot run PlantUML. Install Java and set PLANTUML_JAR to the path of plantuml.jar."
        ) from error
    if result.returncode != 0:
        details = result.stderr.strip() or result.stdout.strip() or "unknown PlantUML error"
        raise DefinitionError(f"PlantUML render failed: {details}")
    return result


def expected_output_file(plantuml_file: Path, output_format: str) -> Path:
    suffix = plantuml_file.suffix.lower()
    if suffix in {".puml", ".plantuml"}:
        output_name = plantuml_file.with_suffix(f".{output_format}").name
        return plantuml_file.parent / output_name
    return plantuml_file.parent / f"{plantuml_file.stem}.{output_format}"


PLANTUML_JAR = Path(__file__).resolve().parent.parent / "vendor" / "plantuml.jar"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qldbh-diagrams",
        description="Generate and render software-analysis diagrams from JSON definitions.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate one or more JSON diagram definitions")
    validate_parser.add_argument("input", type=Path, help="JSON definition file")

    generate_parser = subparsers.add_parser("generate", help="Generate PlantUML, Markdown, or all sources")
    generate_parser.add_argument("input", type=Path, help="JSON definition file")
    output_group = generate_parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument("--out-dir", type=Path, help="Directory for generated files")
    output_group.add_argument("--stdout", action="store_true", help="Print generated source to stdout")
    generate_parser.add_argument("--scenario", action="store_true", help="Generate Markdown scenario instead of PlantUML")
    generate_parser.add_argument("--name", help="Override output file base name when writing files")
    generate_parser.add_argument("--style", choices=["vp", "plain"], default="vp",
                                 help="vp = Visual-Paradigm-like white/black theme (default)")
    generate_parser.add_argument("--engine", choices=["smetana", "dot"], default="smetana",
                                 help="dot needs Graphviz installed but lays out better")

    render_parser = subparsers.add_parser(
        "render",
        help="Generate sources then render diagrams with plantuml.jar",
    )
    render_parser.add_argument("input", type=Path)
    render_parser.add_argument("--out-dir", type=Path, default=Path("output"), help="Output directory")
    render_parser.add_argument("--name", help="Output base name override")
    render_parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="PlantUML process timeout in seconds",
    )
    render_parser.add_argument("--style", choices=["vp", "plain"], default="vp",
                               help="vp = Visual-Paradigm-like white/black theme (default)")
    render_parser.add_argument("--engine", choices=["smetana", "dot"], default="smetana",
                               help="dot needs Graphviz installed but lays out better")

    schemas_parser = subparsers.add_parser("examples", help="List built-in diagram IDs")
    schemas_parser.add_argument("--json", action="store_true")

    return parser


def command_validate(args: argparse.Namespace) -> int:
    diagrams = validate_definition(load_json(args.input))
    print(f"Valid: {len(diagrams)} diagram definition(s)")
    for diagram in diagrams:
        print(f"  - {diagram['id']} ({diagram['type']})")
    return 0


def command_generate(args: argparse.Namespace) -> int:
    diagrams = validate_definition(load_json(args.input))
    if args.stdout:
        if len(diagrams) != 1:
            raise DefinitionError("--stdout requires a file with exactly one diagram")
        diagram = diagrams[0]
        if args.scenario or diagram["type"] == "use_case_scenario":
            print(generate_scenario_markdown(diagram["data"]), end="")
        else:
            print(generate_plantuml(diagram, style=args.style, engine=args.engine), end="")
        return 0

    if args.out_dir is None:
        raise DefinitionError("Choose --out-dir or --stdout")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for diagram in diagrams:
        base_name = args.name or diagram["id"]
        if args.scenario or diagram["type"] == "use_case_scenario":
            output_file = args.out_dir / f"{base_name}.md"
            content = generate_scenario_markdown(diagram["data"])
        else:
            output_file = args.out_dir / f"{base_name}.puml"
            content = generate_plantuml(diagram, style=args.style, engine=args.engine)
        write_text(output_file, content)
        print(f"Generated {output_file}")
    return 0


def command_render(args: argparse.Namespace) -> int:
    diagrams = validate_definition(load_json(args.input))
    if PLANTUML_JAR is None or not PLANTUML_JAR.exists():
        raise DefinitionError(
            f"plantuml.jar not found at {PLANTUML_JAR}. Set it up or run 'generate' instead."
        )
    for diagram in diagrams:
        if diagram["type"] == "use_case_scenario":
            print("Skip render for scenario:", diagram["id"])
            continue
        base_name = args.name or diagram["id"]
        plantuml_file = args.out_dir / f"{base_name}.puml"
        output_file = ensure_valid_output_path(
            args.out_dir / f"{base_name}.{diagram.get('format', 'png')}", diagram.get("format", "png")
        )
        write_text(plantuml_file, generate_plantuml(diagram, style=args.style, engine=args.engine))
        render_file(plantuml_file, output_file, timeout=args.timeout)
        actual_file = expected_output_file(plantuml_file, output_file.suffix[1:])
        if not actual_file.exists():
            raise DefinitionError(f"PlantUML did not create {actual_file}")
        print(f"Rendered {actual_file}")
    return 0


def command_examples(args: argparse.Namespace) -> int:
    definitions_path = Path(__file__).resolve().parent.parent / "definitions" / "exam_diagrams.json"
    diagrams = validate_definition(load_json(definitions_path))
    if args.json:
        print(json.dumps([diagram["id"] for diagram in diagrams], ensure_ascii=False, indent=2))
    else:
        for diagram in diagrams:
            print(f"{diagram['id']}\t{diagram['type']}\t{diagram['title']}")
    return 0


COMMANDS = {
    "validate": command_validate,
    "generate": command_generate,
    "render": command_render,
    "examples": command_examples,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return COMMANDS[args.command](args)
    except DefinitionError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
