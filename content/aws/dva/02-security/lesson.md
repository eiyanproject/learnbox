---
title: "Domain 2: Security"
summary: 26% of the exam. Authenticating users and calls, authorizing them finely, encrypting with KMS from code, and keeping secrets out of code and logs.
order: 2
kind: quiz
---

**Weight: 26% of the scored questions.** Three tasks: authentication and
authorization, encryption, and sensitive data in application code.

## Who is calling

- **Cognito user pools** sign users in and issue **JWTs** (ID and access
  tokens). API Gateway checks them with a **Cognito authorizer** (REST) or a
  **JWT authorizer** (HTTP APIs). **Identity pools** exchange a sign-in for
  temporary AWS credentials.
- **Lambda authorizers** validate anything else - a third-party OAuth
  token, an API key scheme - and return an IAM policy.
- **IAM authorization** on an API: callers sign requests with **SigV4**.
- The SDK's **default credential provider chain** looks, in order, at
  explicit settings, **environment variables**, the shared config/credentials
  files (including **IAM Identity Center** profiles), and then the container
  or **instance role**. Environment variables beat the role.
- **STS AssumeRole** returns temporary credentials for another role,
  including in another account.

## Fine-grained authorization

- **Policy variables**: `${aws:username}`, `${cognito-identity.amazonaws.com:sub}`
  scope a policy to the caller.
- **`dynamodb:LeadingKeys`** limits a user to items whose partition key is
  their ID - multi-tenant tables.
- **Resource-based policies**: a Lambda function's policy (`add-permission`)
  lets S3, SNS or EventBridge invoke it.

## Encryption from code

- **KMS `Encrypt`** takes at most **4 KB**. For anything bigger, use
  **envelope encryption**: `GenerateDataKey` returns a plaintext data key and
  the same key encrypted; encrypt locally with the plaintext key, discard it,
  store the encrypted key beside the data. The **AWS Encryption SDK** does
  this for you.
- **Client-side** encryption: data is encrypted before it reaches AWS.
  **Server-side**: AWS encrypts at rest.
- **AWS Private CA** for internal certificates; ACM for public ones.

## Secrets

- **Secrets Manager**: storage, rotation, cross-account sharing; cache
  secrets in the function rather than calling on every invocation.
- **Parameter Store** SecureString: cheaper, no built-in rotation.
- Lambda environment variables are encrypted at rest; a customer managed key
  and client-side "encryption helpers" protect them further.
- Keep secrets and personal data out of logs: CloudWatch Logs **data
  protection policies** can detect and mask sensitive data.

Source: AWS Certified Developer - Associate (DVA-C02) exam guide, Content
Domain 2; AWS service documentation.

## Questions from open banks

- 2 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
