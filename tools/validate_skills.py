"""Validate Agent Skills stored in a flat source catalog."""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from urllib.parse import unquote

import yaml

ALLOWED_FRONTMATTER_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$",
)
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
URL_SCHEMES = ("http:", "https:", "mailto:", "tel:", "data:")


def validate_catalog(catalog: Path) -> list[str]:
    """Return all validation errors found in a flat skill catalog."""
    if not catalog.is_dir():
        return [f"Skill catalog does not exist or is not a directory: {catalog}"]

    errors: list[str] = []
    for entry in sorted(catalog.iterdir(), key=lambda item: item.name):
        if entry.name.startswith("."):
            continue
        if not entry.is_dir():
            errors.append(f"{entry}: expected a skill directory")
            continue
        errors.extend(validate_skill(entry))
    return errors


def validate_skill(skill_root: Path) -> list[str]:
    """Return all validation errors for a single skill directory."""
    errors: list[str] = []
    skill_file = skill_root / "SKILL.md"
    if not skill_file.is_file():
        return [f"{skill_root}: missing required SKILL.md"]

    try:
        contents = skill_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{skill_file}: must be UTF-8 encoded"]

    frontmatter, body, frontmatter_errors = split_frontmatter(skill_file, contents)
    errors.extend(frontmatter_errors)
    if frontmatter is not None:
        errors.extend(validate_frontmatter(skill_root, skill_file, frontmatter))
    if body is not None and not body.strip():
        errors.append(f"{skill_file}: Markdown instruction body must not be empty")
    if body is not None:
        errors.extend(validate_relative_links(skill_root, skill_file, body))

    metadata_file = skill_root / "agents" / "openai.yaml"
    if metadata_file.exists():
        errors.extend(validate_openai_metadata(metadata_file))
    return errors


def split_frontmatter(
    skill_file: Path,
    contents: str,
) -> tuple[Mapping[str, object] | None, str | None, list[str]]:
    """Parse YAML frontmatter and retain the Markdown body."""
    if not contents.startswith("---\n"):
        return None, None, [f"{skill_file}: frontmatter must start with ---"]

    closing_marker = contents.find("\n---\n", len("---\n"))
    if closing_marker == -1:
        return None, None, [f"{skill_file}: frontmatter closing --- is missing"]

    yaml_text = contents[len("---\n") : closing_marker]
    body = contents[closing_marker + len("\n---\n") :]
    try:
        parsed = yaml.safe_load(yaml_text)
    except yaml.YAMLError as error:
        return None, body, [f"{skill_file}: invalid YAML frontmatter: {error}"]
    if not isinstance(parsed, Mapping):
        return None, body, [f"{skill_file}: frontmatter must be a YAML mapping"]
    return parsed, body, []


def validate_frontmatter(
    skill_root: Path,
    skill_file: Path,
    frontmatter: Mapping[str, object],
) -> list[str]:
    """Validate the portable Agent Skills frontmatter subset."""
    errors: list[str] = []
    unexpected = sorted(set(frontmatter) - ALLOWED_FRONTMATTER_FIELDS)
    if unexpected:
        errors.append(f"{skill_file}: unsupported frontmatter fields: {', '.join(unexpected)}")

    name = frontmatter.get("name")
    if not isinstance(name, str):
        errors.append(f"{skill_file}: name must be a string")
    else:
        errors.extend(validate_name(skill_root, skill_file, name))

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{skill_file}: description must be a non-empty string")
    elif len(description) > 1024:
        errors.append(f"{skill_file}: description must be at most 1024 characters")

    for field_name in ("license", "compatibility", "allowed-tools"):
        value = frontmatter.get(field_name)
        if value is not None and not isinstance(value, str):
            errors.append(f"{skill_file}: {field_name} must be a string when provided")

    compatibility = frontmatter.get("compatibility")
    if isinstance(compatibility, str) and len(compatibility) > 500:
        errors.append(f"{skill_file}: compatibility must be at most 500 characters")

    errors.extend(validate_metadata(skill_file, frontmatter.get("metadata")))
    return errors


def validate_name(skill_root: Path, skill_file: Path, name: str) -> list[str]:
    """Validate that a skill name follows the standard and its directory."""
    errors: list[str] = []
    if not 1 <= len(name) <= 64:
        errors.append(f"{skill_file}: name must be between 1 and 64 characters")
    if not NAME_PATTERN.fullmatch(name):
        errors.append(
            f"{skill_file}: name must use lowercase letters, digits, and single hyphens",
        )
    if name != skill_root.name:
        errors.append(f"{skill_file}: name must match directory {skill_root.name!r}")
    return errors


def validate_metadata(skill_file: Path, metadata: object) -> list[str]:
    """Ensure metadata is a string mapping with a valid skill version."""
    if not isinstance(metadata, Mapping):
        return [f"{skill_file}: metadata must be a mapping"]
    invalid_items = [
        key
        for key, value in metadata.items()
        if not isinstance(key, str) or not isinstance(value, str)
    ]
    if invalid_items:
        return [f"{skill_file}: metadata keys and values must be strings"]

    version = metadata.get("version")
    if version is None:
        return [f"{skill_file}: metadata.version is required"]
    if not SEMVER_PATTERN.fullmatch(version):
        return [f"{skill_file}: metadata.version must be a valid SemVer 2.0 version"]
    return []


def validate_relative_links(skill_root: Path, skill_file: Path, body: str) -> list[str]:
    """Validate local Markdown links without resolving external URLs."""
    errors: list[str] = []
    for raw_target in extract_link_targets(body):
        target = unquote(raw_target).split("#", maxsplit=1)[0]
        if not target or target.startswith(URL_SCHEMES):
            continue
        link_path = Path(target)
        if link_path.is_absolute() or re.match(r"^[A-Za-z]:", target):
            errors.append(f"{skill_file}: link must be relative: {raw_target}")
            continue
        resolved = (skill_root / link_path).resolve()
        try:
            resolved.relative_to(skill_root.resolve())
        except ValueError:
            errors.append(f"{skill_file}: link escapes skill root: {raw_target}")
            continue
        if not resolved.exists():
            errors.append(f"{skill_file}: linked path does not exist: {raw_target}")
    return errors


def extract_link_targets(body: str) -> Iterable[str]:
    """Yield the path component from inline Markdown links."""
    for match in MARKDOWN_LINK_PATTERN.finditer(body):
        target = match.group(1).strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        yield target.split(maxsplit=1)[0]


def validate_openai_metadata(metadata_file: Path) -> list[str]:
    """Check that optional Codex UI metadata is valid YAML mapping."""
    if not metadata_file.is_file():
        return [f"{metadata_file}: openai.yaml must be a file"]
    try:
        parsed = yaml.safe_load(metadata_file.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as error:
        return [f"{metadata_file}: invalid YAML: {error}"]
    if parsed is not None and not isinstance(parsed, Mapping):
        return [f"{metadata_file}: YAML root must be a mapping"]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a flat Agent Skills catalog.")
    parser.add_argument("catalog", nargs="?", default="src/skills", type=Path)
    args = parser.parse_args(argv)

    errors = validate_catalog(args.catalog)
    if errors:
        print("Skill validation failed:", file=sys.stderr)
        print(*[f"- {error}" for error in errors], sep="\n", file=sys.stderr)
        return 1
    print(f"Validated skill catalog: {args.catalog}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
