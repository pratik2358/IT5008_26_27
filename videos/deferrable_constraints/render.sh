#!/usr/bin/env bash
# Renders every scene in scene.py and concatenates them into a single
# video, then copies the result (and a thumbnail) into docs/videos/ so
# the site can serve it.
#
# Usage: ./render.sh [quality]
#   quality: manim quality flag, one of l (480p15), m (720p30, default),
#            h (1080p60), p (1440p60), k (2160p60)

set -euo pipefail

QUALITY="${1:-m}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../.." && pwd)"
PYTHON="/Users/pratik/opt/anaconda3/bin/python3"
MANIM="/Users/pratik/opt/anaconda3/bin/manim"

SCENES=(
  S01_Title
  S02_ThreeQualifiers
  S03_TheSetup
  S04_Immediate
  S05_Deferred
  S06_Peek
  S07_Takeaway
)

cd "$DIR"
"$MANIM" -q"$QUALITY" scene.py "${SCENES[@]}"

# Resolve the resolution directory manim used for this quality flag.
case "$QUALITY" in
  l) RES_DIR="480p15" ;;
  m) RES_DIR="720p30" ;;
  h) RES_DIR="1080p60" ;;
  p) RES_DIR="1440p60" ;;
  k) RES_DIR="2160p60" ;;
  *) echo "unknown quality flag: $QUALITY" >&2; exit 1 ;;
esac

OUT_DIR="$DIR/media/videos/scene/$RES_DIR"
LIST_FILE="$(mktemp)"
for s in "${SCENES[@]}"; do
  echo "file '$OUT_DIR/$s.mp4'" >> "$LIST_FILE"
done

FINAL="$DIR/deferrable_constraints.mp4"
ffmpeg -y -f concat -safe 0 -i "$LIST_FILE" -c copy "$FINAL"
rm -f "$LIST_FILE"

echo "Rendered: $FINAL"

# Copy into the site's video directory.
SITE_DIR="$REPO_ROOT/docs/videos"
mkdir -p "$SITE_DIR/thumbs"
cp "$FINAL" "$SITE_DIR/tut_02_deferrable_constraints.mp4"

# Grab a thumbnail from the deferred-transaction scene.
ffmpeg -y -ss 00:00:50 -i "$FINAL" -frames:v 1 -vf "scale=480:-1" \
  "$SITE_DIR/thumbs/tut_02_deferrable_constraints.png"

echo "Copied video + thumbnail into $SITE_DIR"
