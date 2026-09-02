<!-- source-sha256: 1d865e7f9a28140b4a87a31a73eba16d9edfa35b3d6bf0d7218af809ff59faa2 -->

# Authoring a skill

Create `src/skills/<skill-name>/`, where `<skill-name>` contains only lowercase
Latin letters, digits, and single hyphens. It must contain an English
`SKILL.md` with YAML frontmatter and Markdown instructions.

Required frontmatter fields:

- `name`, exactly matching the directory name;
- `description`, stating the skill's purpose and when to invoke it.
- `metadata.version`, a skill-version string in the complete SemVer 2.0 format.

`metadata` is a required string mapping. Besides `version`, it can contain
optional string metadata such as `author`. The standard optional top-level
fields are `license`, `compatibility`, and `allowed-tools`. Do not add
platform-specific extensions to the common frontmatter. Use `agents/openai.yaml`
inside a skill for Codex UI metadata.

## Skill version

Use a complete SemVer 2.0 string: `MAJOR.MINOR.PATCH`, with prerelease and
build metadata when needed, for example `1.0.0-rc.1+build.42`. A `v` prefix,
whitespace, and leading zeroes in numeric identifiers are not allowed. A new
skill starts at `1.0.0`.

Update the version manually; it is independent from the `ai-skills` package
version in `pyproject.toml`. Increase MAJOR for an incompatible contract
change, MINOR for a new compatible capability, and PATCH for a behavior fix.
Editorial changes that do not change skill behavior need no version increase.

Keep the main file concise. Put detailed reference material in `references/`,
scripts in `scripts/`, and static templates in `assets/`. All links must be
relative to the skill root. Run the skill validator before submitting changes.
