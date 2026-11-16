"""3-4: delete what the participant made, shooting each confirmation.

    # an attachment (3-4-a, 3-4-b)
    AWS_PROFILE=demo1 CWAN_DEL=attachment CWAN_ATT=attachment-... \
      CWAN_SHOT=extraD-01-delete-attachment \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/extra-delete.py

    # the VPN connection (3-4-c)
    CWAN_DEL=vpn AWS_REGION=ap-northeast-2 CWAN_VPN=vpn-... \
      CWAN_SHOT=extraD-03-delete-vpn ...

This really deletes. It is the teardown the workshop ends with, and the
confirmation screens only exist while it happens - which is also why the four
"measured in the pre-test" headings in 3-4 can only be filled in here.
"""
import os

KIND = os.environ.get("CWAN_DEL", "attachment")
ATT = os.environ.get("CWAN_ATT", "")
VPN = os.environ.get("CWAN_VPN", "")
NAME = os.environ.get("CWAN_SHOT", "extraD-delete")
NETWORKS = ("https://us-west-2.console.aws.amazon.com"
            "/networkmanager/home?region=us-west-2#/networks")
WAIT = 8000
NOISE = ["Account ID", "Network function groups", "NAT gateway support",
         "NAT system route support", "Resource ID",
         "Attachment policy rule number"]


def body(f):
    try:
        return f.locator("body").inner_text()
    except Exception:
        return ""


def heads(f):
    try:
        return [h.strip() for h in f.get_by_role("heading").all_inner_texts() if h.strip()][:14]
    except Exception:
        return []


def nav(name, must=None, tries=3):
    for _ in range(tries):
        link = app().get_by_role("link", name=name, exact=True)
        if not link.count():
            close_tours()
            expand_nav()
            page.wait_for_timeout(2500)
            link = app().get_by_role("link", name=name, exact=True)
        if not link.count():
            page.wait_for_timeout(WAIT)
            continue
        if not (link.first.get_attribute("aria-current") == "page"
                or link.first.get_attribute("aria-disabled") == "true"):
            link.first.click()
            page.wait_for_timeout(WAIT)
        f = app()
        if not must or must in body(f):
            return f
        page.wait_for_timeout(WAIT)
    return app()


def confirm_dialog(shot_name):
    """Shoot the confirmation and then go through with it."""
    page.wait_for_timeout(2500)
    f = app()
    dlg = f.get_by_role("dialog")
    print("dialogs:", dlg.count(), "| headings:", heads(f))
    print("dialog text:", body(f)[:500].replace("\n", " | "))
    if dlg.count():
        shot(shot_name, clip=dlg.last)
    else:
        shot(shot_name)
    # Some delete dialogs want the word typed before the button enables.
    box = f.locator('input[placeholder="delete"], input[placeholder="Delete"]')
    if box.count():
        box.first.fill("delete")
        page.wait_for_timeout(800)
    btn = f.get_by_role("button", name=re.compile(r"^(Delete|Confirm)$"))
    print("confirm buttons:", btn.count())
    if btn.count():
        btn.last.click()
        page.wait_for_timeout(6000)
        print("after confirm:", body(app())[:300].replace("\n", " | "))


if KIND == "attachment":
    goto(NETWORKS)
    page.wait_for_timeout(WAIT)
    app().get_by_role("link", name=re.compile(r"^global-network-")).first.click()
    page.wait_for_timeout(WAIT)
    close_tours()
    expand_nav()
    page.wait_for_timeout(2500)
    f = nav("Attachments", must="cwan-ws-att")
    table_columns(hide=NOISE)
    print("select_row:", select_row(ATT))
    f = app()
    acts = f.get_by_role("button", name="Actions", exact=True)
    print("Actions:", acts.count())
    if acts.count():
        acts.first.click()
        page.wait_for_timeout(2500)
        g = app()
        print("menu:", [t.strip() for t in g.get_by_role("menuitem").all_inner_texts() if t.strip()])
        d = g.get_by_role("menuitem", name="Delete", exact=True)
        print("Delete item:", d.count())
        if d.count():
            d.first.click()
            confirm_dialog(NAME)

elif KIND == "vpn":
    goto(f"/vpc/home?region={REGION}#VpnConnections:search={VPN}")
    page.wait_for_timeout(WAIT)
    f = app()
    print("headings:", heads(f))
    row = f.locator("table tbody tr").filter(has_text=VPN)
    print("rows:", row.count())
    if row.count():
        cb = row.first.locator('input[type=checkbox], input[type=radio]')
        if cb.count():
            cb.first.evaluate("e => e.click()")
            page.wait_for_timeout(2000)
    f = app()
    acts = f.get_by_role("button", name="Actions", exact=True)
    print("Actions:", acts.count())
    if acts.count():
        acts.first.click()
        page.wait_for_timeout(2500)
        g = app()
        print("menu:", [t.strip() for t in g.get_by_role("menuitem").all_inner_texts() if t.strip()])
        d = g.get_by_role("menuitem", name=re.compile(r"^Delete"))
        print("Delete item:", d.count())
        if d.count():
            d.first.click()
            confirm_dialog(NAME)

elif KIND == "stack":
    stack = os.environ["CWAN_STACK"]
    goto(f"/cloudformation/home?region={REGION}#/stacks?filteringText={stack}")
    page.wait_for_timeout(WAIT)
    f = app()
    link = f.get_by_role("link", name=stack, exact=True)
    print("stack links:", link.count())
    if link.count():
        link.first.click()
        page.wait_for_timeout(WAIT)
    f = app()
    print("headings:", heads(f))
    d = f.get_by_role("button", name="Delete", exact=True)
    print("Delete button:", d.count())
    if d.count():
        d.last.click()
        confirm_dialog(NAME)

else:
    raise SystemExit(f"unknown CWAN_DEL {KIND!r}")
