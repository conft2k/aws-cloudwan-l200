"""2-4: the policy editor, the change set, and executing it.

    AWS_PROFILE=demo1 CWAN_PV=2 CWAN_PHASE=editor|changeset|live \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/lab3-policy.py

Phases, because the screens exist at different moments:

* editor    - opens Edit on the LIVE version, switches to JSON, shoots, cancels.
              Answers whether a participant can paste JSON there at all.
* changeset - $CWAN_PV must already exist and be READY_TO_EXECUTE. Shoots the
              version list and the change set, then executes it and shoots that.
* live      - after execution: the version list with the new LIVE alias.

Creating the version itself is tools/policy.py's job; this only drives the
screens the workshop pages show.
"""
import os

PV = os.environ.get("CWAN_PV", "")
PHASE = os.environ.get("CWAN_PHASE", "changeset")
NETWORKS = ("https://us-west-2.console.aws.amazon.com"
            "/networkmanager/home?region=us-west-2#/networks")
WAIT = 9000


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


def nav(name, must=None, tries=2):
    for _ in range(tries):
        app().get_by_role("link", name=name, exact=True).first.click()
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
f = nav("Policy versions", must="Policy version - 1")
print("POLICY VERSIONS:", body(f)[:700].replace("\n", " | "))

if PHASE == "editor":
    # Which editing modes does the console actually offer, and is the JSON one
    # usable? 2-4-a tells participants to paste a JSON fragment, so this has to
    # be true before the page can say it.
    row = f"Policy version - {PV}" if PV else "Policy version - 1"
    if select_row(row, f):
        e = app().get_by_role("button", name="Edit", exact=True)
        print("Edit enabled:", bool(e.count()) and e.first.is_enabled())
        e.first.click()
        page.wait_for_timeout(14000)
        g = app()
        print("EDITOR headings:", heads(g))
        print("EDITOR body:", body(g)[:1200].replace("\n", " | "))
        mode = g.get_by_role("radio", name=re.compile("JSON"))
        if not mode.count():
            mode = g.locator("label").filter(has_text=re.compile(r"^JSON"))
        print("JSON mode control:", mode.count())
        if mode.count():
            mode.first.click()
            page.wait_for_timeout(5000)
            g = app()
            print("AFTER JSON MODE:", body(g)[:900].replace("\n", " | "))
            editors = g.evaluate("""() => [...document.querySelectorAll(
                'textarea, .ace_editor, .cm-editor, [role=textbox]')]
                .map(e => ({tag: e.tagName, cls: String(e.className||'').slice(0,50),
                            ro: e.getAttribute('readonly')}))""")
            print("editor elements:", editors)
        cshot("lab3-policy-01-edit", "Create policy", "Policy", "Details")
        for leave in ("Cancel", "Close"):
            b = app().get_by_role("button", name=leave, exact=True)
            if b.count():
                b.first.click()
                print("left with", leave)
                break

elif PHASE == "changeset":
    cshot("lab3-policy-02-versions", "Policy versions")
    if not PV:
        raise SystemExit("set $CWAN_PV to the new version")
    if select_row(f"Policy version - {PV}", app()):
        b = app().get_by_role("button", name="View or apply change set", exact=True)
        print("change set button:", b.count())
        if b.count():
            b.first.click()
            page.wait_for_timeout(WAIT)
            g = app()
            print("CHANGE SET headings:", heads(g))
            print("CHANGE SET body:", body(g)[:1200].replace("\n", " | "))
            cshot("lab3-policy-03-changeset", "Change set", "Changes", "Policy changes")
            ex = g.get_by_role("button", name=re.compile(r"^(Apply change set|Execute)"))
            print("execute buttons:", ex.count())
            if ex.count():
                ex.first.click()
                page.wait_for_timeout(4000)
                h = app()
                cb = h.get_by_role("button", name=re.compile(r"^(Apply|Execute|Confirm)"))
                if cb.count():
                    cb.last.click()
                page.wait_for_timeout(8000)
                cshot("lab3-policy-04-executing", "Change set", "Policy versions", "Changes")
                print("AFTER EXECUTE:", body(app())[:600].replace("\n", " | "))

elif PHASE == "live":
    cshot("lab3-policy-05-live", "Policy versions")

else:
    raise SystemExit(f"unknown CWAN_PHASE {PHASE!r}")
