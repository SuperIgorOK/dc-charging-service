import asyncio
import websockets
from datetime import datetime, timezone

from ocpp.v201 import ChargePoint as CP
from ocpp.v201 import call, enums, datatypes
from ocpp.v201.datatypes import SampledValueType, MeterValueType

SERVER_URI = "ws://localhost:9000/3fa85f64-5717-4562-b3fc-2c963f66afa6"


class ChargePoint(CP):

    async def send_authorize(self, id_token_value: str):
        id_token = datatypes.IdTokenType(
            id_token=id_token_value,
            type=enums.IdTokenEnumType.central,
        )
        request = call.Authorize(id_token=id_token)
        response = await self.call(request)
        print("Authorize response:", response)

    async def send_transaction_event(
        self,
        event_type: enums.TransactionEventEnumType,
        trigger_reason: enums.TriggerReasonEnumType,
        seq_no: int,
        transaction_id: int,
        timestamp: str,
        connector_number: int,
        telemetry: dict | None = None,
    ):
        transaction_info = datatypes.TransactionType(transaction_id=str(transaction_id))
        evse = datatypes.EVSEType(id=1, connector_id=connector_number)

        meter_values = []
        custom_data = None
        if telemetry:
            sampled_values = []
            if "u1" in telemetry:
                sampled_values.append(
                    SampledValueType(
                        value=telemetry["u1"], measurand="Voltage", phase="L1"
                    )
                )
            if "u2" in telemetry:
                sampled_values.append(
                    SampledValueType(
                        value=telemetry["u2"], measurand="Voltage", phase="L2"
                    )
                )
            if "u3" in telemetry:
                sampled_values.append(
                    SampledValueType(
                        value=telemetry["u3"], measurand="Voltage", phase="L3"
                    )
                )
            if "input_amperage" in telemetry:
                sampled_values.append(
                    SampledValueType(
                        value=telemetry["input_amperage"],
                        measurand="Current.Import",
                    )
                )

            if "temperature" in telemetry:
                custom_data = {
                    "vendorId": "my_vendor_id",
                    "temperature": telemetry["temperature"],
                }

            if sampled_values:
                meter_values.append(
                    MeterValueType(timestamp=timestamp, sampled_value=sampled_values)
                )

        payload = call.TransactionEvent(
            event_type=event_type,
            timestamp=timestamp,
            trigger_reason=trigger_reason,
            seq_no=seq_no,
            transaction_info=transaction_info,
            evse=evse,
            meter_value=meter_values or None,
            custom_data=custom_data,
        )
        response = await self.call(payload)
        print(f"TransactionEvent {event_type} response:", response)


async def main():
    async with websockets.connect(SERVER_URI, subprotocols=["ocpp2.0.1"]) as websocket:
        cp = ChargePoint("CP_001", websocket)

        asyncio.create_task(cp.start())

        await cp.send_authorize("TEST_TOKEN")

        now = datetime.now(timezone.utc).isoformat()

        await cp.send_transaction_event(
            event_type=enums.TransactionEventEnumType.started,
            trigger_reason=enums.TriggerReasonEnumType.authorized,
            seq_no=1,
            transaction_id=1234,
            timestamp=now,
            connector_number=1,
        )

        for i in range(1, 6):
            await asyncio.sleep(3)
            now = datetime.now(timezone.utc).isoformat()
            telemetry = {
                "u1": 230.0 + i,
                "u2": 231.0 + i,
                "u3": 229.5 + i,
                "input_amperage": 16 + i,
                "temperature": 40 + i,
            }
            await cp.send_transaction_event(
                event_type=enums.TransactionEventEnumType.updated,
                trigger_reason=enums.TriggerReasonEnumType.meter_value_clock,
                seq_no=1 + i,
                transaction_id=1234,
                timestamp=now,
                connector_number=1,
                telemetry=telemetry,
            )

        now = datetime.now(timezone.utc).isoformat()

        await cp.send_transaction_event(
            event_type=enums.TransactionEventEnumType.ended,
            trigger_reason=enums.TriggerReasonEnumType.trigger,
            seq_no=10,
            transaction_id=1234,
            timestamp=now,
            connector_number=1,
        )

        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
