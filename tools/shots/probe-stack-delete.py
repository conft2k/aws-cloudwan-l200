"""Find out what CloudFormation's stack Delete dialog asks for.

    CWAN_STACK=cwan-ws-probe-delete AWS_PROFILE=demo1 AWS_REGION=ap-northeast-2 \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/probe-stack-delete.py

3-4-d and 3-4-e tell the participant to press Delete and confirm, but the
rehearsal deleted both stacks from the CLI because the Delete button never
resolved by role or name (PLAN 15-6). The open question is whether the
confirmation wants a word typed before it enables, which is where a participant
would get stuck. This runs against a throwaway stack, prints every button with
its Cloudscape classes, opens the dialog, prints what is in it, and goes
through with the delete so the whole path is actually walked.

It really deletes - point CWAN_STACK at a stack you mean to lose.
"""
import os

STACK = os.environ["CWAN_STACK"]
WAIT = 8000


def body(f):
    try:
        return f.locator("body").inner_text()
    except Exception:
        return ""


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
        if "Delete" in b["t"] or "Delete" in b["aria"] or "primary-button" in b["cls"]:
            print("   *", b)
    return out


goto(f"/cloudformation/home?region={REGION}#/stacks/stackinfo?stackId={STACK}")
page.wait_for_timeout(WAIT)
close_tours()
page.wait_for_timeout(2000)

f = app()
print("headings:", [h.strip() for h in f.get_by_role("heading").all_inner_texts() if h.strip()][:10])
buttons(f, "stack detail page")

# What the rehearsal tried, and the class-based match PLAN 15-6 predicted would work.
tries = [
    ("role+name", lambda: f.get_by_role("button", name="Delete", exact=True)),
    ("text", lambda: f.locator("button").filter(has_text=re.compile(r"^Delete$"))),
    ("awsui class", lambda: f.locator('button[class*="awsui_button"]').filter(
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
page.wait_for_timeout(3000)

g = app()
dlg = g.get_by_role("dialog")
print("\ndialogs:", dlg.count())
text = dlg.last.inner_text() if dlg.count() else body(g)[:800]
print("dialog text:", " | ".join(t for t in text.split("\n") if t.strip()))

# The question: does it want something typed first?
box = g.locator('[role=dialog] input[type=text], [role=dialog] input:not([type])')
print("text inputs in the dialog:", box.count())
for i in range(box.count()):
    print("   placeholder:", box.nth(i).get_attribute("placeholder"),
          "| aria-label:", box.nth(i).get_attribute("aria-label"))

# The confirm button carries the same words as the one on the page: "Delete stack".
confirm = g.locator('[role=dialog] button').filter(has_text=re.compile(r"^Delete stack$"))
print("confirm buttons:", confirm.count())
if confirm.count():
    def state(when):
        dis = confirm.last.get_attribute("disabled")
        aria = confirm.last.get_attribute("aria-disabled")
        print(f"  confirm enabled {when}:", dis is None and aria != "true")
    state("before typing")
    if box.count():
        box.first.fill(STACK)
        page.wait_for_timeout(1200)
        state("after typing the stack name")
    confirm.last.click()
    page.wait_for_timeout(8000)
    print("after confirm:", " | ".join(t for t in body(app()).split("\n")[:14] if t.strip()))
