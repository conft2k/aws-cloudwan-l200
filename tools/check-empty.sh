#!/usr/bin/env bash
# Count what the workshop leaves behind, in both lab Regions.
#
#   tools/check-empty.sh [profile]        # default: demo1
#
# Run it before a rehearsal (a used account can hit the global network limit of
# 5 per account) and after the teardown in 3-4. Every count must be 0. Only
# read-only calls, and --profile is always explicit.
set -uo pipefail

PROFILE="${1:-demo1}"
REGIONS=(ap-northeast-2 us-west-2)
FAIL=0

q() {  # q <region> <label> <command...>
    local region="$1" label="$2"; shift 2
    local n
    n=$("$@" --profile "$PROFILE" --region "$region" --output text 2>/dev/null | wc -l | tr -d ' ')
    [ "$n" = 0 ] || FAIL=1
    printf '  %-22s %s\n' "$label" "$n"
}

echo "profile: $PROFILE"
for r in "${REGIONS[@]}"; do
    echo "== $r"
    q "$r" "스택" aws cloudformation list-stacks \
        --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE ROLLBACK_FAILED \
        DELETE_FAILED CREATE_IN_PROGRESS UPDATE_IN_PROGRESS DELETE_IN_PROGRESS \
        --query 'StackSummaries[].StackName'
    q "$r" "기본 아닌 VPC" aws ec2 describe-vpcs \
        --query 'Vpcs[?IsDefault==`false`].VpcId'
    q "$r" "EC2(종료 제외)" aws ec2 describe-instances \
        --query 'Reservations[].Instances[?State.Name!=`terminated`].InstanceId'
    q "$r" "VPN 연결" aws ec2 describe-vpn-connections \
        --query 'VpnConnections[?State!=`deleted`].VpnConnectionId'
    q "$r" "customer gateway" aws ec2 describe-customer-gateways \
        --query 'CustomerGateways[?State!=`deleted`].CustomerGatewayId'
    q "$r" "EIP" aws ec2 describe-addresses --query 'Addresses[].AllocationId'
    q "$r" "EICE" aws ec2 describe-instance-connect-endpoints \
        --query 'InstanceConnectEndpoints[?State!=`delete-complete`].InstanceConnectEndpointId'
done

# Cloud WAN is global; us-west-2 answers for every Region.
echo "== Cloud WAN (글로벌)"
q us-west-2 "global network" aws networkmanager describe-global-networks \
    --query 'GlobalNetworks[?State!=`DELETING`].GlobalNetworkId'
q us-west-2 "core network" aws networkmanager list-core-networks \
    --query 'CoreNetworks[?State!=`DELETING`].CoreNetworkId'

echo
if [ "$FAIL" = 0 ]; then
    echo "잔재 0 - 리허설을 시작해도 되고, 정리가 끝난 것이다"
else
    echo "!! 0이 아닌 항목이 있다. 위 목록을 보고 지운 뒤 다시 돌린다"
fi
exit "$FAIL"
