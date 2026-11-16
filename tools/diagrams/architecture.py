"""Workshop overview: simulated on-premises -> AWS Cloud WAN core network -> VPCs in two Regions."""
import sys
sys.path.insert(0, sys.path[0])
from lib import *

OUT = sys.argv[1]
d = D()
EC2 = "service/Amazon-EC2"
CFN = "CloudFormation"
CON = "콘솔에서 직접"
EXTRA = "추가 과제 3-1"
CORE = PURPLE          # core network band
ORANGE = "#C45500"     # "made in the console" chips: dark AWS orange, white text at 4.5:1
SEG = GREY             # segment rows and the junction dots


def tagw(s):
    return tw(s, F_TAG) + 14


def grp(nid):
    d.raw(f'<g id="node:{nid}">')


def end():
    d.raw("</g>")


def widest(lines):
    return max(tw(s, F_NODE if k == "name" else F_SUB) for s, k in lines)


# ---------------- what the nodes say ----------------
RT_L = [("VPN 라우터 EC2", "name"), ("strongSwan · FRR", "sub"), ("EIP · ASN 65000", "sub")]
VM_L = [("온프레미스 VM", "name"), ("172.16.1.10", "sub")]
VPN_L = [("Site-to-Site VPN", "name"), ("IPsec 터널 2개 · BGP", "sub")]
EDGE_L = "Core network edge"
DC_T, DC_CIDR = "온프레미스", "172.16.1.0/24"
DC_NOTE = "실제로는 서울 리전의 모사 VPC"
BAND_T = "Core network"
OR_T = "미국 서부(오레곤) us-west-2"
SUBT = "서브넷"

# ---------------- sizes that drive the grid ----------------
WSUBW = int(max(32 + tw(SUBT, F_TITLE) + 8, tw("10.10.1.10", F_SUB) + 32) + 1)
VW = WSUBW + 32                                    # workload VPC width
VH = 201                                           # header 54 + subnet 131 + pad 16
EDGE_H = 128
ROW_H = 64
EHALF = tw(EDGE_L, F_NODE) / 2                     # half the edge node's label

# ---------------- x tracks ----------------
CLX = 16                                           # AWS Cloud left
SRX = 32                                           # Seoul Region left
BX = SRX + 8                                       # core network band left
PROD_CX = int(BX + 32 + tw(BAND_T, F_TITLE) + 10 + 1)   # clear of the band's header text
PITCH = VW + 24
DEV_CX = PROD_CX + PITCH
SHR_CX = PROD_CX + 2 * PITCH
# on-premises, the Internet and the VPN sit outside the AWS Cloud, below it
DCW = int(max(32 + tw(DC_NOTE, F_SUB) + 8,
              16 + widest(VM_L) / 2 + widest(VM_L) / 2 + widest(RT_L) / 2 + 8 + widest(RT_L) / 2 + 16) + 1)
VM_CX = CLX + 16 + widest(VM_L) / 2
RT_CX = VM_CX + widest(VM_L) / 2 + 8 + widest(RT_L) / 2
DCW = int(max(32 + tw(DC_NOTE, F_SUB) + 8, RT_CX + widest(RT_L) / 2 + 16 - CLX) + 1)
INT_CX = CLX + DCW + 64
VPN_CX = int(INT_CX + max(104, tw("인터넷", F_NODE) / 2 + widest(VPN_L) / 2 + 8))
ECX = int(max(SHR_CX - 30, VPN_CX + EHALF + 16))   # Seoul edge, clear of the VPN riser's labels
SHR_LX = ECX + 10                                  # shared VPC's attachment line (offset, no step)
SRR = int(max(SHR_CX + VW / 2, ECX + EHALF + 8) + 16 + 1)
ORX = SRR + 24                                     # Oregon Region left
OV_X = ORX + 16
OV1_CX = OV_X + VW / 2                             # Oregon prod VPC
OV2_CX = OV1_CX + PITCH                            # Oregon dev VPC
OECX = OV2_CX - 30                                 # Oregon edge
ODEV_LX = OECX + 10                                # Oregon dev's attachment line
ORR = int(max(OV_X + 2 * VW + 24, ODEV_LX + 10 + tagw("segment=dev"),
              ORX + 32 + tw(OR_T, F_TITLE), OECX + EHALF + 8) + 8 + 1)
CLR = ORR + 16
W = CLR + 16

# ---------------- y tracks ----------------
CLY = 16
SRY = 56
VY = SRY + 40                                      # workload VPC row
VB = VY + VH
TAG = [VB + 22 + 32 * i for i in range(4)]         # tag rows in the gap below the VPCs
BY = TAG[-1] + 36                                  # core network band
JOGY = BY - 12                                     # where dev / Oregon prod step across
R1, R2, R3 = BY + 50, BY + 50 + ROW_H + 10, BY + 50 + 2 * (ROW_H + 10)
EY = R3 + ROW_H + 10
ECY = EY + 30
R4 = EY + EDGE_H + 10
BB = R4 + ROW_H + 8
SRB = ORB = BB + 16
CLB = BB + 32
DCY = CLB + 16                                     # on-premises box, below the Cloud
NCY = DCY + 66 + 30                                # its node row, and the Internet / VPN row
DCB = NCY + 86 + 16
PANY = DCB + 16
H = PANY + 116 + 16

# ================= containers =================
d.group(CLX, CLY, CLR - CLX, CLB - CLY, "cloud", "AWS Cloud")
d.group(SRX, SRY, SRR - SRX, SRB - SRY, "region", "아시아 태평양(서울) ap-northeast-2")
d.group(ORX, SRY, ORR - ORX, ORB - SRY, "region", OR_T)

# core network band across both Regions
d.rect(BX, BY, ORR - 8 - BX, BB - BY, "none", CORE, 2, "6,4")
d.img("service/AWS-Cloud-WAN", BX, BY, 24)
d.text(BX + 32, BY + 19, BAND_T, F_TITLE, CORE, "600")
d.text(BX + 32, BY + 37, "AWS Cloud WAN", F_SUB, INK)

SEGS = [("prod", R1), ("dev", R2), ("shared", R3), ("onprem", R4)]
for name, ry in SEGS:
    d.rect(BX + 8, ry, ORR - 16 - BX - 8, ROW_H, "none", SEG, 1.5, "6,4")
    d.img("resource/AWS-Cloud-WAN_Segment-Network", BX + 18, ry + 8)
    d.text(BX + 76, ry + 38, name, F_NODE, INK, "600")


def seg_y(name):
    return dict(SEGS)[name] + ROW_H / 2


# ================= workload VPCs =================
def wvpc(cx, title, cidr, ip, nid):
    x = cx - VW / 2
    d.group(x, VY, VW, VH, "vpc", title, cidr)
    d.group(x + 16, VY + 54, WSUBW, 131, "private", SUBT)
    grp(nid)
    d.node(EC2, cx, VY + 54 + 54, [("EC2", "name"), (ip, "sub")])
    end()


wvpc(PROD_CX, "prod VPC", "10.10.1.0/24", "10.10.1.10", "prod-ec2")
wvpc(DEV_CX, "dev VPC", "10.20.1.0/24", "10.20.1.10", "dev-ec2")
wvpc(SHR_CX, "shared VPC", "10.30.1.0/24", "10.30.1.10", "shared-ec2")
wvpc(OV1_CX, "prod VPC", "10.11.1.0/24", "10.11.1.10", "or-prod-ec2")
wvpc(OV2_CX, "dev VPC", "10.21.1.0/24", "10.21.1.10", "or-dev-ec2")

# ================= on-premises (outside the AWS Cloud) =================
d.group(CLX, DCY, DCW, DCB - DCY, "onprem", DC_T, DC_CIDR)
d.text(CLX + 32, DCY + 55, DC_NOTE, F_SUB, SUB)
d.tag(CLX + DCW - 12 - tagw(CFN), DCY + 19, CFN, PINK)
grp("onprem-vm")
d.node(EC2, VM_CX, NCY, VM_L)
end()
grp("router")
d.node(EC2, RT_CX, NCY, RT_L)
end()
d.line(VM_CX + 28, NCY, RT_CX - 28, NCY, INK)

# ================= attachment lines into the core network edges =================
# Seoul prod: straight down, then into the edge's left side
d.line(PROD_CX, VB, PROD_CX, ECY - 8, INK)
d.line(PROD_CX, ECY - 8, ECX - 28, ECY - 8, INK)
d.circle(PROD_CX, seg_y("prod"), 5, SEG)
# Seoul dev and Oregon prod: step across in the gap, then down into their edge's top
for cx, tx, seg in ((DEV_CX, ECX - 10, "dev"), (OV1_CX, OECX - 10, "prod")):
    d.poly([(cx, VB), (cx, JOGY), (tx, JOGY), (tx, ECY - 28)], INK)
    d.circle(tx, seg_y(seg), 5, SEG)
# Seoul shared and Oregon dev: leave their VPC above the edge, straight down into its top
for lx, seg in ((SHR_LX, "shared"), (ODEV_LX, "dev")):
    d.line(lx, VB, lx, ECY - 28, INK)
    d.circle(lx, seg_y(seg), 5, SEG)
# AWS backbone between the two edges
d.line(ECX + 28, ECY, OECX - 28, ECY, INK)
d.text((ORX + 8 + OECX - 28) / 2, ECY - 8, "AWS 백본", F_SUB, SUB, None, "middle")

# VPN path: router -> Internet -> Site-to-Site VPN -> up into the Seoul edge's left side
d.line(RT_CX + 28, NCY, INT_CX - 28, NCY, INK)
d.line(INT_CX + 28, NCY, VPN_CX - 28, NCY, INK)
d.poly([(VPN_CX, NCY - 28), (VPN_CX, ECY + 8), (ECX - 28, ECY + 8)], INK)
d.circle(VPN_CX, seg_y("onprem"), 5, SEG)

# ================= nodes on those lines =================
grp("internet")
d.node("resource/Internet", INT_CX, NCY, [("인터넷", "name")])
end()
grp("s2svpn")
d.node("service/AWS-Site-to-Site-VPN", VPN_CX, NCY, VPN_L)
d.tag(VPN_CX - tagw(CON) / 2, NCY + 93, CON, ORANGE)
end()
grp("edge-seoul")
d.node("resource/AWS-Cloud-WAN_Core-Network-Edge", ECX, ECY, [(EDGE_L, "name"), ("ASN 64512", "sub")])
end()
grp("edge-oregon")
d.node("resource/AWS-Cloud-WAN_Core-Network-Edge", OECX, ECY, [(EDGE_L, "name"), ("ASN 64513", "sub")])
end()

# ================= who creates each attachment, and its segment tag =================
def tags(x, rows, items, side="right"):
    for base, (s, kind) in zip(rows, items):
        if kind == "text":
            tx = x + 10 if side == "right" else x - 10 - tw(s, F_SUB)
            d.text(tx, base, s, F_SUB, SUB)
        else:
            tx = x + 10 if side == "right" else x - 10 - tagw(s)
            d.tag(tx, base, s, {"cfn": PINK, "con": ORANGE}.get(kind, INK))


tags(PROD_CX, TAG, [("VPC attachment", "text"), ("segment=prod", "seg"), (CFN, "cfn")])
tags(DEV_CX, TAG[2:], [("segment=dev", "seg"), (CFN, "cfn")])
tags(SHR_LX, TAG, [("segment=shared", "seg"), (CFN, "cfn")], "left")
tags(OV1_CX, TAG, [("segment=prod", "seg"), (CON, "con")])
tags(ODEV_LX, TAG, [("segment=dev", "seg"), (CON, "con"), (EXTRA, "text")])
d.text(VPN_CX + 10, CLB + 42, "VPN attachment", F_SUB, SUB)
d.tag(VPN_CX - 10 - tagw(CON), seg_y("onprem") + 6, CON, ORANGE)
d.tag(VPN_CX - 20 - tagw(CON) - tagw("segment=onprem"), seg_y("onprem") + 6, "segment=onprem", INK)

# ================= legend =================
d.rect(16, PANY, W - 32, 116, "#F8F9F9", "#D5DBDB", 1)
d.circle(38, PANY + 21, 5, SEG)
d.text(56, PANY + 27, "연결선과 세그먼트 행이 만나는 점 = 그 연결이 배정된 세그먼트"
                      " (배정은 연결에 붙인 segment 태그로 결정된다)", F_SUB, INK)
d.text(56, PANY + 51, "AWS 백본 = 두 core network edge 사이의 자동 연결 (참가자가 만들 것 없음)", F_SUB, INK)
d.text(56, PANY + 75, f"{EXTRA} = 본편 실습이 아니라 추가 과제에서 만드는 연결", F_SUB, INK)
d.text(56, PANY + 99, f"{CFN} = 스택이 만든다 · {CON} = 참가자가 만든다"
                      " (VPN 연결, VPN attachment, 오레곤 prod·dev 연결 네 곳)", F_SUB, INK)

open(OUT, "w").write(d.svg(W, H, markers("arrow")))
print("W", W, "H", H, "VW", VW, "PROD_CX", PROD_CX, "ECX", ECX, "SRR", SRR, "VPN_CX", VPN_CX,
      "min font at 900px", round(min(F_SUB, F_TAG) * 900 / W, 2))
