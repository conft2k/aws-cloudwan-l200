"""Find out how the attachments table lets a column be widened.

    AWS_PROFILE=cwan uv run --with playwright --with boto3 \
        python tools/console.py tools/shots/probe-resizer.py

Throwaway: it prints what it finds and takes no screenshot. Delete it once
tools/shots/cwan-console.py resizes the Name column for real.
"""
import re

NETWORKS = ("https://us-west-2.console.aws.amazon.com"
            "/networkmanager/home?region=us-west-2#/networks")
WAIT = 9000

goto(NETWORKS)
page.wait_for_timeout(WAIT)
f = app()
f.get_by_role("link", name=re.compile(r"^global-network-")).first.click()
page.wait_for_timeout(WAIT)
f = app()
f.get_by_role("link", name="Attachments", exact=True).first.click()
page.wait_for_timeout(WAIT)
f = app()

print("BODY HAS cwan-ws-att:", "cwan-ws-att" in f.locator("body").inner_text())

print("\n--- separators (Cloudscape renders a resize handle per column) ---")
print(f.evaluate("""() => {
  const out = [];
  for (const el of document.querySelectorAll('[role=separator], [class*=resizer], [class*=resize]')) {
    out.push({
      tag: el.tagName,
      role: el.getAttribute('role'),
      cls: (el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className || '').slice(0, 90),
      label: el.getAttribute('aria-label'),
      valuenow: el.getAttribute('aria-valuenow'),
      box: (b => b && {x: Math.round(b.x), y: Math.round(b.y), w: Math.round(b.width), h: Math.round(b.height)})(el.getBoundingClientRect()),
    });
  }
  return out.slice(0, 40);
}"""))

print("\n--- header cells, in order, with their widths ---")
print(f.evaluate("""() => {
  const th = [...document.querySelectorAll('table thead th')];
  return th.map(t => ({
    text: t.innerText.trim().split('\\n')[0].slice(0, 36),
    w: Math.round(t.getBoundingClientRect().width),
    kids: [...t.querySelectorAll('*')].filter(e => /resiz|separator/i.test(
      (e.className && e.className.baseVal !== undefined ? e.className.baseVal : e.className || '') + ' ' + (e.getAttribute('role') || '')
    )).length,
  }));
}"""))

print("\n--- does the table advertise itself as resizable? ---")
print(f.evaluate("""() => {
  const t = document.querySelector('table');
  if (!t) return 'no table';
  let n = t, cls = [];
  for (let i = 0; i < 6 && n; i++, n = n.parentElement) {
    const c = n.className && n.className.baseVal !== undefined ? n.className.baseVal : n.className || '';
    cls.push(String(c).slice(0, 120));
  }
  return cls;
}"""))

# --- the Routes tab: last run could not find its segment / edge pickers ------
print("\n=== Routes tab ===")
f.get_by_role("link", name="Core network", exact=True).first.click()
page.wait_for_timeout(WAIT)
f = app()
f.get_by_role("tab", name="Routes", exact=True).first.click()
page.wait_for_timeout(WAIT)
f = app()

print("ROUTES BODY (first 1200):")
print(f.locator("body").inner_text()[:1200].replace("\n", " | "))

print("\n--- form controls on the Routes tab ---")
print(f.evaluate("""() => {
  const out = [];
  for (const el of document.querySelectorAll('input, select, textarea, button[aria-haspopup], [role=combobox], [role=button]')) {
    const b = el.getBoundingClientRect();
    if (b.width === 0 && b.height === 0) continue;
    out.push({
      tag: el.tagName,
      type: el.getAttribute('type'),
      role: el.getAttribute('role'),
      ph: el.getAttribute('placeholder'),
      label: el.getAttribute('aria-label'),
      text: (el.innerText || '').trim().slice(0, 40),
    });
  }
  return out.slice(0, 30);
}"""))
