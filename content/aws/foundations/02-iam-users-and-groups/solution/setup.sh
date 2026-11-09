#!/usr/bin/env bash
# Lesson 2: IAM users, groups and the root user.
set -euo pipefail

# 1. The developers group, with the AWS managed policy ReadOnlyAccess.
aws iam create-group --group-name developers
aws iam attach-group-policy --group-name developers \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# 2. Users alice and bob, both in developers. Nothing attached to them directly.
for user in alice bob; do
  aws iam create-user --user-name "$user"
  aws iam add-user-to-group --group-name developers --user-name "$user"
done

# 3. The account password policy: 14 characters or more; symbols, numbers,
#    upper and lower case all required.
aws iam update-account-password-policy \
  --minimum-password-length 14 \
  --require-symbols --require-numbers \
  --require-uppercase-characters --require-lowercase-characters
