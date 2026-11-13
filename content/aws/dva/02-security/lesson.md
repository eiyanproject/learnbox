---
title: "Domain 2: Security"
summary: 26% of the exam. Authenticating users and calls, authorizing them finely, encrypting with KMS from code, and keeping secrets out of code and logs.
order: 2
kind: quiz
---

Security for a developer is three questions about every call: **who** is
calling (authentication), **what** may they do (authorization), and how are
the data and the secrets protected along the way. The exam asks them in
code terms: which authorizer checks this token, where the SDK finds
credentials, how to encrypt a 2 MB file with KMS.

**Weight: 26% of the scored questions.** Three tasks: authentication and
authorization, encryption, and sensitive data in application code.

## Who is calling

*Practised in Foundations lessons 3-4 and 8.*

- **Cognito user pools** are a user directory for your application: sign-up,
  sign-in, MFA, social and SAML logins. After sign-in they issue **JWTs**
  (JSON Web Tokens: an **ID token** describing the user and an **access
  token** for APIs). API Gateway verifies them with a **Cognito
  authorizer** (REST APIs) or a **JWT authorizer** (HTTP APIs), with no code.
- **Cognito identity pools** exchange a sign-in (from a user pool, Google,
  or even guests) for **temporary AWS credentials** of a role, so a mobile
  app can call S3 or DynamoDB directly.
- **Lambda authorizers** run your own code to validate anything else (a
  third-party OAuth token, a custom header) and return an IAM policy saying
  what the caller may invoke; results can be cached.
- **IAM authorization** on an API: callers sign each request with
  **SigV4** using AWS credentials, as the SDK does for every AWS call.
- The SDK's **default credential provider chain** looks, in order, at:
  1. credentials set explicitly in code;
  2. **environment variables** (`AWS_ACCESS_KEY_ID`...);
  3. the shared `~/.aws/config` and `credentials` files, including **IAM
     Identity Center** profiles;
  4. the container's credentials (ECS task role) or the **instance role**.

  ❗ It stops at the first it finds, so leftover environment variables
  **beat the role**: a common reason code uses the wrong permissions.
- **STS `AssumeRole`** returns temporary credentials for another role,
  including in another account.

| In a question | Answer |
|---|---|
| "users sign in; API must accept their tokens, no code" | Cognito user pool + Cognito (or JWT) authorizer |
| "mobile app uploads straight to S3 per user" | identity pool credentials |
| "validate a third-party token" | Lambda authorizer |
| "the app uses the wrong permissions on EC2" | environment variables or a credentials file overriding the role |

## Fine-grained authorization

- **Policy variables** fill in the caller at evaluation time:
  `arn:aws:s3:::bucket/home/${aws:username}/*` gives each IAM user their own
  prefix; `${cognito-identity.amazonaws.com:sub}` does the same for Cognito
  identities.
- **`dynamodb:LeadingKeys`** restricts a caller to items whose **partition
  key** equals their ID: one table shared by many tenants, each seeing only
  their own rows.
- **Resource-based policies**: a Lambda function's own policy (set with
  `add-permission`) allows S3, SNS, EventBridge or API Gateway to **invoke**
  it. "S3 events do not trigger the function" is often a missing
  permission there.

## Encryption from code

*Practised in Security lesson 1.*

- **KMS `Encrypt`** accepts at most **4 KB**. For anything bigger, use
  **envelope encryption**: `GenerateDataKey` returns a data key twice,
  plaintext and encrypted under the KMS key; encrypt the data **locally**
  with the plaintext key, discard it, and store the **encrypted** key next
  to the data. To read, `Decrypt` the data key, then decrypt locally. The
  **AWS Encryption SDK** does all of this for you.
- **Encryption context**: key-value pairs bound to the ciphertext; decrypt
  needs the same pairs, and they appear in CloudTrail.
- **Client-side** encryption: data is encrypted before it reaches AWS.
  **Server-side**: AWS encrypts it at rest (S3 SSE, DynamoDB, EBS).
- **ACM** for public certificates; **AWS Private CA** for internal ones.
- **KMS throttling**: SSE-KMS on a busy bucket calls KMS per object; **S3
  Bucket Keys** or data key caching reduce the calls.

## Secrets

*Practised in Security lesson 2.*

- **Secrets Manager**: storage, **rotation**, cross-account sharing.
  **Cache** secrets in the function (the extension or the caching library)
  instead of calling on every invocation: faster, and cheaper.
- **Parameter Store** `SecureString`: cheaper, no built-in rotation.
- Lambda **environment variables** are encrypted at rest; a customer
  managed key protects them further, and "encryption helpers" encrypt them
  client-side so even the console shows ciphertext.
- Keep secrets and personal data **out of logs**: CloudWatch Logs **data
  protection policies** detect and mask sensitive data.

| In a question | Answer |
|---|---|
| "encrypt a 1 GB file with KMS" | envelope encryption (`GenerateDataKey`) or the Encryption SDK |
| "database password must rotate automatically" | Secrets Manager |
| "configuration values, cheapest" | Parameter Store |
| "KMS ThrottlingException on S3 uploads" | S3 Bucket Keys |

## Traps

- **ID tokens** describe the user; **access tokens** authorize API calls.
- An **identity pool** does not sign users in; a **user pool** does.
- KMS `Encrypt` on data over 4 KB fails: envelope encryption.
- Hard-coded credentials are never the answer, even "encrypted".

Source: AWS Certified Developer - Associate (DVA-C02) exam guide, Content
Domain 2; AWS service documentation.

## Questions from open banks

- 2 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
