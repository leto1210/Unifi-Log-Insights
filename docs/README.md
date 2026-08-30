# InsightsPlus Documentation Import

This branch contains automation to import the documentation from https://insightsplus.dev/docs into this repository's /docs folder.

The import is automated by a GitHub Actions workflow which mirrors the site, converts HTML pages to Markdown using pandoc, downloads assets (images) into /docs/assets, and commits the resulting files into this branch.

Attribution

> This documentation is copied from https://insightsplus.dev/docs — original project author credited in the original docs. Ensure you keep attribution when publishing.
