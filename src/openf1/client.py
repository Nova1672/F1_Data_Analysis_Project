"""HTTP client for the OpenF1 REST API."""

from __future__ import annotations

from typing import Any, Mapping

import requests


DEFAULT_BASE_URL = "https://api.openf1.org/v1"


class OpenF1Error(Exception):
    """Base exception for OpenF1 client failures."""


class OpenF1RequestError(OpenF1Error):
    """Raised when an OpenF1 HTTP request fails."""


class OpenF1TimeoutError(OpenF1RequestError):
    """Raised when an OpenF1 request times out."""


class OpenF1ConnectionError(OpenF1RequestError):
    """Raised when a connection to OpenF1 cannot be established."""


class OpenF1HTTPError(OpenF1RequestError):
    """Raised when OpenF1 returns an unsuccessful HTTP status."""


class OpenF1ResponseError(OpenF1Error):
    """Raised when an OpenF1 response cannot be decoded or validated."""


class OpenF1Client:
    """Make validated GET requests to OpenF1."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
        session: requests.Session | None = None,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero.")
        if not base_url.strip():
            raise ValueError("base_url must not be empty.")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session if session is not None else requests.Session()

    def get(
        self,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch an endpoint and return a list of JSON objects."""
        normalized_endpoint = endpoint.strip("/")
        if not normalized_endpoint:
            raise ValueError("endpoint must not be empty.")

        url = f"{self.base_url}/{normalized_endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
        except requests.Timeout as error:
            raise OpenF1TimeoutError(
                f"Request to {url} timed out after {self.timeout} seconds."
            ) from error
        except requests.ConnectionError as error:
            raise OpenF1ConnectionError(f"Could not connect to {url}.") from error
        except requests.RequestException as error:
            raise OpenF1RequestError(f"Request to {url} failed: {error}") from error

        try:
            response.raise_for_status()
        except requests.HTTPError as error:
            status_code = response.status_code
            raise OpenF1HTTPError(
                f"OpenF1 returned HTTP {status_code} for {url}."
            ) from error

        try:
            data = response.json()
        except ValueError as error:
            raise OpenF1ResponseError(
                f"OpenF1 returned invalid JSON for {url}."
            ) from error

        if not isinstance(data, list) or any(
            not isinstance(item, dict) for item in data
        ):
            raise OpenF1ResponseError(
                f"Expected a JSON array of objects from {url}."
            )

        return data


__all__ = [
    "OpenF1Client",
    "OpenF1ConnectionError",
    "OpenF1Error",
    "OpenF1HTTPError",
    "OpenF1RequestError",
    "OpenF1ResponseError",
    "OpenF1TimeoutError",
]
