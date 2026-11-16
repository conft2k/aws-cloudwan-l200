# 실습 2-2: 세그먼트 격리와 글로벌 연결. 번호 1~5는 참가자가 하는 일의 순서.
# 생성: python3 lab1_global.py <out.draft.svg>   (build.sh lab1-global 이 호출)
import sys
sys.path.insert(0, sys.path[0])
from lib import *

OUT = sys.argv[1]
d = D()
GREEN_A = "#1D8102"
RED_A = "#D13212"
F_BADGE = 15

EC2 = "service/Amazon-EC2"
ATT = "resource/AWS-Transit-Gateway_Attachment"      # 패키지의 유일한 attachment 리소스 아이콘
SEG = "resource/AWS-Cloud-WAN_Segment-Network"
CWAN = "service/AWS-Cloud-WAN"


def grp(nid):
    d.raw(f'<g id="node:{nid}">')


def end():
    d.raw("</g>")


def badge(cx, cy, n):
    d.circle(cx, cy, 10.5, INK)
    d.text(cx, cy + 5.5, str(n), F_BADGE, "#FFFFFF", "700", "middle")


# ---------------- 좌표 ----------------
W = 1162
CLOUD = (14, 14, 1134, 700)                 # x, y, w, h  -> 14..1148, 14..714
SEOUL = (26, 60, 264, 640)                  # 26..290
CORE = (322, 60, 520, 640)                  # 322..842
OREGON = (872, 256, 264, 230)               # 872..1136
VPCW, VPCH = 240, 164
LANE_X, LANE_W, LANE_H = 362, 460, 150      # 362..822
ROWS = [                                    # (세그먼트, lane y, VPC y, 행 중심 y)
    ("dev", 146, 112, 216),
    ("prod", 342, 308, 412),
    ("shared", 538, 504, 608),
]
AX_S, AX_O = 470, 710
OY = 412                                    # 오레곤 prod 행 중심                       # attachment 아이콘 중심 x (서울 / 오레곤)
PANEL_Y = 730
PANEL_H = 170
H = PANEL_Y + PANEL_H + 16

# ---------------- 컨테이너 ----------------
d.group(*CLOUD, "cloud", "AWS Cloud")
d.group(*SEOUL, "region", "아시아 태평양(서울)", "ap-northeast-2")
d.group(*OREGON, "region", "미국 서부(오레곤)", "us-west-2")

# Cloud WAN core network (전역 구성 요소: 리전 밖, Cloud 안)
cx0, cy0, cw, ch = CORE
d.rect(cx0, cy0, cw, ch, "none", PURPLE, 2, "6,4")
d.img(CWAN, cx0, cy0, 24)
d.text(cx0 + 32, cy0 + 19, "Cloud WAN core network", F_TITLE, PURPLE, "600")
d.text(cx0 + 32, cy0 + 37, "서울 edge AS 64512 · 오레곤 edge AS 64513", F_SUB, INK)

VPCS = {
    "dev": ("dev VPC", "10.20.1.0/24", "10.20.1.10"),
    "prod": ("prod VPC", "10.10.1.0/24", "10.10.1.10"),
    "shared": ("shared VPC", "10.30.1.0/24", "10.30.1.10"),
}


def vpc_box(x, y, title, cidr, ip, nid):
    d.group(x, y, VPCW, VPCH, "vpc", title, cidr)
    d.group(x + 16, y + 50, 208, 100, "sg", "SG: ICMP 허용")
    grp(nid)
    d.img(EC2, x + 62 - S / 2, y + 104 - S / 2)
    d.side(x + 98, y + 104, [("EC2", "name"), (ip, "sub")])
    end()


for seg, ly, vy, cy in ROWS:
    t, cidr, ip = VPCS[seg]
    vpc_box(38, vy, t, cidr, ip, f"ec2-{seg}")
vpc_box(884, 308, "prod VPC", "10.11.1.0/24", "10.11.1.10", "ec2-prod-or")

# ---------------- 세그먼트 레인 ----------------
for seg, ly, vy, cy in ROWS:
    d.rect(LANE_X, ly, LANE_W, LANE_H, "none", PURPLE, 1.5)
    d.img(SEG, LANE_X, ly, 24)
    d.text(LANE_X + 32, ly + 19, f"{seg} 세그먼트", F_TITLE, PURPLE, "600")
    grp(f"att-{seg}")
    d.img(ATT, AX_S - S / 2, cy - S / 2)
    d.text(AX_S, cy + 44, "VPC attachment", F_NODE, INK, None, "middle")
    d.text(AX_S, cy + 65, f"서울 {seg} VPC", F_SUB, SUB, None, "middle")
    end()
    # VPC -> attachment (연결 자체, 화살표 없음)
    d.line(278, cy, AX_S - S / 2 - 4, cy)

# 오레곤 prod attachment
grp("att-prod-or")
d.img(ATT, AX_O - S / 2, OY - S / 2)
d.text(AX_O, OY + 44, "VPC attachment", F_NODE, INK, None, "middle")
d.text(AX_O, OY + 65, "오레곤 prod VPC", F_SUB, SUB, None, "middle")
end()
d.line(AX_O + S / 2 + 4, OY, 884, OY)

# ---------------- 번호가 붙은 단계 ----------------
# 3) attachment 생성 + segment=prod 태그
x0, x1 = d.tag(AX_O - 20, 372, "segment=prod 태그", INK, "middle")
badge(x0 - 18.5, 366.5, 3)
# 4) attachment policy 가 prod 세그먼트에 배정
badge(793.5, OY - 14.5, 4)
# 1) prod -> dev 실패
d.line(AX_S, 342, AX_S, 300, RED_A, 2, "6,4", "arrowRed")
badge(440, 319.5, 1)
bx0, bx1 = d.tag(490, 325, "차단", RED_A)
d.text(bx1 + 10, 325, "실패: 100% packet loss", F_SUB, RED_A, "600")
# 2) prod -> shared 성공
d.line(AX_S, 496, AX_S, 534, GREEN_A, 2, None, "arrowGreen")
badge(440, 515, 2)
d.text(490, 519, "성공: 응답 있음", F_SUB, GREEN_A, "600")
# 5) 서울 prod -> 오레곤 prod 성공
d.line(AX_S + S / 2 + 4, OY, AX_O - S / 2 - 8, OY, GREEN_A, 2, None, "arrowGreen")
badge(528, OY - 14.5, 5)
d.text(546, OY - 10, "성공: 응답 있음", F_SUB, GREEN_A, "600")

# ---------------- 단계 범례 (하단 패널) ----------------
d.rect(16, PANEL_Y, W - 32, PANEL_H, "#F8F9F9", "#D5DBDB", 1)
STEPS = [
    ("서울 prod → 서울 dev (실패)",
     "세그먼트는 기본 격리. 보안 그룹은 ICMP 허용인데도 경로가 없어 100% 유실."),
    ("서울 prod → 서울 shared (성공)",
     "정책의 share(shared → prod·dev·onprem)로 shared 경로만 prod에 전파."),
    ("오레곤 prod attachment 생성",
     "참가자가 VPC attachment를 만들고 segment=prod 태그를 붙입니다."),
    ("attachment policy 규칙 100",
     "tag-exists: segment 조건이 태그 값대로 prod 세그먼트에 자동 배정 (참가자가 고르지 않음)."),
    ("서울 prod → 오레곤 prod (성공)",
     "서울 edge AS 64512 ↔ 오레곤 edge AS 64513은 이미 연결. prod 경로가 리전 간 자동 전파."),
]
HOP_X = 66
DESC_X = HOP_X + max(tw(h, F_SUB) for h, _ in STEPS) + 18
for i, (hop, desc) in enumerate(STEPS):
    base = PANEL_Y + 30 + 30 * i
    badge(44, base - 5.5, i + 1)
    d.text(HOP_X, base, hop, F_SUB, INK, "600")
    d.text(DESC_X, base, desc, F_SUB, SUB)

open(OUT, "w").write(d.svg(W, H, markers("arrow", "arrowGreen", "arrowRed")))
print("canvas", W, H, "| min font @900px:", round(F_SUB * 900 / W, 2),
      "| desc x", round(DESC_X), "widest row end",
      round(max(DESC_X + tw(x[1], F_SUB) for x in STEPS)), "/ panel right", W - 16)
