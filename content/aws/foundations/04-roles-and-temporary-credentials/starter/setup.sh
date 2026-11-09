#!/usr/bin/env bash
# Lesson 4: roles and temporary credentials.
set -euo pipefail

# 1. The web-server role (trusting EC2, from ec2-trust.json), with
#    AmazonS3ReadOnlyAccess, and an instance profile web-server holding it.


# 2. The auditor role (trusting account 111122223333 with the external ID,
#    from auditor-trust.json), with SecurityAudit.

