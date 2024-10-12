"""Client for connecting to Visoma service."""

from attrs import define
from contextlib import AbstractContextManager
import logging
import os

from visoma.http import HttpClient
from visoma.projects import ProjectsManager
from visoma.ticket_statuses import TicketStatusesManager
from visoma.ticket_types import TicketTypesManager
from visoma.tickets import TicketsManager
from visoma.timer_types import TimerTypesManager
from visoma.timers import TimersManager
from visoma.user_groups import UserGroupsManager
from visoma.users import UsersManager
from visoma.workdays import WorkdaysManager

log = logging.getLogger(__name__)


@define
class VisomaClient(AbstractContextManager):
    """Client to connect to a Visoma service."""

    client: HttpClient
    user: str

    @classmethod
    def from_env(cls) -> "VisomaClient":
        """Returns connection to service using environment variables and parameters.

        Environment variables:
            - VISOMA_HOST: Full-qualified domain name of the Visoma service
            - VISOMA_USER: The user name for the Visoma login.
            - VISOMA_PASSWORD: The user's password for the Visoma login.

        Returns:
            Client used to communicate with a Visoma service.

        Raises:
            ValueError when required environment variable is not set.
        """

        host = os.getenv("VISOMA_HOST")
        user = os.getenv("VISOMA_USER")
        password = os.getenv("VISOMA_PASSWORD")
        if not all((host, user, password)):
            raise ValueError(
                f"Missing values from env: VISOMA_HOST={host}, VISOMA_USER={user}, VISOMA_PASSWORD={password}"
            )

        base_url = f"https://{host}"
        visoma_headers = {
            "X_VSM_USERNAME": user,
            "X_VSM_PASSWORD": password,
        }

        client = HttpClient.with_extra_headers(base_url, visoma_headers)
        log.debug(f"HTTP Client: {client}")

        return cls(client, user)

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self):
        log.debug("Closing resources")
        return self.client.close()

    @property
    def tickets(self):
        """Returns a manager for operations on tickets maintained by a Visoma service."""
        return TicketsManager(client=self.client)

    @property
    def ticket_statuses(self):
        """Returns a manager for operations on ticket statuses maintained by a Visoma service."""
        return TicketStatusesManager(client=self.client)

    @property
    def ticket_types(self):
        """Returns a manager for operations on ticket types maintained by a Visoma service."""
        return TicketTypesManager(client=self.client)

    @property
    def timers(self):
        """Returns a manager for operations on timers maintained by a Visoma service."""
        return TimersManager(client=self.client)

    @property
    def timer_types(self):
        """Returns a manager for operations on timer types maintained by a Visoma service."""
        return TimerTypesManager(client=self.client)

    @property
    def users(self):
        """Returns a manager for operations on users maintained by a Visoma service."""
        return UsersManager(client=self.client)

    @property
    def user_groups(self):
        """Returns a manager for operations on user groups maintained by a Visoma service."""
        return UserGroupsManager(client=self.client)

    @property
    def workdays(self):
        """Returns a manager for operations on workdays maintained by a Visoma service."""
        return WorkdaysManager(client=self.client)

    @property
    def projects(self):
        """Returns a manager for operations on projects maintained by a Visoma service."""
        return ProjectsManager(client=self.client)
