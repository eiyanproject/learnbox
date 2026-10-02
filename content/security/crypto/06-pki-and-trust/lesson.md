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

Diffie-Hellman left us needing to bind a key to an *identity*. That is what a
**public-key certificate** does: it is a statement - "this public key belongs to
`bank.example`" - **signed** by someone whose job is to vouch for it, a
**certificate authority** (CA). This is the machinery behind every `https://`.

## The structure

A certificate carries a subject's name and public key, plus a signature from its
**issuer** over those details. Using the RSA signing from the earlier lesson:

- The CA signs a hash of `(subject, public key)` with the CA's **private** key.
- Anyone verifies it with the CA's **public** key.

Certificates form a **chain**: your bank's certificate is signed by an
intermediate CA, whose certificate is signed by a root CA. The root is
**self-signed** - it vouches for itself - and is trusted not because of its
signature but because its fingerprint is baked into your operating system and
browser as a **trusted root**.

```text
leaf (bank.example)  --signed by-->  intermediate CA  --signed by-->  root CA
                                                                      (trusted)
```

## Where trust actually comes from

Verification walks that chain: each certificate must be correctly signed by the
next, and the chain must end at a root you already trust. The crucial point -
and the one attackers exploit - is the last step. **A valid signature proves
nothing on its own.** Anyone can generate a key pair and sign their own
certificate claiming to be `bank.example`; the signature will verify against
their own key perfectly. What stops them is that their root is not in your
trusted set. Trust is anchored, not conjured from a signature.

You will build this, and then watch it reject a technically-valid self-signed
certificate for `bank.example` - because valid is not the same as trusted.

> Uses the textbook RSA from this section, with tiny keys and the hash reduced
> mod n. The structure is exactly real PKI; the key sizes are not.

## Your turn

`keypair(p, q)` is provided. In `pki.py`:

- `fingerprint(subject, n, e)` - the sha256 hex of `f"{subject}|{n}|{e}"`
- `make_cert(subject, subj_n, subj_e, issuer, issuer_key)` - a cert dict with a
  `sig` from the issuer's private key; `issuer` is the issuer's subject name
- `verify_cert(cert, issuer_n, issuer_e)` - is the signature valid for this
  issuer key?
- `verify_chain(chain, trusted)` - leaf-to-root list; each signed by the next,
  the root self-signed and its fingerprint in `trusted`
