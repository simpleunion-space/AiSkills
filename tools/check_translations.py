"""Ensure Russian Markdown sources have current English counterparts."""

from __future__ import annotations

import hashlib
import re
import sys
from collections.abc import Iterable
from pathlib import Path

ROOT_DOCUMENTS = ("README.md", "AGENTS.md", "CODESTYLE.md")
TRANSLATED_DIRECTORIES = (Path("docs"), Path("src/templates"))
HASH_PATTERN = re.compile(r"^<!-- source-sha256: ([a-f0-9]{64}) -->\r?\n")


def validate_translations(root: Path) -> list[str]:
    """Return errors for missing, unpaired, or stale English Markdown files."""
    source_documents = sorted(iter_source_documents(root))
    errors: list[str] = []
    expected_english: set[Path] = set()

    for source in source_documents:
        english = english_path_for(source)
        expected_english.add(english)
        if not english.is_file():
            errors.append(f"{source}: missing English translation {english.name}")
            continue
        errors.extend(validate_translation_hash(source, english))

    for english in iter_english_documents(root):
        if english not in expected_english:
            source = source_path_for(english)
            errors.append(f"{english}: English translation has no source document {source.name}")
    return errors


def iter_source_documents(root: Path) -> Iterable[Path]:
    """Yield all Russian source documents covered by the repository policy."""
    for filename in ROOT_DOCUMENTS:
        document = root / filename
        if document.is_file():
            yield document
    for relative_directory in TRANSLATED_DIRECTORIES:
        directory = root / relative_directory
        if not directory.is_dir():
            continue
        yield from (
            document for document in directory.rglob("*.md") if not document.name.endswith("_EN.md")
        )


def iter_english_documents(root: Path) -> Iterable[Path]:
    """Yield all English documents that must have a Russian source."""
    for filename in ROOT_DOCUMENTS:
        document = root / filename.replace(".md", "_EN.md")
        if document.is_file():
            yield document
    for relative_directory in TRANSLATED_DIRECTORIES:
        directory = root / relative_directory
        if not directory.is_dir():
            continue
        yield from directory.rglob("*_EN.md")


def english_path_for(source: Path) -> Path:
    """Return the conventional English translation path for a Russian source."""
    return source.with_name(f"{source.stem}_EN.md")


def source_path_for(english: Path) -> Path:
    """Return the Russian source path corresponding to an English document."""
    source_stem = english.stem.removesuffix("_EN")
    return english.with_name(f"{source_stem}.md")


def validate_translation_hash(source: Path, english: Path) -> list[str]:
    """Check that an English document records its source's current SHA-256."""
    try:
        english_contents = english.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{english}: translation must be UTF-8 encoded"]

    match = HASH_PATTERN.match(english_contents)
    if match is None:
        return [f"{english}: missing source-sha256 header"]

    expected_hash = source_hash(source)
    if match.group(1) != expected_hash:
        return [f"{english}: source-sha256 does not match {source.name}"]
    return []


def source_hash(source: Path) -> str:
    """Return the SHA-256 hash of the source file's bytes."""
    return hashlib.sha256(source.read_bytes()).hexdigest()


def main() -> int:
    errors = validate_translations(Path.cwd())
    if errors:
        print("Translation validation failed:", file=sys.stderr)
        print(*[f"- {error}" for error in errors], sep="\n", file=sys.stderr)
        return 1
    print("Validated Russian and English documentation pairs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
