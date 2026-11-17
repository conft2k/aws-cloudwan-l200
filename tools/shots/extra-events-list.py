"""3-3-e: the Events tab once events have arrived.

    AWS_PROFILE=demo1 AWS_REGION=us-west-2 \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/extra-events-list.py

Run it while the log has something in it - deleting an attachment or executing a
change set produces events within a minute. Read-only: it opens the tab, shoots
the list, expands one row and shoots that. Nothing is created or deleted.
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

tab = app().get_by_role("tab", name="Events", exact=True)
print("Events 탭:", tab.count())
if not tab.count():
    raise SystemExit("!! Events 탭이 없다")
tab.first.click()
page.wait_for_timeout(WAIT)

# The panel runs a Logs Insights query, so the rows arrive late. Do not touch the
# range buttons - clicking one opens a custom-range popover whose own table looks
# like rows. Find the events table by its Message column and wait for that.
TABLE = 'table:has(th:text-is("Message"))'
rows = None
for attempt in range(12):
    f = app()
    rows = f.locator(f"{TABLE} tbody tr")
    n = rows.count()
    txt = body(f)
    state = ("No data found" if "No data found" in txt else "?")
    print(f"   이벤트 행 {n} | 패널 상태 {state} (시도 {attempt + 1}/12)")
    if n:
        break
    if attempt == 3:
        r = f.get_by_role("button", name=re.compile(r"[Rr]efresh"))
        print("   새로 고침 버튼:", r.count())
        if r.count():
            r.first.click()
    page.wait_for_timeout(5000)

f = app()
if not rows.count():
    print("!! 이벤트가 아직 없다. 기간 선택(1h/12h)과 로그 그룹을 확인하라")
    shot("extraC-06-events-list")
    raise SystemExit(1)

print("첫 행:", rows.first.inner_text().replace("\n", " | ")[:120])
panel = f.locator(TABLE).locator("xpath=ancestor::div[3]")
print("   패널:", panel.count(), panel.first.bounding_box() if panel.count() else None)
shot("extraC-06-events-list", clip=panel.first if panel.count() else None)

# Expand one row to show the fields a single event carries.
tog = rows.first.locator('button[aria-label], [role=button]')
print("행 안의 버튼:", tog.count(),
      [tog.nth(i).get_attribute("aria-label") for i in range(min(tog.count(), 4))])
if tog.count():
    tog.first.click()
    page.wait_for_timeout(3500)
    g = app()
    print("펼친 뒤 첫 행:", g.locator("table tbody tr").first.inner_text()
          .replace("\n", " | ")[:200])
    gp = g.locator(TABLE).locator("xpath=ancestor::div[3]")
    shot("extraC-07-events-detail", clip=gp.first if gp.count() else None)
else:
    print("!! 행을 펼치는 버튼을 찾지 못했다")
