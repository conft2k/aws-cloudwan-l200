"""3-2-a 비교도: 리전이 늘어날 때 Cloud WAN과 Transit Gateway에서 무엇이 늘어나는가.

왼쪽은 세그먼트 하나가 리전 네 개를 품고 있고 리전마다 core network edge가 하나씩만
늘어난다. 오른쪽은 리전마다 Transit Gateway와 라우팅 테이블이 따로 있고 리전을 이으려면
peering을 쌍마다 만들어야 한다. 그물의 선 개수가 본문의 n(n-1)/2 를 눈으로 보여 준다.
"""
import sys
from dg import D, L, M, S, INK, tw

OUT = sys.argv[1]
d = D()
GREY, PURPLE, SUB = "#7D8998", "#8C4FFF", "#3B4552"

EDGE = "resource/AWS-Cloud-WAN_Core-Network-Edge"
TGW = "service/AWS-Transit-Gateway"
RTB = "resource/Amazon-Route-53_Route-Table"
PEER = "resource/Amazon-VPC_Peering-Connection"
CWAN = "service/AWS-Cloud-WAN"
SEG = "resource/AWS-Cloud-WAN_Segment-Network"
REGION = "group/Region_32"

NAMES = ["리전 A", "리전 B", "리전 C", "리전 D"]
MARGIN = 16
HEAD_Y = 34          # 패널 제목 baseline
TOP = 52             # 패널 상자 윗변
RW_L, RH = 120, 120  # 왼쪽 리전 상자 (제목 "리전 A" 가 폭을 정한다)
RW_R = 240           # 오른쪽 리전 상자 (아이콘 두 개가 들어간다)
GAP_L = 24           # 왼쪽 2x2 간격
GAP_RX, GAP_RY = 150, 90   # 가로 간격은 TGW peering 라벨 폭(109px)이 정한다


def region(x, y, w, name):
    """리전 상자. 제목만 있고 CIDR은 없으므로 내용은 y+30 아래부터."""
    d.rect(x, y, w, RH, stroke="#00A4A6", sw=2, dash="3,3")
    d.image(REGION, x, y, 24)
    d.text(x + 32, y + 21, name, L, fill="#00A4A6", weight="600")


# ---- 왼쪽: Cloud WAN -----------------------------------------------------
grid_w = 2 * RW_L + GAP_L
grid_h = 2 * RH + GAP_L
seg_x, seg_y = MARGIN + 20, TOP + 36
seg_w, seg_h = grid_w + 40, 52 + grid_h + 20
cn_w, cn_h = seg_w + 40, 36 + seg_h + 20

d.text(MARGIN, HEAD_Y, "AWS Cloud WAN", 19, weight="700")

# core network 상자 (보라 파선, 배지는 Cloud WAN 서비스 아이콘)
d.rect(MARGIN, TOP, cn_w, cn_h, stroke=PURPLE, sw=2, dash="6,4")
d.image(CWAN, MARGIN, TOP, 24)
d.text(MARGIN + 32, TOP + 21, "core network", L, fill=PURPLE, weight="600")

# 세그먼트 상자가 리전 네 개를 모두 품는다 = 세그먼트는 전역이다
d.rect(seg_x, seg_y, seg_w, seg_h, stroke=GREY, sw=2, dash="6,4")
d.image(SEG, seg_x, seg_y, 24)
d.text(seg_x + 32, seg_y + 21, "segment prod", L, fill=GREY, weight="700")
d.text(seg_x + 32, seg_y + 39, "전역 — 리전마다 만들지 않는다", M, fill=SUB)

for i, name in enumerate(NAMES):
    rx = seg_x + 20 + (i % 2) * (RW_L + GAP_L)
    ry = seg_y + 52 + (i // 2) * (RH + GAP_L)
    region(rx, ry, RW_L, name)
    d.node(EDGE, rx + RW_L / 2, ry + 60, [("edge", L)])

# ---- 오른쪽: Transit Gateway ---------------------------------------------
rg_w = 2 * RW_R + GAP_RX
rg_h = 2 * RH + GAP_RY
DIV = MARGIN + cn_w + 30                 # 두 패널을 가르는 세로선
rg_x = DIV + 30
rg_y = TOP + 36                          # 왼쪽 리전 격자와 같은 높이에서 시작

d.text(rg_x, HEAD_Y, "Transit Gateway", 19, weight="700")

cells = []
for i, name in enumerate(NAMES):
    rx = rg_x + (i % 2) * (RW_R + GAP_RX)
    ry = rg_y + (i // 2) * (RH + GAP_RY)
    region(rx, ry, RW_R, name)
    d.node(TGW, rx + 60, ry + 60, [("TGW", L)])
    d.node(RTB, rx + 170, ry + 60, [("라우팅 테이블", L)])
    cells.append((rx, ry))

# peering 6개 = 4개 리전의 모든 쌍. 선의 수가 n(n-1)/2 다.
A, B, C, Dd = cells
AX, AY = A[0] + RW_R, A[1] + RH / 2
BX, BY = B[0], B[1] + RH / 2
TOPM, BOTM = A[1] + RH, C[1]


def peer(x1, y1, x2, y2):
    d.line(x1, y1, x2, y2, stroke=INK, sw=1.5)


peer(AX + 4, AY, BX - 4, BY)                                   # A-B
peer(C[0] + RW_R + 4, C[1] + RH / 2, Dd[0] - 4, Dd[1] + RH / 2)  # C-D
peer(A[0] + RW_R / 2, TOPM + 4, C[0] + RW_R / 2, BOTM - 4)       # A-C
peer(B[0] + RW_R / 2, TOPM + 4, Dd[0] + RW_R / 2, BOTM - 4)      # B-D
peer(A[0] + RW_R - 10, TOPM + 4, Dd[0] + 10, BOTM - 4)           # A-D 대각
peer(B[0] + 10, TOPM + 4, C[0] + RW_R - 10, BOTM - 4)            # B-C 대각

# attachment 종류는 한 번만 적는다 (A-B 선 위에 아이콘 하나)
PCX, PCY = (AX + BX) / 2, AY
d.rect(PCX - 24, PCY - 24, 48, 48, fill="#FFFFFF")
d.image(PEER, PCX - S / 2, PCY - S / 2, S)
d.text(PCX, PCY + S / 2 + 20, "TGW peering", L, anchor="middle")

# ---- 패널별 요약 ---------------------------------------------------------
left_bottom = TOP + cn_h
right_bottom = rg_y + rg_h
CAP = max(left_bottom, right_bottom) + 34

d.text(MARGIN, CAP, "리전 4개 → edge 4개", L, weight="700")
d.text(MARGIN, CAP + 22, "edge끼리는 자동으로 연결됩니다.", M, fill=SUB)
d.text(MARGIN, CAP + 42, "세그먼트는 정책 한 곳에만 적습니다.", M, fill=SUB)

d.text(rg_x, CAP, "리전 4개 → TGW 4개, peering 6개", L, weight="700")
d.text(rg_x, CAP + 22, "라우팅 테이블은 리전마다 따로 만듭니다.", M, fill=SUB)
d.text(rg_x, CAP + 42, "peering마다 양쪽 테이블에 경로를 넣습니다.", M, fill=SUB)

W = rg_x + rg_w + MARGIN
d.rect(DIV, TOP, 1, CAP + 42 + 8 - TOP, fill="#D5DBDB")

# ---- 아래 설명 패널 -------------------------------------------------------
NY = CAP + 42 + 24
note = "리전이 n개일 때 늘어나는 것: core network edge n개 · Transit Gateway peering n(n−1)/2개."
d.rect(MARGIN, NY, W - 2 * MARGIN, 44, fill="#F8F9F9", stroke="#D5DBDB", sw=1)
d.text(MARGIN + 12, NY + 27, note, M, fill=INK, weight="600")

H = NY + 44 + MARGIN
print("canvas", W, H, "note width", tw(note, M) + 24, file=sys.stderr)
open(OUT, "w").write(d.svg(W, H))
