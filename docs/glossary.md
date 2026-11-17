# 1-3. 용어 풀이

워크숍에 자주 나오는 말을 쉽게 풀었습니다. 콘솔에 보이는 영어 이름을 함께 적었습니다.

## 1-3-a. Cloud WAN 관련 { #cloudwan }

표를 읽기 전에 **무엇이 무엇 안에 들어 있는지**부터 봅니다. 아래 용어가 모두 이 그림 안에 있습니다.

<figure markdown="span">
  ![AWS Cloud WAN의 구성요소와 포함 관계를 보여 주는 그림. 가장 바깥이 AWS Cloud 상자이고 그 안에 global network(Network Manager) 상자가 있다. global network 안에는 서울 ap-northeast-2와 오레곤 us-west-2 두 리전 상자가 나란히 서 있고, 각 리전 상자의 제목 아래에 edge location이라고 적혀 있다. 두 리전 상자를 가로로 가로지르는 보라색 파선 상자가 core network다. core network 안에는 세그먼트 네 개가 가로 행으로 놓여 있다. 위에서부터 segment prod(운영 환경), segment dev(개발 환경), segment shared(공유 서비스)가 있고, 가운데 edge 행을 사이에 두고 그 아래에 segment onprem(온프레미스)이 있다. 세그먼트 행은 리전 상자의 경계를 넘어 두 리전에 걸쳐 있다. 가운데 줄에는 리전마다 하나씩 Core network edge가 있는데 왼쪽이 서울 edge, 오른쪽이 오레곤 edge이고 둘은 AWS 백본이라고 적힌 선으로 이어져 있다. core network 바깥에는 attachment가 붙는다. 서울 리전 위쪽에 VPC 아이콘 두 개가 있어 각각 VPC attachment라고 적혀 있고, 왼쪽 VPC에서 내려온 선은 segment prod 행에서, 오른쪽 VPC에서 내려온 선은 segment shared 행에서 회색 점을 찍은 뒤 서울 edge로 들어간다. 오레곤 리전 위쪽의 VPC 하나는 segment dev 행에서 점을 찍고 오레곤 edge로 들어간다. AWS Cloud 상자 바깥 아래에는 Site-to-Site VPN 아이콘이 있고 Site-to-Site VPN attachment라고 적혀 있으며, 거기서 올라온 선이 segment onprem 행에서 점을 찍고 서울 edge로 들어간다. 회색 점은 그 attachment가 어느 세그먼트에 속하는지를 뜻하고, 점이 없이 선이 지나가기만 한 행은 그 세그먼트에 속하지 않는다는 뜻이다. 오른쪽 아래에는 core network policy 상자가 보라색 파선으로 core network와 이어져 있고, 그 안에 네 가지가 적혀 있다. edge-locations는 edge를 둘 리전, segments는 prod·dev·shared·onprem, attachment policy는 attachment의 세그먼트 배정, segment actions는 세그먼트끼리의 통신(share)이다. 정책 하나가 리전과 세그먼트와 배정과 통신 범위를 모두 정한다는 뜻이다. 주소나 ASN은 적혀 있지 않다. 그림 아래 범례는 회색 점이 그 attachment가 속한 세그먼트이며 attachment 하나는 세그먼트 하나에만 들어간다는 것과, 세그먼트 행이 리전 상자를 가로지르는 것은 세그먼트가 전역이고 core network edge만 리전마다 생기기 때문이라는 것을 설명한다](images/diagrams/cloudwan-components.png)
  <figcaption>그림 1-3-1. Cloud WAN 구성요소와 포함 관계</figcaption>
</figure>

그림에서 먼저 잡아 둘 것은 셋입니다.

- **세그먼트는 리전을 가로지릅니다.** 세그먼트 행이 두 리전 상자를 꿰뚫고 지나가는 것이 그 뜻입니다. 리전마다 생기는 것은 **core network edge** 뿐입니다.
- **attachment는 core network 밖에 있습니다.** VPC와 VPN이 core network에 *붙는* 것이지, 그 안에 들어 있는 것이 아닙니다. 선이 세그먼트 행에서 찍는 **회색 점**이 그 attachment가 속한 세그먼트입니다.
- **정책 하나가 전부를 정합니다.** 오른쪽 아래 **core network policy** 상자의 네 항목이 리전·세그먼트·배정·통신 범위입니다. 이 워크숍에서 참가자가 고치는 것이 바로 이 문서입니다([2-4](lab3.md)).

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
