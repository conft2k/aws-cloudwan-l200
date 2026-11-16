"""Workshop overview: simulated on-premises -> AWS Cloud WAN core network -> VPCs in two Regions."""
import sys
sys.path.insert(0, sys.path[0])
from lib import *

OUT = sys.argv[1]
d = D()
CFN = "CloudFormation"
CON = "콘솔에서 직접"
CORE = PURPLE          # core network band
SEG = GREY             # segment rows and the junction dots


def tagw(s):
    return tw(s, F_TAG) + 14


def grp(nid):
    d.raw(f'<g id="node:{nid}">')


def end():
    d.raw("</g>")


# ---------------- sizes that drive the grid ----------------
SUBT = "프라이빗 서브넷"
WSUBW = int(32 + tw(SUBT, F_TITLE) + 8 + 1)       # workload VPC subnet: its title must fit
VW = WSUBW + 32                                    # workload VPC width
VH = 201                                           # header 54 + subnet 131 + pad 16
OSUBW = 224                                        # on-prem VPC subnets: wider, for the riser corridor
GAPY = 118                                         # VPC row -> core network band (holds the tags)
EDGE_H = 128
ROW_H = 64

# ---------------- x tracks ----------------
CLX = 16                                           # AWS Cloud left
SRX = 32                                           # Seoul Region left
BX = SRX + 8                                       # core network band left
BAND_T = "Core network"
PROD_CX = int(BX + 32 + tw(BAND_T, F_TITLE) + 10 + 1)   # clear of the band's header text
PITCH = VW + 24
DEV_CX = PROD_CX + PITCH
SHR_CX = PROD_CX + 2 * PITCH
ECX = SHR_CX - 30                                  # Seoul core network edge
SHR_LX = ECX + 10                                  # shared VPC's attachment line (offset, no step)
OPX = SRX + 16                                     # on-prem VPC left
OPW = 16 + OSUBW + 32                              # right pad 32: room for the IGW mask on the border
OPR = OPX + OPW
INT_CX = OPR + 70                                  # Internet, below the AWS Cloud
VPN_CX = INT_CX + 120                              # Site-to-Site VPN, below the AWS Cloud
SRR = int(max(SHR_CX + VW / 2, SHR_LX + 10 + tagw("segment=shared")) + 16 + 1)
ORX = SRR + 24                                     # Oregon Region left
OR_T = "미국 서부(오레곤) us-west-2"
OV_X = ORX + 16
OECX = OV_X + VW / 2                               # Oregon core network edge
ORR = int(max(OV_X + VW, OECX + 10 + tagw("segment=prod"), ORX + 32 + tw(OR_T, F_TITLE)) + 8 + 1)
CLR = ORR + 16
W = CLR + 16

# ---------------- y tracks ----------------
CLY = 16
SRY = 56
VY = SRY + 40                                      # workload VPC row
VB = VY + VH
TAG1 = VB + 22                                     # the three tag lines in the gap
TAG2 = TAG1 + 30
TAG3 = TAG2 + 32
BY = VB + GAPY                                     # core network band
JOGY = BY - 12                                     # where dev steps across
R1, R2, R3 = BY + 50, BY + 50 + ROW_H + 10, BY + 50 + 2 * (ROW_H + 10)
EY = R3 + ROW_H + 10
ECY = EY + 30
R4 = EY + EDGE_H + 10
BB = R4 + ROW_H + 8
OPY = BB + 24                                      # on-prem VPC
PS_Y = OPY + 72                                    # public subnet (3-line VPC header)
RCY = PS_Y + 54
VS_Y = PS_Y + 152 + 16
VMCY = VS_Y + 54
OPB = VS_Y + 131 + 16
SRB = OPB + 16
ORB = BB + 16
CLB = SRB + 16
SCY = CLB + 40                                     # Internet / Site-to-Site VPN strip
PANY = SCY + 65 + 12 + 16
H = PANY + 68 + 16

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
    d.node("service/Amazon-EC2", cx, VY + 54 + 54, [("EC2", "name"), (ip, "sub")])
    end()


wvpc(PROD_CX, "prod VPC", "10.10.1.0/24", "10.10.1.10", "prod-ec2")
wvpc(DEV_CX, "dev VPC", "10.20.1.0/24", "10.20.1.10", "dev-ec2")
wvpc(SHR_CX, "shared VPC", "10.30.1.0/24", "10.30.1.10", "shared-ec2")
wvpc(OECX, "prod VPC", "10.11.1.0/24", "10.11.1.10", "or-prod-ec2")

# ================= on-premises simulation VPC =================
d.group(OPX, OPY, OPW, OPB - OPY, "vpc", "온프레미스 모사 VPC", "172.16.1.0/24")
d.text(OPX + 32, OPY + 55, "VPC attachment 없음", F_SUB, SUB)
NCX = OPX + 16 + OSUBW / 2
d.rect(OPX + 16, PS_Y, OSUBW, 152, "none", GREEN, 1.5)     # public subnet: no helper in lib.py
d.img("group/Public-subnet_32", OPX + 16, PS_Y, 24)
d.text(OPX + 48, PS_Y + 19, "퍼블릭 서브넷", F_TITLE, GREEN, "600")
grp("router")
d.node("service/Amazon-EC2", NCX, RCY,
       [("VPN 라우터 EC2", "name"), ("strongSwan · FRR", "sub"), ("EIP · ASN 65000", "sub")])
end()
d.group(OPX + 16, VS_Y, OSUBW, 131, "private", SUBT)
grp("onprem-vm")
d.node("resource/Server", NCX, VMCY, [("온프레미스 VM", "name"), ("172.16.1.10", "sub")])
end()
CORR = OPX + 16 + OSUBW - 24                               # corridor clear of titles and labels
d.poly([(NCX + 28, VMCY), (CORR, VMCY), (CORR, RCY), (NCX + 28, RCY)], INK)

# ================= attachment lines into the core network edges =================
# Seoul prod: straight down, then into the edge's left side
d.line(PROD_CX, VB, PROD_CX, ECY - 8, INK)
d.line(PROD_CX, ECY - 8, ECX - 28, ECY - 8, INK)
d.circle(PROD_CX, seg_y("prod"), 5, SEG)
# Seoul dev: steps across in the gap, then down into the edge's top
d.poly([(DEV_CX, VB), (DEV_CX, JOGY), (ECX - 10, JOGY), (ECX - 10, ECY - 28)], INK)
d.circle(ECX - 10, seg_y("dev"), 5, SEG)
# Seoul shared: leaves its VPC above the edge, straight down into the edge's top
d.line(SHR_LX, VB, SHR_LX, ECY - 28, INK)
d.circle(SHR_LX, seg_y("shared"), 5, SEG)
# Oregon prod: straight down into its own edge's top
d.line(OECX, VB, OECX, ECY - 28, INK)
d.circle(OECX, seg_y("prod"), 5, SEG)
# AWS backbone between the two edges
d.line(ECX + 28, ECY, OECX - 28, ECY, INK)
d.text((ECX + 28 + SRR - 8) / 2, ECY - 8, "AWS 백본", F_SUB, SUB, None, "middle")

# VPN path: router -> IGW -> out of the Cloud -> Internet -> Site-to-Site VPN -> edge
d.line(NCX + 28, RCY, OPR - 24, RCY, INK)
d.poly([(OPR + 24, RCY), (INT_CX, RCY), (INT_CX, SCY - 28)], INK)
d.line(INT_CX + 28, SCY, VPN_CX - 28, SCY, INK)
d.poly([(VPN_CX, SCY - 28), (VPN_CX, ECY + 8), (ECX - 28, ECY + 8)], INK)
d.circle(VPN_CX, seg_y("onprem"), 5, SEG)

# ================= nodes on those lines =================
grp("internet")
d.node("resource/Internet", INT_CX, SCY, [("인터넷", "name")])
end()
grp("s2svpn")
d.node("service/AWS-Site-to-Site-VPN", VPN_CX, SCY,
       [("Site-to-Site VPN", "name"), ("IPsec 터널 2개 · BGP", "sub")])
end()
grp("edge-seoul")
d.node("resource/AWS-Cloud-WAN_Core-Network-Edge", ECX, ECY,
       [("Core network edge", "name"), ("ASN 64512", "sub")])
end()
grp("edge-oregon")
d.node("resource/AWS-Cloud-WAN_Core-Network-Edge", OECX, ECY,
       [("Core network edge", "name"), ("ASN 64513", "sub")])
end()

# ================= who creates each attachment, and its segment tag =================
d.text(PROD_CX + 10, TAG1, "VPC attachment", F_SUB, SUB)
for cx, seg in ((PROD_CX, "prod"), (DEV_CX, "dev"), (SHR_LX, "shared"), (OECX, "prod")):
    d.tag(cx + 10, TAG2, f"segment={seg}", INK)
    d.tag(cx + 10, TAG3, CON if cx == OECX else CFN, INK if cx == OECX else PINK)
d.text(VPN_CX + 10, BB + 49, "VPN attachment", F_SUB, SUB)
d.tag(VPN_CX + 10, seg_y("onprem") + 6, "segment=onprem", INK)
d.tag(VPN_CX + 10 + tagw("segment=onprem") + 10, seg_y("onprem") + 6, CON, INK)

# ================= IGW on the on-prem VPC border (mask last, on top) =================
d.rect(OPR - 24, RCY - 24, 48, 72, "#FFFFFF")
d.img("resource/Amazon-VPC_Internet-Gateway", OPR - 24, RCY - 24)
d.text(OPR, RCY + 44, "IGW", F_NODE, INK, None, "middle")

# ================= legend =================
d.rect(16, PANY, W - 32, 68, "#F8F9F9", "#D5DBDB", 1)
d.circle(38, PANY + 21, 5, SEG)
d.text(56, PANY + 27, "연결선과 세그먼트 행이 만나는 점 = 그 연결이 배정된 세그먼트"
                      " (배정은 연결에 붙인 segment 태그로 결정된다)", F_SUB, INK)
d.text(56, PANY + 51, "AWS 백본 = 두 core network edge 사이의 자동 연결 (참가자가 만들 것 없음)", F_SUB, INK)

open(OUT, "w").write(d.svg(W, H, markers("arrow")))
print("W", W, "H", H, "VW", VW, "PROD_CX", PROD_CX, "ECX", ECX, "SRR", SRR,
      "min font at 900px", round(min(F_SUB, F_TAG) * 900 / W, 2))
