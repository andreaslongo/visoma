import httpx
import pytest

from visoma.ticket_statuses import TicketStatus
from visoma.ticket_statuses import TicketStatusesManager
import tests

FIRST_TICKET_STATUS = {
    "Id": 1,
    "Title": "Ticket Status 1",
}

SECOND_TICKET_STATUS = {
    "Id": 2,
    "Title": "Ticket Status 2",
}


def test_visoma_client(client):
    manager = client.ticket_statuses
    assert isinstance(manager, TicketStatusesManager)


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/ticketstatus/search/").mock(
        httpx.Response(200, json=[FIRST_TICKET_STATUS])
    )

    actual = client.ticket_statuses.get({"id": "1"})
    assert isinstance(actual, TicketStatus)
    assert actual.to_dict() == FIRST_TICKET_STATUS


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_not_found(client, respx_mock):
    route = respx_mock.get(
        f"https://{tests.VISOMA_HOST}/api2/ticketstatus/search/"
    ).mock(httpx.Response(200, json={"Message": "No Ticket Status found"}))

    with pytest.raises(ValueError, match="Ticket status not found"):
        client.ticket_statuses.get({"id": "1"})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_more_than_one_found(client, respx_mock):
    route = respx_mock.get(
        f"https://{tests.VISOMA_HOST}/api2/ticketstatus/search/"
    ).mock(httpx.Response(200, json=[FIRST_TICKET_STATUS, SECOND_TICKET_STATUS]))

    with pytest.raises(ValueError, match="More than one ticket status found"):
        client.ticket_statuses.get({"active": True})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/ticketstatus/search/").mock(
        httpx.Response(200, json=[FIRST_TICKET_STATUS, SECOND_TICKET_STATUS])
    )

    actual = client.ticket_statuses.list()

    assert len(actual) == 2
    assert isinstance(actual[0], TicketStatus)
    assert actual[0].Title == "Ticket Status 1"
    assert isinstance(actual[1], TicketStatus)
    assert actual[1].Title == "Ticket Status 2"


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list_not_found(client, respx_mock):
    route = respx_mock.get(
        f"https://{tests.VISOMA_HOST}/api2/ticketstatus/search/"
    ).mock(httpx.Response(200, json={"Message": "No Ticket Status found"}))

    with pytest.raises(ValueError, match="No Ticket Status found"):
        client.ticket_statuses.list()
    assert route.call_count == 1
