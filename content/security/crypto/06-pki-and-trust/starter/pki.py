import hashlib


def keypair(p, q, e=17):
    n = p * q
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    return {"n": n, "e": e, "d": d}


def fingerprint(subject, n, e):
    pass


def make_cert(subject, subj_n, subj_e, issuer, issuer_key):
    pass


def verify_cert(cert, issuer_n, issuer_e):
    pass


def verify_chain(chain, trusted):
    pass


if __name__ == "__main__":
    root = keypair(1009, 1013)
    leaf = keypair(1019, 1031)
    root_cert = make_cert("root", root["n"], root["e"], "root", root)
    leaf_cert = make_cert("bank.example", leaf["n"], leaf["e"], "root", root)
    trusted = {fingerprint("root", root["n"], root["e"])}
    print("chain trusted:", verify_chain([leaf_cert, root_cert], trusted))
