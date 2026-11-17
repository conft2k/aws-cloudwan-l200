"""2-4-a: the Visual editor route to the same share, shot without creating anything.

    AWS_PROFILE=demo1 AWS_REGION=us-west-2 \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/lab3-visual.py

The page tells the reader to switch to JSON, but the editor opens in Visual
editor and a participant may well stay there. This opens the policy editor on
the LIVE version, goes to Segment actions, and shoots the form that adds a
share.

It never presses Create sharing or Create policy, so no policy version is made.
"""
WAIT = 8000
NETWORKS = ("https://us-west-2.console.aws.amazon.com"
            "/networkmanager/home?region=us-west-2#/networks")


def cookies():
    for name in ("Accept all", "Accept", "Decline all", "Decline"):
        for scope in (page, app()):
            b = scope.get_by_role("button", name=name, exact=True)
            if b.count():
                b.first.click()
                page.wait_for_timeout(1500)
                print(f"쿠키 배너: {name}")
                return


def names(role, f, limit=30):
    try:
        return [t.strip().replace("\n", " / ")[:40]
                for t in f.get_by_role(role).all_inner_texts() if t.strip()][:limit]
    except Exception as e:
        return [f"<{e}>"]


def report(label, f):
    print(f"-- {label}")
    print("   tab:", names("tab", f))
    print("   button:", names("button", f))


goto(NETWORKS)
page.wait_for_timeout(WAIT)
cookies()
close_tours()

f = app()
core = f.get_by_role("link", name=re.compile(r"^core-network-"))
if not core.count():
    raise SystemExit("!! core network 링크를 찾지 못했다")
core.first.click()
page.wait_for_timeout(WAIT)
close_tours()
for _ in range(8):
    f = app()
    if [t for t in f.get_by_role("tab").all_inner_texts() if t.strip()]:
        break
    page.wait_for_timeout(5000)

# Policy versions lives in the left menu, not in the tab strip.
pv = app().get_by_role("link", name="Policy versions", exact=True)
print("Policy versions 링크:", pv.count())
if not pv.count():
    raise SystemExit("!! Policy versions 링크를 찾지 못했다")
pv.first.click()
page.wait_for_timeout(WAIT)

f = app()
report("Policy versions", f)
# select_row() matches on an aria-label; the version rows are labelled by number,
# not by LIVE, so pick the row that carries the LIVE alias and click its radio.
row = f.locator("table tbody tr").filter(has_text=re.compile(r"LIVE"))
print("LIVE 행:", row.count())
if row.count():
    cb = row.first.locator('input[type=radio], input[type=checkbox]')
    print("   선택 입력:", cb.count())
    if cb.count():
        cb.first.evaluate("e => e.click()")
        page.wait_for_timeout(2500)
f = app()
edit = f.get_by_role("button", name="Edit", exact=True)
enabled = edit.count() and edit.first.get_attribute("disabled") is None
print("Edit 버튼:", edit.count(), "| 활성:", enabled)
if not enabled:
    raise SystemExit("!! Edit 가 비활성이다. 행 선택이 되지 않았다")
edit.first.click()
page.wait_for_timeout(WAIT)

f = app()
report("정책 편집기", f)
print("   heading:", names("heading", f, 8))
shot("lab3-policy-06-visual-editor", clip=card("Visual editor", frame=f))

seg = f.get_by_role("tab", name=re.compile(r"Segment actions"))
print("Segment actions 탭:", seg.count())
if not seg.count():
    raise SystemExit("!! Segment actions 탭이 없다")
seg.first.click()
page.wait_for_timeout(4000)

f = app()
report("Segment actions 탭", f)
shot("lab3-policy-07-visual-sharing", clip=card("Sharing", frame=f))

# The button is called just "Create", and this tab has three of them - one per
# panel (Sharing, static routes, routing policy associations). Try each and keep
# the dialog whose title is about sharing; cancel the others.
create = f.get_by_role("button", name=re.compile(r"^Create$"))
print("Create 버튼:", create.count())
g = None
for i in range(create.count()):
    create.nth(i).click()
    page.wait_for_timeout(4000)
    h = app()
    titles = [t.strip() for t in h.get_by_role("heading").all_inner_texts() if t.strip()]
    print(f"   Create #{i} -> 제목 {titles[:4]}")
    if any("sharing" in t.lower() for t in titles):
        g = h
        break
    c = h.get_by_role("button", name="Cancel", exact=True)
    if c.count():
        c.last.click()
        page.wait_for_timeout(2500)
    f = app()
    create = f.get_by_role("button", name=re.compile(r"^Create$"))

if g is None:
    raise SystemExit("!! sharing 창을 여는 Create 를 찾지 못했다")

print("대화상자:", g.get_by_role("dialog").count())
report("Create sharing 창", g)
print("   라디오:", names("radio", g, 8))
dlg = g.get_by_role("dialog")
shot("lab3-policy-08-visual-create-sharing", clip=dlg.last if dlg.count() else None)

# Leave without creating anything.
cancel = g.get_by_role("button", name="Cancel", exact=True)
print("Cancel:", cancel.count())
if cancel.count():
    cancel.last.click()
    page.wait_for_timeout(2500)
print("아무것도 만들지 않고 닫았다")
