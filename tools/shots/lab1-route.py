"""2-2-e: add the two core network routes to the Oregon app route table.

    AWS_PROFILE=demo1 AWS_REGION=us-west-2 CWAN_RTB=rtb-... CWAN_CORE=core-network-... \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/lab1-route.py

Shoots the stack Outputs tab, the Edit routes form and the saved table. Saves
the routes, because the Edit routes form only looks like this before they exist.
If the form resists, the routes can be made with `aws ec2 create-route
--core-network-arn ...` and only the form shot is lost.
"""
import os

RTB = os.environ.get("CWAN_RTB", "")
# edit = walk the Edit routes form and save; view = only shoot the result, for
# when the routes are already there.
PHASE = os.environ.get("CWAN_PHASE", "edit")
STACK = os.environ.get("CWAN_STACK", "cloudwan-workshop-oregon")
DESTS = ["10.0.0.0/8", "172.16.0.0/12"]
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


def cshot(name, *headings):
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


# --- 1. the stack Outputs tab ----------------------------------------------
goto(f"/cloudformation/home?region={REGION}#/stacks?filteringText={STACK}")
page.wait_for_timeout(WAIT)
f = app()
link = f.get_by_role("link", name=STACK, exact=True)
if link.count():
    link.first.click()
    page.wait_for_timeout(WAIT)
f = app()
tb = f.get_by_role("tab", name="Outputs", exact=True)
print("Outputs tab:", tb.count())
if tb.count():
    tb.first.click()
    page.wait_for_timeout(WAIT)
cshot("lab1-route-01-outputs", "Outputs", STACK)

# --- 2. the route table's Edit routes form ----------------------------------
goto(f"/vpcconsole/home?region={REGION}#RouteTables:search={RTB}")
page.wait_for_timeout(WAIT)
f = app()
print("ROUTE TABLE page headings:", heads(f))
rl = f.get_by_role("link", name=RTB, exact=True)
print("route table links:", rl.count())
if rl.count():
    rl.first.click()
    page.wait_for_timeout(WAIT)
f = app()
print("tabs:", [x.strip() for x in f.get_by_role("tab").all_inner_texts() if x.strip()])

eb = f.get_by_role("button", name="Edit routes", exact=True) if PHASE == "edit" else f.locator("nothing")
if not eb.count():
    eb = f.get_by_role("link", name="Edit routes", exact=True)
print("Edit routes buttons:", eb.count())
if eb.count():
    eb.last.click()
    page.wait_for_timeout(WAIT)

f = app()
if PHASE != "edit":
    DESTS = []
else:
    print("EDIT FORM headings:", heads(f))
for i, dest in enumerate(DESTS):
    g = app()
    add = g.get_by_role("button", name="Add route", exact=True)
    if not add.count():
        print("!! no Add route button;",
              [x.strip()[:24] for x in g.locator("button").all_inner_texts() if x.strip()][:18])
        break
    add.first.click()
    page.wait_for_timeout(1500)
    g = app()
    boxes = g.locator('input[placeholder="Destination"], input[aria-label="Destination"]')
    print(f"   destination boxes after add {i}:", boxes.count())
    if boxes.count():
        boxes.last.fill(dest)
        page.wait_for_timeout(800)
    # Target: pick the "Core Network" kind, then the core network itself
    sel = g.locator("button").filter(has_text=re.compile(r"^(Select target type|Choose target)$"))
    if not sel.count():
        sel = g.get_by_role("button", name=re.compile("target", re.I))
    if sel.count():
        sel.last.click()
        page.wait_for_timeout(2000)
        h = app()
        opt = h.get_by_role("option", name=re.compile("Core Network", re.I))
        print("   core network option:", opt.count())
        if opt.count():
            opt.first.click()
            page.wait_for_timeout(2500)
            h = app()
            cn = h.get_by_role("option", name=re.compile("core-network-"))
            if not cn.count():
                sel2 = h.locator("button").filter(has_text=re.compile(r"^(Select core network|Choose)$"))
                if sel2.count():
                    sel2.last.click()
                    page.wait_for_timeout(1800)
                    cn = app().get_by_role("option", name=re.compile("core-network-"))
            print("   core network choices:", cn.count())
            if cn.count():
                cn.first.click()
                page.wait_for_timeout(1500)
        else:
            page.keyboard.press("Escape")
    else:
        print("!! no target selector;",
              [x.strip()[:24] for x in g.locator("button").all_inner_texts() if x.strip()][:18])

if PHASE == "edit":
    cshot("lab1-route-02-edit", "Edit routes", "Routes")
    print("BEFORE SAVE:", body(app())[:600].replace("\n", " | "))

sv = app().get_by_role("button", name="Save changes", exact=True) if PHASE == "edit" else app().locator("nothing")
print("Save changes buttons:", sv.count())
if sv.count():
    sv.last.click()
    page.wait_for_timeout(10000)
    print("AFTER SAVE:", body(app())[:400].replace("\n", " | "))

# --- 3. the saved table -----------------------------------------------------
f = app()
rt = f.get_by_role("tab", name="Routes", exact=True)
if rt.count():
    rt.first.click()
    page.wait_for_timeout(WAIT)
cshot("lab1-route-03-saved", "Routes")
