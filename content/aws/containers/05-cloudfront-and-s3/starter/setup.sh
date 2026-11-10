#!/usr/bin/env bash
# Containers 5: CloudFront in front of a private bucket.
set -euo pipefail

printf '<!doctype html><title>lb-site</title><h1>Served by CloudFront</h1>\n' > index.html

# 1. Bucket lb-site, Block Public Access on, index.html uploaded as text/html.


# 2. Origin access control site-oac (sigv4, always, s3).


# 3. The distribution, from dist.json: origin s3-site with the OAC, index.html,
#    redirect-to-https, CachingOptimized, compression, PriceClass_100.


# 4. Bucket policy: only cloudfront.amazonaws.com, only this distribution.

