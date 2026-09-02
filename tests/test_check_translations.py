from pathlib import Path

from tools.check_translations import source_hash, validate_translations


def write_translation_pair(root: Path, source_contents: str, hash_value: str | None = None) -> None:
    source = root / "README.md"
    source.write_text(source_contents, encoding="utf-8")
    recorded_hash = hash_value if hash_value is not None else source_hash(source)
    (root / "README_EN.md").write_text(
        f"<!-- source-sha256: {recorded_hash} -->\n\n# English\n",
        encoding="utf-8",
    )


def test_current_translation_hash_passes(tmp_path: Path) -> None:
    write_translation_pair(tmp_path, "# Русский\n")
    assert validate_translations(tmp_path) == []


def test_stale_translation_hash_fails(tmp_path: Path) -> None:
    write_translation_pair(tmp_path, "# Русский\n", hash_value="0" * 64)
    errors = validate_translations(tmp_path)
    assert any("source-sha256 does not match" in error for error in errors)


def test_missing_translation_fails(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Русский\n", encoding="utf-8")
    errors = validate_translations(tmp_path)
    assert any("missing English translation" in error for error in errors)
