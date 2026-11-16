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


def pick(f, label, option, also=()):
    """Choose `option` in the dropdown whose trigger currently reads `label`.

    Two things make this awkward. The trigger is a plain <button> whose
    accessible name comes from the form field ("Segment"), not from the
    placeholder it displays ("Select segment"), so a role+name lookup misses it.
    And once something is chosen the trigger stops saying "Select segment" and
    says "prod", so the second visit has to look for the value too - that is
    what `also` is for.
    """
    pat = "|".join(re.escape(x) for x in (label, *also))
    sel = f.locator("button").filter(has_text=re.compile(rf"^({pat})$"))
    if not sel.count():
        sel = f.get_by_role("button", name=re.compile(label))
    if not sel.count():
        sel = f.locator(f'[placeholder="{label}"], [aria-label="{label}"]')
    if not sel.count():
        print(f"!! select {label!r} not found; buttons ="
              f" {[t.strip()[:28] for t in f.locator('button').all_inner_texts() if t.strip()][:18]}")
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
take(f, "lab0-cnet-00-global-networks", "cwan-ws-global")

f.get_by_role("link", name=re.compile(r"^global-network-")).first.click()
page.wait_for_timeout(WAIT)

# --- core network overview and segments ------------------------------------
f = nav("Core network", must="Edge locations")
take(f, "lab1-core-01-overview", "Edge locations")

# The Logical tab is skipped on purpose. It draws the segment-to-attachment
# map as a graph whose labels render rotated and truncated ("cwan-ws-att...")
# and whose lower half falls outside a 900px window, so it reads worse than the
# attachments table for showing which attachment sits in which segment.

# --- segment route tables ---------------------------------------------------
# Three pages read this table. 2-2 reads prod, and 2-3-d reads onprem (shared
# is there, prod is not) and shared (the on-premises prefix arrived as
# PROPAGATED), which is what explains the ping results before anyone pings.
def routes(segment, name, must=None):
    # Re-read the frame between the two dropdowns. Choosing a segment re-renders
    # the filter, and a frame handle taken before that finds no buttons at all,
    # which is why the first run reported "Select edge location not found".
    if not pick(app(), "Select segment", segment,
                also=("prod", "dev", "shared", "onprem")):
        return False
    page.wait_for_timeout(3000)  # choosing a segment re-renders the filter row
    if not pick(app(), "Select edge location", "ap-northeast-2",
                also=("ap-northeast-2", "us-west-2")):
        return False
    f = app()
    b = f.get_by_role("button", name=re.compile(r"^(Search routes|Search)$"))
    if b.count():
        b.first.click()
        page.wait_for_timeout(WAIT)
    f = app()
    print(f"--- routes {segment} ---")
    print(body(f)[:1200].replace("\n", " | "))
    return take(f, name, must)


f = tab(f, "Routes")
print("ROUTE TABS:", [x.inner_text().strip() for x in f.get_by_role("tab").all()])
routes("prod", "lab1-routes-01-segment-table", "10.10.1.0/24")
routes("onprem", "lab2-routes-01-onprem-segment", "10.30.1.0/24")
routes("shared", "lab2-routes-02-shared-segment", "172.16.1.0/24")

# --- attachments -----------------------------------------------------------
NOISE = ["Account ID", "Network function groups", "NAT gateway support",
         "NAT system route support", "Resource ID",
         "Attachment policy rule number"]

f = nav("Attachments", must="cwan-ws-att")
table_columns(hide=NOISE)

# 2-2-a step 5 opens one attachment and reads its segment tag. Do this before
# hiding Attachment ID below: that column holds the only link into the detail
# page, so hiding it first leaves nothing to click.
f = app()
row = f.locator("table tbody tr").filter(has_text="cwan-ws-att-prod-apne2")
print("prod-apne2 rows:", row.count())
opened = False
if row.count():
    # Only the Attachment ID cell links into the detail page. It is an <a> in
    # some console builds and a <button> in others, so try both rather than
    # waiting 45s on one guess.
    for how in (lambda r: r.get_by_role("link").first,
                lambda r: r.locator("a").first,
                lambda r: r.get_by_role("button", name=re.compile(r"^attachment-")).first):
        try:
            how(row.first).click(timeout=8000)
            opened = True
            break
        except Exception as e:
            print("   row link attempt failed:", str(e).splitlines()[0][:80])
if opened:
    page.wait_for_timeout(WAIT)
    f = tab(app(), "Tags", must="segment")
    take(f, "lab1-core-03-attachment-tags", "segment")
    f = nav("Attachments", must="cwan-ws-att")
else:
    print("!! could not open the cwan-ws-att-prod-apne2 detail page")
    if row.count():
        print("   row links:", row.first.evaluate(
            """r => [...r.querySelectorAll('a, button')].map(e => ({
                 tag: e.tagName, href: e.getAttribute('href'),
                 text: (e.innerText || '').trim().slice(0, 40),
                 hidden: e.offsetParent === null,
               }))"""))
    f = app()

# The Region in the attachment name is the whole point of this page, and at
# 168px Name truncates to "cwan-ws-att...". Hiding columns alone does not fix
# it (the freed space stays blank), so hide what 2-2-a does not read and spend
# that space on Name. The navigation stays open: participants see it too.
table_columns(hide=NOISE + ["Attachment ID"])
resize_column("Name", 330)
f = app()
take(f, "lab1-core-02-attachments", "cwan-ws-att-prod-usw2")

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
