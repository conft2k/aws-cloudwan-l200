"""Deploy a workshop stack through the console, shooting 2-1 on the way.

    AWS_PROFILE=cwan AWS_REGION=ap-northeast-2 CWAN_STACK=seoul \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/lab0-deploy.py

$CWAN_STACK picks which half to run: `seoul` or `oregon`. Set $AWS_REGION to
match, because the console decides the Region from the URL.

This one is not read-only: it presses Submit, so it really creates the stack.
That is the point. 2-1's screens (upload, parameters, the IAM acknowledgement,
CREATE_IN_PROGRESS) only exist while a stack is being created, and a stack that
already exists cannot show them again - see PLAN.md 14-4.
"""
import os

WHICH = os.environ.get("CWAN_STACK", "seoul")
SEOUL = WHICH == "seoul"
STACK = f"cloudwan-workshop-{WHICH}"
TEMPLATE = str(ROOT / f"docs/assets/cloudwan-workshop-{WHICH}.yaml")
WAIT = 6000

# 2-1-b shoots the whole form; 2-1-c only shows the upload step and the result,
# because the two forms are identical apart from the file and the stack name.
SHOT_UPLOAD = "lab0-cfn-01-upload" if SEOUL else "lab0-cfn-05-upload-oregon"
SHOT_RUNNING = ("lab0-cfn-04-in-progress-seoul" if SEOUL
                else "lab0-cfn-06-in-progress-oregon")


def body(f):
    try:
        return f.locator("body").inner_text()
    except Exception:
        return ""


def click(f, name, exact=True, wait=WAIT):
    b = f.get_by_role("button", name=name, exact=exact)
    if not b.count():
        b = f.get_by_role("link", name=name, exact=exact)
    if not b.count():
        print(f"!! button {name!r} not found; buttons ="
              f" {[t.strip()[:24] for t in f.locator('button').all_inner_texts() if t.strip()][:20]}")
        return False
    b.last.click()
    page.wait_for_timeout(wait)
    return True


goto(f"/cloudformation/home?region={REGION}#/stacks")
page.wait_for_timeout(WAIT)

# --- Create stack -> With new resources (standard) --------------------------
f = app()
if not click(f, "Create stack", exact=False):
    raise SystemExit("no Create stack button")
f = app()
opt = f.get_by_role("menuitem", name="With new resources (standard)")
if not opt.count():
    opt = f.get_by_text("With new resources (standard)")
if opt.count():
    opt.first.click()
    page.wait_for_timeout(WAIT)
else:
    print("!! no 'With new resources (standard)' menu item; maybe already on the form")

# --- upload the template ----------------------------------------------------
f = app()
up = f.get_by_role("radio", name="Upload a template file")
if up.count():
    up.first.evaluate("e => e.click()")
    page.wait_for_timeout(2000)
f = app()
inp = f.locator('input[type=file]')
print("file inputs:", inp.count())
inp.first.set_input_files(TEMPLATE)
page.wait_for_timeout(WAIT)
f = app()
shot(SHOT_UPLOAD)
print("uploaded; body says:", body(f)[:200].replace("\n", " | "))

click(app(), "Next")

# --- stack name and parameters ---------------------------------------------
f = app()
name_in = f.get_by_role("textbox", name="Stack name")
if not name_in.count():
    name_in = f.locator('input[placeholder*="stack name" i], #stackName')
if name_in.count():
    name_in.first.fill(STACK)
    page.wait_for_timeout(1500)
else:
    print("!! stack name box not found")
f = app()
if SEOUL:
    shot("lab0-cfn-02-parameters")
print("PARAMETERS PAGE:", body(f)[:600].replace("\n", " | "))

click(app(), "Next")
page.wait_for_timeout(WAIT)
click(app(), "Next")   # configure stack options -> review

# --- review: the IAM acknowledgement ----------------------------------------
f = app()
txt = body(f)
# 2-1-b step 6 hedges with "if you see the checkbox". Settle that here: print
# whether the review page really asks for the IAM acknowledgement, and write the
# answer into the page instead of the hedge.
print("REVIEW PAGE has ack text:", "acknowledge" in txt.lower())
ack = f.locator('input[type=checkbox]')
checked = 0
for i in range(ack.count()):
    try:
        if not ack.nth(i).is_checked():
            ack.nth(i).evaluate("e => e.click()")
            checked += 1
    except Exception as e:
        print("   ack click failed:", str(e)[:60])
print("acknowledgement boxes ticked:", checked)
page.wait_for_timeout(1500)
f = app()
if SEOUL:
    shot("lab0-cfn-03-ack")

# --- submit -----------------------------------------------------------------
if not click(app(), "Submit", wait=12000):
    click(app(), "Create stack", exact=False, wait=12000)

page.wait_for_timeout(10000)
f = app()
print("AFTER SUBMIT:", body(f)[:400].replace("\n", " | "))
shot(SHOT_RUNNING)
