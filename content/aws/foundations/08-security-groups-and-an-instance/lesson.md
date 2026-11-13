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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **EC2** | Elastic Compute Cloud: virtual machines rented by the second |
| **instance** | one virtual machine |
| **port** | the number a network service listens on: 443 HTTPS, 22 SSH, 5432 PostgreSQL |
| **SSH** | the remote shell administrators log in with |
| **protocol** | the kind of traffic, such as TCP; `-1` means all |
| **source** | where allowed traffic may come from: a CIDR range or a security group |
| **firewall** | something that allows or blocks network traffic |
| **security group** | a firewall on a network interface; allow-only and stateful |
| **allow-only** | rules can only allow; whatever is not allowed is blocked |
| **stateful** | replies to allowed traffic go back automatically |
| **stateless** | replies need their own rule |
| **inbound** / **outbound** (ingress / egress) | traffic arriving / leaving |
| **group reference** | a rule whose source is another security group: "anything in `web`" |
| **default security group** | the VPC's own group, used if you name none |
| **network ACL** | a subnet-level filter: allow and deny rules, numbered, first match wins, stateless |
| **ephemeral ports** | 1024-65535: the ports replies come back to |
| **AMI** | Amazon Machine Image: the disk image an instance boots from |
| **instance type** | its size, such as `t3.micro` (family, generation, size) |
| **vCPU** | a virtual CPU |
| **GiB** | gibibyte: 1,024 MiB of memory |
| **Systems Manager Parameter Store** | a key-value store; AWS publishes the latest AMI IDs there |
| **instance profile** | how an instance holds a role (lesson 4) |
| **instance metadata** | facts and credentials an instance reads from `http://169.254.169.254/` |
| **IMDSv1** / **IMDSv2** | metadata by a plain request / only with a session token fetched by `PUT` |
| **server-side request forgery (SSRF)** | tricking an application into fetching a URL for an attacker |
| **Elastic IP** | a fixed public address you keep until released; billed |
| **EBS** | Elastic Block Store: an instance's disks |
| **root volume** | the boot disk; deleted with the instance by default |
| **reboot** / **stop** / **terminate** | restart / power off (keeps disks, new public IP on start) / delete |
| **key pair** | the keys for SSH login |
| **EC2 Instance Connect Endpoint** | SSH to private instances without a public IP |
| **Session Manager** | a shell through Systems Manager: no inbound port, controlled by IAM |
| **DHCP**, **Time Sync** | network address and clock services that security groups never filter |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `aws ec2 create-security-group --group-name N --description D --vpc-id V` | creates a group; prints its `sg-...` ID |
| `aws ec2 authorize-security-group-ingress --group-id G --protocol tcp --port 443 --cidr 0.0.0.0/0` | adds an inbound rule |
| `--source-group SG` | rule source: another security group, instead of `--cidr` |
| `aws ssm get-parameters --names /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64` | looks up the latest Amazon Linux 2023 AMI |
| `aws ec2 run-instances --image-id AMI --instance-type t3.micro --subnet-id S --security-group-ids G` | launches an instance |
| `--iam-instance-profile Name=web-server` | gives it the role |
| `--metadata-options HttpTokens=required` | requires IMDSv2 |
| `aws ec2 describe-security-groups --filters Name=group-name,Values=web,db` | shows the groups and their rules |
| `aws ec2 describe-instances --filters Name=tag:Name,Values=web` | shows the instance |
| `eval "$(awslab given web-server-role)"` | builds lesson 4's role and instance profile |

### Errors

| Error | Means |
|---|---|
| `InvalidPermission.Duplicate ... The specified rule already exists` | the same rule added twice |
| `401 Unauthorized` | an IMDS request without a token when IMDSv2 is required |

---

Last lesson's VPC decides where traffic *can* go. This lesson decides what
traffic is *allowed* to arrive at each server, and then puts a server in
the VPC: an **EC2** (Elastic Compute Cloud) **instance**, a virtual machine
you rent by the second. It ends the Foundations section by bringing the
pieces together: the VPC from lesson 7, the role from lesson 4, and
firewalls that let in only what is needed.

```text
 internet ──443 (HTTPS), from anywhere──────────┐
 office 203.0.113.0/24 ──22 (SSH)───────────────┤
                                                v
                                    [ security group web ]  instance "web" in public-a
                                                │
                                      5432 (PostgreSQL), only from members of "web"
                                                v
                                    [ security group db ]   (a database, later)
```

## Ports, in one paragraph

A server runs several network services at once, and each listens on a
numbered **port**: 443 for HTTPS, 22 for SSH (the remote shell
administrators log in with), 5432 for PostgreSQL. A firewall rule allows a
**protocol** (TCP here), a **port** and a **source**. Opening 22 to the
whole internet invites every password-guessing robot on it, which is why the
check refuses it.

## Security groups

A **security group** is a firewall attached to a network interface: an
instance, a database, a load balancer. Three properties define it:

- **Allow-only.** Its rules only ever allow; there is no deny rule.
  Whatever no rule allows is blocked.
- **Stateful.** If a request is allowed **in**, the reply goes back out
  automatically, with no rule of its own. The firewall remembers the
  connection.
- **Defaults.** A new group allows **no inbound** traffic and **all
  outbound** traffic. You can see the outbound rule it starts with: protocol
  `-1` (all) to `0.0.0.0/0`.

A rule's source can be an address range in CIDR notation, or **another
security group**. That second form is the one to use inside a VPC: "the
database accepts 5432 from anything in the `web` group" stays true however
many web servers come and go, and whatever their addresses. A rule with an
address range would need updating every time a server is replaced.

Security groups do not filter everything: traffic to the VPC's own DNS
resolver, DHCP, the instance metadata service and the Amazon Time Sync
service always gets through.

Creating a group returns its ID (`sg-...`), which the rule commands need:

```
WEB_SG=$(aws ec2 create-security-group --group-name web --description "web tier" \
  --vpc-id "$VPC_ID" --query GroupId --output text)
aws ec2 authorize-security-group-ingress --group-id "$WEB_SG" \
  --protocol tcp --port 443 --cidr 0.0.0.0/0
```

`--description` is required, and `--vpc-id` puts the group in your VPC (a
group belongs to one VPC). For a rule from another group, write
`--source-group "$WEB_SG"` instead of `--cidr`. Adding the same rule twice
is an error:
`InvalidPermission.Duplicate ... The specified rule already exists`.

## Network ACLs, for contrast

A **network ACL** (access control list) also filters traffic, but at the
boundary of a **subnet**, and works differently. The exam asks about the
difference often:

| | Security group | Network ACL |
|---|---|---|
| Attached to | a network interface (an instance, a database) | a subnet |
| Rules | allow only | allow **and deny**, in numbered order, first match wins |
| State | **stateful**: replies allowed automatically | **stateless**: replies need their own rule, usually the ephemeral ports 1024-65535 |
| Default | no inbound, all outbound | the VPC's default ACL allows everything |

Most designs leave network ACLs at their allow-all default and do the real
work in security groups; an ACL is the tool for **blocking** a specific
address range, which a security group cannot do (section 2, lesson 2).

## Launching an instance

An instance needs four things:

- an **AMI** (Amazon Machine Image): the disk image it boots from, with the
  operating system installed;
- an **instance type**: its size. `t3.micro` has 2 virtual CPUs and 1 GiB of
  memory; types are named family (`t3`), generation, and size (`micro`,
  `large`, ...);
- a **subnet**, which places it in a VPC and an AZ;
- its **security groups**;

and, ideally, a role.

AMI IDs differ per Region and change with every release, so never paste one
into a script: it will be stale, or wrong in another Region. AWS publishes
the current one for each of its operating systems in **Systems Manager
Parameter Store**, a key-value store, under a fixed name:

```
$ aws ssm get-parameters \
    --names /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
    --query 'Parameters[0].Value' --output text
ami-0d27e0fb3bac4d724
```

The name reads as "Amazon Linux 2023, default kernel, for x86-64
processors". Capture the result into a variable, like every other ID.

Two launch options are worth setting on every instance:

- **`--iam-instance-profile Name=web-server`** gives the instance the role
  from lesson 4, through its instance profile: AWS credentials for the code
  on it, without a key anywhere on disk.
- **`--metadata-options HttpTokens=required`** turns on **IMDSv2**, version
  2 of the instance metadata service. Code on an instance reads its
  metadata, including the role's temporary credentials, from the address
  `http://169.254.169.254/`. With IMDSv1, a single plain request is enough,
  so a web application tricked into fetching a URL for an attacker (a
  "server-side request forgery") can hand over the credentials. IMDSv2
  requires a session token fetched first with a `PUT` request (valid for 1
  second to 6 hours, as the caller asks), which such tricks usually cannot
  make. A new instance accepts **both** versions unless you require tokens;
  with `HttpTokens=required`, a request without a token gets `401
  Unauthorized`.

`run-instances` launches it; `--tag-specifications` names it as in lesson
7, with `ResourceType=instance`, and `--query 'Instances[0].InstanceId'
--output text` prints its ID.

## More about security groups and instances

- Every network interface must have **at least one** security group (up to
  five by default). Launch without naming one and the VPC's **default**
  group is used, which allows traffic from its own members.
- Being in the same security group does **not** let instances talk to each
  other; that needs a rule whose source is the group itself.
- Removing a rule does not cut connections that are already open; the
  group only judges new ones.

What survives what, for an instance:

| Action | Private IP | Auto-assigned public IP | Elastic IP | EBS disks |
|---|---|---|---|---|
| reboot | kept | kept | kept | kept |
| stop, then start | kept | **new address** | kept | kept |
| terminate | released | released | stays in the account, billed | root volume deleted by default |

Ways to get a shell on an instance, from least to most recommended:

| Method | Needs a public IP? | Inbound rule? |
|---|---|---|
| SSH with a key pair | yes | 22 from your address |
| EC2 Instance Connect Endpoint | no | 22 from the endpoint's group |
| **Systems Manager Session Manager** | no | **none**; audited and controlled by IAM |

## Your task

`setup.sh` starts by building lesson 7's VPC and lesson 4's `web-server`
role and instance profile, with `eval "$(awslab given vpc)"` and `eval
"$(awslab given web-server-role)"`. These set `VPC_ID`, `PUBLIC_A`,
`PUBLIC_B`, `PRIVATE_A` and `PRIVATE_B` for you to use. (`awslab given vpc
--show` prints the CLI commands it stands for.) Add:

1. a security group **`web`** in the VPC whose inbound rules are exactly
   two: TCP **443 from anywhere** (`0.0.0.0/0`), and TCP **22 only from
   203.0.113.0/24** (the office);
2. a security group **`db`** in the VPC whose only inbound rule is TCP
   **5432 from the `web` group**, with no address ranges at all;
3. **one** instance named **`web`**: the latest **Amazon Linux 2023** AMI
   looked up from Parameter Store (the check compares it with the published
   value), type **t3.micro**, in **public-a**, in the `web` group and no
   other, with the **`web-server`** instance profile and **IMDSv2
   required**.

After **Run**, check what you built:

```
aws ec2 describe-security-groups --filters Name=group-name,Values=web,db \
  --query 'SecurityGroups[].[GroupName,IpPermissions]'
aws ec2 describe-instances --filters Name=tag:Name,Values=web \
  --query 'Reservations[].Instances[].[InstanceId,InstanceType,MetadataOptions.HttpTokens]'
```

(The emulator records the instance as running, but no virtual machine
starts. In a real account it would, and t3.micro is billed while it runs.)

## Check yourself

1. A security group allows 443 in. Does the reply need an outbound rule?
   *No: security groups are stateful.*
2. Why reference the `web` group from the `db` group rather than the web
   servers' addresses?
   *The rule stays right however many web servers come and go.*
3. How do you block one bad address range with a security group?
   *You cannot: they only allow. Use a network ACL deny.*
4. Why look up the AMI in Parameter Store instead of pasting an ID?
   *AMI IDs differ per Region and change with every release.*
5. What does `HttpTokens=required` protect against?
   *Tricked web applications fetching the instance's role credentials from
   the metadata service with a single plain request.*
