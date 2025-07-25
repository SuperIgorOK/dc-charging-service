import asyncio
import logging
import websockets

from redis.asyncio import Redis

from apps.settings.config import get_settings
from apps.settings.database import get_session_context
from apps.mqtt.publisher import MQTTPublisher
from apps.services.event_service import EventService
from apps.services.ocpp_service import OCPPService
from apps.ocpp.charge_point import ChargePoint
from apps.services.session_service import SessionService
from apps.services.station_service import StationService

settings = get_settings()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class OCPPWebsocketServer:
    def __init__(self):
        self.websocket_host = settings.WEBSOCKET_HOST
        self.websocket_port = settings.WEBSOCKET_PORT
        self.active_connections: dict[str, ChargePoint] = {}

        self.redis = Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
        )

    async def _on_connect(self, websocket, path: str):
        print(f"Connected: path={path}")
        station_id = path.strip("/")

        async with get_session_context() as db:
            mqtt = MQTTPublisher()
            await mqtt.connect()

            station_service = StationService(db)
            session_service = SessionService(db)
            event_service = EventService(db)

            ocpp_service = OCPPService(
                db=db,
                redis=self.redis,
                station_service=station_service,
                session_service=session_service,
                event_service=event_service,
                mqtt=mqtt,
            )

            charge_point = ChargePoint(station_id, websocket, ocpp_service)
            self.active_connections[station_id] = charge_point

            logger.info(f"Station connected: {station_id}")
            try:
                await charge_point.start()
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"Station disconnected: {station_id}")
                await self._on_disconnect(station_id)

    async def _on_disconnect(self, station_id: str):
        if station_id in self.active_connections:
            del self.active_connections[station_id]
        logger.info(f"Connection {station_id} closed.")

    async def start(self):
        server = await websockets.serve(
            self._on_connect,
            self.websocket_host,
            self.websocket_port,
            subprotocols=["ocpp2.0.1"],
            ping_interval=None,
        )

        logger.info(
            f"OCPP server started on ws://{self.websocket_host}:{self.websocket_port}"
        )
        await server.wait_closed()

    async def stop(self):
        for station_id in list(self.active_connections.keys()):
            await self._on_disconnect(station_id)
        logger.info("Server stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(OCPPWebsocketServer().start())
    except KeyboardInterrupt:
        logger.info("Stopping OCPP server...")
