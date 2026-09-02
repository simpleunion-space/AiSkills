<!-- source-sha256: 86aa59b9582f590a8d160ee3e5d3650ce7823ca22fd1410c6b3e6a9a39837a16 -->

# Code Style

Formatting is defined by `.editorconfig` and `pyproject.toml`. Use UTF-8, LF,
a final newline, and space indentation. Markdown documents preserve meaningful
trailing whitespace.

Python code must support Python 3.12, be formatted with Ruff, and pass `ruff
check`. Write shell scripts for POSIX `sh` with `set -eu` and check them with
ShellCheck; check YAML with yamllint. Run the complete suite only through the
`tests` container in `tools/docker/tests.yaml`.

Write `SKILL.md` in concise, imperative English. Move detail to `references/`;
use paths relative to the skill root. Generated, vendor, and third-party
material is not edited by hand.

A behavior change requires tests and both language versions of documentation to
be updated.
