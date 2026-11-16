# 4-2. Direct Connect로 연결할 때

이 워크숍은 온프레미스를 AWS 안의 "온프레미스 모사 VPC"와 Site-to-Site VPN으로 흉내 냈습니다([2-3](lab2.md)). 실습 1시간 안에 전용선 연결까지 다루기 어렵기 때문입니다. 하지만 실제 고객 환경에서 온프레미스를 붙이는 수단은 대개 AWS Direct Connect(전용선)입니다.

이 페이지는 실제 회선을 쓸 때 무엇이 달라지는지 정리합니다. 결론부터 말하면, **Transit Gateway 없이 Direct Connect gateway를 Cloud WAN core network에 바로 붙일 수 있습니다.**

## 4-2-a. Transit Gateway 없이 바로 붙입니다 { #dx-attach }

전에는 전용선으로 들어온 온프레미스를 여러 VPC에 연결하려면 Direct Connect gateway(DX gateway)를 Transit Gateway에 연결(gateway association)하고, 그 Transit Gateway를 다시 Cloud WAN에 peering하는 식으로 중간 단계를 거쳐야 했습니다.

Cloud WAN은 **Direct Connect gateway attachment**를 지원합니다. 공식 문서의 문장은 "directly attach your Direct Connect gateways to Cloud WAN without the need for an intermediate AWS Transit Gateway"입니다. 중간의 Transit Gateway가 필요 없습니다.

- 연결에는 **전송 가상 인터페이스(transit VIF, Virtual Interface)** 를 씁니다. **VIF는 물리 회선 하나 위에 논리적으로 나누어 만드는 연결**입니다. 회선 하나에 여러 VIF를 만들 수 있고 종류마다 닿는 곳이 다릅니다. 그중 DX gateway에 붙는 종류가 transit VIF이고, Cloud WAN은 이것을 씁니다. 공식 문서의 문장은 "The Cloud WAN Direct Connect gateway attachment uses the transit virtual interface type for connectivity."입니다.
- 경로는 BGP(Border Gateway Protocol)로 주고받습니다. Cloud WAN은 DX gateway와 transit VIF를 통해 온프레미스가 광고한 경로를 배웁니다.
- 세그먼트 배정은 다른 연결과 똑같습니다. [4-1-e](concepts.md#attachment)의 attachment policy가 그대로 적용되므로, 실습에서 쓴 `segment` 태그 규칙이 DX 연결에도 그대로 동작합니다.

출처: [Direct Connect gateway attachments in Cloud WAN](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-dxattach-about.html), [AWS Cloud WAN and Direct Connect](https://docs.aws.amazon.com/directconnect/latest/UserGuide/direct-connect-cloud-wan.html)

## 4-2-b. 전제와 제약 { #dx-limits }

VPN 연결과 달리 DX gateway attachment에는 지켜야 할 조건이 여럿 있습니다. 설계 단계에서 미리 확인하세요.

| 조건 | 내용 |
|---|---|
| core network는 하나만 | 한 DX gateway는 core network 하나에만 연결됩니다. 공식 문서의 문장은 "Only one core network can be associated with a Direct Connect gateway."입니다 |
| 다른 용도와 겸할 수 없음 | core network에 연결되어 있는 동안 그 DX gateway는 다른 게이트웨이 유형에 쓸 수 없습니다. 여기에는 virtual private gateway(가상 프라이빗 게이트웨이), Transit Gateway, private VIF가 모두 들어갑니다. 연결을 끊으면 다시 쓸 수 있습니다 |
| 정적 경로의 next hop 불가 | core network policy의 정적 경로(`create-route`)에서 DX gateway attachment를 목적지로 지정할 수 없습니다. 경로는 BGP로 동적으로 광고되어야 합니다 |
| allowed prefixes 불가 | Transit Gateway 연결에서 쓰던 allowed prefixes(허용된 접두사) 목록을 설정할 수 없습니다. DX 가이드는 세그먼트에 있는 모든 접두사가 그 세그먼트에 연결된 DX gateway로 광고된다고 적습니다 |
| ASN 범위 | DX gateway의 ASN(Autonomous System Number, 자율 시스템 번호)은 core network policy의 `asn-ranges` **밖**이어야 합니다 |
| 한 세그먼트 | DX 가이드는 DX gateway가 core network의 세그먼트 하나에만 연결된다고 적습니다 |

!!! warning "ASN을 겹치지 않게 정하세요"
    실습 정책의 `asn-ranges`는 `64512-64520`입니다([4-1-b](concepts.md#config)). 여기에 DX gateway를 붙인다면 DX gateway의 ASN은 이 범위 밖이어야 합니다. core network edge의 ASN은 만든 뒤에 바꿀 수 없으므로, 전용선을 붙일 계획이 있다면 범위를 처음에 넉넉히 떼어 두세요.

!!! info "allowed prefixes가 없다는 뜻"
    Transit Gateway에서는 게이트웨이 연결에 적은 접두사만 온프레미스로 광고됐습니다. Cloud WAN의 DX attachment에는 그 설정이 없으므로, 온프레미스로 무엇을 광고할지는 **세그먼트 설계와 `share`로** 정하게 됩니다. 이 페이지에서 설명한 정책 설계가 그대로 광고 범위가 됩니다.

추가로, DX attachment를 transport 유형으로 쓸 때는 Private IP VPN attachment와 Connect attachment가 지원되지 않습니다.

출처: [Direct Connect gateway attachments in Cloud WAN](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-dxattach-about.html), [AWS Cloud WAN and Direct Connect](https://docs.aws.amazon.com/directconnect/latest/UserGuide/direct-connect-cloud-wan.html)

## 4-2-c. 한도 { #dx-quotas }

| 항목 | 기본값 | 조정 |
|---|---|---|
| core network당 Direct Connect attachment | 40 | 가능 |
| Direct Connect gateway당 core network attachment | 1 | **불가** |
| Direct Connect attachment당 outbound 경로 | 5,000 | 가능 |

"DX gateway당 core network attachment 1개"가 조정 불가라는 점이 설계에 가장 크게 영향을 줍니다. core network를 둘 운영하면서 같은 전용선을 양쪽에 쓰는 구성은 만들 수 없습니다.

출처: [Cloud WAN quotas](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-quotas.html)

## 4-2-d. 어느 콘솔에서 관리하나 { #dx-console }

DX gateway 자체는 **Direct Connect** 콘솔에서 먼저 만듭니다. 하지만 core network와의 연결(association)은 다릅니다.

- **만들고 지우고 관리하는 것은 Cloud WAN(Network Manager) 콘솔과 API뿐입니다.** 공식 문서의 문장은 "The association between a core network and a Direct Connect gateway is created, deleted, and managed from the Cloud WAN Console in Network Manager."입니다.
- Direct Connect 콘솔·API·CLI에서는 그 연결이 **보이기만** 합니다. 연결이 만들어졌는지 확인하는 조회는 되지만 수정은 되지 않습니다.

AWS CLI로 만들 때 쓰는 명령은 `create-direct-connect-gateway-attachment`입니다.

!!! tip "운영에서 헷갈리기 쉬운 부분입니다"
    Transit Gateway 시절에는 게이트웨이 연결을 Direct Connect 콘솔에서 다뤘습니다. Cloud WAN에서는 반대입니다. Direct Connect 콘솔에서 연결을 지우려다 메뉴를 못 찾는 일이 생기면, Network Manager 쪽을 보세요.

출처: [AWS Cloud WAN and Direct Connect](https://docs.aws.amazon.com/directconnect/latest/UserGuide/direct-connect-cloud-wan.html), [Create a Direct Connect gateway attachment](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-dxattachment-add.html)

## 4-2-e. edge location을 고르는 방법 { #dx-edge }

Network Manager 콘솔에서 **Create attachment** → **Attachment type**에서 **Direct Connect gateway**를 고르면, **Edge locations** 항목에서 두 가지 중 하나를 고릅니다.

| 선택 | 동작 |
|---|---|
| **All** | core network의 모든 edge location에 연결합니다. 새 정책 버전으로 edge를 **추가**하면 자동으로 따라 추가됩니다. 그런데 정책에서 edge를 **제거**해도 자동으로 갱신되지 않습니다 |
| **Specific** | 고른 edge에만 연결합니다. 정책 버전을 배포한 뒤 edge를 직접 추가하거나 제거해야 합니다 |

!!! warning "All로 두어도 제거는 따라오지 않습니다"
    공식 문서는 **All**이 새로 배포된 edge location은 자동으로 추가하지만, core network policy에서 제거한 edge location은 자동으로 갱신하지 않는다고 적습니다. 리전을 접을 때는 DX attachment의 edge 목록을 직접 확인하세요.

출처: [Create a Direct Connect gateway attachment](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-dxattachment-add.html)

## 4-2-f. 온프레미스를 붙이는 네 가지 방법 { #dx-compare }

Cloud WAN에 온프레미스나 외부 네트워크를 붙이는 방법을 모아 비교합니다.

| 방법 | 전제 | 쓰는 상황 |
|---|---|---|
| **Site-to-Site VPN attachment** | 인터넷 회선과 공인 IP를 가진 라우터. VPN 연결을 **Target Gateway Type = Not Associated**로 만들어야 하고, core network를 소유한 계정에서 만들어야 합니다. BGP 동적 라우팅 필수(정적 라우팅은 지원하지 않습니다) | 가장 빨리 붙입니다. 이 워크숍이 쓴 방법입니다. 지사·소규모 거점, 전용선 개통 전의 임시 연결, 전용선의 백업 |
| **Connect attachment (GRE)** | 기존 attachment 위에 GRE(Generic Routing Encapsulation) 터널을 얹습니다. core network edge에 **inside CIDR block이 반드시 설정되어 있어야 합니다**([4-1-b](concepts.md#config)) | 서드파티 SD-WAN(Software-Defined WAN) 장비나 가상 라우터를 Cloud WAN에 BGP로 붙일 때 |
| **Direct Connect gateway attachment** | 전용선과 transit VIF, 그리고 다른 용도로 쓰이지 않는 DX gateway. ASN은 core network 범위 밖 | 대역폭과 지연이 중요한 본사·데이터 센터. 이 페이지의 주제입니다 |
| **Transit Gateway peering** | Transit Gateway가 core network edge와 **같은 리전**에 있어야 하고, Transit Gateway와 core network의 ASN이 서로 달라야 합니다. 동적 전파 경로만 지원하며 정적 경로를 추가하면 오류가 납니다 | 이미 Transit Gateway로 지은 네트워크가 있고, 그것을 그대로 둔 채 Cloud WAN으로 옮겨 가는 중간 단계. peering 위에 route table attachment를 만들면 Transit Gateway 라우팅 테이블과 Cloud WAN 세그먼트 사이에서 경로를 골라 교환할 수 있습니다 |

고르는 기준을 한 줄로 정리하면 이렇습니다. **전용선이 이미 있으면 DX gateway attachment, 인터넷뿐이면 VPN attachment, 서드파티 장비를 끼우면 Connect attachment, 기존 Transit Gateway를 살려야 하면 peering입니다.**

!!! info "VPN attachment를 쓸 때의 순서"
    공식 문서는 core network에 attach하기 전에는 AWS가 VPN 엔드포인트를 프로비저닝하지 않는다고 적습니다. 그래서 VPN 연결만 먼저 만들어 두고 customer gateway 설정을 시작할 수는 없습니다. 실습 [2-3](lab2.md)에서 VPN 연결 → Cloud WAN attachment → 라우터 설정 순서로 진행하는 이유입니다.

출처: [Core network attachments](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-create-attachment.html), [Site-to-Site VPN attachments](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-s2s-vpn-attachment.html), [Create a Cloud WAN VPN attachment](https://docs.aws.amazon.com/vpn/latest/s2svpn/create-cwan-vpn-attachment.html), [Peering](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-peerings.html), [JSON policy document](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policies-json.html)

## 4-2-g. 요금 { #dx-pricing }

Cloud WAN은 core network edge 한 개당 시간 요금과 연결(attachment) 한 개당 시간 요금, 그리고 데이터 전송 요금으로 나뉩니다. 연결 요금은 연결 종류와 리전에 따라 다릅니다.

!!! warning "DX gateway attachment의 시간당 요금은 공식 가격 페이지에서 확인하세요"
    이 워크숍에서는 Direct Connect gateway attachment의 단가를 확인하지 않았습니다. 숫자가 필요하면 [AWS Cloud WAN 요금](https://aws.amazon.com/cloud-wan/pricing/) 페이지를 보세요. 전용선 자체의 포트 요금과 데이터 전송 요금은 Direct Connect 쪽에서 따로 청구됩니다.

출처: [AWS Cloud WAN 요금](https://aws.amazon.com/cloud-wan/pricing/)
