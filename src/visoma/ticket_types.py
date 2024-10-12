from attrs import define
import cattrs

from visoma.http import HttpClient
from visoma.lib import visoma_params_from_filters_with_limit


@define
class TicketType:
    """Details for a ticket type managed by the Visoma service."""

    Id: int
    Title: str
    Description: str

    Active: bool | None = None
    erpid: int | None = None

    @classmethod
    def from_dict(cls, data):
        return cattrs.structure(data, cls)

    def to_dict(self):
        d = cattrs.unstructure(self)
        return {k: v for k, v in d.items() if v is not None}


@define
class TicketTypesManager:
    """Manager for ticket type resources."""

    client: HttpClient

    def get(self, filters: dict[str, str] | None = None) -> TicketType:
        """Returns a single ticket type."""
        try:
            ticket_types = self.list(filters=filters)
        except ValueError as err:
            raise ValueError(f"Ticket type not found: '{filters}'") from err

        if len(ticket_types) > 1:
            raise ValueError(f"More than one ticket type found: {ticket_types}")

        ticket_type = ticket_types[0]
        return ticket_type

    def list(
        self, limit: int = 2, filters: dict[str, str] | None = None
    ) -> list[TicketType]:
        """Report on ticket types.

        Args:
            limit: Fetch ticket types up to this limit. The default fetches 2
            ticket types.
            filters: Criteria to filter the ticket types list.
        """
        params = visoma_params_from_filters_with_limit(filters, limit)
        response = self.client.get("/api2/tickettype/search/", params=params)

        try:
            return [TicketType.from_dict(item) for item in response]
        except cattrs.errors.ClassValidationError as err:
            raise ValueError(response["Message"]) from err
