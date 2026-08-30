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
  echo "Contents of $TMPDIR:"
  ls -la "$TMPDIR"
  exit 1
fi

echo "Found mirrored site at: $SRC_DIR"

# Try to find the docs subdirectory
SRC_DOCS="$SRC_DIR/docs"
if [ ! -d "$SRC_DOCS" ]; then
  echo "No docs/ subdirectory, using domain root"
  SRC_DOCS="$SRC_DIR"
fi

echo "Looking for HTML files in: $SRC_DOCS"
HTML_COUNT=$(find "$SRC_DOCS" -type f -name '*.html' | wc -l)
echo "Found $HTML_COUNT HTML files"

if [ "$HTML_COUNT" -eq 0 ]; then
  echo "Error: No HTML files found in $SRC_DOCS"
  echo "Directory structure:"
  find "$SRC_DOCS" -type f | head -20
  exit 1
fi

# Convert HTML files to markdown using pandoc
CONVERSION_FAILED=0
find "$SRC_DOCS" -type f -name '*.html' | while read -r html; do
  rel=$(realpath --relative-to="$SRC_DOCS" "$html")
  md="$OUTDIR/${rel%.html}.md"
  mkdir -p "$(dirname "$md")"
  echo "Converting $html -> $md"
  if ! pandoc -f html -t gfm --wrap=preserve "$html" -o "$md" 2>&1; then
    echo "ERROR: pandoc failed for $html"
    exit 1
  fi
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
if [ $? -ne 0 ]; then
  exit 1
fi

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
