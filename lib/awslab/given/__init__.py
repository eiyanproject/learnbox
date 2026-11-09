"""Ready-made setups that later lessons build on.

Each is the end state of an earlier lesson. `awslab given vpc` builds it in
the current sandbox with boto3 - one process instead of a dozen CLI calls -
and prints shell assignments for the IDs, so a lesson script can say

    eval "$(awslab given vpc)"

`awslab given vpc --show` prints the same setup as the AWS CLI commands it
stands for (the .sh file beside this one), to read.
"""

from __future__ import annotations

import json
import os
import shlex

HERE = os.path.dirname(os.path.abspath(__file__))


def names() -> list[str]:
    return sorted(f[:-3] for f in os.listdir(HERE) if f.endswith(".sh"))


def show(name: str) -> str:
    with open(os.path.join(HERE, name + ".sh")) as f:
        return f.read()


def _tag(kind: str, name: str) -> list[dict]:
    return [{"ResourceType": kind, "Tags": [{"Key": "Name", "Value": name}]}]


def vpc(client) -> dict[str, str]:
    ec2 = client("ec2")
    vpc_id = ec2.create_vpc(CidrBlock="10.0.0.0/16", TagSpecifications=_tag("vpc", "lb-vpc"))["Vpc"]["VpcId"]
    out = {"VPC_ID": vpc_id}
    for name, cidr, az in [
        ("public-a", "10.0.1.0/24", "us-east-1a"),
        ("public-b", "10.0.2.0/24", "us-east-1b"),
        ("private-a", "10.0.11.0/24", "us-east-1a"),
        ("private-b", "10.0.12.0/24", "us-east-1b"),
    ]:
        sid = ec2.create_subnet(VpcId=vpc_id, CidrBlock=cidr, AvailabilityZone=az, TagSpecifications=_tag("subnet", name))["Subnet"]["SubnetId"]
        out[name.upper().replace("-", "_")] = sid
    igw = ec2.create_internet_gateway(TagSpecifications=_tag("internet-gateway", "lb-igw"))["InternetGateway"]["InternetGatewayId"]
    ec2.attach_internet_gateway(InternetGatewayId=igw, VpcId=vpc_id)
    rt = ec2.create_route_table(VpcId=vpc_id, TagSpecifications=_tag("route-table", "public"))["RouteTable"]["RouteTableId"]
    ec2.create_route(RouteTableId=rt, DestinationCidrBlock="0.0.0.0/0", GatewayId=igw)
    for key in ("PUBLIC_A", "PUBLIC_B"):
        ec2.associate_route_table(RouteTableId=rt, SubnetId=out[key])
        ec2.modify_subnet_attribute(SubnetId=out[key], MapPublicIpOnLaunch={"Value": True})
    out.update(IGW_ID=igw, PUBLIC_RT=rt)
    return out


def web_server_role(client) -> dict[str, str]:
    iam = client("iam")
    trust = {
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}],
    }
    arn = iam.create_role(RoleName="web-server", AssumeRolePolicyDocument=json.dumps(trust))["Role"]["Arn"]
    iam.attach_role_policy(RoleName="web-server", PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
    iam.create_instance_profile(InstanceProfileName="web-server")
    iam.add_role_to_instance_profile(InstanceProfileName="web-server", RoleName="web-server")
    return {"WEB_ROLE_ARN": arn}


BUILDERS = {"vpc": vpc, "web-server-role": web_server_role}


def build(name: str, endpoint: str, region: str) -> str:
    """Build a setup and return the shell assignments for its IDs."""
    import boto3

    def client(service: str):
        return boto3.client(
            service,
            endpoint_url=endpoint,
            region_name=region,
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
            aws_session_token="testing",
        )

    ids = BUILDERS[name](client)
    lines = [f"{k}={shlex.quote(v)}" for k, v in ids.items()]
    lines.append(f"echo {shlex.quote('given ' + name + ': ' + ' '.join(f'{k}={v}' for k, v in ids.items()))} >&2")
    return "\n".join(lines) + "\n"
