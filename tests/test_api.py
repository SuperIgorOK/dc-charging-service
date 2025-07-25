import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID
from apps.schemas.redis_schema import ConnectorStatusRedisModel
from apps.services.station_service import StationService
from apps.models import Station  # твоя модель станции


@pytest.mark.asyncio
async def test_get_station_status(mocker):
    station_id = UUID("00000000-0000-0000-0000-000000000001")

    # Мокаем результат запроса SQLAlchemy
    fake_station = Station(id=station_id, name="Test Station", status="Available")

    # Мокаем объект результата execute()
    mock_result = MagicMock()
    mock_result.scalars.return_value.one_or_none.return_value = fake_station

    # Мокаем сессию и её метод execute
    mock_db_session = MagicMock()
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    # Мокаем Redis find().all()
    fake_connector1 = MagicMock(
        connector_number=1, status="available", updated_at="2025-07-24T12:00:00Z"
    )
    fake_connector2 = MagicMock(
        connector_number=2, status="fault", updated_at="2025-07-24T12:05:00Z"
    )

    find_mock = MagicMock()
    find_mock.all = AsyncMock(return_value=[fake_connector1, fake_connector2])

    mocker.patch.object(ConnectorStatusRedisModel, "find", return_value=find_mock)

    # Создаем сервис с мокнутой сессией
    service = StationService(db=mock_db_session)

    result = await service.get_station_status(station_id)

    assert result.station_id == str(station_id)
    assert result.name == "Test Station"
    assert len(result.connectors) == 2
    assert result.connectors[0].connector_number == 1
    assert result.connectors[1].status == "fault"
