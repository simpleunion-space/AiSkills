<!-- source-sha256: 8ddbc4ed9925f092c4ae273733012144ce0fef085dd42d8ac6f896418c716ab5 -->

# Development

All checks run through Docker Compose on Windows, Linux, and macOS. The
container includes Python 3.12, project dependencies, and linters; do not run
checks through Python on the host.

| Action | Command | Side effects |
| --- | --- | --- |
| Verify | `docker compose -f tools/docker/verify.yaml run --rm verify` | Local Docker image and cache; source is available read-only |
| Test | `docker compose -f tools/docker/tests.yaml run --rm tests` | Local Docker image and cache; runs verify, validators, tests, and linters |

`verify` checks the active repository contract and Git diff whitespace. `tests`
first runs `verify`, then validates skills and translations and runs pytest,
Ruff, ShellCheck, and yamllint. No secrets are required. If a future skill
calls an external service, document its environment variables and safe rollback
in that skill.
