# 2-2. 세그먼트와 글로벌 연결 (22분)

이 실습에서는 core network 안의 세그먼트가 서로를 어떻게 막고 여는지 확인하고, 오레곤 리전의 VPC를 core network에 연결해 서울과 통신합니다.

아래 그림 1의 번호 순서로 진행합니다. 처음 보는 용어는 [1-3. 용어 풀이](glossary.md)를 보세요.

<!-- alt-pending: lab1-global -->
<figure markdown="span">
  ![실습 2-2 구성: 서울 리전의 core network edge에 prod, dev, shared 세그먼트의 VPC 3개가 연결되어 있다. 서울 prod EC2(10.10.1.10)가 dev EC2(10.20.1.10)로 보내는 ping은 세그먼트가 달라 실패하고(번호 1), shared EC2(10.30.1.10)로 보내는 ping은 shared 세그먼트가 prod에 공유되어 성공한다(번호 2). 오레곤 리전에는 참가자가 segment=prod 태그를 붙여 만든 VPC attachment(번호 3)가 있고, attachment policy가 태그를 보고 이 연결을 prod 세그먼트에 배정한다(번호 4). 서울 prod EC2에서 오레곤 prod EC2(10.11.1.10)로 보내는 ping은 두 edge 사이 연결을 거쳐 성공한다(번호 5)](images/diagrams/lab1-global.png)
  <figcaption>그림 1. 실습 2-2에서 하는 일</figcaption>
</figure>

| 번호 | 단계 | 내용 |
|---|---|---|
| ① | prod → dev 실패 | 서울 prod EC2에서 dev EC2로 ping을 보냅니다. 세그먼트가 달라 실패하는 것이 맞습니다. |
| ② | prod → shared 성공 | 서울 prod EC2에서 shared EC2로 ping을 보냅니다. 정책의 `share` 덕분에 성공합니다. |
| ③ | 오레곤 attachment 생성과 태그 | 오레곤 VPC를 core network에 연결하고 태그 `segment` = `prod` 를 붙입니다. |
| ④ | attachment policy가 세그먼트에 배정 | 참가자가 세그먼트를 고르지 않습니다. 정책이 태그를 읽고 `prod` 세그먼트에 배정합니다. |
| ⑤ | 서울 prod → 오레곤 prod 성공 | 서울 prod EC2에서 오레곤 prod EC2로 ping을 보냅니다. 두 edge 사이 연결은 이미 있습니다. |

시작하기 전에 확인합니다.

- 실습 2-1에서 서울 스택과 오레곤 스택이 모두 **CREATE_COMPLETE**인가요?
- core network의 **Policy versions** 탭에서 정책이 `LIVE`이고, Change set state가 `Execution succeeded`인가요? 아직이면 2-2-a만 먼저 하고 기다립니다.

## 2-2-a. core network 둘러보기 { #lab1-a }

먼저 스택이 만든 core network를 눈으로 봅니다. 여기서는 아무것도 바꾸지 않습니다.

1. 콘솔 오른쪽 위에서 리전이 **Asia Pacific (Seoul)** 인지 확인합니다.
2. **Network Manager** 콘솔 → **Core networks**에서 스택이 만든 core network를 엽니다.
3. **Segments** 탭에서 세그먼트를 확인합니다. `prod`, `dev`, `shared`, `onprem` 4개가 보입니다.
4. **Attachments** 탭에서 서울 연결을 확인합니다. VPC attachment 3개(prod, dev, shared)가 보입니다.
5. 연결을 하나씩 열어 **Tags**에서 `segment` 태그를 봅니다. 연결 이름은 `cwan-ws-attach-prod`, `cwan-ws-attach-dev`, `cwan-ws-attach-shared` 입니다.

<!-- shot: lab1-core-01-segments -->
<!-- shot: lab1-core-02-attachments -->
<!-- shot: lab1-core-03-attachment-tags -->

세그먼트는 core network 안의 가상 라우팅 구역입니다. 같은 세그먼트에 있는 연결끼리만 통신하는 것이 기본 동작입니다.

**성공 확인**: 세그먼트 4개와 서울 연결 3개가 보이고, 각 연결의 `segment` 태그 값이 연결 이름(`prod`, `dev`, `shared`)과 같습니다.

## 2-2-b. 운영에서 개발로 통신해 보기 { #lab1-b }

그림 1의 ①입니다. 서울 prod EC2에서 서울 dev EC2로 ping을 보냅니다.

EC2에는 인터넷 주소가 없습니다. 그래서 스택이 만든 EC2 Instance Connect Endpoint로 브라우저에서 접속합니다.

1. **EC2** 콘솔 → **Instances**에서 서울 리전의 `cwan-ws-prod-ec2`를 고르고 **Connect**를 누릅니다.
2. **In web browser** 탭에서 **EC2 Instance Connect Endpoint**를 고릅니다. 엔드포인트와 사용자 이름은 자동으로 채워집니다.
3. **Connect**를 누르면 터미널이 열립니다.

<!-- shot: lab1-eic-01-connect -->

!!! tip "브라우저 탭을 두 개 열어 두세요"
    이 실습은 EC2 터미널과 Network Manager 콘솔을 번갈아 씁니다. VPC 콘솔과 Network Manager는 새 탭에 따로 열어 두면 터미널을 닫지 않고 오갈 수 있습니다.

서울 prod EC2 터미널에서 실행합니다.

```bash
ping -c 5 10.20.1.10
```

**결과(실패가 맞습니다)**: `100% packet loss`가 나옵니다.

<!-- shot: lab1-ping-01-prod-to-dev -->

보안 그룹은 열려 있습니다. dev EC2의 보안 그룹은 `10.0.0.0/8`에서 오는 ICMP(Internet Control Message Protocol, ping에 쓰는 프로토콜)를 허용하고, prod EC2의 주소 `10.10.1.10`도 이 대역 안에 있습니다. 그런데도 막힌 이유는 보안 그룹이 아니라 **Cloud WAN 세그먼트**입니다. `prod`와 `dev`는 서로 다른 세그먼트이고, 둘 사이에 `share`가 없으면 서로의 경로를 배우지 못합니다. 막으려고 따로 설정한 것이 없다는 점이 이 워크숍의 핵심입니다.

**성공 확인**: `100% packet loss`가 나옵니다. 응답이 오면 안 됩니다.

## 2-2-c. 운영에서 공유 서비스로 통신해 보기 { #lab1-c }

그림 1의 ②입니다. 같은 서울 prod EC2 터미널을 그대로 씁니다. 끊겼으면 2-2-b처럼 다시 **Connect**를 누릅니다.

서울 prod EC2 터미널에서 실행합니다.

```bash
ping -c 5 10.30.1.10
```

<!-- shot: lab1-ping-02-prod-to-shared -->

**결과**: 응답이 옵니다.

이것은 core network policy의 `share` 때문입니다. 정책의 `segment-actions`에 다음 부분이 들어 있습니다.

```json
{
  "action": "share",
  "mode": "attachment-route",
  "segment": "shared",
  "share-with": ["prod", "dev", "onprem"]
}
```

`shared` 세그먼트의 경로를 `prod`, `dev`, `onprem` 세그먼트에 공유한다는 뜻입니다. 그래서 세 세그먼트는 `shared`에 닿습니다. 하지만 `prod`와 `dev`는 서로 공유하지 않으므로 여전히 닿지 않습니다. 공유 서비스 패턴은 이 비대칭을 이용합니다.

**성공 확인**: `0% packet loss`이고 5개 모두 응답합니다.

## 2-2-d. 오레곤 연결 만들기 { #lab1-d }

그림 1의 ③과 ④입니다. 오레곤 prod VPC를 core network에 연결합니다. 오레곤 스택은 VPC와 EC2만 만들었고 attachment는 만들지 않았습니다.

!!! warning "attachment 생성에 걸리는 시간"
    attachment가 `Available`이 되기까지 걸리는 시간은 사전 테스트에서 측정합니다. 생성하는 동안 다음 소절의 준비를 합니다.

1. 콘솔 오른쪽 위에서 리전을 **US West (Oregon)** 으로 바꿉니다.
2. **Network Manager** 콘솔 → **Core networks**에서 같은 core network를 엽니다.
3. **Attachments** 탭에서 VPC attachment를 만드는 버튼(**Create attachment**)을 누르고, 종류로 **VPC**를 고릅니다.
4. 아래 값을 넣습니다.

    | 항목 | 값 |
    |---|---|
    | Core network | 서울에서 본 core network |
    | Edge location | `us-west-2` |
    | VPC | 오레곤 스택 **Outputs**의 `VpcId`에 있는 VPC (`cwan-ws-prod-vpc`) |
    | Subnets | 오레곤 스택 **Outputs**의 `CwanSubnetAId`, `CwanSubnetBId` 두 개 (`cwan-ws-prod-cwan-az1`, `cwan-ws-prod-cwan-az2`) |

5. **Tags**에 아래 태그를 추가합니다.

    | Key | Value |
    |---|---|
    | `segment` | `prod` |

6. 만들기 버튼을 누릅니다.

<!-- shot: lab1-attach-01-create -->
<!-- shot: lab1-attach-02-subnets -->
<!-- shot: lab1-attach-03-tags -->

서브넷은 앱 서브넷이 아니라 attachment 전용 서브넷(`/28`) 2개를 고릅니다. Cloud WAN이 이 서브넷에 네트워크 인터페이스를 만들어 VPC와 core network를 잇습니다.

**참가자는 세그먼트를 고르지 않습니다.** 만드는 화면에 세그먼트를 직접 고르는 칸은 없습니다. 대신 core network policy의 attachment policy가 세그먼트를 정합니다. 정책에는 이런 규칙이 들어 있습니다.

```json
{
  "rule-number": 100,
  "description": "segment 태그 값에 따라 세그먼트에 배정",
  "conditions": [{ "type": "tag-exists", "key": "segment" }],
  "action": { "association-method": "tag", "tag-value-of-key": "segment" }
}
```

`tag-exists` 조건은 `segment` 태그가 있는지 봅니다. 있으면 그 태그의 값(`prod`)과 이름이 같은 세그먼트에 연결을 배정합니다. 그래서 태그 값을 `prod`로 넣었는지가 중요합니다. 대소문자도 같아야 합니다.

attachment 상태가 `Available`이 되면 상세 화면에서 **Segment**가 `prod`인지 확인합니다.

<!-- shot: lab1-attach-04-available -->

**성공 확인**: attachment 상태가 `Available`이고 **Segment**가 `prod`입니다. 직접 고르지 않았는데 `prod`에 들어갔습니다.

## 2-2-e. 오레곤 VPC에 경로 넣기 { #lab1-e }

!!! info "연결을 붙이는 것과 VPC 라우트를 넣는 것은 다른 일입니다"
    attachment는 VPC와 core network 사이에 길을 놓습니다. 하지만 VPC 안의 서브넷이 그 길로 트래픽을 보내려면, 서브넷의 라우트 테이블에 "이 대역은 core network로 보내라"는 경로가 따로 있어야 합니다. 경로가 없으면 attachment가 `Available`이어도 트래픽은 core network에 닿지 않습니다.

오레곤 앱 서브넷의 라우트 테이블에 경로 2개를 넣습니다. 리전은 **US West (Oregon)** 그대로입니다.

1. **CloudFormation** 콘솔에서 오레곤 스택 `cloudwan-workshop-oregon`의 **Outputs** 탭을 열고 `AppRouteTableId` 값을 확인합니다.
2. **VPC** 콘솔 → **Route tables**에서 그 ID의 라우트 테이블(`cwan-ws-prod-app`)을 엽니다.
3. **Routes** 탭 → **Edit routes** → **Add route**를 누릅니다.
4. 아래 두 경로를 넣습니다. 대상(**Target**)은 종류로 **Core Network**를 고르고 core network를 고릅니다.

    | Destination | Target |
    |---|---|
    | `10.0.0.0/8` | core network |
    | `172.16.0.0/12` | core network |

5. **Save changes**를 누릅니다.

<!-- shot: lab1-route-01-outputs -->
<!-- shot: lab1-route-02-edit -->
<!-- shot: lab1-route-03-saved -->

`10.0.0.0/8`은 서울의 `10.x` 대역 전체를, `172.16.0.0/12`는 온프레미스 대역(`172.16.1.0/24`)을 덮습니다. 온프레미스는 실습 2-3에서 연결합니다. 지금 미리 넣어 두면 2-3에서 오레곤 쪽을 다시 고칠 일이 없습니다.

**성공 확인**: **Routes** 탭에 두 경로가 보이고 **Status**가 `Active`입니다.

## 2-2-f. 리전을 넘어 통신해 보기 { #lab1-f }

그림 1의 ⑤입니다. 서울 prod EC2에서 오레곤 prod EC2로 ping을 보냅니다.

서울 prod EC2 터미널에서 실행합니다. 리전을 **Asia Pacific (Seoul)** 로 되돌리고 `cwan-ws-prod-ec2`에 **Connect**합니다. 열려 있는 터미널이 있으면 그대로 씁니다.

```bash
ping -c 5 10.11.1.10
```

<!-- shot: lab1-ping-03-seoul-to-oregon -->

**결과**: 응답이 옵니다.

서울과 오레곤 edge 사이의 연결, 그리고 경로를 서로 알려 주는 일은 참가자가 설정하지 않았습니다. 두 리전의 `prod` 연결이 같은 세그먼트에 있으면 Cloud WAN이 edge 사이를 이어 경로를 전파합니다. 정책에 서울과 오레곤 edge를 모두 적어 두었기 때문입니다. 참가자가 한 일은 attachment에 태그를 붙인 것과 VPC 라우트 2개를 넣은 것뿐입니다.

이제 경로가 실제로 전파됐는지 봅니다.

1. 리전이 **Asia Pacific (Seoul)** 인지 확인합니다.
2. **Network Manager** 콘솔 → **Core networks**에서 core network를 열고 **Routes**(세그먼트 경로 테이블)를 엽니다.
3. 세그먼트 `prod`, edge `ap-northeast-2`를 고릅니다.
4. 목적지 `10.11.1.0/24`가 보이는지 확인합니다.

<!-- shot: lab1-routes-01-segment-table -->

`10.11.1.0/24`가 오레곤 attachment를 가리키는 경로로 `prod` 세그먼트의 서울 edge에 있습니다. 서울 prod의 `10.10.1.0/24`도 함께 보입니다. `dev`를 고르면 `10.11.1.0/24`가 보이지 않습니다.

**성공 확인**: ping이 `0% packet loss`이고, `prod` 세그먼트 경로 테이블에 `10.11.1.0/24`가 보입니다.

## 2-2-g. 정리 { #lab1-g }

| 확인한 것 | 결과 |
|---|---|
| 서울 prod → dev | 실패. 보안 그룹이 아니라 세그먼트가 막았습니다 |
| 서울 prod → shared | 성공. `share`로 경로가 공유됩니다 |
| 오레곤 attachment | `segment` = `prod` 태그만 붙이면 attachment policy가 `prod`에 배정합니다 |
| 오레곤 VPC 라우트 | 연결을 붙인 것과 별개로, 서브넷 라우트 테이블에 직접 넣어야 합니다 |
| 서울 prod → 오레곤 prod | 성공. edge 사이 연결과 경로 전파는 Cloud WAN이 합니다 |

세그먼트로 통신 범위를 정하고, 태그로 연결을 배정하며, 리전을 넘는 경로는 정책이 알아서 전파합니다. 리전이 늘어도 정책 하나로 관리한다는 뜻입니다.

다음은 [2-3. 온프레미스 연결](lab2.md)입니다.
