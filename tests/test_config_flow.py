"""Test the Victron GX modbusTCP config flow."""

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant import config_entries
from homeassistant.components.victron.config_flow import CannotConnect, InvalidAuth
from homeassistant.components.victron.const import (
    CONF_ADVANCED_OPTIONS,
    CONF_INTERVAL,
    DOMAIN,
)
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import HomeAssistantError


@pytest.mark.usefixtures("mock_victron_client")
async def test_full_flow(hass: HomeAssistant) -> None:
    """Test the full flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert not result["errors"]

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: "1.1.1.1",
            CONF_PORT: 502,
            CONF_INTERVAL: 30,
            CONF_ADVANCED_OPTIONS: False,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "victron"
    assert result["options"] == {
        CONF_HOST: "1.1.1.1",
        CONF_PORT: 502,
        CONF_INTERVAL: 30,
        CONF_ADVANCED_OPTIONS: False,
    }


@pytest.mark.usefixtures("mock_victron_client")
async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "homeassistant.components.victron.config_flow.validate_input",
        new=AsyncMock(side_effect=CannotConnect),
    ) as mock_get:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "1.1.1.1",
                CONF_PORT: 502,
                CONF_INTERVAL: 30,
                CONF_ADVANCED_OPTIONS: False,
            },
        )
        mock_get.assert_called_once()

    assert result2["type"] is FlowResultType.FORM
    assert result2["step_id"] == "user"
    assert result2["errors"] == {"base": "cannot_connect"}


@pytest.mark.usefixtures("mock_victron_client")
async def test_form_invalid_auth(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "homeassistant.components.victron.config_flow.validate_input",
        new=AsyncMock(side_effect=InvalidAuth),
    ) as mock_get:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "1.1.1.1",
                CONF_PORT: 502,
                CONF_INTERVAL: 30,
                CONF_ADVANCED_OPTIONS: False,
            },
        )
        mock_get.assert_called_once()

    assert result2["type"] is FlowResultType.FORM
    assert result2["step_id"] == "user"
    assert result2["errors"] == {"base": "invalid_auth"}


@pytest.mark.usefixtures("mock_victron_client")
async def test_form_unknown_exception(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    with patch(
        "homeassistant.components.victron.config_flow.validate_input",
        new=AsyncMock(side_effect=HomeAssistantError),
    ) as mock_get:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "1.1.1.1",
                CONF_PORT: 502,
                CONF_INTERVAL: 30,
                CONF_ADVANCED_OPTIONS: False,
            },
        )
        mock_get.assert_called_once()

    assert result2["type"] is FlowResultType.FORM
    assert result2["step_id"] == "user"
    assert result2["errors"] == {"base": "unknown"}
