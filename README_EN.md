<!-- source-sha256: e2b291259e93e6ce2da6a5cf5be0f1e1d4e58e77bfbde4df5e4634164ae1f8d1 -->

# AiSkills

This repository contains portable skills for AI agents. The canonical skill
sources live in `src/skills`; they follow the Agent Skills standard and can be
connected to Codex and Claude Code without duplicating content.

## Structure

- `src/skills` contains completed skills.
- `src/templates` contains templates and reference material for skill authors.
- `tools` contains local structure and translation validators.
- `tools/scripts` contains verification scripts run inside containers.
- `tools/docker` contains Docker Compose entry points for checks.
- `tests` contains automated checks and fixtures.
- `docs` contains detailed documentation.

## Checks

All checks require Docker Engine with Docker Compose. The container includes
Python 3.12 and the development dependencies, so checks do not need to run
through Python on the host.

Use the same commands on Windows, Linux, and macOS:

```powershell
docker compose -f tools/docker/verify.yaml run --rm verify
docker compose -f tools/docker/tests.yaml run --rm tests
```

The first run builds a local image and Docker cache; containers mount the
source tree read-only.

## Connecting a skill

Copy the required `src/skills/<skill-name>` directory to `.agents/skills/` in a
working repository for Codex, or to `.claude/skills/` for Claude Code. See the
[installation guide](docs/installation_EN.md) for details.

Russian documentation is the source of truth. Whenever it changes, update its
English `_EN` counterpart in the same task.
