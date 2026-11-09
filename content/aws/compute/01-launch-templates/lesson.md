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

Launching instances by hand with a dozen flags (lesson 8 of the
foundations) does not scale. A **launch template** writes the flags down
once - AMI, instance type, security groups, role, disks, metadata options,
user data, tags - and Auto Scaling groups, Spot Fleet and `run-instances`
all launch from it.

## Versions

A template is **versioned**. Each change creates a new version; one is the
**default**. An Auto Scaling group can follow `$Latest`, `$Default` or a
fixed number. Pinning to `$Default` and moving the default deliberately is
the safe habit: a half-finished edit does not reach production by itself.

## User data

**User data** is a script the instance runs as root on its **first boot**
(through cloud-init). It is how an instance installs and configures itself,
so nobody logs in to set it up. It is limited to 16 KB and stored
base64-encoded. Never put secrets in it: anyone who can describe the
instance can read it. Fetch secrets at boot from Secrets Manager, with the
instance's role.

## Disks

The root volume is defined in **block device mappings**. Make it **gp3**
(cheaper than gp2, IOPS and throughput set separately) and **encrypted**.
(You can also turn on *EBS encryption by default* for the whole Region, so
nothing unencrypted is ever created.)

## Your task

The script builds the VPC and the `web-server` role (`awslab given`), a
security group **web**, and reads the latest Amazon Linux 2023 AMI. Then:

1. write **`user-data.sh`**: install nginx with `dnf`, enable and start it,
   and write a page saying `hello from learnbox` to
   `/usr/share/nginx/html/index.html`;
2. write **`template.json`**: the AMI (the script substitutes `AMI_ID`),
   **t3.micro**, the **web** security group (`WEB_SG`), the **web-server**
   instance profile, **IMDSv2 required with a hop limit of 1**, a **20 GiB
   encrypted gp3** root volume on `/dev/xvda`, the user data (`USER_DATA`),
   and instances tagged **Name=web**;
3. create the launch template **`web`** from it;
4. create **version 2** with instance type **t3.small** and make it the
   **default**.

After **Run**: `aws ec2 describe-launch-template-versions --launch-template-name
web --query 'LaunchTemplateVersions[].[VersionNumber,DefaultVersion,
LaunchTemplateData.InstanceType]' --output table`.
