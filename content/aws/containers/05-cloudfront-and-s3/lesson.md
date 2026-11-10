---
title: CloudFront in front of a private bucket
summary: A static site served from a bucket nobody can reach directly - origin access control, a distribution that forces HTTPS and caches with a managed policy, and a bucket policy that admits only that one distribution.
order: 5
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "`OAC=$(aws cloudfront create-origin-access-control --origin-access-control-config Name=site-oac,SigningProtocol=sigv4,SigningBehavior=always,OriginAccessControlOriginType=s3 --query OriginAccessControl.Id --output text)`."
  - "Write the distribution config with python3 and `aws cloudfront create-distribution --distribution-config file://dist.json --query Distribution.ARN --output text`. The origin needs `\"OriginAccessControlId\": OAC` and `\"S3OriginConfig\": {\"OriginAccessIdentity\": \"\"}` (empty: OAC replaces the old OAI)."
  - "The default cache behavior: `\"TargetOriginId\"` matching the origin's Id, `\"ViewerProtocolPolicy\": \"redirect-to-https\"`, `\"CachePolicyId\": \"658327ea-f89d-4fab-a63d-7e88639e58f6\"` (CachingOptimized), `\"Compress\": true`."
  - "The bucket policy allows `\"Principal\": {\"Service\": \"cloudfront.amazonaws.com\"}` to `s3:GetObject` on `arn:aws:s3:::lb-site/*`, with `\"Condition\": {\"StringEquals\": {\"AWS:SourceArn\": \"<distribution ARN>\"}}`."
---

**CloudFront** is AWS's CDN: hundreds of edge locations that cache content
near users, terminate TLS, absorb DDoS attacks (Shield Standard is
included), and talk to your origin over the AWS network. For a static site
on S3 it is also how the bucket stays **private**.

## Origin access control

The old way to serve a bucket was static website hosting with a public
bucket. Now: keep **Block Public Access** on, and let only CloudFront in.

- An **origin access control** (OAC) makes CloudFront sign its requests to
  S3 with SigV4. (It replaces the older origin access identity, OAI, and
  also works with SSE-KMS buckets and PUT requests.)
- The **bucket policy** allows the service principal
  `cloudfront.amazonaws.com` to read objects **only** when `AWS:SourceArn`
  is your distribution's ARN - another customer's distribution with an OAC
  cannot read your bucket.

## The distribution

- **Origins** - where content comes from (S3, an ALB, any HTTP server),
  with an `Id` that cache behaviors refer to.
- **Cache behaviors** - by path pattern, which origin, which viewer
  protocols, which cache policy. The default behavior catches everything.
  `redirect-to-https` sends plain-HTTP viewers to HTTPS.
- **Cache policies** decide the cache key and TTLs. Use the managed ones:
  **CachingOptimized** for static content, **CachingDisabled** for APIs.
  Origin request policies decide what is forwarded without affecting the
  cache key.
- **Price class** - `PriceClass_100` uses only the cheapest edge locations
  (North America, Europe), `PriceClass_All` all of them.
- **Default root object** - what `/` serves, usually `index.html`.

Updating content: either version the file names (`app.3f9c.js`) or create
an **invalidation** - the first is free and instant, the second costs
beyond a monthly allowance and takes a minute or two.

## Your task

1. A bucket **`lb-site`** with all four **Block Public Access** settings
   on, and an `index.html` uploaded to it (any content, content type
   `text/html`).
2. An origin access control **`site-oac`**: SigV4, always sign, for S3.
3. A distribution created from a config file **`dist.json`**, comment
   **`lb-site`**, enabled: one S3 origin (Id
   **`s3-site`**, domain `lb-site.s3.us-east-1.amazonaws.com`) using the
   OAC; default root object **`index.html`**; default behavior
   **redirect-to-https**, the **CachingOptimized** managed cache policy,
   compression on; **`PriceClass_100`**; the default CloudFront
   certificate. (The emulator does not keep an origin's OAC, so the check
   reads that from `dist.json`; everything else it reads from the
   distribution.)
4. A bucket policy on `lb-site` allowing **only** `cloudfront.amazonaws.com`
   to `s3:GetObject`, and only for **this** distribution's ARN.

After **Run**: `aws cloudfront list-distributions --query
'DistributionList.Items[].DomainName'`.
