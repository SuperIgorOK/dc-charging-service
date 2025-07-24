import pytest


@pytest.mark.asyncio
async def test_publish_event(fake_mqtt):
    await fake_mqtt.publish_event("station_id", "event_name", {"key": "value"})
    fake_mqtt.publish_event.assert_called_once()


@pytest.mark.asyncio
async def test_publish_telemetry(fake_mqtt):
    await fake_mqtt.publish_telemetry("station_id", 1, {"u1": 230})
    fake_mqtt.publish_telemetry.assert_called_once()
