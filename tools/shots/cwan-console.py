"""Cloud WAN console screenshots, one lab stage per run.

    AWS_PROFILE=cwan CWAN_STAGE=core uv run --with playwright --with boto3 \
        python tools/console.py tools/shots/cwan-console.py

$CWAN_STAGE picks the stage, because each one needs the environment in the
state a participant is in at that point (PLAN.md 14-4):

* core         - 2-1-d and 2-2-a: before anything is attached by hand
* routes-prod  - 2-2-f: after the Oregon prod attachment exists
* routes-onprem- 2-3-d: after the VPN attachment is up, before the 2-4 policy
* policy       - 2-4: the policy version list and the editor

Two things this console forces:

* Navigate by CLICKING, never by a hash URL. Network Manager keeps the core
  network id in memory, so entering "#/networks/<arn>/corenetwork/attachments"
  renders an empty body or "Failed to fetch attachments within this core
  network".
* Widen the column you care about. Tables are fixed-layout at 168px a column,
  so Name truncates to "cwan-ws-att..." and the page cannot show which Region
  an attachment belongs to. Hiding other columns does not help - the freed
  space stays blank - and neither does folding the navigation or widening the
  window. Drag the header's resize handle (resize_column).

Read-only by intent: it opens the policy editor to shoot the form and leaves
without creating a policy version or executing a change set.
"""
import os
import re

NETWORKS = ("https://us-west-2.console.aws.amazon.com"
            "/networkmanager/home?region=us-west-2#/networks")
WAIT = 9000


def body(f):
    try:
        return f.locator("body").inner_text()
    except Exception:
        return ""


def take(f, name, must=None, crop=None):
    """Shoot `name`, cropped to the panel(s) the workshop page talks about.

    `crop` is a panel heading, or a tuple of them when a step reads two panels
    together. Without it the whole window is kept, which is mostly navigation
    and empty space.
    """
    t = body(f)
    if "could not be fetched" in t or "Failed to fetch" in t:
        print(f"!! {name}: console reported a fetch error, not shooting")
        return False
    if must and must not in t:
        print(f"!! {name}: expected {must!r} missing, not shooting")
        print("   body:", t[:400].replace("\n", " | "))
        return False
    clip = None
    if crop:
        names = (crop,) if isinstance(crop, str) else tuple(crop)
        parts = [card(n) for n in names]
        # A table panel's container often measures as the header strip alone,
        # which crops the rows away, so always take the table in as well.
        tbl = f.locator("table")
        if tbl.count():
            parts.append(tbl.last)
        clip = span(*parts)
        if clip is None:
            print(f"!! {name}: no panel for {names}, keeping the whole window")
    shot(name, clip=clip)
    return True


def nav(name, must=None, tries=3):
    """Click a left-navigation link, retrying while the pane is still filling.

    A first-time account opens with the service navigation folded, and the
    folded state is remembered, so the link may not be there at all. Unfold and
    dismiss the cookie banner before giving up on it.
    """
    for i in range(tries):
        link = app().get_by_role("link", name=name, exact=True)
        if not link.count():
            print(f".. {name}: no such link yet, unfolding the navigation")
            close_tours()
            expand_nav()
            page.wait_for_timeout(2500)
            link = app().get_by_role("link", name=name, exact=True)
        if not link.count():
            page.wait_for_timeout(WAIT)
            continue
        # The link for the page you are already on is aria-disabled, and
        # clicking it waits for an element that never becomes enabled.
        here = (link.first.get_attribute("aria-current") == "page"
                or link.first.get_attribute("aria-disabled") == "true")
        if here:
            print(f".. {name}: already on this page")
        else:
            link.first.click()
            page.wait_for_timeout(WAIT)
        f = app()
        if not must or must in body(f):
            return f
        print(f".. {name}: {must!r} not there yet, waiting")
        page.wait_for_timeout(WAIT)
    print(f"!! nav({name!r}) gave up;"
          f" links = {[x.strip()[:24] for x in app().get_by_role('link').all_inner_texts() if x.strip()][:20]}")
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


STAGE = os.environ.get("CWAN_STAGE", "core")
NOISE = ["Account ID", "Network function groups", "NAT gateway support",
         "NAT system route support", "Resource ID",
         "Attachment policy rule number"]


def open_core_network():
    """Network Manager -> Global networks -> the workshop one -> Core network."""
    goto(NETWORKS)
    page.wait_for_timeout(WAIT)
    f = app()
    take(f, "lab0-cnet-00-global-networks", "cwan-ws-global", crop="Global networks")
    f.get_by_role("link", name=re.compile(r"^global-network-")).first.click()
    page.wait_for_timeout(WAIT)
    close_tours()
    expand_nav()
    page.wait_for_timeout(2500)
    return nav("Core network", must="Edge locations")


def routes(segment, name, must=None):
    """Fill the Routes tab filter and shoot the table.

    Re-read the frame between the two dropdowns: choosing a segment re-renders
    the filter row, and a handle taken before that finds no buttons at all.
    """
    if not pick(app(), "Select segment", segment,
                also=("prod", "dev", "shared", "onprem")):
        return False
    page.wait_for_timeout(3000)
    if not pick(app(), "Select edge location", "ap-northeast-2",
                also=("ap-northeast-2", "us-west-2")):
        return False
    f = app()
    b = f.get_by_role("button", name=re.compile(r"^(Search routes|Search)$"))
    if b.count():
        b.first.click()
        page.wait_for_timeout(WAIT)
    # Destinations truncates to "attachment-0d39747b96dd62bf6 ..." and the tail
    # is the point: it says what the route points at. CIDR, Route type and Route
    # state hold short values, so take the width from them.
    # Destinations carries the whole point of this table - what the route points
    # at - and truncates to "attachment-0d39747b96dd62bf6 ...". Route state is
    # the last column, which Cloudscape refuses to drag because it absorbs
    # whatever the others leave, so squeeze CIDR and Route type down to what
    # their values need and spend all of it on Destinations.
    for col, w in (("CIDR", 120), ("Route type", 130)):
        resize_column(col, w)
    resize_column("Destinations", 620)
    f = app()
    print(f"--- routes {segment} ---")
    print(body(f)[:1200].replace("\n", " | "))
    return take(f, name, must, crop=("Route Filter", "Routes"))


def attachments(expect):
    """2-2-a: the attachment list, and one attachment's segment tag."""
    f = nav("Attachments", must="cwan-ws-att")
    table_columns(hide=NOISE)

    # The rows hold no links. Selecting one opens a detail pane *below* the
    # table with its own Details / Routing policy label / 1:1 NAT / Flow logs /
    # Tags tabs, and the URL never changes. So click the row, then its Tags tab.
    f = app()
    row = f.locator("table tbody tr").filter(has_text="cwan-ws-att-prod-apne2")
    print("prod-apne2 rows:", row.count())
    try:
      if row.count():
          # Prefer the row's link - the Attachment ID cell - because that opens
          # the attachment itself. Clicking the name cell only ticks the row.
          # (An earlier probe saw no link in the row because that run had the
          # Attachment ID column hidden.)
          link = row.first.get_by_role("link")
          if link.count():
              print("   opening via the row link:", link.first.inner_text().strip()[:30])
              link.first.click()
          else:
              cell = row.first.locator("td").filter(has_text="cwan-ws-att-prod-apne2")
              (cell.first if cell.count() else row.first.locator("td").nth(1)).click()
          page.wait_for_timeout(WAIT)
          # The detail pane opens below the table and takes a moment to appear.
          tags = None
          for _ in range(4):
              g = app()
              names = [x.strip() for x in g.get_by_role("tab").all_inner_texts() if x.strip()]
              print("   detail tabs:", names)
              if "Tags" in names:
                  tags = tab(g, "Tags", must="segment")
                  break
              page.wait_for_timeout(4000)
          if tags is not None:
              take(tags, "lab1-core-03-attachment-tags", "segment", crop="Tags")
          else:
              # Not fatal. The segment tag is also visible as the table's Segment
              # column, which 2-2-a reads anyway, so losing this one shot does not
              # stop the stage.
              print("!! the attachment detail pane never showed a Tags tab")
              # Is the split panel simply closed? On the account used for the
              # first rehearsal it was already open, so clicking a row showed
              # the tabs; a first-time account may need the handle opened, and
              # then 2-2-a step 5 has to say so.
              g = app()
              print("   panel-ish controls:", g.evaluate("""() => [...document.querySelectorAll(
                    'button, [role=button]')]
                  .map(e => ({t: (e.innerText||'').trim().slice(0,30),
                              l: e.getAttribute('aria-label'),
                              x: e.getAttribute('aria-expanded')}))
                  .filter(o => /panel|split|detail|expand/i.test((o.l||'') + ' ' + o.t))
                  .slice(0, 12)"""))
              print("   row actions:", [x.strip() for x in
                    g.get_by_role("button").all_inner_texts() if x.strip()][:14])
      else:
        print("!! no row named cwan-ws-att-prod-apne2")
    except Exception as e:
        print("!! tags shot gave up:", str(e).splitlines()[0][:90])

    # At 168px Name truncates to "cwan-ws-att...", and the Region in that name
    # is the whole point of the page. Hiding columns alone does not fix it (the
    # freed space stays blank), so hide what 2-2-a does not read and spend that
    # space on Name. The navigation stays open: participants see it too.
    f = nav("Attachments", must="cwan-ws-att")
    table_columns(hide=NOISE + ["Attachment ID"])
    resize_column("Name", 330)
    take(app(), "lab1-core-02-attachments", expect, crop="Attachments")


def policy_versions(shot_name):
    f = nav("Policy versions", must="Policy version - 1")
    take(f, shot_name, "Policy version - 1", crop="Policy versions")
    return f


print(f"=== stage {STAGE} ===")

if STAGE == "core":
    f = open_core_network()
    take(f, "lab1-core-01-overview", "Edge locations", crop="Inventory")
    attachments("cwan-ws-att-shared-apne2")
    policy_versions("lab0-cnet-01-policy-versions")

elif STAGE == "routes-prod":
    f = open_core_network()
    f = tab(f, "Routes")
    routes("prod", "lab1-routes-01-segment-table", "10.11.1.0/24")

elif STAGE == "routes-onprem":
    f = open_core_network()
    f = tab(f, "Routes")
    routes("onprem", "lab2-routes-01-onprem-segment", "10.30.1.0/24")
    routes("shared", "lab2-routes-02-shared-segment", "172.16.1.0/24")

elif STAGE == "policy":
    f = open_core_network()
    f = policy_versions("lab3-policy-02-versions")
    if select_row("Policy version - 1", f):
        e = f.get_by_role("button", name="Edit", exact=True)
        print("Edit enabled:", bool(e.count()) and e.first.is_enabled())
        e.first.click()
        page.wait_for_timeout(14000)
        f = app()
        print("--- editor ---")
        print("tabs:", [x.inner_text().strip() for x in f.get_by_role("tab").all()])
        print(body(f)[:2000])
        take(f, "lab3-policy-01-edit", crop="Create policy")

else:
    raise SystemExit(f"unknown CWAN_STAGE {STAGE!r}")
