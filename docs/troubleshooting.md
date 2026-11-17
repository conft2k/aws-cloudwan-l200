# 4-3. 문제 해결

실습 중에 막혔을 때 어디를 볼지 정리했습니다.

## 4-3-a. 증상으로 찾기 { #by-symptom }

| 이럴 때 | 볼 곳 | 해결 |
|---|---|---|
| 연결(attachment)을 만들려는데 오류가 난다 | **Network Manager** → core network → **Policy versions** | core network가 아직 배포 중일 수 있습니다. 정책이 **LIVE** 이고 **Change set state** 가 **Execution succeeded** 가 될 때까지 기다립니다. 배포에는 최대 30분이 걸립니다([2-1-d](lab0.md#lab0-d)) |
| 연결 이름을 눌러도 상세 창이 열리지 않는다 | **Attachments** 목록의 행 맨 왼쪽 | **Name** 열의 글자는 링크가 아닙니다. 행 맨 왼쪽의 동그란 **선택 버튼**을 눌러야 표 아래에 상세 창이 열립니다([2-2-a](lab1.md#lab1-a)) |
| 연결은 만들어졌는데 세그먼트가 비어 있다 | 연결의 **Tags** | `segment` 태그가 있는지, 값이 세그먼트 이름과 **정확히** 같은지 봅니다. `prod`, `dev`, `shared`, `onprem` 은 모두 소문자입니다. 어느 attachment policy 규칙에도 맞지 않으면 연결은 어느 세그먼트에도 들어가지 않습니다 |
| 연결이 `Pending attachment acceptance` 에서 멈춰 있다 | core network → **Attachments** | 세그먼트가 승인을 요구하도록 설정되어 있습니다. 연결을 골라 승인합니다([3-1-b](extra-a.md#a-b)) |
| 같은 세그먼트인데 통신이 안 된다 | VPC 라우트 테이블 | 연결을 붙이는 것과 VPC 라우트를 넣는 것은 다른 일입니다. 앱 서브넷의 라우트 테이블에 상대 대역을 core network로 보내는 경로가 있는지 봅니다([2-2-e](lab1.md#lab1-e)) |
| 오레곤 EC2로 ping이 안 된다 | 오레곤 라우트 테이블, 오레곤 연결 상태 | 위 항목을 먼저 보고, 오레곤 연결이 **Available** 인지, `prod` 세그먼트에 들어갔는지 봅니다 |
| **Routes** 탭에 경로가 하나도 나오지 않는다 | **Route Filter** | **Segment** 와 **Edge location** 을 고른 뒤 **Search routes** 를 눌러야 경로가 나옵니다([2-2-f](lab1.md#lab1-f)) |
| 정책을 고쳤는데 통신이 그대로다 | core network → **Policy versions** | 정책 버전은 자동으로 배포되지 않습니다. change set을 **실행**해야 합니다([2-4-c](lab3.md#lab3-c)) |
| 왼쪽 메뉴의 **Policies** 를 눌렀더니 정책 편집 화면이 아니다 | 메뉴 위치 | **Policies** 는 VPC IP Address Manager 쪽 화면입니다. core network 안의 **Policy versions** 로 가세요([2-4-a](lab3.md#lab3-a)) |
| 정책을 고치려는데 JSON은 없고 입력 폼만 나온다 | **Choose policy view mode** | 기본값이 **Visual editor** 입니다. **JSON** 으로 바꾸면 현재 정책 전체가 줄 번호가 달린 편집기에 나옵니다([2-4-a](lab3.md#lab3-a)) |
| change set이 **Out of date** 라서 실행할 수 없다 | core network → **Policy versions** | 다른 버전이 먼저 적용되어 그 change set은 쓸 수 없게 된 것입니다. **LIVE** 버전을 골라 **Edit** 로 새 버전을 다시 만드세요([2-4-a](lab3.md#lab3-a)) |
| VPN 연결을 만들어 두었는데 Cloud WAN에 붙일 수 없다 | VPN 연결을 만들 때 고른 두 값 | Cloud WAN에 붙일 VPN 연결은 **Target gateway type** 이 **Not associated** 이고 **Routing options** 가 **Dynamic (requires BGP)** 여야 합니다. 다르게 만들었다면 그 VPN 연결을 지우고 다시 만듭니다([2-3-a](lab2.md#lab2-a)) |
| 터널 설정 스크립트가 `FAILED at: waiting for the IPsec security associations` 로 끝난다 | core network → **Attachments** 에서 VPN 연결의 상태 | 거의 언제나 **attachment가 아직 `Available` 이 아닌 것**입니다. `Pending network update` 면 아직입니다. 화면은 보안 그룹과 customer gateway 주소를 의심하라고 알려 주지만, 스택이 만든 보안 그룹은 UDP 500·4500을 이미 열어 두었습니다. `Available` 이 된 뒤 **같은 명령을 그대로 다시 실행**하면 됩니다([2-3-b](lab2.md#lab2-b)) |
| VPN 터널이 올라오지 않는다 | VPN 연결 → **Tunnel details** | Cloud WAN VPN은 attachment를 붙인 **뒤에** AWS 쪽 터널 엔드포인트가 생깁니다. 순서가 [2-3-a](lab2.md#lab2-a) → [2-3-b](lab2.md#lab2-b) → [2-3-c](lab2.md#lab2-c) 인 이유입니다. attachment가 **Available** 인지 먼저 봅니다 |
| 터널 설정 스크립트가 실패한다 | 스크립트가 출력한 `FAILED at:` 줄 | 어느 단계에서 멈췄는지 알려 줍니다. VPN 연결 ID를 제대로 넣었는지, attachment가 **Available** 인지 확인하고 다시 실행합니다 |
| BGP 세션이 올라오지 않는다 | 라우터에서 `sudo vtysh -c 'show bgp summary'` | attachment가 없으면 AWS 쪽 BGP 이웃이 생기지 않습니다. attachment 상태를 먼저 봅니다. 올라온 이웃은 **Up/Down** 열이 시간으로 세어지고, 아직이면 그 자리에 `Active` 나 `Connect` 가 나옵니다([2-3-c](lab2.md#lab2-c)) |
| 터널과 BGP는 올라왔는데 `show ip route bgp` 가 비어 있다 | 같은 명령을 몇 번 더 | 경로가 설치되기까지 잠시 걸립니다. 고장이 아니라 수렴을 기다리는 것이니 `10.30.1.0/24` 가 나타난 뒤에 ping을 합니다([2-3-c](lab2.md#lab2-c)) |
| 온프레미스에서 `prod` 로 통신이 안 된다 | 정책의 `segment-actions` | 실습 [2-3-f](lab2.md#lab2-f) 에서는 **실패가 맞습니다**. `onprem` 과 `prod` 를 여는 것은 [2-4](lab3.md) 입니다 |
| **Connect** 버튼이 회색이라 EC2에 접속할 수 없다 | **Connect to Linux instance** 의 **Choose how to connect** | 콘솔은 첫 번째 **EC2 Instance Connect** 가 골라진 채로 열리는데, 실습 EC2는 퍼블릭 IP가 없어 `No public IPv4 or IPv6 address assigned` 경고와 함께 버튼이 잠깁니다. **Private subnet access** 의 **EC2 Instance Connect Endpoint** 를 고릅니다([2-2-b](lab1.md#lab1-b)) |
| 승인 대기 중인 연결의 VPC에 라우트를 넣으려니 거부된다 | 오류 메시지 | `InvalidCoreNetworkArn.NotFound` 가 납니다. 승인 전에는 VPC가 아직 core network에 붙지 않은 것으로 취급됩니다. **승인을 먼저 하고 라우트를 넣습니다**([3-1-b](extra-a.md#a-b)) |
| VPN 연결을 지우려니 거부된다 | VPN attachment 상태 | `UnsupportedOperation: Unable to delete a vpn that's associated to a Core Network` 가 납니다. VPN attachment가 **목록에서 완전히 사라진 뒤에야** VPN 연결을 지울 수 있습니다. attachment가 `Deleting` 인 동안 VPN 연결은 `Modifying` 으로 보입니다([3-4-c](extra-d.md#d-c)) |
| 스택 삭제 창의 **Delete stack** 버튼이 회색이다 | 창 안의 입력 칸 | `Type "<스택 이름>" to confirm deletion of the stack.` 이라고 적힌 칸에 **스택 이름을 그대로 입력해야** 버튼이 활성화됩니다. attachment 삭제 창은 입력을 요구하지 않아 요령이 다릅니다([3-4-d](extra-d.md#d-d)) |
| 스택이 지워지지 않는다 | CloudFormation 스택 **Events** | 참가자가 만든 연결이 남아 있으면 core network가 지워지지 않습니다. [3-4](extra-d.md) 의 순서대로 연결을 먼저 지웁니다 |
| 스택 생성이 실패하고 **ROLLBACK_FAILED** 로 멈춘다 | CloudFormation 스택 **Events** | core network가 아직 만들어지는 중(`PENDING`)이라 롤백이 지우지 못한 것입니다. 아래 [4-3-b](#rollback-failed) 를 보세요 |
| 오레곤 스택을 서울에서 만들려 하니 거부된다 | 콘솔 오른쪽 위 리전 | 오레곤 템플릿은 `us-west-2` 에서만 배포됩니다. 리전을 **US West (Oregon)** 으로 바꿉니다 |
| 콘솔 화면이 한국어로 나온다 | 콘솔 언어 설정 | 이 워크숍의 예제 화면은 영어 기준입니다. 언어를 **English** 로 바꾸면 따라 하기 쉽습니다([1-2-c](prerequisites.md#browser)) |

## 4-3-b. 스택이 ROLLBACK_FAILED 로 멈췄을 때 { #rollback-failed }

스택 생성이 실패하면 CloudFormation이 되돌리기(롤백)를 시작하고, 그 과정에서 core network를 지우려 합니다. 그런데 core network는 만드는 데 15분 안팎이 걸려서, 그 시점에는 아직 **만들어지는 중**(`PENDING`)입니다. 만들어지는 중인 것은 지울 수 없으므로 롤백이 멈추고 스택은 **ROLLBACK_FAILED** 가 됩니다.

스택 **Events** 에 이런 메시지가 보입니다.

```text
STATE: PENDING cannot be modified by ACTION: DELETE
```

!!! info "참가자 잘못이 아닙니다"
    Cloud WAN의 생성 시간 때문에 생기는 일입니다. 아래 순서대로 하면 복구됩니다. 강사에게 알려 주세요.

1. core network가 다 만들어질 때까지 기다립니다. **Network Manager** → **Core networks** 에서 상태가 **Available** 이 되면 됩니다. 생성에는 **15분** 안팎이 걸립니다.
2. **Available** 이 된 뒤 CloudFormation 콘솔에서 그 스택을 **Delete stack** 으로 지웁니다. 확인 창의 입력 칸에 스택 이름을 그대로 적어야 버튼이 눌립니다([3-4-d](extra-d.md#d-d)). 이번에는 지워집니다.
3. 삭제가 끝나면 [2-1-b](lab0.md#lab0-b) 부터 다시 합니다.

**결과**: 스택이 목록에서 사라지고, **Network Manager** 에 core network와 global network가 남아 있지 않습니다.

## 4-3-c. 그래도 안 되면 { #ask }

강사에게 다음을 알려 주세요.

1. 어느 단계에서 막혔는지(예: [2-2-d](lab1.md#lab1-d))
2. 리전(서울인지 오레곤인지)
3. 화면에 나온 오류 메시지 그대로
4. core network의 정책 상태(**LIVE** 인지)와 해당 연결의 상태
