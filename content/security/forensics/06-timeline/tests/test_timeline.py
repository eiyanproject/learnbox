from timeline import merge, sequence, dwell_time

FW = [("2026-01-02T03:00:00", "fw", "port scan")]
AUTH = [("2026-01-02T03:05:00", "sshd", "login succeeded")]
FILES = [("2026-01-02T03:20:00", "nfs", "bulk file access")]
PROXY = [("2026-01-02T03:35:00", "proxy", "large upload offsite")]


def test_merge_combines_and_sorts():
    out = merge([FILES, FW, PROXY, AUTH])
    times = [e[0] for e in out]
    assert times == sorted(times)
    assert len(out) == 4


def test_merge_preserves_fields():
    out = merge([FW])
    assert out[0] == ("2026-01-02T03:00:00", "fw", "port scan")


def test_sequence_is_the_story_in_order():
    assert sequence([FILES, FW, PROXY, AUTH]) == [
        "port scan", "login succeeded", "bulk file access", "large upload offsite",
    ]


def test_sequence_single_source():
    assert sequence([AUTH]) == ["login succeeded"]


def test_dwell_time_spans_first_to_last():
    # 03:00:00 to 03:35:00 is 35 minutes.
    assert dwell_time([FILES, FW, PROXY, AUTH]) == 35 * 60


def test_dwell_time_single_event_is_zero():
    assert dwell_time([FW]) == 0


def test_dwell_time_empty_is_zero():
    assert dwell_time([]) == 0


def test_merge_empty_sources():
    assert merge([[], []]) == []
