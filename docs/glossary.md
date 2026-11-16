# 1-3. 용어 풀이

워크숍에 자주 나오는 말을 쉽게 풀었습니다. 콘솔에 보이는 영어 이름을 함께 적었습니다.

## 1-3-a. Cloud WAN 관련 { #cloudwan }

| 용어 | 콘솔 이름 | 뜻 |
|---|---|---|
| global network | Global network | Network Manager에서 네트워크 리소스를 한데 모아 관리하는 가장 큰 상자. core network는 global network 안에 만듭니다 |
| core network | Core network | Cloud WAN이 관리하는 전 세계 네트워크 본체. 여러 리전의 연결을 하나의 정책으로 묶습니다 |
| core network edge(CNE) | Core network edge | 정책에 적은 리전(edge location)마다 AWS가 만들어 주는 연결 지점. VPC와 VPN은 같은 리전의 edge에 붙습니다 |
| edge location | Edge locations | core network edge를 둘 리전. 정책의 `edge-locations`에 적습니다. 이 워크숍은 서울과 오레곤입니다 |
| segment | Segments | core network 안의 분리된 경로 구역. 기본적으로 같은 세그먼트끼리만 통신합니다. 이 워크숍은 `prod`, `dev`, `shared`, `onprem` 네 개입니다 |
| attachment | Attachments | VPC나 VPN 같은 네트워크를 core network에 붙인 것. attachment 하나는 세그먼트 하나에만 속합니다. 어느 attachment policy 규칙에도 맞지 않으면 어느 세그먼트에도 들어가지 않습니다 |
| VPC attachment | VPC | VPC를 core network에 붙인 attachment. 리전마다 서브넷을 골라 연결합니다 |
| Site-to-Site VPN attachment | Site-to-Site VPN | Site-to-Site VPN 연결을 core network에 붙인 attachment. 온프레미스를 core network에 잇는 데 씁니다 |
| Connect attachment | Connect | 이미 붙여 둔 attachment 위에 GRE(Generic Routing Encapsulation) 터널을 얹어 AWS 밖의 네트워크 장비를 core network에 잇는 attachment. 이 워크숍에서는 쓰지 않고 [4-2-f](direct-connect.md#dx-compare)에서 비교만 합니다 |
| core network policy | Core network policy | core network의 리전, 세그먼트, 통신 규칙을 JSON(JavaScript Object Notation)으로 적은 문서. 정책 하나로 전체를 관리합니다 |
| policy version | Policy versions | 정책을 고칠 때마다 생기는 번호가 붙은 판. 현재 적용 중인 판은 `LIVE`로 표시됩니다 |
| change set | Change sets | 새 policy version을 적용했을 때 무엇이 바뀌는지 모은 목록. 검토한 뒤 실행해야 새 정책이 적용됩니다 |
| attachment policy | Attachment policies | attachment를 어느 세그먼트에 넣을지 정하는 규칙. 이 워크숍은 attachment의 `segment` 태그 값으로 정합니다 |
| segment action | Segment actions | 정책에서 세그먼트끼리의 경로를 정하는 규칙. 이 워크숍은 `share`를 씁니다 |
| share | `share` | 한 세그먼트의 경로를 다른 세그먼트에 알려 주어 둘이 통신하게 하는 segment action |
| isolate-attachments | Isolate attachments | 켜면 같은 세그먼트 안의 attachment끼리도 통신하지 못하게 하는 세그먼트 설정 |
| require-attachment-acceptance | Require attachment acceptance | 켜면 새 attachment를 사람이 수락해야 세그먼트에 들어가는 세그먼트 설정. 이 워크숍은 꺼 둡니다 |

## 1-3-b. 연결과 라우팅 관련 { #network }

| 용어 | 콘솔 이름 | 뜻 |
|---|---|---|
| ASN(Autonomous System Number) | ASN | BGP에서 한 조직이 관리하는 네트워크(자율 시스템)를 구분하는 번호. 이 워크숍은 서울 edge 64512, 오레곤 edge 64513, 온프레미스 라우터 65000을 씁니다 |
| BGP(Border Gateway Protocol) | — | 라우터끼리 "이 대역은 나에게 보내라"고 경로를 알려 주는 방법. 알려 주는 것을 **광고**라고 합니다 |
| customer gateway | Customer gateways | AWS에 "내 온프레미스 라우터는 이 공인 IP와 ASN을 쓴다"고 알려 주는 리소스 |
| IPsec 터널 | Tunnel | 인터넷 위에서 데이터를 암호화해 보내는 가상 통로. Site-to-Site VPN 연결 하나에 터널이 2개 있습니다 |
| inside CIDR block | Inside IPv4 CIDR | 터널 양 끝이 BGP 대화에 쓰는 작은 주소 대역(`169.254.0.0/16` 안의 `/30`). 데이터가 오가는 대역과는 다릅니다 |
| 경로 전파(propagation) | Route type `PROPAGATED` | 연결이 알린 대역이 세그먼트의 경로 테이블에 자동으로 올라오는 것. 경로의 **Route type** 이 `PROPAGATED` 이고 **Route state** 가 `ACTIVE` 이면 쓸 수 있는 경로입니다. 참가자가 직접 넣은 경로가 아닙니다 |
| Transit Gateway | Transit gateways | 리전 안에서 VPC와 온프레미스를 허브처럼 이어 주는 AWS 서비스. Cloud WAN은 여러 리전을 정책으로 묶습니다 |
| Transit Gateway peering | Peering attachment | 서로 다른 Transit Gateway를 이어 주는 연결. Cloud WAN과 기존 Transit Gateway를 이을 때도 씁니다 |
| Transit Gateway route table attachment | Transit gateway route table | Transit Gateway의 라우팅 테이블을 Cloud WAN 세그먼트에 잇는 attachment. 기존 Transit Gateway를 그대로 둔 채 단계적으로 옮겨 갈 때 씁니다([3-2-d](extra-b.md#b-d)) |
| Direct Connect gateway | Direct Connect gateways | Direct Connect 회선을 여러 리전의 Transit Gateway나 가상 게이트웨이에 이어 주는 AWS 리소스. 이 워크숍에서는 만들지 않고 [4-2](direct-connect.md)에서 설명만 합니다 |

## 1-3-c. 실습 도구 관련 { #tools }

| 용어 | 콘솔 이름 | 뜻 |
|---|---|---|
| CloudFormation 스택 | Stacks | 템플릿 하나로 만든 AWS 리소스 묶음. 스택을 지우면 묶음이 함께 지워집니다 |
| EC2 Instance Connect Endpoint | EC2 Instance Connect Endpoint | 공인 IP가 없는 EC2에 브라우저로 접속하게 해 주는 VPC 안의 입구 |
| strongSwan | — | 온프레미스 라우터 역할을 하는 EC2에서 IPsec 터널을 맡는 프로그램. 터널 상태는 `swanctl --list-sas` 로 봅니다 |
| FRR | — | 같은 EC2에서 BGP를 맡는 라우팅 프로그램(FRRouting). 상태는 `vtysh -c '...'` 명령으로 봅니다 |
