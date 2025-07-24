import json
import logging
from typing import Any

from aiomqtt import Client, MqttError

from apps.settings.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MQTTPublisher:
    def __init__(self):
        self.client = Client(
            hostname=settings.MQTT_HOST,
            port=settings.MQTT_PORT,
            username=settings.MQTT_USER or None,
            password=settings.MQTT_PASSWORD or None,
        )

    async def connect(self):
        try:
            await self.client.__aenter__()
            logger.info("Connected to MQTT broker")
        except MqttError as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    async def disconnect(self):
        try:
            await self.client.__aexit__(None, None, None)
            logger.info("Disconnected from MQTT broker")
        except MqttError as e:
            logger.warning(f"Error during MQTT disconnect: {e}")

    async def publish_event(
        self, station_id: str, event_name: str, data: dict[str, Any]
    ):
        topic = f"stations/{station_id}/events"
        payload = {"event": event_name, **data}
        try:
            await self.client.publish(topic, json.dumps(payload))
            logger.debug(f"Published event to {topic}: {payload}")
        except MqttError as e:
            logger.error(f"MQTT publish failed: {e}")

    async def publish_telemetry(
        self, station_id: str, connector_number: int, data: dict[str, Any]
    ):
        topic = f"stations/{station_id}/telemetry"
        payload = {"connector_number": connector_number, **data}
        try:
            await self.client.publish(topic, json.dumps(payload))
            logger.debug(f"Published telemetry to {topic}: {payload}")
        except MqttError as e:
            logger.error(f"MQTT telemetry publish failed: {e}")
