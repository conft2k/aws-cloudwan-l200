"""Lab 2-4 (docs/lab3.md): the core network policy edit screen and its change set.

    AWS_PROFILE=cwan uv run --with playwright --with boto3 \
        python tools/console.py tools/shots/lab3-policy.py

Read-only by intent: it opens the editor and the change set view and then
leaves. It never submits a policy version and never executes a change set.
Set CWAN_GN / CWAN_ACCOUNT for a rebuilt environment.
"""
import os

ACCOUNT = os.environ.get("CWAN_ACCOUNT", "912748707045")
GN = os.environ.get(
    "CWAN_GN",
    f"arn:aws:networkmanager::{ACCOUNT}:global-network:global-network-0021916997aa1cba4",
)
NM = "https://us-west-2.console.aws.amazon.com/networkmanager/home?region=us-west-2"
VERSIONS = f"{NM}#/networks/{GN}/corenetwork/policy-versions"


def dump(f, label):
    print(f"\n===== {label} =====")
    print("URL:", page.url)
    for role in ("tab", "button", "link"):
        names = []
        for el in f.get_by_role(role).all():
            try:
                s = el.inner_text(timeout=600).strip()
            except Exception:
                continue
            if s and s not in names:
                names.append(s)
        print(f"-- {role}: {names}")
    try:
        print("-- inputs:", f.evaluate(
            """() => Array.from(document.querySelectorAll('input,textarea,select'))
                 .map(e => [e.tagName, e.type || '', e.placeholder || '',
                            e.getAttribute('aria-label') || ''])"""))
    except Exception:
        pass
    print("-- text --")
    print(f.locator("body").inner_text()[:6000])


def select_row(f, text):
    """Select a Cloudscape table row. The native radio is visually hidden, so
    click it from JS; a plain click() times out on 'element is not visible'."""
    row = f.locator("tr", has_text=text).last
    row.scroll_into_view_if_needed()
    try:
        row.locator('input[type="radio"]').first.evaluate("e => e.click()")
    except Exception:
        row.locator("td").first.click()
    page.wait_for_timeout(1500)


# --- 1. policy version list ------------------------------------------------
goto(VERSIONS)
page.wait_for_timeout(5000)
f = app()
dump(f, "policy versions list")
shot("lab3-policy-02-versions")

# --- 2. the edit screen: JSON editor or form? ------------------------------
select_row(f, "Policy version - 1")
f.get_by_role("button", name="Edit", exact=True).click()
page.wait_for_timeout(10000)
f = app()
dump(f, "edit policy version")
shot("lab3-policy-01-edit")

# every tab of the editor (form view vs JSON view live here)
for name in ("Segments", "Network function groups", "Attachment policies",
             "Core network configuration", "Policy", "JSON", "Visual"):
    tab = f.get_by_role("tab", name=name)
    if tab.count():
        tab.first.click()
        page.wait_for_timeout(3000)
        dump(f, f"edit tab: {name}")
        shot("lab3-policy-01-edit-" + name.lower().replace(" ", "-"))

# leave without saving
for name in ("Cancel", "Close"):
    b = f.get_by_role("button", name=name, exact=True)
    if b.count():
        b.first.click()
        page.wait_for_timeout(3000)
        break

# --- 3. change set view (never executed) -----------------------------------
goto(VERSIONS)
page.wait_for_timeout(5000)
f = app()
select_row(f, "Policy version - 1")
f.get_by_role("button", name="View or apply change set").click()
page.wait_for_timeout(8000)
f = app()
dump(f, "change set")
shot("lab3-policy-03-changeset")
