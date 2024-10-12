import httpx

# import json
import pytest

from visoma.projects import Project
from visoma.projects import ProjectsManager
import tests

FIRST_PROJECT = {
    "Id": 1,
    "Title": "Project 1",
    "Description": "The first test project.",
}

SECOND_PROJECT = {
    "Id": 2,
    "Title": "Project 2",
    "Description": "The second test project.",
}


def test_visoma_client(client):
    manager = client.projects
    assert isinstance(manager, ProjectsManager)


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/project/search/").mock(
        httpx.Response(200, json=[FIRST_PROJECT])
    )

    actual = client.projects.get({"id": "1"})
    assert isinstance(actual, Project)
    assert actual.to_dict() == FIRST_PROJECT


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_not_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/project/search/").mock(
        httpx.Response(200, json={"Message": "No Project found"})
    )

    with pytest.raises(ValueError, match="Project not found"):
        client.projects.get({"id": "1"})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_get_more_than_one_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/project/search/").mock(
        httpx.Response(200, json=[FIRST_PROJECT, SECOND_PROJECT])
    )

    with pytest.raises(ValueError, match="More than one project found"):
        client.projects.get({"userid": "1"})
    assert route.call_count == 1


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list(client, respx_mock):
    respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/project/search/").mock(
        httpx.Response(200, json=[FIRST_PROJECT, SECOND_PROJECT])
    )

    actual = client.projects.list()

    assert len(actual) == 2
    assert isinstance(actual[0], Project)
    assert actual[0].Description == "The first test project."
    assert isinstance(actual[1], Project)
    assert actual[1].Description == "The second test project."


@pytest.mark.respx(assert_all_mocked=True, assert_all_called=True)
def test_list_not_found(client, respx_mock):
    route = respx_mock.get(f"https://{tests.VISOMA_HOST}/api2/project/search/").mock(
        httpx.Response(200, json={"Message": "No Project found"})
    )

    with pytest.raises(ValueError, match="No Project found"):
        client.projects.list()
    assert route.call_count == 1
