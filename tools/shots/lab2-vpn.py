"""2-3-a: create the Site-to-Site VPN connection, shooting the form.

    AWS_PROFILE=demo1 AWS_REGION=ap-northeast-2 CWAN_CGW=cgw-... \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/lab2-vpn.py

Target gateway type stays "Not associated": the connection is attached to the
core network in 2-3-b, not to a gateway. Routing must be dynamic, because a
Cloud WAN VPN attachment does not support static routes.

Submits the form, because the form only exists before the connection does.
"""
import os

CGW = os.environ.get("CWAN_CGW", "")
NAME = os.environ.get("CWAN_VPN_NAME", "cwan-ws-vpn")
WAIT = 7000


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


def wait_app(must, tries=8):
    for _ in range(tries):
        f = app()
        if must in body(f):
            return f
        page.wait_for_timeout(3000)
    print(f"!! wait_app: never saw {must!r}")
    return app()


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


def radio(f, label):
    """Tick a Cloudscape radio by its visible label (the input is hidden)."""
    for loc in (f.locator("label").filter(has_text=re.compile(rf"^{re.escape(label)}")),
                f.get_by_role("radio", name=re.compile(re.escape(label)))):
        if loc.count():
            try:
                loc.first.click(timeout=6000)
                page.wait_for_timeout(1200)
                return True
            except Exception as e:
                print(f"   radio {label!r}:", str(e).splitlines()[0][:70])
    print(f"!! radio {label!r} not found")
    return False


goto(f"/vpc/home?region={REGION}#VpnConnections:")
page.wait_for_timeout(WAIT)
f = app()
print("LIST headings:", heads(f))
b = f.get_by_role("button", name="Create VPN connection", exact=True)
if not b.count():
    b = f.get_by_role("link", name="Create VPN connection", exact=True)
print("create buttons:", b.count())
b.last.click()
page.wait_for_timeout(WAIT)

f = wait_app("Target gateway type")
print("FORM headings:", heads(f))
print("FORM body:", body(f)[:900].replace("\n", " | "))

name_in = f.get_by_role("textbox", name=re.compile("Name tag", re.I))
if not name_in.count():
    name_in = f.locator('input[placeholder="Name"], input[aria-label="Name tag - optional"]')
if name_in.count():
    name_in.first.fill(NAME)
else:
    print("!! Name tag box not found")

radio(app(), "Not associated")
radio(app(), "Existing")
page.wait_for_timeout(1500)

f = app()
if CGW:
    sel = f.locator("button").filter(has_text=re.compile(r"^(Choose a customer gateway|Select a customer gateway)$"))
    if sel.count():
        sel.first.click()
        page.wait_for_timeout(2000)
        g = app()
        opt = g.get_by_role("option", name=re.compile(re.escape(CGW)))
        if opt.count():
            opt.first.click()
            page.wait_for_timeout(1500)
        else:
            print(f"!! customer gateway {CGW} not in the list;"
                  f" options = {[x.strip()[:40] for x in g.get_by_role('option').all_inner_texts()][:10]}")
            page.keyboard.press("Escape")
    else:
        print("!! customer gateway select not found;"
              f" buttons = {[x.strip()[:30] for x in f.locator('button').all_inner_texts() if x.strip()][:20]}")

radio(app(), "Dynamic (requires BGP)")
cshot("lab2-vpn-01-create", "Create VPN connection", "Details", "Routing options")

print("BEFORE SUBMIT:", body(app())[:600].replace("\n", " | "))
f = app()
sb = f.get_by_role("button", name="Create VPN connection", exact=True)
print("submit buttons:", sb.count())
if sb.count():
    sb.last.click()
    page.wait_for_timeout(15000)
    print("AFTER SUBMIT:", body(app())[:500].replace("\n", " | "))
