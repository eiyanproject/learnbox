from harden import findings, harden, is_hardened


def test_findings_flags_insecure():
    cfg = {"PermitRootLogin": "yes", "PasswordAuthentication": "yes", "Protocol": 2}
    assert findings(cfg) == ["PasswordAuthentication", "PermitRootLogin"]


def test_findings_none_when_clean():
    cfg = {"PermitRootLogin": "no", "Protocol": 2, "debug": False}
    assert findings(cfg) == []


def test_findings_ignores_absent_settings():
    assert findings({}) == []


def test_findings_catches_non_string_values():
    assert "Protocol" in findings({"Protocol": 1})
    assert "debug" in findings({"debug": True})


def test_harden_corrects_settings():
    cfg = {"PermitRootLogin": "yes", "debug": True}
    out = harden(cfg)
    assert out["PermitRootLogin"] == "no"
    assert out["debug"] is False


def test_harden_leaves_good_settings_alone():
    cfg = {"PermitRootLogin": "no", "Protocol": 2, "Banner": "/etc/issue"}
    assert harden(cfg) == cfg


def test_harden_does_not_mutate_input():
    cfg = {"PermitRootLogin": "yes"}
    harden(cfg)
    assert cfg["PermitRootLogin"] == "yes"


def test_is_hardened():
    assert is_hardened({"PermitRootLogin": "no", "Protocol": 2})
    assert not is_hardened({"PermitRootLogin": "yes"})


def test_harden_result_is_hardened():
    cfg = {"PermitRootLogin": "yes", "PasswordAuthentication": "yes", "Protocol": 1}
    assert is_hardened(harden(cfg))
