import httpx
import pytest

from visoma.user_groups import UserGroup
from visoma.user_groups import UserGroupsManager
import tests

FIRST_USER_GROUP = {
    "id": 1,
    "title": "User Group 1",
    "active": True,
}

SECOND_USER_GROUP = {
    "id": 2,
    "title": "User Group 2",
    "active": True,
}


def test_visoma_client(client):
    manager = client.user_groups
    assert isinstance(manager, UserGroupsManager)


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/usergroups/search/").mock(
        httpx.Response(200, json=[FIRST_USER_GROUP])
    )

    actual = client.user_groups.get({"id": "1"})
    assert isinstance(actual, UserGroup)
    assert actual.to_dict() == FIRST_USER_GROUP


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_not_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/usergroups/search/").mock(
        httpx.Response(200, json={"Message": "No User Group found"})
    )

    with pytest.raises(ValueError, match="User group not found"):
        client.user_groups.get({"id": "1"})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_more_than_one_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/usergroups/search/").mock(
        httpx.Response(200, json=[FIRST_USER_GROUP, SECOND_USER_GROUP])
    )

    with pytest.raises(ValueError, match="More than one user group found"):
        client.user_groups.get({"active": True})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/usergroups/search/").mock(
        httpx.Response(200, json=[FIRST_USER_GROUP, SECOND_USER_GROUP])
    )

    actual = client.user_groups.list()

    assert len(actual) == 2
    assert isinstance(actual[0], UserGroup)
    assert actual[0].title == "User Group 1"
    assert isinstance(actual[1], UserGroup)
    assert actual[1].title == "User Group 2"


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list_not_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/usergroups/search/").mock(
        httpx.Response(200, json={"Message": "No User Group found"})
    )

    with pytest.raises(ValueError, match="No User Group found"):
        client.user_groups.list()
    assert route.call_count == 1
