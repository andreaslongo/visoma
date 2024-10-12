from attrs import define
import pytest

from visoma.http import HttpError
from visoma.http import handle_response


@define
class FakeResponse:
    status_code: int
    text: str


def test_error_response_is_error():
    with pytest.raises(HttpError, match="400: Some client error"):
        handle_response(FakeResponse(400, "Some client error"))

    with pytest.raises(HttpError, match="500: Some server error"):
        handle_response(FakeResponse(500, "Some server error"))


def test_redirect_response_is_nothing():
    assert handle_response(FakeResponse(303, "Some redirect")) is None


def test_success_response_is_something():
    assert handle_response(FakeResponse(200, "Something"), as_json=False) == "Something"
