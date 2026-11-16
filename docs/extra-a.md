# 3-1. 연결 승인과 격리 옵션

실습에서는 세그먼트 설정 `require-attachment-acceptance`를 `false`로 두어서, 연결을 만들면 바로 세그먼트에 들어갔습니다. 운영 환경에서는 아무나 연결을 붙이지 못하게 막거나, 같은 세그먼트 안의 연결끼리도 서로 못 보게 해야 할 때가 있습니다. 이 페이지에서는 그때 쓰는 옵션 두 가지를 봅니다.

- `require-attachment-acceptance`: 연결을 만들어도 **승인해야** 세그먼트에 들어갑니다.
- `isolate-attachments`: 같은 세그먼트 안의 연결끼리도 **서로 통신하지 못합니다**.

시간이 남거나 워크숍이 끝난 뒤에 혼자 해 보는 과제입니다. 3-1-c는 정책을 직접 바꾸므로 [2-4](lab3.md)까지 마친 뒤에 하세요.

## 3-1-a. 연결 승인 요구하기 { #a-a }

`require-attachment-acceptance`를 `true`로 두면 연결이 만들어져도 바로 세그먼트에 들어가지 않고 **승인 대기** 상태로 멈춥니다. 네트워크 담당자가 승인해야 통신이 시작됩니다. 연결을 만드는 팀과 core network를 관리하는 팀이 다를 때 쓰는 안전장치입니다.

이 값은 두 곳에서 정할 수 있습니다.

| 위치 | 정책의 키 | 적용 대상 |
|---|---|---|
| 세그먼트 | `segments[]`의 `require-attachment-acceptance` | 그 세그먼트에 들어오는 모든 연결 |
| attachment policy | `attachment-policies[]`의 `action.require-acceptance` | 그 규칙에 맞는 연결 |

둘이 다르면 **attachment policy 쪽이 세그먼트 설정을 덮어씁니다**. 예를 들어 세그먼트는 `false`여도 규칙의 `require-acceptance`가 `true`이면 그 규칙에 맞는 연결은 승인이 필요합니다.

실습 정책에서 attachment policy에 넣는다면 다음 모양입니다. 이 JSON은 설명용이며, 이 페이지의 과제에서는 적용하지 않습니다.

```json
{
  "rule-number": 100,
  "conditions": [{ "type": "tag-exists", "key": "segment" }],
  "action": {
    "association-method": "tag",
    "tag-value-of-key": "segment",
    "require-acceptance": true
  }
}
```

**성공 확인**: 세그먼트 설정과 attachment policy 설정 중 어느 쪽이 이기는지 한 문장으로 말할 수 있습니다(attachment policy).

## 3-1-b. 콘솔에서 연결 승인하기 { #a-b }

승인이 필요한 연결은 만들면 **Network Manager** 콘솔의 core network 화면에서 승인 대기 상태로 보입니다. 승인 흐름은 다음과 같습니다.

1. **Network Manager** → **Core network** → **Attachments**로 갑니다.
2. 승인 대기 상태인 연결을 고릅니다.
3. 연결이 어느 세그먼트로 가려는지 확인하고 승인합니다.
4. 상태가 **Available**로 바뀌고 해당 세그먼트의 경로 테이블에 경로가 들어옵니다.

<!-- shot: extraA-01-pending-acceptance -->

<!-- shot: extraA-02-accept-attachment -->

!!! info "화면 이름은 사전 테스트에서 확인합니다"
    승인 대기 상태의 표시 이름과 승인 버튼의 위치는 사전 테스트에서 확인한 뒤 이 절에 적습니다. 위 순서는 흐름만 설명합니다.

연결을 승인하지 않고 두면 그 연결은 세그먼트에 들어가지 못하므로 통신하지 않습니다. 승인하지 않을 연결은 **거절**하거나 삭제합니다.

**성공 확인**: 승인 전에는 연결이 세그먼트의 경로 테이블에 경로를 내지 않고, 승인한 뒤에야 경로가 보입니다.

## 3-1-c. 과제: `dev`를 격리하기 { #a-c }

`isolate-attachments`를 `true`로 두면 그 세그먼트 안의 연결끼리도 통신하지 못합니다. 세그먼트는 기본적으로 같은 세그먼트 안의 연결끼리 통신합니다. 이 옵션은 그 기본값을 끕니다. 남는 경로는 두 가지뿐입니다.

- 다른 세그먼트에서 **share**로 받은 경로
- **static route**(정적 경로)

!!! info "Transit Gateway route table attachment는 예외입니다"
    Transit Gateway route table attachment를 통해 들어오는 경로는 `isolate-attachments`의 영향을 받지 않습니다. 이 옵션을 켠 세그먼트에서도 그런 경로는 그대로 남습니다.

실습 환경의 `dev` 세그먼트에는 서울 dev VPC 연결이 하나뿐입니다. 연결끼리 통신하는지 직접 보려면 연결이 둘 이상 있어야 하므로, 이 과제는 **`shared`로 가는 경로가 그대로 남는지**를 봅니다.

### 해 보기

1. **Network Manager** → **Core network** → **Policy versions**에서 `LIVE` 정책을 열어 새 버전을 만듭니다([2-4-a](lab3.md)와 같은 방법입니다).
2. `segments`의 `dev` 항목에 `isolate-attachments`를 추가합니다.

    ```json
    { "name": "dev", "description": "개발 환경", "require-attachment-acceptance": false, "isolate-attachments": true }
    ```

3. change set을 검토하고 실행합니다([2-4-b](lab3.md), [2-4-c](lab3.md)).
4. `Execution succeeded`가 된 뒤, 서울 dev EC2(`10.20.1.10`)에서 다음을 확인합니다.

    ```bash
    ping -c 3 10.30.1.10
    ```

<!-- shot: extraA-03-isolate-change-set -->

**결과**: `dev` 연결이 하나뿐이므로 `shared`로 가는 ping은 그대로 성공합니다. `shared`는 share로 경로를 받기 때문입니다. 격리가 막는 것은 **같은 세그먼트 안의 다른 연결**입니다. `dev`에 VPC를 하나 더 붙이면 두 VPC는 서로 통신하지 못하지만 둘 다 `shared`에는 닿습니다.

### 되돌리기

1. `LIVE` 정책에서 새 버전을 만들어 `isolate-attachments`를 `false`로 바꾸거나 키를 지웁니다.
2. change set을 검토하고 실행합니다.

또는 **Policy versions**에서 이전 버전(격리를 넣기 전 버전)을 골라 다시 `LIVE`로 만들 수도 있습니다. 이 방법을 쓸 때의 화면은 사전 테스트에서 확인합니다.

**성공 확인**: change set에 `dev`의 변경이 보이고 `Execution succeeded`가 됩니다. 되돌린 뒤에는 change set에 반대 방향의 변경이 보입니다.
