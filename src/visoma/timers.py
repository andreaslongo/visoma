from attrs import define
from datetime import datetime
import cattrs

from visoma.http import HttpClient
from visoma.lib import VisomaResponse
from visoma.lib import visoma_params_from_filters_with_limit


@define
class Timer:
    """Details for a timer managed by the Visoma service."""

    Id: int
    UserId: int
    User: str
    Start: datetime
    Stop: datetime
    Description: str

    TicketId: int | None = None
    ArticleId: int | None = None
    TypeId: int | None = None
    InternalNotice: str | None = None
    Scheduled: bool | None = None
    Billable: bool | None = None
    Closed: bool | None = None
    Approach: bool | None = None
    erpid: int | None = None

    @classmethod
    def from_dict(cls, data):
        return cattrs.structure(data, cls)

    def to_dict(self):
        d = cattrs.unstructure(self)
        return {k: v for k, v in d.items() if v is not None}


@define
class TimerRequest:
    """Represents a timer request."""

    UserId: int
    Start: datetime
    Stop: datetime
    Description: str

    Billable: bool | None = False

    ArticleId: int | None = None
    InternalNotice: str | None = None
    Scheduled: bool | None = None
    TicketId: int | None = None
    TypeId: int | None = None

    # Not needed or has no effect.
    # Some can only be set on already created records via update?
    Approach: bool | None = None
    Closed: bool | None = None
    Status: int | None = None
    UpdateWorktime: bool | None = None
    bCustomTime: bool | None = None
    cti: str | None = None
    erpid: int | None = None
    roundTime: bool | None = None

    @classmethod
    def from_dict(cls, data):
        return cattrs.structure(data, cls)

    def to_dict(self):
        d = cattrs.unstructure(self)
        return {k: v for k, v in d.items() if v is not None}


@define
class TimersManager:
    """Manager for timer resources."""

    client: HttpClient

    def get(self, filters: dict[str, str] | None = None) -> Timer:
        """Returns a single timer."""
        try:
            timers = self.list(filters=filters)
        except ValueError as err:
            raise ValueError(f"Timer not found: '{filters}'") from err

        if len(timers) > 1:
            raise ValueError(f"More than one timer found: {timers}")

        timer = timers[0]
        return timer

    def list(
        self, limit: int = 2, filters: dict[str, str] | None = None
    ) -> list[Timer]:
        """Report on timers.

        Args:
            limit: Fetch timers up to this limit. The default fetches 2
            timers.
            filters: Criteria to filter the timer list.
        """
        params = visoma_params_from_filters_with_limit(filters, limit)
        response = self.client.get("/api2/timer/search/", params=params)

        try:
            return [Timer.from_dict(item) for item in response]
        except cattrs.errors.ClassValidationError as err:
            raise ValueError(response["Message"]) from err

    def delete(self, idx: Timer | int):
        """Delete a timer.

        Args:
            idx: Identifier for timer to be deleted.
        """

        if isinstance(idx, Timer):
            idx = idx.Id

        response = self.client.delete(f"/api2/timer/{idx}")
        try:
            return VisomaResponse.from_dict(response)
        except cattrs.errors.ClassValidationError as err:
            raise ValueError(response["Message"]) from err

    def close(self, idx: Timer | int):
        """Close a timer.

        There is currently no API endpoint for this operation. We can also send
        this request when the timer is already closed. Then it has no effect.
        The response to this is a 302 redirect to a Visoma HTML page:
        /workend/index/date/

        Args:
            idx: Identifier for timer to be closed.
        """

        if isinstance(idx, Timer):
            idx = idx.Id

        self.client.get(f"/timer/close/id/{idx}")

    def create(self, request: TimerRequest):
        """Create a timer."""
        response = self.client.post("/api2/timer/", data=request.to_dict())
        try:
            return VisomaResponse.from_dict(response)
        except cattrs.errors.ClassValidationError as err:
            raise ValueError(response["Message"]) from err
