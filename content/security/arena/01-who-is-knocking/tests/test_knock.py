from knock import suspects


def failed(second, ip, user="root", minute=0):
    return f"2026-03-04T10:{minute:02d}:{second:02d} FAILED user={user} ip={ip}"


def ok(second, ip, user="ana"):
    return f"2026-03-04T10:00:{second:02d} OK user={user} ip={ip}"


BURST = [failed(s, "203.0.113.9") for s in (7, 12, 20, 33, 40)]


def test_a_burst_is_a_suspect():
    assert suspects(BURST) == ["203.0.113.9"]


def test_four_is_not_five():
    assert suspects(BURST[:4]) == []


def test_slow_failures_are_not_a_burst():
    slow = [failed(0, "198.51.100.4", minute=m) for m in (0, 10, 20, 30, 40)]
    assert suspects(slow) == []


def test_the_window_is_inclusive():
    edge = [failed(0, "10.0.0.1"), failed(1, "10.0.0.1"), failed(2, "10.0.0.1"), failed(3, "10.0.0.1"),
            failed(0, "10.0.0.1", minute=1)]
    assert suspects(edge) == ["10.0.0.1"]
    late = edge[:4] + [failed(1, "10.0.0.1", minute=1)]
    assert suspects(late) == []


def test_the_burst_can_come_late():
    lines = [failed(0, "10.0.0.2", minute=0), failed(0, "10.0.0.2", minute=5)]
    lines += [failed(s, "10.0.0.2", minute=30) for s in (1, 2, 3, 4, 5)]
    assert suspects(lines) == ["10.0.0.2"]


def test_successes_do_not_count_and_do_not_reset():
    lines = BURST[:2] + [ok(15, "203.0.113.9")] + BURST[2:]
    assert suspects(lines) == ["203.0.113.9"]
    assert suspects([ok(s, "198.51.100.4") for s in range(10)]) == []


def test_counted_per_address_whatever_the_user():
    lines = [failed(s, "203.0.113.9", user=u) for s, u in enumerate(["root", "admin", "ana", "test", "pi"])]
    assert suspects(lines) == ["203.0.113.9"]
    spread = [failed(s, f"10.0.0.{s}") for s in range(1, 9)]
    assert suspects(spread) == []


def test_several_suspects_come_back_sorted():
    lines = []
    for s in range(5):
        lines.append(failed(s, "203.0.113.9"))
        lines.append(failed(s, "192.0.2.50"))
        lines.append(failed(s, "198.51.100.4") if s < 3 else ok(s, "198.51.100.4"))
    assert suspects(lines) == ["192.0.2.50", "203.0.113.9"]


def test_threshold_and_window_can_be_changed():
    assert suspects(BURST[:3], threshold=3) == ["203.0.113.9"]
    assert suspects(BURST, window=30) == []
    assert suspects(BURST, threshold=4, window=30) == ["203.0.113.9"]


def test_junk_lines_are_skipped():
    junk = ["", "# rotated", "2026-03-04T10:00:07 FAILED", "yesterday FAILED user=root ip=203.0.113.9",
            "2026-03-04T10:00:07 FAILED ip=203.0.113.9 user=root", "FAILED FAILED FAILED FAILED"]
    assert suspects(junk * 5) == []
    assert suspects(junk + BURST + junk) == ["203.0.113.9"]


def test_nothing_in_nothing_out():
    assert suspects([]) == []
