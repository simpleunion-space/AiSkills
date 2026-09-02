# SimpleUnion repo-template reference

## Source and revision

Use only this catalog URL:

```text
https://github.com/simpleunion-space/repo-templates.git
```

For `create-repository` version `1.0.0`, use only this source lock:

```text
tag: v1.0.0
commit: d97248c4002a39e97f06d09be8a636da571d2c13
```

Clone with `--branch v1.0.0 --single-branch`, explicitly check out detached
`refs/tags/v1.0.0`, and obtain `git -C <clone-directory> rev-parse HEAD`. The
result must equal the locked commit before invoking a generator. Do not use a
branch, another tag, a local checkout, or another URL as a fallback.

The generated directory is a file tree, not a Git repository. Do not add
`git init`, a remote, a commit, or a publication step.

## Profiles

| Profile | Use it for |
| --- | --- |
| `base` | A neutral repository foundation without a language-specific stack. |
| `net` | A .NET library with its standard project and test layout. |
| `net-consoleapp` | A .NET library and console application. |
| `net-webapp` | A .NET library and Razor Pages web application with `/health`. |
| `net-desktopapp` | A .NET library and cross-platform Avalonia desktop application. |
| `python` | A Python project with a `src` layout, pytest, and Ruff. |
| `unity` | A Unity project with C# and edit-mode test foundations. |
| `iac-base` | A tool-neutral infrastructure-as-code repository. |
| `ansible` | An Ansible automation repository. |
| `salt` | A Salt automation repository. |

When the user has not selected a profile, propose the closest one and wait for
confirmation instead of generating immediately.

The application profiles inherit the `net` profile. Every `net*` generated
project includes `src/<Name>.Core`, `tests/<Name>.Core`, and
`build/<Name>.Core`. Each application profile additionally includes matching
components in the same three locations:

| Profile | Additional components |
| --- | --- |
| `net-consoleapp` | `src/<Name>.ConsoleApp`, `tests/<Name>.ConsoleApp`, `build/<Name>.ConsoleApp` |
| `net-webapp` | `src/<Name>.WebApp`, `tests/<Name>.WebApp`, `build/<Name>.WebApp` |
| `net-desktopapp` | `src/<Name>.DesktopApp`, `tests/<Name>.DesktopApp`, `build/<Name>.DesktopApp` |

The current base-template contract also includes `tools/scripts/verify-template.sh`.
This is part of the generated repository; this skill does not run it as part
of creation.

## Official generators

Run a generator from the temporary clone only after the profile, project name,
and absolute destination have been confirmed.

| Platform | Prerequisites | Command form |
| --- | --- | --- |
| Windows | Git and PowerShell 7 or later | `pwsh -NoProfile -File make/New-RepositoryFromTemplate.ps1 -Profile <profile> -Name <name> -Destination <directory>` |
| Linux or macOS | Git, Bash, and Python 3 | `bash make/New-RepositoryFromTemplate.sh --profile <profile> --name <name> --destination <directory>` |

The project-name contract is `^[A-Za-z][A-Za-z0-9._-]*$`. The destination
must not exist, or must be empty. Reject a nonempty directory without changing
or clearing it.

## Optional version parameters

Pass these values only when the user explicitly asks for them. Omitting a
parameter keeps the generator's own default.

| User value | PowerShell parameter | Bash parameter | Generator default |
| --- | --- | --- | --- |
| .NET SDK version | `-DotnetSdkVersion <version>` | `--dotnet-sdk-version <version>` | `10.0.302` |
| Target framework | `-TargetFramework <tfm>` | `--target-framework <tfm>` | `net10.0` |
| Python version | `-PythonVersion <version>` | `--python-version <version>` | `3.12` |
| Unity version | `-UnityVersion <version>` | `--unity-version <version>` | `6000.3.17f1` |

Only send a relevant override: use .NET values for any `net*` profile,
`PythonVersion` for `python`, and `UnityVersion` for `unity`. Do not infer a
version merely because it appears in an existing project or a common default.

## Safety boundaries

- Confirm the profile, project name, and destination before cloning or writing.
- Use a unique temporary clone outside the destination and remove only that
  temporary clone after the attempt.
- If cloning fails or the source lock does not match, do not create the
  destination. If the generator fails, do not delete its partial destination
  output.
- Do not run Docker checks, `git init`, commits, remote setup, deploy, apply,
  or publication commands as part of generation.
