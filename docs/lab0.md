# 2-1. 시작하기 (10분)

이 페이지는 **이론 강의를 듣기 전에** 합니다. Cloud WAN의 core network는 처음 만들 때 최대 30분이 걸립니다([공식 문서](https://docs.aws.amazon.com/network-manager/latest/cloudwan/cloudwan-getting-started.html)). 그동안에는 attachment(연결)와 policy version(정책 버전)을 만들 수 없습니다. 그래서 스택 2개를 먼저 배포해 두고, 이론 강의를 듣는 동안 core network가 백그라운드로 완성되게 합니다. 배포가 끝나기를 기다리지 않습니다.

## 2-1-a. 콘솔에 로그인하기 { #lab0-a }

1. 강사가 알려 준 계정 정보로 AWS 콘솔에 로그인합니다.
2. 콘솔 오른쪽 위의 리전 선택 메뉴에서 **Asia Pacific (Seoul)** 을 고릅니다.
3. 화면 언어를 영어로 맞춥니다. 이 워크숍의 버튼 이름은 모두 영어 화면 기준입니다. 콘솔 아래쪽(또는 오른쪽 위 설정 메뉴)의 언어 설정에서 **English (US)** 를 고릅니다.

    <!-- shot: lab0-login-01-region-language -->

**성공 확인**: 콘솔 오른쪽 위에 **Asia Pacific (Seoul)** 이 보이고, 메뉴가 영어로 나옵니다.

## 2-1-b. 서울 스택 배포하기 { #lab0-b }

서울 스택은 워크숍의 중심인 core network와 서울 쪽 리소스를 만듭니다.

- global network `cwan-ws-global`과 core network (초기 policy 포함, 세그먼트 4개, edge 2개: 서울·오레곤)
- prod VPC(`10.10.1.0/24`), dev VPC(`10.20.1.0/24`), shared VPC(`10.30.1.0/24`)와 각 VPC의 EC2 1대
- 온프레미스를 흉내 내는 VPC(`172.16.1.0/24`): 퍼블릭 서브넷의 VPN 라우터 EC2와 프라이빗 서브넷의 VM EC2
- 서울 prod·dev·shared VPC를 core network에 붙이는 VPC attachment 3개(`segment` 태그 포함)
- customer gateway(온프레미스 라우터의 Elastic IP, ASN `65000`)
- EC2 Instance Connect Endpoint: EC2 4대에 브라우저로 접속할 때 씁니다

1. 리전이 **Asia Pacific (Seoul)** 인지 다시 확인합니다.
2. 템플릿 파일을 내려받습니다: [cloudwan-workshop-seoul.yaml](assets/cloudwan-workshop-seoul.yaml){ download }
3. **CloudFormation** 콘솔 → **Create stack** → **With new resources (standard)** 를 누릅니다.
4. **Upload a template file** → **Choose file**로 내려받은 파일을 고르고 **Next**를 누릅니다.

    <!-- shot: lab0-cfn-01-upload -->

5. **Stack name**에 `cloudwan-workshop-seoul`을 넣습니다. **Parameters**는 그대로 두고 **Next**를 누릅니다.

    <!-- shot: lab0-cfn-02-parameters -->

6. 다음 화면에서 **Next**를 누르고, 마지막 검토 화면 맨 아래에 IAM 리소스를 만드는 것을 인정하는 확인란이 보이면 선택합니다. 이 스택은 EC2에 붙일 IAM 역할(role)과 인스턴스 프로파일을 만듭니다.

    <!-- shot: lab0-cfn-03-ack -->

7. **Submit**을 누릅니다.

**성공 확인**: 스택 상태가 **CREATE_IN_PROGRESS**입니다. 배포에 걸리는 시간은 사전 테스트에서 측정합니다.

<!-- shot: lab0-cfn-04-in-progress-seoul -->

## 2-1-c. 오레곤 스택 배포하기 { #lab0-c }

오레곤 스택은 오레곤 쪽 prod VPC(`10.11.1.0/24`)와 EC2 1대, EC2 Instance Connect Endpoint를 만듭니다. 오레곤 VPC를 core network에 붙이는 일은 이 스택이 하지 않습니다. 실습 2-2에서 직접 합니다.

!!! warning "리전을 바꾸는 것을 잊지 마세요"
    오레곤 스택은 **US West (Oregon)** 에서만 배포됩니다. 콘솔 오른쪽 위의 리전 선택 메뉴에서 먼저 **US West (Oregon)** 으로 바꾼 뒤 시작합니다. 서울에 그대로 두면 템플릿이 거부합니다. 서울 스택이 아직 배포 중이어도 상관없으니 바로 이어서 합니다.

1. 리전을 **US West (Oregon)** 으로 바꿉니다.
2. 템플릿 파일을 내려받습니다: [cloudwan-workshop-oregon.yaml](assets/cloudwan-workshop-oregon.yaml){ download }
3. **CloudFormation** 콘솔 → **Create stack** → **With new resources (standard)** → **Upload a template file** → **Choose file**로 파일을 고르고 **Next**를 누릅니다.

    <!-- shot: lab0-cfn-05-upload-oregon -->

4. **Stack name**에 `cloudwan-workshop-oregon`을 넣습니다. **Parameters**는 그대로 두고 **Next**를 누릅니다.
5. 다음 화면에서 **Next**를 누르고, 마지막 화면에서 **Submit**을 누릅니다. 이 스택에는 IAM 리소스가 없어서 IAM 확인란은 나오지 않을 수 있습니다.

**성공 확인**: 오레곤 리전에서 스택 상태가 **CREATE_IN_PROGRESS**입니다.

<!-- shot: lab0-cfn-06-in-progress-oregon -->

## 2-1-d. core network가 준비됐는지 보는 법 { #lab0-d }

스택이 **CREATE_COMPLETE**가 되어도 core network를 바로 쓸 수 있는지는 아직 확인하지 않았습니다. 그래서 **Policy versions** 화면의 상태를 준비 완료의 유일한 기준으로 삼습니다. 지금은 보는 법만 익히고, 실제 확인은 이론 강의가 끝난 뒤 실습 2-2 시작 전에 합니다.

1. **Network Manager** 콘솔 → **Global networks**를 엽니다. Cloud WAN은 리전에 묶이지 않아서 오른쪽 위 리전 선택에 **Global** 이 뜹니다.

    <!-- shot: lab0-cnet-00-global-networks -->

2. `cwan-ws-global`을 엽니다. 스택 배포 직후에는 아직 목록에 없거나 생성 중으로 보일 수 있습니다.
3. 왼쪽 메뉴에서 **Policy versions** 를 엽니다.

    <!-- shot: lab0-cnet-01-policy-versions -->

4. 정책이 **LIVE** 이고 **Change set state** 가 **Execution succeeded** 이면 준비가 끝난 것입니다.

    <!-- shot: lab0-cnet-02-live-succeeded -->

아직 준비되지 않았으면 여기서 기다리지 않습니다. 이론 강의를 들으러 갑니다.

**성공 확인**: **Policy versions** 가 어디에 있는지 알고, 어떤 값이 보이면 준비 완료인지 말할 수 있습니다.

## 2-1-e. 정리 { #lab0-e }

| 확인한 것 | 결과 |
|---|---|
| 콘솔 리전과 언어 | **Asia Pacific (Seoul)**, 영어 |
| 서울 스택 `cloudwan-workshop-seoul` | **CREATE_IN_PROGRESS** 또는 **CREATE_COMPLETE** |
| 오레곤 스택 `cloudwan-workshop-oregon` | **CREATE_IN_PROGRESS** 또는 **CREATE_COMPLETE** |
| core network 준비 기준 | **Policy versions** 에서 **LIVE**, **Change set state**가 **Execution succeeded** |

이제 이론 강의를 듣습니다. 강의가 끝나면 [2-2](lab1.md)로 넘어갑니다.
