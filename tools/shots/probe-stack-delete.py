"""Find out what CloudFormation's stack Delete dialog asks for.

    CWAN_STACK=cwan-ws-probe-delete AWS_PROFILE=demo1 AWS_REGION=ap-northeast-2 \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/probe-stack-delete.py

3-4-d and 3-4-e tell the participant to press Delete and confirm, but the
rehearsal deleted both stacks from the CLI because the Delete button never
resolved by role or name (PLAN 15-6). The cause turned out to be the name:
the button says **Delete stack**. The lesson is the method - when a control
cannot be found, print every button on that screen before reaching for a
cleverer selector. That is what this script is for, and why it stays after
the question it was written for was answered (PLAN 15-10).

It really deletes - point CWAN_STACK at a stack you mean to lose. The dialog
itself is handled by `confirm_dialog()` in tools/console.py, so the console's
confirmation behaviour is described in one place.
"""
import os

STACK = os.environ["CWAN_STACK"]
WAIT = 8000


def buttons(f, label):
    """Every button with its text and the Cloudscape classes, to see what to match on."""
    out = f.evaluate("""() => Array.from(document.querySelectorAll('button, a[role=button]'))
        .map(b => ({t: (b.innerText || '').trim().slice(0, 30),
                    aria: b.getAttribute('aria-label') || '',
                    cls: (b.className || '').toString().slice(0, 90),
                    vis: !!(b.offsetWidth || b.offsetHeight)}))
        .filter(b => b.vis && (b.t || b.aria))""")
    print(f"\n-- {label}: {len(out)} buttons")
    for b in out:
        print("   ", b)
    return out


goto(f"/cloudformation/home?region={REGION}#/stacks/stackinfo?stackId={STACK}")
page.wait_for_timeout(WAIT)
close_tours()
page.wait_for_timeout(2000)

f = app()
print("headings:", [h.strip() for h in f.get_by_role("heading").all_inner_texts() if h.strip()][:10])
buttons(f, "stack detail page")

# Each way of asking for the button, so a future failure shows which ones miss.
tries = [
    ("role+name Delete", lambda: f.get_by_role("button", name="Delete", exact=True)),
    ("text ^Delete$", lambda: f.locator("button").filter(has_text=re.compile(r"^Delete$"))),
    ("text ^Delete stack$", lambda: f.locator("button").filter(
        has_text=re.compile(r"^Delete stack$"))),
    ("awsui class + ^Delete$", lambda: f.locator('button[class*="awsui_button"]').filter(
        has_text=re.compile(r"^Delete$"))),
    ("any button Delete", lambda: f.locator("button", has_text=re.compile(r"Delete"))),
]
btn = None
for name, make in tries:
    loc = make()
    n = loc.count()
    print(f"  {name}: {n}")
    if n and btn is None:
        btn = loc.first
        print(f"  -> using {name!r}")

if btn is None:
    raise SystemExit("!! no Delete control found at all")

btn.click()
if not confirm_dialog(type_name=STACK, probe=True):
    raise SystemExit("!! the dialog opened with no confirm button")
