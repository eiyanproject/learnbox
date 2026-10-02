from shellcmd import run_vulnerable, injection_payload, run_safe


def test_payload_executes_a_second_command():
    # 42 is the output of the injected `expr 6 * 7`, and is not in the payload.
    assert "42" not in injection_payload()
    assert "42" in run_vulnerable(injection_payload())


def test_safe_neutralises_the_payload():
    # No shell, so the second command never runs: 42 does not appear.
    assert "42" not in run_safe(injection_payload())


def test_safe_still_does_its_job():
    out = run_safe("example.com")
    assert "example.com" in out
    assert "pinging" in out


def test_safe_treats_metacharacters_as_text():
    # A payload with ; and backticks is echoed literally, not executed.
    out = run_safe("a; whoami")
    assert "whoami" in out       # printed as text...
    assert "42" not in out       # ...and no injected command ran
