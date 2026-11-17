"""R6: does 2-2-d really need the Region switched to Oregon?

    AWS_PROFILE=demo1 AWS_REGION=ap-northeast-2 \
      uv run --with playwright --with boto3 python tools/console.py \
      tools/shots/probe-region-nav.py

With the Region left on Seoul, open Create attachment, pick VPC and the Oregon
edge location, and print the VPC dropdown's options. If Oregon VPCs are listed
from Seoul, step 1 of 2-2-d is unnecessary. The form is never submitted.
"""
WAIT = 7000

def cookies():
    """The cookie banner sits over the left menu until it is answered."""
    for name in ("Accept all", "Accept", "Decline all", "Decline"):
        b = page.get_by_role("button", name=name, exact=True)
        if b.count():
            b.first.click()
            page.wait_for_timeout(1500)
            print(f"쿠키 배너: {name} 누름")
            return


goto(f"/networkmanager/home?region={REGION}#/networks")
page.wait_for_timeout(WAIT)
cookies()
close_tours()
page.wait_for_timeout(1500)
f = app()
f.get_by_role("link", name=re.compile(r"^global-network-")).first.click()
page.wait_for_timeout(WAIT)
cookies()
close_tours()
expand_nav()
page.wait_for_timeout(3000)
f = app()
print("왼쪽 메뉴:", [t.strip() for t in f.get_by_role("link").all_inner_texts() if t.strip()][:30])

for name in ("Core network", "Attachments"):
    link = f.get_by_role("link", name=name, exact=True)
    print(f"{name}: {link.count()}")
    if link.count():
        link.first.click()
        page.wait_for_timeout(WAIT)
        f = app()

btn = f.get_by_role("button", name="Create attachment", exact=True)
print("Create attachment 버튼:", btn.count())
if not btn.count():
    print("버튼 목록:", [t.strip()[:30] for t in f.locator("button").all_inner_texts() if t.strip()][:20])
else:
    btn.first.click()
    page.wait_for_timeout(WAIT)
    f = app()
    print("폼 제목:", [t.strip() for t in f.get_by_role("heading").all_inner_texts() if t.strip()][:5])
    print("리전 표시:", page.locator('button[aria-label*="Regions"]').first.inner_text().strip())

    def pick(label, want):
        """Open the dropdown next to <label> and click the option matching <want>."""
        trig = f.locator(f'//*[self::label or self::span][contains(text(), "{label}")]'
                         f'/following::button[@aria-expanded][1]')
        print(f"  {label}: trigger {trig.count()}", trig.first.inner_text().strip() if trig.count() else "")
        if not trig.count():
            return False
        trig.first.click()
        page.wait_for_timeout(2500)
        g = app()
        opts = g.get_by_role("option")
        texts = [o.strip() for o in opts.all_inner_texts() if o.strip()]
        print(f"    선택지 {len(texts)}:", texts[:12])
        hit = g.get_by_role("option", name=re.compile(want))
        if hit.count():
            hit.first.click()
            page.wait_for_timeout(3000)
            return True
        page.keyboard.press("Escape")
        return False

    pick("Attachment type", r"^VPC$")
    f = app()
    pick("Edge location", r"Oregon")
    f = app()
    print("\n-- 리전을 서울에 둔 채 VPC 드롭다운에 무엇이 나오는가")
    pick("VPC", r"__never__")
