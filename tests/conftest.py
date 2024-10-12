import os
import pytest

from visoma import VisomaClient
import tests


@pytest.fixture
def client():
    os.environ["VISOMA_HOST"] = tests.VISOMA_HOST
    os.environ["VISOMA_USER"] = tests.VISOMA_USER
    os.environ["VISOMA_PASSWORD"] = tests.VISOMA_PASSWORD
    client = VisomaClient.from_env()
    yield client
    client.close()
