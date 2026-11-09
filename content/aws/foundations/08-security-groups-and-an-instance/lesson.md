---
title: Security groups and an instance
summary: Stateful firewalls that reference each other, the latest Amazon Linux AMI from Parameter Store, and an instance launched with a role, IMDSv2 and nothing open to the world it does not need.
order: 8
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "`aws ec2 create-security-group --group-name web --description \"web tier\" --vpc-id \"$VPC_ID\" --query GroupId --output text`."
  - "HTTPS from anywhere: `aws ec2 authorize-security-group-ingress --group-id \"$WEB_SG\" --protocol tcp --port 443 --cidr 0.0.0.0/0`. SSH only from the office: the same with `--port 22 --cidr 203.0.113.0/24`."
  - "To allow traffic from another security group rather than an address range, use `--source-group \"$WEB_SG\"` instead of `--cidr`."
  - "`aws ssm get-parameters --names /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query 'Parameters[0].Value' --output text` prints the AMI ID. Launch with `--iam-instance-profile Name=web-server --metadata-options HttpTokens=required`."
---

## Security groups

A **security group** is a firewall around a network interface - an
instance, a database, a load balancer. Its rules only ever **allow**; there
is no deny rule. And it is **stateful**: if a request is allowed in, the
reply goes out without a rule of its own.

A rule's source can be a CIDR range or **another security group**. That
second form is the one to reach for inside a VPC: "the database accepts
5432 from anything in the `web` group" stays true however many web servers
come and go, and whatever their addresses.

New groups allow all outbound traffic and no inbound.

## Network ACLs, for contrast

A **network ACL** filters at the subnet boundary instead. It is
**stateless** (replies need their own rule, usually the ephemeral ports
1024-65535), its numbered rules are evaluated in order, and it **can deny** -
which makes it the tool for blocking a specific address range. Most designs
leave NACLs at their allow-all default and do the real work in security
groups.

## Launching an instance

An instance needs an **AMI** (the disk image), an **instance type**
(`t3.micro`: 2 vCPUs, 1 GiB), a subnet, security groups - and ideally a role.

AMI IDs differ per Region and change with every release, so do not paste
one in. AWS publishes the latest in **Systems Manager Parameter Store**:

```
aws ssm get-parameters \
  --names /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query 'Parameters[0].Value' --output text
```

Two launch options worth always setting:

- `--iam-instance-profile Name=web-server` gives the instance the role from
  lesson 4: AWS credentials without a key anywhere on disk.
- `--metadata-options HttpTokens=required` turns on **IMDSv2**: code on the
  instance must fetch a session token before reading metadata (and the
  role's credentials). It blunts a whole class of attacks where a tricked web
  app fetches `http://169.254.169.254/...` on an attacker's behalf.

## Your task

`setup.sh` already builds lesson 7's VPC and lesson 4's `web-server` role and
instance profile. Add:

1. a security group **`web`** allowing **443 from anywhere** and **22 only
   from 203.0.113.0/24** (the office);
2. a security group **`db`** allowing **5432 (PostgreSQL) only from the
   `web` group** - no address ranges at all;
3. an instance named **`web`**: the latest **Amazon Linux 2023** AMI from
   Parameter Store, **t3.micro**, in **public-a**, in the `web` group, with
   the **`web-server`** instance profile and **IMDSv2 required**.
