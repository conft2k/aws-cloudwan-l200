"""How does one open an attachment and read its segment tag?

    AWS_PROFILE=cwan uv run --with playwright --with boto3 \
        python tools/console.py tools/shots/probe-attachment-detail.py

The attachments table has no link in its rows (`row links: []`), so lab1 2-2-a
step 5 - "open an attachment and look at Tags" - may not describe a real path.
Find out what Actions offers once a row is selected, and shoot the tags screen
if there is one. Throwaway probe; delete once 2-2-a says the verified steps.
"""
import re

NETWORKS = ("https://us-west-2.console.aws.amazon.com"
            "/networkmanager/home?region=us-west-2#/networks")
WAIT = 8000

goto(NETWORKS)
page.wait_for_timeout(WAIT)
app().get_by_role("link", name=re.compile(r"^global-network-")).first.click()
page.wait_for_timeout(WAIT)
app().get_by_role("link", name="Attachments", exact=True).first.click()
page.wait_for_timeout(WAIT)

f = app()
print("rows:", f.locator("table tbody tr").count())
print("row 1 cells:", [c.strip()[:30] for c in
                       f.locator("table tbody tr").first.locator("td").all_inner_texts()])

# the selection control's aria-label is the attachment id, which select_row()
# uses; find the id of the Seoul prod row first
rid = f.locator('table tbody tr').filter(has_text="cwan-ws-att-prod-apne2") \
       .first.locator('label[aria-label^="attachment-"]').get_attribute("aria-label")
print("seoul prod attachment id:", rid)

print("select_row ->", select_row(rid))

f = app()
acts = f.get_by_role("button", name="Actions", exact=True)
print("Actions button:", acts.count())
if acts.count():
    acts.first.click()
    page.wait_for_timeout(2500)
    f = app()
    items = [t.strip() for t in f.get_by_role("menuitem").all_inner_texts() if t.strip()]
    print("ACTIONS MENU:", items)
    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)

# does clicking the row itself (not a link) open a detail panel?
f = app()
before = page.url
f.locator("table tbody tr").filter(has_text="cwan-ws-att-prod-apne2") \
 .first.locator("td").nth(1).click()
page.wait_for_timeout(WAIT)
print("url changed:", page.url != before, "->", page.url[-90:])
f = app()
t = f.locator("body").inner_text()
print("page mentions Tags tab:", "Tags" in t, "| segment:", "segment" in t)
print("tabs now:", [x.strip() for x in f.get_by_role("tab").all_inner_texts() if x.strip()])
