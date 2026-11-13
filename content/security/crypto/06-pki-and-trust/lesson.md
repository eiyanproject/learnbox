---
title: Certificates and the chain of trust
summary: The capstone - a certificate authority signs keys, verification walks the chain to a trusted root, and a valid signature from the wrong signer is rejected.
order: 6
files: [pki.py]
run: python pki.py
hints:
  - "`fingerprint`: hash a canonical string of the subject and its public key, `f\"{subject}|{n}|{e}\"`, with sha256; return the hex digest."
  - "`make_cert`: sign `int(fingerprint, 16) % issuer_n` with the issuer's private key (`pow(h, issuer_d, issuer_n)`), and store it in the cert dict under 'sig'."
  - "`verify_cert`: recompute the same `h` from the cert's own subject and key, and check `pow(cert['sig'], issuer_e, issuer_n) == h`."
  - "`verify_chain`: each cert must verify against the next one's key and name it as issuer; the last must be self-signed AND its fingerprint in `trusted`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **certificate** (public-key certificate) | a signed statement: "this public key belongs to this name" |
| **subject** | the name a certificate is about, such as `bank.example` |
| **issuer** | whoever signed the certificate |
| **certificate authority** (CA) | an organisation whose job is to check identities and sign certificates |
| **PKI** (public key infrastructure) | the whole system of CAs, certificates and trusted roots |
| **leaf certificate** | the certificate of the website itself, at the bottom of the chain |
| **intermediate CA** | a CA whose own certificate is signed by a root; it signs leaf certificates |
| **root CA** | the top of a chain; its certificate is self-signed |
| **self-signed** | signed with its own key: issuer and subject are the same |
| **chain of trust** | leaf, signed by intermediate, signed by root |
| **trusted root** (trust anchor) | a root certificate that your operating system or browser already trusts |
| **trust store** | the list of trusted roots shipped with your system or browser |
| **fingerprint** | a hash of a certificate's contents, used to identify it |
| **valid signature** | the maths checks out under the given key; says nothing about who owns that key |
| **trusted** | the chain ends at a root you already trust |
| **TLS** | the protocol behind `https://`: key exchange plus certificates |
| **toy key** | a key far too small to be safe, used so the numbers stay readable |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python pki.py` | runs your program: builds a root and a leaf certificate and checks the chain |
| `openssl x509 -in c.pem -noout -subject -issuer -dates` | shows a certificate's subject, issuer and validity dates |
| `openssl verify c.pem` | checks a certificate against the system's trusted roots |
| `openssl verify -CAfile root.pem c.pem` | checks it against the root(s) in `root.pem` instead |

### Python names

| Name | What it does |
|---|---|
| `keypair(p, q)` | given to you: a toy RSA key as a dict with `"n"`, `"e"` and `"d"` |
| `{"subject": ..., "sig": ...}` | a dict: values looked up by name, such as `cert["sig"]` |
| `f"{subject}\|{n}\|{e}"` | the three values joined into one string with `\|` between them |
| `int(hex_string, 16)` | a hex string read as a (very large) number |
| `% issuer_key["n"]` | reduced mod `n`, only because these toy keys are smaller than a hash |
| `pow(h, d, n)`, `pow(sig, e, n)` | sign with the private key; check with the public key (Crypto lesson 4) |
| `chain[i + 1]` | the next certificate up the chain |
| `chain[-1]` | the last item of the list: the root |
| `range(len(chain) - 1)` | each position except the last |
| `x in trusted` | `True` when `x` is in the set `trusted` |

---

Diffie-Hellman left one problem: you can agree on a key with someone, but not
know **who**. A **certificate** fixes that. It is a statement, "this public
key belongs to `bank.example`", **signed** by someone whose job is to check
such claims: a **certificate authority** (CA). This machinery is behind every
`https://` address.

## What a certificate contains

A certificate holds a **subject** (the name), the subject's **public key**,
the name of its **issuer**, and the issuer's **signature** over those
details. With the RSA signatures of lesson 4:

- the CA hashes `(subject, public key)` and signs the hash with the CA's
  **private** key;
- anyone checks the signature with the CA's **public** key.

If an attacker changes the name or swaps in their own key, the hash changes
and the signature no longer matches.

## The chain

Certificates come in a **chain**. Your bank's certificate (the **leaf**) is
signed by an **intermediate CA**. The intermediate's certificate is signed by
a **root CA**. The root's certificate is **self-signed**: it signs itself.

```text
leaf (bank.example)  --signed by-->  intermediate CA  --signed by-->  root CA
                                                                      (trusted)
```

A self-signature proves nothing about who you are, so why trust the root?
Because your operating system and browser already contain a list of
**trusted roots**, the **trust store**, chosen by their makers. The root is
trusted because it is on that list, not because of its signature.

## Where trust really comes from

Checking a chain means:

1. each certificate is correctly signed by the next one up, and names it as
   its issuer;
2. the last certificate is a correctly self-signed root;
3. that root is in your trust store.

Step 3 is the one that matters, and the one an attacker hopes you skip.
**A valid signature proves nothing on its own.** Anyone can make a key pair
and sign a certificate saying "I am `bank.example`". The signature checks out
perfectly against their own key. What stops them is that their certificate
is not in your trust store.

You can see this with OpenSSL. Here is a freshly made self-signed
certificate for `bank.example`, with subject and issuer the same:

```text
$ openssl x509 -in c.pem -noout -subject -issuer
subject=CN=bank.example
issuer=CN=bank.example
$ openssl verify c.pem
CN=bank.example
error 18 at 0 depth lookup: self-signed certificate
error c.pem: verification failed
```

Its signature is perfectly valid; it fails because nothing you trust vouches
for it. Tell OpenSSL to trust it, with `-CAfile c.pem`, and the same file
passes with `c.pem: OK`. Trust is a decision, not a property of the
signature. (`CN` is "common name", the classic field for the site's name.)

You will build the same check in Python, and watch it reject a
self-signed `bank.example` certificate that has a valid signature: valid is
not the same as trusted.

The keys here are the toy RSA keys of this section, and the hash is reduced
mod `n` because these keys are smaller than a SHA-256 digest. The structure
is exactly that of real PKI; the key sizes are not.

## Your turn

`keypair(p, q)` is given to you; it returns a dict with the keys `"n"`,
`"e"` and `"d"`. In `pki.py`:

- `fingerprint(subject, n, e)`: the SHA-256 hex digest of
  `f"{subject}|{n}|{e}"`.
- `make_cert(subject, subj_n, subj_e, issuer, issuer_key)`: a certificate
  dict with exactly these keys: `"subject"`, `"n"`, `"e"` (the subject's
  public key), `"issuer"` (the issuer's name) and `"sig"`. To make the
  signature:
  1. `h = int(fingerprint(subject, subj_n, subj_e), 16) % issuer_key["n"]`;
  2. `sig = pow(h, issuer_key["d"], issuer_key["n"])`.
- `verify_cert(cert, issuer_n, issuer_e)`: `True` when the signature checks
  out. Recompute `h` from the certificate's own fields, and compare it with
  `pow(cert["sig"], issuer_e, issuer_n)`.
- `verify_chain(chain, trusted)`: `chain` is a list of certificates from leaf
  to root, `trusted` a set of root fingerprints. Return `True` only when:
  - every certificate names the next one as its issuer, and verifies under
    the next one's key;
  - the last one verifies under its **own** key (self-signed);
  - and that root's fingerprint is in `trusted`.

Run it:

```text
chain trusted: True
```

## Check yourself

1. What does a certificate say, and who says it?
   *"This key belongs to this name", signed by the issuer.*
2. What is special about a root certificate?
   *It is self-signed, and trusted because it is in the trust store.*
3. An attacker signs their own certificate for `bank.example`. Does the
   signature verify?
   *Yes, under their own key.*
4. So what makes the browser reject it?
   *Its chain does not end at a trusted root.*
5. What must hold between each certificate and the next one in a chain?
   *It names the next as issuer and its signature verifies under the next
   one's public key.*
