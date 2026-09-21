# Browser Extension — Removed from `main`

The Chrome/Firefox extension that shipped alongside earlier versions of UniFi
Insights Plus is **no longer maintained in this fork**, and its source has been
removed from `main`.

## Where the code lives now

The full source and its history are preserved on the **[`archive/extension`](https://github.com/leto1210/Unifi-Log-Insights/tree/archive/extension)**
branch (the extension directory promoted to the repository root, with all 25
commits of history intact). Nothing was lost — check it out with:

```sh
git fetch origin archive/extension
git switch archive/extension
```

## Status

- No new builds are published from this repo.
- The published extensions remain available under their original publisher
  accounts on the Chrome Web Store and Firefox Add-ons and continue to work
  against a current backend — the API endpoints and the `extension` token
  client type they rely on are still supported.
- Bug reports and pull requests against the extension code will not be actioned.

## For users

If you already have the extension installed, no action is required. If you want
to remove it, uninstall it from your browser's extension manager.

## For maintainers / forks

Anyone who wants to keep the extension alive is free to branch from
`archive/extension` into a standalone repository and publish under their own
store accounts.
