"""2-1-a: where the Region and the language are set.

    AWS_PROFILE=demo1 AWS_REGION=ap-northeast-2 \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/lab0-login.py

The page used to hedge - "the bottom of the console (or the settings menu at
the top right)" - so this finds out which it is. Answer: the gear in the top
navigation. The footer has no language item any more; its links are Privacy,
Terms and the service shortcuts only, which this prints to show its work.

The settings popover is a Cloudscape dropdown, not a container with a heading,
so panel() cannot find it. The crop is the union of the Region selector, the
gear and the popover's own text, which puts step 2 (Region) and step 3
(language) of 2-1-a in one picture. Read-only: it opens the popover and
changes nothing.
"""
WAIT = 6000


def body(f):
    try:
        return f.locator("body").inner_text()
    except Exception:
        return ""


goto(f"/console/home?region={REGION}")
page.wait_for_timeout(WAIT)

f = app()
print("footer links:", [t.strip() for t in
                        f.get_by_role("link").all_inner_texts() if t.strip()][-12:])

# The Region selector is a BUTTON with role=combobox, so get_by_role("button") misses it.
region_btn = page.locator('button[aria-label*="Regions"]')
print("region selector candidates:", region_btn.count(),
      "| label:", region_btn.first.get_attribute("aria-label") if region_btn.count() else "-")

gear = page.locator('button[aria-label="Settings"], [data-testid="awsc-nav-settings"] button')
print("gear candidates:", gear.count())
if not gear.count():
    raise SystemExit("!! no settings gear in the top navigation")
gear.first.click()
page.wait_for_timeout(3000)

g = app()
txt = body(g)
for word in ("Language", "Visual mode", "See all user settings"):
    print(f"  settings mentions {word!r}:", word in txt)

# The popover's own text marks its extent; the Region selector sits to its right.
anchors = [page.get_by_text("Current user settings", exact=True),
           page.get_by_text("See all user settings", exact=True),
           gear.first]
if region_btn.count():
    anchors.append(region_btn.first)
have = [a for a in anchors if a.count()]
print("clip anchors:", len(have), "of", len(anchors))
box = span(*have, margin=20)
print("clip box:", box)
shot("lab0-login-01-region-language", clip=box)

page.keyboard.press("Escape")
