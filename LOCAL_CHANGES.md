# Humanizer local overlay

- Upstream: https://github.com/blader/humanizer
- Upstream commit: `0ef9fe5bc3572734fd3ae6c448fe00a30cd5dcf0`
- Upstream version: 3.1.0
- Local revision: 2026-10-29.1

This package starts from the complete upstream checkout. Its local changes retain the existing drafting/invocation instructions and add the two agreed editorial refinements. The upstream plugin manifest correction is included. Examples contain no private correspondence or personal names.

## Updating

Keep upstream history and local changes as separate commits in the maintained repository. Fetch upstream, merge or rebase deliberately, review conflicts, and run the upstream package validator before distributing a reviewed revision. Do not replace this package with a direct upstream install, which would discard the overlay.

Use the same reviewed commit on Windows, WSL, and Clawbox, with a local checkout or installed copy for each environment. Machine-specific paths belong in deployment configuration, not in the skill. Record the installed commit on each host. A universal rollout has not yet been performed.
