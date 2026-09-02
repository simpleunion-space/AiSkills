from pathlib import Path

import pytest

from tools.validate_skills import validate_catalog, validate_frontmatter

FIXTURES = Path(__file__).parent / "fixtures" / "skills"


def test_valid_skill_catalog_passes() -> None:
    assert validate_catalog(FIXTURES / "valid" / "skills") == []


@pytest.mark.parametrize(
    ("case", "expected_message"),
    [
        ("bad-name", "name must use lowercase letters, digits, and single hyphens"),
        ("missing-description", "description must be a non-empty string"),
        ("invalid-yaml", "invalid YAML frontmatter"),
        ("mismatched-name", "name must match directory"),
        ("broken-link", "linked path does not exist"),
        ("missing-version", "metadata.version is required"),
        ("invalid-version", "metadata.version must be a valid SemVer 2.0 version"),
    ],
)
def test_invalid_skill_catalogs_report_expected_error(case: str, expected_message: str) -> None:
    errors = validate_catalog(FIXTURES / "invalid" / case / "skills")
    assert any(expected_message in error for error in errors)


def test_missing_catalog_is_reported(tmp_path: Path) -> None:
    errors = validate_catalog(tmp_path / "missing")
    assert errors == [f"Skill catalog does not exist or is not a directory: {tmp_path / 'missing'}"]


@pytest.mark.parametrize(
    "version",
    [
        "0.0.0",
        "1.0.0",
        "12.34.56-rc.1",
        "2.4.6-alpha-1+build.9",
        "3.2.1-0+001",
    ],
)
def test_semver_versions_are_accepted(version: str, tmp_path: Path) -> None:
    errors = validate_frontmatter(
        tmp_path / "versioned-skill",
        tmp_path / "versioned-skill" / "SKILL.md",
        {
            "name": "versioned-skill",
            "description": "Validate the accepted SemVer 2.0 forms.",
            "metadata": {"version": version, "author": "example-org"},
        },
    )
    assert errors == []


@pytest.mark.parametrize(
    "metadata, expected_message",
    [
        (None, "metadata must be a mapping"),
        ({}, "metadata.version is required"),
        ({"version": 1}, "metadata keys and values must be strings"),
        ({"version": "01.0.0"}, "metadata.version must be a valid SemVer 2.0 version"),
        ({"version": "1.0.0-01"}, "metadata.version must be a valid SemVer 2.0 version"),
        ({"version": "v1.0.0"}, "metadata.version must be a valid SemVer 2.0 version"),
        ({"version": "1.0.0 "}, "metadata.version must be a valid SemVer 2.0 version"),
        ({"version": "١.0.0"}, "metadata.version must be a valid SemVer 2.0 version"),
    ],
)
def test_invalid_semver_metadata_is_rejected(
    metadata: object,
    expected_message: str,
    tmp_path: Path,
) -> None:
    errors = validate_frontmatter(
        tmp_path / "versioned-skill",
        tmp_path / "versioned-skill" / "SKILL.md",
        {
            "name": "versioned-skill",
            "description": "Validate invalid SemVer 2.0 forms.",
            "metadata": metadata,
        },
    )
    assert any(expected_message in error for error in errors)


def test_top_level_version_is_not_a_supported_frontmatter_field(tmp_path: Path) -> None:
    errors = validate_frontmatter(
        tmp_path / "versioned-skill",
        tmp_path / "versioned-skill" / "SKILL.md",
        {
            "name": "versioned-skill",
            "description": "Reject a nonportable top-level version field.",
            "version": "1.0.0",
            "metadata": {"version": "1.0.0"},
        },
    )
    assert any("unsupported frontmatter fields: version" in error for error in errors)
