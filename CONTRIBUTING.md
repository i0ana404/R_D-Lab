# Contributing

These rules apply to every change, whether written by a person or by an AI coding agent.

## Workflow

1. Never push to `main`. It is protected by the ruleset `protect-main`; direct pushes are rejected. (R-01)
2. Create a branch named `<type>/<short-description>`, for example `feat/sigma-bruteforce-rule` or `docs/update-risk-register`.
3. Open a pull request into `main`.
4. The code owner (see `.github/CODEOWNERS`) reviews the change before merging. (R-01)
5. Delete the branch after merge.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/): `<type>: <summary>`. (R-04)

| Type | Use for |
|---|---|
| `feat` | New functionality (rules, pipelines, scripts) |
| `fix` | Bug fixes |
| `docs` | Documentation, including the risk register |
| `test` | Tests and log samples |
| `chore` | Repository settings and maintenance |
| `ci` | CI workflows |

## Pull requests

- The description starts with `Addresses: R-xx`, citing every risk ID from [RISK-REGISTER.md](RISK-REGISTER.md) the change works on. (R-04)
- When a control is implemented, the same pull request updates its row in the risk register: status and evidence.
- From Session 4, all CI checks must pass before merge. (R-01, R-03)

## Secrets

- Never commit real credentials, API keys or private keys. (R-02)
- GitHub secret scanning and push protection are enabled on this repository.
- If a secret is committed by mistake, revoke it first, then follow [SECURITY.md](SECURITY.md).

## AI-generated changes

- The AI agent works only on branches and only through pull requests. (R-01)
- The agent does not merge its own pull requests; the owner reviews and merges. (R-01)
- AI-written detection rules ship with positive and negative log samples and tests. (R-03)
