from attrs import define
from datetime import datetime
import cattrs
import logging

from visoma.http import HttpClient
from visoma.lib import VisomaResponse
from visoma.lib import visoma_params_from_filters_with_limit
from visoma.lib import structure


log = logging.getLogger(__name__)

# cattrs.register_structure_hook(datetime, lambda v, _: datetime.strptime(v, "%d.%m.%Y %H:%M:%S"))
# cattrs.register_unstructure_hook(datetime, lambda v: v.strftime("%d.%m.%Y %H:%M:%S"))


@define(str=True)
class Ticket:
    """Details for a ticket managed by the Visoma service."""

    Id: int
    Number: int
    Title: str
    Description: str
    CustomerName: str
    CustomerId: int
    Status: str
    StatusId: int

    Created: datetime | None = None
    Modified: datetime | None = None
    DueOn: datetime | None = None
    Duration: float | None = None
    NotifyCustomer: bool | None = None
    PriorityId: int | None = None
    ProjectIds: str | None = None  # a comma separated list of project IDs: "6,87,10"

    @classmethod
    def from_dict(cls, data):
        return structure(data, cls)

    def to_dict(self):
        d = cattrs.unstructure(self)
        return {k: v for k, v in d.items() if v is not None}


@define
class TicketRequest:
    """Represents a ticket request."""

    Title: str
    Description: str
    CustomerId: int
    AddressId: int

    DueOn: datetime | None = None
    NotifyCustomer: bool | None = None
    PriorityId: int | None = None
    ProjectIds: str | None = None  # a comma separated list of project IDs: "6,87,10"

    @classmethod
    def from_dict(cls, data):
        return structure(data, cls)


    def to_dict(self):
        d = cattrs.unstructure(self)
        return {k: v for k, v in d.items() if v is not None}


@define
class TicketsManager:
    """Manager for ticket resources."""

    client: HttpClient

    def get(self, filters: dict[str, str]) -> Ticket:
        """Returns a single ticket."""
        try:
            tickets = self.list(filters=filters)
        except ValueError as err:
            raise ValueError(f"Ticket not found: '{filters}'") from err

        if len(tickets) > 1:
            raise ValueError(f"More than one ticket found: {tickets}")

        ticket = tickets[0]
        return ticket

    def list(
        self, limit: int = 2, filters: dict[str, str] | None = None
    ) -> list[Ticket]:
        """Report on tickets.

        Args:
            limit: Fetch tickets up to this limit. The default fetches 2
            tickets.
            filters: Criteria to filter the ticket list.
        """
        params = visoma_params_from_filters_with_limit(filters, limit)
        response = self.client.get("/api2/tickets/search/", params=params)

        try:
            return [Ticket.from_dict(item) for item in response]
        except cattrs.errors.ClassValidationError as err:
            raise ValueError(response["Message"]) from err

    def create(self, request: TicketRequest):
        """Create a ticket."""
        log.debug("Creating ticket")
        log.debug(f"request={request}")
        response = self.client.post("/api2/ticket/", data=request.to_dict())
        log.debug(f"response={response}")
        try:
            return VisomaResponse.from_dict(response)
        except cattrs.errors.ClassValidationError as err:
            log.error(f"ClassValidationError: {err.args}")
            raise ValueError(response["Message"]) from err
