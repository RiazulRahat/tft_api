# test_APIs.py

import pytest
import pathlib
import sys

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from utilities.get_APIs import TftAPIClient


def test_init_raises_without_api_key(monkeypatch):
    """TftAPIClient should raise ValueError if X-RIOT-TOKEN is not set."""
    monkeypatch.delenv("X-RIOT-TOKEN", raising=False)

    with pytest.raises(ValueError):
        TftAPIClient()


def test_get_puuid_from_riot_id(monkeypatch):
    """get_puuid_from_riot_id should call the correct URL and return the puuid."""
    # Arrange: fake API key
    monkeypatch.setenv("X-RIOT-TOKEN", "test-api-key")
    client = TftAPIClient()

    captured = {}

    # Fake response object
    class DummyResponse:
        def json(self):
            return {"puuid": "fake-puuid"}

    # Monkeypatch the internal _get_with_rate_limit method
    def fake_get_with_rate_limit(url, params=None):
        captured["url"] = url
        captured["params"] = params
        return DummyResponse()

    monkeypatch.setattr(client, "_get_with_rate_limit", fake_get_with_rate_limit)

    # Act
    puuid = client.get_puuid_from_riot_id("MyName", "EUW")

    # Assert
    assert puuid == "fake-puuid"
    expected_url = (
        client.base_url + "/riot/account/v1/accounts/by-riot-id/MyName/EUW"
    )
    assert captured["url"] == expected_url
    assert captured["params"] is None


def test_get_matches_from_puuid(monkeypatch):
    """get_matches_from_puuid should pass query params and return a list."""
    monkeypatch.setenv("X-RIOT-TOKEN", "test-api-key")
    client = TftAPIClient()

    captured = {}

    class DummyResponse:
        def json(self):
            return ["match1", "match2"]

    def fake_get_with_rate_limit(url, params=None):
        captured["url"] = url
        captured["params"] = params
        return DummyResponse()

    monkeypatch.setattr(client, "_get_with_rate_limit", fake_get_with_rate_limit)

    matches = client.get_matches_from_puuid("fake-puuid", count=10, start=5)

    expected_url = client.base_url + "/tft/match/v1/matches/by-puuid/fake-puuid/ids"
    assert captured["url"] == expected_url
    assert captured["params"] == {"count": 10, "start": 5}
    assert matches == ["match1", "match2"]


def test_get_match_details(monkeypatch):
    """get_match_details should return (metadata, info) from the response JSON."""
    monkeypatch.setenv("X-RIOT-TOKEN", "test-api-key")
    client = TftAPIClient()

    captured = {}

    class DummyResponse:
        def json(self):
            return {
                "metadata": {"match_id": "match123"},
                "info": {"game_datetime": 1234567890},
            }

    def fake_get_with_rate_limit(url, params=None):
        captured["url"] = url
        captured["params"] = params
        return DummyResponse()

    monkeypatch.setattr(client, "_get_with_rate_limit", fake_get_with_rate_limit)

    metadata, info = client.get_match_details("match123")

    expected_url = client.base_url + "/tft/match/v1/matches/match123"
    assert captured["url"] == expected_url
    assert captured["params"] is None
    assert metadata == {"match_id": "match123"}
    assert info == {"game_datetime": 1234567890}
