#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-https://insightsplus.dev/docs}"
TMPDIR=$(mktemp -d)
OUTDIR="$PWD/docs"
ASSET_DIR="$OUTDIR/assets"
mkdir -p "$TMPDIR" "$OUTDIR" "$ASSET_DIR"

echo "Mirroring $BASE_URL to $TMPDIR"
# Mirror the docs site
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --restrict-file-names=windows --domains insightsplus.dev "$BASE_URL" -P "$TMPDIR"

# Locate mirrored root
SRC_DIR=$(find "$TMPDIR" -maxdepth 3 -type d -name "insightsplus.dev" -print | head -n1 || true)
if [ -z "$SRC_DIR" ]; then
  echo "Could not find mirrored site under $TMPDIR"
  ls -la "$TMPDIR"
  exit 1
fi

SRC_DOCS="$SRC_DIR/docs"
if [ ! -d "$SRC_DOCS" ]; then
  # sometimes wget places pages directly under the domain root
  SRC_DOCS="$SRC_DIR"
fi

# Convert HTML files to markdown using pandoc
find "$SRC_DOCS" -type f -name '*.html' | while read -r html; do
  rel=$(realpath --relative-to="$SRC_DOCS" "$html")
  md="$OUTDIR/${rel%.html}.md"
  mkdir -p "$(dirname "$md")"
  echo "Converting $html -> $md"
  pandoc -f html -t gfm --wrap=preserve "$html" -o "$md" || { echo "pandoc failed for $html"; exit 1; }
  # Prepend attribution/frontmatter
  tmpfile=$(mktemp)
  echo "---" > "$tmpfile"
  echo "original_url: ${BASE_URL%/}/${rel}" >> "$tmpfile"
  echo "original_source: insightsplus.dev" >> "$tmpfile"
  echo "attribution: \"Copied from https://insightsplus.dev/docs — original author credited\"" >> "$tmpfile"
  echo "---" >> "$tmpfile"
  echo "" >> "$tmpfile"
  cat "$md" >> "$tmpfile"
  mv "$tmpfile" "$md"
done

# Copy image assets
find "$SRC_DOCS" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.gif' -o -iname '*.svg' \) -print0 | while IFS= read -r -d '' img; do
  rel=$(realpath --relative-to="$SRC_DOCS" "$img")
  dest="$ASSET_DIR/$rel"
  mkdir -p "$(dirname "$dest")"
  cp "$img" "$dest"
done

# NOTE: This script does not yet rewrite image links inside Markdown. Pandoc usually embeds relative links to the local images. If links are broken, run a link-fix step.

# Commit changes
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

git add docs || true
if git diff --cached --quiet; then
  echo "No docs changes to commit"
else
  git commit -m "Automated import of InsightsPlus docs from $BASE_URL"
  # Push to the current branch
  git push origin HEAD
fi
