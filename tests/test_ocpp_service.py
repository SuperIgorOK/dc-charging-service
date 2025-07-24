from unittest.mock import AsyncMock, MagicMock

import pytest
from datetime import datetime, timezone
from uuid import UUID

from pytest_mock import mocker

from apps.enums.session_enums import SessionStatusEnum

STATION_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
CONNECTOR_NUMBER = 1


@pytest.mark.asyncio
async def test_handle_authorize_creates_station(ocpp_service, fake_station_service):
    fake_station_service.get_or_create.return_value = object()

    await ocpp_service.handle_authorize(STATION_ID, "TEST_TOKEN")

    fake_station_service.get_or_create.assert_called_once_with(UUID(STATION_ID))


@pytest.mark.asyncio
async def test_handle_transaction_event_started(
    ocpp_service, fake_session_service, fake_event_service, fake_mqtt, mocker
):
    mocker.patch(
        "apps.schemas.redis_schema.ConnectorStatusRedisModel.find",
        return_value=MagicMock(first=AsyncMock(return_value=None)),
    )
    mocker.patch(
        "apps.schemas.redis_schema.ConnectorStatusRedisModel.save",
        new_callable=AsyncMock,
    )

    session_mock = type("Session", (), {"id": 1})()
    fake_session_service.start_session.return_value = session_mock

    payload = {
        "event_type": "Started",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evse": {"connector_id": CONNECTOR_NUMBER},
    }

    await ocpp_service.handle_transaction_event(STATION_ID, payload)

    fake_session_service.start_session.assert_called_once()
    fake_event_service.add_event.assert_called_once()
    fake_mqtt.publish_event.assert_called_once()


@pytest.mark.asyncio
async def test_handle_transaction_event_ended(
    ocpp_service, fake_session_service, fake_event_service, fake_mqtt, mocker
):
    mocker.patch(
        "apps.schemas.redis_schema.ConnectorStatusRedisModel.find",
        return_value=MagicMock(first=AsyncMock(return_value=None)),
    )
    mocker.patch(
        "apps.schemas.redis_schema.ConnectorStatusRedisModel.save",
        new_callable=AsyncMock,
    )

    session_mock = type("Session", (), {"id": 2})()
    fake_session_service.get_active_session.return_value = session_mock

    payload = {
        "event_type": "Ended",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evse": {"connector_id": CONNECTOR_NUMBER},
    }

    await ocpp_service.handle_transaction_event(STATION_ID, payload)

    fake_session_service.end_session.assert_called_once_with(
        session_mock,
        pytest.approx(
            datetime.fromisoformat(payload["timestamp"]).replace(tzinfo=None)
        ),
        SessionStatusEnum.finished,
    )
    fake_event_service.add_event.assert_called_once()
    fake_mqtt.publish_event.assert_called_once()


@pytest.mark.asyncio
async def test_handle_transaction_event_updated_calls_telemetry(ocpp_service, mocker):
    telemetry_mock = mocker.patch.object(
        ocpp_service, "_handle_telemetry", autospec=True
    )

    payload = {
        "event_type": "Updated",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evse": {"connector_id": CONNECTOR_NUMBER},
        "meter_value": [],
    }

    await ocpp_service.handle_transaction_event(STATION_ID, payload)

    telemetry_mock.assert_called_once_with(STATION_ID, CONNECTOR_NUMBER, payload)


@pytest.mark.asyncio
async def test_handle_telemetry_parses_and_publishes(ocpp_service, fake_mqtt):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evse": {"connector_id": CONNECTOR_NUMBER},
        "meter_value": [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sampled_value": [
                    {"measurand": "Voltage", "phase": "L1", "value": 230},
                    {"measurand": "Voltage", "phase": "L2", "value": 231},
                    {"measurand": "Voltage", "phase": "L3", "value": 232},
                    {"measurand": "Current.Import", "value": 15},
                ],
            }
        ],
        "custom_data": {
            "temperature": 44,
        },
    }

    await ocpp_service._handle_telemetry(STATION_ID, CONNECTOR_NUMBER, payload)

    fake_mqtt.publish_telemetry.assert_called_once()
    args = fake_mqtt.publish_telemetry.call_args[0]
    telemetry_data = args[2]
    assert telemetry_data["u1"] == 230
    assert telemetry_data["u2"] == 231
    assert telemetry_data["u3"] == 232
    assert telemetry_data["input_amperage"] == 15
    assert telemetry_data["temperature"] == 44
