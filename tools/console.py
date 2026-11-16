"""Drive the AWS console (English) for rehearsal and screenshots.

    uv run --with playwright --with boto3 python tools/console.py <script.py>

The script file is executed with `page`, `shot(name)`, `goto(path)` and
`mask()` in scope. Login: GetFederationToken for the IAM user of
$AWS_PROFILE, then a federation sign-in URL. The browser storage state is kept
in $CONSOLE_STATE (default: a file outside the repo) so later runs reuse the
session. Screenshots go to docs/images/console/<name>.png with the account ID
replaced by 111122223333.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import boto3
from playwright.sync_api import sync_playwright

PROFILE = os.environ.get("AWS_PROFILE", "sandbox")
REGION = os.environ.get("AWS_REGION", "ap-northeast-2")
STATE = Path(os.environ.get("CONSOLE_STATE", Path.home() / ".cache/cwan-console-state.json"))


def _viewport():
    """Window size. Widen it ($CONSOLE_VIEWPORT=1920x1080) when a console table
    truncates the column the page needs to show, such as an attachment name."""
    v = os.environ.get("CONSOLE_VIEWPORT", "1440x900").lower().split("x")
    return int(v[0]), int(v[1])


VIEWPORT = _viewport()
ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "docs/images/console"
FAKE = "111122223333"
# The console prints the signed-in identity in the top-right of every page, and
# with IAM Identity Center that is a real email address. It is not the account
# ID, so the account mask below never touches it, and it ends up in every shot
# these pages publish. Rewrite any address to this one instead.
FAKE_EMAIL = os.environ.get("CONSOLE_FAKE_EMAIL", "participant@example.com")


def signin_url() -> str:
    """Build a console sign-in URL for $AWS_PROFILE.

    GetFederationToken cannot be called with role credentials, so when the
    profile resolves to an assumed role (IAM Identity Center, AssumeRole) the
    session credentials are handed to the federation endpoint directly. In that
    case SessionDuration must be omitted: the role's own expiry applies.
    """
    s = boto3.Session(profile_name=PROFILE, region_name=REGION)
    ident = s.client("sts").get_caller_identity()
    account = ident["Account"]
    is_role = ":assumed-role/" in ident["Arn"]
    if is_role:
        c = s.get_credentials().get_frozen_credentials()
        session = json.dumps({"sessionId": c.access_key, "sessionKey": c.secret_key,
                              "sessionToken": c.token})
        q = urllib.parse.urlencode({"Action": "getSigninToken", "Session": session})
    else:
        policy = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}
        creds = s.client("sts").get_federation_token(
            Name="workshop-user", Policy=json.dumps(policy), DurationSeconds=43200)["Credentials"]
        session = json.dumps({"sessionId": creds["AccessKeyId"], "sessionKey": creds["SecretAccessKey"],
                              "sessionToken": creds["SessionToken"]})
        q = urllib.parse.urlencode({"Action": "getSigninToken", "SessionDuration": 43200, "Session": session})
    token = json.load(urllib.request.urlopen(f"https://signin.aws.amazon.com/federation?{q}"))["SigninToken"]
    dest = f"https://{REGION}.console.aws.amazon.com/console/home?region={REGION}"
    q = urllib.parse.urlencode({"Action": "login", "Issuer": "cwan-workshop", "Destination": dest,
                                "SigninToken": token})
    os.environ["CWAN_ACCOUNT"] = account
    return f"https://signin.aws.amazon.com/federation?{q}"


def resolve_account() -> str:
    """Account ID for masking. $CWAN_ACCOUNT wins, so a run can reuse a live
    browser session (in $CONSOLE_STATE) after the profile's credentials expire."""
    env = os.environ.get("CWAN_ACCOUNT", "").strip()
    if env:
        return env
    return boto3.Session(profile_name=PROFILE).client("sts").get_caller_identity()["Account"]


def main() -> int:
    script = Path(sys.argv[1]).read_text()
    account = resolve_account()
    dashed = f"{account[:4]}-{account[4:8]}-{account[8:]}"
    SHOTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        vw, vh = VIEWPORT
        ctx_args = {"viewport": {"width": vw, "height": vh}, "locale": "en-US",
                    "device_scale_factor": 1}
        if STATE.exists():
            ctx_args["storage_state"] = str(STATE)
        ctx = browser.new_context(**ctx_args)
        page = ctx.new_page()
        # A failed selector should cost seconds, not the 30-45s default: a
        # console run makes dozens of guesses and the waits dominate it.
        page.set_default_timeout(15000)

        cur = {"page": page}

        def P():
            return cur["page"]

        def use(p):
            """Point goto/shot/mask at another tab (e.g. the EC2 Instance Connect terminal)."""
            cur["page"] = p

        def goto(path: str):
            url = path if path.startswith("http") else f"https://{REGION}.console.aws.amazon.com{path}"
            P().goto(url, wait_until="domcontentloaded")
            if "signin.aws.amazon.com" in P().url or "/oauth" in P().url:
                P().goto(signin_url(), wait_until="domcontentloaded")
                P().wait_for_url(re.compile(r".*console\.aws\.amazon\.com.*"), timeout=60000)
                P().goto(url, wait_until="domcontentloaded")
            P().wait_for_load_state("load", timeout=60000)
            P().wait_for_timeout(4000)  # the console keeps polling; never networkidle
            close_tours()
            expand_nav()

        def expand_nav():
            """Unfold the service's left navigation.

            A folded nav is remembered in storage_state, so a later run finds no
            nav links at all and every nav() click times out. Call it before
            navigating; collapse_nav() is for the moment of the screenshot only.
            """
            for frame in frames():
                for sel in ('button[aria-label="Open side navigation"]',
                            '[aria-label="Open side navigation"]'):
                    try:
                        b = frame.locator(sel)
                        if b.count() and b.first.is_visible():
                            b.first.click(timeout=3000)
                            P().wait_for_timeout(1500)
                            return True
                    except Exception:
                        pass
            return False

        def close_tours():
            # The cookie consent banner covers the bottom of the window, which is
            # where wizards put Next and Create. A fresh account always gets it,
            # and its button is "Accept" in some builds, "Accept all cookies" in
            # others, so try the ids first and then the text inside the dialog.
            for sel in ('button[aria-label="Accept all cookies"]',
                        "#awsccc-cb-btn-accept",
                        '[data-id="awsccc-cb-btn-accept"]',
                        '#awsccc-sb-ux-c button[data-id*="accept"]'):
                try:
                    b = P().locator(sel)
                    if b.count() and b.first.is_visible():
                        b.first.click(timeout=3000)
                        P().wait_for_timeout(800)
                except Exception:
                    pass
            try:
                box = P().locator('#awsccc-sb-ux-c, [data-id="awsccc-sb-ux-c"]')
                if box.count() and box.first.is_visible():
                    acc = box.first.get_by_role("button", name=re.compile(r"^Accept"))
                    if acc.count():
                        acc.first.click(timeout=3000)
                        P().wait_for_timeout(800)
            except Exception:
                pass
            # first-visit console tours ("Service menu" etc.) and info banners
            for _ in range(6):
                t = P().locator('[data-testid^="awsc-nav-services-tooltip"] button, [data-testid*="tooltip-confirm"]')
                vis = [x for x in t.all() if x.is_visible()]
                if not vis:
                    break
                vis[-1].click(timeout=3000)
                P().wait_for_timeout(500)
            for x in P().get_by_role("button", name=re.compile(r"^(Dismiss|Close)( notification)?$")).all():
                try:
                    if x.is_visible():
                        x.click(timeout=2000)
                except Exception:
                    pass

        def frames():
            return [f for f in P().frames if not f.is_detached()]

        def app():
            # the frame that holds the console page body (VPC console uses an iframe)
            best, size = P().main_frame, -1
            for f in frames():
                if "lotus/" in f.url or "continuum." in f.url:
                    continue  # console nav / search widgets
                try:
                    n = len(f.locator("body").inner_text(timeout=3000))
                except Exception:
                    continue
                if f is not P().main_frame and n > size:
                    best, size = f, n
            return best if size > 200 else P().main_frame

        def all_text():
            out = []
            for f in frames():
                try:
                    out.append(f.locator("body").inner_text(timeout=3000))
                except Exception:
                    pass
            return "\n".join(out)

        def mask():
            for f in frames():
                try:
                    mask_frame(f)
                except Exception:
                    pass
            digits = re.sub(r"[\s\-\u00a0]", "", all_text())
            if account in digits:
                raise RuntimeError("account ID still visible on the page; screenshot refused")
            left = [a for a in re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", all_text())
                    if a != FAKE_EMAIL]
            if left:
                raise RuntimeError(f"email still visible on the page {left[:3]}; screenshot refused")

        def mask_frame(frame):
            # account ID in any spacing (plain, dashed, split across spans) -> FAKE,
            # and any email address (the signed-in identity) -> FAKE_EMAIL
            frame.evaluate(
                """([a, f, fe]) => {
                  const re = new RegExp(a.split('').join('[\\s\\-\\u00a0]?'), 'g');
                  const mail = /[\\w.+-]+@[\\w-]+\\.[\\w.-]+/g;
                  // the bucket CloudFormation makes for uploaded templates is
                  // named from the account; the upload screen prints its URL
                  const bucket = /cf-templates-[a-z0-9]+-/g;
                  const fd = f.slice(0,4)+'-'+f.slice(4,8)+'-'+f.slice(8);
                  const reset = () => { re.lastIndex = 0; mail.lastIndex = 0; bucket.lastIndex = 0; };
                  const sub = (s) => {
                    reset();
                    s = s.replace(re, m => m.includes('-') ? fd : f);
                    reset();
                    s = s.replace(mail, fe);
                    reset();
                    return s.replace(bucket, 'cf-templates-example-');
                  };
                  const hit = (s) => {
                    reset();
                    const r = re.test(s) || mail.test(s) || bucket.test(s);
                    reset();
                    return r;
                  };
                  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                  let n; while ((n = w.nextNode())) {
                    if (hit(n.nodeValue)) n.nodeValue = sub(n.nodeValue);
                  }
                  for (const el of document.querySelectorAll('input, textarea')) {
                    if (el.value && hit(el.value)) el.value = sub(el.value);
                  }
                }""",
                [account, FAKE, FAKE_EMAIL])

        secrets = [x for x in os.environ.get("CONSOLE_SECRETS", "").split(",") if x]

        def mask_secrets():
            if secrets:
              for fr in frames():
               try:
                fr.evaluate(
                    """(ss) => {
                      const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                      let n; while ((n = w.nextNode())) for (const s of ss)
                        if (n.nodeValue.includes(s)) n.nodeValue = n.nodeValue.split(s).join('(hidden)');
                      for (const el of document.querySelectorAll('input, textarea')) for (const s of ss)
                        if (el.value.includes(s)) el.value = el.value.split(s).join('(hidden)');
                    }""", secrets)
               except Exception:
                pass
              if any(x in all_text() for x in secrets):
                    raise RuntimeError("secret still visible on the page; screenshot refused")

        def collapse_nav():
            """Fold the service's left navigation away. A console table steals the
            space, so a truncated column ("cwan-ws-a...") becomes readable."""
            for frame in frames():
                for sel in ('button[aria-label="Close side navigation"]',
                            '[aria-label="Close side navigation"]'):
                    try:
                        b = frame.locator(sel)
                        if b.count() and b.first.is_visible():
                            b.first.click(timeout=3000)
                            P().wait_for_timeout(1500)
                            return True
                    except Exception:
                        pass
            return False

        def table_columns(hide=(), wrap=None, page_size=None, frame=None):
            """Trim a console table through its Preferences (gear) dialog.

            Console tables show every column and truncate the useful ones
            ("cwan-ws-a..."). Hiding the columns a page does not need beats
            widening the window. Names are as the dialog lists them, e.g.
            "Account ID", "Network function groups", "NAT gateway support".
            """
            f = frame if frame is not None else app()
            # name="Preferences" also matches "Customize cookie preferences",
            # so address the gear by its exact aria-label
            gear = f.locator('button[aria-label="Preferences"]')
            if not gear.count():
                gear = f.get_by_role("button", name="Preferences", exact=True)
            if not gear.count():
                print("!! table_columns: no Preferences button")
                return False
            gear.last.click()
            P().wait_for_timeout(2500)
            f = app()
            # the cookie-consent modal also has role=dialog, so match on content
            dlg = f.get_by_role("dialog").filter(has_text="Select visible columns")
            if not dlg.count():
                print("!! table_columns: preferences dialog did not open")
                return False
            dlg = dlg.last
            for name in hide:
                cb = dlg.get_by_role("checkbox", name=name, exact=True)
                if not cb.count():
                    print(f"!! table_columns: no column {name!r}")
                    continue
                try:
                    if cb.first.is_checked():
                        cb.first.evaluate("e => e.click()")  # the input is visually hidden
                        P().wait_for_timeout(250)
                except Exception as e:
                    print(f"!! table_columns: {name!r}: {e}")
            if wrap is not None:
                cb = dlg.get_by_role("checkbox", name="Wrap lines", exact=True)
                if cb.count() and cb.first.is_checked() != wrap:
                    cb.first.evaluate("e => e.click()")
            if page_size:
                r = dlg.get_by_role("radio", name=re.compile(rf"^{page_size}\b"))
                if r.count():
                    r.first.evaluate("e => e.click()")
            dlg.get_by_role("button", name="Confirm", exact=True).first.click()
            P().wait_for_timeout(3000)
            return True

        def card(heading: str, frame=None, exact: bool = False):
            """The panel that holds `heading`, to pass to shot(clip=...).

            A full console window is mostly chrome: the service navigation, the
            top bar, the footer and a lot of empty space. A workshop page wants
            the one panel its text is talking about, so crop to the Cloudscape
            container (header, controls and body) around that heading.

            Returns a locator, or None when the heading is not on the page - the
            caller should then shoot the whole window rather than nothing.
            """
            f = frame if frame is not None else app()
            h = f.get_by_role("heading", name=heading, exact=exact)
            if not h.count():
                print(f"!! card: no heading {heading!r}")
                return None
            box = h.first.locator(
                "xpath=ancestor::div[contains(@class,'awsui_variant-default')"
                " or contains(@class,'awsui_variant-container')][1]")
            if box.count():
                return box.first
            # Wizard steps (CloudFormation's "Specify stack details",
            # "Capabilities") are not Container components, so they have no
            # variant class. Climb to the first ancestor wide enough to be the
            # section rather than the heading's own wrapper.
            wide = h.first.locator("xpath=ancestor::div[contains(@class,'awsui_')]")
            for i in range(wide.count()):
                bb = wide.nth(wide.count() - 1 - i).bounding_box()
                if bb and bb["width"] >= 400 and bb["height"] >= 80:
                    return wide.nth(wide.count() - 1 - i)
            print(f"!! card: {heading!r} has no container ancestor")
            return None

        def span(*locators, margin: int = 16):
            """A clip box covering several panels, for shot(clip=...).

            Some steps read two panels together - the Routes tab's filter says
            which segment the table below belongs to, so cropping to the table
            alone drops the thing that makes it meaningful.
            """
            boxes = [l.bounding_box() for l in locators if l is not None]
            boxes = [b for b in boxes if b]
            if not boxes:
                return None
            vw = P().viewport_size
            return (max(0, min(b["x"] for b in boxes) - margin),
                    max(0, min(b["y"] for b in boxes) - margin),
                    min(vw["width"], max(b["x"] + b["width"] for b in boxes) + margin),
                    min(vw["height"], max(b["y"] + b["height"] for b in boxes) + margin))

        def resize_column(header: str, width: int, frame=None):
            """Widen one column of a console table by dragging its resize handle.

            Console tables are `table-layout: fixed` with every column at 168px,
            so a long value truncates ("cwan-ws-att...") however wide the window
            is. Hiding other columns with table_columns() does NOT help: the
            freed space is left blank and the remaining columns stay at 168px.
            Each header carries its own handle (button.awsui_resizer_*) on its
            right edge; drag that.

            Widening past the container makes the table scroll sideways and the
            last columns fall out of the shot, so hide what the page does not
            need first, then spend the space this frees on `header`.
            """
            f = frame if frame is not None else app()
            ths = f.locator("table thead th")
            idx, total = None, ths.count()
            for i in range(total):
                try:
                    t = ths.nth(i).inner_text().strip().split("\n")[0]
                except Exception:
                    continue
                if t == header:
                    idx = i
                    break
            if idx is None:
                print(f"!! resize_column: no column {header!r}")
                return False
            th = ths.nth(idx)
            grip = th.locator("button[class*='awsui_resizer']")
            if not grip.count():
                print(f"!! resize_column: {header!r} has no resize handle")
                return False
            bb, cell = grip.first.bounding_box(), th.bounding_box()
            if not bb or not cell:
                print(f"!! resize_column: {header!r} is not on screen")
                return False
            x, y = bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2
            P().mouse.move(x, y)
            P().mouse.down()
            P().mouse.move(x + (width - cell["width"]), y, steps=12)
            P().mouse.up()
            P().wait_for_timeout(1200)
            got = app().locator("table thead th").nth(idx).bounding_box()
            print(f"resize_column({header!r}) {round(cell['width'])} ->"
                  f" {round(got['width']) if got else '?'} (asked {width})")
            return True

        def select_row(name: str, frame=None):
            """Tick a Cloudscape table row by its visible label.

            The control is an <input type=checkbox> even where the table is
            single-select and the console paints a radio; its aria-label is the
            row's first column. The input is visually hidden, so click() reports
            "element is not visible" - click the <label> that wraps it instead.
            """
            f = frame if frame is not None else app()
            lab = f.locator(f'label[aria-label="{name}"]')
            if not lab.count():
                print(f"!! select_row: no row labelled {name!r}")
                return False
            lab.first.click(timeout=10000)
            P().wait_for_timeout(1500)
            try:
                ok = f.locator(f'input[aria-label="{name}"]').first.is_checked()
            except Exception:
                ok = False
            print(f"select_row({name!r}) -> {ok}")
            return ok

        def shot(name: str, locator=None, clip=None, margin: int = 16):
            """Full-window original to shots/raw, cropped (clip locator or box) to docs/images."""
            mask()
            mask_secrets()
            path = SHOTS / f"{name}.png"
            raw = ROOT / "shots/raw/console" / f"{name}.png"
            raw.parent.mkdir(parents=True, exist_ok=True)
            if locator is not None:
                locator.scroll_into_view_if_needed()
                mask()
                mask_secrets()
            P().screenshot(path=str(raw))
            box = None
            if clip is not None and not isinstance(clip, (tuple, list)):
                clip.scroll_into_view_if_needed()
                mask()
                mask_secrets()
                P().screenshot(path=str(raw))
                bb = clip.bounding_box()
                if bb:
                    vw = P().viewport_size
                    box = (max(0, bb["x"] - margin), max(0, bb["y"] - margin),
                           min(vw["width"], bb["x"] + bb["width"] + margin),
                           min(vw["height"], bb["y"] + bb["height"] + margin))
            elif clip is not None:
                box = tuple(clip)
            if box:
                box = tuple(int(round(v)) for v in box)
                P().screenshot(path=str(path), clip={"x": box[0], "y": box[1],
                                                     "width": box[2] - box[0], "height": box[3] - box[1]})
                # keep shots/crops.json in step so shots/crop.py reproduces this crop from the raw file
                crops_file = ROOT / "shots/crops.json"
                text = crops_file.read_text()
                crops = json.loads(text)
                crops[f"images/console/{name}.png"] = list(box)
                crops_file.write_text(json.dumps(crops, indent=1) + ("\n" if text.endswith("\n") else ""))
            else:
                import shutil
                shutil.copy(raw, path)
            print(f"shot {path.relative_to(ROOT)}", flush=True)

        if not STATE.exists():
            page.goto(signin_url(), wait_until="domcontentloaded")
            page.wait_for_url(re.compile(r".*console\.aws\.amazon\.com.*"), timeout=60000)
        try:
            exec(script, {"page": page, "use": use, "app": app, "goto": goto, "close_tours": close_tours, "shot": shot, "mask": mask,
                          "collapse_nav": collapse_nav, "expand_nav": expand_nav, "select_row": select_row,
                          "table_columns": table_columns, "resize_column": resize_column,
                          "card": card, "span": span, "REGION": REGION, "ROOT": ROOT, "re": re})
        finally:
            STATE.parent.mkdir(parents=True, exist_ok=True)
            ctx.storage_state(path=str(STATE))
            os.chmod(STATE, 0o600)
            browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
