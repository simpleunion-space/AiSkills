<!-- source-sha256: b23b0ed8c1ea0c240c7ad39afc01b966873a0a13aab43563174e5a75978e5e75 -->

# Repository Guidelines

Before starting work, read the README, `docs/development_EN.md`, the current
rules in `CODESTYLE_EN.md`, and Git status. Skills are product source material
in this repository: store them only in `src/skills/<name>/` and do not create
copies in `.agents/skills` or `.claude/skills`.

Every skill contains an English Agent Skills `SKILL.md` frontmatter file. Its
name must match the directory name and use kebab-case; the required
`metadata.version` string uses complete SemVer 2.0. Use `references/`,
`scripts/`, and `assets/` only for material that cannot fit concisely in the
main file. Links from `SKILL.md` must be relative and point to existing files.

Start with read-only analysis and Docker Compose checks. Preserve a user's
uncommitted work and do not revert it without explicit instruction. For every
changed Russian Markdown document, update its `_EN` counterpart and
`source-sha256`.

Do not deploy or apply, run migrations, delete data, publish artifacts, rewrite
Git history, or make external changes without confirmation. Never store real
secrets in Git; use safe examples and environment variables.

After changing a skill, validator, or document, run the applicable Compose
commands from `docs/development_EN.md`: `verify` checks the repository
contract and `tests` runs it in full. Do not run checks through Python on the
host or document commands that do not exist.
