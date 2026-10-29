# Humanizer local overlay

- Upstream: https://github.com/blader/humanizer
- Upstream commit: `0ef9fe5bc3572734fd3ae6c448fe00a30cd5dcf0`
- Upstream version: 3.1.0
- Local revision: 2026-10-29.1

This package starts from the complete upstream checkout. Its local changes retain the existing drafting/invocation instructions and add the two agreed editorial refinements. The upstream plugin manifest correction is included. Examples contain no private correspondence or personal names.

## Updating

Keep upstream history and local changes as separate commits in the maintained repository. Fetch upstream, merge or rebase deliberately, review conflicts, and run the upstream package validator before distributing a reviewed revision. Do not replace this package with a direct upstream install, which would discard the overlay.

Use the same reviewed commit on Windows, WSL, and Clawbox, with a local checkout or installed copy for each environment. Machine-specific paths belong in deployment configuration, not in the skill.

## Install and verify

The maintained repository is private: https://github.com/sam2kb/humanizer. Keep the public source as the `upstream` Git remote and the private repository as `origin`.

From a clean checkout of the reviewed commit, run:

```sh
python3 scripts/install-local.py --dest "$HOME/.agents/skills/humanizer" --revision "$(git rev-parse HEAD)"
```

On Windows, use Python and the destination in your profile. Add another `--dest` for each existing agent-specific copy that needs the same revision. Use `--check` to verify installed file hashes without making changes. The installer records the commit in `.humanizer-install.json`, backs up existing directories outside the skill discovery folder, validates the staged package, and rolls back if replacement verification fails.

For a host without repository credentials, an operator can transfer a `git archive` of the reviewed commit and run the included installer with that full commit SHA. Keep credentials and deployment records outside the repository. The installer requires Python 3.9 or newer.
