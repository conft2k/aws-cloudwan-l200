#!/bin/bash
# Regenerate workshop diagrams from their generator scripts.
#   build.sh [name ...]          write the draft, check the layout, export SVG + PNG (2x) into docs/images
#   build.sh --check [name ...]  only regenerate into a temp dir and report whether each matches the committed draft
# With no names, every diagram is processed.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
SKILL=${SKILL_DIR:-$HOME/.claude/skills/skill-aws-arch-diagram}/scripts

# name | generator | draft path (relative to docs/images)
TABLE="architecture|architecture.py|architecture.draft.svg
segments|segments.py|diagrams/segments.draft.svg
lab1-global|lab1_global.py|diagrams/lab1-global.draft.svg
lab2-onprem|lab2_onprem.py|diagrams/lab2-onprem.draft.svg
lab3-policy|lab3_policy.py|diagrams/lab3-policy.draft.svg
extra-b-compare|extra_b.py|diagrams/extra-b-compare.draft.svg
cloudwan-components|cloudwan_components.py|diagrams/cloudwan-components.draft.svg"

CHECK=0
if [[ ${1:-} == --check ]]; then CHECK=1; shift; fi
WANT=" $* "

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
rc=0
while IFS='|' read -r name script draft; do
  [[ $# -gt 0 && $WANT != *" $name "* ]] && continue
  dest="$ROOT/docs/images/$draft"
  if (( CHECK )); then
    python3 "$HERE/$script" "$TMP/$name.svg" >/dev/null 2>&1
    if cmp -s "$TMP/$name.svg" "$dest"; then echo "same     $name"; else echo "differs  $name"; rc=1; fi
    continue
  fi
  echo "== $name"
  mkdir -p "$(dirname "$dest")"
  python3 "$HERE/$script" "$dest"
  python3 "$SKILL/check_layout.py" "$dest" || echo "!! check_layout reported the problems above"
  w=$(grep -o 'viewBox="0 0 [0-9.]*' "$dest" | awk '{print $3}')
  w=$(python3 -c "print(round(float('$w') * 2))")
  uv run -q --with python-pptx --with cairosvg python "$SKILL/export.py" "$dest" --svg --png \
    --png-width "$w" --out-dir "$(dirname "$dest")" >/dev/null
  echo "exported $(dirname "$draft")/$(basename "$draft" .draft.svg).{svg,png}"
done <<< "$TABLE"
exit $rc
