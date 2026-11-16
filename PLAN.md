# AWS Cloud WAN L200 워크숍 계획

- 저장소: `conft2k/ws-aws-cloudwan-l200`
- 사이트: https://ws.nettfc.net/ws-aws-cloudwan-l200/
- 형식: 2시간 (이론 1시간 + 실습 1시간)
- 레벨: 200
- 작성 시작: 2026-11-16

## 1. 개요

고객이 운영(prod), 개발(dev), 공유(shared) 환경을 쓰면서 온프레미스와 연결하고, 두 개 리전으로 글로벌 확장하는 상황을 AWS Cloud WAN 하나로 푸는 워크숍이다.

이론 1시간은 기존 `conft2k/deck-aws-cloudwan` deck(49장, 약 50분)을 쓴다. 실습 1시간은 참가자가 콘솔에서 core network policy와 연결(attachment)을 직접 다룬다.

핵심 메시지는 deck과 같다: **리전이 늘고 환경이 늘어도 정책 하나로 관리한다.**

## 2. 결정 사항 (2026-11-16, 사용자 결정)

| 항목 | 결정 | 이유 |
|---|---|---|
| 온프레미스 역할 | AWS 안에 "온프레미스 모사 VPC"를 만들고 Site-to-Site VPN attachment로 연결 | DX 랩 Pod를 쓰면 hosted connection 수락·Transit VIF·라우터 BGP에만 20~30분이 들어 실습 1시간 중 세그먼트 실습 시간이 남지 않는다 |
| 리전 | 서울 `ap-northeast-2` + 오레곤 `us-west-2` | 대륙 간 연결이라 "글로벌"이 체감된다. 오레곤 attachment 단가가 더 싸다($0.065/시간) |
| 참가자 계정 | 기존에 만들어 둔 임시 실습 계정 | 계정당 global network 5개 한도와 정리 책임 때문 |
| DX 랩 Pod | 쓰지 않는다 | 위와 같음. Direct Connect 연결은 deck과 부록 문서로만 다룬다 |
| 실시일 | 미정 | 리허설 2회(1차 검증 → 수정 → 2차 확인)를 기준으로 완성도를 최대로 올린다 |
| 계정 | 참가자 1명당 1개 | global network가 계정당 5개 한도라 공유할 수 없다 |
| 이론 deck | **손대지 않는다** | 기존 `deck-aws-cloudwan` 을 그대로 쓴다. deck에 실습 안내 슬라이드가 없으므로 강의 전 10분 운영을 사이트와 강사 안내로 푼다 |
| 사이트의 "작성 중" 배너 | 유지한다 | 콘솔 절차가 검증 전이라 그대로 따라 하면 막히는 단계가 있다. 2차 배포 때 지운다 |
| `dev` 세그먼트 VPC 추가 | **오레곤에 dev VPC를 둔다**(2026-11-16 변경) | 서울에 하나 더 두는 안은 버렸다. 오레곤에 두면 `dev` 세그먼트가 두 리전에 걸쳐 "세그먼트는 전역"이 한 번 더 드러나고, 추가 과제 3-1의 `isolate-attachments` 효과를 서울 dev ↔ 오레곤 dev 통신이 끊기는 것으로 **실제로 볼 수 있다**. 본편 시간을 늘리지 않으려고 VPC는 스택이 만들고 attachment는 3-1에서 참가자가 만든다. 비용은 참가자당 약 $0.07 늘어난다 |
| 라우터 보안 그룹 | `0.0.0.0/0` 에서 UDP 500·4500·ESP 허용 | AWS 터널 엔드포인트 IP는 참가자가 VPN 연결을 만든 뒤에야 정해진다. 임시 계정에서 2시간만 존재하고 IPsec은 사전 공유 키로 인증한다. 운영 환경에서 좁히는 방법은 부록에 적는다 |
| 강의 전 10분 운영 | 강사 구두 안내 + 사이트 1-2 맨 위의 안내 블록 | 별도 안내문(PDF)은 관리할 산출물만 늘고 효과가 겹친다 |
| 리허설 | 2회. 1차가 끝나면 **즉시 정리**하고 2차는 처음부터 다시 배포 | 배포 단계가 참가자가 가장 먼저 만나는 곳이고, core network 생성 시간을 두 번 재는 값이 있다. 리허설 2회 합쳐 $10 안쪽 |
| 콘솔 스크린샷 | 35장 안팎 | 집필 담당이 남긴 자리는 53개. 처음 보는 화면, 틀리기 쉬운 폼, 성공·실패 결과 화면만 남기고 다른 워크숍에서 이미 본 화면과 단순 상태 표시는 뺀다 |
| Codex 리뷰 | 세 묶음 | ⑴ 서울 템플릿(IPsec·BGP 자동 설정과 정책 JSON, 가장 높은 등급, **리허설 전에** 보낸다) ⑵ 실습 4페이지 + 리소스 정리 ⑶ 소개·용어·부록. 구성도는 리뷰 대신 리허설에서 실제 구성과 대조한다 |
| QA 테스터 | 문서만 읽는 테스터 1회, 2차 리허설 전 | "무엇을 눌러야 할지 모르겠는 곳, 앞 단계 결과 없이는 못 하는 곳, 용어가 처음 나오는데 설명이 없는 곳"을 찾는 역할로 한정한다. 실제 조작 검증은 2차 리허설이 겸한다 |

## 3. 시나리오

참가자는 한 고객의 네트워크 담당자 역할이다. 고객은 다음을 요구한다.

1. 운영과 개발은 서로 통신하면 안 된다.
2. 공유 서비스(로그, 인증, 모니터링)는 운영과 개발 양쪽에서 쓸 수 있어야 한다.
3. 온프레미스는 운영과 공유 서비스에는 닿아야 하지만 개발에는 닿으면 안 된다.
4. 미국(오레곤)에 운영 환경을 하나 더 연다. 서울 운영과 통신해야 한다.

### 3-1. 세그먼트 설계

| 세그먼트 | 담는 연결 | 기본 동작 |
|---|---|---|
| `prod` | 서울 prod VPC, 오레곤 prod VPC | 같은 세그먼트끼리만 통신 |
| `dev` | 서울 dev VPC, 오레곤 dev VPC(추가 과제 3-1에서 붙인다) | 같은 세그먼트끼리만 통신 |
| `shared` | 서울 shared VPC | `prod`, `dev`, `onprem`에 share |
| `onprem` | Site-to-Site VPN attachment | 처음에는 `shared` 와만 통신한다. `prod` 는 실습 2-4에서 연다 |

세그먼트는 기본적으로 자기 세그먼트 안에서만 통신한다. `prod`와 `dev` 사이를 막으려고 따로 할 일이 없다는 것이 Cloud WAN의 기본 동작이고, 실습 2-2에서 이것을 먼저 확인한다.

`shared`가 `prod`·`dev`·`onprem`에 share하면, 세 세그먼트는 `shared`에 닿지만 서로는 닿지 않는다. 이 비대칭이 공유 서비스 패턴의 핵심이다.

`onprem`은 일부러 `prod` 와의 share 없이 시작한다. `shared` 가 `onprem` 에도 share하므로 온프레미스는 처음부터 공유 서비스에는 닿는다(실습 2-3-d에서 확인한다). 운영 환경에는 닿지 않는다. 실습 2-4에서 참가자가 정책에 share 한 줄을 넣어 온프레미스와 운영 환경을 연다. 이것이 "정책 하나로 관리한다"를 직접 체험하는 지점이다.

### 3-2. 주소 설계

| 구분 | 리전 | 대역 | 테스트 호스트 |
|---|---|---|---|
| 온프레미스 모사 LAN | 서울 | `172.16.1.0/24` | `172.16.1.10` (온프레미스 VM) |
| prod VPC | 서울 | `10.10.1.0/24` | `10.10.1.10` |
| dev VPC | 서울 | `10.20.1.0/24` | `10.20.1.10` |
| shared VPC | 서울 | `10.30.1.0/24` | `10.30.1.10` |
| prod VPC | 오레곤 | `10.11.1.0/24` | `10.11.1.10` |
| dev VPC | 오레곤 | `10.21.1.0/24` | `10.21.1.10` |

- 참가자마다 계정이 다르므로 대역은 모든 참가자가 똑같이 쓴다. Pod 번호 같은 참가자별 값이 없다.
- 온프레미스 모사 VPC는 Cloud WAN에 VPC attachment로 붙이지 않는다. 오직 VPN으로만 연결한다. 그래야 실제 온프레미스처럼 동작한다.

### 3-3. ASN

| 구분 | ASN |
|---|---|
| core network `asn-ranges` | `64512-64520` (끝 값은 포함되지 않아 실제로는 64512~64519) |
| 서울 edge | `64512` |
| 오레곤 edge | `64513` |
| 온프레미스 라우터(customer gateway) | `65000` |

edge ASN은 만든 뒤 바꿀 수 없다. 템플릿에서 리전별로 명시한다.

## 4. 학습 목표

워크숍을 마치면 참가자는 다음을 할 수 있다.

1. core network, core network edge, 세그먼트, 연결의 관계를 설명한다.
2. core network policy에서 세그먼트가 격리되는 기본 동작과 `share`의 효과를 설명한다.
3. 연결에 태그를 붙여 세그먼트에 배정되는 것을 콘솔에서 확인한다.
4. 리전을 하나 더 쓰는 환경에서 같은 세그먼트의 연결이 리전을 넘어 통신하는 것을 확인한다.
5. Site-to-Site VPN으로 온프레미스를 core network에 연결하고 BGP 경로를 확인한다.
6. policy version을 만들고 change set을 검토·실행해 통신 가능 범위를 바꾼다.
7. Transit Gateway 구성과 비교해 무엇이 달라지는지 설명한다.

## 5. 진행 원칙

- 오래 걸리는 것을 먼저 시작한다. core network 최초 생성은 **최대 30분**이고 그 동안 attachment 생성과 policy 편집이 모두 막힌다([공식 문서](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-getting-started.html)). 그래서 스택 배포를 **이론 강의 전에** 시작해 강의 1시간 동안 끝나게 한다.
- 참가자가 직접 만드는 것은 학습 목표에 직접 닿는 것만 남긴다. 나머지는 CloudFormation이 미리 만든다.
- 실패를 먼저 보여 주고 고친다. `prod`→`dev` 차단, 온프레미스→`prod` 차단을 먼저 확인한 뒤 정책으로 연다.
- 모든 확인은 ping·curl과 Network Manager의 경로 테이블 두 가지로 한다.

## 6. 진행표

| 시간 | 구분 | 내용 |
|---|---|---|
| -0:10–0:00 | [2-1](docs/lab0.md) | 로그인, 스택 2개 배포 시작 (강의 전에 한다) |
| 0:00–1:00 | 이론 | `deck-aws-cloudwan` deck. 강의 중 core network가 완성된다 |
| 1:00–1:22 | [2-2](docs/lab1.md) | core network 둘러보기, 세그먼트 격리 확인, 오레곤 연결 추가 |
| 1:22–1:42 | [2-3](docs/lab2.md) | 온프레미스 VPN 연결과 BGP 경로 확인 |
| 1:42–1:57 | [2-4](docs/lab3.md) | 정책 한 줄로 온프레미스 열기 |
| 1:57–2:00 | [3-4](docs/extra-d.md) | 참가자가 만든 연결 삭제, 스택 삭제 시작 (나머지는 강사가 회수) |

추가 과제 3-1~3-3은 시간이 남거나 워크숍 뒤에 혼자 할 사람을 위한 것이다.

### 6-1. 강의 전 10분 진행 대본 (강사용)

deck에는 실습 안내 슬라이드가 없다. 이 10분은 강사가 구두로 연다.

| 시각 | 강사가 하는 일 |
|---|---|
| -0:10 | 참가자에게 계정 정보를 나눠 주고 사이트 주소를 화면에 띄운다. "강의를 듣기 전에 10분만 먼저 작업하겠습니다"라고 연다 |
| -0:09 | 사이트 1-2(사전 준비) 맨 위의 빨간 상자를 함께 읽는다. **왜** 먼저 하는지를 말한다: core network를 처음 만드는 데 최대 30분이 걸리고 그 동안 아무 작업도 못 한다 |
| -0:08 | 2-1로 이동하게 하고, 서울 리전에서 스택을 배포하는 것까지 함께 한다. 리전을 틀리는 사람이 반드시 나오므로 오른쪽 위 리전 표시를 소리 내어 확인시킨다 |
| -0:04 | 리전을 오레곤으로 바꾸고 두 번째 스택을 배포하게 한다. 여기서 리전 전환을 놓치는 사람이 가장 많다 |
| -0:01 | 2-1-d를 보여 주며 "준비가 끝났는지는 Policy versions 탭이 LIVE이고 Change set state가 Execution succeeded인지로 봅니다. 지금은 기다리지 말고 강의를 들으세요"라고 닫는다 |
| 0:00 | 이론 강의 시작 |

강의 중간(약 30분 지점)에 한 번 "스택이 끝났는지 확인해 보세요"라고 끼워 넣는다. 실패한 참가자를 이때 발견해야 실습 시작 전에 복구할 수 있다.

## 7. 과제 표

번호 체계는 **묶음 `2.` / 페이지 `2-2` / 소절 `2-2-a`** 다. 문서 제목에 이 번호를 그대로 쓴다.

### 2-1. 시작하기 (10분, 이론 강의 전)

| 번호 | 참가자가 하는 일 | 확인 포인트 | 시간 |
|---|---|---|---|
| 2-1-a | 콘솔 로그인, 리전을 서울로 맞추기 | 오른쪽 위에 **Asia Pacific (Seoul)** | 2분 |
| 2-1-b | 서울 스택 배포 | `CREATE_IN_PROGRESS` | 3분 |
| 2-1-c | 오레곤 스택 배포 | `CREATE_IN_PROGRESS` | 3분 |
| 2-1-d | core network 준비 상태 확인하는 법 익히기 | Policy versions 탭에서 `LIVE`, Change set state `Execution succeeded` | 2분 + 대기 |

### 2-2. 세그먼트와 글로벌 연결 (22분)

| 번호 | 참가자가 하는 일 | 확인 포인트 | 시간 |
|---|---|---|---|
| 2-2-a | Network Manager에서 core network, 세그먼트, 연결 둘러보기 | 세그먼트 4개와 서울 연결 3개, 각 연결의 `segment` 태그 | 5분 |
| 2-2-b | 서울 prod EC2 → 서울 dev EC2 ping (실패가 맞다) | `100% packet loss`. 보안 그룹은 열려 있다 | 3분 |
| 2-2-c | 서울 prod EC2 → 서울 shared EC2 ping (성공) | 응답 있음 | 2분 |
| 2-2-d | 오레곤 prod VPC attachment 생성, `segment=prod` 태그 | attachment가 `prod` 세그먼트에 자동 배정 | 7분 |
| 2-2-e | 오레곤 앱 서브넷 라우트 테이블에 `10.0.0.0/8`, `172.16.0.0/12` → core network 경로 추가 | 경로가 `Active` | 3분 |
| 2-2-f | 서울 prod EC2 → 오레곤 prod EC2 ping | 응답 있음, 경로 테이블에 `10.11.1.0/24` | 2분 |

2-2-e가 필요한 이유는 오레곤 스택이 attachment를 만들지 않기 때문이다(8-2절). 참가자는 "연결을 붙이는 것과 VPC 라우트를 넣는 것은 다른 일"을 여기서 배운다.

### 2-3. 온프레미스 연결 (20분)

| 번호 | 참가자가 하는 일 | 확인 포인트 | 시간 |
|---|---|---|---|
| 2-3-a | Site-to-Site VPN 연결 생성 (Target Gateway Type = **Not Associated**) | 상태 `Available` | 5분 |
| 2-3-b | Cloud WAN VPN attachment 생성, `segment=onprem` 태그, edge `ap-northeast-2` | `onprem` 세그먼트에 배정 | 4분 |
| 2-3-c | VPN 라우터 EC2에서 `sudo /opt/onprem/setup-tunnels.sh <vpn-id>` 실행 | 터널 2개 `UP`, BGP 세션 2개 established, `172.16.1.0/24` 광고 | 6분 |
| 2-3-d | 온프레미스 VM → 서울 shared EC2 ping (성공) | 응답 있음 | 2분 |
| 2-3-e | 온프레미스 VM → 서울 prod EC2 ping (실패가 맞다) | `100% packet loss` | 3분 |

### 2-4. 정책으로 통신 범위 바꾸기 (15분)

| 번호 | 참가자가 하는 일 | 확인 포인트 | 시간 |
|---|---|---|---|
| 2-4-a | policy에 `onprem` → `prod` share 추가, 새 policy version 생성 | 새 버전이 목록에 보임 | 4분 |
| 2-4-b | change set 검토 | 바뀌는 것 목록에 `onprem`·`prod` 경로 추가 | 3분 |
| 2-4-c | change set 실행 | `Execution succeeded` | 4분 |
| 2-4-d | 온프레미스 VM → 서울 prod EC2, 오레곤 prod EC2 ping (성공) | 양쪽 다 응답 있음. dev는 여전히 차단 | 2분 |
| 2-4-e | 워크숍 전체 정리, Transit Gateway와 대비 | — | 2분 |

### 3-1 ~ 3-3. 추가 과제 (시간이 남을 때, 선택)

본편이 아니므로 1시간 배분에 들어가지 않는다. 3-1은 오레곤 dev VPC가 생기면서 **직접 해 보는 과제**가 됐다.

| 번호 | 참가자가 하는 일 | 확인 포인트 |
|---|---|---|
| 3-1-d | 오레곤 dev VPC attachment 생성(`segment=dev` 태그)과 VPC 라우트 추가 | `dev` 세그먼트에 자동 배정 |
| 3-1-e | 서울 dev EC2 → 오레곤 dev EC2 ping | 응답 있음. 같은 세그먼트는 리전을 넘어 통신된다 |
| 3-1-f | `dev` 세그먼트에 `isolate-attachments: true` 를 넣고 change set 실행 | 서울 dev → 오레곤 dev **차단**. `shared`(`10.30.1.10`)로는 **여전히 통신**. 이 대조가 이 과제의 핵심 |
| 3-1-g | 되돌리기 | 다시 통신된다. 되돌리지 않으면 3-3에서 보는 경로가 달라진다 |
| 3-2 | Transit Gateway로 같은 구성을 만들면 무엇이 다른지 읽기 | — |
| 3-3 | 세그먼트별 경로 테이블 비교 | `prod` 에 오레곤 대역이 어떻게 들어왔는지 |

3-4(리소스 정리)는 선택이 아니라 **반드시** 한다.

시간은 모두 **추정값**이다. 사전 테스트에서 측정해 13절에 기록하고 이 표를 고친다.

## 8. CloudFormation 스택

### 8-1. 서울 스택 `cloudwan-workshop-seoul`

| 리소스 | 내용 |
|---|---|
| global network | `cwan-ws-global` |
| core network | 초기 policy 포함, 세그먼트 4개, edge 2개(서울·오레곤) |
| prod VPC | `10.10.1.0/24`, 서브넷, EC2 1대 |
| dev VPC | `10.20.1.0/24`, 서브넷, EC2 1대 |
| shared VPC | `10.30.1.0/24`, 서브넷, EC2 1대 |
| 온프레미스 모사 VPC | `172.16.1.0/24`, 퍼블릭 서브넷의 VPN 라우터 EC2, 프라이빗 서브넷의 VM EC2 |
| VPC attachment 3개 | 서울 prod·dev·shared. `segment` 태그 포함 |
| customer gateway | 온프레미스 라우터의 Elastic IP, ASN `65000` |
| EC2 Instance Connect Endpoint 3개 | prod VPC, dev VPC, 온프레미스 VPC에 하나씩. 본편의 명령은 prod EC2와 온프레미스 VM에서 실행하지만, **추가 과제 3-1에서 서울 dev EC2 → 오레곤 dev EC2 ping이 필요해** dev VPC에도 둔다. prod에서는 dev로 갈 수 없다(그 차단이 바로 이 워크숍이 보여 주는 것이다). shared EC2는 응답 대상일 뿐이라 셸이 필요 없다. EC2 Instance Connect Endpoint 자체에는 시간당 요금이 없다 |

### 8-2. 오레곤 스택 `cloudwan-workshop-oregon`

| 리소스 | 내용 |
|---|---|
| prod VPC | `10.11.1.0/24`, 서브넷, EC2 1대(`10.11.1.10`) |
| dev VPC | `10.21.1.0/24`, 서브넷, EC2 1대(`10.21.1.10`) |
| EC2 Instance Connect Endpoint | prod VPC에 1개. dev EC2는 ping·HTTP 응답 대상일 뿐이라 셸이 필요 없다 |

두 VPC 모두 attachment는 만들지 않는다. 오레곤 prod attachment는 참가자가 실습 2-2-d에서, 오레곤 dev attachment는 추가 과제 3-1에서 만든다. 본편 실습 시간은 오레곤 dev 때문에 늘어나지 않는다.

### 8-3. 확정된 기술 사항 (2026-11-16 조사)

| 항목 | 결과 | 출처 |
|---|---|---|
| `AWS::NetworkManager::GlobalNetwork` | 필수 속성 없음. `Description`, `Tags`만 쓴다 | [CFN 참조](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-networkmanager-globalnetwork.html) |
| `AWS::NetworkManager::CoreNetwork` | `GlobalNetworkId`만 필수. `PolicyDocument`를 인라인 JSON으로 넣을 수 있다 | [CFN 참조](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-networkmanager-corenetwork.html) |
| `AWS::NetworkManager::VpcAttachment` | `CoreNetworkId`, `SubnetArns`, `VpcArn` 필수. AZ당 서브넷 1개 | [CFN 참조](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-networkmanager-vpcattachment.html) |
| `AWS::NetworkManager::SiteToSiteVpnAttachment` | `CoreNetworkId`, `VpnConnectionArn` 필수 | [CFN 참조](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-networkmanager-sitetositevpnattachment.html) |
| attachment policy의 `tag-exists` 조건 | 공식 정책 예시에 있다. 쓸 수 있다 | [3단계 환경 예시](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policy-examples-three-stage.html) |
| 세그먼트 이름 대소문자 | 공식 예시가 `sharedServices`와 `sharedservices`를 섞어 쓴다. **모두 소문자로 통일한다** | 같은 예시 |
| Cloud WAN 홈 리전 | `us-west-2` 고정 | [Cloud WAN 소개](https://docs.aws.amazon.com/network-manager/latest/cloudwan/what-is-cloudwan.html) |

### 8-4. 설계를 바꾼 것: VPN 연결은 참가자가 만든다

`AWS::EC2::VPNConnection`은 `TransitGatewayId`와 `VpnGatewayId` 중 **하나를 반드시 지정**해야 한다고 문서가 적는다("You must specify either TransitGatewayId or VpnGatewayId, but not both"). Cloud WAN용 VPN 연결은 둘 다 없는 상태(콘솔의 Target Gateway Type = **Not Associated**)로 만들어야 하는데, 이것을 CloudFormation으로 만들 수 있다는 근거를 찾지 못했다([CFN 참조](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-ec2-vpnconnection.html), [Cloud WAN VPN attachment](https://docs.aws.amazon.com/vpn/latest/s2svpn/create-cwan-vpn-attachment.html)).

그래서 다음과 같이 나눈다.

| 누가 | 무엇을 |
|---|---|
| CloudFormation | 온프레미스 모사 VPC, VPN 라우터 EC2(Elastic IP), 내부 VM EC2, customer gateway |
| 참가자 (실습 2-3) | Site-to-Site VPN 연결 생성 (Target Gateway Type = Not Associated), Cloud WAN VPN attachment 생성 |

이 편이 비용 면에서도 낫다. VPN 연결은 시간당 과금이므로 워크숍 중에만 존재하는 쪽이 좋다.

### 8-5. 온프레미스 라우터 자동 설정

VPN 터널 정보(외부 IP 2개, PSK, BGP 주소)는 VPN 연결을 만든 뒤에야 나온다. 참가자가 설정 파일을 받아 손으로 옮기면 10분 넘게 걸린다.

그래서 VPN 라우터 EC2에 설정 스크립트를 미리 넣어 둔다. 참가자는 VPN 연결 ID 하나만 넣고 스크립트를 실행한다.

```bash
sudo /opt/onprem/setup-tunnels.sh vpn-0123456789abcdef0
```

스크립트는 `aws ec2 describe-vpn-connections`로 터널 정보를 받아 strongSwan(IPsec)과 FRR(BGP) 설정을 만들고 서비스를 다시 시작한다. EC2에는 `ec2:DescribeVpnConnections` 권한만 있는 IAM 역할을 붙인다.

이 스크립트는 사전 테스트에서 반드시 검증한다. 실습 성패가 여기에 달려 있다.

### 8-6. 온프레미스 라우터의 OS와 패키지 (2026-11-16 확정)

라우터는 IPsec(strongSwan)과 BGP(FRR)가 필요하다. 둘 다 **Amazon Linux 2023 코어 저장소에는 없다.** 코어에는 libreswan만 있고 BGP 데몬은 아예 없다.

AWS가 제공하는 확장 저장소 **SPAL**(Supplementary Packages for Amazon Linux)을 켜면 둘 다 dnf로 설치된다. 그래서 다섯 인스턴스를 모두 Amazon Linux 2023 arm64로 통일한다.

```bash
dnf install -y spal-release     # 코어 저장소에 있는 활성화 패키지
dnf install -y strongswan frr
```

2026-11-16에 AL2023 aarch64(`ap-northeast-2`)에서 직접 확인한 값이다.

| 항목 | 값 |
|---|---|
| `spal-release` | `2023-5.amzn2023`, 저장소 `amazonlinux`(코어) |
| 함께 설치되는 것 | `spal-repo-s3` 가 `/etc/yum.repos.d/amazonlinux-spal.repo` 를 넣는다 |
| `strongswan` | `6.0.6-1.1.spal2023` (`swanctl` 포함) |
| `frr` | `10.4.1-2.1.spal2023` |
| systemd 유닛 | `strongswan.service`, `strongswan-starter.service`, `frr.service` |

Debian 계열과 다른 점은 다음과 같다. 템플릿 스크립트가 여기서 갈린다.

- `strongswan-swanctl`, `charon-systemd`, `frr-pythontools` 패키지는 **없다**. Debian 전용 이름이다. `swanctl` 은 `strongswan` 패키지가 제공한다.
- Ubuntu의 `strongswan-swanctl.service` 유닛이 없다.

SPAL은 EPEL9 파생이고 **AWS Enterprise Support 대상이 아니다.** 보안 패치는 EPEL9 업스트림에 있을 때만 제공되는 as-is 패키지다. 2시간짜리 실습 환경에는 문제가 없다고 판단했다. 다만 참가자가 운영 환경에도 그대로 써도 되는 것으로 오해하지 않도록, 부록에 이 지원 정책을 한 단락 적는다.

### 8-7. 아직 확인하지 못한 것 (사전 테스트에서 확인)

- `PolicyDocument`를 넣은 CoreNetwork **최초 생성**이 change set 자동 실행까지 가서 `LIVE`가 되는지. 문서는 갱신할 때의 동작만 적는다.
- 스택이 `CREATE_COMPLETE`가 된 시점과 core network가 실제로 쓸 수 있는 시점(policy `LIVE`, change set `Execution succeeded`)이 일치하는지.
- 서울 리전 스택에서 global network와 core network를 만들 수 있는지(Cloud WAN 홈 리전은 `us-west-2`다). 안 되면 **두 스택의 역할을 바꿔** 오레곤 스택이 core network를 만들게 한다.
- 각 단계의 실제 소요 시간(13절).
- **서울 템플릿에 아직 반영하지 않은 수정 2건**(Codex 리뷰가 끝나는 대로 함께 반영한다). ⑴ dev VPC에 EC2 Instance Connect Endpoint 추가(위 8-1 참조). ⑵ HTTP 응답 형식과 서비스 이름을 오레곤 템플릿과 통일. 지금은 서울이 `you reached <host> (<ip>) / I saw you as <ip>:<port>` 와 `cwanws-whoami`, 오레곤이 `<host> saw <ip>:<port>` 와 `cwan-echo` 로 갈려 있어 참가자가 `curl` 결과를 리전끼리 비교할 때 혼란스럽다.
- 정책 JSON 전체가 API에 받아들여지는지. `tag-exists` 는 2026-11-16 조사에서 **유효한 것으로 확인**했다(Terraform AWS provider의 조건 type 허용 목록에 있고, AWS 공식 예시 3곳 — 3단계 환경, service insertion, 분산 WAN — 이 쓴다). 태그 키 필드 이름도 `key` 가 맞고 `operator` 와 `value` 는 넣지 않는다. 공식 JSON 레퍼런스의 `type` 목록에서만 빠져 있어 문서 누락으로 본다. 그대로 쓰되 배포가 거부되면 `tag-name` 으로 바꾼다.
- **정책을 배포 전에 검증할 수단은 없다.** core network 없이 정책 JSON만 검증하는 API가 없고, CloudFormation이 `PolicyDocument` 를 언제 검증하는지도 문서에 없다. 최악의 경우 30분을 쓰고 실패한다. 리허설 1차의 첫 관문을 서울 스택 배포로 두고, 실패하면 스택 이벤트에서 정책 오류인지부터 본다.

## 9. 초기 core network policy 초안

```json
{
  "version": "2021.12",
  "core-network-configuration": {
    "asn-ranges": ["64512-64520"],
    "vpn-ecmp-support": true,
    "edge-locations": [
      { "location": "ap-northeast-2", "asn": 64512 },
      { "location": "us-west-2", "asn": 64513 }
    ]
  },
  "segments": [
    { "name": "prod", "description": "운영 환경", "require-attachment-acceptance": false },
    { "name": "dev", "description": "개발 환경", "require-attachment-acceptance": false },
    { "name": "shared", "description": "공유 서비스", "require-attachment-acceptance": false },
    { "name": "onprem", "description": "온프레미스", "require-attachment-acceptance": false }
  ],
  "segment-actions": [
    {
      "action": "share",
      "mode": "attachment-route",
      "segment": "shared",
      "share-with": ["prod", "dev", "onprem"]
    }
  ],
  "attachment-policies": [
    {
      "rule-number": 100,
      "description": "segment 태그 값에 따라 세그먼트에 배정",
      "conditions": [{ "type": "tag-exists", "key": "segment" }],
      "action": { "association-method": "tag", "tag-value-of-key": "segment" }
    }
  ]
}
```

실습 2-4에서 참가자가 `segment-actions`에 다음을 추가한다.

```json
{
  "action": "share",
  "mode": "attachment-route",
  "segment": "onprem",
  "share-with": ["prod"]
}
```

## 10. 정리 순서

순서가 중요하다. 참가자가 만든 것을 먼저 지우고 스택을 지운다.

1. 참가자가 만든 오레곤 VPC attachment 삭제 (prod, 그리고 추가 과제 3-1을 했다면 dev도)
2. 참가자가 만든 Site-to-Site VPN attachment 삭제
3. 참가자가 만든 Site-to-Site VPN 연결 삭제 (8-4절대로 참가자가 만들었으므로 스택이 지우지 않는다)
4. 오레곤 스택 삭제
5. 서울 스택 삭제 (core network는 attachment가 모두 없어야 지워진다)

스택 삭제가 실패하는 원인과 대처를 문서에 적는다.

## 11. 사이트 구성

| 파일 | 번호 | 제목 |
|---|---|---|
| `index.md` | 1-1 | 소개 |
| `prerequisites.md` | 1-2 | 사전 준비 |
| `glossary.md` | 1-3 | 용어 풀이 |
| `lab0.md` | 2-1 | 시작하기 |
| `lab1.md` | 2-2 | 세그먼트와 글로벌 연결 |
| `lab2.md` | 2-3 | 온프레미스 연결 |
| `lab3.md` | 2-4 | 정책으로 통신 범위 바꾸기 |
| `extra-a.md` | 3-1 | 연결 승인과 격리 옵션 |
| `extra-b.md` | 3-2 | Transit Gateway와 비교 |
| `extra-c.md` | 3-3 | 경로 테이블과 지표 보기 |
| `extra-d.md` | 3-4 | 리소스 정리 |
| `concepts.md` | 4-1 | core network policy 읽는 법 |
| `direct-connect.md` | 4-2 | Direct Connect로 연결할 때 |
| `troubleshooting.md` | 4-3 | 문제 해결 |
| `references.md` | 4-4 | 참고 문서 |

### 11-1. 번호 체계

| 단위 | 형식 | 예 |
|---|---|---|
| 묶음 (nav 그룹) | `N.` | `2. 실습` |
| 페이지 (H1) | `N-N.` | `## 2-2. 세그먼트와 글로벌 연결 (22분)` |
| 소절 (H2) | `N-N-a.` | `## 2-2-d. 오레곤 연결 만들기` |

- 소절은 영문 소문자 `a`, `b`, `c` 순으로 붙인다.
- 소절마다 `{ #lab1-d }` 형태의 앵커를 단다. 파일 접두사는 lab0(2-1), lab1(2-2), lab2(2-3), lab3(2-4)이고, extra는 `#a-a`, `#b-a`, `#c-a`, `#d-a` 식이다.
- 교차 링크는 번호와 앵커를 함께 쓴다: `[2-2-d](lab1.md#lab1-d)`.

### 11-2. 집필 관례

`aws-tgw-nat-l200`을 그대로 따른다. `**성공 확인**` 한 줄, 영어 UI 이름 굵게, `{ .shot }` 스크린샷, admonition(`!!! warning`, `!!! tip`, `!!! info`), 쉬운 한국어 존댓말, 처음 나오는 약어 풀어 쓰기.

## 12. 사전 준비와 위험

| 위험 | 대처 |
|---|---|
| core network 생성이 30분을 넘긴다 | 강의 전에 배포를 시작하고, 강의 중간에 상태를 확인한다. 늦는 참가자는 강사 계정 화면으로 따라온다 |
| policy change set 실행 시간이 길다 | 사전 테스트에서 측정한다. 5분을 넘으면 실습 2-4를 강사 시연으로 바꾼다 |
| VPN 터널이 올라오지 않는다 | 라우터 설정을 복사·붙여넣기 한 줄로 제공한다. 터널 상태 확인 단계를 따로 둔다 |
| 계정당 global network 5개 한도 | 임시 계정을 재사용할 때 이전 워크숍의 global network가 남아 있는지 사전에 확인한다 |
| 비용 | 참가자 1명당 약 $1.3~2.7 (edge 2개 $0.50/시간, attachment $0.065~0.09/시간). 정리가 늦으면 늘어난다 |
| 오레곤 리전 EC2·VPC 한도 | 임시 계정에서 오레곤을 처음 쓸 수 있다. 사전에 확인한다 |

## 13. 진행 타임라인 (KST)

시각은 모두 한국 표준시다. 늦으면 멈추고 백로그로 보낸다.

| 시각 | 단계 | 통과 조건 | 상태 |
|---|---|---|---|
| 14:53 | 1차 문서 배포 | `mkdocs build --strict` 통과, 사이트 HTTP 200 | **완료** |
| ~15:15 | Codex 서울 템플릿 리뷰 완료 | 전체 판정 수령 | 진행 중 |
| 15:55~16:25 | 차단 4건 수정 | UserData 크기 실측이 한도 이내, LAN 경로 복구 | |
| 16:10~16:40 | 재검증 | cfn-lint 오류·경고 0, 스크립트 문법 통과 | |
| 16:35~17:20 | 독립 재리뷰 | **차단 0건.** 남으면 배포하지 않는다 | |
| 16:40~17:40 | 2차 문서 배포 | 전체 구성도 + 수정 템플릿 | |
| 16:40~17:40 | 리허설 1차 배포 시작 | 서울·오레곤 스택 `CREATE_IN_PROGRESS` | |
| 17:10~18:10 | core network 완성 | 정책 `LIVE`, change set `Execution succeeded` | |
| 18:40~20:40 | 리허설 1차 + 스크린샷 완료 | 실습 2-1~2-4 전 과정 통과, 측정값을 14절에 기록 | |

### 13-1. 2026-11-16 리뷰에서 나온 차단 (수정 대상)

Codex 리뷰가 커밋 `746d903` 의 서울 템플릿에서 찾은 것이다. **기본값 그대로는 실습을 완료할 수 없다.**

| 구분 | 내용 |
|---|---|
| 확정 차단 | 라우터 UserData가 EC2 한도를 초과해 `OnPremRouterInstance` 생성이 실패한다. Base64 인코딩으로 해결되지 않는 제한 위반이라 배포 없이 확정된다 |
| 확정 차단 | BGP 광고용 `172.16.1.0/24 blackhole` 경로가 실제 LAN 통신을 끊는다. 라우터 ENI는 `172.16.1.64/26`, VM과 EC2 Instance Connect Endpoint는 `172.16.1.0/26` 에 있는데 LAN `/26` 으로 가는 더 구체적인 경로가 없다. 리뷰어가 격리된 네트워크 네임스페이스에서 재현했다. 터널이 올라와도 실습 2-3-d의 ping이 실패하고 라우터 SSH 응답까지 버려진다. `write memory` 로 저장되어 재부팅 후에도 남는다 |
| 조건부 차단 | 인터넷 준비보다 패키지 설치가 먼저 시작할 수 있다 |
| 조건부 차단 | 기본 서브넷이 한 AZ에만 남은 계정에서는 AZ 선택이 실패한다 |

수정 기회는 1회다(전역 지침). 수정 뒤에도 차단이 남으면 작은 잔여 항목을 빼고는 설계를 다시 본다.

## 14. 사전 테스트 측정 로그

아직 하지 않았다. 측정할 항목은 다음과 같다.

- 서울 스택 배포 시간 (core network 생성 포함)
- core network policy가 `LIVE`가 되는 시각
- VPC attachment 생성 → `Available` 시간
- VPN attachment 생성 → `Available` 시간, 터널 `UP` 시간
- policy version 생성 → change set 생성 시간
- change set 실행 → `Execution succeeded` 시간, 실제 통신이 되는 시각
- 스택 삭제 시간
