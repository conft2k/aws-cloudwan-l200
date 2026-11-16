# 3-4. 리소스 정리

!!! danger "실습이 끝나면 반드시 정리합니다"
    core network edge는 리전당 시간당 요금이 붙습니다(리전당 $0.50/시간). 연결(attachment)과 VPN 연결도 시간당 요금이 붙습니다. 정리하지 않으면 요금이 계속 늘어납니다.

실습이 끝나면 만든 리소스를 지웁니다. 아래 **순서대로** 진행합니다. **순서가 중요합니다.** 참가자가 직접 만든 것을 먼저 지우고, 그다음에 스택을 지웁니다. core network는 연결이 하나라도 남아 있으면 지워지지 않기 때문입니다.

| 순서 | 지울 것 | 누가 만들었나 |
|---|---|---|
| 1 | 오레곤 VPC attachment | 참가자([2-2-d](lab1.md)) |
| 2 | Site-to-Site VPN attachment | 참가자([2-3-b](lab2.md)) |
| 3 | Site-to-Site VPN 연결 | 참가자([2-3-a](lab2.md)) |
| 4 | 오레곤 스택 `cloudwan-workshop-oregon` | CloudFormation |
| 5 | 서울 스택 `cloudwan-workshop-seoul` | CloudFormation |

각 단계의 소요 시간은 사전 테스트에서 측정합니다.

## 3-4-a. 오레곤 VPC attachment 지우기 (사전 테스트에서 측정합니다) { #d-a }

1. **Network Manager** → **Global networks** → `cwan-ws-global` → **Core network** → **Attachments**로 갑니다.
2. 오레곤(`us-west-2`)의 prod VPC 연결을 고르고 삭제합니다. 확인 창이 나오면 한 번 더 확인합니다.

<!-- shot: extraD-01-delete-attachment -->

**성공 확인**: 연결이 목록에서 사라지거나 삭제된 상태가 됩니다. 연결 목록에서 오레곤 VPC 연결이 더 보이지 않을 때까지 기다린 뒤 다음으로 넘어갑니다.

## 3-4-b. Site-to-Site VPN attachment 지우기 (사전 테스트에서 측정합니다) { #d-b }

같은 **Attachments** 화면에서 온프레미스 쪽 Site-to-Site VPN 연결(`segment=onprem`)을 고르고 삭제합니다.

<!-- shot: extraD-02-delete-vpn-attachment -->

**성공 확인**: VPN attachment가 목록에서 사라지거나 삭제된 상태가 됩니다. 이 단계가 끝나면 core network에는 서울 VPC 연결 3개만 남습니다(스택이 만든 연결입니다).

## 3-4-c. Site-to-Site VPN 연결 지우기 (사전 테스트에서 측정합니다) { #d-c }

VPN attachment를 먼저 지워야 VPN 연결을 지울 수 있습니다.

1. **VPC** 콘솔(서울) → **Site-to-Site VPN connections**로 갑니다.
2. [2-3-a](lab2.md)에서 만든 VPN 연결을 고르고 **Actions** → **Delete VPN connection**을 누릅니다.
3. 확인 창에서 삭제를 확정합니다.

<!-- shot: extraD-03-delete-vpn -->

**성공 확인**: VPN 연결의 상태가 **Deleted**가 됩니다. customer gateway는 스택이 만든 것이므로 그대로 둡니다. 서울 스택을 지울 때 함께 지워집니다.

## 3-4-d. 오레곤 스택 지우기 (사전 테스트에서 측정합니다) { #d-d }

1. 리전을 오레곤(`us-west-2`)으로 바꿉니다.
2. **CloudFormation** → `cloudwan-workshop-oregon` → **Delete**를 누릅니다.
3. 확인 창에서 삭제를 확정합니다.

<!-- shot: extraD-04-delete-oregon-stack -->

**성공 확인**: 스택이 목록에서 사라집니다(`DELETE_COMPLETE`). 오레곤 prod VPC와 EC2도 함께 지워집니다.

## 3-4-e. 서울 스택 지우기 (사전 테스트에서 측정합니다) { #d-e }

1. 리전을 서울(`ap-northeast-2`)로 바꿉니다.
2. **CloudFormation** → `cloudwan-workshop-seoul` → **Delete**를 누릅니다.
3. 확인 창에서 삭제를 확정합니다.

<!-- shot: extraD-05-delete-seoul-stack -->

**성공 확인**: 스택이 목록에서 사라집니다(`DELETE_COMPLETE`). core network, global network, 서울의 VPC와 EC2가 함께 지워집니다.

### 스택 삭제가 실패할 때 { #d-fail }

가장 흔한 원인은 **연결이 남아 있어 core network가 지워지지 않는 것**입니다. 스택이 `DELETE_FAILED`가 되면 다음 순서로 확인합니다.

1. **Events** 탭에서 실패한 리소스와 이유를 봅니다.
2. core network에 연결이 남아 있는지 **Network Manager** → **Core network** → **Attachments**에서 봅니다. 참가자가 만든 오레곤 VPC 연결이나 VPN 연결이 남아 있으면 3-4-a, 3-4-b로 돌아가 지웁니다.
3. 연결이 모두 사라졌으면 스택에서 **Delete**를 다시 누릅니다.

!!! warning "오레곤 스택을 먼저 지우지 않았다면"
    오레곤 VPC 연결을 먼저 지우지 않고 오레곤 스택을 지우면 VPC가 지워지지 않을 수 있습니다. 연결을 지운 뒤 스택 삭제를 다시 시도하세요.

그래도 해결되지 않으면 [4-3 문제 해결](troubleshooting.md)을 보세요.

## 3-4-f. 마무리 { #d-f }

아래를 모두 확인하면 정리가 끝납니다.

- [ ] 오레곤 VPC attachment가 없습니다
- [ ] Site-to-Site VPN attachment가 없습니다
- [ ] Site-to-Site VPN 연결이 **Deleted**입니다(서울)
- [ ] 스택 `cloudwan-workshop-oregon`이 `DELETE_COMPLETE`입니다(오레곤)
- [ ] 스택 `cloudwan-workshop-seoul`이 `DELETE_COMPLETE`입니다(서울)
- [ ] **Network Manager**에 `cwan-ws-global`(global network)과 core network가 없습니다
- [ ] 서울과 오레곤의 EC2 콘솔에 실습 EC2가 없습니다

**성공 확인**: 위 체크 목록이 모두 확인되었습니다.
