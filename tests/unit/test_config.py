"""Unit tests for TrueNAS config validation."""

import pytest

from truenas_mcp.config import Config


def test_https_required_by_default():
    with pytest.raises(ValueError, match="HTTPS"):
        Config(
            truenas_base_url="http://truenas.selfhosted.svc.cluster.local",
            truenas_api_key="key",
        )


def test_insecure_http_opt_in():
    c = Config(
        truenas_base_url="http://truenas.selfhosted.svc.cluster.local",
        truenas_api_key="key",
        allow_insecure_http=True,
    )
    assert c.truenas_base_url == "http://truenas.selfhosted.svc.cluster.local"


def test_insecure_http_from_env(monkeypatch):
    monkeypatch.setenv("ALLOW_INSECURE_HTTP", "true")
    c = Config(
        truenas_base_url="http://truenas.selfhosted.svc.cluster.local",
        truenas_api_key="key",
    )
    assert c.allow_insecure_http is True


def test_missing_value_raises():
    with pytest.raises(ValueError, match="TRUENAS_BASE_URL"):
        Config(truenas_api_key="key", truenas_base_url=None)
