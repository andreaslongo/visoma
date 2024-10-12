from attrs import define
import cattrs

from visoma.http import HttpClient
from visoma.lib import visoma_params_from_filters_with_limit


@define
class UserGroup:
    """Details for a user group managed by the Visoma service."""

    id: int
    title: str
    active: bool

    @classmethod
    def from_dict(cls, data):
        return cattrs.structure(data, cls)

    def to_dict(self):
        d = cattrs.unstructure(self)
        return {k: v for k, v in d.items() if v is not None}


@define
class UserGroupsManager:
    """Manager for user group resources."""

    client: HttpClient

    def get(self, filters: dict[str, str] | None = None) -> UserGroup:
        """Returns a single user group."""
        try:
            user_groups = self.list(filters=filters)
        except ValueError as err:
            raise ValueError(f"User group not found: '{filters}'") from err

        if len(user_groups) > 1:
            raise ValueError(f"More than one user group found: {user_groups}")

        user_group = user_groups[0]
        return user_group

    def list(
        self, limit: int = 2, filters: dict[str, str] | None = None
    ) -> list[UserGroup]:
        """Report on user groups.

        Args:
            limit: Fetch user groups up to this limit. The default fetches 2
            user groups.
            filters: Criteria to filter the user groups list.
        """
        params = visoma_params_from_filters_with_limit(filters, limit)
        response = self.client.get("/api2/usergroups/search/", params=params)

        try:
            return [UserGroup.from_dict(item) for item in response]
        except cattrs.errors.ClassValidationError as err:
            raise ValueError(response["Message"]) from err
