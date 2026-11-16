"""Read, change and apply the core network policy.

    uv run --with boto3 python tools/policy.py show
    uv run --with boto3 python tools/policy.py share onprem prod
    uv run --with boto3 python tools/policy.py segment dev require-attachment-acceptance true
    uv run --with boto3 python tools/policy.py segment dev isolate-attachments true
    uv run --with boto3 python tools/policy.py execute <version>
    uv run --with boto3 python tools/policy.py wait <version>

Creating a policy version from here keeps the rehearsal on schedule; the
console screens that the workshop pages need (the editor, the change set, the
execution) are shot separately against the version this made. $AWS_PROFILE
defaults to demo1.

A new version is only created, never executed, unless you say `execute`: the
workshop's point is that a version does nothing until its change set runs.
"""
import json
import os
import sys
import time

import boto3

PROFILE = os.environ.get("AWS_PROFILE", "demo1")
REGION = os.environ.get("CWAN_HOME_REGION", "us-west-2")
nm = boto3.Session(profile_name=PROFILE, region_name=REGION).client("networkmanager")


def core_network_id() -> str:
    cns = nm.list_core_networks()["CoreNetworks"]
    if not cns:
        sys.exit("no core network in this account")
    return cns[0]["CoreNetworkId"]


CN = core_network_id()


def live_policy() -> dict:
    p = nm.get_core_network_policy(CoreNetworkId=CN, Alias="LIVE")["CoreNetworkPolicy"]
    return {"version": p["PolicyVersionId"], "doc": p["PolicyDocument"]}


def put(doc: dict, description: str) -> int:
    r = nm.put_core_network_policy(
        CoreNetworkId=CN, PolicyDocument=json.dumps(doc), Description=description)
    v = r["CoreNetworkPolicy"]["PolicyVersionId"]
    print(f"created policy version {v}: {description}")
    return v


def wait(version: int, want="READY_TO_EXECUTE", timeout=900) -> str:
    start = time.time()
    while time.time() - start < timeout:
        vs = nm.list_core_network_policy_versions(CoreNetworkId=CN)["CoreNetworkPolicyVersions"]
        st = next((v.get("ChangeSetState") for v in vs
                   if v["PolicyVersionId"] == int(version)), None)
        print(f"  version {version} change set: {st}")
        if st == want or st == "EXECUTION_SUCCEEDED":
            return st
        if st and "FAILED" in st:
            sys.exit(f"change set {st}")
        time.sleep(15)
    sys.exit("timed out waiting for the change set")


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "show":
        cur = live_policy()
        print(f"core network {CN}, LIVE version {cur['version']}")
        print(json.dumps(cur["doc"], indent=2))
        return
    if cmd == "share":
        seg, with_seg = sys.argv[2], sys.argv[3]
        cur = live_policy()
        doc = cur["doc"]
        doc.setdefault("segment-actions", []).append(
            {"action": "share", "mode": "attachment-route",
             "segment": seg, "share-with": [with_seg]})
        v = put(doc, f"Lab 2-4: share {seg} with {with_seg}")
        print(f"VERSION={v}")
        return
    if cmd == "segment":
        name, key, val = sys.argv[2], sys.argv[3], sys.argv[4].lower() == "true"
        cur = live_policy()
        doc = cur["doc"]
        for s in doc["segments"]:
            if s["name"] == name:
                if val:
                    s[key] = True
                else:
                    s.pop(key, None)
                break
        else:
            sys.exit(f"no segment {name}")
        v = put(doc, f"Extra 3-1: {name} {key}={str(val).lower()}")
        print(f"VERSION={v}")
        return
    if cmd == "execute":
        version = int(sys.argv[2])
        nm.execute_core_network_change_set(CoreNetworkId=CN, PolicyVersionId=version)
        print(f"executing change set for version {version}")
        print(wait(version, want="EXECUTION_SUCCEEDED"))
        return
    if cmd == "wait":
        print(wait(int(sys.argv[2])))
        return
    sys.exit(f"unknown command {cmd!r}")


if __name__ == "__main__":
    main()
