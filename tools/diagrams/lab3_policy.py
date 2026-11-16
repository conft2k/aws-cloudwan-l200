"""Generate docs/images/diagrams/lab3-policy.draft.svg (layout source).

실습 2-4: core network policy 의 segment-actions 에 share 한 줄을 넣으면 통신 범위가 바뀐다.
위(정책 변경 전) / 가운데(추가하는 JSON 조각) / 아래(정책 변경 후) 를 같은 좌표로 그려,
바뀐 것이 onprem -> prod 하나뿐이라는 점이 한눈에 보이게 한다.

세그먼트/대역/정책 값은 PLAN.md 3-1, 3-2, 9절을 따른다.
연결선은 도달 가능 여부(토폴로지)를 나타내므로 화살표를 쓰지 않고 레이블로 구분한다.
"""
import sys
from lib import D, markers, INK, SUB, GREY, PURPLE, F_SUB, F_TITLE, S

OUT = sys.argv[1]
OK = "#1D8102"      # 통신됨
NO = "#D13212"      # 차단
MONO = "'Noto Sans Mono CJK KR', monospace"
FM = 16             # JSON 조각 글자 크기

SEG = "resource/AWS-Cloud-WAN_Segment-Network"
VPCI = "service/Amazon-Virtual-Private-Cloud"
VPNI = "service/AWS-Site-to-Site-VPN"

d = D()

# --- x grid (both panels share it) -------------------------------------------
VPN_CX = 110
CORE_X, CORE_W = 280, 728           # core network container
ON_X, ON_W = 294, 170               # onprem segment box
SEG_X = 540                         # segment boxes on the right
PROD_W, OTH_W = 369, 250
BOX_H, GAP = 118, 44                # 세그먼트 박스 높이와 행 간격
CORE_H = 36 + 3 * BOX_H + 2 * GAP + 16
SEG_CX, V1_CX, V2_CX = 590, 720, 850
COR_X = 938                         # corridor for the prod <-> dev line
W = CORE_X + CORE_W + 16


def link(pts, ok, label, lx, ly, anchor="middle", sw=2):
    """도달 가능(실선 + 통신됨) / 차단(점선 + 차단) 선 하나와 그 레이블."""
    color = OK if ok else NO
    d.poly(pts, stroke=color, sw=sw, dash=None if ok else "5,4")
    d.text(lx, ly, label, F_SUB, color, "700", anchor)


def segbox(x, y, w, h, name, members):
    """세그먼트 박스: 회색 점선 + Segment network 아이콘과 세그먼트 이름 + 멤버 노드."""
    d.rect(x, y, w, h, "none", GREY, 1.5, "6,3")
    cy = y + 36
    d.node(SEG, SEG_CX, cy, [(name, "namebold")])
    for cx, (ref, lines) in zip((V1_CX, V2_CX), members):
        d.node(ref, cx, cy, lines)
    return cy


def panel(ct, after):
    """core top 이 ct 인 패널 하나. after=True 면 onprem -> prod 가 열린 상태."""
    R = ct + 36
    r1, r2, r3 = R, R + BOX_H + GAP, R + 2 * (BOX_H + GAP)   # prod / shared / dev row
    cy1, cy2, cy3 = r1 + 36, r2 + 36, r3 + 36

    # core network container
    d.rect(CORE_X, ct, CORE_W, CORE_H, "none", PURPLE, 2, "6,4")
    d.img("service/AWS-Cloud-WAN", CORE_X, ct, 24)
    d.text(CORE_X + 32, ct + 19, "Core network", F_TITLE, PURPLE, "600")

    # on-premises side: Site-to-Site VPN attachment
    d.node(VPNI, VPN_CX, cy2, [("Site-to-Site VPN", "name"),
                               ("온프레미스 LAN", "sub")])
    d.line(VPN_CX + S / 2 + 4, cy2, ON_X - 4, cy2, INK, 1.5)
    d.text((VPN_CX + S / 2 + ON_X) / 2 - 4, cy2 - 10, "segment=onprem", F_SUB, SUB, None, "middle")

    # segment boxes
    d.rect(ON_X, r2, ON_W, BOX_H, "none", GREY, 1.5, "6,3")
    d.node(SEG, ON_X + ON_W / 2, cy2, [("onprem", "namebold")])
    segbox(SEG_X, r1, PROD_W, BOX_H, "prod",
           [(VPCI, [("prod VPC", "name"), ("서울", "sub")]),
            (VPCI, [("prod VPC", "name"), ("오레곤", "sub")])])
    segbox(SEG_X, r2, OTH_W, BOX_H, "shared", [(VPCI, [("shared VPC", "name"), ("서울", "sub")])])
    segbox(SEG_X, r3, OTH_W, BOX_H, "dev", [(VPCI, [("dev VPC", "name"), ("서울", "sub")])])

    ocx = ON_X + ON_W / 2
    # onprem <-> shared: 처음부터 통신됨 (shared 가 onprem 에 share)
    link([(ON_X + ON_W + 4, cy2), (SEG_X - 4, cy2)], True, "통신됨",
         (ON_X + ON_W + SEG_X) / 2, cy2 - 10)
    # onprem <-> prod: 정책으로 바뀌는 단 하나의 선
    up = [(ocx, r2 - 4), (ocx, cy1), (SEG_X - 4, cy1)]
    if after:
        link(up, True, "통신됨", (ocx + SEG_X) / 2, cy1 - 10, sw=3)
        d.tag((ocx + SEG_X) / 2, cy1 + 32, "정책에서 바뀐 부분", OK, "middle")
    else:
        link(up, False, "차단", (ocx + SEG_X) / 2 + 20, cy1 - 10)
    # onprem <-> dev: 전후 모두 차단 (고객 요구사항)
    link([(ocx, r2 + BOX_H + 4), (ocx, cy3), (SEG_X - 4, cy3)], False, "차단",
         (ocx + SEG_X) / 2 + 20, cy3 - 10)
    # shared <-> prod, shared <-> dev: 공유 서비스는 양쪽에서 쓴다
    link([(640, r1 + BOX_H + 4), (640, r2 - 4)], True, "통신됨", 650, (r1 + BOX_H + r2) / 2 + 6, "start")
    link([(700, r2 + BOX_H + 4), (700, r3 - 4)], True, "통신됨", 710, (r2 + BOX_H + r3) / 2 + 6, "start")
    # prod <-> dev: 세그먼트 기본 동작으로 차단
    link([(SEG_X + PROD_W + 4, cy1), (COR_X, cy1), (COR_X, cy3), (SEG_X + OTH_W + 4, cy3)],
         False, "차단", COR_X + 12, cy2 + 6, "start")


# --- 위: 정책 변경 전 ----------------------------------------------------------
d.text(16, 40, "정책 변경 전 — 온프레미스는 shared 에만 닿는다", F_TITLE, INK, "700")
panel(56, False)

# --- 가운데: 참가자가 추가하는 JSON 조각 ------------------------------------------
BY, BH = 56 + CORE_H + 24, 180
d.rect(16, BY, W - 32, BH, "#F8F9F9", "#D5DBDB", 1)
d.text(36, BY + 32, "실습 2-4 — segment-actions 에 share 한 줄 추가", F_TITLE, INK, "700")
for i, t in enumerate(["policy version 생성 → change set 검토 → 실행",
                       "리전별 설정 없이 서울 · 오레곤 prod 양쪽이 함께 열린다",
                       "dev 격리는 그대로 둔다 (고객 요구사항)"]):
    d.text(36, BY + 68 + i * 26, t, F_SUB, SUB)

JX, JY = 560, BY + 12
JSON = ['{', '  "action": "share",', '  "mode": "attachment-route",',
        '  "segment": "onprem",', '  "share-with": ["prod"]', '}']
jw = max(len(s) for s in JSON) * FM * 0.62 + 32
d.rect(JX, JY, jw, BH - 24, "#FFFFFF", "#D5DBDB", 1)
for i, s in enumerate(JSON):
    d.raw(f'<text x="{JX + 16:g}" y="{JY + 30 + i * 22:g}" font-size="{FM}" '
          f'font-family="{MONO}" fill="{INK}">{s}</text>')

# --- 아래: 정책 변경 후 ----------------------------------------------------------
d.text(16, BY + BH + 32, "정책 변경 후 — onprem → prod 만 열렸다", F_TITLE, INK, "700")
panel(BY + BH + 48, True)

H = BY + BH + 48 + CORE_H + 16
open(OUT, "w").write(d.svg(W, H, markers()))
print(f"{OUT}  {W} x {H}")
