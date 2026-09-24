from netlab import build

PROTECTED = ("FastEthernet0/1", "FastEthernet0/2")
UNPROTECTED = ("FastEthernet0/3", "FastEthernet0/4")


def configured():
    return build("switched", {"SW1": "sw1.ios"})


def test_config_is_accepted_by_ios():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_the_ports_are_access_ports_first():
    lab, _ = configured()
    sw = lab.device("SW1")
    for port in PROTECTED:
        assert sw.interface(port).mode == "access", (
            f"{port} must be an access port before port security can be enabled"
        )


def test_port_security_is_enabled_where_it_should_be():
    lab, _ = configured()
    sw = lab.device("SW1")
    for port in PROTECTED:
        assert sw.interface(port).port_security, f"{port} has no port security"


def test_the_maximum_is_one():
    lab, _ = configured()
    sw = lab.device("SW1")
    for port in PROTECTED:
        assert sw.interface(port).port_security_max == 1, f"{port} should allow one MAC address"


def test_the_violation_mode_is_restrict():
    lab, _ = configured()
    sw = lab.device("SW1")
    for port in PROTECTED:
        mode = sw.interface(port).port_security_violation
        assert mode == "restrict", (
            f"{port} is set to '{mode}' - shutdown would err-disable the port and need a site visit"
        )


def test_the_other_ports_were_left_alone():
    lab, _ = configured()
    sw = lab.device("SW1")
    for port in UNPROTECTED:
        assert not sw.interface(port).port_security, f"{port} should not have been configured"


def test_the_protected_ports_still_pass_traffic():
    """Port security does not block the device that is legitimately there."""
    lab, _ = configured()
    assert lab.ping("PC1", "PC2").ok
