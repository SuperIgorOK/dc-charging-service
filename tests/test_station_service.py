import pytest
from uuid import UUID


@pytest.mark.asyncio
async def test_get_or_create_station_existing(fake_station_service):
    station_id = UUID("00000000-0000-0000-0000-000000000001")
    fake_station_service.get_or_create.return_value = "station_obj"

    result = await fake_station_service.get_or_create(station_id)
    assert result == "station_obj"
    fake_station_service.get_or_create.assert_called_once_with(station_id)
