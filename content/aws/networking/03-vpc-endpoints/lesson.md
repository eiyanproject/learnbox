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

An instance in a private subnet that reads from S3 normally goes out
through a NAT gateway and back in over S3's public endpoint. It works - but
the traffic leaves your network, and the NAT gateway charges for every
gigabyte. A **VPC endpoint** gives the VPC a private path to the service
instead.

## Gateway endpoints

For **S3 and DynamoDB** only. A gateway endpoint is a target in your route
tables: AWS adds routes for the service's address ranges (a *prefix list*)
pointing at it. Nothing to scale or secure at the network level, and **no
charge** - which is why "reduce NAT costs for S3 traffic" so often has this
answer.

An endpoint can carry an **endpoint policy**: a resource policy saying what
may pass through it. The default allows everything; a tight one lets the VPC
reach only your buckets, which closes a data-exfiltration path.

## Interface endpoints (PrivateLink)

For almost every other service - Systems Manager, Secrets Manager, KMS,
CloudWatch, STS, SQS... An interface endpoint puts **network interfaces with
private IPs** in your subnets. With **private DNS** on, the service's normal
name (`ssm.us-east-1.amazonaws.com`) resolves to those private IPs, so
existing code needs no change. They are billed per hour per AZ and per GB,
and they need a **security group** allowing HTTPS from the VPC.

Session Manager - shell access to instances with no SSH and no inbound port -
works from private subnets with no NAT once the `ssm`, `ssmmessages` and
`ec2messages` interface endpoints exist. This lesson makes the first.

## Locking a bucket to the endpoint

The other half: make the bucket refuse anything that did **not** come
through your endpoint, with the condition key `aws:SourceVpce`:

```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:*",
  "Resource": ["arn:aws:s3:::lb-private-data", "arn:aws:s3:::lb-private-data/*"],
  "Condition": { "StringNotEquals": { "aws:SourceVpce": "vpce-0123456789abcdef0" } }
}
```

(Careful in real life: this locks out the console and your own laptop too.
Real policies usually exempt an admin role.)

## Your task

The script builds the foundations VPC, a **private route table** shared by
both private subnets (`PRIVATE_RT`), and the bucket **`lb-private-data`**.
Add:

1. **`endpoint-policy.json`** allowing only `s3:GetObject`, `s3:PutObject`
   and `s3:ListBucket` on `lb-private-data` and its objects, for any
   principal;
2. a **gateway endpoint for S3** on the private route table, with that
   policy;
3. a security group **`endpoints`** allowing TCP 443 from 10.0.0.0/16, and an
   **interface endpoint for SSM** in both private subnets with it and
   **private DNS** on;
4. **`bucket-policy.json`** denying everything on the bucket unless it comes
   through **your S3 endpoint** - and apply it.
