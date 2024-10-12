from attrs import define
import cattrs

from visoma.http import HttpClient
from visoma.lib import visoma_params_from_filters_with_limit


@define
class TicketStatus:
    """Details for a ticket status managed by the Visoma service."""

    Id: int
    Title: str

    Default: bool | None = None
    Color: str | None = None
    erpid: int | None = None

    @classmethod
    def from_dict(cls, data):
        return cattrs.structure(data, cls)

    def to_dict(self):
        d = cattrs.unstructure(self)
        return {k: v for k, v in d.items() if v is not None}


@define
class TicketStatusesManager:
    """Manager for ticket status resources."""

    client: HttpClient

    def get(self, filters: dict[str, str] | None = None) -> TicketStatus:
        """Returns a single ticket status."""
        try:
            ticket_status = self.list(filters=filters)
        except ValueError as err:
            raise ValueError(f"Ticket status not found: '{filters}'") from err

        if len(ticket_status) > 1:
            raise ValueError(f"More than one ticket status found: {ticket_status}")

        ticket_status = ticket_status[0]
        return ticket_status

    def list(
        self, limit: int = 2, filters: dict[str, str] | None = None
    ) -> list[TicketStatus]:
        """Report on ticket statuses.

        Args:
            limit: Fetch ticket statuses up to this limit. The default fetches 2
            ticket statuses.
            filters: Criteria to filter the ticket statuses list.
        """
        params = visoma_params_from_filters_with_limit(filters, limit)
        response = self.client.get("/api2/ticketstatus/search/", params=params)

        try:
            return [TicketStatus.from_dict(item) for item in response]
        except cattrs.errors.ClassValidationError as err:
            raise ValueError(response["Message"]) from err
