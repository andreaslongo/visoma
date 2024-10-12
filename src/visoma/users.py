from attrs import define
from datetime import datetime
import cattrs

from visoma.http import HttpClient
from visoma.lib import visoma_params_from_filters_with_limit


@define(str=True)
class User:
    """Details for a user managed by the Visoma service."""

    id: int
    username: str
    FullName: str
    email: str
    usertype: str
    comment: str
    lastlogin: datetime

    @classmethod
    def from_dict(cls, data):
        return cattrs.structure(data, cls)

    def to_dict(self):
        d = cattrs.unstructure(self)
        return {k: v for k, v in d.items() if v is not None}


@define
class UsersManager:
    """Manager for user resources."""

    client: HttpClient

    def get(self, filters: dict[str, str]) -> User:
        """Returns a single user."""
        try:
            users = self.list(filters=filters)
        except ValueError as err:
            raise ValueError(f"User not found: '{filters}'") from err

        if len(users) > 1:
            raise ValueError(f"More than one user found: {users}")

        user = users[0]
        return user

    def list(self, limit: int = 2, filters: dict[str, str] | None = None) -> list[User]:
        """Report on users.

        Args:
            limit: Fetch users up to this limit. The default fetches 2
            users.
            filters: Criteria to filter the user list.
        """
        params = visoma_params_from_filters_with_limit(filters, limit)
        response = self.client.get("/api2/user/search/", params=params)

        try:
            return [User.from_dict(item) for item in response]
        except cattrs.errors.ClassValidationError as err:
            raise ValueError(response["Message"]) from err
