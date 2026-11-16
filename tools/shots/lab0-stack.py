"""Shoot a stack's page while it is being created (2-1-b and 2-1-c results).

    AWS_PROFILE=demo1 AWS_REGION=ap-northeast-2 CWAN_STACK=seoul \
      CWAN_SHOT=lab0-cfn-04-in-progress-seoul \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/lab0-stack.py

Read-only. CREATE_IN_PROGRESS is what the page's success check asks for, so run
this while the stack is still building.
"""
import os

WHICH = os.environ.get("CWAN_STACK", "seoul")
STACK = f"cloudwan-workshop-{WHICH}"
NAME = os.environ.get("CWAN_SHOT", f"lab0-cfn-in-progress-{WHICH}")
WAIT = 6000


def body(f):
    try:
        return f.locator("body").inner_text()
    except Exception:
        return ""


def heads(f):
    try:
        return [h.strip() for h in f.get_by_role("heading").all_inner_texts() if h.strip()][:16]
    except Exception:
        return []


goto(f"/cloudformation/home?region={REGION}#/stacks?filteringText={STACK}")
page.wait_for_timeout(WAIT)
f = app()
print("STACKS headings:", heads(f))

link = f.get_by_role("link", name=STACK, exact=True)
print("stack links:", link.count())
if link.count():
    link.first.click()
    page.wait_for_timeout(WAIT)
    f = app()

print("DETAIL headings:", heads(f))
txt = body(f)
print("status seen:", [s for s in ("CREATE_IN_PROGRESS", "CREATE_COMPLETE",
                                   "ROLLBACK", "CREATE_FAILED") if s in txt])

for h in ("Overview", "Stack info", STACK, "Events"):
    c = panel(h, frame=f)
    if c is not None:
        shot(NAME, clip=c)
        print(f"shot cropped to {h!r}")
        break
else:
    print("!! no panel matched, keeping the whole window")
    shot(NAME)
