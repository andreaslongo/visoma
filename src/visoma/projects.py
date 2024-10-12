from attrs import define
from datetime import date
import cattrs

from visoma.http import HttpClient
from visoma.lib import visoma_params_from_filters_with_limit


@define
class Project:
    """Details for a project managed by the Visoma service."""

    Id: int
    Title: str
    Description: str

    Begin: date | None = None
    Deadline: date | None = None
    Archived: bool | None = None
    Duration: int | None = None
    TicketIds: list[int] | None = None

    @classmethod
    def from_dict(cls, data):
        return cattrs.structure(data, cls)

    def to_dict(self):
        d = cattrs.unstructure(self)
        return {k: v for k, v in d.items() if v is not None}


@define
class ProjectsManager:
    """Manager for project resources."""

    client: HttpClient

    def get(self, filters: dict[str, str] | None = None) -> Project:
        """Returns a single project."""
        try:
            projects = self.list(filters=filters)
        except ValueError as err:
            raise ValueError(f"Project not found: '{filters}'") from err

        if len(projects) > 1:
            raise ValueError(f"More than one project found: {projects}")

        project = projects[0]
        return project

    def list(
        self, limit: int = 2, filters: dict[str, str] | None = None
    ) -> list[Project]:
        """Report on projects.

        Args:
            limit: Fetch projects up to this limit. The default fetches 2
            projects.
            filters: Criteria to filter the project list.
        """
        params = visoma_params_from_filters_with_limit(filters, limit)
        response = self.client.get("/api2/project/search/", params=params)

        try:
            return [Project.from_dict(item) for item in response]
        except cattrs.errors.ClassValidationError as err:
            raise ValueError(response["Message"]) from err
