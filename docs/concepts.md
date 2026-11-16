# 4-1. core network policy 읽는 법

AWS Cloud WAN에서 여러분이 다루는 것은 사실상 **core network policy** 문서 하나입니다. 세그먼트를 몇 개 둘지, 어느 리전에 core network edge를 둘지, 어떤 연결(attachment)이 어느 세그먼트에 들어갈지, 어느 세그먼트끼리 통신할지를 모두 이 JSON 한 개가 정합니다. 콘솔에서 버튼을 눌러 바꾸더라도 결국 바뀌는 것은 이 JSON입니다.

이 페이지는 실습에서 쓴 정책([2-1](lab0.md)의 CloudFormation 스택이 넣어 둔 정책)을 예로 들어 필드를 하나씩 풀어 설명합니다. 이 페이지를 읽고 나면 처음 보는 정책 JSON도 혼자 읽을 수 있습니다.

실습에서 쓴 정책은 다음과 같습니다. 아래 소절에서 이 JSON을 계속 참조합니다.

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

## 4-1-a. 정책의 뼈대 { #skeleton }

정책 JSON은 최상위 키 몇 개로 나뉩니다. 이 워크숍에서 쓰는 것은 다음 다섯 덩어리입니다.

| 키 | 필수 | 무엇을 정하나 |
|---|---|---|
| `version` | 예 | 정책 문서의 형식 버전입니다. `2021.12` 또는 `2025.11`을 고릅니다 |
| `core-network-configuration` | 예 | core network가 동작할 리전(core network edge)과 ASN(Autonomous System Number, 자율 시스템 번호), 그리고 DNS·ECMP 같은 전역 설정을 정합니다 |
| `segments` | 예 | 세그먼트(격리된 라우팅 도메인)의 목록과 각 세그먼트의 성격을 정합니다 |
| `segment-actions` | 아니요 | 세그먼트 **사이**의 라우팅을 정합니다. 공유(`share`)와 정적 경로(`create-route`)가 여기 들어갑니다 |
| `attachment-policies` | 아니요 | 연결이 **어느 세그먼트에 들어갈지**를 규칙으로 정합니다 |

읽는 순서를 정해 두면 편합니다. 먼저 `core-network-configuration`에서 "어느 리전에 있는 네트워크인가"를 보고, `segments`에서 "방이 몇 개인가"를 보고, `segment-actions`에서 "방 사이에 문이 있는가"를 보고, 마지막으로 `attachment-policies`에서 "내 연결은 어느 방에 들어가는가"를 봅니다.

`version`은 문서 형식의 버전이면서 쓸 수 있는 기능도 함께 정합니다. `2025.11`은 라우팅 정책(routing policy)과 BGP(Border Gateway Protocol) 커뮤니티 전파를 쓸 때 필요합니다. 이 워크숍은 그 기능을 쓰지 않으므로 `2021.12`로 충분합니다.

!!! info "이 페이지에서 다루지 않는 섹션"
    공식 JSON 레퍼런스에는 `network-function-groups`, `routing-policies`, `attachment-routing-policy-rules` 섹션도 있습니다. 방화벽 같은 장비를 거쳐 가게 하거나(서비스 삽입) 경로를 더 정교하게 고르는 데 쓰며, 이 워크숍의 범위 밖입니다.

출처: [Core network policies — JSON policy document](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policies-json.html)

## 4-1-b. core-network-configuration { #config }

core network가 **어디에 생길지**를 정하는 덩어리입니다. 여기에 적은 리전마다 core network edge가 하나씩 생기고, 각 edge는 여기 적힌 다른 모든 edge와 자동으로 peering됩니다. 실습에서 서울 운영 EC2와 오레곤 운영 EC2가 통신한 것([2-2-f](lab1.md#lab1-f))은 이 자동 peering 덕분입니다.

| 필드 | 필수 | 내용 |
|---|---|---|
| `asn-ranges` | 예 | core network edge에 배정할 ASN의 범위입니다. 쓸 수 있는 범위는 `64512-65534`와 `4200000000-4294967294`뿐입니다 |
| `edge-locations` | 예 | edge를 만들 리전 목록입니다. 항목마다 `location`(리전 코드)과 선택 항목 `asn`을 적습니다 |
| `vpn-ecmp-support` | 아니요 | 여러 VPN 연결에 트래픽을 나눠 보내는 ECMP(Equal-Cost Multi-Path)를 켭니다. 기본값은 `true`입니다 |
| `dns-support` | 아니요 | 연결된 VPC 사이에서 도메인 이름을 풀 수 있게 합니다. 기본값은 `true`입니다 |
| `security-group-referencing-support` | 아니요 | 한 VPC의 보안 그룹이 다른 VPC의 보안 그룹을 참조할 수 있게 합니다. 기본값은 `false`입니다 |
| `inside-cidr-blocks` | 아니요 | **Connect attachment**(AWS 밖의 네트워크 장비를 Cloud WAN에 잇는 연결)에 줄 주소 대역입니다. 이 워크숍에서는 쓰지 않으므로 비워 두었습니다([아래](#inside-cidr)에서 자세히) |

실습 정책에서는 `asn-ranges`를 `64512-64520`으로 주고, 서울 edge에 `64512`, 오레곤 edge에 `64513`을 직접 지정했습니다. `asn`을 생략하면 범위 안에서 자동으로 배정됩니다.

!!! warning "edge ASN은 만든 뒤 바꿀 수 없습니다"
    공식 문서는 "You can't change the ASN of a core network edge."라고 적습니다. 그래서 워크숍 템플릿은 리전별 ASN을 정책에 명시해 둡니다. 또 같은 ASN을 쓰는 Transit Gateway는 그 edge와 peering할 수 없으므로, 나중에 Transit Gateway를 붙일 계획이 있다면 ASN을 처음에 신중히 정하세요.

!!! info "ASN 범위는 끝 값을 포함하지 않습니다"
    콘솔 설명에 따르면 ASN 범위는 왼쪽은 포함하고 오른쪽은 제외합니다. 예를 들어 `64900-64903`은 `64900`~`64902`입니다. 실습의 `64512-64520`은 `64512`~`64519`를 뜻합니다.

#### `inside-cidr-blocks` { #inside-cidr }

**이 워크숍은 Connect attachment를 쓰지 않으므로 이 필드를 비워 두었습니다.** 읽고 넘어가도 됩니다.

**Connect attachment** 는 AWS 밖에 있는 네트워크 장비(여러 거점을 소프트웨어로 묶어 주는 SD-WAN 장비 같은 것)를 Cloud WAN에 잇는 연결 방식이고, **GRE**(Generic Routing Encapsulation)는 이미 있는 연결 위에 패킷을 한 번 더 감싸 보내는 터널 방식입니다. `inside-cidr-blocks` 는 그 GRE 터널의 양 끝에 줄 주소를 떼어 오는 **주소 풀**입니다.

!!! info "용어집의 **inside CIDR block** 과 이름만 비슷합니다"
    [용어집](glossary.md)의 `inside CIDR block`(`169.254.x.x/30`)은 **Site-to-Site VPN 터널 하나가 BGP 대화에 쓰는 주소**입니다. 여기 `inside-cidr-blocks` 는 **Connect attachment에 떼어 줄 주소 풀**이고 크기도 훨씬 큽니다. 쓰이는 곳이 다릅니다.

??? info "Connect attachment를 쓰게 될 때 알아야 할 것 (실습에는 필요 없습니다)"
    공식 문서는 "an Inside CIDR block is required for attaching Connect attachments to a Core Network Edge"라고 적습니다. 최소 크기는 IPv4 `/24`, IPv6 `/64`입니다. 큰 범위를 적어 두면 새 edge가 생길 때마다 `/24`와 `/64`를 자동으로 떼어 갑니다. 한 번 edge에 배정된 inside CIDR은 지울 수 없고, 큰 범위에 남은 공간이 없으면 정책 예외(policy exception)가 납니다.

리전은 그 리전에 걸린 연결을 모두 지우기 전에는 `edge-locations`에서 뺄 수 없습니다.

출처: [JSON policy document](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policies-json.html), [Core network configuration](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-core-network-config.html)

## 4-1-c. segments { #segments }

세그먼트는 **완전히 분리된 라우팅 도메인**입니다. 공식 문서는 세그먼트마다 별도의 라우팅 도메인이고, 기본적으로 한 연결은 **같은 세그먼트의 연결하고만** 통신한다고 적습니다. 실습 [2-2-b](lab1.md#lab1-b)에서 서울 운영 EC2가 서울 개발 EC2에 ping이 안 된 것은 고장이 아니라 이 기본 동작입니다. `prod`와 `dev` 사이를 막으려고 따로 적은 것이 하나도 없다는 점을 정책 JSON에서 직접 확인해 보세요.

| 필드 | 필수 | 내용 |
|---|---|---|
| `name` | 예 | 세그먼트 이름입니다. 쓸 수 있는 문자는 영문자와 숫자(`a`–`z`, `A`–`Z`, `0`–`9`)뿐이라 공백은 넣을 수 없습니다 |
| `description` | 아니요 | 설명입니다. 통신에는 영향이 없습니다 |
| `edge-locations` | 아니요 | 이 세그먼트가 존재할 리전을 더 좁힙니다. `core-network-configuration`의 `edge-locations`의 부분집합이어야 합니다 |
| `isolate-attachments` | 아니요 | 기본값 `false`입니다. `true`로 하면 같은 세그먼트 안의 연결끼리도 통신하지 못합니다 |
| `require-attachment-acceptance` | 아니요 | 기본값 `true`입니다. 연결이 세그먼트에 들어오기 전에 사람이 승인해야 합니다 |
| `allow-filter` / `deny-filter` | 아니요 | 이 세그먼트가 경로를 받아들일(또는 거부할) 상대 세그먼트 목록입니다 |

실습 정책은 네 세그먼트 모두 `require-attachment-acceptance`를 `false`로 두었습니다. 기본값이 `true`라서 그대로 두면 참가자가 연결을 만들 때마다 **Accept** 버튼을 한 번 더 눌러야 하고, 실습 시간이 그만큼 길어집니다. 승인 동작은 추가 과제 [3-1](extra-a.md)에서 따로 다룹니다.

!!! warning "`require-attachment-acceptance: false`의 뒷면"
    공식 문서는 이 값이 `false`이면 **태그가 바뀌는 것만으로** 연결이 세그먼트에 들어오거나 빠질 수 있다고 적습니다. 운영 환경에서 그것을 원하지 않으면 `true`로 두세요.

`isolate-attachments`를 `true`로 하면 그 세그먼트의 연결은 `share`로 받은 경로와 정적 경로만 쓸 수 있습니다. 지사 수백 개가 본사하고만 통신해야 하는 구성에 씁니다.

`allow-filter`와 `deny-filter`는 **함께 쓸 수 없습니다**. 공식 문서는 "You can use either allow-filter or deny-filter, but you can't use both of them simultaneously."라고 적습니다. 두 필터는 `segment-actions`의 `share`가 적용된 **뒤에** 적용되므로, 공유로 열린 것을 다시 좁히는 데 씁니다.

세그먼트에는 ARN(Amazon Resource Name)이나 ID가 없습니다. 이름이 곧 식별자입니다. 그래서 `attachment-policies`에서 태그 값으로 세그먼트를 고를 수 있습니다.

출처: [JSON policy document](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policies-json.html)

## 4-1-d. segment-actions { #actions }

세그먼트 사이에 문을 내는 덩어리입니다. 실습에서 쓰는 것은 `share`이고, 정적 경로가 필요할 때 `create-route`를 씁니다.

### share

```json
{
  "action": "share",
  "mode": "attachment-route",
  "segment": "shared",
  "share-with": ["prod", "dev", "onprem"]
}
```

| 필드 | 내용 |
|---|---|
| `mode` | `attachment-route`만 지원합니다. 공식 문서도 "attachment-route is the only supported value"라고 적습니다 |
| `segment` | 경로를 나눠 주는 쪽 세그먼트입니다 |
| `share-with` | 받는 쪽 세그먼트 이름 배열이거나 `"*"`(모든 세그먼트)입니다. `{"except": ["dev"]}` 처럼 제외할 세그먼트를 적는 형태도 됩니다 |

**공유는 기본적으로 양방향입니다.** 두 세그먼트 사이에 `share`를 만들면 양쪽 경로가 서로에게 광고됩니다(공식 문서의 표현은 "create mutual advertisements"입니다). 단방향으로 만들려면 받는 쪽 세그먼트에 deny filter를 씁니다.

**그런데 `share-with` 배열에 함께 적힌 세그먼트끼리는 서로 공유되지 않습니다.** 실습 정책을 이 규칙으로 읽어 보세요.

| 쌍 | 통신 | 이유 |
|---|---|---|
| `shared` ↔ `prod` | 가능 | `share`로 양방향 |
| `shared` ↔ `dev` | 가능 | `share`로 양방향 |
| `shared` ↔ `onprem` | 가능 | `share`로 양방향 |
| `prod` ↔ `dev` | 불가 | 둘 다 `shared`와만 공유되고 서로는 아님 |
| `prod` ↔ `onprem` | 불가 | 같은 이유 ([2-3-f](lab2.md#lab2-f)에서 확인합니다) |
| `dev` ↔ `onprem` | 불가 | 같은 이유 |

이 비대칭이 공유 서비스 패턴의 핵심입니다. 로그·인증·모니터링은 모두에게 열어 주면서, 운영과 개발과 온프레미스는 서로 못 보게 하는 것을 `share` 한 덩어리로 끝냅니다. 실습 [2-4](lab3.md)에서는 여기에 `onprem` → `prod` 공유를 한 덩어리 더 넣어 온프레미스와 운영 사이만 엽니다. `dev`는 그대로 막혀 있습니다.

### create-route

정적 경로를 세그먼트에 심습니다.

| 필드 | 내용 |
|---|---|
| `segment` | 경로를 심을 세그먼트입니다(필수) |
| `destination-cidr-blocks` | 목적지 대역 배열입니다. IPv4와 IPv6 모두 됩니다(필수) |
| `destinations` | 그 대역으로 가는 트래픽을 보낼 연결 목록입니다. 리전당 `attachment-id`는 최대 1개입니다 |

`destinations`에 연결 ID 대신 `blackhole`을 적으면 그 대역으로 가는 트래픽을 모두 버립니다. 특정 대역을 확실히 막고 싶을 때 씁니다. Cloud WAN은 blackhole 경로를 다른 곳에 전파하지 않습니다. 같은 정적 경로를 여러 세그먼트에 심으려면 `create-route`를 세그먼트마다 하나씩 씁니다.

!!! info "`segment-actions`의 다른 액션"
    이 섹션에는 `send-via`, `send-to`, `associate-routing-policy` 액션도 있습니다. 트래픽을 방화벽 같은 장비로 보내거나 라우팅 정책을 붙일 때 쓰며, 이 워크숍에서는 다루지 않습니다.

출처: [JSON policy document](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policies-json.html), [Creating a core network policy version](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-create-policy-version.html), [Shared services 예시](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policy-examples.html)

## 4-1-e. attachment-policies { #attachment }

연결이 **어느 세그먼트에 들어갈지**를 정하는 규칙 목록입니다. 방화벽 규칙처럼 위에서부터 차례로 맞춰 봅니다.

| 필드 | 내용 |
|---|---|
| `rule-number` | 1~65535의 정수입니다. **낮은 번호부터** 처리하고, 맞는 규칙이 나오면 그 동작을 하고 **멈춥니다** |
| `description` | 설명입니다 |
| `conditions` | 이 규칙이 맞는지 판단하는 조건 목록입니다 |
| `condition-logic` | 조건이 **2개 이상이면 필수**입니다. `and` 또는 `or`입니다 |
| `action` | 맞았을 때 할 일입니다 |

공식 문서의 문장은 "When a match is made, the action is taken and no further rules are processed."입니다. 그러니 좁은 규칙을 낮은 번호에, 넓은 규칙을 높은 번호에 두세요.

### conditions

| `type` | 보는 것 |
|---|---|
| `any` | 항상 맞습니다. 가장 높은 번호에 두어 기본 세그먼트(fallback)로 씁니다 |
| `resource-id` | 연결 대상 리소스의 ID(VPC ID, VPN 연결 ID 등) |
| `region` | 연결이 붙는 리전 |
| `attachment-type` | 연결의 종류. 값은 `vpc`, `site-to-site-vpn`, `connect`, `transit-gateway-route-table` |
| `account` | 연결을 요청한 AWS 계정 ID |
| `tag-value` | 특정 태그 키의 **값** |
| `tag-name` | 특정 태그 키가 **있는지** (값은 보지 않습니다) |

`operator`는 `equals`, `not-equals`, `contains`, `begins-with` 중 하나입니다. `resource-id`, `region`, `attachment-type`, `account`, `tag-value`에 씁니다. 태그 이름의 존재만 보는 조건에는 `operator`가 필요 없습니다.

!!! warning "`tag-exists`와 `tag-name`"
    공식 JSON 레퍼런스의 `type` 목록에는 `tag-name`이 있고 `tag-exists`는 없습니다. 그런데 같은 문서의 정책 예시와 [3단계 환경 예시](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policy-examples-three-stage.html)에는 `tag-exists`가 쓰입니다. 두 이름은 "그 태그 키가 붙어 있는가"라는 같은 뜻입니다. 정책이 거부되면 다른 이름으로 바꿔 보세요.

### action

| 필드 | 내용 |
|---|---|
| `association-method` | `constant`이면 `segment`에 적은 세그먼트로 고정합니다. `tag`이면 태그 값을 세그먼트 이름으로 씁니다 |
| `segment` | `constant`일 때 쓸 세그먼트 이름 |
| `tag-value-of-key` | `tag`일 때 세그먼트 이름을 읽어 올 태그 키 |
| `require-acceptance` | `true`로만 설정할 수 있습니다. 세그먼트의 `require-attachment-acceptance`가 `false`여도 이 규칙에 걸린 연결만 승인을 요구합니다 |

### 실습 규칙 풀어 읽기

```json
{
  "rule-number": 100,
  "description": "Put an attachment in the segment named by its segment tag",
  "conditions": [{ "type": "tag-exists", "key": "segment" }],
  "action": { "association-method": "tag", "tag-value-of-key": "segment" }
}
```

이 규칙 하나를 말로 풀면 이렇습니다. **"연결에 `segment`라는 태그 키가 붙어 있으면, 그 태그의 값과 이름이 같은 세그먼트에 넣어라."**

그래서 실습에서 오레곤 VPC 연결을 만들 때 태그 `segment = prod`만 붙이면([2-2-d](lab1.md#lab1-d)) 그 연결이 `prod` 세그먼트에 들어갑니다. VPN 연결에 `segment = onprem`을 붙이면([2-3-b](lab2.md#lab2-b)) `onprem`에 들어갑니다. 세그먼트가 늘어도 정책은 그대로입니다. 세그먼트마다 규칙을 하나씩 쓰는 대신 규칙 한 개로 끝난 이유입니다.

이 방식에는 전제가 있습니다. **태그 값이 세그먼트 이름과 정확히 같아야 합니다.** 대소문자도 같아야 합니다. 그래서 이 워크숍은 세그먼트 이름을 모두 소문자(`prod`, `dev`, `shared`, `onprem`)로 통일했습니다.

!!! warning "어느 규칙에도 맞지 않으면"
    공식 문서는 "If no rules are matched ..., the attachment won't be associated to a segment."라고 적습니다. 연결은 만들어지지만 **어느 세그먼트에도 들어가지 않아** 아무 데도 통신하지 못합니다. 실습에서 태그를 빠뜨리고 연결을 만들면 정확히 이 상태가 됩니다. 연결이 **Available**인데 통신이 안 되면 세그먼트 배정부터 확인하세요([4-3. 문제 해결](troubleshooting.md)).

연결 하나는 세그먼트 하나에만 속할 수 있습니다.

출처: [JSON policy document](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policies-json.html), [Attachment policies](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policy-attachments.html)

## 4-1-f. 정책을 바꿀 때 { #change }

Cloud WAN에서 정책을 바꾸는 것은 파일을 저장하는 일이 아니라 **새 버전을 만들고 배포하는 일**입니다. 실습 [2-4](lab3.md)에서 직접 해 보는 흐름이 이렇습니다.

1. 정책 JSON을 고쳐 **새 policy version**을 만듭니다. 버전 번호는 최신 버전에서 1씩 올라갑니다.
2. Cloud WAN이 그 버전과 현재 적용 중인 정책을 비교해 **change set**(바뀌는 것 목록)을 만듭니다.
3. 사람이 change set을 보고 **Apply change set**을 눌러야 실제로 적용됩니다.
4. 적용이 끝나면 그 버전의 Alias가 `LIVE`가 되고, Change set state가 **Execution succeeded**가 됩니다.

!!! warning "배포는 자동이 아닙니다"
    공식 문서의 문장은 "Deploying a new policy version never occurs automatically."입니다. 버전을 만들어 두는 것만으로는 통신이 바뀌지 않습니다. 실습에서 새 버전을 만든 뒤에도 ping이 그대로 실패한다면, change set을 아직 실행하지 않은 것이 가장 흔한 원인입니다.

| 상태 | 뜻 |
|---|---|
| `LIVE` | 지금 적용 중인 정책입니다. 늘 하나뿐입니다 |
| `LATEST` | 번호가 가장 큰 버전입니다 |
| **Ready to execute** | change set이 만들어졌고 실행을 기다립니다. 이 상태의 버전은 여러 개일 수 있습니다 |
| **Execution succeeded** | 실행이 끝났습니다 |
| **Out of date** | 다른 버전이 먼저 적용되어 이 change set은 쓸 수 없게 되었습니다 |
| **Pending generation** / **Failed generation** | change set을 만드는 중이거나 만들기에 실패했습니다 |

**이전 버전으로 되돌릴 수 있습니다.** 공식 문서는 "You can also restore any out-of-date policy to become the new current version."이라고 적습니다. **Out of date** 상태의 버전을 골라 다시 현재 버전으로 만들면, 그 버전에 대해 change set이 새로 만들어지고 그것을 실행하는 방식입니다. 되돌리기도 결국 배포이므로 실행 단계가 필요합니다. 쓸 수 없게 된 change set은 기본 90일 동안 보관됩니다.

### 어느 정책 변경이 어느 edge에 작업을 일으키나

정책을 바꾸면 영향받는 core network edge가 갱신됩니다. 이 갱신에 시간이 걸리므로, 무엇을 바꾸면 어디까지 흔들리는지 알아 두면 변경 창을 잡기 쉽습니다.

| 바꾼 것 | 갱신되는 edge |
|---|---|
| `version` | 모든 edge |
| `vpn-ecmp-support`, `dns-support`, `security-group-referencing-support` | 모든 edge |
| `edge-locations` 추가·제거 | 모든 edge (다른 모든 edge와의 연결을 만들거나 끊어야 하므로) |
| `segments` 항목 추가·삭제 | 모든 edge. 그 세그먼트에 `edge-locations`가 적혀 있으면 그 리전들만 |
| `isolate-attachments`, `allow-filter`, `deny-filter` 변경 | 그 세그먼트가 있는 모든 edge |
| `share` 추가·삭제 | 관련된 세그먼트들의 모든 edge |
| `create-route` 추가·삭제 | `destinations`의 연결이 있는 리전들. blackhole이면 그 세그먼트의 모든 edge |
| `attachment-policies` 변경 | 연결이 새로 배정되거나 빠지는 리전 |
| `asn-ranges`, `inside-cidr-blocks` 변경 | 그 자체로는 어느 리전도 갱신하지 않습니다 |
| `description`, `require-attachment-acceptance` 변경 | **어느 edge도 갱신하지 않습니다** |

마지막 줄을 기억해 두면 좋습니다. 설명을 고치거나 승인 요구 여부만 바꾸는 변경은 네트워크에 작업을 일으키지 않습니다. 반대로 세그먼트를 하나 추가하는 것은 모든 리전의 edge를 건드립니다.

출처: [Deploying a policy version](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policy-version-deploy.html), [Creating a policy version](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-create-policy-version.html), [Regional scope of policy changes](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-policy-regional-scope.html)

## 4-1-g. 알아 둘 한도 { #quotas }

정책을 설계할 때 먼저 보는 숫자들입니다.

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

- **global network당 core network는 1개**이고 조정할 수 없습니다. core network를 둘 쓰려면 global network를 둘 만들어야 합니다. 계정당 global network가 5개이므로 임시 실습 계정을 재사용할 때는 이전 워크숍의 global network가 남아 있는지 먼저 확인하세요([1-2. 사전 준비](prerequisites.md)).
- **리전당 edge는 1개**입니다. 한 리전에 core network edge를 둘 둘 수 없습니다. Transit Gateway를 리전에 여러 개 두던 방식과 다른 점입니다.
- **core network당 경로 10,000개**는 모든 세그먼트의 경로를 합한 숫자입니다. 정적 경로, 공유로 받은 경로, 동적으로 배운 경로를 모두 셉니다. BGP로 받았지만 설치되지 않은 경로는 세지 않습니다.
- 그 밖에 정책 문서 크기 1 MB(조정 불가), core network당 정책 버전 10,000개, 연결당 Connect peer 4개(조정 불가), core network당 Direct Connect 연결 40개(조정 가능), VPN을 통해 core network에 광고하는 경로 1,000개가 있습니다.

출처: [Cloud WAN quotas](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-quotas.html)
