#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-https://insightsplus.dev/docs}"
TMPDIR=$(mktemp -d)
OUTDIR="$PWD/docs"
ASSET_DIR="$OUTDIR/assets"
mkdir -p "$TMPDIR" "$OUTDIR" "$ASSET_DIR"

echo "Mirroring $BASE_URL to $TMPDIR"
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --restrict-file-names=windows --domains insightsplus.dev "$BASE_URL" -P "$TMPDIR" 2>&1 | tail -20

# Find the mirrored domain directory
echo "Searching for mirrored content..."
SRC_DIR=$(find "$TMPDIR" -maxdepth 3 -type d -name "insightsplus.dev" -print 2>/dev/null | head -n1)
if [ -z "$SRC_DIR" ]; then
  echo "ERROR: Could not find mirrored site directory"
  ls -la "$TMPDIR"
  exit 1
fi
echo "✓ Found mirrored site at: $SRC_DIR"

# Locate HTML files
SRC_DOCS="$SRC_DIR/docs"
if [ ! -d "$SRC_DOCS" ]; then
  echo "  No docs/ subdirectory, checking domain root"
  SRC_DOCS="$SRC_DIR"
fi

HTML_COUNT=$(find "$SRC_DOCS" -type f -name '*.html' 2>/dev/null | wc -l || echo 0)
echo "✓ Found $HTML_COUNT HTML files in $SRC_DOCS"

if [ "$HTML_COUNT" -eq 0 ]; then
  echo "ERROR: No HTML files found!"
  echo "Directory contents:"
  find "$SRC_DOCS" -type f | head -20
  exit 1
fi

# Convert HTML files using pandoc
echo "Converting HTML to Markdown..."
find "$SRC_DOCS" -type f -name '*.html' -print0 2>/dev/null | while IFS= read -r -d '' html; do
  rel=$(realpath --relative-to="$SRC_DOCS" "$html" 2>/dev/null || basename "$html")
  md="$OUTDIR/${rel%.html}.md"
  mkdir -p "$(dirname "$md")"
  
  echo "  Converting: $rel"
  if ! pandoc -f html -t gfm --wrap=preserve "$html" -o "$md" 2>/dev/null; then
    echo "    ⚠ Pandoc conversion failed for $html (skipping)"
    rm -f "$md"
    continue
  fi
  
  # Prepend attribution frontmatter
  tmpfile=$(mktemp)
  {
    echo "---"
    echo "original_url: ${BASE_URL%/}/${rel}"
    echo "original_source: insightsplus.dev"
    echo "attribution: \"Copied from https://insightsplus.dev/docs — original author credited\""
    echo "---"
    echo ""
    cat "$md"
  } > "$tmpfile"
  mv "$tmpfile" "$md"
done

# Copy image assets
echo "Copying image assets..."
ASSET_COUNT=$(find "$SRC_DOCS" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.gif' -o -iname '*.svg' \) -print0 2>/dev/null | wc -l || echo 0)
echo "✓ Found $ASSET_COUNT image files"

find "$SRC_DOCS" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.gif' -o -iname '*.svg' \) -print0 2>/dev/null | while IFS= read -r -d '' img; do
  rel=$(realpath --relative-to="$SRC_DOCS" "$img" 2>/dev/null || basename "$img")
  dest="$ASSET_DIR/$rel"
  mkdir -p "$(dirname "$dest")"
  cp "$img" "$dest"
done

# Commit and push changes
echo "Committing changes..."
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

git add docs || true
if git diff --cached --quiet; then
  echo "✓ No docs changes to commit"
else
  echo "✓ Committing docs updates"
  git commit -m "Automated import of InsightsPlus docs from $BASE_URL"
  git push origin HEAD
fi

echo "✓ Import complete!"

