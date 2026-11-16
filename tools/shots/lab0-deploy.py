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
import re

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


def heads(f):
    """Panel headings on the page. The CloudFormation console names its panels
    differently from Network Manager, so log them and pin the crops afterwards."""
    try:
        return [h.strip() for h in f.get_by_role("heading").all_inner_texts() if h.strip()][:14]
    except Exception:
        return []


def wait_app(must, tries=8):
    """The console frame that actually holds `must`.

    app() picks the frame with the most text, and on a slow wizard step it can
    still be the console shell - which is how a run ended up looking for the
    form's Submit button among cookie-banner buttons.
    """
    for _ in range(tries):
        f = app()
        if must in body(f):
            return f
        page.wait_for_timeout(3000)
    print(f"!! wait_app: never saw {must!r}")
    return app()


def primary(f=None):
    """Click the wizard's primary button.

    Find it by the class Cloudscape marks it with rather than by name. The last
    step's button is "Submit", but the step navigation also has a button whose
    text is "Create stack" (aria-label "Step 1: Create stack"), and a name
    lookup on a stale frame found neither.
    """
    for _ in range(6):
        g = app()
        b = g.locator('button[class*="awsui_primary-button"]')
        if b.count():
            print("   primary button:", b.last.inner_text().strip())
            b.last.click()
            return True
        page.wait_for_timeout(2500)
    g = app()
    print("!! primary: no primary-variant button;"
          f" buttons = {[x.strip()[:26] for x in g.locator('button').all_inner_texts() if x.strip()][-12:]}")
    return False


def cshot(name, *headings):
    """Shoot cropped to the first of `headings` that is on the page."""
    f = app()
    print(f"   headings for {name}: {heads(f)}")
    for h in headings:
        c = panel(h, frame=f)
        if c is not None:
            shot(name, clip=c)
            return True
    print(f"!! {name}: none of {headings} found, keeping the whole window")
    shot(name)
    return False


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
# Create stack is a dropdown; the documented path is its first item. Clicking
# the button with a loose name match lands somewhere else entirely.
f = app()
opt = f.get_by_role("menuitem", name="With new resources (standard)")
if not opt.count():
    opt = f.get_by_text("With new resources (standard)")
print("menu items:",
      [m.strip() for m in f.get_by_role("menuitem").all_inner_texts() if m.strip()][:8])
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
print("uploaded; body says:", body(f)[:200].replace("\n", " | "))
cshot(SHOT_UPLOAD, "Specify template", "Create stack", "Prepare template")

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
    # "Specify stack details" is the page heading, so cropping to it keeps the
    # whole window. The two panels the step actually reads are these.
    clip = span(card("Provide a stack name", f), card("Parameters", f))
    shot("lab0-cfn-02-parameters", clip=clip)
    print("   parameters clip:", clip)
print("PARAMETERS PAGE:", body(f)[:600].replace("\n", " | "))

click(app(), "Next")
page.wait_for_timeout(WAIT)
click(app(), "Next")   # configure stack options -> review

# --- review: the IAM acknowledgement ----------------------------------------
f = wait_app("acknowledge")
txt = body(f)
# 2-1-b step 6 hedges with "if you see the checkbox". Settle that here: print
# whether the review page really asks for the IAM acknowledgement, and write the
# answer into the page instead of the hedge.
print("REVIEW PAGE has ack text:", "acknowledge" in txt.lower())
# Tick only the acknowledgement. Scope it to the Capabilities panel: ticking
# every checkbox on the page would also flip stack options that are checkboxes,
# and Cloudscape puts the wording in a <span>, not in the <label> text, so
# matching on "I acknowledge" finds nothing.
# Only ever tick inside the Capabilities panel. Falling back to the whole page
# ticked four unrelated stack-option checkboxes on the Oregon review screen,
# which has no Capabilities panel at all because that template makes no IAM
# resources.
cap = card("Capabilities", f)
if cap is None:
    print("no Capabilities panel - this template needs no acknowledgement")
boxes = cap.locator('input[type=checkbox]') if cap is not None else None
print("acknowledgement boxes in Capabilities:", boxes.count() if boxes else 0)
for i in range(boxes.count() if boxes else 0):
    try:
        if not boxes.nth(i).is_checked():
            boxes.nth(i).evaluate("e => e.click()")   # the input is hidden
            page.wait_for_timeout(600)
    except Exception as e:
        print("   ack click failed:", str(e).splitlines()[0][:70])
if boxes:
    print("checked now:", [boxes.nth(i).is_checked() for i in range(boxes.count())])
page.wait_for_timeout(1500)
f = app()
if SEOUL:
    cshot("lab0-cfn-03-ack", "Capabilities and transforms", "Capabilities", "Review")

# --- submit -----------------------------------------------------------------
f = wait_app("acknowledge")
primary()
page.wait_for_timeout(15000)
f = app()
print("AFTER SUBMIT:", body(f)[:400].replace("\n", " | "))
f = wait_app(STACK)
print("STACK PAGE headings:", heads(f))
print("STACK PAGE body:", body(f)[:400].replace("\n", " | "))
cshot(SHOT_RUNNING, "Overview", "Stack info", "Events", "Resources")
