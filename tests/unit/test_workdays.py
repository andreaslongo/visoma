import httpx
import pytest

from visoma.workdays import WorkdaysManager
import tests


def test_visoma_client(client):
    manager = client.workdays
    assert isinstance(manager, WorkdaysManager)


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_close(client, respx_mock):
    route_1 = respx_mock.get(
        f"https://{tests.VISOMA_HOST}/workend/index/date/2024-01-08"
    ).mock(httpx.Response(200, text="/workend/submitworkend/id/1/"))

    route_2 = respx_mock.get(
        f"https://{tests.VISOMA_HOST}/workend/submitworkend/id/1"
    ).mock(httpx.Response(302))

    client.workdays.close("2024-01-08")
    assert route_1.call_count == 1
    assert route_2.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_close_id_not_found(client, respx_mock):
    route_1 = respx_mock.get(
        f"https://{tests.VISOMA_HOST}/workend/index/date/2024-01-08"
    ).mock(httpx.Response(200))

    with pytest.raises(ValueError, match="Could not extract workday ID"):
        client.workdays.close("2024-01-08")
    assert route_1.call_count == 1
