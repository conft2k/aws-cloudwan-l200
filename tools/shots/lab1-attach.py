"""2-2-d: make the Oregon prod VPC attachment, shooting the form on the way.

    AWS_PROFILE=demo1 CWAN_VPC=vpc-... CWAN_SUBNETS=subnet-a,subnet-b \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/lab1-attach.py

The form screens only exist while an attachment is being made, and the
attachment is made once (PLAN.md 14-4), so this both shoots and submits.

It prints every control it finds before touching it. The selectors here are
guesses until a run confirms them; read the log, not the code, to see what the
form actually offers.
"""
import os

VPC = os.environ.get("CWAN_VPC", "")
SUBNETS = [s for s in os.environ.get("CWAN_SUBNETS", "").split(",") if s]
EDGE = os.environ.get("CWAN_EDGE", "us-west-2")
ATT_NAME = os.environ.get("CWAN_ATT_NAME", "cwan-ws-att-prod-usw2")
SEGMENT = os.environ.get("CWAN_SEGMENT", "prod")
NETWORKS = ("https://us-west-2.console.aws.amazon.com"
            "/networkmanager/home?region=us-west-2#/networks")
WAIT = 8000


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


def controls(f):
    return f.evaluate("""() => [...document.querySelectorAll(
        'input, select, textarea, button[aria-haspopup], [role=combobox], [role=radio]')]
      .filter(e => { const b = e.getBoundingClientRect(); return b.width || b.height; })
      .map(e => ({tag: e.tagName, type: e.getAttribute('type'), role: e.getAttribute('role'),
                  ph: e.getAttribute('placeholder'), label: e.getAttribute('aria-label'),
                  text: (e.innerText || '').trim().slice(0, 36)}))
      .slice(0, 36)""")


def cshot(name, *headings):
    f = app()
    print(f"   headings for {name}: {heads(f)}")
    for h in headings:
        c = card(h, f)
        if c is not None:
            shot(name, clip=c)
            return True
    print(f"!! {name}: none of {headings} found, keeping the whole window")
    shot(name)
    return False


def choose(f, trigger_text, option, also=()):
    """Open the dropdown whose trigger reads `trigger_text` and pick `option`."""
    pat = "|".join(re.escape(x) for x in (trigger_text, *also))
    sel = f.locator("button").filter(has_text=re.compile(rf"^({pat})$"))
    if not sel.count():
        print(f"!! choose: no trigger {trigger_text!r};"
              f" buttons = {[t.strip()[:30] for t in f.locator('button').all_inner_texts() if t.strip()][:20]}")
        return False
    sel.first.click()
    page.wait_for_timeout(2500)
    g = app()
    opt = g.get_by_role("option", name=re.compile(re.escape(option)))
    if not opt.count():
        print(f"!! choose: option {option!r} missing;"
              f" options = {[t.strip()[:40] for t in g.get_by_role('option').all_inner_texts()][:20]}")
        page.keyboard.press("Escape")
        return False
    opt.first.click()
    page.wait_for_timeout(2500)
    return True


# --- open the create form ---------------------------------------------------
goto(NETWORKS)
page.wait_for_timeout(WAIT)
app().get_by_role("link", name=re.compile(r"^global-network-")).first.click()
page.wait_for_timeout(WAIT)
app().get_by_role("link", name="Attachments", exact=True).first.click()
page.wait_for_timeout(WAIT)

f = app()
f.get_by_role("button", name="Create attachment", exact=True).first.click()
page.wait_for_timeout(WAIT)
f = app()
print("CREATE FORM headings:", heads(f))
print("CREATE FORM controls:", controls(f))
print("CREATE FORM body:", body(f)[:900].replace("\n", " | "))

# --- core network, edge location, attachment type, VPC -----------------------
choose(f, "Choose a core network", "core-network-", also=("Select core network",))
choose(app(), "Choose an edge location", EDGE, also=("Select edge location",))
choose(app(), "Choose an attachment type", "VPC", also=("Select attachment type",))
cshot("lab1-attach-01-create", "Create attachment", "Attachment settings", "Details")

f = app()
if VPC:
    choose(f, "Choose a VPC", VPC, also=("Select VPC",))
else:
    print("!! no $CWAN_VPC given")

f = app()
print("AFTER VPC controls:", controls(f))
for s in SUBNETS:
    choose(app(), "Choose subnets", s, also=("Select subnets",))
cshot("lab1-attach-02-subnets", "Subnets", "VPC", "Create attachment")

# --- tags --------------------------------------------------------------------
f = app()
add = f.get_by_role("button", name=re.compile(r"^Add (new )?tag$"))
print("Add tag buttons:", add.count())
for key, val in (("Name", ATT_NAME), ("segment", SEGMENT)):
    if not add.count():
        print("!! no Add tag button")
        break
    add.first.click()
    page.wait_for_timeout(1500)
    g = app()
    keys = g.locator('input[placeholder="Enter key"], input[aria-label="Key"]')
    vals = g.locator('input[placeholder="Enter value"], input[aria-label="Value"]')
    if keys.count() and vals.count():
        keys.last.fill(key)
        vals.last.fill(val)
        page.wait_for_timeout(800)
    else:
        print(f"!! tag inputs not found for {key}; controls = {controls(g)}")
    f = app()
    add = f.get_by_role("button", name=re.compile(r"^Add (new )?tag$"))
cshot("lab1-attach-03-tags", "Tags", "Create attachment")

print("BEFORE SUBMIT:", body(app())[:700].replace("\n", " | "))
b = app().get_by_role("button", name="Create attachment", exact=True)
print("submit buttons:", b.count())
if b.count():
    b.last.click()
    page.wait_for_timeout(12000)
    print("AFTER SUBMIT:", body(app())[:500].replace("\n", " | "))
