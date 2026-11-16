# 4-3. 문제 해결

실습 중에 막혔을 때 어디를 볼지 정리했습니다.

!!! warning "사전 테스트 전 초안입니다"
    이 표는 공식 문서와 템플릿 내용을 근거로 미리 정리한 것입니다. 사전 테스트에서 실제로 만난 오류와 대처를 확인해 채웁니다.

## 4-3-a. 증상으로 찾기 { #by-symptom }

| 이럴 때 | 볼 곳 | 해결 |
|---|---|---|
| 연결(attachment)을 만들려는데 오류가 난다 | **Network Manager** → core network → **Policy versions** | core network가 아직 배포 중일 수 있습니다. 정책이 **LIVE** 이고 **Change set state** 가 **Execution succeeded** 가 될 때까지 기다립니다. 배포에는 최대 30분이 걸립니다([2-1-d](lab0.md#lab0-d)) |
| 연결은 만들어졌는데 세그먼트가 비어 있다 | 연결의 **Tags** | `segment` 태그가 있는지, 값이 세그먼트 이름과 **정확히** 같은지 봅니다. `prod`, `dev`, `shared`, `onprem` 은 모두 소문자입니다. 어느 attachment policy 규칙에도 맞지 않으면 연결은 어느 세그먼트에도 들어가지 않습니다 |
| 연결이 `Pending attachment acceptance` 에서 멈춰 있다 | core network → **Attachments** | 세그먼트가 승인을 요구하도록 설정되어 있습니다. 연결을 골라 승인합니다([3-1-b](extra-a.md#a-b)) |
| 같은 세그먼트인데 통신이 안 된다 | VPC 라우트 테이블 | 연결을 붙이는 것과 VPC 라우트를 넣는 것은 다른 일입니다. 앱 서브넷의 라우트 테이블에 상대 대역을 core network로 보내는 경로가 있는지 봅니다([2-2-e](lab1.md#lab1-e)) |
| 오레곤 EC2로 ping이 안 된다 | 오레곤 라우트 테이블, 오레곤 연결 상태 | 위 항목을 먼저 보고, 오레곤 연결이 **Available** 인지, `prod` 세그먼트에 들어갔는지 봅니다 |
| 정책을 고쳤는데 통신이 그대로다 | core network → **Policy versions** | 정책 버전은 자동으로 배포되지 않습니다. change set을 **실행**해야 합니다([2-4-c](lab3.md#lab3-c)) |
| VPN 터널이 올라오지 않는다 | VPN 연결 → **Tunnel details** | Cloud WAN VPN은 attachment를 붙인 **뒤에** AWS 쪽 터널 엔드포인트가 생깁니다. 순서가 [2-3-a](lab2.md#lab2-a) → [2-3-b](lab2.md#lab2-b) → [2-3-c](lab2.md#lab2-c) 인 이유입니다. attachment가 **Available** 인지 먼저 봅니다 |
| 터널 설정 스크립트가 실패한다 | 스크립트가 출력한 `FAILED at:` 줄 | 어느 단계에서 멈췄는지 알려 줍니다. VPN 연결 ID를 제대로 넣었는지, attachment가 **Available** 인지 확인하고 다시 실행합니다 |
| BGP 세션이 올라오지 않는다 | 라우터에서 `sudo vtysh -c 'show bgp summary'` | attachment가 없으면 AWS 쪽 BGP 이웃이 생기지 않습니다. attachment 상태를 먼저 봅니다 |
| 온프레미스에서 `prod` 로 통신이 안 된다 | 정책의 `segment-actions` | 실습 [2-3-e](lab2.md#lab2-e) 에서는 **실패가 맞습니다**. `onprem` 과 `prod` 를 여는 것은 [2-4](lab3.md) 입니다 |
| 스택이 지워지지 않는다 | CloudFormation 스택 **Events** | 참가자가 만든 연결이 남아 있으면 core network가 지워지지 않습니다. [3-4](extra-d.md) 의 순서대로 연결을 먼저 지웁니다 |
| 오레곤 스택을 서울에서 만들려 하니 거부된다 | 콘솔 오른쪽 위 리전 | 오레곤 템플릿은 `us-west-2` 에서만 배포됩니다. 리전을 **US West (Oregon)** 으로 바꿉니다 |
| 콘솔 화면이 한국어로 나온다 | 콘솔 언어 설정 | 이 워크숍의 예제 화면은 영어 기준입니다. 언어를 **English** 로 바꾸면 따라 하기 쉽습니다([1-2-c](prerequisites.md#browser)) |

## 4-3-b. 그래도 안 되면 { #ask }

강사에게 다음을 알려 주세요.

1. 어느 단계에서 막혔는지(예: [2-2-d](lab1.md#lab1-d))
2. 리전(서울인지 오레곤인지)
3. 화면에 나온 오류 메시지 그대로
4. core network의 정책 상태(**LIVE** 인지)와 해당 연결의 상태
