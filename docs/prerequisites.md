# 1-2. 사전 준비

!!! danger "강의가 시작되기 전에 [실습 2-1](lab0.md)을 끝내 주세요"
    계정을 받으면 **강사의 안내를 기다리지 말고 바로** [2-1. 시작하기](lab0.md)로 가서 스택 2개를 배포하세요. 10분이면 끝납니다.

    Cloud WAN의 core network를 처음 만드는 데에는 **최대 30분**이 걸리고, 그 동안에는 연결을 만들거나 정책을 고칠 수 없습니다. 강의 전에 배포를 시작해 두면 이 시간이 강의 1시간 안에 지나가고, 실습 시간을 온전히 쓸 수 있습니다. 강의가 끝난 뒤에 배포를 시작하면 실습 시간의 절반을 기다리는 데 씁니다.

    배포를 시작한 뒤에는 기다리지 말고 강의를 들으세요. 준비가 끝났는지 보는 방법은 [2-1-d](lab0.md#lab0-d)에 있습니다.

## 1-2-a. 준비할 것들 { #received }

강사가 참가자마다 다음을 준비해 둡니다.

| 항목 | 내용 |
|---|---|
| AWS 계정 | 임시 실습 계정 1개 |
| 콘솔 로그인 정보 | 위 계정에 로그인하는 정보 |

별도로 설치할 프로그램은 없습니다. 브라우저만 있으면 됩니다.

## 1-2-b. 내 값 적어 두기 { #notes }

실습에서 계속 쓰는 값입니다. **값은 그 리소스를 가진 서비스 화면에서 직접 확인합니다.** CloudFormation 스택의 **Outputs** 탭에도 같은 값이 있지만, 실무에서 그렇게 찾지 않습니다. 각 서비스에서 찾는 연습이 그대로 남습니다.

| 값 | 예 | 찾는 곳 |
|---|---|---|
| global network ID | `global-network-0123456789abcdef0` | **Network Manager** → **Global networks** 목록([2-1-d](lab0.md#lab0-d)) |
| core network ID | `core-network-0123456789abcdef0` | **Network Manager** → core network 화면([2-1-d](lab0.md#lab0-d)) |
| VPN 연결 ID | `vpn-0123456789abcdef0` | **VPC** 콘솔 → **Site-to-Site VPN connections** → 그 연결의 **Details** 탭 → **VPN ID**. 실습 [2-3-a](lab2.md#lab2-a)에서 직접 만든 뒤에 생깁니다 |
| customer gateway ID | `cgw-0123456789abcdef0` | 같은 **Details** 탭의 **Customer gateway**. 또는 **VPC** 콘솔 → **Customer gateways** 의 `cwan-ws-onprem-cgw` |
| VPN 라우터 Elastic IP | `203.0.113.10` | 같은 **Details** 탭의 **Customer gateway address**. AWS가 터널을 걸 상대 주소가 이 값입니다 |

예는 모두 형식을 보여 주는 가짜 값입니다. VPN 연결 ID만 지금은 비워 둡니다.

!!! tip "VPN 연결 **Details** 탭 하나에 세 값이 모두 있습니다"
    [2-3-a](lab2.md#lab2-a)에서 VPN 연결을 만들고 나면, 그 연결의 **Details** 탭에 **VPN ID**, **Customer gateway**, **Customer gateway address** 가 나란히 있습니다. **Core network ARN** 과 **Core network attachment ARN** 도 [2-3-b](lab2.md#lab2-b) 뒤에 같은 화면에 채워집니다.

## 1-2-c. 브라우저 준비 { #browser }

- 콘솔 언어를 **English**로 바꾸면 이 안내와 화면이 같습니다. 예제 화면이 영어 기준입니다. 콘솔 오른쪽 위 톱니바퀴 아이콘을 누르면 열리는 **Current user settings** 창의 **Language** 에서 바꿉니다([2-1-a](lab0.md#lab0-a)에 그림이 있습니다).
- **브라우저 탭을 여러 개 쓰세요.** 서울 콘솔, 오레곤 콘솔, **Network Manager**, EC2 접속 화면을 탭 하나씩 열어 두면 리전을 바꾸느라 시간을 쓰지 않습니다. 탭마다 오른쪽 위 리전이 맞는지 보고 시작하세요.

## 1-2-d. 꼭 지켜 주세요 { #notes-must }

!!! danger "실습이 끝나면 정리를 반드시 합니다"
    실습이 끝나면 [3-4. 리소스 정리](extra-d.md)를 반드시 합니다. core network edge는 리전당 시간당 요금이 붙고, 정리하지 않으면 계속 늘어납니다.

!!! warning "리전을 잘못 고르면 실습이 되지 않습니다"
    서울(`ap-northeast-2`)과 오레곤(`us-west-2`) 두 리전을 오갑니다. 단계마다 어느 리전인지 적혀 있으니, 콘솔 오른쪽 위에 **Asia Pacific (Seoul)** 또는 **US West (Oregon)** 가 맞게 보이는지 확인하세요.

## 1-2-e. 비용 { #cost }

실습 계정에 다음 요금이 발생합니다. 계정과 비용은 강사가 관리합니다. 금액은 공개된 시간당 요금으로 계산한 추정치입니다([4-4](references.md)에 요금 문서 링크가 있습니다).

| 항목 | 요금 |
|---|---|
| core network edge | 리전당 시간당 $0.50 (이 워크숍은 서울과 오레곤 2개) |
| attachment | 시간당 $0.065~0.09 (리전과 종류에 따라 다릅니다. 오레곤이 더 쌉니다) |
| 참가자 1명당 합계 | 약 $1.3~2.7 |

- 부분 시간은 올림입니다. 1시간 중 1분만 써도 1시간으로 계산됩니다.
- 정리가 늦어지면 합계가 늘어납니다. 그 밖에 EC2 인스턴스, Site-to-Site VPN 연결, 데이터 전송 요금이 붙습니다.
