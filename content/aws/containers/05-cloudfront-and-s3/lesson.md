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

A website's files (HTML, CSS, JavaScript, images) sit in one bucket in one
Region. A visitor in Tokyo fetching them from us-east-1 waits for every
request to cross the Pacific, and the bucket would have to be **public**
for browsers to read it. **CloudFront**, AWS's **CDN** (content delivery
network), fixes both. Its hundreds of **edge locations** keep copies near
users, and it fetches from your bucket over the AWS network as the only
reader the bucket admits.

```text
 visitor ──HTTP──> edge ──301──> HTTPS ──> edge location (cache)
                                             │ hit: answer from the cache
                                             │ miss: fetch, signed with SigV4 (OAC)
                                             ▼
                                   bucket lb-site (Block Public Access on)
                                   bucket policy: only cloudfront.amazonaws.com,
                                                  only for THIS distribution's ARN
 anyone ──https://lb-site.s3...amazonaws.com/index.html──> 403 Access Denied
```

## Words first

- A **distribution** is one CloudFront configuration, reached at its own
  name, such as `d1234abcd.cloudfront.net` (or your own domain, through a
  Route 53 alias, as in the previous lesson).
- An **origin** is where the real content lives: an S3 bucket, an ALB, or
  any HTTP server. Each has an `Id` that behaviors refer to.
- An **edge location** answers viewers. On a **cache hit** it already has
  the file; on a **miss** it fetches it from the origin once and keeps it
  for later viewers.
- A **viewer** is the browser or client asking.

Besides speed, CloudFront terminates TLS at the edge, includes **Shield
Standard** DDoS protection, can attach AWS WAF, and can block countries
(**geo restriction**). 💸 Data sent from CloudFront to the internet is
usually cheaper than from S3 directly, and requests from CloudFront to an
S3 origin carry no data transfer charge.

## Keeping the bucket private: origin access control

The old way to host a site on S3 was **static website hosting** with a
public bucket. The bucket's contents are then open to anyone, and the
website endpoint speaks only HTTP. The current way keeps **Block Public
Access** on (Foundations lesson 6), and admits CloudFront alone:

1. An **origin access control** (OAC) makes CloudFront **sign** its
   requests to S3 with SigV4, like any AWS caller. `SigningBehavior always`
   signs every request. OAC replaces the older **origin access identity**
   (OAI); unlike an OAI, it works with SSE-KMS encrypted objects, with
   uploads, and in every Region. In the distribution, an origin using OAC
   still has an `S3OriginConfig`, with `OriginAccessIdentity` set to `""`.
2. The **bucket policy** lets the service principal
   `cloudfront.amazonaws.com` read objects, with a condition:

   ```json
   {"Effect": "Allow",
    "Principal": {"Service": "cloudfront.amazonaws.com"},
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::lb-site/*",
    "Condition": {"StringEquals": {"AWS:SourceArn": "arn:aws:cloudfront::ACCOUNT:distribution/DIST_ID"}}}
   ```

❗ Without the `AWS:SourceArn` condition, **every** CloudFront distribution
in every AWS account could read the bucket: the service principal is the
same for all of them. This is the confused-deputy problem from Foundations
lesson 4.

Two consequences worth knowing:

- The policy above allows only `s3:GetObject`, not `s3:ListBucket`, so a
  request for a file that does not exist gets **403 Access Denied** from S3,
  not 404 (S3 will not tell a caller who cannot list whether a key exists).
  A custom error response can turn it into a friendly page.
- If objects are encrypted with a customer managed KMS key, the **key
  policy** must also allow `cloudfront.amazonaws.com` to `kms:Decrypt`,
  with the same condition.

## The distribution

**Cache behaviors** match paths to origins. The **default** behavior
(`*`) catches everything; more can be added for patterns such as `/api/*`.
Each behavior sets:

- the **viewer protocol policy**: `allow-all`, `https-only`, or
  `redirect-to-https`, which answers plain HTTP with a 301 to the HTTPS
  address, so old links still work;
- a **cache policy**, deciding the **cache key** (which parts of a request
  make a different cached copy) and how long copies are kept;
- `Compress`: gzip or Brotli for text files, when the browser accepts it.

Use the **managed** cache policies rather than writing your own:

| Policy | ID | For |
|---|---|---|
| **CachingOptimized** | `658327ea-f89d-4fab-a63d-7e88639e58f6` | static files: cache key is the path only; kept a day by default, up to a year |
| **CachingDisabled** | `4135ea2d-6df8-44a3-9df3-4b5a84be39ad` | APIs and pages that differ per user |

An **origin request policy** separately decides which headers, cookies and
query strings reach the origin, without adding them to the cache key.
Fewer things in the key means more cache hits.

**Other settings:**

| Setting | What it does |
|---|---|
| **Price class** | `PriceClass_100`: only the cheapest edges (North America, Europe, Israel); `PriceClass_200` adds most others; `PriceClass_All`: every edge, fastest and most expensive. Viewers elsewhere are still served, from a farther edge. |
| **Default root object** | what a request for `/` returns, usually `index.html`. It applies to the root only, not to subfolders. |
| **Viewer certificate** | the default `*.cloudfront.net` certificate, or an ACM certificate for your own domain. ❗ The ACM certificate must be in **us-east-1**, whatever Region the content is in. |

A new or changed distribution takes a few minutes to reach every edge: its
`Status` goes from `InProgress` to `Deployed`.

## Updating content

Edges keep a cached file until its TTL ends, so a new `index.html` in the
bucket is not seen at once. Two ways:

| | **Versioned file names** (`app.3f9c.js`) | **Invalidation** (`/index.html`, `/*`) |
|---|---|---|
| How | each build writes new names; pages refer to the new ones | `create-invalidation` tells every edge to drop those paths |
| Speed | immediate: the new name has never been cached | usually within a minute or two |
| 💸 Cost | free | the first 1,000 paths a month free, then charged per path (`/*` counts as one) |

Build tools version the assets; the small `index.html` that names them is
then invalidated, or given a short TTL.

### CloudFront or Global Accelerator?

| | **CloudFront** | **Global Accelerator** |
|---|---|---|
| Caches | yes | no: it carries traffic to your application |
| Protocols | HTTP and HTTPS | any TCP or UDP |
| Addresses | changing, by DNS name | **two static anycast IPs** |
| Exam wording | "CDN", static content, global website | "static IP", UDP, gaming, fast Regional failover |

## Your task

1. A bucket **`lb-site`** with all four **Block Public Access** settings on,
   and an `index.html` (any content) uploaded with content type
   **`text/html`**.
2. An origin access control **`site-oac`**: signing protocol `sigv4`,
   signing behavior `always`, origin type `s3`.
3. A distribution created from a config file named **`dist.json`**, with:
   - comment **`lb-site`**, enabled, and a unique `CallerReference`;
   - one origin with the Id **`s3-site`** and domain
     `lb-site.s3.us-east-1.amazonaws.com`, using `site-oac`, with
     `S3OriginConfig.OriginAccessIdentity` empty;
   - default root object **`index.html`**;
   - a default cache behavior to `s3-site`: **redirect-to-https**, the
     **CachingOptimized** policy (by its ID), compression on;
   - **`PriceClass_100`**, and the default CloudFront certificate.

   (The emulator does not keep an origin's OAC, so the check reads that
   from `dist.json`; everything else it reads from the distribution.)
4. A bucket policy on `lb-site` whose only principal is
   `cloudfront.amazonaws.com`, allowing `s3:GetObject` on the bucket's
   objects, only when `AWS:SourceArn` is **this** distribution's ARN. The
   check confirms another distribution is refused, and that CloudFront
   cannot write (`s3:PutObject`).

After **Run**:

```
$ aws cloudfront list-distributions --query 'DistributionList.Items[].[Id,DomainName,Status,Comment]' --output text
JM4YMGV20ZAN5	udm4qpvx9o0ru.cloudfront.net	Deployed	lb-site
```

The ID and domain differ on each run. In AWS, `https://` that domain would
show the page, and the bucket's own URL would answer 403. The emulator
serves no edge, and does not apply Block Public Access to unsigned reads,
so try neither here.

## Check yourself

1. Why does the bucket policy need the `AWS:SourceArn` condition?
   *Every distribution, in every account, uses the principal
   `cloudfront.amazonaws.com`; the condition admits only yours.*
2. A visitor requests a file that is not in the bucket and gets 403, not
   404. Why?
   *Without `s3:ListBucket`, S3 does not reveal whether a key exists.*
3. You uploaded a new `style.css` under the same name, and visitors still
   get the old one. What are your options?
   *Invalidate `/style.css`, or, better, publish it under a new versioned
   name.*
4. Your ACM certificate for `www.example.com` is in eu-west-1, and
   CloudFront cannot use it. Why?
   *CloudFront uses certificates from us-east-1 only.*
5. Which cache policy for `/api/*`, which returns different data per user?
   *CachingDisabled.*
