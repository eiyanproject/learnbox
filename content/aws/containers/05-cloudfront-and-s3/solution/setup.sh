#!/usr/bin/env bash
# Containers 5: CloudFront in front of a private bucket.
set -euo pipefail

printf '<!doctype html><title>lb-site</title><h1>Served by CloudFront</h1>\n' > index.html

# 1. Bucket lb-site, Block Public Access on, index.html uploaded as text/html.
aws s3api create-bucket --bucket lb-site >/dev/null
aws s3api put-public-access-block --bucket lb-site \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api put-object --bucket lb-site --key index.html --body index.html \
  --content-type text/html >/dev/null

# 2. Origin access control site-oac (sigv4, always, s3).
OAC=$(aws cloudfront create-origin-access-control --origin-access-control-config \
  Name=site-oac,SigningProtocol=sigv4,SigningBehavior=always,OriginAccessControlOriginType=s3 \
  --query OriginAccessControl.Id --output text)

# 3. The distribution.
python3 - "$OAC" "$(date +%s)" > dist.json <<'PY'
import json, sys
oac, ref = sys.argv[1:]
print(json.dumps({
    "CallerReference": f"lb-site-{ref}",
    "Comment": "lb-site",
    "Enabled": True,
    "DefaultRootObject": "index.html",
    "PriceClass": "PriceClass_100",
    "Origins": {"Quantity": 1, "Items": [{
        "Id": "s3-site",
        "DomainName": "lb-site.s3.us-east-1.amazonaws.com",
        "OriginAccessControlId": oac,
        "S3OriginConfig": {"OriginAccessIdentity": ""},
    }]},
    "DefaultCacheBehavior": {
        "TargetOriginId": "s3-site",
        "ViewerProtocolPolicy": "redirect-to-https",
        "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
        "Compress": True,
    },
    "ViewerCertificate": {"CloudFrontDefaultCertificate": True},
}, indent=2))
PY
DIST_ARN=$(aws cloudfront create-distribution --distribution-config file://dist.json \
  --query Distribution.ARN --output text)

# 4. Bucket policy: only cloudfront.amazonaws.com, only this distribution.
cat > site-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "CloudFrontRead",
    "Effect": "Allow",
    "Principal": {"Service": "cloudfront.amazonaws.com"},
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::lb-site/*",
    "Condition": {"StringEquals": {"AWS:SourceArn": "$DIST_ARN"}}
  }]
}
EOF
aws s3api put-bucket-policy --bucket lb-site --policy file://site-policy.json
