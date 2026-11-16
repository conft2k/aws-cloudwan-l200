# 4-4. 참고 문서

이 워크숍을 만들면서 확인한 공식 문서입니다. 용어의 뜻은 [1-3. 용어 풀이](glossary.md)에 있습니다.

!!! warning "이 워크숍에서 확인하지 못한 것"
    아래 문서에 적힌 사양은 2026년 11월에 확인했지만, 워크숍 자체의 **실측값은 아직 없습니다.** 다음은 사전 테스트에서 측정해 채울 항목입니다.

    - 각 단계의 실제 소요 시간(core network 최초 생성, 연결이 **Available**이 되기까지, policy version 생성부터 change set 생성까지, change set 실행부터 통신이 되기까지, 스택 삭제)
    - CloudFormation이 `PolicyDocument`를 넣어 core network를 **처음 만들 때** change set이 자동으로 실행되어 `LIVE`까지 가는지. 공식 문서는 정책을 **갱신**할 때의 동작만 적습니다
    - 스택이 `CREATE_COMPLETE`가 된 시점과 core network를 실제로 쓸 수 있는 시점이 같은지
    - 서울 리전 스택에서 global network와 core network를 만들 수 있는지(Cloud WAN의 홈 리전은 `us-west-2`입니다)
    - Direct Connect gateway attachment의 시간당 요금. 숫자는 지어내지 않고 [요금 페이지](https://aws.amazon.com/cloud-wan/pricing/)로 넘겼습니다([4-2-g](direct-connect.md#dx-pricing))

    진행표의 시간은 모두 **추정값**입니다.

## 4-4-a. 개념 { #ref-concept }

- [What is AWS Cloud WAN?](https://docs.aws.amazon.com/network-manager/latest/cloudwan/what-is-cloudwan.html) — Cloud WAN의 구성 요소(global network, core network, core network edge, 세그먼트, 연결)와 홈 리전이 `us-west-2`라는 사실
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
- [Peering](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-peerings.html) — Transit Gateway peering과 route table attachment. Transit Gateway가 같은 리전에 있어야 하고 ASN이 서로 달라야 합니다. 비교는 [3-2. Transit Gateway와 비교](extra-b.md)에 있습니다

## 4-4-d. 운영 { #ref-ops }

- [Creating a core network policy version](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-create-policy-version.html) — 새 policy version을 만드는 방법, change set의 상태 값, 이전 버전으로 되돌리는 방법. `share`가 기본적으로 양방향이라는 설명도 여기 있습니다
- [Deploying a core network policy version](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policy-version-deploy.html) — change set을 실행해 `LIVE`로 만드는 방법. **"Deploying a new policy version never occurs automatically."** 라는 문장이 있습니다. 실습 [2-4](lab3.md)의 핵심입니다
- [Regional scope of policy changes](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policy-regional-scope.html) — 어떤 정책 변경이 어느 core network edge를 갱신하는지 정리한 표. 변경 창을 잡을 때 먼저 보세요([4-1-f](concepts.md#change))

## 4-4-e. 요금과 한도 { #ref-cost }

- [AWS Cloud WAN quotas](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-quotas.html) — 계정당 global network 5개, global network당 core network 1개(조정 불가), 리전당 edge 1개(조정 불가), VPC당 core network 연결 5개(조정 불가) 등. 주요 숫자는 [4-1-g](concepts.md#quotas)에 옮겨 두었습니다
- [AWS Cloud WAN 요금](https://aws.amazon.com/cloud-wan/pricing/) — core network edge 시간 요금, 연결 시간 요금, 데이터 전송 요금. 실습 비용을 가늠하거나 정리를 서둘러야 하는 이유를 확인할 때 보세요([3-4. 리소스 정리](extra-d.md))
