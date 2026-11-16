"""What is the last button of the Create stack wizard actually called?

    AWS_PROFILE=demo1 AWS_REGION=ap-northeast-2 \
      CONSOLE_STATE=$HOME/.cache/demo1-probe-console-state.json \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/probe-submit.py

2-1-b step 7 said "Submit"; a run found neither "Submit" nor "Create stack" by
role and name, so the page says something else. Walk to the last step and print
every button, including which one Cloudscape marks as the primary. Stops there:
it never submits. Throwaway probe.
"""
WAIT = 6000
TEMPLATE = str(ROOT / "docs/assets/cloudwan-workshop-oregon.yaml")


def body(f):
    try:
        return f.locator("body").inner_text()
    except Exception:
        return ""


def buttons(f):
    return f.evaluate("""() => [...document.querySelectorAll('button, [role=button]')]
      .filter(e => { const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0; })
      .map(e => ({text: (e.innerText || '').trim().slice(0, 40),
                  label: e.getAttribute('aria-label'),
                  primary: /variant-primary/.test(e.className || ''),
                  cls: String(e.className || '').slice(0, 60)}))""")


def nxt(f, n=1):
    for _ in range(n):
        b = f.get_by_role("button", name="Next", exact=True)
        if not b.count():
            print("!! no Next;", [x['text'] for x in buttons(f)][:25])
            return f
        b.last.click()
        page.wait_for_timeout(WAIT)
        f = app()
    return f


goto(f"/cloudformation/home?region={REGION}#/stacks")
page.wait_for_timeout(WAIT)
f = app()
print("STACKS PAGE buttons:", [b for b in buttons(f) if b["text"]][:18])

cs = f.get_by_role("button", name="Create stack", exact=False)
print("Create stack controls:", cs.count())
cs.last.click()
page.wait_for_timeout(WAIT)
f = app()
print("AFTER CLICK headings:",
      [h.strip() for h in f.get_by_role("heading").all_inner_texts() if h.strip()][:10])
print("menu items:", [m.strip() for m in f.get_by_role("menuitem").all_inner_texts() if m.strip()][:10])

mi = f.get_by_role("menuitem", name="With new resources (standard)")
print("menu item found:", mi.count())
if mi.count():
    mi.first.click()
    page.wait_for_timeout(WAIT)

f = app()
up = f.get_by_role("radio", name="Upload a template file")
if up.count():
    up.first.evaluate("e => e.click()")
    page.wait_for_timeout(1500)
f = app()
f.locator('input[type=file]').first.set_input_files(TEMPLATE)
page.wait_for_timeout(WAIT)

f = nxt(app())
n = f.get_by_role("textbox", name="Stack name")
if n.count():
    n.first.fill("probe-delete-me")
    page.wait_for_timeout(1000)
f = nxt(app(), 2)

print("\n=== LAST STEP ===")
f = app()
print("headings:", [h.strip() for h in f.get_by_role("heading").all_inner_texts() if h.strip()][:14])
for b in buttons(f):
    if b["text"] or b["primary"]:
        print("  ", b)
shot("probe-last-step")
print("\nNOTHING SUBMITTED")
