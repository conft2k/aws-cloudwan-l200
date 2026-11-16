#!/usr/bin/env bash
# Run a command on a workshop EC2 instance and print what it said.
#
#   tools/ec2run.sh <instance-id> <region> '<command>'
#   tools/ec2run.sh i-0abc ap-northeast-2 'ping -c 5 10.20.1.10'
#
# The instances have no public address and no SSM agent role, so this goes the
# same way participants do: through the stack's EC2 Instance Connect Endpoint.
# It pushes a throwaway public key (valid for 60 seconds), opens a tunnel to
# port 22 and runs the command over SSH.
#
# Use it to put measured output in the workshop pages instead of a screenshot
# of a terminal: the pages already print the commands, so the output is what
# is missing. $AWS_PROFILE defaults to cwan.
set -euo pipefail

ID=${1:?instance id}
REGION=${2:?region}
CMD=${3:?command}
PROFILE=${AWS_PROFILE:-cwan}
USER_NAME=${EC2_USER:-ec2-user}
DIR=~/.cache/cwan-rehearsal
PORT=${EC2RUN_PORT:-0}

mkdir -p "$DIR"
[ -f "$DIR/key" ] || ssh-keygen -q -t ed25519 -N "" -f "$DIR/key" -C cwan-rehearsal

# a free local port, unless one was asked for
if [ "$PORT" = 0 ]; then
  PORT=$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1]);s.close()')
fi

aws ec2-instance-connect open-tunnel --profile "$PROFILE" --region "$REGION" \
  --instance-id "$ID" --remote-port 22 --local-port "$PORT" \
  > "$DIR/tunnel-$ID.log" 2>&1 &
TUNNEL=$!
trap 'kill "$TUNNEL" 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
  (exec 3<>/dev/tcp/127.0.0.1/"$PORT") 2>/dev/null && break
  sleep 1
done

# the pushed key only lasts 60 seconds, so push it right before connecting
aws ec2-instance-connect send-ssh-public-key --profile "$PROFILE" --region "$REGION" \
  --instance-id "$ID" --instance-os-user "$USER_NAME" \
  --ssh-public-key "file://$DIR/key.pub" --output text > /dev/null

ssh -q -i "$DIR/key" -p "$PORT" \
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ConnectTimeout=20 -o LogLevel=ERROR \
    "$USER_NAME@127.0.0.1" "$CMD"
