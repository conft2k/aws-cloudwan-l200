"""Apply shots/retouch.json: cut the rows a shot should not be showing.

Three table shots were taken at the wrong moment. The screens are real, but the
rehearsal had moved on, so the attachment list holds rows that belong to a later
step - a us-west-2 dev attachment from 3-1, an onprem VPN from 2-3, two rows in
Deleting from the teardown. Showing a reader a list that cannot exist at their
step is worse than showing no picture, and these screens cannot be re-shot
without standing the whole lab up again, so the stale rows come out here.

Each row band is a half-open [top, bottom) box in the cropped image, taken so
that it carries the row's content plus the separator line under it. The rows
below slide up and the canvas loses that much height, which is what the console
itself would have drawn with one row fewer.

The row counter in the panel heading goes too, because "(6)" over four rows
contradicts the picture. It is erased, not corrected: the console sets it in
Amazon Ember, a webfont we do not have, so a re-rendered digit would sit beside
real text in the wrong typeface. A heading with no count is how Cloudscape draws
the panel before a count is known, and the rows stay countable by eye.

Coordinates are in the CROPPED image, as crop.py writes it, so re-measure them
if a crop box moves. `size` is the cropped size each entry was measured against;
an image of any other size is left alone rather than cut in the wrong place.

    uv run --with pillow python shots/retouch.py           # report
    uv run --with pillow python shots/retouch.py --apply    # rewrite docs images
"""
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent / "docs"
PLAN = json.loads((HERE / "retouch.json").read_text())


def retouch(im: Image.Image, spec: dict) -> Image.Image:
    """Drop the recorded row bands and white out the recorded boxes."""
    w, h = im.size
    drops = sorted(tuple(b) for b in spec["drop_rows"])
    keep = []
    y = 0
    for top, bottom in drops:
        if y < top:
            keep.append((y, top))
        y = max(y, bottom)
    if y < h:
        keep.append((y, h))
    out = Image.new(im.mode, (w, sum(b - a for a, b in keep)), "white")
    at = 0
    for a, b in keep:
        out.paste(im.crop((0, a, w, b)), (0, at))
        at += b - a
    for box in spec.get("erase", []):
        out.paste("white", tuple(box))
    return out


def main(argv=None) -> None:
    apply = "--apply" in (sys.argv if argv is None else argv)
    for rel, spec in sorted(PLAN.items()):
        dst = DOCS / rel
        if not dst.exists():
            print(f"{rel}: not built yet, skipped")
            continue
        with Image.open(dst) as im:
            if list(im.size) != spec["size"]:
                print(f"{rel}: is {im.size[0]}x{im.size[1]}, expected "
                      f"{spec['size'][0]}x{spec['size'][1]} - already retouched "
                      f"or re-cropped, left alone")
                continue
            out = retouch(im.convert("RGB"), spec)
        rows = len(spec["drop_rows"])
        print(f"{rel}: {spec['size'][0]}x{spec['size'][1]} -> "
              f"{out.size[0]}x{out.size[1]} ({rows} row{'' if rows == 1 else 's'} out)")
        if apply:
            out.save(dst, optimize=True)
    if not apply:
        print("\npass --apply to write them")


if __name__ == "__main__":
    main()
