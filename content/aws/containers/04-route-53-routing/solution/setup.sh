#!/usr/bin/env bash
# Containers 4: Route 53 routing.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"
REF=$(date +%s)

# 1. Public hosted zone example.com.
ZONE=$(aws route53 create-hosted-zone --name example.com \
  --caller-reference "$REF-public" --query HostedZone.Id --output text)

# 2. Health check: HTTPS 192.0.2.10:443 /health, 30 s, 3 failures.
HC=$(aws route53 create-health-check --caller-reference "$REF-hc" \
  --health-check-config IPAddress=192.0.2.10,Port=443,Type=HTTPS,ResourcePath=/health,RequestInterval=30,FailureThreshold=3 \
  --query HealthCheck.Id --output text)

# 3-5. Failover, weighted and latency records, in one change batch.
python3 - "$HC" > changes.json <<'PY'
import json, sys
hc = sys.argv[1]
def rec(name, ip, **extra):
    return {"Action": "CREATE", "ResourceRecordSet": {
        "Name": name, "Type": "A", "TTL": 60,
        "ResourceRecords": [{"Value": ip}], **extra}}
print(json.dumps({"Comment": "routing lesson", "Changes": [
    rec("app.example.com", "192.0.2.10", SetIdentifier="primary", Failover="PRIMARY", HealthCheckId=hc),
    rec("app.example.com", "198.51.100.10", SetIdentifier="secondary", Failover="SECONDARY"),
    rec("www.example.com", "192.0.2.20", SetIdentifier="blue", Weight=90),
    rec("www.example.com", "192.0.2.30", SetIdentifier="green", Weight=10),
    rec("api.example.com", "192.0.2.40", SetIdentifier="us-east-1", Region="us-east-1"),
    rec("api.example.com", "198.51.100.40", SetIdentifier="eu-west-1", Region="eu-west-1"),
]}, indent=2))
PY
aws route53 change-resource-record-sets --hosted-zone-id "$ZONE" \
  --change-batch file://changes.json >/dev/null

# 6. Private zone internal.example.com for the VPC (DNS hostnames on), and
#    the CNAME db.internal.example.com.
aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames '{"Value":true}'
PRIVATE_ZONE=$(aws route53 create-hosted-zone --name internal.example.com \
  --caller-reference "$REF-private" --vpc "VPCRegion=us-east-1,VPCId=$VPC_ID" \
  --hosted-zone-config PrivateZone=true --query HostedZone.Id --output text)
aws route53 change-resource-record-sets --hosted-zone-id "$PRIVATE_ZONE" --change-batch '{
  "Changes": [{"Action": "CREATE", "ResourceRecordSet": {
    "Name": "db.internal.example.com", "Type": "CNAME", "TTL": 300,
    "ResourceRecords": [{"Value": "orders.cluster-abc.us-east-1.rds.amazonaws.com"}]}}]
}' >/dev/null
