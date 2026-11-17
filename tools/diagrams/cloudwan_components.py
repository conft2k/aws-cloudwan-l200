"""Cloud WAN 주요 구성요소 레퍼런스: 무엇이 무엇 안에 들어 있는가 (1-3 용어 풀이 앞에 놓는 개념도).

global network 안에 core network 가 있고, core network 는 세그먼트 행과 core network edge
행으로 이루어진다. 세그먼트 행은 리전 상자를 가로질러 그려서 세그먼트가 전역이라는 것을,
core network edge 는 리전마다 하나씩 그려서 edge location 이라는 것을 보인다. VPC 와
Site-to-Site VPN 은 core network 밖에 두고, attachment 은 edge 로 가는 선 하나로 그린다.
선이 어느 세그먼트 행을 지날 때 찍히는 회색 점이 그 attachment 의 세그먼트 소속이다.
주소·ASN 같은 이 워크숍 고유의 값은 넣지 않는다 (시나리오 구성도는 architecture / segments).
"""
import sys
from dg import D, L, M, S, INK, tw

OUT = sys.argv[1]
d = D()
GREY, PURPLE, TEAL, SUB = "#7D8998", "#8C4FFF", "#00A4A6", "#3B4552"
PANEL_BG, PANEL_BD = "#F8F9F9", "#D5DBDB"

VPC = "service/Amazon-Virtual-Private-Cloud"
VPN = "service/AWS-Site-to-Site-VPN"
EDGE = "resource/AWS-Cloud-WAN_Core-Network-Edge"
SEGI = "resource/AWS-Cloud-WAN_Segment-Network"
CWAN = "service/AWS-Cloud-WAN"
REGI = "group/Region_32"

BAND_T = "core network"
GN_T, GN_SUB = "global network", "Network Manager"
EDGE_T = "Core network edge"
SEGS_UP = [("segment prod", "운영 환경"), ("segment dev", "개발 환경")]
SEGS_DN = [("segment shared", "공유 서비스"), ("segment onprem", "온프레미스")]
REGIONS = [("ap-northeast-2", "edge location · 서울"), ("us-west-2", "edge location · 오레곤")]
POLICY = [("edge-locations", "core network edge 를 둘 리전"),
          ("segments", "prod · dev · shared · onprem"),
          ("attachment policy", "attachment 을 어느 세그먼트에 넣을지"),
          ("segment actions", "세그먼트끼리의 통신 (share)")]
VPC_L = [("VPC", L), ("VPC attachment", M, SUB)]
VPN_L = [("Site-to-Site VPN", L), ("Site-to-Site VPN attachment", M, SUB)]

# ---------------- x tracks ----------------
MARGIN = 16
CLX = MARGIN                                   # AWS Cloud
GNX = CLX + 16                                  # global network
BX = GNX + 8                                    # core network band (리전 상자를 가로지른다)
HDRW = int(max(tw(BAND_T, L), max(tw(t, L) for t, _ in SEGS_UP + SEGS_DN)) + 32 + 14)
REG1X = BX + HDRW                               # 리전 상자는 헤더 글자 오른쪽에서 시작한다
NODE_W = max(tw("VPC attachment", M), tw(EDGE_T, L))
REG_W = int(max(NODE_W + 2 * 16, 36 + max(tw(t, L) for t, _ in REGIONS) + 8,
                36 + max(tw(s, M) for _, s in REGIONS) + 8) + 1)
REG_W = max(REG_W, 220)                         # 아래에서 올라오는 선이 테두리에서 12px 이상 떨어지도록
REG2X = REG1X + REG_W + 24
BW = REG2X + REG_W + 16 - BX
SX = REG1X + REG_W / 2                          # 서울 열 중심
OX = REG2X + REG_W / 2                          # 오레곤 열 중심
OFF = 92                                        # 아래에서 올라오는 선의 가로 오프셋
PX = BX + BW + 24                               # core network policy 패널
PW = int(max(max(tw(t, L) for t, _ in POLICY), max(tw(s, M) for _, s in POLICY)) + 24 + 1)
GNW = PX + PW + 16 - GNX
W = GNX + GNW + 16 + MARGIN

# ---------------- y tracks ----------------
CLY = MARGIN
GNY = CLY + 40
REGY = GNY + 52
CY_A = REGY + 52 + S / 2                        # 상단 VPC 행
BY = CY_A + 66 + 30                             # core network 상자 윗변
ROW_H = 52
R1 = BY + 36
R2 = R1 + ROW_H + 10
CY_E = R2 + ROW_H + 18 + S / 2                  # core network edge 행
R3 = CY_E + 66 + 18
R4 = R3 + ROW_H + 10
BH = R4 + ROW_H + 16 - BY
CY_C = BY + BH + 30 + S / 2                     # 하단 VPC 행
REG_H = CY_C + 66 + 16 - REGY
GNH = REG_H + 52 + 16
CLH = GNY + GNH + 16 - CLY
CY_V = CLY + CLH + 16 + S / 2                   # Site-to-Site VPN (AWS Cloud 밖)
NY = CY_V + 66 + 24


def rowc(y):
    return y + ROW_H / 2 + 4


# ---------------- containers ----------------
d.cloud(CLX, CLY, W - 2 * MARGIN, CLH)

d.rect(GNX, GNY, GNW, GNH, stroke=GREY, sw=1.5, dash="6,4")
d.text(GNX + 12, GNY + 21, GN_T, L, fill=GREY, weight="600")
d.text(GNX + 12, GNY + 39, GN_SUB, M, fill=SUB)

for (title, sub), rx in zip(REGIONS, (REG1X, REG2X)):
    d.group("region", rx, REGY, REG_W, REG_H, title, sub)

d.rect(BX, BY, BW, BH, stroke=PURPLE, sw=2, dash="6,4")
d.image(CWAN, BX, BY, 24)
d.text(BX + 32, BY + 21, BAND_T, L, fill=PURPLE, weight="600")

for (title, sub), ry in zip(SEGS_UP + SEGS_DN, (R1, R2, R3, R4)):
    d.rect(BX + 8, ry, BW - 16, ROW_H, stroke=GREY, sw=1.5, dash="6,4")
    d.image(SEGI, BX + 8, ry, 24)
    d.text(BX + 40, ry + 21, title, L, fill=GREY, weight="600")
    d.text(BX + 40, ry + 41, sub, M, fill=SUB)

# ---------------- attachment lines ----------------
DOT = 4.5


def dot(x, y):
    d.circle(x, y, DOT, GREY)


# 위에서 내려오는 VPC attachment: 서울 prod, 오레곤 dev
for cx, ry in ((SX, R1), (OX, R2)):
    d.line(cx, CY_A + S / 2 + 4, cx, CY_E - S / 2 - 4)
    dot(cx, rowc(ry))

# 아래에서 올라오는 attachment: edge 노드 라벨을 피해 옆으로 돌아 들어간다
d.poly([(OX + S / 2 + 4, CY_C), (OX + OFF, CY_C), (OX + OFF, CY_E), (OX + S / 2 + 4, CY_E)])
dot(OX + OFF, rowc(R3))
d.poly([(SX - S / 2 - 4, CY_V), (SX - OFF, CY_V), (SX - OFF, CY_E), (SX - S / 2 - 4, CY_E)])
dot(SX - OFF, rowc(R4))

# edge 끼리는 AWS 백본으로 자동 연결된다
d.line(SX + S / 2 + 4, CY_E, OX - S / 2 - 4, CY_E)
d.text((SX + OX) / 2, CY_E - 10, "AWS 백본으로 자동 연결", M, fill=SUB, anchor="middle")

# ---------------- nodes ----------------
for cx, (title, sub) in zip((SX, OX), REGIONS):
    d.node(EDGE, cx, CY_E, [(EDGE_T, L), (sub.split(" · ")[1] + " edge", M, SUB)])
d.node(VPC, SX, CY_A, VPC_L)
d.node(VPC, OX, CY_A, VPC_L)
d.node(VPC, OX, CY_C, VPC_L)
d.node(VPN, SX, CY_V, VPN_L)

# ---------------- core network policy ----------------
PH = 36 + len(POLICY) * 46
PY = int(BY + BH / 2 - PH / 2)
d.rect(PX, PY, PW, PH, fill=PANEL_BG, stroke=PURPLE, sw=1.5)
d.text(PX + 12, PY + 24, "core network policy", L, fill=PURPLE, weight="600")
y = PY + 36
for t, s in POLICY:
    d.text(PX + 12, y + 20, t, L, weight="600")
    d.text(PX + 12, y + 40, s, M, fill=SUB)
    y += 46
d.line(BX + BW + 4, BY + BH / 2, PX - 4, BY + BH / 2, stroke=PURPLE, dash="4,3")

# ---------------- note ----------------
notes = ["회색 점 = 그 attachment 이 속한 세그먼트. attachment 하나는 세그먼트 하나에만 들어갑니다.",
         "세그먼트 행은 리전 상자를 가로지릅니다. 세그먼트는 전역이고, core network edge 만 리전마다 생깁니다."]
NH = 20 + len(notes) * 24
d.rect(MARGIN, NY, W - 2 * MARGIN, NH, fill=PANEL_BG, stroke=PANEL_BD, sw=1)
for i, s in enumerate(notes):
    d.text(MARGIN + 12, NY + 28 + i * 24, s, M, fill=INK, weight="600")

H = NY + NH + MARGIN
print("canvas", W, H, "note width", max(tw(s, M) for s in notes) + 24, file=sys.stderr)
open(OUT, "w").write(d.svg(W, H))
