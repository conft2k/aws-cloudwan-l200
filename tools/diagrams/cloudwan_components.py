"""Cloud WAN 주요 구성요소 레퍼런스: 무엇이 무엇 안에 들어 있는가 (1-3 용어 풀이 앞의 개념도).

global network 가 가장 바깥 상자이고 그 안에 core network 가 있다. core network 는 세그먼트
행과 core network edge 행으로 이루어진다. 세그먼트 행은 리전 상자를 가로질러 그려서 세그먼트가
전역이라는 것을, core network edge 는 리전마다 하나씩 그려서 edge location 이라는 것을 보인다.
VPC 와 Site-to-Site VPN 은 core network 밖에 두고, attachment 은 edge 로 가는 선 하나로 그린다.
선이 어느 세그먼트 행에서 회색 점을 찍느냐가 그 attachment 의 세그먼트 소속이다.
core network policy 패널은 정책 하나가 edge location · segment · attachment 배정 · 세그먼트 간
통신을 모두 정한다는 것을 보인다.

세그먼트 배정은 PLAN.md 의 세그먼트 설계와 같다. prod 는 서울, dev 는 오레곤(추가 과제 3-1),
shared 는 서울 하나뿐, onprem 은 Site-to-Site VPN. 그래서 세그먼트 행은 위에서부터
prod · dev · shared 를 edge 행 위에, onprem 을 edge 행 아래에 둔다. 주소·ASN 같은 이 워크숍
고유의 값은 넣지 않는다(시나리오 구성도는 architecture 와 segments).
"""
import sys
from dg import D, L, M, S, INK, tw

OUT = sys.argv[1]
d = D()
GREY, PURPLE, SUB = "#7D8998", "#8C4FFF", "#3B4552"
PANEL_BG, PANEL_BD = "#F8F9F9", "#D5DBDB"

VPC = "service/Amazon-Virtual-Private-Cloud"
VPN = "service/AWS-Site-to-Site-VPN"
EDGE = "resource/AWS-Cloud-WAN_Core-Network-Edge"
SEGI = "resource/AWS-Cloud-WAN_Segment-Network"
CWAN = "service/AWS-Cloud-WAN"

GN_T, GN_SUB = "global network", "Network Manager"
BAND_T = "core network"
EDGE_T = "Core network edge"
BACKBONE = "AWS 백본"
SEG_ROWS = [("segment prod", "운영 환경"), ("segment dev", "개발 환경"),
            ("segment shared", "공유 서비스"), ("segment onprem", "온프레미스")]
REGIONS = [("ap-northeast-2", "edge location · 서울"), ("us-west-2", "edge location · 오레곤")]
POLICY_T = "core network policy"
POLICY = [("edge-locations", "edge 를 둘 리전"),
          ("segments", "prod · dev · shared · onprem"),
          ("attachment policy", "attachment 의 세그먼트 배정"),
          ("segment actions", "세그먼트끼리의 통신 (share)")]
VPC_L = [("VPC", L), ("VPC attachment", M, SUB)]
VPN_L = [("Site-to-Site VPN", L), ("Site-to-Site VPN attachment", M, SUB)]

ROW_H = 56
OFF = 92            # 아래에서 올라오는 선이 edge 라벨을 피해 도는 거리
PAIR = 90           # 한 리전에 VPC 가 둘일 때 아이콘과 edge 열의 거리
SOLO = 80           # 한 리전에 VPC 가 하나일 때


def half(lines):
    return max(tw(ln[0], ln[1]) for ln in lines) / 2


VPC_H = half(VPC_L)
VPN_H = half(VPN_L)
EDGE_H = max(tw(EDGE_T, L), tw("오레곤 edge", M)) / 2

# ---------------- x tracks ----------------
MARGIN = 16
CLX = MARGIN                                     # AWS Cloud
GNX = CLX + 16                                   # global network
BX = GNX + 24                                    # core network (리전 상자를 가로지른다)
HDRW = int(max(tw(BAND_T, L), max(tw(t, L) for t, _ in SEG_ROWS)) + 32 + 14)
RW = int(2 * max(PAIR + VPC_H + 16, EDGE_H + 16, OFF + VPN_H / 3 + 16) + 1)   # 리전 상자 폭
R1X = BX + HDRW
R2X = R1X + RW + 24
E1 = R1X + RW / 2                                # 서울 edge 열
E2 = R2X + RW / 2                                # 오레곤 edge 열
GAP_CX = (R1X + RW + R2X) / 2                    # 리전 사이 틈 (정책 연결선이 지난다)
BW = R2X + RW + 28 - BX          # 리전 상자보다 좌우로 더 나가야 '가로지른다'가 보인다
GNW = BW + 48
W = GNX + GNW + 16 + MARGIN

# ---------------- y tracks ----------------
CLY = MARGIN
GNY = CLY + 40
REGY = GNY + 52
CY_A = REGY + 52 + S / 2                         # VPC 행 (세 개 모두 core network 위)
BY = CY_A + 66 + 30                              # core network 상자 윗변
R1 = BY + 36                                     # prod
R2 = R1 + ROW_H + 10                             # dev
R3 = R2 + ROW_H + 10                             # shared
CY_E = R3 + ROW_H + 18 + S / 2                   # core network edge 행
R4 = CY_E + 66 + 18                              # onprem
BH = R4 + ROW_H + 16 - BY
REG_H = BY + BH + 16 - REGY
PY = REGY + REG_H + 24                           # core network policy 패널
PH = 36 + 2 * 46 + 8
GNH = PY + PH + 16 - GNY
CLH = GNY + GNH + 16 - CLY
CY_V = CLY + CLH + 16 + S / 2                    # Site-to-Site VPN (AWS Cloud 밖)
NY = CY_V + 66 + 24


def rowc(y):
    return y + ROW_H / 2


# ---------------- containers ----------------
d.cloud(CLX, CLY, W - 2 * MARGIN, CLH)

d.rect(GNX, GNY, GNW, GNH, stroke=GREY, sw=1.5, dash="6,4")
d.text(GNX + 12, GNY + 21, GN_T, L, fill=GREY, weight="600")
d.text(GNX + 12, GNY + 39, GN_SUB, M, fill=SUB)

for (title, sub), rx in zip(REGIONS, (R1X, R2X)):
    d.group("region", rx, REGY, RW, REG_H, title, sub)

d.rect(BX, BY, BW, BH, stroke=PURPLE, sw=2, dash="6,4")
d.image(CWAN, BX, BY, 24)
d.text(BX + 32, BY + 21, BAND_T, L, fill=PURPLE, weight="600")

for (title, sub), ry in zip(SEG_ROWS, (R1, R2, R3, R4)):
    d.rect(BX + 8, ry, BW - 28, ROW_H, stroke=GREY, sw=1.5, dash="6,4")
    d.image(SEGI, BX + 8, ry, 24)
    d.text(BX + 40, ry + 21, title, L, fill=GREY, weight="600")
    d.text(BX + 40, ry + 41, sub, M, fill=SUB)


# ---------------- attachment lines ----------------
def dot(x, y):
    d.circle(x, y, 4.5, GREY)


def from_above(node_cx, line_x, ry):
    """VPC 아이콘 옆으로 빠져나와 세로로 내려가 edge 아이콘 위로 들어간다."""
    side = S / 2 + 4 if line_x > node_cx else -(S / 2 + 4)
    d.poly([(node_cx + side, CY_A), (line_x, CY_A), (line_x, CY_E - S / 2 - 4)])
    dot(line_x, rowc(ry))


# 서울: prod VPC 와 shared VPC. 오레곤: dev VPC (추가 과제 3-1)
from_above(E1 - PAIR, E1 - 10, R1)               # 서울 prod VPC -> segment prod
from_above(E1 + PAIR, E1 + 10, R3)               # 서울 shared VPC -> segment shared
from_above(E2 - SOLO, E2, R2)                    # 오레곤 dev VPC -> segment dev

# 아래에서 올라오는 attachment 은 edge 아이콘 라벨을 피해 옆면으로 들어간다
d.poly([(E1 - OFF, CY_V - S / 2 - 4), (E1 - OFF, CY_E), (E1 - S / 2 - 4, CY_E)])
dot(E1 - OFF, rowc(R4))                          # Site-to-Site VPN -> segment onprem

# edge 끼리는 AWS 백본으로 자동 연결된다
d.line(E1 + S / 2 + 4, CY_E, E2 - S / 2 - 4, CY_E)
d.text(E1 + S / 2 + 12, CY_E - 10, BACKBONE, M, fill=SUB)

# ---------------- nodes ----------------
for ex, (_, sub) in zip((E1, E2), REGIONS):
    d.node(EDGE, ex, CY_E, [(EDGE_T, L), (sub.split(" · ")[1] + " edge", M, SUB)])
d.node(VPC, E1 - PAIR, CY_A, VPC_L)
d.node(VPC, E1 + PAIR, CY_A, VPC_L)
d.node(VPC, E2 - SOLO, CY_A, VPC_L)
d.node(VPN, E1 - OFF, CY_V, VPN_L)

# ---------------- core network policy ----------------
COL1 = max(max(tw(POLICY[i][0], L), tw(POLICY[i][1], M)) for i in (0, 2))
COL2 = max(max(tw(POLICY[i][0], L), tw(POLICY[i][1], M)) for i in (1, 3))
PWID = int(12 + COL1 + 32 + COL2 + 12 + 1)
PX = BX + BW - PWID                               # 서울 attachment 선 오른쪽에 둔다
assert PX >= E1 - OFF + 40, (PX, E1 - OFF)
d.rect(PX, PY, PWID, PH, stroke=PURPLE, sw=1.5, dash="4,3")
d.text(PX + 12, PY + 24, POLICY_T, L, fill=PURPLE, weight="600")
for i, (t, s) in enumerate(POLICY):
    x = PX + 12 + (i % 2) * (COL1 + 32)
    y = PY + 36 + (i // 2) * 46
    d.text(x, y + 20, t, L, weight="600")
    d.text(x, y + 40, s, M, fill=SUB)
d.poly([(GAP_CX, PY), (GAP_CX, BY + BH)], stroke=PURPLE, dash="4,3")

# ---------------- note ----------------
notes = ["회색 점 = 그 attachment 이 속한 세그먼트. attachment 하나는 세그먼트 하나에만 들어갑니다.",
         "세그먼트 행은 리전 상자를 가로지릅니다. 세그먼트는 전역이고 core network edge 만 리전마다 생깁니다."]
NH = 20 + len(notes) * 24
d.rect(MARGIN, NY, W - 2 * MARGIN, NH, fill=PANEL_BG, stroke=PANEL_BD, sw=1)
for i, s in enumerate(notes):
    d.text(MARGIN + 12, NY + 28 + i * 24, s, M, fill=INK, weight="600")

H = NY + NH + MARGIN
print("canvas", W, H, "note width", max(tw(s, M) for s in notes) + 24, file=sys.stderr)
open(OUT, "w").write(d.svg(W, H))
