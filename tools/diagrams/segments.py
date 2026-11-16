"""세그먼트 관계도: 어느 세그먼트끼리 통신되고 어디가 막혀 있는지 (논리 관계도)."""
import sys
from dg import D, L, M, S, INK, tw

OUT = sys.argv[1]
d = D()
GREY, RED, GREEN, SUB = "#7D8998", "#D13212", "#1D8102", "#3B4552"
PAD = 20          # segment box padding
H = 150           # every segment box is the same height
ALLOW, BLOCK, LAB = "허용", "차단", "실습 2-4"


def node_w(lines):
    return max(tw(s, fs) for s, fs in lines)


def head_w(name, role):
    return 32 + tw(name, L) + 22 + tw(role, M) + 12


def seg_box(x, y, w, name, role, nodes):
    """nodes = [(icon, [(text, size), ...])] laid out left to right."""
    d.rect(x, y, w, H, stroke=GREY, sw=2, dash="6,4")
    d.image("resource/AWS-Cloud-WAN_Segment-Network", x, y, 24)
    d.text(x + 32, y + 21, name, L, fill=GREY, weight="700")
    d.text(x + 32 + tw(name, L) + 22, y + 21, role, M, fill=SUB)
    cy = y + 64
    cxs = []
    cx = x + PAD
    for i, (ref, lines) in enumerate(nodes):
        half = node_w(lines) / 2
        c = cx + half
        d.node(ref, c, cy, [(s, fs) for s, fs in lines])
        cxs.append(c)
        cx = c + half + GAP_IN
    return cxs, cy


VPC = "service/Amazon-Virtual-Private-Cloud"
VPN = "service/AWS-Site-to-Site-VPN"
GAP_IN = 110      # gap between two node label boxes inside one segment

PROD_A = [("서울 prod VPC", L), ("10.10.1.0/24", M)]
PROD_B = [("오레곤 prod VPC", L), ("10.11.1.0/24", M)]
DEV_A = [("서울 dev VPC", L), ("10.20.1.0/24", M)]
DEV_B = [("오레곤 dev VPC", L), ("10.21.1.0/24", M)]
SHARED_N = [("서울 shared VPC", L), ("10.30.1.0/24", M)]
VPN_N = [("Site-to-Site VPN", L), ("온프레미스 172.16.1.0/24", M)]

w_onprem = max(2 * PAD + node_w(VPN_N), head_w("onprem", "온프레미스"))
w_shared = max(2 * PAD + node_w(SHARED_N), head_w("shared", "공유 서비스"))
w_dev = max(2 * PAD + node_w(DEV_A) + GAP_IN + node_w(DEV_B), head_w("dev", "개발 환경"))
w_prod = max(2 * PAD + node_w(PROD_A) + GAP_IN + node_w(PROD_B), head_w("prod", "운영 환경"))

# columns
X_ON = 20
X_SH = X_ON + w_onprem + 150
X_RT = X_SH + w_shared + 80
# rows
Y_PROD = 46
Y_MID = 268
Y_DEV = 490
MID = Y_MID + H / 2                      # 375
Y_UP = Y_PROD + H / 2                    # 135, prod row centre line
Y_DN = Y_DEV + H / 2                     # 615, dev row centre line
Y_TOP = Y_PROD + 32                      # onprem -> prod run, above the prod centre
Y_BOT = Y_DEV + 118                      # onprem -> dev run, below the dev centre

prod_cxs, _ = seg_box(X_RT, Y_PROD, w_prod, "prod", "운영 환경", [(VPC, PROD_A), (VPC, PROD_B)])
seg_box(X_SH, Y_MID, w_shared, "shared", "공유 서비스", [(VPC, SHARED_N)])
on_cxs, _ = seg_box(X_ON, Y_MID, w_onprem, "onprem", "온프레미스", [(VPN, VPN_N)])
dev_cxs, _ = seg_box(X_RT, Y_DEV, w_dev, "dev", "개발 환경", [(VPC, DEV_A), (VPC, DEV_B)])

ON_CX = X_ON + w_onprem / 2
SH_CX = X_SH + w_shared / 2
ON_R = X_ON + w_onprem
SH_R = X_SH + w_shared


def allow(pts):
    d.poly(pts)


def block(pts):
    d.poly(pts, stroke=RED, dash="2,4")


def lab(pts):
    d.poly(pts, stroke=GREEN, dash="7,5")


# prod 와 dev 안: 리전이 달라도 같은 세그먼트라서 통신된다
for (a, b), cy in ((prod_cxs, Y_UP), (dev_cxs, Y_DN)):
    d.line(a + S / 2 + 4, cy, b - S / 2 - 4, cy)
    d.text((a + b) / 2, cy - 9, "리전 간 통신 " + ALLOW, M, anchor="middle")

# shared -> onprem / prod / dev : share
allow([(ON_R + 4, MID), (X_SH - 4, MID)])
d.text((ON_R + X_SH) / 2, MID - 9, "share → " + ALLOW, M, anchor="middle")
allow([(SH_CX, Y_MID - 4), (SH_CX, Y_UP), (X_RT - 4, Y_UP)])
d.text((SH_CX + X_RT) / 2, Y_UP - 9, "share → " + ALLOW, M, anchor="middle")
allow([(SH_CX, Y_MID + H + 4), (SH_CX, Y_DN), (X_RT - 4, Y_DN)])
d.text((SH_CX + X_RT) / 2, Y_DN - 9, "share → " + ALLOW, M, anchor="middle")

# onprem ↔ prod : 실습 2-4에서 share 한 줄을 넣어 연다
lab([(ON_CX, Y_MID - 4), (ON_CX, Y_TOP), (X_RT - 4, Y_TOP)])
d.text((ON_CX + X_RT) / 2, Y_TOP - 9, LAB + "에서 share 추가 → " + ALLOW, M, fill=GREEN, anchor="middle")

# onprem ↔ dev : 끝까지 차단
block([(ON_CX, Y_MID + H + 4), (ON_CX, Y_BOT), (X_RT - 4, Y_BOT)])
d.text((ON_CX + X_RT) / 2 + 80, Y_BOT - 11, BLOCK + " (고객 요구사항)", M, fill=RED, anchor="middle")

# prod ↔ dev : 세그먼트 기본 격리
BX = X_RT + 70
block([(BX, Y_PROD + H + 4), (BX, Y_DEV - 4)])
d.text(BX + 12, MID, BLOCK, M, fill=RED, weight="700")
d.text(BX + 12, MID + 20, "(세그먼트 기본 격리)", M, fill=SUB)

# ---- legend -------------------------------------------------------------
W = X_RT + w_prod + 16
LY = Y_DEV + H + 24
items = [("실선 = " + ALLOW + " (같은 세그먼트 / share)", INK),
         ("빨간 점선 = " + BLOCK + " (share 없음)", RED),
         ("초록 파선 = " + LAB + "에서 share 추가", GREEN)]
lw = [tw(t, M) for t, _ in items]
panel_h = 44
d.rect(16, LY, W - 32, panel_h, fill="#F8F9F9", stroke="#D5DBDB", sw=1)
x = 28
for (t, col), wi in zip(items, lw):
    d.text(x, LY + 27, t, M, fill=col, weight="600")
    x += wi + 40

Hc = LY + panel_h + 16
print("canvas", W, Hc, "legend width", x, file=sys.stderr)
open(OUT, "w").write(d.svg(W, Hc))
