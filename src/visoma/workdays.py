from attrs import define
from datetime import date
import re

from visoma.http import HttpClient


@define
class WorkdaysManager:
    """Manager for workday resources."""

    client: HttpClient

    def close(self, day: date):
        """Close a workday.

        There is currently no API endpoint for this operation. We can also send
        this request when the day is already closed. Then it has no effect.
        The response to this is a 30x redirect to a Visoma HTML page.

        Examples:
            GET /workend/index/date/2024-01-08
            GET /workend/submitworkend/id/154942

        Args:
            day: The workday to be closed.
        """

        # We need to get a workday ID for a date.
        idx = extract_workday_id_from_html(
            self.client.get(f"/workend/index/date/{day}", as_json=False)
        )

        self.client.get(f"/workend/submitworkend/id/{idx}")


def extract_workday_id_from_html(html: str) -> int:
    pattern = r"/workend/submitworkend/id/(\d+)/"
    match = re.search(pattern, html)

    if match:
        extracted_id = match.group(1)
        return int(extracted_id)
    else:
        raise ValueError(f"Could not extract workday ID from HTML: {html}")
