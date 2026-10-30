from unittest.mock import Mock

import pytest
import requests

from src.openf1.client import (
    OpenF1Client,
    OpenF1ConnectionError,
    OpenF1HTTPError,
    OpenF1ResponseError,
    OpenF1TimeoutError,
)


def _client_with_response(payload):
    session = Mock()
    response = Mock()
    response.json.return_value = payload
    response.status_code = 200
    session.get.return_value = response
    return OpenF1Client(
        base_url="https://example.test/v1/",
        timeout=3.5,
        session=session,
    ), session, response


def test_get_returns_json_objects_and_passes_endpoint_parameters():
    client, session, response = _client_with_response(
        [{"meeting_key": 123, "year": 2025}]
    )

    result = client.get("meetings", params={"year": 2025})

    assert result == [{"meeting_key": 123, "year": 2025}]
    session.get.assert_called_once_with(
        "https://example.test/v1/meetings",
        params={"year": 2025},
        timeout=3.5,
    )
    response.raise_for_status.assert_called_once_with()


def test_get_wraps_request_timeout():
    client, session, _ = _client_with_response([])
    session.get.side_effect = requests.Timeout("slow")

    with pytest.raises(OpenF1TimeoutError, match="timed out"):
        client.get("meetings")


def test_get_wraps_connection_failure():
    client, session, _ = _client_with_response([])
    session.get.side_effect = requests.ConnectionError("offline")

    with pytest.raises(OpenF1ConnectionError, match="Could not connect"):
        client.get("meetings")


def test_get_wraps_http_error():
    client, _, response = _client_with_response([])
    response.status_code = 503
    response.raise_for_status.side_effect = requests.HTTPError("unavailable")

    with pytest.raises(OpenF1HTTPError, match="HTTP 503"):
        client.get("meetings")


def test_get_rejects_invalid_json():
    client, _, response = _client_with_response([])
    response.json.side_effect = ValueError("invalid JSON")

    with pytest.raises(OpenF1ResponseError, match="invalid JSON"):
        client.get("meetings")


@pytest.mark.parametrize("payload", [{"meeting_key": 123}, "not a list", [1, None]])
def test_get_rejects_unexpected_response_structure(payload):
    client, _, _ = _client_with_response(payload)

    with pytest.raises(OpenF1ResponseError, match="JSON array of objects"):
        client.get("meetings")


def test_get_accepts_an_empty_result_list():
    client, _, _ = _client_with_response([])

    assert client.get("meetings") == []
