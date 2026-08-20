"""Root pytest config. The dummy env must live here because the truenas_mcp.config
singleton is instantiated at import of client/server, so vars must be set before
any test module imports."""

import os

import pytest


def pytest_collection_modifyitems(items):
    if os.getenv("CI"):
        skip = pytest.mark.skip(reason="skipped in CI")
        for item in items:
            if "skip_in_ci" in item.keywords:
                item.add_marker(skip)


# Dummy values so suites collect without a .env; real shell/.env win via setdefault.
os.environ.setdefault("TRUENAS_BASE_URL", "https://truenas.example.com")
os.environ.setdefault("TRUENAS_API_KEY", "test-key")
