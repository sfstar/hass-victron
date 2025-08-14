"""Common fixtures for the Victron GX modbusTCP tests."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from homeassistant.components.victron import DOMAIN
from homeassistant.const import CONF_HOST, CONF_PORT

from tests.common import MockConfigEntry


@pytest.fixture
def mock_victron_client() -> Generator[MagicMock]:
    """Mock a victron client."""
    with (
        patch(
            "homeassistant.components.victron.config_flow.ModbusTcpClient",
        ) as mock_client,
    ):
        client = mock_client.return_value
        client.update.return_value = True
        yield client


@pytest.fixture(autouse=True)
def mock_modbus() -> Generator[MagicMock]:
    """Mock a modbus client."""
    with patch(
        "homeassistant.components.victron.config_flow.ModbusTcpClient",
        autospec=True,
    ) as mock_client:
        yield mock_client


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Mock a config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="victron",
        data={CONF_HOST: "1.1.1.1", CONF_PORT: 502},
    )
