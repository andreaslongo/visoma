from attrs import define
import cattrs

from visoma.http import HttpClient
from visoma.lib import visoma_params_from_filters_with_limit


@define
class TimerType:
    """Details for a timer type managed by the Visoma service."""

    id: int
    title: str
    description: str

    type: int | None = None
    erpid: int | None = None
    typename: str | None = None
    color: str | None = None

    @classmethod
    def from_dict(cls, data):
        return cattrs.structure(data, cls)

    def to_dict(self):
        d = cattrs.unstructure(self)
        return {k: v for k, v in d.items() if v is not None}


@define
class TimerTypesManager:
    """Manager for timer type resources."""

    client: HttpClient

    def get(self, filters: dict[str, str] | None = None) -> TimerType:
        """Returns a single timer type."""
        try:
            timer_types = self.list(filters=filters)
        except ValueError as err:
            raise ValueError(f"Timer type not found: '{filters}'") from err

        if len(timer_types) > 1:
            raise ValueError(f"More than one timer type found: {timer_types}")

        timer_type = timer_types[0]
        return timer_type

    def list(
        self, limit: int = 2, filters: dict[str, str] | None = None
    ) -> list[TimerType]:
        """Report on timer types.

        Args:
            limit: Fetch timer types up to this limit. The default fetches 2
            timer types.
            filters: Criteria to filter the timer types list.
        """
        params = visoma_params_from_filters_with_limit(filters, limit)
        response = self.client.get("/api2/timertype/search/", params=params)

        try:
            return [TimerType.from_dict(item) for item in response]
        except cattrs.errors.ClassValidationError as err:
            raise ValueError(response["Message"]) from err
