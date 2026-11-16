"""3-1-b: an attachment waiting for acceptance, and accepting it.

    AWS_PROFILE=demo1 CWAN_ATT=attachment-... \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/extra-accept.py

Only exists while `require-attachment-acceptance` is on for the segment and an
attachment has just been made into it, so it is shot and accepted in one pass.
"""
import os

ATT = os.environ.get("CWAN_ATT", "")
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


goto(NETWORKS)
page.wait_for_timeout(WAIT)
app().get_by_role("link", name=re.compile(r"^global-network-")).first.click()
page.wait_for_timeout(WAIT)
close_tours()
expand_nav()
page.wait_for_timeout(2500)

f = nav("Attachments", must="cwan-ws-att")
table_columns(hide=NOISE + ["Attachment ID"])
resize_column("Name", 300)
resize_column("State", 290)
f = app()
print("states:", [s for s in ("Pending attachment acceptance", "Available")
                  if s in body(f)])
c = panel("Attachments", frame=f)
shot("extraA-b1-pending-acceptance", clip=c)

# Accept it: select the row, then Actions -> Accept.
print("select_row:", select_row(ATT) if ATT else "no $CWAN_ATT")
f = app()
acts = f.get_by_role("button", name="Actions", exact=True)
print("Actions button:", acts.count())
if acts.count():
    acts.first.click()
    page.wait_for_timeout(2500)
    g = app()
    items = [t.strip() for t in g.get_by_role("menuitem").all_inner_texts() if t.strip()]
    print("ACTIONS MENU:", items)
    shot("extraA-b2-accept-attachment")
    acc = g.get_by_role("menuitem", name="Accept", exact=True)
    print("Accept item:", acc.count())
    if acc.count():
        acc.first.click()
        page.wait_for_timeout(4000)
        h = app()
        print("after accept:", body(h)[:400].replace("\n", " | "))
        confirm = h.get_by_role("button", name=re.compile(r"^(Accept|Confirm)$"))
        if confirm.count():
            confirm.last.click()
            page.wait_for_timeout(6000)
            print("confirmed")
