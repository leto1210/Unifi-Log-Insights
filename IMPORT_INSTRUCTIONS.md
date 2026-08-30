This repository will import the InsightsPlus documentation into /docs using the automation in .github/scripts/fetch_docs.sh and the workflow .github/workflows/fetch_docs_and_commit.yml.

How to run the import manually:

1. Go to Actions -> Import InsightsPlus Docs -> Run workflow (workflow_dispatch).
2. The action will mirror https://insightsplus.dev/docs, convert HTML pages to Markdown (via pandoc), download assets into docs/assets, and commit the results to the current branch.

After the docs are merged to the default branch (main/master), the Sync docs to wiki workflow will push the /docs contents to the repository wiki. To enable wiki pushes, create a repository secret named WIKI_PAT containing a Personal Access Token with repo permissions.

Attribution: All content is copied from https://insightsplus.dev/docs — original author credited.
