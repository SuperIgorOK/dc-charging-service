import pytest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

import apps.services.ocpp_service as ocpp_module


@pytest.fixture
def db_session():
    mock = AsyncMock(spec=AsyncSession)
    # Здесь можно настроить поведение, если нужно, например commit/rollback
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    return mock


@pytest.fixture
def fake_redis(mocker):
    redis_mock = mocker.Mock()
    # если в коде вызывается redis.get/set/… - добавь мок-методы здесь
    return redis_mock


@pytest.fixture
def fake_station_service(mocker):
    service = mocker.Mock()
    service.get_or_create = AsyncMock()
    return service


@pytest.fixture
def fake_session_service(mocker):
    service = mocker.Mock()
    service.start_session = AsyncMock()
    service.get_active_session = AsyncMock()
    service.end_session = AsyncMock()
    return service


@pytest.fixture
def fake_event_service(mocker):
    service = mocker.Mock()
    service.add_event = AsyncMock()
    return service


@pytest.fixture
def fake_mqtt(mocker):
    service = mocker.Mock()
    service.publish_event = AsyncMock()
    service.publish_telemetry = AsyncMock()
    return service


@pytest.fixture
def ocpp_service(
    db_session,
    fake_redis,
    fake_mqtt,
    fake_station_service,
    fake_session_service,
    fake_event_service,
):
    from apps.services.ocpp_service import OCPPService

    return OCPPService(
        db=db_session,
        redis=fake_redis,
        station_service=fake_station_service,
        session_service=fake_session_service,
        event_service=fake_event_service,
        mqtt=fake_mqtt,
    )
