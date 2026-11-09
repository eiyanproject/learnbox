"""Finding the virtualenv that holds the AWS CLI, boto3 and moto."""

from __future__ import annotations

import glob
import os
import sys

DEFAULT_VENV = "/opt/learnbox-toolchain/aws"

# The sandbox account. Not secrets: moto accepts any key, and these are the
# values its own documentation uses. Real credentials never belong here.
FAKE_CREDENTIALS = {
    "AWS_ACCESS_KEY_ID": "testing",
    "AWS_SECRET_ACCESS_KEY": "testing",
    "AWS_SESSION_TOKEN": "testing",
}
DEFAULT_REGION = "us-east-1"

# Settings for the emulator itself. AWS managed policies (ReadOnlyAccess,
# SecurityAudit, ...) are not loaded unless asked for, and the lessons attach
# them the way a real account would.
EMULATOR_ENV = {"MOTO_IAM_LOAD_MANAGED_POLICIES": "true"}


def venv() -> str:
    return os.environ.get("LEARNBOX_AWS_VENV", DEFAULT_VENV)


def venv_bin(name: str) -> str:
    return os.path.join(venv(), "bin", name)


def use_venv() -> None:
    """Make boto3 and moto importable from whatever Python is running.

    Appended rather than prepended, so a learner's own packages keep
    precedence in their own environment. The venv is built from the same
    system python3 as the learner's, so the compiled parts match.
    """
    for site in glob.glob(os.path.join(venv(), "lib", "python3*", "site-packages")):
        if site not in sys.path:
            sys.path.append(site)
    try:
        import boto3  # noqa: F401
    except ImportError as e:
        raise RuntimeError(
            f"the AWS tools are not installed (looked in {venv()}). "
            "They come with learnbox unless it was installed with --no-aws."
        ) from e


def sandbox_env(endpoint: str, base: dict[str, str] | None = None) -> dict[str, str]:
    """The environment that points the AWS CLI and boto3 at an emulator."""
    env = dict(os.environ if base is None else base)
    env.update(FAKE_CREDENTIALS)
    env["AWS_ENDPOINT_URL"] = endpoint
    env.setdefault("AWS_DEFAULT_REGION", DEFAULT_REGION)
    # No pager, no config files from the real world, no instance metadata.
    env["AWS_PAGER"] = ""
    env["AWS_CONFIG_FILE"] = os.devnull
    env["AWS_SHARED_CREDENTIALS_FILE"] = os.devnull
    env["AWS_EC2_METADATA_DISABLED"] = "true"
    env.pop("AWS_PROFILE", None)
    return env
