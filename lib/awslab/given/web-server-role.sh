# The web-server role and instance profile from foundations lesson 4.
# What `eval "$(awslab given web-server-role)"` builds, written as the CLI commands it
# stands for (awslab does the same in one boto3 process, which is faster).
# Sets: WEB_ROLE_ARN
WEB_ROLE_ARN=$(aws iam create-role --role-name web-server --assume-role-policy-document \
  '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
  --query Role.Arn --output text)
aws iam attach-role-policy --role-name web-server \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
aws iam create-instance-profile --instance-profile-name web-server >/dev/null
aws iam add-role-to-instance-profile --instance-profile-name web-server --role-name web-server
echo "given web-server-role: $WEB_ROLE_ARN"
