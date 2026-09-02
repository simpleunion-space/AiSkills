---
name: create-repository
description: Create a new project directory from the SimpleUnion repo-templates catalog. Use this skill whenever the user asks to bootstrap, scaffold, or generate a repository or project from a SimpleUnion template; mentions base, .NET library, .NET console app, Razor Pages web app, Avalonia desktop app, Python, Unity, IaC, Ansible, or Salt profiles; or requests a new repository starter. Confirm the exact profile, project name, and empty destination before cloning the catalog and invoking its official generator. Do not initialize Git, commit, or publish.
compatibility: Requires Git and network access to clone https://github.com/simpleunion-space/repo-templates.git. On Windows, requires PowerShell 7. On Linux or macOS, requires Bash and Python 3.
metadata:
  version: "1.0.0"
---

# Create a SimpleUnion repository

Create only the project files produced by the official SimpleUnion template
generator. The generator deliberately does not initialize Git, create a remote,
commit, publish artifacts, or run Docker checks; leave those actions for an
explicit later request.

## Gather and confirm the request

Collect the project name, destination directory, requested runtime overrides,
and the user's platform. Resolve a relative destination against the current
working directory and restate the absolute path.

Choose a profile from [the repo-template reference](references/repo-template.md).
If the user did not name one, propose the best match from their project
description. Route a console application to `net-consoleapp`, a Razor Pages web
application to `net-webapp`, and an Avalonia desktop application to
`net-desktopapp`. For an otherwise unspecified .NET project, ask whether the
user needs a library, console, web, or desktop project before confirmation.
Before cloning or creating files, ask the user to confirm all three values:

- profile;
- project name;
- absolute destination directory.

For any `net*` profile, accept `DotnetSdkVersion` and `TargetFramework` only
when the user explicitly requests them. Accept `PythonVersion` only for the
`python` profile and `UnityVersion` only for the `unity` profile, again only
when explicitly requested. Otherwise, omit those parameters so that the
template generator uses its own defaults.

## Validate the target

After confirmation and before cloning, validate all of the following:

- the project name matches `^[A-Za-z][A-Za-z0-9._-]*$`;
- the destination does not exist or is empty; never clear a nonempty directory;
- the destination is not the repository root, a home directory, or the
  temporary clone directory;
- Git is available; on Windows also require PowerShell 7, and on Linux or
  macOS require Bash and Python 3.

If any validation fails, stop before calling the generator. Do not replace it
with a hand-built project structure.

## Generate the project

1. Create a unique temporary directory outside the destination.
2. Clone only `https://github.com/simpleunion-space/repo-templates.git` into
   it with `--branch v1.0.0 --single-branch`. Explicitly check out detached
   `refs/tags/v1.0.0`, then obtain `git -C <clone-directory> rev-parse HEAD`.
   It must equal `d97248c4002a39e97f06d09be8a636da571d2c13`; otherwise stop
   before generation and clean up only the temporary clone.
3. Verify that the applicable official generator exists in the clone's `make`
   directory.
4. On Windows, run
   `make/New-RepositoryFromTemplate.ps1` with `-Profile`, `-Name`, and
   `-Destination`. On Linux or macOS, run
   `make/New-RepositoryFromTemplate.sh` with `--profile`, `--name`, and
   `--destination`. Pass a version override only when the user supplied it.
5. Confirm that the destination now contains generated files. The generator
   performs its own schema and path checks; do not run Docker or modify the
   generated result afterwards.

Always clean up the temporary clone directory, whether cloning or generation
succeeds. If generation fails, leave the destination untouched: it can contain
a partially created project that the user may want to inspect or recover.

## Report the outcome

On success, report the selected profile, absolute destination, template URL,
tag `v1.0.0`, and verified source SHA
`d97248c4002a39e97f06d09be8a636da571d2c13`. List any explicit version
overrides. State clearly that Git was not initialized and no commit, remote, or
publication was made.

On failure, report the stage that failed and whether the destination might
contain partial output. Never delete the destination as error recovery; report
only the cleanup of the temporary clone.
