import logging
from datetime import datetime, timezone
from uuid import UUID

from aredis_om import NotFoundError
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from apps.enums.session_enums import SessionStatusEnum
from apps.mqtt.publisher import MQTTPublisher
from apps.schemas.redis_schema import ConnectorStatusRedisModel
from apps.services.event_service import EventService
from apps.services.session_service import SessionService
from apps.services.station_service import StationService

logger = logging.getLogger(__name__)


class OCPPService:
    def __init__(
        self,
        db: AsyncSession,
        redis: Redis,
        station_service: StationService,
        session_service: SessionService,
        event_service: EventService,
        mqtt: MQTTPublisher,
    ):
        self.db = db
        self.redis = redis
        self.station_service = station_service
        self.session_service = session_service
        self.event_service = event_service
        self.mqtt = mqtt

    async def handle_authorize(self, station_id: str, id_token: str):
        station_uuid = UUID(station_id)
        await self.station_service.get_or_create(station_uuid)

        logger.info(
            f"Authorize accepted for station {station_id} with token: {id_token}"
        )

    async def handle_transaction_event(self, station_id: str, payload: dict):
        station_uuid = UUID(station_id)
        event_type = payload.get("event_type")
        timestamp = datetime.fromisoformat(payload["timestamp"]).replace(tzinfo=None)
        connector_number = payload["evse"]["connector_id"]

        logger.debug(
            f"TransactionEvent: {event_type} at {timestamp} for {station_id}:{connector_number}"
        )

        try:
            if event_type == "Started":
                session = await self.session_service.start_session(
                    station_uuid, connector_number, timestamp
                )
                await self._add_session_event(session.id, timestamp, event_type)
                await self._update_connector_status(
                    station_id, connector_number, "occupied"
                )
                await self._publish_mqtt_event(
                    station_id,
                    "session_started",
                    session.id,
                    connector_number,
                    timestamp,
                )
                logger.info(
                    f"Started session {session.id} for {station_id}:{connector_number}"
                )

            elif event_type == "Ended":
                session = await self.session_service.get_active_session(
                    station_uuid, connector_number
                )
                if not session:
                    logger.warning(
                        f"No active session for {station_id}:{connector_number}"
                    )
                    return
                status = SessionStatusEnum.finished
                await self.session_service.end_session(session, timestamp, status)
                await self._add_session_event(session.id, timestamp, event_type)
                await self._update_connector_status(
                    station_id, connector_number, "available"
                )
                await self._publish_mqtt_event(
                    station_id,
                    "session_finished",
                    session.id,
                    connector_number,
                    timestamp,
                )
                logger.info(
                    f"Ended session {session.id} for {station_id}:{connector_number}"
                )

            elif event_type == "Updated":
                await self._handle_telemetry(station_id, connector_number, payload)

            await self.db.commit()

        except Exception:
            logger.exception("Failed to handle transaction event")
            await self.db.rollback()
            raise

    async def _add_session_event(
        self, session_id: int, timestamp: datetime, event_type: str
    ):
        timestamp = timestamp.replace(tzinfo=None)
        await self.event_service.add_event(session_id, timestamp, event_type)

    @staticmethod
    async def _update_connector_status(
        station_id: UUID, connector_number: int, new_status: str
    ):
        try:
            connector_status = await ConnectorStatusRedisModel.find(
                ConnectorStatusRedisModel.station_id == station_id,
                ConnectorStatusRedisModel.connector_number == connector_number,
            ).first()
        except NotFoundError:
            connector_status = None

        if connector_status:
            connector_status.status = new_status
            connector_status.updated_at = datetime.now(tz=timezone.utc)
            await connector_status.save()
        else:
            connector_status = ConnectorStatusRedisModel(
                station_id=station_id,
                connector_number=connector_number,  # поменял тут на правильное поле
                status=new_status,
                updated_at=datetime.now(tz=timezone.utc),
            )
            await connector_status.save()

    async def _publish_mqtt_event(
        self,
        station_id: str,
        event_name: str,
        session_id: int,
        connector_number: int,
        timestamp: datetime,
    ):
        timestamp = timestamp.replace(tzinfo=None)
        await self.mqtt.publish_event(
            station_id,
            event_name,
            {
                "session_id": str(session_id),
                "connector_number": connector_number,
                "timestamp": timestamp.isoformat(),
                "station_id": station_id,
            },
        )

    async def _handle_telemetry(
        self, station_id: str, connector_number: int, payload: dict
    ):
        """
        Извлекает телеметрию из meter_value и публикует в MQTT.
        """
        logger.debug(f"Raw telemetry payload: {payload}")
        meter_values = payload.get("meter_value", [])
        if not meter_values:
            return

        latest = meter_values[-1]
        sampled_values = latest.get("sampled_value", [])
        telemetry_data = {
            "connector_number": connector_number,
            "timestamp": payload["timestamp"],
        }

        for sv in sampled_values:
            measurand = sv.get("measurand")
            value = float(sv.get("value"))
            phase = sv.get("phase")

            if measurand == "Voltage":
                if phase == "L1":
                    telemetry_data["u1"] = value
                elif phase == "L2":
                    telemetry_data["u2"] = value
                elif phase == "L3":
                    telemetry_data["u3"] = value
            elif measurand == "Current.Import":
                telemetry_data["input_amperage"] = value

        custom_data = payload.get("custom_data", {})
        logger.info(f"CustomData in payload: {custom_data}")
        temperature = custom_data.get("temperature")
        if temperature is not None:
            telemetry_data["temperature"] = float(temperature)

        logger.debug(f"Prepared telemetry_data: {telemetry_data}")
        await self.mqtt.publish_telemetry(station_id, connector_number, telemetry_data)
        logger.info(
            f"Published telemetry for {station_id}:{connector_number} -> {telemetry_data}"
        )
