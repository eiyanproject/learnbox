import hashlib


def keypair(p, q, e=17):
    n = p * q
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    return {"n": n, "e": e, "d": d}


def fingerprint(subject, n, e):
    return hashlib.sha256(f"{subject}|{n}|{e}".encode()).hexdigest()


def make_cert(subject, subj_n, subj_e, issuer, issuer_key):
    # The issuer signs a hash of the subject's identity and key with its
    # private exponent. Reduced mod n because these toy keys are smaller than a
    # sha256 digest; real keys are not.
    h = int(fingerprint(subject, subj_n, subj_e), 16) % issuer_key["n"]
    sig = pow(h, issuer_key["d"], issuer_key["n"])
    return {"subject": subject, "n": subj_n, "e": subj_e, "issuer": issuer, "sig": sig}


def verify_cert(cert, issuer_n, issuer_e):
    # Recompute the hash from the cert's own fields and check the signature
    # undoes to it under the issuer's public key.
    h = int(fingerprint(cert["subject"], cert["n"], cert["e"]), 16) % issuer_n
    return pow(cert["sig"], issuer_e, issuer_n) == h


def verify_chain(chain, trusted):
    # Walk leaf to root. Every link must be signed by the next, and name it as
    # its issuer; the root must vouch for itself AND be independently trusted.
    for i in range(len(chain) - 1):
        issuer = chain[i + 1]
        if chain[i]["issuer"] != issuer["subject"]:
            return False
        if not verify_cert(chain[i], issuer["n"], issuer["e"]):
            return False
    root = chain[-1]
    if not verify_cert(root, root["n"], root["e"]):
        return False
    # The decisive step: a valid self-signature is worthless unless the root is
    # already trusted. This is what rejects an attacker's own certificate.
    return fingerprint(root["subject"], root["n"], root["e"]) in trusted


if __name__ == "__main__":
    root = keypair(1009, 1013)
    leaf = keypair(1019, 1031)
    root_cert = make_cert("root", root["n"], root["e"], "root", root)
    leaf_cert = make_cert("bank.example", leaf["n"], leaf["e"], "root", root)
    trusted = {fingerprint("root", root["n"], root["e"])}
    print("chain trusted:", verify_chain([leaf_cert, root_cert], trusted))
