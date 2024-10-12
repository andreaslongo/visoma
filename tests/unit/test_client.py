import pytest
import os

from visoma import VisomaClient
import tests


def test_missing_env_is_error():
    os.environ["VISOMA_HOST"] = ""
    os.environ["VISOMA_USER"] = ""
    os.environ["VISOMA_PASSWORD"] = ""
    with pytest.raises(ValueError, match="Missing values from env"):
        VisomaClient.from_env()


def test_context_manager():
    os.environ["VISOMA_HOST"] = tests.VISOMA_HOST
    os.environ["VISOMA_USER"] = tests.VISOMA_USER
    os.environ["VISOMA_PASSWORD"] = tests.VISOMA_PASSWORD

    with VisomaClient.from_env() as client:
        pass

    with pytest.raises(RuntimeError, match="client has been closed"):
        client.tickets.list()
