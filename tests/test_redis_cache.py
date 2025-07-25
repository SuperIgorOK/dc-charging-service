import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_update_connector_status_new(mocker):
    mock_find = mocker.patch(
        "apps.schemas.redis_schema.ConnectorStatusRedisModel.find",
        return_value=MagicMock(first=AsyncMock(return_value=None)),
    )
    mock_save = mocker.patch(
        "apps.schemas.redis_schema.ConnectorStatusRedisModel.save",
        new_callable=AsyncMock,
    )

    from apps.services.ocpp_service import OCPPService

    service = OCPPService(
        db=None,
        redis=None,
        station_service=None,
        session_service=None,
        event_service=None,
        mqtt=None,
    )
    await service._update_connector_status("station_id", 1, "available")

    mock_find.assert_called_once()
    mock_save.assert_called_once()
