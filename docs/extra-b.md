# 3-2. Transit Gateway와 비교

오늘 만든 구성(세그먼트 4개, 리전 2개, 온프레미스 연결)을 Transit Gateway로 만들면 무엇을 해야 하는지 비교합니다. 어느 쪽이 낫다는 이야기가 아니라, **일이 어디에 생기는지** 보는 것이 목적입니다. 이 페이지는 읽는 내용이고 콘솔에서 할 일은 없습니다.

## 3-2-a. 구조 비교 { #b-a }

| 항목 | Cloud WAN | Transit Gateway |
|---|---|---|
| 리전 간 연결 | core network edge가 리전마다 하나씩 생기고, edge끼리는 자동으로 연결됩니다 | 리전마다 Transit Gateway를 만들고 peering으로 서로 잇습니다 |
| 리전이 n개일 때 연결 수 | core network edge **n개** | Transit Gateway peering **n(n-1)/2개** |
| 격리 단위 | 세그먼트. **전역**이라 모든 리전에서 같은 세그먼트입니다 | 라우팅 테이블. 리전마다 따로 만듭니다 |
| 연결 배정 | 연결의 `segment` 태그와 attachment policy로 세그먼트에 배정합니다 | 리전마다 association과 propagation을 따로 설정합니다 |
| 공유 서비스 | 정책에 `share` 한 줄 | 라우팅 테이블마다 공유 서비스 경로를 넣습니다 |
| 설정 위치 | core network policy 하나 | 리전별 Transit Gateway와 라우팅 테이블 |

!!! info "표에 나온 **association** 과 **propagation** 이 무엇인가요"
    Transit Gateway에서 연결마다 따로 지정하는 두 가지입니다.

    - **association**(연결): 그 연결로 **들어온** 트래픽이 **어느 라우팅 테이블을 보고** 길을 찾을지 정합니다. 연결 하나에 테이블 하나입니다.
    - **propagation**(전파): 그 연결 뒤에 있는 대역을 **어느 라우팅 테이블에 자동으로 올릴지** 정합니다. 여러 테이블에 올릴 수 있습니다.

    둘을 나눠 지정하기 때문에 "A는 B를 볼 수 있지만 B는 A를 볼 수 없다" 같은 구성도 만들 수 있습니다. 대신 연결과 리전이 늘 때마다 이 짝을 손으로 맞춰야 합니다. Cloud WAN에서는 연결에 `segment` 태그 하나를 붙이면 세그먼트가 정해지고, 그와 함께 두 가지가 모두 정해집니다.

리전이 늘어날 때 차이가 커집니다. 두 리전이면 peering은 1개이고 edge는 2개이지만, 리전이 4개가 되면 peering은 6개, edge는 4개입니다. Transit Gateway는 peering마다 양쪽 라우팅 테이블 경로도 맞춰 주어야 합니다.

![리전 네 개를 Cloud WAN과 Transit Gateway로 각각 이었을 때를 나란히 놓은 비교도. 왼쪽은 AWS Cloud WAN이다. 보라색 파선의 core network 상자 안에 회색 파선의 segment prod 상자가 있고, 그 상자가 리전 A, B, C, D 네 개를 모두 품고 있다. 세그먼트 상자에는 전역 — 리전마다 만들지 않는다고 적혀 있다. 리전 상자마다 core network edge 아이콘이 하나씩 들어 있고 리전끼리 잇는 선은 하나도 그려져 있지 않다. 아래에 리전 4개 → edge 4개, edge끼리는 자동으로 연결됩니다, 세그먼트는 정책 한 곳에만 적습니다라고 적혀 있다. 오른쪽은 Transit Gateway다. 리전 A, B, C, D 네 상자가 2×2로 놓여 있고 상자마다 Transit Gateway 아이콘과 라우팅 테이블 아이콘이 따로 하나씩 들어 있다. 네 리전은 선 여섯 개로 모든 쌍이 이어져 있다. 가로 두 개, 세로 두 개, 가운데서 교차하는 대각선 두 개이며, A와 B를 잇는 선 위에만 TGW peering 아이콘과 이름이 붙어 있다. 아래에 리전 4개 → TGW 4개, peering 6개, 라우팅 테이블은 리전마다 따로 만듭니다, peering마다 양쪽 테이블에 경로를 넣습니다라고 적혀 있다. 그림 맨 아래 띠에는 리전이 n개일 때 늘어나는 것: core network edge n개 · Transit Gateway peering n(n−1)/2개라고 적혀 있다. 왼쪽은 선이 없고 오른쪽은 선이 여섯 개라는 모양 차이가 그대로 관리 부담의 차이다](images/diagrams/extra-b-compare.png)

**결과**: 리전이 5개일 때 Transit Gateway peering은 10개, core network edge는 5개임을 계산할 수 있습니다.

## 3-2-b. 이 워크숍의 구성을 Transit Gateway로 만든다면 { #b-b }

| 하는 일 | Cloud WAN | Transit Gateway |
|---|---|---|
| 운영과 개발 분리 | 아무것도 하지 않습니다. 세그먼트는 기본이 격리입니다 | 라우팅 테이블을 따로 만들고 association을 나눕니다 |
| 공유 서비스 열기 | `share` 한 줄 | 운영, 개발, 온프레미스 라우팅 테이블마다 공유 VPC 경로를 넣습니다 |
| 오레곤 운영 환경 추가 | 연결에 `segment=prod` 태그를 붙입니다 | 오레곤에 Transit Gateway와 라우팅 테이블을 만들고, peering을 만들고, 양쪽 라우팅 테이블에 경로를 넣습니다 |
| 온프레미스를 운영에 열기 | 정책에 `share` 한 줄 | 라우팅 테이블에 경로를 넣고, 리전마다 반복합니다 |

!!! info "Transit Gateway가 더 맞는 경우도 있습니다"
    리전이 하나이고 구성이 단순하면 Transit Gateway로 충분합니다. 이 표는 리전과 환경이 늘어날 때의 관리 부담을 보여 줍니다.

**결과**: "운영과 개발을 분리하려고 Cloud WAN에서는 따로 할 일이 없다"는 이유를 세그먼트의 기본 동작으로 설명할 수 있습니다.

## 3-2-c. 요금 비교 { #b-c }

Cloud WAN 요금은 이 워크숍에서 쓰는 값으로 정리합니다. 최신 요금은 AWS 요금 페이지에서 확인하세요.

| 항목 | 요금 |
|---|---|
| core network edge | 리전당 시간당 $0.50 |
| attachment 시간당 요금 | 서울 $0.09, 오레곤 $0.065 |
| 데이터 처리 | $0.02/GB |

Transit Gateway는 연결(attachment) 시간당 요금과 데이터 처리 요금 외에 **Transit Gateway peering에도 별도 시간당 요금**이 있습니다. 비교할 때는 리전 수에 따라 peering 개수가 늘어난다는 점과, Cloud WAN에서는 core network edge 요금이 리전마다 붙는다는 점을 함께 봅니다. 실제 금액은 구성에 따라 달라지므로 AWS 요금 계산기로 따로 계산하세요.

**결과**: 두 서비스에서 리전이 늘 때 늘어나는 요금 항목이 각각 무엇인지 말할 수 있습니다(Cloud WAN은 edge, Transit Gateway는 peering).

## 3-2-d. 이미 Transit Gateway가 있다면 { #b-d }

기존 Transit Gateway를 쓰고 있다면 한 번에 옮기지 않아도 됩니다. Transit Gateway **route table attachment**를 쓰면 Transit Gateway와 Cloud WAN을 함께 두고 단계적으로 옮길 수 있습니다. 자세한 절차는 이 페이지에서 다루지 않습니다. [4-4 참고 문서](references.md)를 보세요.

**결과**: 공존 단계를 거쳐 옮길 수 있다는 것과, 자세한 내용을 찾을 곳을 알고 있습니다.
