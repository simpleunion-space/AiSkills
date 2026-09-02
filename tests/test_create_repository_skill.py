import json
from pathlib import Path

import yaml

from tools.validate_skills import validate_catalog

PROJECT_ROOT = Path(__file__).parent.parent
SKILL_ROOT = PROJECT_ROOT / "src" / "skills" / "create-repository"
EVALS_PATH = SKILL_ROOT / "evals" / "evals.json"
SOURCE_URL = "https://github.com/simpleunion-space/repo-templates.git"
SOURCE_TAG = "v1.0.0"
SOURCE_COMMIT = "d97248c4002a39e97f06d09be8a636da571d2c13"


def test_create_repository_skill_validates() -> None:
    assert validate_catalog(PROJECT_ROOT / "src" / "skills") == []


def test_create_repository_skill_has_initial_version() -> None:
    frontmatter = (
        SKILL_ROOT.joinpath("SKILL.md").read_text(encoding="utf-8").split("---", maxsplit=2)[1]
    )
    assert yaml.safe_load(frontmatter)["metadata"]["version"] == "1.0.0"


def test_create_repository_skill_uses_only_the_pinned_https_source() -> None:
    contents = "\n".join(
        (
            SKILL_ROOT.joinpath("SKILL.md").read_text(encoding="utf-8"),
            SKILL_ROOT.joinpath("references", "repo-template.md").read_text(encoding="utf-8"),
        ),
    )

    assert SOURCE_URL in contents
    assert SOURCE_TAG in contents
    assert SOURCE_COMMIT in contents
    assert "--branch v1.0.0 --single-branch" in contents
    assert "refs/tags/v1.0.0" in contents
    assert "default branch" not in contents
    assert "git@github.com:" not in contents


def test_create_repository_evals_cover_profiles_platforms_and_refusals() -> None:
    payload = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    evals = payload["evals"]

    assert payload["skill_name"] == "create-repository"
    assert [evaluation["id"] for evaluation in evals] == list(range(1, 25))
    assert all(evaluation["files"] == [] for evaluation in evals)

    profile_ids = {
        "base": (1, 2),
        "net": (3, 4),
        "python": (5, 6),
        "unity": (7, 8),
        "iac-base": (9, 10),
        "ansible": (11, 12),
        "salt": (13, 14),
        "net-consoleapp": (18, 19),
        "net-webapp": (20, 21),
        "net-desktopapp": (22, 23),
    }
    for profile, ids in profile_ids.items():
        for evaluation_id in ids:
            prompt = evals[evaluation_id - 1]["prompt"].lower()
            assert profile in prompt

    windows_ids = (1, 3, 5, 7, 9, 11, 13, 18, 20, 22)
    assert all("Windows" in evals[evaluation_id - 1]["prompt"] for evaluation_id in windows_ids)
    posix_ids = (2, 4, 6, 8, 10, 12, 14, 19, 21, 23)
    assert all(
        "Linux" in evals[evaluation_id - 1]["prompt"]
        or "macOS" in evals[evaluation_id - 1]["prompt"]
        for evaluation_id in posix_ids
    )

    successful_ids = (*range(1, 15), *range(18, 24))
    for evaluation_id in successful_ids:
        expectations = " ".join(evals[evaluation_id - 1]["expectations"])
        assert SOURCE_URL in expectations
        assert SOURCE_TAG in expectations
        assert SOURCE_COMMIT in expectations
        assert "git init" in expectations.lower()

    assert any("nonempty" in item.lower() for item in evals[14]["expectations"])
    assert "violates the generator contract" in evals[15]["expected_output"]
    assert "clone-stage failure" in evals[16]["expected_output"]
    assert "source-lock" in evals[23]["expected_output"].lower()
