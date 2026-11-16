#!/usr/bin/env bash
# Count what the workshop leaves behind, in both lab Regions.
#
#   tools/check-empty.sh [profile]        # default: demo1
#
# Run it before a rehearsal (a used account can hit the global network limit of
# 5 per account) and after the teardown in 3-4. Every count must be 0.
#
# A failed call is NOT zero. Expired credentials make every describe fail, and
# a script that hid that would report an account full of core network edges as
# clean. Anything that is not a plain number counts as a failure and is printed.
#
# Only read-only calls, and --profile is always explicit.
set -uo pipefail

PROFILE="${1:-demo1}"
REGIONS=(ap-northeast-2 us-west-2)
FAIL=0

q() {  # q <region> <label> <jmespath for the resources> <aws args...>
    local region="$1" label="$2" sel="$3"; shift 3
    local out rc
    out=$(aws "$@" --profile "$PROFILE" --region "$region" \
              --query "$sel | length(@)" --output text 2>&1)
    rc=$?
    if [ "$rc" -ne 0 ] || ! [[ "$out" =~ ^[0-9]+$ ]]; then
        echo "  $label: 조회 실패 - $(echo "$out" | tail -1)"
        FAIL=1
        return
    fi
    echo "  $label: $out"
    [ "$out" = 0 ] || FAIL=1
}

echo "profile: $PROFILE"
for r in "${REGIONS[@]}"; do
    echo "== $r"
    # Every status but DELETE_COMPLETE is a stack that still exists, including
    # ROLLBACK_COMPLETE and the *_ROLLBACK_* states a failed deploy leaves.
    q "$r" "스택" 'StackSummaries[?StackStatus!=`DELETE_COMPLETE`]' \
        cloudformation list-stacks
    q "$r" "기본 아닌 VPC" 'Vpcs[?IsDefault==`false`]' ec2 describe-vpcs
    q "$r" "EC2(종료 제외)" 'Reservations[].Instances[?State.Name!=`terminated`][]' \
        ec2 describe-instances
    q "$r" "VPN 연결" 'VpnConnections[?State!=`deleted`]' ec2 describe-vpn-connections
    q "$r" "customer gateway" 'CustomerGateways[?State!=`deleted`]' \
        ec2 describe-customer-gateways
    q "$r" "EIP" 'Addresses' ec2 describe-addresses
    q "$r" "EICE" 'InstanceConnectEndpoints[?State!=`delete-complete`]' \
        ec2 describe-instance-connect-endpoints
done

# Cloud WAN is global; us-west-2 answers for every Region. Nothing is filtered
# out here - one still being deleted holds its place against the limit.
echo "== Cloud WAN (글로벌)"
q us-west-2 "global network" 'GlobalNetworks' networkmanager describe-global-networks
q us-west-2 "core network" 'CoreNetworks' networkmanager list-core-networks

echo
if [ "$FAIL" = 0 ]; then
    echo "잔재 0 - 리허설을 시작해도 되고, 정리가 끝난 것이다"
else
    echo "!! 0이 아니거나 조회가 실패한 항목이 있다. 위 목록을 보고 처리한 뒤 다시 돌린다"
fi
exit "$FAIL"
