"""2-1-a: where the Region and the language are set.

    AWS_PROFILE=demo1 AWS_REGION=ap-northeast-2 \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/lab0-login.py

The page hedges - "the bottom of the console (or the settings menu at the top
right)" - so find out which it is, and shoot it. Read-only: it opens the
settings panel and changes nothing.
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

# The unified settings live behind a gear in the top navigation.
gear = page.locator('button[aria-label="Settings"], [data-testid="awsc-nav-settings"] button')
print("gear candidates:", gear.count())
opened = False
if gear.count():
    gear.first.click()
    page.wait_for_timeout(3000)
    opened = True

g = app()
txt = body(g)
for word in ("Language", "Default Region", "Display", "Visual mode"):
    print(f"  settings mentions {word!r}:", word in txt)

print("settings body:", txt[:900].replace("\n", " | "))

for h in ("Settings", "Unified settings", "Language"):
    c = panel(h, frame=g)
    if c is not None:
        shot("lab0-login-01-region-language", clip=c)
        print(f"shot cropped to {h!r}")
        break
else:
    print("!! no settings panel matched, keeping the whole window")
    shot("lab0-login-01-region-language")

if opened:
    page.keyboard.press("Escape")
