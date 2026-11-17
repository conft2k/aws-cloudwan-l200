"""3-3-e: the Events tab once events have arrived.

    CWAN_GN=global-network-... AWS_PROFILE=demo1 AWS_REGION=us-west-2 \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/extra-events-list.py

Run it while the log has something in it - deleting an attachment or executing a
change set produces events within a minute.

The events table is NOT in the Network Manager page: the tab embeds a CloudWatch
dashboard widget in its own iframe, which is why looking for the table in the
main frame finds nothing however long you wait. This walks into that frame and
clips the shot to the iframe element.

Read-only: it opens the tab, shoots the list, expands one row and shoots that.
"""
import os

GN = os.environ.get("CWAN_GN", "")
WAIT = 8000


def cookies():
    for name in ("Accept all", "Accept", "Decline all", "Decline"):
        for scope in (page, app()):
            b = scope.get_by_role("button", name=name, exact=True)
            if b.count():
                b.first.click()
                page.wait_for_timeout(1500)
                print(f"쿠키 배너: {name}")
                return


def widget():
    """The frame holding the embedded CloudWatch dashboard, and its iframe box."""
    for fr in page.frames:
        if "cloudwatch/dashboard" in (fr.url or ""):
            try:
                return fr, fr.frame_element().bounding_box()
            except Exception:
                return fr, None
    return None, None


if GN:
    goto("https://us-west-2.console.aws.amazon.com/networkmanager/home"
         f"?region=us-west-2#/networks/{GN}/corenetwork/events")
else:
    goto("https://us-west-2.console.aws.amazon.com"
         "/networkmanager/home?region=us-west-2#/networks")
    page.wait_for_timeout(WAIT)
    cookies()
    close_tours()
    core = app().get_by_role("link", name=re.compile(r"^core-network-"))
    if not core.count():
        raise SystemExit("!! core network 링크를 찾지 못했다")
    core.first.click()
    page.wait_for_timeout(WAIT)
    close_tours()
    for _ in range(8):
        if [t for t in app().get_by_role("tab").all_inner_texts() if t.strip()]:
            break
        page.wait_for_timeout(5000)
    tab = app().get_by_role("tab", name="Events", exact=True)
    if not tab.count():
        raise SystemExit("!! Events 탭이 없다")
    tab.first.click()

page.wait_for_timeout(WAIT)
cookies()
close_tours()

# The rows are not reachable as `tbody tr` from the widget frame - whatever the
# grid renders them as, the text is what to wait for.
READY = re.compile(r"(have been uninstalled|Core Network policy)")
fr = None
for attempt in range(14):
    fr, box = widget()
    seen = False
    for f2 in page.frames:
        try:
            if READY.search(f2.locator("body").inner_text()):
                seen = True
                break
        except Exception:
            pass
    print(f"   위젯 프레임 {'있음' if fr else '없음'} | 이벤트 글자 {'보임' if seen else '아직'}"
          f" (시도 {attempt + 1}/14)")
    if fr is not None and seen:
        break
    page.wait_for_timeout(5000)

if fr is None:
    print("!! 위젯 프레임을 찾지 못했다")
    shot("extraC-06-events-list")
    raise SystemExit(1)

fr, box = widget()
print("   위젯 박스:", box)
if box is None:
    print("!! 위젯 위치를 재지 못했다")
    shot("extraC-06-events-list")
    raise SystemExit(1)
clip = (box["x"], box["y"], box["x"] + box["width"], box["y"] + min(box["height"], 430))
shot("extraC-06-events-list", clip=clip)

# The first row's disclosure triangle. Scope it to the row - a page-wide button
# search hits the time-range buttons in the toolbar instead, which silently
# changes the range to 1h.
row1 = fr.get_by_role("row").nth(1)
btns = row1.get_by_role("button")
print("1행 안의 버튼:", btns.count(),
      [btns.nth(i).get_attribute("aria-label") for i in range(min(btns.count(), 3))])
if btns.count():
    btns.first.click()
    page.wait_for_timeout(4000)
    fr, box = widget()
    clip = (box["x"], box["y"], box["x"] + box["width"], box["y"] + min(box["height"], 600))
    shot("extraC-07-events-detail", clip=clip)
else:
    print("!! 행을 펼치는 버튼을 찾지 못했다")
