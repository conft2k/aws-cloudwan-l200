"""Shrink every crop in shots/crops.json to the pixels that carry content.

    uv run --with pillow python shots/trim.py            # report only
    uv run --with pillow python shots/trim.py --apply    # rewrite crops.json
                                                         # and the docs images

A panel crop keeps whatever width the console gave the panel, which is often far
wider than the form inside it, so the useful part ends up small on the page.
This finds the bounding box of everything that differs from the surrounding
background and tightens the box to it, leaving a small margin.

It reads shots/raw/, so it never needs the console. Boxes are absolute
coordinates in the raw screenshot, exactly as shot() recorded them, and stay
that way after trimming - crop.py keeps reproducing the same result.
"""
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent / "docs"
MARGIN = 10          # keep this much background around the content
TOLERANCE = 8        # a channel must differ by more than this to count as content


def ink_mask(im: Image.Image):
    """Per-column and per-row counts of pixels that carry ink.

    "Ink" is anything clearly darker than the near-white the console fills
    panels and pages with. Text, icons, control borders and filled buttons all
    count; the flat background does not.
    """
    g = im.convert("L")
    w, h = g.size
    px = g.load()
    cols = [0] * w
    rows = [0] * h
    for y in range(h):
        for x in range(w):
            if px[x, y] < 232:
                cols[x] += 1
                rows[y] += 1
    return cols, rows


def blocks(counts, floor):
    """Runs of consecutive indexes whose count clears `floor`."""
    out, start = [], None
    for i, c in enumerate(counts):
        if c > floor:
            if start is None:
                start = i
        elif start is not None:
            out.append((start, i - 1))
            start = None
    if start is not None:
        out.append((start, len(counts) - 1))
    return out


def span(counts, floor, thin=4, gap=40):
    """Content span, with the panel's own frame dropped.

    A card's left and right borders are single vertical lines, so they look
    like content in a per-column count - a tall thin spike far from everything
    else. Drop a run that is at most `thin` wide when a gap of at least `gap`
    empty columns separates it from the rest, which is exactly the shape of a
    border standing off the end of a form.
    """
    runs = blocks(counts, floor)
    if not runs:
        return None
    while len(runs) > 1 and runs[0][1] - runs[0][0] + 1 <= thin \
            and runs[1][0] - runs[0][1] > gap:
        runs.pop(0)
    while len(runs) > 1 and runs[-1][1] - runs[-1][0] + 1 <= thin \
            and runs[-1][0] - runs[-2][1] > gap:
        runs.pop()
    return runs[0][0], runs[-1][1]


def content_box(im: Image.Image) -> tuple | None:
    """Bounding box of the content, with a margin and without the panel frame."""
    w, h = im.size
    cols, rows = ink_mask(im)
    cs = span(cols, max(3, h // 60))
    rs = span(rows, max(3, w // 60))
    if cs is None or rs is None:
        return None
    return (max(0, cs[0] - MARGIN), max(0, rs[0] - MARGIN),
            min(w, cs[1] + 1 + MARGIN), min(h, rs[1] + 1 + MARGIN))


def main() -> None:
    apply = "--apply" in sys.argv
    crops_file = HERE / "crops.json"
    crops = json.loads(crops_file.read_text())
    changed = {}
    for rel, box in sorted(crops.items()):
        src = HERE / "raw" / Path(rel).relative_to("images")
        if not src.exists():
            print(f"{rel}: no raw file, skipped")
            continue
        with Image.open(src) as raw:
            region = raw.crop(tuple(box))
            inner = content_box(region)
            if inner is None:
                print(f"{rel}: all background, left alone")
                continue
            new = (box[0] + inner[0], box[1] + inner[1],
                   box[0] + inner[2], box[1] + inner[3])
            was = (box[2] - box[0], box[3] - box[1])
            now = (new[2] - new[0], new[3] - new[1])
            if now == was:
                print(f"{rel}: already tight ({was[0]}x{was[1]})")
                continue
            print(f"{rel}: {was[0]}x{was[1]} -> {now[0]}x{now[1]}")
            changed[rel] = list(new)
            if apply:
                raw.crop(new).save(DOCS / rel, optimize=True)
    if apply and changed:
        crops.update(changed)
        crops_file.write_text(json.dumps(crops, indent=1) + "\n")
        print(f"\nrewrote {len(changed)} boxes in {crops_file.name}")
    elif not apply:
        print(f"\n{len(changed)} would change; pass --apply to write them")


if __name__ == "__main__":
    main()
