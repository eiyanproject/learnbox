---
title: Launch templates and user data
summary: Everything an instance needs written down once - AMI, type, role, IMDSv2, an encrypted gp3 disk and a boot script - and versioned so changes are deliberate.
order: 1
files: [setup.sh, user-data.sh, template.json]
run: awslab run setup.sh
hints:
  - "User data goes into a launch template base64-encoded: the script does `UD=$(base64 -w0 user-data.sh)` and puts it into the JSON with sed."
  - "In template.json: `\"BlockDeviceMappings\": [{\"DeviceName\": \"/dev/xvda\", \"Ebs\": {\"VolumeSize\": 20, \"VolumeType\": \"gp3\", \"Encrypted\": true, \"DeleteOnTermination\": true}}]`."
  - "`\"MetadataOptions\": {\"HttpTokens\": \"required\", \"HttpPutResponseHopLimit\": 1}` and `\"IamInstanceProfile\": {\"Name\": \"web-server\"}`."
  - "A new version: `aws ec2 create-launch-template-version --launch-template-name web --source-version 1 --launch-template-data '{\"InstanceType\":\"t3.small\"}'`, then `aws ec2 modify-launch-template --launch-template-name web --default-version 2`."
---

Foundations lesson 8 launched one instance with a long `run-instances`
command: AMI, type, subnet, security group, role, metadata options, tags.
Doing that by hand for every server does not scale, and two people typing it
will not type it the same way. A **launch template** writes all those
settings down **once**, under a name. Auto Scaling groups (lesson 3), Spot
Fleet and `run-instances` itself all launch from it, so every instance comes
out the same.

This section builds a web tier step by step: the template here, a load
balancer in lesson 2, and an Auto Scaling group that launches from this
template behind that load balancer in lesson 3.

## What a template holds

A template's **launch template data** is a JSON document with the same
fields as `run-instances`' options: `ImageId`, `InstanceType`,
`SecurityGroupIds`, `IamInstanceProfile`, `MetadataOptions`,
`BlockDeviceMappings`, `UserData`, `TagSpecifications`. Anything left out
must be given at launch time instead. It is created with:

```
aws ec2 create-launch-template --launch-template-name web \
  --launch-template-data file://template.final.json
```

## Versions

A template is **versioned**. You never edit a version: each change creates
a new, numbered one, and the old ones stay, so you can always see what
changed and go back. One version is the **default**.

```
aws ec2 create-launch-template-version --launch-template-name web \
  --source-version 1 --launch-template-data '{"InstanceType":"t3.small"}'
aws ec2 modify-launch-template --launch-template-name web --default-version 2
```

`--source-version 1` means "start from version 1's data"; the JSON given
then changes only what it names, here the instance type, and version 2 keeps
everything else from version 1. Without `--source-version`, version 2 would
hold *only* the instance type, and launch without an AMI.

Version 1 is the default when the template is created, and the default
only moves when you say so: creating version 2 does not change it. That is
why step 4 below needs `modify-launch-template`.

Whatever launches from the template chooses which version to use: a fixed
number, `$Latest` (the newest) or `$Default`. Following `$Default`, and
moving the default deliberately once a new version is tested, is the safe
habit: a half-finished new version does not reach production just by being
created.

```
$ aws ec2 describe-launch-template-versions --launch-template-name web \
    --query 'LaunchTemplateVersions[].[VersionNumber,DefaultVersion,LaunchTemplateData.InstanceType]' --output table
--------------------------------
|DescribeLaunchTemplateVersions|
+----+----------+--------------+
|  1 |  False   |  t3.micro    |
|  2 |  True    |  t3.small    |
+----+----------+--------------+
```

## User data

**User data** is a script the instance runs, as root, on its **first boot**
(through **cloud-init**, the program on the AMI that sets an instance up).
It is how an instance installs and configures itself, so nobody has to log
in to set it up, and a replacement instance comes up identical.

```bash
#!/bin/bash
set -euo pipefail
dnf install -y nginx                     # install the nginx web server
echo "hello from learnbox" > /usr/share/nginx/html/index.html
systemctl enable --now nginx             # start it now, and at every boot
```

`dnf` is Amazon Linux 2023's package manager (`-y` answers "yes" to its
questions, since nobody is there to answer); `systemctl enable --now` is
systemd's "start this service, and start it at every boot too". The first
line, `#!/bin/bash`, is required: it tells cloud-init this is a shell
script. Its output goes to `/var/log/cloud-init-output.log` on the instance,
the first place to look when a new instance comes up without its web
server.

Three limits and a rule:

- it runs **once**, on the first boot, not on every boot;
- it is limited to **16 KB**;
- the API takes it **base64-encoded**: converted to plain letters and
  digits, so it fits safely in JSON. `base64 -w0 user-data.sh` does that,
  on one line (`-w0` means "no line wrapping");
- ❗ **never put secrets in it**: anyone allowed to describe the instance
  can read it, in plain text. Fetch secrets at boot from Secrets Manager
  (section 7), using the instance's role.

## Disks

An instance's disks are **EBS** volumes (Elastic Block Store): network
disks that live separately from the instance. The **root volume**, the one
it boots from, is set in the template's **block device mappings**, under the
device name the AMI expects (`/dev/xvda` for Amazon Linux):

```json
"BlockDeviceMappings": [{
  "DeviceName": "/dev/xvda",
  "Ebs": { "VolumeSize": 20, "VolumeType": "gp3", "Encrypted": true, "DeleteOnTermination": true }
}]
```

- **gp3** is the current general-purpose SSD type: cheaper than the older
  gp2, with its speed (IOPS and throughput) set separately from its size
  instead of growing with it.
- **Encrypted** with the default EBS key. You can also turn on *EBS
  encryption by default* for the whole Region, so nothing unencrypted is
  ever created.
- **DeleteOnTermination** removes the volume with the instance; 💸
  otherwise each replaced instance leaves an orphan disk you keep paying
  for.

## The metadata hop limit

IMDSv2 (Foundations lesson 8) has one more setting. The **hop limit**,
`HttpPutResponseHopLimit`, is how many network hops the metadata token
response may travel. With **1**, only processes on the instance itself get
it; a container running on the instance, one hop further away, cannot reach
the instance's role credentials. (Container hosts that need it raise it to
2 deliberately.)

## Filling in the IDs

The template needs values only known when the script runs: the AMI ID and
the security group ID. The starter does what Networking lesson 3 did:
`template.json` holds placeholders (`AMI_ID`, `WEB_SG`, `USER_DATA`), and
this line replaces them, writing `template.final.json`:

```
sed -e "s/AMI_ID/$AMI_ID/" -e "s/WEB_SG/$WEB_SG/" -e "s|USER_DATA|$USER_DATA|" \
  template.json > template.final.json
```

(The last one uses `|` instead of `/` to separate the parts, because
base64 text can itself contain `/`.) So write the placeholders exactly as
they are in the starter, and create the template from
`template.final.json`.

## Related things worth knowing

- **Launch configurations**, the older way to describe instances for Auto
  Scaling, are deprecated and cannot be versioned; use launch templates.
- An AMI built with everything pre-installed boots ready to serve in
  seconds; an AMI plus a long user data script is more flexible but slower
  to scale out. Teams pick a point between the two.
- Some instance types have **instance store** disks, physically attached and
  fast, but their data is lost when the instance stops; EBS volumes keep
  their data.

## Your task

The script builds the VPC and the `web-server` role (`awslab given`), a
security group **web**, and reads the latest Amazon Linux 2023 AMI. Then:

1. write **`user-data.sh`**: keep the `#!/bin/bash` line, install nginx
   with `dnf`, write a page saying `hello from learnbox` to
   `/usr/share/nginx/html/index.html`, and enable and start nginx with
   `systemctl`;
2. write **`template.json`** with:
   - the AMI (`"ImageId": "AMI_ID"`, filled in by the script) and type
     **t3.micro**;
   - the **web** security group (`"SecurityGroupIds": ["WEB_SG"]`);
   - the **web-server** instance profile;
   - **IMDSv2 required**, with a **hop limit of 1**;
   - a **20 GiB encrypted gp3** root volume on `/dev/xvda`;
   - the user data (`"UserData": "USER_DATA"`);
   - instances tagged **Name=web** (a `TagSpecifications` entry with
     `"ResourceType": "instance"`);
3. create the launch template **`web`** from `template.final.json`;
4. create **version 2**, from version 1 but with instance type **t3.small**,
   and make it the **default**.

After **Run**, the table above shows both versions, with 2 as the default.
`aws ec2 describe-launch-template-versions --launch-template-name web
--versions 1` shows everything version 1 holds; its `UserData` is the
base64 text, which `base64 -d` turns back into your script.

## Check yourself

1. You edit a launch template. What actually happens?
   *A new version is created; earlier versions are unchanged.*
2. You create version 2. Do new instances use it?
   *Only if they ask for it, or `$Default` is moved to it.*
3. Why must secrets never go in user data?
   *Anyone who can describe the instance can read it.*
4. User data ran on the first boot. Does it run again after a reboot?
   *No, only on the first boot.*
