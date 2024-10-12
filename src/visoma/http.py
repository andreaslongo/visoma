from attrs import frozen
import httpx
import json
import logging

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 20
DEFAULT_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0."
}


class HttpError(Exception):
    """Custom exception for HTTP errors."""

    pass


@frozen
class HttpClient:
    """A client for basic HTTP requests/responses."""

    client: httpx.Client

    @classmethod
    def with_extra_headers(cls, base_url, headers) -> "HttpClient":
        headers = DEFAULT_HEADERS | headers
        client = httpx.Client(
            timeout=DEFAULT_TIMEOUT, base_url=base_url, headers=headers
        )
        return cls(client)

    def get(
        self,
        url,
        headers=None,
        params=None,
        as_json=True,
        verify_cert=True,
        basic_auth=None,
    ):
        """Make a GET requests."""
        response = self.client.get(url, headers=headers, params=params, auth=basic_auth)
        log.debug(f"GET {response.url}")
        return handle_response(response, as_json)

    def post(self, url, headers=None, data=None):
        """Make a POST requests."""
        response = self.client.post(url, headers=headers, json=data)
        log.debug(f"POST {response.url} :: {data}")
        return handle_response(response)

    def delete(self, url, headers=None):
        """Make a DELETE requests."""
        response = self.client.delete(url, headers=headers)
        log.debug(f"DELETE {response.url}")
        return handle_response(response)

    def close(self):
        """Close the client."""
        log.debug("Closing client")
        self.client.close()
        log.debug("HttpClient closed")


def handle_response(response, as_json=True):
    """Handle HTTP responses."""
    log.debug(f"Response: {response.status_code}")

    # Success
    if 200 <= response.status_code < 300:
        if as_json:
            response = response.json()
            log.debug(f"Response: {json.dumps(response, indent=4)}")
        else:
            response = response.text
            # Extract the first line of potentially long text (could be a
            # whole HTML page)
            log.debug(f"Response: {response.partition('\n')[0]}")
        return response

    # Redirect
    elif 300 <= response.status_code < 400:
        pass

    else:
        raise HttpError(f"{response.status_code}: {response.text}")
