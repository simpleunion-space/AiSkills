#!/usr/bin/env sh
set -eu

sh tools/scripts/verify.sh
python -m tools.validate_skills src/skills
python -m tools.check_translations
python -m pytest -p no:cacheprovider
RUFF_CACHE_DIR=/tmp/ruff-cache ruff check .
RUFF_CACHE_DIR=/tmp/ruff-cache ruff format --check .

shell_files=$(find tools -type f -name '*.sh' -print)
if [ -n "$shell_files" ]; then
    printf '%s\n' "$shell_files" | xargs shellcheck -x
fi

yaml_files=$(find tools src -type f \( -name '*.yaml' -o -name '*.yml' \) -print)
if [ -n "$yaml_files" ]; then
    printf '%s\n' "$yaml_files" | xargs yamllint -c .yamllint
fi
