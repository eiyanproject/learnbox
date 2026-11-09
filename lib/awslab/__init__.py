"""awslab - the AWS lessons' sandbox: the real `aws` command against moto.

moto is an emulator of the AWS APIs. Pointed at it, the genuine AWS CLI
behaves as it would against an account - same commands, same JSON, same
errors - except that nothing leaves the box, nothing costs money, and the
"account" can be wiped and rebuilt in a second.

Two ways in:

  * Interactively. `aws ...` in the terminal goes through a wrapper that
    starts a private emulator on 127.0.0.1 the first time and keeps it
    running; `awslab reset` empties it and `awslab run setup.sh` rebuilds it
    from a lesson's script.

  * Graded. A lesson's test runs the learner's script against a fresh,
    throwaway emulator and inspects what it built:

        import pytest
        from awslab import lab

        @pytest.fixture(scope="module")
        def acct():
            with lab("setup.sh") as a:
                yield a

        def test_the_script_runs(acct):
            assert acct.ok, acct.failure()

        def test_the_bucket(acct):
            assert "my-bucket" in acct.bucket_names()

The emulator, the CLI and boto3 live in their own virtualenv
(LEARNBOX_AWS_VENV, /opt/learnbox-toolchain/aws by default), which is put on
sys.path here so the learner's own environment needs none of them.
"""

from __future__ import annotations

from ._venv import use_venv
from .account import Account, lab

__all__ = ["Account", "lab", "use_venv"]
