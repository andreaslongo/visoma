import httpx
import pytest

from visoma.ticket_types import TicketType
from visoma.ticket_types import TicketTypesManager
import tests

FIRST_TICKET_TYPE = {
    "Id": 1,
    "Title": "Ticket Type 1",
    "Description": "The first ticket type.",
}

SECOND_TICKET_TYPE = {
    "Id": 2,
    "Title": "Ticket Type 2",
    "Description": "The second ticket type.",
}


def test_visoma_client(client):
    manager = client.ticket_types
    assert isinstance(manager, TicketTypesManager)


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/tickettype/search/").mock(
        httpx.Response(200, json=[FIRST_TICKET_TYPE])
    )

    actual = client.ticket_types.get({"id": "1"})
    assert isinstance(actual, TicketType)
    assert actual.to_dict() == FIRST_TICKET_TYPE


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_not_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/tickettype/search/").mock(
        httpx.Response(200, json={"Message": "No Ticket Type found"})
    )

    with pytest.raises(ValueError, match="Ticket type not found"):
        client.ticket_types.get({"id": "1"})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_more_than_one_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/tickettype/search/").mock(
        httpx.Response(200, json=[FIRST_TICKET_TYPE, SECOND_TICKET_TYPE])
    )

    with pytest.raises(ValueError, match="More than one ticket type found"):
        client.ticket_types.get({"active": True})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/tickettype/search/").mock(
        httpx.Response(200, json=[FIRST_TICKET_TYPE, SECOND_TICKET_TYPE])
    )

    actual = client.ticket_types.list()

    assert len(actual) == 2
    assert isinstance(actual[0], TicketType)
    assert actual[0].Title == "Ticket Type 1"
    assert isinstance(actual[1], TicketType)
    assert actual[1].Title == "Ticket Type 2"


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list_not_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/tickettype/search/").mock(
        httpx.Response(200, json={"Message": "No Ticket Type found"})
    )

    with pytest.raises(ValueError, match="No Ticket Type found"):
        client.ticket_types.list()
    assert route.call_count == 1
