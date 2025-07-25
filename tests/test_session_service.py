import pytest
from datetime import datetime
from apps.enums.session_enums import SessionStatusEnum


@pytest.mark.asyncio
async def test_start_session(fake_session_service):
    fake_session_service.start_session.return_value = "session_obj"
    result = await fake_session_service.start_session(
        "station_uuid", 1, datetime.utcnow()
    )
    assert result == "session_obj"
    fake_session_service.start_session.assert_called_once()


@pytest.mark.asyncio
async def test_end_session(fake_session_service):
    session_mock = object()
    await fake_session_service.end_session(
        session_mock, datetime.utcnow(), SessionStatusEnum.finished
    )
    fake_session_service.end_session.assert_called_once()
