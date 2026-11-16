"""The EC2 "Connect to instance" screen, for the steps that open a terminal.

    AWS_PROFILE=demo1 AWS_REGION=ap-northeast-2 CWAN_INSTANCE=i-... \
      CWAN_SHOT=lab1-eic-01-connect \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/eic-connect.py

Read-only: it stops at the form and never presses Connect. The pages disagree
about the tab's name - 2-2-b says "In web browser", 2-3-c says "EC2 Instance
Connect" - so this prints the tab list and the page can then say the real one.
"""
import os

INSTANCE = os.environ.get("CWAN_INSTANCE", "")
NAME = os.environ.get("CWAN_SHOT", "eic-connect")
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


goto(f"/ec2/home?region={REGION}#InstanceDetails:instanceId={INSTANCE}")
page.wait_for_timeout(WAIT)
f = app()
print("DETAIL headings:", heads(f))

btn = f.get_by_role("button", name="Connect", exact=True)
if not btn.count():
    btn = f.get_by_role("link", name="Connect", exact=True)
print("Connect buttons:", btn.count())
if btn.count():
    btn.last.click()
    page.wait_for_timeout(WAIT)

f = app()
tabs = [x.strip() for x in f.get_by_role("tab").all_inner_texts() if x.strip()]
print("CONNECT TABS:", tabs)
print("headings:", heads(f))
print("body:", body(f)[:800].replace("\n", " | "))

# Whichever of these the console calls it, land on the browser-terminal tab.
for want in ("EC2 Instance Connect", "In web browser", "Instance Connect"):
    tb = f.get_by_role("tab", name=want, exact=True)
    if tb.count():
        tb.first.click()
        page.wait_for_timeout(3000)
        print("clicked tab:", want)
        break

f = app()
for h in ("Connect to instance", "EC2 Instance Connect", "Instance ID"):
    c = panel(h, frame=f)
    if c is not None:
        shot(NAME, clip=c)
        print(f"shot cropped to {h!r}")
        break
else:
    print("!! no panel matched, keeping the whole window")
    shot(NAME)
