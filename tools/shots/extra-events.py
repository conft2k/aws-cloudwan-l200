"""3-3-e: turn the core network's Events tab on, shooting what the console asks.

    AWS_PROFILE=demo1 AWS_REGION=us-west-2 \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/extra-events.py

The tab is off until someone onboards it, and the console then creates an
EventBridge rule and a CloudWatch Logs group in us-west-2 (that is where Cloud
WAN publishes its events). This walks that path so 3-3-e can name the buttons
and say what appears after each one.

It really creates those resources. Delete them again afterwards:

    aws events remove-targets --rule DON_NOT_DELETE_networkmanager_rule --ids 121 \
      --profile demo1 --region us-west-2
    aws events delete-rule --name DON_NOT_DELETE_networkmanager_rule \
      --profile demo1 --region us-west-2
    aws logs delete-log-group --log-group-name /aws/events/networkmanagerloggroup \
      --profile demo1 --region us-west-2
    aws logs delete-resource-policy \
      --policy-name DON_NOT_DELETE_networkmanager_TrustEventsToStoreLogEvents \
      --profile demo1 --region us-west-2
"""
WAIT = 8000
NETWORKS = ("https://us-west-2.console.aws.amazon.com"
            "/networkmanager/home?region=us-west-2#/networks")


def cookies():
    """The cookie banner sits over the left menu until it is answered."""
    for name in ("Accept all", "Accept", "Decline all", "Decline"):
        for scope in (page, app()):
            b = scope.get_by_role("button", name=name, exact=True)
            if b.count():
                b.first.click()
                page.wait_for_timeout(1500)
                print(f"쿠키 배너: {name}")
                return


def heads(f):
    try:
        return [h.strip() for h in f.get_by_role("heading").all_inner_texts() if h.strip()][:12]
    except Exception:
        return []


def report(label, f):
    print(f"-- {label}")
    print("   headings:", heads(f))
    print("   본문:", " | ".join(t for t in body(f)[:800].split("\n") if t.strip()))
    print("   버튼:", [t.strip()[:30] for t in f.locator("button").all_inner_texts() if t.strip()][:24])


goto(NETWORKS)
page.wait_for_timeout(WAIT)
cookies()
close_tours()

# The Global networks table has a column of core network ids. That link is the
# way into the core network; the global network's own page has only Overview,
# Details and the two topology tabs.
f = app()
core = f.get_by_role("link", name=re.compile(r"^core-network-"))
print("core network 링크:", core.count())
if not core.count():
    raise SystemExit("!! Global networks 목록에서 core network 링크를 찾지 못했다")
core.first.click()
page.wait_for_timeout(WAIT)
close_tours()

# The core network page loads its tabs late - wait for them instead of guessing.
for attempt in range(8):
    f = app()
    tabs = [t.strip() for t in f.get_by_role("tab").all_inner_texts() if t.strip()]
    if tabs:
        break
    print(f"   탭을 기다리는 중 {attempt + 1}/8  URL={page.url[:90]}")
    page.wait_for_timeout(5000)
print("core network 탭:", tabs)
print("본문 앞부분:", " | ".join(t for t in body(f)[:300].split("\n") if t.strip()))
tab = f.get_by_role("tab", name="Events", exact=True)
if not tab.count():
    tab = f.get_by_role("link", name="Events", exact=True)
print("Events 탭/링크:", tab.count())
if not tab.count():
    raise SystemExit("!! Events 탭을 찾지 못했다")
tab.first.click()
page.wait_for_timeout(WAIT)

f = app()
report("Events 탭 (켜기 전)", f)
# The off state is a callout with no heading, so card() cannot find it. Clip to
# the alert box itself; print which locator matched so the next run knows.
off = None
for how, loc in (("role=alert", lambda: f.get_by_role("alert")),
                 ("text ancestor", lambda: f.get_by_text("Unable to show events")
                  .locator("xpath=ancestor::div[.//button][1]")),
                 ("awsui alert", lambda: f.locator('div[class*="awsui_root"][class*="alert"]'))):
    l = loc()
    n = l.count()
    print(f"   꺼진 상태 상자 {how}: {n}")
    if n and off is None:
        off = l.first
        print(f"   -> {how!r} 로 자른다")
shot("extraC-04-events-off", clip=off)

btn = f.get_by_role("button", name=re.compile(r"Onboard"))
print("Onboard 버튼:", btn.count(),
      btn.first.inner_text().strip() if btn.count() else "")
if not btn.count():
    raise SystemExit("!! Onboard 버튼이 없다. 이미 켜져 있는지 확인하라")

btn.first.click()
page.wait_for_timeout(9000)
g = app()
print("대화상자:", g.get_by_role("dialog").count(), "(없으면 확인 창 없이 바로 적용된 것)")
report("Onboard 를 누른 뒤", g)
shot("extraC-05-events-on", clip=card("Events", frame=g))

# Whatever the next control is called, print it before touching anything.
for name in ("Onboard", "Enable", "Confirm", "Submit", "Save", "Continue"):
    c = g.get_by_role("button", name=re.compile(rf"^{name}"))
    if c.count():
        print(f"   다음 버튼 후보: {name!r} x{c.count()} -> {c.first.inner_text().strip()!r}")

print("\n여기까지가 1차 확인이다. 다음 버튼을 실제로 누를지는 로그를 보고 정한다.")
