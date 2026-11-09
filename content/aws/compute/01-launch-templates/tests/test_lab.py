import base64

import pytest

from awslab import lab


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def versions(acct):
    ec2 = acct.client("ec2")
    try:
        vs = ec2.describe_launch_template_versions(LaunchTemplateName="web")["LaunchTemplateVersions"]
    except ec2.exceptions.ClientError:
        pytest.fail("there is no launch template called web")
    return {v["VersionNumber"]: v for v in vs}


def v1(acct):
    vs = versions(acct)
    assert 1 in vs, "the launch template has no version 1"
    return vs[1]["LaunchTemplateData"]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_ami_type_and_group(acct):
    d = v1(acct)
    ami = acct.client("ssm").get_parameters(Names=["/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"])["Parameters"][0]["Value"]
    assert d.get("ImageId") == ami, f"version 1 uses {d.get('ImageId')}, not the Amazon Linux 2023 AMI ({ami})"
    assert d.get("InstanceType") == "t3.micro", f"version 1 should be t3.micro, not {d.get('InstanceType')}"
    web = acct.client("ec2").describe_security_groups(Filters=[{"Name": "group-name", "Values": ["web"]}])["SecurityGroups"][0]["GroupId"]
    assert d.get("SecurityGroupIds") == [web], "version 1 should use the web security group"


def test_role_and_imdsv2(acct):
    d = v1(acct)
    assert (d.get("IamInstanceProfile") or {}).get("Name") == "web-server" or (d.get("IamInstanceProfile") or {}).get("Arn", "").endswith("/web-server"), (
        "version 1 should give instances the web-server instance profile"
    )
    md = d.get("MetadataOptions") or {}
    assert md.get("HttpTokens") == "required", "IMDSv2 is not required"
    assert md.get("HttpPutResponseHopLimit") == 1, "the metadata hop limit should be 1, so containers on the instance cannot reach it"


def test_encrypted_gp3_root(acct):
    maps = {m["DeviceName"]: m for m in v1(acct).get("BlockDeviceMappings", [])}
    assert "/dev/xvda" in maps, "there is no block device mapping for /dev/xvda"
    ebs = maps["/dev/xvda"].get("Ebs", {})
    assert ebs.get("VolumeType") == "gp3", f"the root volume is {ebs.get('VolumeType')}, not gp3"
    assert ebs.get("VolumeSize") == 20, f"the root volume is {ebs.get('VolumeSize')} GiB, not 20"
    assert ebs.get("Encrypted") is True, "the root volume is not encrypted"


def test_user_data_installs_and_starts_nginx(acct):
    raw = v1(acct).get("UserData")
    assert raw, "version 1 has no user data"
    script = base64.b64decode(raw).decode(errors="replace")
    assert script.startswith("#!"), "user data should start with #!/bin/bash"
    assert "dnf install" in script and "nginx" in script, "user data should install nginx with dnf"
    assert "hello from learnbox" in script, "user data should write 'hello from learnbox' into the index page"
    assert "systemctl" in script and ("start" in script or "--now" in script), "user data should start nginx (systemctl enable --now nginx)"


def test_instances_are_tagged(acct):
    specs = {s["ResourceType"]: s for s in v1(acct).get("TagSpecifications", [])}
    tags = {t["Key"]: t["Value"] for t in specs.get("instance", {}).get("Tags", [])}
    assert tags.get("Name") == "web", "instances launched from the template should be tagged Name=web"


def test_version_2_is_t3_small_and_the_default(acct):
    vs = versions(acct)
    assert 2 in vs, "there is no version 2"
    assert vs[2]["LaunchTemplateData"].get("InstanceType") == "t3.small", "version 2 should be t3.small"
    default = [n for n, v in vs.items() if v.get("DefaultVersion")]
    assert default == [2], f"the default version is {default}, not 2"
