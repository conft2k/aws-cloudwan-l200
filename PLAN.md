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
| 계정 상태 전제 | **테스트·실습 계정은 항상 아무것도 없는 기본 상태로 배정된다**(사용자 확인, 2026-11-16) | 기본 VPC 1개 외에는 VPC·Cloud WAN 리소스·EC2 Instance Connect Endpoint가 없다. 그래서 VPC 한도(5개), global network 한도(5개), 이전 워크숍 잔재를 강사가 계정마다 확인할 필요가 없다. 한도 계산은 "기본 VPC 1개 + 스택이 만드는 것"만 보면 된다 |
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
| Cloud WAN 홈 리전 | `us-west-2` 고정. **이것은 Network Manager API·콘솔의 홈 리전일 뿐, edge를 둘 수 있는 리전과는 다르다.** 서울은 Cloud WAN GA 리전이므로 edge를 두는 데 문제가 없고(사용자 확인, 2026-11-16), 서울 엔드포인트로 global network 생성도 된다(2026-11-16 `cwan` 계정에서 실제 호출로 확인) | [Cloud WAN 소개](https://docs.aws.amazon.com/network-manager/latest/cloudwan/what-is-cloudwan.html) |

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
- 각 단계의 실제 소요 시간(13절).
- **AZ 선택을 `Fn::GetAZs` 로 되돌린다**(2026-11-16 사용자 지적). 리뷰어가 "기본 서브넷이 한 AZ에만 남은 계정에서 AZ 선택이 실패한다"고 지적해 `${AWS::Region}a`·`c` 로 하드코딩했으나, 그 상황이 실재하지 않는 것을 확인했다. `cwan` 계정 실측(2026-11-16): 서울·오레곤 모두 AZ 4개가 `available` 이고 `opt-in-not-required` 이며, 서울은 기본 서브넷이 4개 AZ 전부에 있다. 하드코딩은 오히려 위험하다. README의 "다른 리전에서 진행할 때"를 따를 때 `${AWS::Region}a` 가 그 리전에 있다는 보장이 없고(AZ가 2개뿐인 리전도 있다), 특정 AZ의 용량 부족을 피할 수도 없다. 표준대로 `!Select [0, !GetAZs ""]` 와 `!Select [1, !GetAZs ""]` 를 쓴다. 재리뷰가 끝난 뒤 반영한다.
- **서울 템플릿에 아직 반영하지 않은 수정 2건**(Codex 리뷰가 끝나는 대로 함께 반영한다). ⑴ dev VPC에 EC2 Instance Connect Endpoint 추가(위 8-1 참조). ⑵ HTTP 응답 형식과 서비스 이름을 오레곤 템플릿과 통일. 지금은 서울이 `you reached <host> (<ip>) / I saw you as <ip>:<port>` 와 `cwanws-whoami`, 오레곤이 `<host> saw <ip>:<port>` 와 `cwan-echo` 로 갈려 있어 참가자가 `curl` 결과를 리전끼리 비교할 때 혼란스럽다.
- 정책 JSON 전체가 API에 받아들여지는지. `tag-exists` 는 2026-11-16 조사에서 **유효한 것으로 확인**했다(Terraform AWS provider의 조건 type 허용 목록에 있고, AWS 공식 예시 3곳 — 3단계 환경, service insertion, 분산 WAN — 이 쓴다). 태그 키 필드 이름도 `key` 가 맞고 `operator` 와 `value` 는 넣지 않는다. 공식 JSON 레퍼런스의 `type` 목록에서만 빠져 있어 문서 누락으로 본다. 그대로 쓰되 배포가 거부되면 `tag-name` 으로 바꾼다.
- **정책을 배포 전에 검증할 수단은 없다.** core network 없이 정책 JSON만 검증하는 API가 없고, CloudFormation이 `PolicyDocument` 를 언제 검증하는지도 문서에 없다. 최악의 경우 30분을 쓰고 실패한다. 리허설 1차의 첫 관문을 서울 스택 배포로 두고, 실패하면 스택 이벤트에서 정책 오류인지부터 본다.

## 9. 초기 core network policy 초안

!!! warning "`description` 에 한글을 쓰지 않는다"
    정책 JSON의 `description` 은 전부 영어로 쓴다. 참가자가 콘솔에서 읽고 **실습 2-4에서 직접 편집**하는 대상이고, 콘솔 언어도 English로 안내한다. 비ASCII 문자가 허용되는지도 확인된 바 없다. 보안 그룹 규칙 Description이 작은따옴표 하나로 배포를 실패시킨 전례가 있다(14-2절). 실습 한가운데서 그 위험을 감수할 이유가 없다.

아래는 배포된 템플릿의 `PolicyDocument` 를 그대로 옮긴 것이다. 템플릿이 기준이고, 이 절은 그 사본이다.

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
    { "name": "prod", "description": "Production", "require-attachment-acceptance": false },
    { "name": "dev", "description": "Development", "require-attachment-acceptance": false },
    { "name": "shared", "description": "Shared services", "require-attachment-acceptance": false },
    { "name": "onprem", "description": "On-premises", "require-attachment-acceptance": false }
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
      "description": "Put an attachment in the segment named by its segment tag",
      "conditions": [{ "type": "tag-exists", "key": "segment" }],
      "action": { "association-method": "tag", "tag-value-of-key": "segment" }
    }
  ]
}
```

edge ASN을 파라미터가 아니라 정수 리터럴로 적은 이유가 있다. `Number` 파라미터를 `!Ref` 로 읽으면 문자열이 되는데 edge ASN은 JSON 숫자여야 한다. 생성 후 변경할 수 없는 값이기도 해서 파라미터로 둘 이유가 없다.

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

`aws-tgw-nat-l200`을 그대로 따른다. `**결과**` 한 줄(실패가 정답인 단계는 `**결과(실패가 맞습니다)**`), 영어 UI 이름 굵게, `{ .shot }` 스크린샷, admonition(`!!! warning`, `!!! tip`, `!!! info`), 쉬운 한국어 존댓말, 처음 나오는 약어 풀어 쓰기.

## 12. 사전 준비와 위험

| 위험 | 대처 |
|---|---|
| core network 생성이 30분을 넘긴다 | 강의 전에 배포를 시작하고, 강의 중간에 상태를 확인한다. 늦는 참가자는 강사 계정 화면으로 따라온다 |
| policy change set 실행 시간이 길다 | 사전 테스트에서 측정한다. 5분을 넘으면 실습 2-4를 강사 시연으로 바꾼다 |
| VPN 터널이 올라오지 않는다 | 라우터 설정을 복사·붙여넣기 한 줄로 제공한다. 터널 상태 확인 단계를 따로 둔다 |
| 계정당 global network 5개 한도 | **확인할 필요 없다.** 2절의 전제대로 실습 계정은 아무것도 없는 기본 상태로 배정된다. 스택이 만드는 global network는 1개뿐이다 |
| 비용 | 참가자 1명당 약 $1.3~2.7 (edge 2개 $0.50/시간, attachment $0.065~0.09/시간). 정리가 늦으면 늘어난다 |
| 서울 VPC 여유가 0 | 리전당 VPC 한도 5개에 기본 VPC 1개가 있으므로 서울 스택의 4개를 더하면 정확히 5개가 된다. **참가자 계정은 문제없다**(아래 2-1절 전제 참조). 다만 **리허설에서는 1차 스택이 완전히 지워진 뒤에 2차를 배포해야 한다.** `DELETE_FAILED` 로 VPC가 남으면 2차가 막힌다. 2026-11-16 `cwan` 계정 실측: 서울 1/5, 오레곤 1/5 |
| 오레곤 리전 EC2 한도 | 임시 계정에서 오레곤을 처음 쓸 수 있다. 사전에 확인한다 |

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

### 13-2. Codex 리뷰 세션 (이어서 쓸 것)

| 항목 | 값 |
|---|---|
| 세션 id | `01a1e2eb-b20e-7a51-bf40-5e7eb2911c41` |
| 인자 | `-m global.openai.gpt-6-astra -c model_reasoning_effort='"high"' -c model_context_window=272000` |
| 첫 리뷰 프롬프트 | `~/.cache/codex-review-cwan-seoul/prompt.md` |
| 첫 리뷰 결과 | `~/.cache/codex-review-cwan-seoul/review.log` (292KB, 최종 판정은 뒷부분) |
| 리뷰어 검증 기록 | `~/.cache/codex-review-cwan-seoul/verification-summary.txt` |
| 재리뷰 프롬프트 | `~/.cache/codex-review-cwan-seoul/prompt-recheck.md` |

재리뷰는 같은 세션을 이어 쓴다. 템플릿을 이미 읽은 맥락이 남아 있어 변경분만 보면 되므로 빠르다.

```bash
cd /home/ec2-user/dev/ws-aws-cloudwan-l200
codex exec resume 01a1e2eb-b20e-7a51-bf40-5e7eb2911c41 \
  -m global.openai.gpt-6-astra -c model_reasoning_effort='"high"' -c model_context_window=272000 \
  - < ~/.cache/codex-review-cwan-seoul/prompt-recheck.md
```

재리뷰 범위는 **차단 4건의 해소 여부와 수정이 새로 만든 문제**로 좁혔다. 첫 리뷰가 이미 확인한 정책 JSON, 정리 의존성, 참가자 입력, 백로그 항목은 다시 보지 않는다. 이것이 임계 경로 위에 있어 전체 완료 시각을 그대로 당긴다.

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

### 14-1. 1차 리허설 (2026-11-16, `cwan` 계정)

| 시각 (KST) | 사건 |
|---|---|
| 16:29:47 | 서울·오레곤 스택 배포 시작 |
| 16:30:19 | 서울 스택 `CREATE_FAILED` — `OnPremRouterSg` (아래 실패 1) |
| 약 16:40 | 오레곤 스택 `CREATE_COMPLETE` (약 10분) |
| 16:41 | 서울 스택 `ROLLBACK_FAILED` (아래 실패 2) |
| **16:43:59** | **core network `AVAILABLE`. 생성에 14분 12초** (문서는 "최대 30분") |

**확인된 것**

- **core network 생성은 14분대다.** 공식 문서 상한의 절반이다. 이론 강의 1시간 안에 넉넉히 끝나므로 진행표의 전제가 성립한다.
- **인라인 `PolicyDocument` 가 동작한다.** core network가 edge 2개, 세그먼트 4개로 만들어졌다. 8-7절의 미확인 항목이 해소됐다.
- **서울 리전 스택이 global network와 core network를 만든다.** 사전 점검의 결론과 일치한다.

### 14-2. 실패 1 — 보안 그룹 규칙 Description의 작은따옴표

```
Invalid rule description. Valid descriptions are strings less than 256 characters
from the following set:  a-zA-Z0-9. _-:/()#,@[]+=&;{}!$*
```

`OnPremRouterSg` 의 규칙 설명에 `the LAN's transit traffic` 을 써서 작은따옴표가 들어갔다. **허용 문자 집합에 `'` 가 없다.** cfn-lint도 Codex 리뷰 두 번도 잡지 못했다. EC2 API만 아는 제약이기 때문이다.

얄궂게도 이것은 **리뷰의 백로그 항목을 고치다 생겼다.** "SG 주석이 실제 규칙과 다르다"는 지적을 받아 설명을 사실에 맞게 다시 쓰면서 들어갔다.

고친 방법: `LAN's` → `LAN`. 템플릿 전체의 Description을 허용 문자 집합으로 다시 훑어 다른 위반이 없음을 확인했다.

**교훈:** 보안 그룹 규칙 Description에는 작은따옴표·큰따옴표·물음표를 쓰지 않는다. 템플릿을 고칠 때마다 Description을 허용 문자 집합으로 훑는다.

### 14-3. 실패 2 — 롤백이 `PENDING` core network를 지우지 못한다 (참가자에게도 일어난다)

```
STATE: PENDING cannot be modified by ACTION: DELETE
```

스택 생성이 실패하면 CloudFormation이 롤백에서 core network 삭제를 시도한다. 그런데 core network는 생성에 14분 이상 걸리므로 그 시점에 `PENDING` 이다. 삭제가 거부되고 스택은 **`ROLLBACK_FAILED`** 로 멈춘다.

**이것은 참가자에게 그대로 일어난다.** 파라미터 실수나 한도 초과로 스택이 실패하면 똑같이 막히고, 참가자는 손쓸 방법이 없다.

**복구 순서**

1. core network가 `PENDING` 을 벗어날 때까지 기다린다(최대 30분, 실측 14분).
   ```bash
   aws networkmanager get-core-network --profile <p> --region us-west-2 \
     --core-network-id <id> --query 'CoreNetwork.State' --output text
   ```
2. `AVAILABLE` 이 되면 스택을 다시 삭제한다. `aws cloudformation delete-stack` 으로 된다.
3. 삭제가 끝난 뒤 재배포한다.

**문서에 반영할 것:** 4-3(문제 해결)에 이 증상과 복구 순서를 넣는다. 참가자가 혼자 판단할 수 있어야 한다.

### 14-4. 스크린샷은 순서대로 찍어야 한다 (2026-11-16에 확인)

1차 리허설이 끝난 환경에서 스크린샷을 찍으려다 알게 된 것이다. **실습을 다 마친 계정에서는 찍을 수 없는 화면이 있다.** 참가자가 그 단계에서 보는 상태가 이미 지나가 버렸기 때문이다.

| 화면 | 참가자가 보는 상태 | 리허설 종료 시점의 상태 |
|---|---|---|
| 2-2-a **Attachments** | 연결 3개 (서울 prod·dev·shared) | 연결 5개 (오레곤 prod와 VPN까지) |
| 2-2-d attachment 만드는 폼 | 빈 폼 | 이미 만들어져 있음 |
| 2-3-f 온프레미스 → prod ping | **실패** | 정책 v2가 `LIVE` 라 **성공** |
| 2-4-b change set 검토 | 실행 전 | `EXECUTION_SUCCEEDED` |
| 2-1 CloudFormation 업로드·파라미터·진행 중 | 생성 중 | 이미 `CREATE_COMPLETE` |

**결론: 단계 순서대로 찍어야 하는 화면은 새 배포에서 실습을 따라가며 찍는다.** 끝난 환경에서 찍어도 되는 것은 상태가 변하지 않는 화면뿐이다. core network **Overview**, 세그먼트 경로 테이블, **Policy versions** 목록, VPN **Tunnel details** 가 거기에 해당한다.

마침 템플릿을 깨끗하게 처음부터 배포한 적이 아직 없다. 서울 스택은 1차 배포가 실패한 뒤 **업데이트**로 고친 것이라(`UPDATE_COMPLETE`), 최종 템플릿의 `CREATE` 경로는 검증되지 않았다. 2차 리허설은 스크린샷과 템플릿 검증을 한 번에 해결한다.

### 14-5. 콘솔 캡처에서 고친 것

- **로그인 계정 이메일이 모든 화면에 찍힌다.** 콘솔은 오른쪽 위에 로그인 신원을 표시하는데, IAM Identity Center에서는 그것이 실제 이메일 주소다. 계정 ID 마스킹은 이것을 건드리지 않는다. `tools/console.py` 의 마스킹에 이메일 치환을 넣고, 남아 있으면 촬영을 거부하게 했다.
- **표의 열 폭은 고정이다.** 콘솔 표는 `table-layout: fixed` 에 모든 열이 168px여서 `cwan-ws-att-prod-apne2` 가 `cwan-ws-att...` 로 잘린다. **열을 숨겨도 소용없다** — 비는 자리는 그대로 비어 있고 남은 열은 168px를 유지한다. 창을 넓히거나 내비게이션을 접는 것도 같은 이유로 효과가 없다. 헤더마다 있는 크기 조절 핸들(`button.awsui_resizer_*`)을 끌어야 한다(`resize_column()`).
- **core network 화면 구조.** **Attachments** 와 **Policy versions** 는 탭이 아니라 **왼쪽 메뉴** 항목이다. **Segments** 라는 탭은 없다. core network 탭은 Overview, Details, Sharing, Flow logs, Topology graph, Topology tree, Logical, Routing information base, Routes, Events, Monitoring이다. 세그먼트 개수는 **Overview** 탭의 **Inventory** 에서 본다. Network Manager는 리전에 묶이지 않아 리전 선택에 **Global** 이 뜬다. 문서의 조작 순서를 여기에 맞춰 고쳤다.


아직 하지 않았다. 측정할 항목은 다음과 같다.

- 서울 스택 배포 시간 (core network 생성 포함)
- core network policy가 `LIVE`가 되는 시각
- VPC attachment 생성 → `Available` 시간
- VPN attachment 생성 → `Available` 시간, 터널 `UP` 시간
- policy version 생성 → change set 생성 시간
- change set 실행 → `Execution succeeded` 시간, 실제 통신이 되는 시각
- 스택 삭제 시간

## 15. 2차 리허설 운영 계획 (2026-11-16 20:43 시작)

1차 리허설이 끝난 환경에서는 단계별 화면을 찍을 수 없다는 것이 14-4절의 결론이다. 사용자가 2차 리허설을 선택했다(2026-11-16 20:40). 이 리허설은 두 가지를 한 번에 끝낸다. **최종 템플릿의 `CREATE` 경로 검증**과 **실습 순서대로 찍은 스크린샷**이다.

| 시각 (KST) | 단계 | 통과 조건 |
|---|---|---|
| 21:03 | 서울·오레곤 스택 배포 시작 | 두 스택 `CREATE_IN_PROGRESS`, 2-1 화면 캡처 완료 — **끝남** |
| ~21:18 | core network 준비 | 정책 `LIVE`, change set `EXECUTION_SUCCEEDED` |
| 21:20 | 2-2-a 캡처 | **Attachments** 에 서울 연결 3개만 보이는 상태에서 촬영 |
| 21:35 | 2-2-d~f | 오레곤 prod attachment 생성, 서브넷 경로 추가, 리전 간 ping 성공 |
| 22:00 | 2-3-a~f | VPN 연결·attachment 생성, 터널 2개 UP, shared 성공·prod 실패 |
| 22:35 | 2-4-a~d | change set 검토·실행, 실행 후 prod 성공·dev 실패 |
| 23:00 | 3-1 (추가 과제) | 승인 요구 켜고 되돌리기, 오레곤 dev attachment, 격리 켜고 되돌리기 |
| 23:50 | 3-3 (추가 과제) | 세그먼트별 경로 테이블 비교 |
| 00:05 | 3-4 (추가 과제) = 정리 | 콘솔로 지우며 촬영, 삭제 소요 시간 측정, 잔재 0 |

추가 과제는 전부 포함한다(사용자 결정, 2026-11-16 21:10). 3-2는 콘솔 화면이 아니라 구성도라 리허설 범위 밖이다. 3-3은 2-3-d와 같은 Routes 탭이라 세그먼트만 바꿔 찍는다. 3-4는 정리 과정 그 자체라, 리허설을 끝내면서 찍어야만 얻을 수 있고 삭제 소요 시간도 거기서 측정된다.

**늦으면 멈춘다.** 단계마다 30분을 넘기면 그 단계의 남은 캡처는 백로그로 보내고 다음 단계로 간다. 환경을 켜 둔 채로 끝내지 않는다. edge 2개가 시간당 $0.50이다.

**순서가 중요한 캡처 (이 리허설에서만 얻을 수 있다)**

| 단계 | 찍어야 하는 상태 |
|---|---|
| 2-1 | CloudFormation 템플릿 업로드, 파라미터 폼, 확인 체크박스, `CREATE_IN_PROGRESS` |
| 2-2-a | **Attachments** 에 연결 3개만 (오레곤과 VPN 생기기 전) |
| 2-2-d | attachment 생성 폼과 태그 입력 |
| 2-3-a~c | VPN 연결 생성 폼, attachment 생성, 터널 UP |
| 2-3-f | 온프레미스 → prod ping **실패** (정책 v2 적용 전) |
| 2-4-b~d | change set 검토, 실행 중, 실행 완료 |

**상태 파일:** `~/.cache/cwan-shots/` 에 단계별 로그를 남긴다. Claude 세션이 끊기면 거기서 이어 간다.

### 15-0. 2차 리허설 실측 (2026-11-16, `demo1`)

| 시각 (KST) | 사건 |
|---|---|
| 21:03:38 | 서울·오레곤 스택 생성 시작 (CLI, 템플릿은 S3 경유) |
| 21:10 | 오레곤 스택 `CREATE_COMPLETE` — **약 7분** |
| **21:19:17** | **core network `AVAILABLE`, 정책 1 `LIVE`/`EXECUTION_SUCCEEDED` — 15분 14초** |
| 21:22~21:25 | 서울 VPC attachment 3개 `CREATING` → `PENDING_NETWORK_UPDATE` → `AVAILABLE`. 관측 시작부터 2분 48초 |
| 21:24 | 서울 스택 `CREATE_COMPLETE` (시작부터 약 21분) |
| 21:38~21:42 | 오레곤 prod VPC attachment: 콘솔로 생성, **4분 15초** 만에 `AVAILABLE` |
| 21:50~21:54 | Site-to-Site VPN attachment: **3분 30초** 만에 `AVAILABLE` |
| 21:54 | `setup-tunnels.sh` 실행. 끝났을 때 이미 IPsec 2개 `ESTABLISHED`, BGP 이웃 2개 연결, `10.30.1.0/24` 수신 |
| 22:00:50 | 정책 버전 2 생성 |
| **22:01:28** | **change set `READY_TO_EXECUTE` — 38초** |
| 22:03~22:05 | change set 실행 — **약 1분** |
| 22:13~22:14 | 정책 v3(`dev` 승인 요구 켜기) 생성부터 적용까지 **70초** |
| 22:34~22:37 | 정책 v4(`dev` 격리 켜기) — change set 변경 **2건** |
| 22:38~22:40 | 정책 v5(되돌리기) |
| 22:47~22:51 | 오레곤 attachment 2개와 VPN attachment 삭제. VPN attachment는 확인 창 뒤 **22초** 만에 사라짐 |
| 22:53:20 | 오레곤 스택 삭제 시작 |
| 22:54:53 | **오레곤 스택 삭제 완료 — 1분 32초** |
| **23:09:26** | **서울 스택 삭제 완료 — 14분 32초.** core network와 global network가 함께 사라짐. 잔재 0 |

**서울 스택 삭제는 14분 32초로 생성(15분 14초)과 거의 같다.** core network 삭제가 대부분을 차지하기 때문이다. 참가자에게 마지막 삭제가 15분쯤 걸린다고 미리 알려 줘야 한다.

통신 확인은 모두 `tools/ec2run.sh` 로 실제 출력을 받아 문서에 넣었다. 서울 prod→dev `100% packet loss`, prod→shared `0%` 약 1.1ms, prod→오레곤 prod `0%` 약 116ms, 온프레미스→shared `0%` 약 2.7ms, 온프레미스→prod `100%`.

**정책 버전을 만들기만 해서는 아무것도 바뀌지 않는다.** 버전 2가 `READY_TO_EXECUTE` 인 상태에서 온프레미스→prod ping이 그대로 `100% packet loss` 였다. 2-4-b의 설명을 실측으로 확인했다.

core network 생성은 1차 14분 12초, 2차 15분 14초다. **두 번 모두 공식 문서 상한(30분)의 절반 근처**이고, 이론 강의 1시간 안에 끝난다는 진행표 전제가 두 번 확인됐다.

서울 스택은 core network가 준비된 뒤에도 `CREATE_IN_PROGRESS` 다. EC2 부트스트랩과 VPC attachment 생성이 남아서다. **2-1-d가 스택 상태가 아니라 정책 상태를 준비 기준으로 삼은 것이 맞다.**

인라인 템플릿은 51,200자 한도를 넘는다(서울 템플릿 71KB). CLI로 배포하려면 S3에 올려 `--template-url` 을 써야 한다. 참가자는 콘솔의 **Upload a template file** 을 쓰므로 콘솔이 알아서 올린다. 문서에 영향 없다.

### 15-1. 2차 리허설에서 답을 내야 하는 미확인 항목

| 항목 | 지금 문서 | 확인할 것 |
|---|---|---|
| 정책 편집 모드 | 2-4-a가 JSON 조각을 넣으라고 한다 | 편집기는 **Choose policy view mode** 에서 **Visual editor** 와 **JSON** 중 하나를 고르게 한다. 기본값은 **Visual editor** 다. JSON으로 바꾸는 단계를 문서에 넣을지, 아니면 **Segment actions** 폼으로 바꿀지 정한다 |
| IAM 확인란 | 2-1-b 6단계가 "보이면 선택합니다" 로 얼버무린다 | 서울 스택 검토 화면에 실제로 나오는지 보고 단정해 쓴다 |
| attachment 생성 시간 | "사전 테스트에서 측정합니다" | 오레곤 VPC attachment가 `Available` 이 되기까지 실측 |
| 리전을 바꿔야 하는가 | 2-2-d 1단계가 "리전을 **US West (Oregon)** 으로 바꿉니다" 로 시작한다 | Network Manager는 리전에 묶이지 않는다. attachment 생성 폼이 **Edge location** 을 고른 뒤 그 리전의 VPC를 보여 주는지, 아니면 콘솔 리전 선택을 따르는지 확인한다. 전자라면 리전을 바꾸라는 단계가 불필요하다 |
| 터널 수렴 시간 | 같음 | `setup-tunnels.sh` 실행부터 `show ip route bgp` 에 `10.30.1.0/24` 가 뜰 때까지 실측 |
| change set 실행 시간 | 같음 | 실행부터 `EXECUTION_SUCCEEDED` 까지 실측. 5분을 넘으면 2-4를 강사 시연으로 바꾼다(12절) |
| BGP 이웃 주소 | 2-3-c의 확인 명령이 `show ip bgp neighbors 169.254.21.1 advertised-routes` 로 **주소를 고정**해 두었다 | 터널 내부 주소(`169.254.x.x/30`)는 **VPN 연결마다 AWS가 새로 배정한다.** 1차 리허설의 값이 그대로 들어간 것으로 보인다. 참가자 계정에서는 다른 주소가 나오므로 이 명령은 빈 결과를 낸다. 주소를 묻지 않는 명령으로 바꾼다 |

### 15-2. 리허설 계정

`demo1`(`884747280022`)을 쓴다. 사용자 지정(2026-11-16 21:10). 완전 초기화 상태를 확인했다. 서울·오레곤 모두 기본 VPC 1개뿐이고 global network, 스택, EC2, EIP, VPN이 없다. VPC 한도는 리전당 5개라 서울은 스택 4개를 더하면 정확히 5/5가 된다. 기본 서브넷은 두 리전 모두 4개 AZ에 있어 AZ 선택 차단은 생기지 않는다.

`cwan`(`912748707045`)의 1차 환경은 10절 순서대로 지웠다.

### 15-3. 콘솔 자동화에서 드러난 것 (2026-11-16 22:00 전후)

처음 쓰는 계정에서만 나타나는 것들이다. `cwan` 세션에는 이미 상태가 저장되어 있어 1차 리허설에서는 보이지 않았다.

- **쿠키 동의 배너가 마법사 버튼을 가린다.** 신규 계정의 첫 방문에 뜨고, 창 아래쪽을 덮어 **Next** 와 **Create stack** 을 가린다. 참가자도 똑같이 겪는다. 배너의 버튼 이름은 빌드에 따라 **Accept** 또는 **Accept all cookies** 다.
- **마지막 버튼은 Submit이 아니라 Create stack 이다.** 문서가 **Submit** 으로 적고 있었다. 고쳤다.
- **IAM 확인란은 반드시 나온다.** **Review and create** 맨 아래 **Capabilities** 에 `The following resource(s) require capabilities: [AWS::IAM::Role]` 과 함께 확인란이 하나 나오고, 선택하지 않으면 `Please acknowledge all checkboxes before proceeding.` 로 막힌다. 2-1-b 6단계의 "보이면 선택합니다" 를 단정형으로 고쳤다.
- **스택 생성 마법사는 4단계다.** Step 1 Create stack, Step 2 Specify stack details, Step 3 Configure stack options, Step 4 Review and create. 파라미터는 기본값 그대로 두면 된다.

### 15-7. 리허설이 찾아낸 문서 오류 (실제 화면으로 확인)

참가자가 그대로 따라 하면 **막히는** 것부터 적는다.

| 쪽 | 문서가 적고 있던 것 | 실제 |
|---|---|---|
| 2-3-c | `show ip bgp neighbors 169.254.21.1 advertised-routes` | 터널 내부 주소는 VPN 연결마다 AWS가 배정한다. 이번 리허설은 `169.254.203.157`, `169.254.241.109` 였다. 주소를 묻지 않는 명령으로 바꿨다 |
| 2-3-b | Attachment type = **Site-to-Site VPN** | **VPN**. 선택지는 VPN / VPC / Connect / Transit gateway route table / Direct Connect Gateway |
| 2-3-c | "**EC2 Instance Connect** 탭에서 **Connection Type** 을…" | 그런 탭도 그런 칸도 없다. 화면은 **Connect to Linux instance**, 탭은 **In web browser** / **In SSH client** |
| 2-4-a | "현재 정책을 편집하고 새 버전을 만듭니다" | 편집기는 **Visual editor** 로 열린다. **Choose policy view mode** 에서 **JSON** 으로 바꿔야 JSON을 붙여 넣을 수 있다 |
| 2-2-d | 입력 표에 **Core network** 행 | 그런 칸이 없다. 이미 core network 안에서 만들고 있다 |
| 3-1-d | 승인과 라우트 순서를 적지 않음 | **승인 전에는 VPC에 core network 라우트를 넣을 수 없다**(`InvalidCoreNetworkArn.NotFound`). 승인이 필요 없는 연결은 `Creating` 중에도 된다 |

그 밖의 정정: **Attachments** 와 **Policy versions** 는 탭이 아니라 왼쪽 메뉴, **Segments** 탭은 없음(개수는 **Overview** 의 **Inventory**), Network Manager는 리전 선택이 **Global**, 마법사 마지막 버튼은 **Submit**, 경로 표의 열은 **Route type** / **Route state** 에 조회 버튼은 **Search routes**, VPN 터널 표는 **Tunnel details** 탭 안의 **Tunnel state**, attachment 이름은 태그가 아니라 폼의 **Name** 칸, 서브넷은 **VPC** 를 고른 뒤 AZ마다 한 줄씩 나타남.

### 15-6. 자동화 백로그 (문서 문제가 아니라 도구 문제)

리허설을 멈추지 않으려고 CLI로 돌려 넘긴 것들이다. **어디까지 눈으로 봤는지는 자리마다 다르다.** `lab1-route-02-edit` 과 `extraD-03` 은 문제가 난 지점까지 화면이 문서와 맞는 것을 확인했지만, `extraD-04`·`extraD-05` 는 **스택 화면의 Delete 버튼을 끝내 찾지 못했다.** 즉 3-4-d와 3-4-e의 "**Delete** 를 누릅니다" 와 "확인 창에서 삭제를 확정합니다" 는 **실행으로 확인되지 않은 단계다.** CloudFormation의 보통 UI를 따른 것이지만 집필 규칙(직접 실행한 것만 적는다)에는 미달이므로 3차 캡처 때 가장 먼저 확인할 것.

| 자리 | 무엇이 막혔나 | 대신 한 일 |
|---|---|---|
| `lab1-route-02-edit` | **Edit routes** 에서 **Target** 종류로 **Core Network** 까지는 골랐는데, 그다음 core network를 고르는 드롭다운을 찾지 못했다(`core network choices: 0`). 문서의 2단계 설명은 화면과 맞다 | `aws ec2 create-route --core-network-arn` 으로 경로 2개를 넣었다. 결과 화면(`lab1-route-03-saved`)은 찍었다 |
| `extraD-03-delete-vpn` | **Actions** → **Delete VPN connection** 클릭이 탭 패널에 가로막혔다 | `aws ec2 delete-vpn-connection` 으로 지웠다 |
| `extraD-04-delete-oregon-stack`, `extraD-05-delete-seoul-stack` | **풀렸다 (2026-11-16).** 버튼 이름이 **Delete** 가 아니라 **Delete stack** 이다. `Delete` 로 역할+이름·정확한 텍스트를 찾으니 0개가 나온 것이다. 실제 클래스는 `e2e-test-delete-stack-button awsui_button_…` 이고 `awsui_primary-button` 이 아니라 `variant-normal` 이라 15-6이 예상한 클래스 매칭으로도 안 잡혔다 | `aws cloudformation delete-stack` 으로 지웠고, 나중에 빈 스택으로 화면을 확인했다 |

**막히는 패턴이 일정하다.** 표의 행 선택과 행 단위 메뉴는 잘 되는데, **툴바의 단일 동작 버튼**(`Delete`, `Connect`, `Submit`)은 역할+이름으로 잡히지 않을 때가 많다. 해결책도 일정했다. Cloudscape가 붙이는 클래스(`button[class*="awsui_primary-button"]`)로 찾거나, 전용 해시 URL로 바로 들어가는 것이다(`#ConnectToInstance:instanceId=` 가 그랬다). 남은 세 장도 같은 방법으로 풀릴 것으로 본다.

**확인 창 중복은 해소했다 (2026-11-16).** 2026-11-16 리뷰가 판단 사안으로 올린 것이다 — `tools/shots/extra-delete.py` 의 `confirm_dialog()` 와 `tools/shots/probe-stack-delete.py` 가 확인 창 입력 선택자와 "이름 입력 → 대기 → 버튼 클릭" 순서를 똑같이 갖고 있어서, 콘솔 확인 절차가 바뀌면 두 곳을 함께 고쳐야 했다. 두 파일은 `tools/console.py` 가 `exec` 으로 돌리는 스크립트라 서로 import 할 수 없으므로, 리뷰 때 적어 둔 대로 **`console.py` 의 exec 전역으로 옮겼다.** 이제 `confirm_dialog(shot_name, type_name, probe)` 와 `body(f)` 는 `page`·`app`·`shot` 과 같은 자리에서 주입된다.

- `probe=True` 는 스크린샷 대신 **버튼이 입력 전후에 활성인지**를 찍는다. 15-10을 알아낸 방식이 인자 하나로 남았다.
- 두 파일에 똑같이 있던 `body(f)` 도 같이 올렸다.
- 두 스크립트의 **목적은 여전히 다르다.** `extra-delete.py` 는 캡처와 삭제를, `probe-stack-delete.py` 는 "이 화면의 버튼 이름이 진짜 무엇인가"를 찍는 진단을 맡는다. 진단 쪽에는 그 일을 하는 `buttons()` 만 남았고, 찾기를 시도하는 선택자 목록에 `^Delete stack$` 을 넣어 두어 다음에 같은 일이 생기면 어느 방식이 빗나가는지 한눈에 보인다.

`lab1-core-03-attachment-tags` 는 **해결했다.** 행의 선택 버튼으로 고르면(`select_row()`) 상세 창이 열리고 **Tags** 탭이 있다. 이름 셀을 클릭하던 것이 원인이었다. **Name** 열의 글자는 링크가 아니다.

### 15-5. 캡처 뒤에 남는 일: 자리를 이미지로 바꾸기

지금 페이지들의 스크린샷 자리는 `<!-- shot: 이름 -->` 주석이라 **사이트에 아무 그림도 보이지 않는다.** 캡처가 끝나면 주석을 실제 이미지로 바꿔야 한다.

```markdown
![본문이 가리키는 것을 설명하는 대체 텍스트](images/console/lab1-core-02-attachments.png){ .shot }
```

- 대체 텍스트는 구성도와 같은 기준으로 쓴다. 그림을 보지 않고도 그 단계에서 무엇을 확인해야 하는지 알 수 있어야 한다.
- 찍지 못한 자리는 주석을 그대로 둔다. 빈 이미지 링크를 만들지 않는다. `mkdocs build --strict` 가 없는 파일을 잡아 준다.
- **그 그림이 필요 없다고 결정한 자리는 주석도 지운다.** 남겨 두면 할 일이 남은 것처럼 보인다. 3-4-c·3-4-d·3-4-e의 세 자리가 그렇다(사용자 결정, 2026-11-16: "리소스 정리라면 중요도가 낮으니 실제 이미지 캡쳐 화면은 생략해도 좋다"). 확인 창 한 장씩이고, 같은 모양의 창은 3-4-a·3-4-b에 이미 있다.
- 11-2절의 `{ .shot }` 관례를 따른다.

### 15-4. 스크린샷 크롭 기준 (사용자 지정, 2026-11-16 21:50)

전체 창이 아니라 **본문이 가리키는 패널만** 남긴다. 콘솔 창은 대부분 내비게이션과 여백이라 정작 읽어야 할 표가 작게 들어간다.

- `card("<패널 제목>")` 이 그 제목을 담은 Cloudscape 컨테이너를 찾아 crop 영역으로 돌려준다.
- 한 단계가 두 패널을 함께 읽어야 하면 `span()` 으로 묶는다. 경로 화면이 그렇다. **Route Filter** 없이 **Routes** 표만 남기면 어느 세그먼트의 표인지가 사라진다.
- 패널을 못 찾으면 전체 창을 남기고 로그에 적는다. 조용히 빈 그림을 만들지 않는다.
- crop 영역은 `shots/crops.json` 에 기록되어 `shots/crop.py` 가 원본에서 같은 영역을 다시 잘라낼 수 있다.

### 15-8. 단계와 맞지 않는 행을 잘라내기 (2026-11-16, 사용자 지시)

14-4가 경고한 함정("완성된 환경에서는 단계 순서대로 찍을 수 없다")에 세 장이 실제로 걸렸다. 화면 자체는 진짜인데, 찍은 시각이 늦어서 **그 단계에서는 아직 없어야 할 연결까지 목록에 들어 있었다.**

| 이미지 | 찍은 시각 (KST) | 들어가 있던 남의 행 | 맞는 줄 수 |
|---|---|---|---|
| `lab1-core-02-attachments` (2-2-a) | 22:50 | 정리 중이라 `Deleting` 두 줄(onprem VPN, us-west-2 VPC) | 3 |
| `lab1-attach-04-available` (2-2-d) | 22:44 | 3-1의 `cwan-ws-att-dev-usw2`, 2-3의 onprem VPN | 4 |
| `lab2-attach-02-available` (2-3-b) | 22:45 | 3-1의 `cwan-ws-att-dev-usw2` | 5 |

`lab1-core-02-attachments` 는 **이미 본문에 쓰이고 있었다.** 대체 텍스트는 "연결이 세 개뿐"이라고 적었는데 그림에는 다섯 줄이 있었고, 같은 페이지의 "`onprem` 세그먼트는 아직 비어 있습니다" 안내와도 어긋났다. 나머지 두 장은 정직하지 않다고 보고 뺐던 것인데, 사용자가 **화면에서 수정해서 쓰라**고 지시했다.

기준은 이렇다.

- 남의 행은 **잘라낸다**. 행 띠(행 내용 + 그 아래 구분선)를 통째로 들어내고 아래 행을 끌어올린다. 콘솔이 행 하나 적게 그렸을 때와 같은 그림이 된다.
- 패널 제목 옆의 **행 개수 표시는 지운다**. 네 줄짜리 그림 위의 `(6)` 은 그림과 모순된다. 숫자를 고쳐 그리지 않는 이유는 콘솔이 Amazon Ember 웹폰트로 그리기 때문이다. 가진 폰트로 다시 그리면 진짜 글자 옆에 다른 서체의 숫자가 앉는다. 실제로 Noto Sans·Liberation·DejaVu로 맞춰 봤지만 획 모양이 달라 바로 티가 났다. 개수 표시가 없는 제목은 Cloudscape가 개수를 알기 전에 그리는 모습이라 어색하지 않고, 줄은 눈으로 세면 된다.
- 어느 행을 들어냈는지와 왜 그랬는지를 `shots/retouch.json` 에 적는다. `shots/crop.py` 가 크롭 뒤에 자동으로 적용하므로, 한 번 돌리면 페이지가 쓰는 이미지가 그대로 다시 만들어진다.
- 좌표는 **크롭된 그림 기준**이다. crop 영역을 옮기면 다시 재야 한다. `retouch.json` 의 `size` 가 그 안전장치다. 크기가 다르면 자르지 않고 건너뛴다. `shots/trim.py` 도 이 세 장은 건드리지 않는다.

**다시 찍는 것이 원칙이고 잘라내는 것은 예외다.** 원본이 남지 않은 두 장(`lab1-attach-04`, `lab2-attach-02`)은 git 기록에서 되살려 `shots/raw/` 에 넣었으므로, 실제 raw 창이 아니라 이미 크롭된 그림이 원본 자리에 있다. 3차 리허설을 하게 되면 이 세 장은 **단계 순서대로 다시 찍는다.**

### 15-9. 스크린샷 전수 감사 (2026-11-16)

세 장을 고치면서 `lab1-core-02-attachments` 가 **이미 본문에 쓰이는데도** 틀린 상태를 보여 주고 있었다는 것이 우연히 드러났다. 한 장이 그랬다면 다른 장도 그럴 수 있으므로 **쓰고 있는 이미지 43장을 전부** 페이지별로 나눠 감사했다. 기준은 두 가지였다. ① 화면에 보이는 상태가 그 단계에 존재할 수 있는가 ② 대체 텍스트가 실제 픽셀과 맞는가.

**단계와 맞지 않아 고친 것**

| 이미지 | 무엇이 틀렸나 | 어떻게 했나 |
|---|---|---|
| `lab0-cnet-01-policy-versions` | 2-1-d의 **준비 확인 그림**인데 정책 버전이 다섯 개이고 `LIVE, LATEST` 가 5번에 붙어 있었다. 2-1-d 시점에는 버전 1개가 LIVE다. 본문이 "**Alias** 가 LIVE 이면 준비 끝"이라고 가르치는데 그림의 1번은 Alias가 `-` 였다 | 같은 표 5번 행의 `LIVE, LATEST` 셀을 1번 행으로 옮기고(실제 콘솔이 그린 픽셀이다) 2~5번 행을 들어냈다. 행 간격이 정확히 38px의 배수라 셀이 어긋나지 않는다 |
| `lab1-core-02`, `lab1-attach-04`, `lab2-attach-02` | 15-8 참조 | 남의 행 제거, 행 카운터 제거 |
| 같은 세 장 | **Last updated** 시각 때문에 2-2-a 그림(22:50)이 2-2-d 그림(22:44)보다 늦게 찍힌 것이 드러났다. 나란히 보면 순서가 거꾸로 읽힌다 | 시각 블록을 지웠다. 캡처 메타데이터이지 단계 내용이 아니다 |

**대체 텍스트가 픽셀과 달라 고친 것**

- `lab1-route-01-outputs` — "`ProdVpcId`, `ProdAppRouteTableId` … 값들이 들어 있다"고 적었지만 화면에 보이는 것은 `Dev…` 여섯 줄이고 `ProdAppRouteTableId` 는 맨 아래 반쯤 잘려 있다. **Key** 오름차순이기 때문이다. 바로 위 단계가 그 값을 찾으라고 시키므로 스크롤·검색 안내를 함께 넣었다.
- `lab0-cfn-03-ack` — 확인란은 이미 체크되어 있고 `Please acknowledge all checkboxes before proceeding.` 오류는 그림에 없다. 그 문장은 본문에만 둔다.
- `extraD-01-delete-attachment` — 15-8에서 여백을 걷어내 확인 창만 남겼는데 대체 텍스트는 그대로 "뒤로 목록과 상세 창이 보인다"였다. **크롭을 바꾸면 대체 텍스트도 다시 읽어야 한다.**

**그림을 빼고 본문으로 돌린 것**

- `lab2-router-01-connect`, `lab2-vm-01-connect` — 둘 다 **Public subnet access / EC2 Instance Connect** 가 선택된 화면이다. 본문은 **EC2 Instance Connect Endpoint** 를 고르라고 하므로 그림이 본문과 반대였고, VM 쪽은 `No public IPv4 or IPv6 address assigned` 경고에 **Connect** 가 비활성이라 **그대로 따라 하면 막히는 화면**이었다. 2-2-b와 같은 화면이라 그쪽 그림을 가리키게 하고 두 장은 지웠다.
- 다만 그 첫 번째 카드가 선택된 상태는 **콘솔의 기본값**이다(2-2-b의 `lab1-eic-01-connect` 도 같다). 그래서 2-2-b 대체 텍스트에 경고 배너와 비활성 **Connect** 를 적어 두었다. 참가자가 반드시 만나는 화면이다.
- `extraC-02-route-table-dev` 는 `extraA-02-oregon-dev-route` 와 **바이트까지 같은 파일**이었다(원본도 같다). 한 장만 두고 extra-c 에서 그 경로를 가리킨다.

**전제가 빠져 있던 것**

- `extraA-b1`, `extraA-b2` (승인 대기 화면) — 기본 정책은 `require-attachment-acceptance` 가 `false` 라 참가자는 이 상태를 볼 수 없다. "승인을 켠 뒤의 화면"이라는 단서를 넣었다.
- `extraC-02`(=`extraA-02`) 의 `10.21.1.0/24` 는 추가 과제 3-1을 해야 생기는 경로인데 3-3은 3-1을 전제하지 않는다. 3-1을 건너뛰면 경로가 두 개라고 적었다.
- `extraA-04b-isolate-executing` 는 **어느 페이지도 참조하지 않고 있었다.** 3-1-f 3단계(실행 중)에 그대로 맞는 그림이라 본문에 넣었다.

**남은 교훈:** 크롭·보정·대체 텍스트는 한 묶음이다. 그림을 자르거나 행을 들어낼 때마다 그 그림의 대체 텍스트를 다시 읽는다. 이번에 고친 10건 중 3건이 대체 텍스트만의 문제였고, 그중 하나는 바로 앞 작업(여백 크롭)이 만든 것이다.

### 15-10. 스택 삭제 확인 창 (2026-11-16, 빈 스택으로 확인)

3-4-d·3-4-e는 리허설에서 CLI로 지워서 화면을 못 봤다(15-6). 사용자 승인을 받아 **요금 0원짜리 빈 스택**(SSM 파라미터 하나, `cwan-ws-probe-delete`)을 `demo1` 에 만들고 콘솔에서 끝까지 지워 보며 확인했다. 확인 뒤 스택과 파라미터 모두 사라진 것을 확인했고 `demo1` 에 남은 스택은 없다.

| 물음 | 답 |
|---|---|
| 스택 화면의 버튼 이름 | **Delete stack** 이다. 문서가 적고 있던 **Delete** 가 아니다 |
| 확인 창 제목 | `Delete stack?` |
| 본문 | `Delete stack <이름> permanently? This action cannot be undone.` / `Deleting this stack will delete all stack resources. Resources will be deleted according to their DeletionPolicy.` |
| **입력을 요구하는가** | **그렇다.** `Type "<스택 이름>" to confirm deletion of the stack.` 이라고 적혀 있고, 그 칸이 비어 있는 동안 **Delete stack** 버튼은 비활성이다. 이름을 넣으면 활성화된다(실측: 입력 전 `False` → 입력 후 `True`) |
| 창의 버튼 | **Cancel** 과 **Delete stack** |
| 그 밖에 | **Express mode - new** 선택지가 있다. `Delete this stack faster. Resource cleanup runs without waiting for each resource to finish stabilizing.` **워크숍 스택으로는 시험하지 않았다.** 기본값(꺼짐)으로 두라고 문서에 적었다 |

**이것이 왜 중요한가.** 워크숍의 **마지막 단계**에서 참가자가 회색 버튼 앞에 멈춰 선다. 3-4-a·3-4-b의 attachment 삭제 창은 **Delete** 만 누르면 되므로, 같은 요령일 것이라 생각하고 입력 칸을 지나칠 가능성이 높다. 게다가 서울 스택 삭제는 14분 32초가 걸려서 참가자가 이미 조바심을 내는 자리다.

**자동화에도 같은 교훈.** 15-6은 "툴바 단일 동작 버튼은 `awsui_primary-button` 클래스로 찾으면 된다"고 추정했는데 **그 추정이 틀렸다.** 이 버튼의 클래스는 `e2e-test-delete-stack-button awsui_button_… awsui_variant-normal_…` 이다. 원인은 클래스가 아니라 **이름이 달랐던 것**이다. 찾는 이름이 틀렸을 때는 선택자 기법을 바꾸기 전에 **그 화면의 버튼 이름을 먼저 전부 찍어 보는 것**이 빠르다. `tools/shots/probe-stack-delete.py` 가 그 일을 한다.

### 15-11. 독립 리뷰 3축 (2026-11-16, Codex)

문서가 어느 정도 갖춰진 뒤 `/code-review` 로 두 축(Standards, Spec)을 돌리고, 사용자 요청으로 **L200 수준 적합성** 축을 하나 더 돌렸다. 모두 `gpt-6.1-sol`, effort high. 세 축을 **각각 독립 세션**으로 돌려 서로의 결론이 섞이지 않게 했고, 재리뷰는 같은 세션을 이어 범위를 좁혀 물었다.

| 축 | 1차 | 최종 |
|---|---|---|
| Standards (`CLAUDE.md` 집필 규칙 + Fowler 냄새) | 하드 1, 판단 2 | **차단 0.** 백로그로 받았던 중복 1건도 뒤에 해소했다(15-6) |
| Spec (`PLAN.md` 대조) | 4건 | **전부 해소, 새 차단 0** |
| L200 수준 | 15건 | **전부 해소** (해소 8 → 13 → 15, 재리뷰 3회) |

**가장 값졌던 지적 셋.**

1. **3-4 실패 복구 절이 아직 `Delete` 였다.** 같은 페이지에서 `Delete stack` 으로 고쳐 놓고 아래쪽을 놓쳤다. 고치는 자리마다 **같은 용어가 그 페이지 안에 또 있는지** 봐야 한다.
2. **"1분 4초"는 지켜보기 시작한 시점부터 잰 값이었다.** 로그의 `from this watcher start` 를 그대로 "실행 시간"으로 적었다. 측정값을 쓸 때는 **무엇을 기준으로 쟀는지**를 함께 적는다. 리뷰어가 원로그에서 63초로 다시 계산해 확인했다.
3. **`!!! tip` 이 코드블록으로 렌더되고 있었다.** 목록이 아닌 줄 아래에 4칸 들여쓰기로 넣어서다. `mkdocs build --strict` 는 이것을 잡지 못한다. admonition 을 넣은 뒤에는 **빌드된 HTML에 `<pre><code>!!! ` 가 없는지** 확인한다.

**리뷰어 지적을 하나 받아들이지 않았다.** "`policy는 JSON 문서입니다` 의 JSON이 미해설"이라는 판정이다. 이 워크샵의 전제에 "CloudFormation으로 스택을 배포해 본 경험"이 들어 있어 과하다고 보고 근거를 달아 되물었고, 재리뷰에서 **"직전 지적은 과했다"고 동의**했다. 리뷰 결과를 그대로 다 받지 않고 근거를 붙여 되묻는 것이 유효하다.

**L200 축은 따로 돌릴 값이 있었다.** Standards·Spec 두 축은 끝까지 한 번도 짚지 못한 것을 15건 찾았다. 예를 들어 `association` 과 `propagation` 은 저장소 어디에도 설명이 없었고, `show bgp summary` 에는 나오지도 않는 `Established` 를 확인하라고 적고 있었다. **독자 수준을 명시적으로 준 것**(전제해도 되는 것 / 안 되는 것 목록)이 이 축이 작동한 이유다.

## 16. 3차 리허설 계획 (2026-11-16 저녁 예정)

### 16-1. 왜 한 번 더 하나

1·2차는 **둘 다 자동화와 CLI로** 돌렸다. 그래서 지금도 비어 있는 것이 셋이다.

| 비어 있는 것 | 자동화로 낼 수 없는 이유 |
|---|---|
| 묶음별 시간 배분(2-2를 22분에 끝내는가) | 사람이 페이지를 읽고 따라가는 속도여야 한다 |
| 참가자 1명당 실제 청구액 | 실제 청구 내역을 봐야 한다 |
| 고친 단계가 실제로 통하는가 | 브라우저에서 눌러 봐야 한다 |

**세 번째가 이번의 핵심이다.** 2026-11-16에 고친 것 중 상당수는 리허설 로그와 스크린샷을 근거로 고쳤을 뿐, **다시 걸어 보지 않았다.** 특히 다음은 참가자가 막히는 자리라 직접 확인해야 한다.

- `Delete stack` 버튼과 **스택 이름 입력**을 요구하는 확인 창 (3-4-d, 3-4-e)
- EC2 접속 화면에서 **두 번째 카드**(EC2 Instance Connect Endpoint)를 고르는 것. 첫 카드가 기본이라 버튼이 잠긴다 (2-2-b, 2-3-c, 2-3-e)
- Edge location 드롭다운의 표기 **United States (Oregon)** (2-2-d)
- 제출 버튼 **Create attachment** (2-2-d, 2-3-b)
- 단계 번호가 1로 되돌아가던 6곳이 정말 1·2·3으로 보이는지 (2-2-b, 2-3-c, 2-4-a, 2-4-d, 3-1-d, 3-1-f)

### 16-2. 이번에는 방식이 달라야 한다

**사람이 공개된 페이지를 순서대로 따라간다.** 자동화를 쓰면 1·2차와 같은 사각지대가 또 생긴다. 집필자가 아니라 **참가자처럼** 읽어야 하므로, 막히면 그 자리를 적고 넘어간다(미리 아는 것으로 메꾸지 않는다).

기록할 것: 묶음마다 시작·끝 시각, 막힌 자리와 이유, 페이지와 화면이 다른 곳.

### 16-3. 계정

`demo1`(ap-northeast-2 / us-west-2). **재사용 가능하다.** 2026-11-16에 확인한 상태는 다음과 같다.

```text
스택 0 / 기본 아닌 VPC 0 / EC2 0 / VPN 연결 0 / customer gateway 0 / EIP 0 / EICE 0
global network 0 / core network 0        (리전 무관, us-west-2 에서 조회)
```

시작 전에 같은 확인을 다시 한다. Cloud WAN 리소스가 0이어야 global network 한도(계정당 5개)에 걸리지 않는다. `network-manager` 는 Service Quotas 에 서비스 코드가 없으므로 쿼터 API 로는 조회되지 않는다. 사용량 0을 직접 확인하는 것으로 갈음한다.

### 16-4. 미리 해 둘 것

core network 생성에 **15분쯤** 걸리므로, 사람이 시작하기 전에 서울·오레곤 스택을 배포해 두면 기다리지 않아도 된다. 실제 워크숍도 이론 강의 전에 배포하는 구성이라 진행 방식과도 맞는다. 다만 **2-1(로그인·배포)을 사람이 직접 해 보는 것이 목적이라면 미리 배포하면 안 된다.** 둘 중 무엇을 볼지 먼저 정한다.

### 16-5. 요금과 정리

core network edge 는 리전당 시간당 $0.50 이고 2개 리전이다. attachment·EC2·VPN 을 더해 2시간 30분 기준 **$5~8** 로 본다. 끝나면 [3-4](docs/extra-d.md) 순서대로 지우고 16-3 의 확인 명령을 다시 돌려 **잔재 0** 을 확인한다. 이번에는 **실제 청구 내역**도 확인해 `1-2-e` 의 추정치와 대조한다.
