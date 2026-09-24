from netlab import build


def configured():
    lab, errors = build("one-router", {"R1": "r1.ios"})
    return lab, errors


def test_config_has_no_lines_ios_would_reject():
    _, errors = configured()
    assert errors == [], f"IOS would reject: {errors}"


def test_the_interface_has_the_right_address():
    lab, _ = configured()
    g0 = lab.device("R1").interface("GigabitEthernet0/0")
    assert g0.ip == "192.168.1.1", "GigabitEthernet0/0 needs the address 192.168.1.1"
    assert g0.mask == "255.255.255.0", "the mask should be 255.255.255.0"


def test_the_interface_is_not_shut():
    lab, _ = configured()
    assert not lab.device("R1").interface("GigabitEthernet0/0").shutdown, (
        "the interface is administratively down - it needs 'no shutdown'"
    )


def test_pc1_can_reach_the_router():
    lab, _ = configured()
    result = lab.ping("PC1", "R1")
    assert result.ok, f"PC1 cannot reach R1: {result.reason}"


def test_the_other_interface_is_left_alone():
    """This lesson is only about g0/0; g0/1 comes next."""
    lab, _ = configured()
    assert lab.device("R1").interface("GigabitEthernet0/1").ip is None
