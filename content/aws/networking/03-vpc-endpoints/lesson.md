---
title: VPC endpoints
summary: Reaching AWS services without the internet - a free gateway endpoint for S3 with a policy of its own, an interface endpoint for Systems Manager, and a bucket that only answers through the endpoint.
order: 3
files: [setup.sh, endpoint-policy.json, bucket-policy.json]
run: awslab run setup.sh
hints:
  - "Gateway endpoint: `aws ec2 create-vpc-endpoint --vpc-id \"$VPC_ID\" --service-name com.amazonaws.us-east-1.s3 --route-table-ids \"$PRIVATE_RT\" --policy-document file://endpoint-policy.json --query VpcEndpoint.VpcEndpointId --output text`."
  - "Interface endpoint: add `--vpc-endpoint-type Interface --subnet-ids \"$PRIVATE_A\" \"$PRIVATE_B\" --security-group-ids \"$EP_SG\" --private-dns-enabled`, with service name com.amazonaws.us-east-1.ssm."
  - "The endpoint's security group allows TCP 443 from the VPC's range, 10.0.0.0/16 - the instances talk to the endpoint's network interfaces over HTTPS."
  - "The bucket policy denies `s3:*` on the bucket and its objects to `\"Principal\": \"*\"` when `\"StringNotEquals\": {\"aws:SourceVpce\": \"vpce-...\"}`. Put the endpoint's real ID in: write the file from the script with the ID substituted, or use `sed`."
---

AWS services such as S3 and Systems Manager are reached at **public**
addresses (`s3.us-east-1.amazonaws.com`). So an instance in a private subnet
that reads from S3 normally goes out through a NAT gateway (lesson 1), onto
the internet, and back in to S3. It works, but the traffic leaves your
private network, and 💸 the NAT gateway charges for every gigabyte it
carries. For a job copying terabytes to S3, that is the largest line on the
bill.

A **VPC endpoint** gives the VPC a **private** path to an AWS service
instead, one that never touches the internet. There are two kinds, built
very differently:

| | Gateway endpoint | Interface endpoint (PrivateLink) |
|---|---|---|
| Services | **S3 and DynamoDB** only | almost every other service (SSM, Secrets Manager, KMS, STS, SQS, CloudWatch...) |
| How it works | a target in your **route tables** | **network interfaces** with private IPs in your subnets |
| Network security | route tables and the endpoint policy | a **security group** on the interfaces, plus the endpoint policy |
| 💸 Cost | **free** | per hour per AZ, plus per GB |
| Reachable from on-premises or a peered VPC | no | yes |

Exam questions about "reduce NAT gateway costs for S3 traffic" are almost
always answered by a gateway endpoint.

## Gateway endpoints

A gateway endpoint for S3 is attached to one or more **route tables**. AWS
then adds a route to each: destination, a **prefix list** (`pl-...`, a named
list of all of S3's address ranges in the Region, which AWS keeps up to
date), target, the endpoint:

```
$ aws ec2 describe-route-tables --filters Name=tag:Name,Values=private \
    --query 'RouteTables[0].Routes[].[DestinationCidrBlock,DestinationPrefixListId,GatewayId]' --output table
-------------------------------------------------------------------
|                       DescribeRouteTables                       |
+-------------+------------------------+--------------------------+
|  10.0.0.0/16|  None                  |  local                   |
|  None       |  pl-1e908183ac622c5b9  |  vpce-548573294c37b7eb7  |
+-------------+------------------------+--------------------------+
```

From then on, traffic from those subnets to S3 matches that more specific
route and goes through the endpoint, while other traffic still uses the
default route. Code does not change at all. Two limits: the endpoint only
carries traffic to S3 in the **same Region** (a bucket in another Region
still goes out by the default route), and a route table can hold only one
endpoint route per service.

### Endpoint policies

An endpoint can carry an **endpoint policy**: a policy saying what may pass
**through** it. The default allows everything (both kinds of endpoint have
one). A tight one lets the VPC
reach only your own buckets, which closes a data-exfiltration path: code
running on a compromised instance cannot copy your data to **its owner's**
bucket through the endpoint, because that bucket is not listed.

An endpoint policy is a resource policy, so its statements name a
`Principal` (`"*"` here, anyone in the VPC) as well as actions and
resources. It is the same JSON as before; for this lesson, allow the three
actions on the bucket's ARNs, remembering from Foundations lesson 3 that
`s3:ListBucket` acts on the bucket and the object actions on `bucket/*`.

## Interface endpoints (PrivateLink)

An interface endpoint puts a **network interface** (an ENI, elastic network
interface: a virtual network card with a private IP) in each subnet you
choose. Traffic to the service goes to those private IPs.

With **private DNS** on, the service's normal name
(`ssm.us-east-1.amazonaws.com`) resolves **inside the VPC** to those private
IPs, so the AWS CLI and SDKs on your instances find the endpoint with no
configuration change. With it off, code would still resolve the public
address and go out through the NAT gateway, ignoring the endpoint.

Because they are network interfaces, interface endpoints need a **security
group**, which must allow **HTTPS (TCP 443)** from the instances that use
them; allowing the VPC's whole range, `10.0.0.0/16`, is the usual rule.

Session Manager, part of Systems Manager (SSM), gives shell access to
instances with no SSH and no inbound port open. It works from private
subnets with no NAT gateway once three interface endpoints exist: `ssm`,
`ssmmessages` and `ec2messages`. This lesson makes the first.

## Locking a bucket to the endpoint

The endpoint policy controls what the VPC may reach. The other half is the
**bucket's** side: make the bucket refuse anything that did **not** come
through your endpoint. Requests through an endpoint carry the condition key
`aws:SourceVpce`, the endpoint's ID:

```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:*",
  "Resource": ["arn:aws:s3:::lb-private-data", "arn:aws:s3:::lb-private-data/*"],
  "Condition": { "StringNotEquals": { "aws:SourceVpce": "vpce-0123456789abcdef0" } }
}
```

Read it as "deny everyone everything on the bucket, **unless** the request
came through endpoint `vpce-0123...`". `StringNotEquals` is the "unless":
the Deny applies when the value is anything else, including when it is
missing because the request came over the internet.

⚠ Careful in real life: this also locks out the console and your own laptop,
since neither comes through the endpoint. Real policies usually exempt an
administrator role with a second condition.

### Putting the real ID in the file

The endpoint's ID only exists once the endpoint has been created, so the
policy file cannot be written in advance. One way: write the file with a
placeholder, and have the script fill it in with `sed`, a stream editor
that substitutes text:

```
sed "s/VPCE_ID/$S3_ENDPOINT/" bucket-policy.json > bucket-policy.final.json
aws s3api put-bucket-policy --bucket lb-private-data --policy file://bucket-policy.final.json
```

`s/VPCE_ID/.../` replaces `VPCE_ID` with the value of the shell variable;
the double quotes let the shell expand it. (Writing the whole file from the
script with a "here document", `cat > file <<EOF ... EOF`, works too.)

## More about endpoints

- A gateway endpoint does not change **DNS**: the S3 name still resolves to
  S3's public addresses, and the **route** to them is what changes. An
  interface endpoint works the other way round, through DNS.
- Gateway endpoints only work from **inside** the VPC. A data centre
  connected by VPN or Direct Connect, or a peered VPC, cannot use them; it
  needs an S3 **interface** endpoint.
- Common sets: Session Manager without NAT needs `ssm`, `ssmmessages` and
  `ec2messages`; pulling container images from ECR without NAT needs
  `ecr.api`, `ecr.dkr` **and** the S3 gateway endpoint, because the image
  layers are stored in S3.
- **PrivateLink** also lets you offer **your own** service to other VPCs and
  accounts, behind a Network Load Balancer. It is one-way, consumers to the
  service, and works even when the networks' address ranges overlap.

## Your task

The script builds the Foundations VPC, a **private route table** shared by
both private subnets (in `PRIVATE_RT`), and the bucket
**`lb-private-data`**. The two policy files start empty. Add:

1. **`endpoint-policy.json`**, allowing only `s3:GetObject`, `s3:PutObject`
   and `s3:ListBucket` on `lb-private-data` and its objects, for any
   principal. The check makes sure it allows those three, and refuses
   reading someone else's bucket and deleting this one.
2. **one** **gateway endpoint for S3** (`com.amazonaws.us-east-1.s3`) on the
   private route table, with that policy; keep its ID in a variable;
3. a security group **`endpoints`** whose only inbound rule is TCP 443 from
   `10.0.0.0/16`, and an **interface endpoint for SSM**
   (`com.amazonaws.us-east-1.ssm`) in **private-a and private-b**, using that
   group and no other, with **private DNS** on;
4. **`bucket-policy.json`**, denying `s3:*` to everyone on the bucket **and**
   its objects unless the request comes through **your S3 endpoint** (its
   real ID, not an example), applied to the bucket.

After **Run**, `aws ec2 describe-vpc-endpoints --query
'VpcEndpoints[].[VpcEndpointId,VpcEndpointType,ServiceName,State]' --output
table` lists both endpoints. (The emulator reports the gateway endpoint's
type as `None`; real AWS says `Gateway`.) The bucket policy bites at once:
your terminal is not inside the VPC, so its requests do not come through the
endpoint, and

```
$ aws s3 cp x.txt s3://lb-private-data/x.txt
upload failed: ./x.txt to s3://lb-private-data/x.txt An error occurred (403) when calling the PutObject operation: Forbidden
```

which is exactly the lock-out the warning above describes.

## Check yourself

1. Which services have gateway endpoints?
   *Only S3 and DynamoDB.*
2. How does each kind steer traffic?
   *Gateway: a route table entry (prefix list to the endpoint). Interface:
   network interfaces with private IPs, plus private DNS.*
3. Why does an interface endpoint need a security group allowing 443?
   *Clients talk to its network interfaces over HTTPS.*
4. A data centre needs private access to S3 over Direct Connect. Which
   endpoint?
   *An interface endpoint; gateway endpoints only serve the VPC itself.*
