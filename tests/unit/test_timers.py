import httpx
import json
import pytest

from visoma.lib import VisomaResponse
from visoma.timers import Timer
from visoma.timers import TimerRequest
from visoma.timers import TimersManager
import tests

FIRST_TIMER = {
    "Id": 1,
    "UserId": 1,
    "User": "user-1",
    "Start": "2024-01-01 00:00:00",
    "Stop": "2024-01-01 02:30:00",
    "Description": "The first test timer.",
}

SECOND_TIMER = {
    "Id": 2,
    "UserId": 1,
    "User": "user-1",
    "Start": "2024-02-01 00:00:00",
    "Stop": "2024-02-01 02:30:00",
    "Description": "The second test timer.",
}

TIMER_REQUEST = {
    "UserId": 1,
    "Start": "2024-03-01 00:00:00",
    "Stop": "2024-03-01 02:30:00",
    "Description": "The third test timer.",
    "Billable": True,
}


def test_visoma_client(client):
    manager = client.timers
    assert isinstance(manager, TimersManager)


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/timer/search/").mock(
        httpx.Response(200, json=[FIRST_TIMER])
    )

    actual = client.timers.get({"id": "1"})
    assert isinstance(actual, Timer)
    assert actual.to_dict() == FIRST_TIMER


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_not_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/timer/search/").mock(
        httpx.Response(200, json={"Message": "No Timer found"})
    )

    with pytest.raises(ValueError, match="Timer not found"):
        client.timers.get({"id": "1"})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_more_than_one_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/timer/search/").mock(
        httpx.Response(200, json=[FIRST_TIMER, SECOND_TIMER])
    )

    with pytest.raises(ValueError, match="More than one timer found"):
        client.timers.get({"userid": "1"})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/timer/search/").mock(
        httpx.Response(200, json=[FIRST_TIMER, SECOND_TIMER])
    )

    actual = client.timers.list()

    assert len(actual) == 2
    assert isinstance(actual[0], Timer)
    assert actual[0].Description == "The first test timer."
    assert isinstance(actual[1], Timer)
    assert actual[1].Description == "The second test timer."


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list_not_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/timer/search/").mock(
        httpx.Response(200, json={"Message": "No Timer found"})
    )

    with pytest.raises(ValueError, match="No Timer found"):
        client.timers.list()
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_create(client, respx_mock):
    route = respx_mock.post(f"https://{tests.VISOMA_HOST}/api2/timer/").mock(
        httpx.Response(200, json={"Success": True, "Id": 1, "Message": ""})
    )

    actual = client.timers.create(TimerRequest.from_dict(TIMER_REQUEST))

    assert isinstance(actual, VisomaResponse)
    assert route.call_count == 1
    assert json.loads(route.calls.last.request.content) == TIMER_REQUEST


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_create_failed(client, respx_mock):
    route = respx_mock.post(f"https://{tests.VISOMA_HOST}/api2/timer/").mock(
        httpx.Response(
            200, json={"Success": False, "Id": -1, "Message": "Error creating timer"}
        )
    )

    with pytest.raises(ValueError, match="Error creating timer"):
        client.timers.create(TimerRequest.from_dict(TIMER_REQUEST))
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_delete(client, respx_mock):
    route = respx_mock.delete(f"https://{tests.VISOMA_HOST}/api2/timer/1").mock(
        httpx.Response(200, json={"Success": True, "Id": 1, "Message": ""})
    )

    actual = client.timers.delete(1)

    assert isinstance(actual, VisomaResponse)
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_delete_from_object(client, respx_mock):
    route = respx_mock.delete(f"https://{tests.VISOMA_HOST}/api2/timer/1").mock(
        httpx.Response(200, json={"Success": True, "Id": 1, "Message": ""})
    )

    timer = Timer.from_dict(FIRST_TIMER)
    actual = client.timers.delete(timer)

    assert isinstance(actual, VisomaResponse)
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_delete_failed(client, respx_mock):
    route = respx_mock.delete(f"https://{tests.VISOMA_HOST}/api2/timer/1").mock(
        httpx.Response(
            200, json={"Success": False, "Id": 1, "Message": "Error deleting timer"}
        )
    )

    with pytest.raises(ValueError, match="Error deleting timer"):
        client.timers.delete(1)
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_close(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/timer/close/id/1").mock(
        httpx.Response(302)
    )

    client.timers.close(1)
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_close_from_object(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/timer/close/id/1").mock(
        httpx.Response(302)
    )

    timer = Timer.from_dict(FIRST_TIMER)
    client.timers.close(timer)
    assert route.call_count == 1
