#!/usr/bin/env bash
set -uo pipefail  # Remove 'e' - we'll handle errors explicitly

BASE_URL="${BASE_URL:-https://insightsplus.dev/docs}"
TMPDIR=$(mktemp -d)
OUTDIR="$PWD/docs"
ASSET_DIR="$OUTDIR/assets"
mkdir -p "$TMPDIR" "$OUTDIR" "$ASSET_DIR"

echo "Mirroring $BASE_URL"
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --restrict-file-names=windows --domains insightsplus.dev "$BASE_URL" -P "$TMPDIR" 2>&1 | tail -5

# Find the mirrored domain directory
SRC_DIR=$(find "$TMPDIR" -maxdepth 3 -type d -name "insightsplus.dev" 2>/dev/null | head -n1)
if [ -z "$SRC_DIR" ]; then
  echo "ERROR: Could not find mirrored site directory" >&2
  exit 1
fi
echo "Found mirrored site at: $SRC_DIR"

# Locate HTML files (try docs subdirectory first, then domain root)
SRC_DOCS="$SRC_DIR/docs"
[ -d "$SRC_DOCS" ] || SRC_DOCS="$SRC_DIR"
echo "Converting HTML files from: $SRC_DOCS"

# Convert HTML files using pandoc
MD_COUNT=0
find "$SRC_DOCS" -type f -name '*.html' -print0 2>/dev/null | while IFS= read -r -d '' html; do
  rel=$(realpath --relative-to="$SRC_DOCS" "$html" 2>/dev/null || basename "$html")
  md="$OUTDIR/${rel%.html}.md"
  mkdir -p "$(dirname "$md")"
  
  if pandoc -f html -t gfm --wrap=preserve "$html" -o "$md" 2>/dev/null; then
    # Add attribution frontmatter
    {
      echo "---"
      echo "original_url: ${BASE_URL%/}/${rel}"
      echo "original_source: insightsplus.dev"
      echo "attribution: \"Copied from https://insightsplus.dev/docs — original author credited\""
      echo "---"
      echo ""
      cat "$md"
    } > "$md.tmp" && mv "$md.tmp" "$md"
    ((MD_COUNT++))
  fi
done
echo "✓ Converted $MD_COUNT markdown files"

# Copy image assets
find "$SRC_DOCS" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.gif' -o -iname '*.svg' \) -print0 2>/dev/null | while IFS= read -r -d '' img; do
  rel=$(realpath --relative-to="$SRC_DOCS" "$img" 2>/dev/null || basename "$img")
  dest="$ASSET_DIR/$rel"
  mkdir -p "$(dirname "$dest")"
  cp "$img" "$dest" 2>/dev/null || true
done
echo "✓ Assets copied to $ASSET_DIR"

# Commit and push
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
git add docs || true

if git diff --cached --quiet; then
  echo "✓ No docs changes to commit"
else
  git commit -m "Automated import of InsightsPlus docs from $BASE_URL"
  git push origin HEAD || echo "Warning: Push failed (may already be up-to-date)"
fi

echo "✓ Import complete!"
