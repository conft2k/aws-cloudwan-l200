"""Make a core network attachment through the console, shooting the form.

    # 2-2-d: the Oregon prod VPC
    AWS_PROFILE=demo1 CWAN_EDGE=us-west-2 CWAN_VPC=vpc-... \
      CWAN_SUBNETS=subnet-a,subnet-b CWAN_ATT_NAME=cwan-ws-att-prod-usw2 \
      CWAN_SEGMENT=prod CWAN_SHOTS=lab1-attach-01-create,lab1-attach-02-subnets,lab1-attach-03-tags \
      uv run --with playwright --with boto3 python tools/console.py tools/shots/attach.py

    # 2-3-b: the Site-to-Site VPN
    CWAN_TYPE="Site-to-Site VPN" CWAN_EDGE=ap-northeast-2 CWAN_VPN=vpn-... \
      CWAN_ATT_NAME=cwan-ws-att-onprem-apne2 CWAN_SEGMENT=onprem \
      CWAN_SHOTS=lab2-attach-01-form ...

    # 3-1-d: the Oregon dev VPC
    CWAN_VPC=... CWAN_SEGMENT=dev CWAN_SHOTS=extraA-01-oregon-dev-attachment ...

Three pages make an attachment, and the form screens only exist while one is
being made (PLAN.md 14-4), so this both shoots and submits. $CWAN_SHOTS names
the shots in order - form, subnets, tags - and a name may be left empty to skip
that one.

It prints every control it finds before touching it. Read the log, not the code,
to see what the form offers.
"""
import os

TYPE = os.environ.get("CWAN_TYPE", "VPC")
VPC = os.environ.get("CWAN_VPC", "")
VPN = os.environ.get("CWAN_VPN", "")
SUBNETS = [s for s in os.environ.get("CWAN_SUBNETS", "").split(",") if s]
EDGE = os.environ.get("CWAN_EDGE", "us-west-2")
ATT_NAME = os.environ.get("CWAN_ATT_NAME", "cwan-ws-att-prod-usw2")
SEGMENT = os.environ.get("CWAN_SEGMENT", "prod")
SHOTS = (os.environ.get("CWAN_SHOTS") or
         "lab1-attach-01-create,lab1-attach-02-subnets,lab1-attach-03-tags").split(",")
SHOTS += [""] * (3 - len(SHOTS))
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
        c = panel(h, frame=f)
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

# --- fill the form --------------------------------------------------------
# What the form really offers (a run on 2026-11-16 printed it): a Name text box
# with the placeholder "My attachment", an attachment-type button that already
# reads "VPC", a "Choose edge location" button, a "Select a VPC ID" button, and
# a tag row of "Enter key" / "Enter value". There is no core network field -
# you are already inside one. The subnet picker only appears once a VPC is set.
f = app()
name_in = f.locator('input[placeholder="My attachment"]')
print("name box:", name_in.count())
if name_in.count():
    name_in.first.fill(ATT_NAME)
    page.wait_for_timeout(800)

if TYPE != "VPC":
    # The type list calls it "VPN", not "Site-to-Site VPN".
    choose(app(), "VPC", TYPE)
    print("AFTER TYPE controls:", controls(app()))
choose(app(), "Choose edge location", EDGE)

if SHOTS[0]:
    cshot(SHOTS[0], "Attachment settings", "Create attachment", "Details")

if TYPE == "VPC":
    if VPC:
        choose(app(), "Select a VPC ID", VPC)
    else:
        print("!! no $CWAN_VPC given")
    g = app()
    print("AFTER VPC controls:", controls(g))
    for sub in SUBNETS:
        choose(app(), "Select subnet IDs", sub,
               also=("Select subnets", "Choose subnets", "Select a subnet ID"))
else:
    if VPN:
        choose(app(), "Select a VPN connection", VPN,
               also=("Choose a VPN connection", "Select a Site-to-Site VPN connection",
                     "Select a VPN ID", "Select a VPN connection ID",
                     "Choose a Site-to-Site VPN connection"))
    else:
        print("!! no $CWAN_VPN given")

if SHOTS[1]:
    cshot(SHOTS[1], "VPC attachment", "Subnets", "Create attachment")

# --- tags -------------------------------------------------------------------
# One empty tag row is already on the form, so fill it rather than adding one.
# Name is a form field here, not a tag, so only `segment` is needed.
f = app()
keys = f.locator('input[placeholder="Enter key"]')
vals = f.locator('input[placeholder="Enter value"]')
print("tag rows:", keys.count())
if not keys.count():
    add = f.get_by_role("button", name=re.compile(r"^Add (new )?tag$"))
    if add.count():
        add.first.click()
        page.wait_for_timeout(1500)
        f = app()
        keys = f.locator('input[placeholder="Enter key"]')
        vals = f.locator('input[placeholder="Enter value"]')
if keys.count() and vals.count():
    keys.last.fill("segment")
    vals.last.fill(SEGMENT)
    page.wait_for_timeout(800)
else:
    print("!! no tag inputs;", controls(app()))
if SHOTS[2]:
    cshot(SHOTS[2], "Tags", "Create attachment")

print("BEFORE SUBMIT:", body(app())[:700].replace("\n", " | "))
b = app().get_by_role("button", name="Create attachment", exact=True)
print("submit buttons:", b.count())
if b.count():
    b.last.click()
    page.wait_for_timeout(12000)
    print("AFTER SUBMIT:", body(app())[:500].replace("\n", " | "))
