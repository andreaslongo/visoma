import httpx
import pytest

from visoma.users import User
from visoma.users import UsersManager
import tests

FIRST_USER = {
    "id": 1,
    "username": "user-1",
    "FullName": "First User",
    "email": "user-1@example.com",
    "usertype": "employee",
    "comment": "The first test user.",
    "lastlogin": "2024-01-01 00:00:00",
}

SECOND_USER = {
    "id": 2,
    "username": "user-2",
    "FullName": "Second User",
    "email": "user-2@example.com",
    "usertype": "employee",
    "comment": "The second test user.",
    "lastlogin": "2024-02-01 00:00:00",
}


def test_visoma_client(client):
    manager = client.users
    assert isinstance(manager, UsersManager)


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/user/search/").mock(
        httpx.Response(200, json=[FIRST_USER])
    )

    actual = client.users.get({"id": "1"})
    assert isinstance(actual, User)
    assert actual.to_dict() == FIRST_USER


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_not_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/user/search/").mock(
        httpx.Response(200, json={"Message": "No User found"})
    )

    with pytest.raises(ValueError, match="User not found"):
        client.users.get({"id": "1"})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_more_than_one_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/user/search/").mock(
        httpx.Response(200, json=[FIRST_USER, SECOND_USER])
    )

    with pytest.raises(ValueError, match="More than one user found"):
        client.users.get({"usertype": "employee"})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/user/search/").mock(
        httpx.Response(200, json=[FIRST_USER, SECOND_USER])
    )

    actual = client.users.list()

    assert len(actual) == 2
    assert isinstance(actual[0], User)
    assert actual[0].username == "user-1"
    assert isinstance(actual[1], User)
    assert actual[1].username == "user-2"


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list_not_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/user/search/").mock(
        httpx.Response(200, json={"Message": "No User found"})
    )

    with pytest.raises(ValueError, match="No User found"):
        client.users.list()
    assert route.call_count == 1
