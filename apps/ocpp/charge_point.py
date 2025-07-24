from ocpp.v201 import ChargePoint as CP
from ocpp.v201 import call_result
from ocpp.v201.datatypes import IdTokenInfoType
from ocpp.routing import on

from apps.services.ocpp_service import OCPPService


class ChargePoint(CP):
    def __init__(self, id, websocket, service: OCPPService):
        super().__init__(id, websocket)
        self.service = service

    @on("Authorize")
    async def on_authorize(self, id_token):
        await self.service.handle_authorize(self.id, id_token)
        return call_result.Authorize(id_token_info=IdTokenInfoType(status="Accepted"))

    @on("TransactionEvent")
    async def on_transaction_event(self, **kwargs):
        await self.service.handle_transaction_event(self.id, kwargs)
        return call_result.TransactionEvent(
            total_cost=0,
            charging_priority=1,
            id_token_info=IdTokenInfoType(status="Accepted"),
        )
