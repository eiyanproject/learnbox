from pki import keypair, fingerprint, make_cert, verify_cert, verify_chain

ROOT = keypair(1009, 1013)
INTER = keypair(1019, 1031)
LEAF = keypair(1033, 1039)


def root_cert():
    return make_cert("root", ROOT["n"], ROOT["e"], "root", ROOT)


def inter_cert():
    return make_cert("intermediate", INTER["n"], INTER["e"], "root", ROOT)


def leaf_cert():
    return make_cert("bank.example", LEAF["n"], LEAF["e"], "intermediate", INTER)


TRUSTED = {fingerprint("root", ROOT["n"], ROOT["e"])}


def test_fingerprint_is_stable_hex():
    fp = fingerprint("bank.example", 1, 2)
    assert fp == fingerprint("bank.example", 1, 2)
    assert len(fp) == 64


def test_fingerprint_depends_on_key():
    assert fingerprint("bank.example", 1, 2) != fingerprint("bank.example", 9, 2)


def test_a_cert_verifies_under_its_issuer():
    assert verify_cert(leaf_cert(), INTER["n"], INTER["e"])


def test_a_cert_fails_under_the_wrong_key():
    assert not verify_cert(leaf_cert(), ROOT["n"], ROOT["e"])


def test_tampering_with_the_subject_breaks_it():
    c = leaf_cert()
    c["subject"] = "evil.example"
    assert not verify_cert(c, INTER["n"], INTER["e"])


def test_a_full_chain_is_trusted():
    assert verify_chain([leaf_cert(), inter_cert(), root_cert()], TRUSTED)


def test_chain_fails_if_root_not_trusted():
    assert not verify_chain([leaf_cert(), inter_cert(), root_cert()], set())


def test_self_signed_impostor_is_rejected():
    # An attacker makes their own key and self-signs a cert for bank.example.
    # The signature is internally valid; the root is not trusted, so it fails.
    evil = keypair(1049, 1051)
    impostor = make_cert("bank.example", evil["n"], evil["e"], "bank.example", evil)
    assert verify_cert(impostor, evil["n"], evil["e"])        # signature is valid...
    assert not verify_chain([impostor], TRUSTED)              # ...but not trusted


def test_broken_issuer_link_is_rejected():
    # Leaf claims 'intermediate' as issuer but is handed the root to verify against.
    assert not verify_chain([leaf_cert(), root_cert()], TRUSTED)
