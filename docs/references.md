# 4-4. 참고 문서

이 워크숍의 설명이 근거로 삼은 공식 문서입니다. 용어의 뜻은 [1-3. 용어 풀이](glossary.md)에 있습니다.

## 4-4-a. 개념 { #ref-concept }

- [What is AWS Cloud WAN?](https://docs.aws.amazon.com/network-manager/latest/cloudwan/what-is-cloudwan.html) — Cloud WAN의 구성 요소(global network, core network, core network edge, 세그먼트, 연결)와 지원 리전. 홈 리전이 `us-west-2`라는 것은 Network Manager API와 콘솔의 홈 리전을 뜻하며, core network edge는 지원 리전 어디에나 둘 수 있습니다
- [Getting started with AWS Cloud WAN](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-getting-started.html) — core network를 처음 만드는 순서. **core network 최초 생성이 최대 30분 걸리고 그 동안 연결 생성과 정책 편집이 막힌다**는 설명이 여기 있습니다. 워크숍이 스택 배포를 이론 강의 전에 시작하는 이유입니다

## 4-4-b. 정책 { #ref-policy }

- [Core network policies — JSON policy document](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policies-json.html) — 정책 JSON의 모든 필드를 정의한 레퍼런스입니다. 이 묶음에서 가장 많이 보게 되는 문서입니다. 쉬운 설명은 [4-1](concepts.md)에 있습니다
- [Core network configuration](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-core-network-config.html) — 콘솔에서 `asn-ranges`와 edge location을 다루는 방법. ASN 범위가 끝 값을 포함하지 않는다는 설명이 있습니다
- [Attachment policies](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policy-attachments.html) — 연결을 세그먼트에 배정하는 규칙. 규칙이 맞으면 더 이상 다음 규칙을 보지 않는다는 평가 순서를 설명합니다
- [Core network policy examples](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policy-examples.html) — 공식 정책 예시 모음. 공유 서비스 패턴(`share`)의 원본입니다
- [Three-stage environment example](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policy-examples-three-stage.html) — 운영·개발·공유를 세 세그먼트로 나눈 예시. 이 워크숍의 세그먼트 설계가 여기서 왔습니다. `tag-exists` 조건과 `association-method: tag` 규칙이 쓰인 예시이기도 합니다

## 4-4-c. 연결 { #ref-attachment }

- [Core network attachments](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-create-attachment.html) — 지원하는 연결 종류의 목록과 공통 생성 절차
- [VPC attachments](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-vpc-attachment.html) — VPC를 붙이는 방법. 가용 영역당 서브넷을 하나씩 고릅니다. 실습 [2-2-d](lab1.md#lab1-d)에서 직접 만듭니다
- [Site-to-Site VPN attachments](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-s2s-vpn-attachment.html) — VPN 연결을 **Target Gateway Type = Not Associated**로 만들어야 한다는 전제, core network를 소유한 계정에서 만들어야 한다는 전제, core network에 attach하기 전에는 VPN 엔드포인트가 프로비저닝되지 않는다는 설명
- [Create a VPN attachment](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-vpn-attachment-add.html) — 콘솔에서 VPN attachment를 만드는 절차. 실습 [2-3-b](lab2.md#lab2-b)에 해당합니다
- [Create a Cloud WAN VPN attachment (Site-to-Site VPN 가이드)](https://docs.aws.amazon.com/vpn/latest/s2svpn/create-cwan-vpn-attachment.html) — VPN 쪽에서 본 같은 작업. Cloud WAN용 VPN은 **BGP 동적 라우팅이 필수**이고 정적 라우팅을 지원하지 않습니다(CLI에서는 `StaticRoutesOnly=false`)
- [Direct Connect gateway attachments](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-dxattach-about.html) — Transit Gateway 없이 전용선을 붙이는 방법과 그 제약. 정리는 [4-2](direct-connect.md)에 있습니다
- [Create a Direct Connect gateway attachment](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-dxattachment-add.html) — 콘솔 절차와 **Edge locations**의 **All**·**Specific** 선택
- [AWS Cloud WAN and AWS Direct Connect (Direct Connect 가이드)](https://docs.aws.amazon.com/directconnect/latest/UserGuide/direct-connect-cloud-wan.html) — Direct Connect 쪽에서 본 같은 기능. 전송 가상 인터페이스(transit VIF)를 쓴다는 것과, 연결 관리는 Cloud WAN 콘솔에서만 한다는 설명
- [Peering](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-peerings.html) — Transit Gateway peering과 route table attachment. Transit Gateway가 같은 리전에 있어야 하고 ASN이 서로 달라야 합니다. 비교는 [3-2. Transit Gateway와 비교](extra-b.md)에 있고, 기존 Transit Gateway를 둔 채 단계적으로 옮겨 가는 방법([3-2-d](extra-b.md#b-d))도 이 문서에서 출발합니다

## 4-4-d. 운영 { #ref-ops }

- [Creating a core network policy version](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-create-policy-version.html) — 새 policy version을 만드는 방법, change set의 상태 값, 이전 버전으로 되돌리는 방법. `share`가 기본적으로 양방향이라는 설명도 여기 있습니다
- [Deploying a core network policy version](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policy-version-deploy.html) — change set을 실행해 `LIVE`로 만드는 방법. **"Deploying a new policy version never occurs automatically."** 라는 문장이 있습니다. 실습 [2-4](lab3.md)의 핵심입니다
- [Regional scope of policy changes](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policy-regional-scope.html) — 어떤 정책 변경이 어느 core network edge를 갱신하는지 정리한 표. 변경 창을 잡을 때 먼저 보세요([4-1-f](concepts.md#change))

## 4-4-e. 요금과 한도 { #ref-cost }

### 무엇에 요금이 붙나 { #ref-pricing }

**시간 요금이 핵심입니다.** 만들어 둔 것은 쓰지 않아도 시간당 요금이 붙고, **부분 시간은 올림**입니다. [3-4. 리소스 정리](extra-d.md)를 서둘러야 하는 이유가 이것입니다.

| 요금이 붙는 것 | 단위 | 이 워크숍에서는 |
|---|---|---|
| core network edge | **리전당 시간당 $0.50** | 서울과 오레곤 **2개**. 가장 큰 항목입니다 |
| 연결(attachment) | 연결당 **시간당 $0.065~0.09** | VPC 연결 4~5개와 VPN 연결 1개. 리전과 종류에 따라 다르고 오레곤이 더 쌉니다 |
| 데이터 전송 | GB당 | ping과 HTTP 요청 몇 번뿐이라 사실상 0입니다 |
| Site-to-Site VPN 연결 | 연결당 시간당 | [2-3-a](lab2.md#lab2-a)에서 만드는 VPN 연결 1개. Cloud WAN이 아니라 VPN 쪽 요금입니다 |
| EC2 인스턴스 | 인스턴스당 시간당 | 스택이 만드는 테스트용 EC2 |
| CloudWatch Logs | 수집·저장량 | [3-3-e](extra-c.md#c-e)의 이벤트 로그를 켰을 때만 붙습니다 |

금액은 공개된 목록 가격이고 바뀔 수 있습니다. 기준은 늘 공식 요금 페이지입니다.

- [AWS Cloud WAN 요금](https://aws.amazon.com/cloud-wan/pricing/) — core network edge 시간 요금, 연결 시간 요금, 데이터 전송 요금
- [Site-to-Site VPN 요금](https://aws.amazon.com/vpn/pricing/) — VPN 연결 시간 요금

### 한도 { #ref-quotas }

정책을 설계할 때 먼저 보는 숫자들입니다. **조정 불가**인 넷(global network당 core network 1개, 리전당 edge 1개, VPC당 연결 5개, 정책 문서 1 MB)이 설계를 가장 많이 가릅니다.

| 항목 | 기본값 | 조정 |
|---|---|---|
| 계정당 global network | 5 | 가능 |
| global network당 core network | 1 | **불가** |
| 리전당 core network edge | 1 | **불가** |
| core network당 세그먼트 | 40 | 문서에 "Contact your SA or TAM"으로 적혀 있습니다. SA는 솔루션 아키텍트(Solutions Architect), TAM은 기술 계정 관리자(Technical Account Manager)로, AWS 쪽 담당자입니다 |
| core network당 연결(attachment) | 5,000 | 가능 |
| VPC당 core network 연결 | 5 | **불가** |
| core network당 경로 | 10,000 | 문서에 "Contact your SA or TAM"으로 적혀 있습니다 |

읽을 때 주의할 점을 덧붙입니다.

- **global network당 core network는 1개**이고 조정할 수 없습니다. core network를 둘 쓰려면 global network를 둘 만들어야 합니다. 계정당 global network는 5개까지입니다.
- **리전당 edge는 1개**입니다. 한 리전에 core network edge를 둘 둘 수 없습니다. Transit Gateway를 리전에 여러 개 두던 방식과 다른 점입니다.
- **core network당 경로 10,000개**는 모든 세그먼트의 경로를 합한 숫자입니다. 정적 경로, 공유로 받은 경로, 동적으로 배운 경로를 모두 셉니다. BGP로 받았지만 설치되지 않은 경로는 세지 않습니다.
- 그 밖에 정책 문서 크기 1 MB(조정 불가), core network당 정책 버전 10,000개, 연결당 Connect peer 4개(조정 불가), core network당 Direct Connect 연결 40개(조정 가능), VPN을 통해 core network에 광고하는 경로 1,000개가 있습니다.

- [AWS Cloud WAN quotas](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-quotas.html) — 원문. 조정 가능 여부가 항목마다 적혀 있습니다
