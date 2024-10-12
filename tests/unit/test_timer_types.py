import httpx
import pytest

from visoma.timer_types import TimerType
from visoma.timer_types import TimerTypesManager
import tests

FIRST_TIMER_TYPE = {
    "id": 1,
    "title": "Timer Type 1",
    "description": "The first timer type.",
}

SECOND_TIMER_TYPE = {
    "id": 2,
    "title": "Timer Type 2",
    "description": "The second timer type.",
}


def test_visoma_client(client):
    manager = client.timer_types
    assert isinstance(manager, TimerTypesManager)


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/timertype/search/").mock(
        httpx.Response(200, json=[FIRST_TIMER_TYPE])
    )

    actual = client.timer_types.get({"id": "1"})
    assert isinstance(actual, TimerType)
    assert actual.to_dict() == FIRST_TIMER_TYPE


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_not_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/timertype/search/").mock(
        httpx.Response(200, json={"Message": "No Timer Type found"})
    )

    with pytest.raises(ValueError, match="Timer type not found"):
        client.timer_types.get({"id": "1"})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_more_than_one_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/timertype/search/").mock(
        httpx.Response(200, json=[FIRST_TIMER_TYPE, SECOND_TIMER_TYPE])
    )

    with pytest.raises(ValueError, match="More than one timer type found"):
        client.timer_types.get({"active": True})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/timertype/search/").mock(
        httpx.Response(200, json=[FIRST_TIMER_TYPE, SECOND_TIMER_TYPE])
    )

    actual = client.timer_types.list()

    assert len(actual) == 2
    assert isinstance(actual[0], TimerType)
    assert actual[0].title == "Timer Type 1"
    assert isinstance(actual[1], TimerType)
    assert actual[1].title == "Timer Type 2"


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list_not_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/timertype/search/").mock(
        httpx.Response(200, json={"Message": "No Timer Type found"})
    )

    with pytest.raises(ValueError, match="No Timer Type found"):
        client.timer_types.list()
    assert route.call_count == 1
