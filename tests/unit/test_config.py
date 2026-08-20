"""Unit tests for TrueNAS config validation."""

import pytest

from truenas_mcp.config import Config


def test_uri_required():
    with pytest.raises(ValueError, match="TRUENAS_URI"):
        Config(truenas_api_key="key", truenas_uri=None)


def test_api_key_required():
    with pytest.raises(ValueError, match="TRUENAS_API_KEY"):
        Config(truenas_uri="ws://host/api/current", truenas_api_key=None)


def test_http_uri_rejected():
    with pytest.raises(ValueError, match="must be a ws:// or wss://"):
        Config(truenas_uri="http://truenas/api/current", truenas_api_key="key")


def test_ws_uri_accepted():
    c = Config(truenas_uri="ws://truenas/api/current", truenas_api_key="key")
    assert c.truenas_uri == "ws://truenas/api/current"


def test_wss_with_verify_false_allowed():
    # self-signed home TrueNAS behind wss needs verification off
    c = Config(truenas_uri="wss://asc.internal/api/current", truenas_api_key="key", truenas_verify_ssl=False)
    assert c.truenas_verify_ssl is False
