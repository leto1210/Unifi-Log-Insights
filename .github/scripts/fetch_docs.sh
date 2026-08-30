#!/usr/bin/env bash
set -uo pipefail

BASE_URL="${BASE_URL:-https://insightsplus.dev/docs}"
TMPDIR=$(mktemp -d)
OUTDIR="$PWD/docs"
ASSET_DIR="$OUTDIR/assets"
mkdir -p "$TMPDIR" "$OUTDIR" "$ASSET_DIR"

echo "Mirroring $BASE_URL"
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --restrict-file-names=windows --domains insightsplus.dev "$BASE_URL" -P "$TMPDIR" >/dev/null 2>&1

# Find the mirrored domain directory
SRC_DIR=$(find "$TMPDIR" -maxdepth 3 -type d -name "insightsplus.dev" 2>/dev/null | head -n1)
if [ -z "$SRC_DIR" ]; then
  echo "ERROR: Could not find mirrored site directory" >&2
  exit 1
fi
echo "Found mirrored site at: $SRC_DIR"

# Locate HTML files
SRC_DOCS="$SRC_DIR/docs"
[ -d "$SRC_DOCS" ] || SRC_DOCS="$SRC_DIR"
echo "Source directory: $SRC_DOCS"

# Create conversion script
CONVERT_SCRIPT=$(mktemp)
cat > "$CONVERT_SCRIPT" <<'CONVERT_EOF'
#!/bin/bash
html="$1"
SRC_DOCS="$2"
OUTDIR="$3"
BASE_URL="$4"

rel=$(realpath --relative-to="$SRC_DOCS" "$html" 2>/dev/null || basename "$html")
md="$OUTDIR/${rel%.html}.md"
mkdir -p "$(dirname "$md")"

echo "Converting: $rel"
if pandoc -f html -t gfm --wrap=preserve "$html" -o "$md"; then
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
else
  echo "ERROR: Failed to convert $html" >&2
fi
CONVERT_EOF
chmod +x "$CONVERT_SCRIPT"

# Convert HTML files using pandoc
echo "Converting HTML to Markdown..."
find "$SRC_DOCS" -type f -name '*.html' 2>/dev/null -exec "$CONVERT_SCRIPT" {} "$SRC_DOCS" "$OUTDIR" "$BASE_URL" \;

# Copy image assets
find "$SRC_DOCS" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.gif' -o -iname '*.svg' \) 2>/dev/null -exec bash -c 'img="$1"; SRC_DOCS="$2"; ASSET_DIR="$3"; rel=$(realpath --relative-to="$SRC_DOCS" "$img" 2>/dev/null || basename "$img"); dest="$ASSET_DIR/$rel"; mkdir -p "$(dirname "$dest")"; cp "$img" "$dest" 2>/dev/null' _ {} "$SRC_DOCS" "$ASSET_DIR" \;

# Cleanup
rm -f "$CONVERT_SCRIPT"

# Commit and push
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
git add docs || true

if git diff --cached --quiet; then
  echo "No changes to commit"
else
  git commit -m "Automated import of InsightsPlus docs from $BASE_URL"
  git push origin HEAD
fi

echo "Done!"
