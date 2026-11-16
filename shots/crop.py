"""Re-apply shots/crops.json: crop shots/raw/<path> into docs/images/<path>.

Shots listed in shots/retouch.json then have their stale table rows cut out, so
one run of this reproduces every image the pages use.

Run from anywhere: uv run --with pillow python shots/crop.py
"""
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent / "docs"

sys.path.insert(0, str(HERE))
import retouch  # noqa: E402  (needs HERE on the path first)

for rel, box in json.loads((HERE / "crops.json").read_text()).items():
    src = HERE / "raw" / Path(rel).relative_to("images")
    dst = DOCS / rel
    with Image.open(src) as im:
        out = im.crop(tuple(box))
        out.save(dst, optimize=True)
    print(f"{rel}: {box} -> {out.size[0]}x{out.size[1]}")

print()
retouch.main(["--apply"])
