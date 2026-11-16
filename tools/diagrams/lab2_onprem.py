"""실습 2-3: 온프레미스를 Site-to-Site VPN으로 Cloud WAN에 연결하는 순서 (1~5)."""
import sys

sys.path.insert(0, sys.path[0])
from lib import *  # noqa: F403

OUT = sys.argv[1]
d = D()

GREEN = "#1D8102"
BLOCK = "#D13212"

# ---- grid ---------------------------------------------------------------
W, H = 1198, 947
r1, r2, r3, r4, r5 = 200, 345, 495, 645, 795      # dev / shared / onprem(main) / prod / 오레곤

# left block
PANE = (12, 86, 636, 403)                          # 번호 설명 패널
OP = (12, 417, 214, 770)                           # 온프레미스 박스
x_host = 118                                       # VPN 라우터 · 온프레미스 VM
y_vm = 660
x_cgw, x_net, x_vpn = 310, 430, 560

# cloud block
CL = (654, 86, 1186, 935)                          # AWS Cloud
CN = (670, 126, 1170, 915)                         # core network
x_edge, x_bus, x_seg, x_vpc, x_or = 768, 874, 941, 1078, 988

d.raw(markers("arrow", "arrowGreen", "arrowRed"))


def chip(x0, base, s):
    w = tw(s, F_TAG) + 26
    d.rect(x0, base - 16.5, w, 22, INK, rx=3)
    d.text(x0 + w / 2, base, s, F_TAG, "#FFFFFF", "600", "middle")


def badge(cx, cy, n):
    d.circle(cx, cy, 10.5, INK)
    d.text(cx, cy + 5.5, str(n), F_TAG, "#FFFFFF", "700", "middle")


# ---- AWS Cloud / core network ------------------------------------------
d.group(CL[0], CL[1], CL[2] - CL[0], CL[3] - CL[1], "cloud", "AWS Cloud")
d.rect(CN[0], CN[1], CN[2] - CN[0], CN[3] - CN[1], "none", PURPLE, 2, "6,4")
d.img("service/AWS-Cloud-WAN", CN[0], CN[1], 24)
d.text(CN[0] + 32, CN[1] + 19, "core network", F_TITLE, PURPLE, "600")
d.text(CN[0] + 32, CN[1] + 37, "AWS Cloud WAN", F_SUB, INK)
d.text(x_seg, 150, "세그먼트", F_SUB, SUB, None, "middle")

# core network edge (서울 · 오레곤)
EDGE = "resource/AWS-Cloud-WAN_Core-Network-Edge"
d.node(EDGE, x_edge, r3, [("core network edge", "name"), ("서울 ap-northeast-2", "sub"), ("ASN 64512", "sub")])
d.node(EDGE, x_edge, r5, [("core network edge", "name"), ("오레곤 us-west-2", "sub"), ("ASN 64513", "sub")])

# segment bus: 두 edge 모두 네 세그먼트를 가진다
d.line(x_bus, r1, x_bus, r5)
d.line(x_edge + S / 2 + 4, r3, x_bus, r3)
d.line(x_edge + S / 2 + 4, r5, x_bus, r5)
SEG = "resource/AWS-Cloud-WAN_Segment-Network"
for y, name in ((r1, "dev"), (r2, "shared"), (r3, "onprem"), (r4, "prod")):
    d.line(x_bus, y, x_seg - S / 2 - 4, y)
    d.img(SEG, x_seg - S / 2, y - S / 2)
    d.text(x_seg + S / 2 + 8, y + 14, name, F_NODE, INK, "600")

# VPC attachment
VPC = "resource/Amazon-VPC_Virtual-private-cloud-VPC"
d.node(VPC, x_vpc, r1, [("dev VPC", "name"), ("서울 10.20.1.0/24", "sub"), ("VPC attachment", "sub")])
d.node(VPC, x_vpc, r2, [("shared VPC", "name"), ("서울 10.30.1.0/24", "sub"), ("EC2 10.30.1.10", "sub")])
d.node(VPC, x_vpc, r4, [("prod VPC", "name"), ("서울 10.10.1.0/24", "sub"), ("EC2 10.10.1.10", "sub")])
d.node(VPC, x_vpc, r5, [("prod VPC", "name"), ("오레곤 10.11.1.0/24", "sub")])
for y in (r1, r2, r4):
    d.line(x_vpc - S / 2 - 4, y - 16, x_seg + S / 2 + 4, y - 16)
d.poly([(x_vpc - S / 2 - 4, r5), (x_or, r5), (x_or, r4 + 55), (x_seg, r4 + 55), (x_seg, r4 + S / 2 + 4)])

# ---- 온프레미스 ----------------------------------------------------------
d.group(OP[0], OP[1], OP[2] - OP[0], OP[3] - OP[1], "onprem", "온프레미스", "172.16.1.0/24")
EC2 = "resource/Amazon-EC2_Instance"
d.node(EC2, x_host, r3, [("VPN 라우터 EC2", "name"), ("strongSwan · FRR", "sub"), ("Elastic IP", "sub")])
d.node(EC2, x_host, y_vm, [("온프레미스 VM", "name"), ("172.16.1.10", "sub")])
d.poly([(x_host - S / 2 - 4, r3), (40, r3), (40, y_vm), (x_host - S / 2 - 4, y_vm)])

# ---- 온프레미스 → AWS 경로 ----------------------------------------------
d.node("resource/Amazon-VPC_Customer-Gateway", x_cgw, r3,
       [("Customer Gateway", "name"), ("ASN 65000", "sub"), ("Elastic IP", "sub")])
d.node("resource/Internet", x_net, r3,
       [("인터넷", "name"), ("IPsec 터널 2개", "sub"), ("BGP 2 세션", "sub")])
d.node("service/AWS-Site-to-Site-VPN", x_vpn, r3,
       [("Site-to-Site VPN", "name"), ("Not Associated", "sub"), ("(게이트웨이 미연결)", "sub")])

d.line(x_host + S / 2 + 4, r3, x_cgw - S / 2 - 4, r3)
for dy in (-8, 8):
    d.line(x_cgw + S / 2 + 4, r3 + dy, x_net - S / 2 - 4, r3 + dy)
    d.line(x_net + S / 2 + 4, r3 + dy, x_vpn - S / 2 - 4, r3 + dy)
d.line(x_vpn + S / 2 + 4, r3, x_edge - S / 2 - 4, r3)

# ---- 번호 ----------------------------------------------------------------
badge(x_vpn + S / 2 + 3, 455, 1)
badge(700, 479, 2)
chip(688, 452, "segment=onprem")
badge(497, 473, 3)

# 4: onprem -> shared (성공)
d.line(x_seg, r3 - S / 2 - 4, x_seg, r2 + S / 2 + 4, GREEN, 1.8, None, "arrowGreen")
badge(908, 420, 4)
d.text(959, 426, "성공", F_SUB, GREEN, "700")

# 5: onprem -> prod (차단)
d.line(x_seg, r3 + S / 2 + 4, x_seg, r4 - S / 2 - 4, BLOCK, 1.8, "6,4", "arrowRed")
badge(908, 570, 5)
d.text(959, 576, "차단(실패)", F_SUB, BLOCK, "700")

# ---- 번호 설명 패널 -------------------------------------------------------
d.rect(PANE[0], PANE[1], PANE[2] - PANE[0], PANE[3] - PANE[1], "#FBFBFB", "#D5DBDB", 1.5)
d.text(PANE[0] + 20, PANE[1] + 26, "실습 2-3 진행 순서", F_TITLE, INK, "600")
STEPS = [
    (1, ["Site-to-Site VPN 연결 생성 (Target Gateway Type = Not Associated)",
         "Customer Gateway = VPN 라우터 Elastic IP · ASN 65000"]),
    (2, ["Cloud WAN VPN attachment 생성 · 태그 segment=onprem",
         "edge location ap-northeast-2 · tag-exists 규칙이 onprem에 배정"]),
    (3, ["attachment 뒤에 AWS 터널 엔드포인트(외부 IP 2개)가 생긴다",
         "sudo /opt/onprem/setup-tunnels.sh <vpn 연결 ID> 실행",
         "터널 2개 UP · BGP 65000 ↔ 64512 · 172.16.1.0/24 광고"]),
    (4, ["172.16.1.10 → shared EC2 10.30.1.10 : 성공",
         "shared 가 onprem 에도 share 되어 있다"]),
    (5, ["172.16.1.10 → prod EC2 10.10.1.10 : 실패(차단)",
         "onprem ↔ prod 공유 없음 → 실습 2-4에서 share 추가"]),
]
y = PANE[1] + 56
for n, lines in STEPS:
    badge(PANE[0] + 30, y - 5, n)
    for i, s in enumerate(lines):
        d.text(PANE[0] + 50, y + i * 20, s, F_SUB, INK if i == 0 else SUB)
    y += len(lines) * 20 + 8

open(OUT, "w").write(d.svg(W, H, ""))
print("canvas", W, H, "min@900", round(F_SUB * 900 / W, 2))
