# 2-4. 정책으로 통신 범위 바꾸기 (13분)

이 실습이 워크숍의 결론입니다. 정책(policy)에 JSON 몇 줄을 넣고 반영하면, 서울과 오레곤에 걸친 통신 범위가 한 번에 바뀝니다. 리전마다 따로 설정하지 않습니다. 그 변화를 직접 확인합니다.

<figure markdown="span">
  ![AWS Cloud WAN 실습 2-4의 정책 변경 전후 비교 구성도. 위쪽은 정책 변경 전이다. 왼쪽에 온프레미스 LAN을 나타내는 AWS Site-to-Site VPN이 있고, 그 attachment가 segment=onprem 태그로 core network 안의 onprem 세그먼트에 배정되어 있다. core network 안에는 세그먼트 네 개가 있다. prod 세그먼트는 서울 prod VPC와 오레곤 prod VPC 두 개를 담고, dev 세그먼트도 서울 dev VPC와 오레곤 dev VPC 두 개를 담으며, shared 세그먼트는 서울 shared VPC 하나를, onprem 세그먼트는 Site-to-Site VPN attachment 하나를 담는다. 변경 전 통신 상태는 onprem과 shared는 통신됨, onprem과 prod는 차단, onprem과 dev는 차단, prod와 dev는 차단, shared와 prod는 통신됨, shared와 dev는 통신됨이다. 가운데 밴드는 참가자가 정책의 segment-actions에 추가하는 JSON 조각을 보여 준다. action은 share, mode는 attachment-route, segment는 onprem, share-with는 prod 하나다. 반영 순서는 policy version 생성, change set 검토, 실행이며, 리전별 설정 없이 서울과 오레곤 prod 양쪽이 함께 열리고 dev 격리는 그대로 둔다고 적혀 있다. 아래쪽은 정책 변경 후이며 위쪽과 배치가 완전히 같다. 달라진 것은 onprem과 prod 사이 선 하나뿐으로, 빨간 점선 차단이 굵은 초록 실선 통신됨으로 바뀌고 정책에서 바뀐 부분이라는 표시가 붙는다. 이 한 선으로 온프레미스는 서울 prod VPC와 오레곤 prod VPC 양쪽에 모두 닿는다. 나머지는 그대로다. 온프레미스는 서울 dev VPC와 오레곤 dev VPC 어느 쪽에도 닿지 않고, prod와 dev도 여전히 차단이며, onprem과 shared는 그대로 통신됨, shared와 prod, dev도 그대로 통신됨이다](images/diagrams/lab3-policy.png)
  <figcaption>그림 1. 정책 한 줄로 바뀌는 것</figcaption>
</figure>

[2-3](lab2.md)에서 온프레미스 VM `172.16.1.10`은 서울 shared EC2에는 닿았지만 서울 prod EC2에는 닿지 못했습니다. `onprem` 세그먼트가 `prod`와 아무것도 공유하지 않았기 때문입니다. 이번에는 정책에 `onprem`과 `prod`의 share를 넣어 이 둘을 연결합니다.

## 2-4-a. 정책에 share 한 줄 넣기 { #lab3-a }

현재 정책을 바탕으로 새 policy version을 만듭니다. `segment-actions`에 share 하나를 더 넣습니다.

1. **Network Manager** 콘솔에서 이 워크숍의 core network를 엽니다.
2. **Policy versions**로 이동해 현재 정책을 편집하고, 새 policy version을 만듭니다.

    !!! warning "왼쪽 메뉴의 **Policies**가 아닙니다"
        왼쪽 메뉴에도 **Policies**라는 항목이 있지만 그것은 VPC IP Address Manager 쪽이라 전혀 다른 화면입니다. core network 안의 **Policy versions**로 가세요.
3. `segment-actions` 배열에 다음 항목을 추가합니다.

    ```json
    {
      "action": "share",
      "mode": "attachment-route",
      "segment": "onprem",
      "share-with": ["prod"]
    }
    ```

넣을 위치는 기존 `shared` share 항목의 바로 뒤입니다. 두 항목 사이에 쉼표(`,`)가 있어야 합니다. 편집을 마친 `segment-actions`는 다음과 같습니다.

```json
  "segment-actions": [
    {
      "action": "share",
      "mode": "attachment-route",
      "segment": "shared",
      "share-with": ["prod", "dev", "onprem"]
    },
    {
      "action": "share",
      "mode": "attachment-route",
      "segment": "onprem",
      "share-with": ["prod"]
    }
  ],
```

`share-with`에 `dev`는 넣지 않습니다. 고객 요구사항은 온프레미스가 개발 환경에 닿지 않는 것입니다.

<!-- shot: lab3-policy-01-edit -->

**성공 확인**: 정책 버전 목록에 새 버전이 보입니다.

<!-- shot: lab3-policy-02-versions -->

## 2-4-b. change set 검토하기 { #lab3-b }

새 버전을 만들면 Cloud WAN이 현재 적용 중인 정책과 새 버전을 비교해 change set(바뀌는 내용의 목록)을 만듭니다. 적용하기 전에 무엇이 바뀌는지 읽어 봅니다.

1. 방금 만든 새 policy version의 change set을 엽니다.
2. 바뀌는 항목을 읽습니다. 이번 변경에서는 `onprem`과 `prod` 사이의 share가 새로 생기는 것이 보여야 합니다.
3. 의도하지 않은 항목(세그먼트 삭제 등)이 없는지 확인합니다.

!!! info "이 단계에서는 아직 반영되지 않습니다"
    정책 버전은 만들기만 해서는 배포되지 않습니다. 다음 단계에서 change set을 실행해야 적용됩니다. 그전까지 통신 범위는 그대로입니다.

!!! tip "세그먼트를 추가·삭제하거나 격리 옵션을 바꿀 때"
    세그먼트를 추가·삭제하거나 격리 옵션을 바꾸면 그 세그먼트의 모든 edge에 작업이 생깁니다. 이번 변경은 share 추가입니다.

<!-- shot: lab3-policy-03-changeset -->

**성공 확인**: change set 목록에 `onprem`과 `prod` 사이의 변경이 보입니다. 상태는 **Ready to execute**입니다.

## 2-4-c. change set 실행하기 { #lab3-c }

change set을 실행해 새 버전을 적용합니다.

1. change set을 실행합니다.
2. 상태가 **Ready to execute** → **Executing policy** → **Execution succeeded**로 바뀌는 것을 지켜봅니다.
3. 새 정책이 **LIVE**가 되었는지 확인합니다.

반영에 걸리는 시간은 사전 테스트에서 측정합니다. 상태가 **Executing policy**에 머무르는 동안에는 다음 단계로 가지 말고 기다립니다.

<!-- shot: lab3-policy-04-executing -->
<!-- shot: lab3-policy-05-live -->

**성공 확인**: change set 상태가 **Execution succeeded**이고, 새 정책 버전이 **LIVE**로 표시됩니다.

## 2-4-d. 다시 통신해 보기 { #lab3-d }

[2-3](lab2.md)에서 실패했던 통신을 다시 시도합니다. 온프레미스 VM 터미널에서 실행합니다.

1. 서울 prod EC2로 ping을 보냅니다.

    ```bash
    ping -c 4 10.10.1.10
    ```

2. 오레곤 prod EC2로 ping을 보냅니다.

    ```bash
    ping -c 4 10.11.1.10
    ```

<!-- shot: lab3-policy-06-ping-prod -->

**성공 확인**: 두 ping 모두 응답이 오고 **0% packet loss**입니다. 오레곤은 따로 설정하지 않았는데도 함께 열렸습니다. 정책이 `prod` 세그먼트 전체에 적용되기 때문입니다.

3. dev EC2로 ping을 보냅니다. 고객 요구사항대로 실패해야 합니다.

    ```bash
    ping -c 4 10.20.1.10
    ```

**결과(실패가 맞습니다)**: **100% packet loss**입니다. `onprem`과 `dev` 사이에는 share가 없습니다.

<!-- shot: lab3-policy-07-ping-dev -->

prod ↔ dev도 여전히 막혀 있습니다. 서울 prod EC2에서 dev EC2 `10.20.1.10`으로 ping을 보내 확인해 보세요(2-2에서 쓴 방법과 같습니다). 이쪽도 **결과(실패가 맞습니다)**입니다.

## 2-4-e. 워크숍 정리 { #lab3-e }

| 확인한 것 | 결과 |
|---|---|
| 기본 동작 | 세그먼트는 같은 세그먼트끼리만 통신. `prod` ↔ `dev`는 따로 막을 필요가 없음 |
| 공유 서비스 | `shared`가 `prod`·`dev`·`onprem`에 share. 세 세그먼트는 `shared`에 닿지만 서로는 닿지 않음 |
| 글로벌 연결 | 서울과 오레곤의 `prod`가 같은 세그먼트로 통신 |
| 정책 변경 전 | 온프레미스 → `prod` 차단 |
| 정책 변경 후 | 온프레미스 → 서울 `prod`, 오레곤 `prod` 통신. `dev`는 계속 차단 |
| 반영 방법 | share 항목 하나 추가 → change set 검토 → 실행 |

Transit Gateway로 같은 일을 하려면 리전마다 라우팅 테이블을 따로 만들고, 연결(attachment)마다 연결과 전파(propagation)를 따로 설정해야 합니다. 리전이 늘수록 설정할 곳도 늘어납니다. Cloud WAN에서는 이 일을 정책 한 곳의 몇 줄로 했고, 모든 리전에 같이 적용되었습니다.

이제 [3-4 리소스 정리](extra-d.md)를 **반드시** 하세요. 정리하지 않으면 요금이 계속 나옵니다. 시간이 남으면 [3-1](extra-a.md) ~ [3-3](extra-c.md)을 해 보세요.
