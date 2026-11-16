"""Cloud WAN console screenshots for labs 2-2, 2-3 and 2-4.

    AWS_PROFILE=cwan uv run --with playwright --with boto3 \
        python tools/console.py tools/shots/cwan-console.py

Two things this console forces:

* Navigate by CLICKING, never by a hash URL. Network Manager keeps the core
  network id in memory, so entering "#/networks/<arn>/corenetwork/attachments"
  renders an empty body or "Failed to fetch attachments within this core
  network".
* Trim the table columns. With all of them on, Name and Attachment ID
  truncate to "cwan-ws-a..." and the page cannot show which VPC an attachment
  belongs to. Do not fold the left navigation instead - the later steps click
  its links.

Read-only by intent: it opens the policy editor and the change set view and
leaves without creating a policy version or executing a change set.
"""
import re

NETWORKS = ("https://us-west-2.console.aws.amazon.com"
            "/networkmanager/home?region=us-west-2#/networks")
WAIT = 9000


def body(f):
    try:
        return f.locator("body").inner_text()
    except Exception:
        return ""


def take(f, name, must=None):
    t = body(f)
    if "could not be fetched" in t or "Failed to fetch" in t:
        print(f"!! {name}: console reported a fetch error, not shooting")
        return False
    if must and must not in t:
        print(f"!! {name}: expected {must!r} missing, not shooting")
        print("   body:", t[:400].replace("\n", " | "))
        return False
    shot(name)
    return True


def nav(name, must=None, tries=2):
    """Click a left-navigation link, retrying while the pane is still filling."""
    for i in range(tries):
        app().get_by_role("link", name=name, exact=True).first.click()
        page.wait_for_timeout(WAIT)
        f = app()
        if not must or must in body(f):
            return f
        print(f".. {name}: {must!r} not there yet, waiting")
        page.wait_for_timeout(WAIT)
    return app()


def tab(f, name, must=None):
    t = f.get_by_role("tab", name=name, exact=True)
    if not t.count():
        print(f"!! tab {name!r} not found; tabs ="
              f" {[x.inner_text().strip() for x in f.get_by_role('tab').all()]}")
        return f
    t.first.click()
    page.wait_for_timeout(WAIT)
    f = app()
    if must and must not in body(f):
        page.wait_for_timeout(WAIT)
        f = app()
    return f


def pick(f, label, option):
    sel = f.get_by_role("button", name=re.compile(label))
    if not sel.count():
        sel = f.locator(f'[placeholder="{label}"], [aria-label="{label}"]')
    if not sel.count():
        print(f"!! select {label!r} not found")
        return False
    sel.first.click()
    page.wait_for_timeout(2500)
    opt = f.get_by_role("option", name=option, exact=True)
    if not opt.count():
        opt = f.get_by_role("option", name=re.compile(option))
    if not opt.count():
        print(f"!! option {option!r} not found under {label!r}")
        page.keyboard.press("Escape")
        return False
    opt.first.click()
    page.wait_for_timeout(3000)
    return True


# --- global network list ---------------------------------------------------
goto(NETWORKS)
page.wait_for_timeout(WAIT)
f = app()
take(f, "lab1-core-00-global-networks", "cwan-ws-global")

f.get_by_role("link", name=re.compile(r"^global-network-")).first.click()
page.wait_for_timeout(WAIT)

# --- core network overview and segments ------------------------------------
f = nav("Core network", must="Edge locations")
take(f, "lab1-core-01-overview", "Edge locations")

f = tab(f, "Logical", must="prod")
take(f, "lab1-core-02-segments", "prod")

# --- segment route table ---------------------------------------------------
f = tab(f, "Routes")
if pick(f, "Select segment", "prod") and pick(f, "Select edge location", "ap-northeast-2"):
    b = f.get_by_role("button", name=re.compile(r"^(Search routes|Search)$"))
    if b.count():
        b.first.click()
        page.wait_for_timeout(WAIT)
    f = app()
    print("--- routes ---")
    print(body(f)[:1800])
    take(f, "lab1-routes-01-segment-table")

# --- attachments -----------------------------------------------------------
f = nav("Attachments", must="cwan-ws-att")
table_columns(hide=["Account ID", "Network function groups",
                    "NAT gateway support", "NAT system route support"])
f = app()
take(f, "lab1-core-03-attachments", "cwan-ws-att-prod-apne2")

# --- policy versions and the FORM editor -----------------------------------
f = nav("Policy versions", must="Policy version - 1")
take(f, "lab3-policy-01-versions", "Policy version - 1")

if select_row("Policy version - 2", f):
    e = f.get_by_role("button", name="Edit", exact=True)
    print("Edit enabled:", bool(e.count()) and e.first.is_enabled())
    e.first.click()
    page.wait_for_timeout(14000)
    f = app()
    print("--- editor ---")
    print("URL:", page.url)
    print("tabs:", [x.inner_text().strip() for x in f.get_by_role("tab").all()])
    print(body(f)[:2500])
    take(f, "lab3-policy-02-edit")
