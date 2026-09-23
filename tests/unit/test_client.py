import json

import pytest
import responses

from datajud_tcc.client import (
    DatajudClient,
    InvalidResponseError,
)


ENDPOINT = "https://api.example.test/search"


def valid_response():
    return {
        "took": 2,
        "timed_out": False,
        "_shards": {"total": 1, "successful": 1, "failed": 0},
        "hits": {
            "total": {"value": 1, "relation": "eq"},
            "hits": [
                {
                    "_index": "processos-tjpr",
                    "_id": "TJPR_1",
                    "_source": {"id": "TJPR_1", "grau": "G1"},
                    "sort": ["TJPR_1"],
                }
            ],
        },
    }


def client_factory(**kwargs):
    return DatajudClient(
        endpoint=ENDPOINT,
        api_key="segredo-sintetico",
        connect_timeout_seconds=1,
        read_timeout_seconds=1,
        max_attempts=3,
        max_wait_seconds=30,
        **kwargs,
    )


@responses.activate
def test_search_sends_api_key_and_returns_page():
    responses.post(ENDPOINT, json=valid_response(), status=200)
    page = client_factory().search({"size": 100})
    assert page.next_cursor == ["TJPR_1"]
    assert page.total == {"value": 1, "relation": "eq"}
    assert responses.calls[0].request.headers["Authorization"] == "APIKey segredo-sintetico"


@pytest.mark.parametrize(
    "body",
    [
        "not-json",
        {"hits": {}},
        {**valid_response(), "timed_out": True},
        {**valid_response(), "_shards": {"failed": 1}},
        {**valid_response(), "hits": {**valid_response()["hits"], "hits": [{"_source": {}}]}},
    ],
)
@responses.activate
def test_invalid_success_responses_are_rejected(body):
    if isinstance(body, str):
        responses.post(ENDPOINT, body=body, status=200)
    else:
        responses.post(ENDPOINT, json=body, status=200)
    with pytest.raises(InvalidResponseError):
        client_factory().search({"size": 100})


@responses.activate
def test_429_honors_retry_after():
    waits = []
    responses.post(ENDPOINT, status=429, headers={"Retry-After": "7"})
    responses.post(ENDPOINT, json=valid_response(), status=200)
    client = client_factory(sleep=waits.append)
    client.search({"size": 100})
    assert waits == [7.0]
