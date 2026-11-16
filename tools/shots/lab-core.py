# Core screens for labs 2-2 .. 2-4, from a finished rehearsal environment.
# Read-only: opens the policy editor but always leaves with Cancel.
import os
GN = os.environ.get("CWAN_GN", "")
BASE = f"/networkmanager/home?region=us-west-2#/networks/{GN}/corenetwork"

def settle(ms=5000):
    page.wait_for_timeout(ms)
    close_tours()

def names(f, role):
    try:
        return f.get_by_role(role).all_inner_texts()
    except Exception:
        return []

# --- core network overview: segments 4, edges 2 ---------------------------
goto(f"{BASE}/overview"); settle()
f = app(); shot("lab1-core-01-overview")
print("TABS:", [t for t in names(f, "tab")][:20])

# --- attachments: five, each with its segment and Region in the name ------
goto(f"{BASE}/attachments"); settle()
f = app(); shot("lab1-core-02-attachments")

# --- segment route table --------------------------------------------------
goto(f"{BASE}/routes"); settle()
f = app(); shot("lab1-routes-01-segment-table")
print("ROUTE INPUTS:", f.evaluate("() => [...document.querySelectorAll('input,select')].map(e => e.placeholder || e.name || e.type).slice(0,12)"))

# --- policy versions: two versions, version 2 is LIVE ----------------------
goto(f"{BASE}/policy-versions"); settle()
f = app(); shot("lab3-policy-02-versions")

# --- the editor: form tabs or a JSON editor? ------------------------------
clicked = f.evaluate("""() => {
  const r = document.querySelector('table input[type=radio], [role=radio]');
  if (r) { r.click(); return true; } return false;
}""")
print("ROW SELECTED:", clicked)
if clicked:
    page.wait_for_timeout(1500)
    btn = f.get_by_role("button", name="Edit", exact=True)
    if btn.count():
        btn.first.click()
        settle(9000)
        f = app()
        shot("lab3-policy-01-edit")
        tabs = [t for t in names(f, "tab")]
        print("EDITOR TABS:", tabs)
        for t in tabs:
            if not t.strip():
                continue
            try:
                f.get_by_role("tab", name=t, exact=True).first.click()
                page.wait_for_timeout(2500)
                shot("lab3-policy-01-edit-" + t.lower().replace(" ", "-").replace("/", "-")[:40])
                print("  tab shot:", t)
            except Exception as e:
                print("  tab failed:", t, str(e)[:70])
        for leave in ("Cancel", "Close"):
            b = f.get_by_role("button", name=leave, exact=True)
            if b.count():
                b.first.click(); print("LEFT WITH:", leave); break
