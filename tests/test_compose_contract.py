from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
REQUIRED_DIRECTORIES = (
    "docs",
    "src",
    "tests",
    "tools",
    "tools/scripts",
    "tools/docker",
)
REQUIRED_FILES = (
    ".dockerignore",
    ".yamllint",
    "README.md",
    "README_EN.md",
    "AGENTS.md",
    "AGENTS_EN.md",
    "CODESTYLE.md",
    "CODESTYLE_EN.md",
    "tools/scripts/verify.sh",
    "tools/scripts/tests.sh",
    "tools/docker/Dockerfile",
    "tools/docker/verify.yaml",
    "tools/docker/tests.yaml",
)
FORBIDDEN_PATHS = (
    "make",
    "build",
    ".template",
    "tools/scripts/build.sh",
    "tools/docker/build.yaml",
    "tools/docker/compose.yaml",
)


def test_active_compose_contract_is_present() -> None:
    for relative_path in REQUIRED_DIRECTORIES:
        assert (PROJECT_ROOT / relative_path).is_dir(), relative_path
    for relative_path in REQUIRED_FILES:
        assert (PROJECT_ROOT / relative_path).is_file(), relative_path

    dockerfile = (PROJECT_ROOT / "tools/docker/Dockerfile").read_text(encoding="utf-8")
    assert "FROM python:3.12-slim" in dockerfile
    assert "git shellcheck" in dockerfile
    assert 'pip install --no-cache-dir ".[dev]" yamllint' in dockerfile


def test_compose_services_run_read_only_scripts() -> None:
    expected_services = {
        "verify.yaml": ("verify", ["sh", "tools/scripts/verify.sh"]),
        "tests.yaml": ("tests", ["sh", "tools/scripts/tests.sh"]),
    }
    for filename, (service_name, command) in expected_services.items():
        payload = yaml.safe_load((PROJECT_ROOT / "tools/docker" / filename).read_text())
        service = payload["services"][service_name]
        assert service["command"] == command
        assert service["image"] == "ai-skills-checks"
        assert "../..:/workspace:ro" in service["volumes"]
        assert service["build"] == {
            "context": "../..",
            "dockerfile": "tools/docker/Dockerfile",
        }


def test_no_inactive_build_or_workspace_interfaces_exist() -> None:
    for relative_path in FORBIDDEN_PATHS:
        assert not (PROJECT_ROOT / relative_path).exists(), relative_path

    verify_script = (PROJECT_ROOT / "tools/scripts/verify.sh").read_text(encoding="utf-8")
    tests_script = (PROJECT_ROOT / "tools/scripts/tests.sh").read_text(encoding="utf-8")
    assert "git diff --check" in verify_script
    assert "Unresolved template tokens found." in verify_script
    assert "sh tools/scripts/verify.sh" in tests_script
    for command in (
        "python -m tools.validate_skills src/skills",
        "python -m tools.check_translations",
        "python -m pytest",
        "ruff check .",
        "ruff format --check .",
        "shellcheck -x",
        "yamllint -c .yamllint",
    ):
        assert command in tests_script
