<!-- source-sha256: fd1aa8b71f3d4f7801b09bc77fb7a079b5b7c6db4a78be0db18934584877adba -->

# Connecting a skill

`src/skills` is the only source directory. Do not add symlinks or duplicated
platform-specific views to this repository.

For Codex, copy the required skill directory to `.agents/skills/` in the target
repository. For Claude Code, copy the same directory to `.claude/skills/`. For
example, in PowerShell:

```powershell
Copy-Item -Recurse src/skills/example-skill <target>/.agents/skills/
```

Replace the target path with `<target>/.claude/skills/` for Claude Code. After
copying, restart the agent if the current session does not automatically detect
a newly created skill directory.
