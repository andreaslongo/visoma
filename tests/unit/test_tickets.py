import httpx
import json
import pytest

from visoma.lib import VisomaResponse
from visoma.tickets import Ticket
from visoma.tickets import TicketRequest
from visoma.tickets import TicketsManager
import tests


FIRST_TICKET = {
    "Id": 1,
    "Number": 1,
    "Title": "Ticket 1",
    "Description": "The first test ticket.",
    "CustomerName": "Customer 1",
    "CustomerId": 1,
    "Status": "Open",
    "StatusId": 1,
}


SECOND_TICKET = {
    "Id": 2,
    "Number": 2,
    "Title": "Ticket 2",
    "Description": "The second test ticket.",
    "CustomerName": "Customer 1",
    "CustomerId": 1,
    "Status": "Closed",
    "StatusId": 2,
}

TICKET_REQUEST = {
    "Title": "Ticket 3",
    "Description": "The third test ticket.",
    "CustomerId": 1,
    "AddressId": 1,
}


def test_visoma_client(client):
    manager = client.tickets
    assert isinstance(manager, TicketsManager)


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/tickets/search/").mock(
        httpx.Response(200, json=[FIRST_TICKET])
    )

    actual = client.tickets.get({"title": "Ticket 1"})
    assert isinstance(actual, Ticket)
    assert actual.to_dict() == FIRST_TICKET


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_not_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/tickets/search/").mock(
        httpx.Response(200, json={"Message": "No Ticket found"})
    )

    with pytest.raises(ValueError, match="Ticket not found"):
        client.tickets.get({"title": "Ticket 1"})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_more_than_one_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/tickets/search/").mock(
        httpx.Response(200, json=[FIRST_TICKET, SECOND_TICKET])
    )

    with pytest.raises(ValueError, match="More than one ticket found"):
        client.tickets.get({"customerid": "1"})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/tickets/search/").mock(
        httpx.Response(200, json=[FIRST_TICKET, SECOND_TICKET])
    )

    actual = client.tickets.list()

    assert len(actual) == 2
    assert isinstance(actual[0], Ticket)
    assert actual[0].Title == "Ticket 1"
    assert isinstance(actual[1], Ticket)
    assert actual[1].Title == "Ticket 2"


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list_not_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/tickets/search/").mock(
        httpx.Response(200, json={"Message": "No Ticket found"})
    )

    with pytest.raises(ValueError, match="No Ticket found"):
        client.tickets.list()
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_create(client, respx_mock):
    route = respx_mock.post(f"https://{tests.VISOMA_HOST}/api2/ticket/").mock(
        httpx.Response(200, json={"Success": True, "Id": 1, "Message": ""})
    )

    actual = client.tickets.create(TicketRequest.from_dict(TICKET_REQUEST))

    assert isinstance(actual, VisomaResponse)
    assert route.call_count == 1
    assert json.loads(route.calls.last.request.content) == TICKET_REQUEST
    # assert title == "Ticket 3"


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_create_failed(client, respx_mock):
    route = respx_mock.post(f"https://{tests.VISOMA_HOST}/api2/ticket/").mock(
        httpx.Response(
            200, json={"Success": False, "Id": -1, "Message": "Error creating ticket"}
        )
    )

    with pytest.raises(ValueError, match="Error creating ticket"):
        client.tickets.create(TicketRequest.from_dict(TICKET_REQUEST))
    assert route.call_count == 1
