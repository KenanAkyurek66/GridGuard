import json
import sys
from datetime import datetime, timezone
from typing import Any

import requests
from pymodbus.client import ModbusTcpClient


MODBUS_HOST = "127.0.0.1"
MODBUS_PORT = 5020
DEVICE_ID = 1

PANEL_ID = "LV-060"

REGISTER_START_ADDRESS = 0
REGISTER_COUNT = 7

GRIDGUARD_API_URL = (
    "http://127.0.0.1:8000/telemetry"
)


QUALITY_MAP = {
    0: "BAD",
    1: "DEGRADED",
    2: "GOOD",
}


def print_separator() -> None:
    print("-" * 72)


def decode_registers(
    registers: list[int],
) -> dict[str, Any]:
    if len(registers) < REGISTER_COUNT:
        raise ValueError(
            "Modbus response does not contain "
            "all expected registers."
        )

    current_a = (
        registers[0] / 10.0
    )

    cable_temperature_c = (
        registers[1] / 10.0
    )

    ambient_temperature_c = (
        registers[2] / 10.0
    )

    humidity_pct = (
        registers[3] / 10.0
    )

    pd_index = (
        registers[4] / 10.0
    )

    arc_detected = (
        registers[5] == 1
    )

    data_quality = QUALITY_MAP.get(
        registers[6],
        "BAD",
    )

    return {
        "panel_id": PANEL_ID,
        "timestamp": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "current_a": current_a,
        "cable_temperature_c":
            cable_temperature_c,
        "ambient_temperature_c":
            ambient_temperature_c,
        "humidity_pct":
            humidity_pct,
        "pd_index":
            pd_index,
        "arc_detected":
            arc_detected,
        "data_quality":
            data_quality,
    }


def send_to_gridguard(
    payload: dict[str, Any],
) -> bool:
    print()
    print("[FORWARDING TO GRIDGUARD]")
    print(
        f"POST {GRIDGUARD_API_URL}"
    )

    try:
        response = requests.post(
            GRIDGUARD_API_URL,
            json=payload,
            timeout=5,
        )

    except requests.RequestException as exc:
        print()
        print("[GRIDGUARD API ERROR]")
        print(exc)

        return False

    if response.ok:
        print()
        print("[GRIDGUARD ACCEPTED]")

        try:
            print(
                json.dumps(
                    response.json(),
                    indent=2,
                    ensure_ascii=False,
                )
            )

        except ValueError:
            print(response.text)

        return True

    print()
    print("[GRIDGUARD REJECTED]")
    print(
        f"HTTP {response.status_code}"
    )

    try:
        print(
            json.dumps(
                response.json(),
                indent=2,
                ensure_ascii=False,
            )
        )

    except ValueError:
        print(response.text)

    return False


def main() -> None:
    print()
    print("=" * 72)
    print(
        " GridGuard Modbus TCP Adapter"
    )
    print("=" * 72)

    print(
        f"Panel     : {PANEL_ID}"
    )

    print(
        f"PLC       : "
        f"{MODBUS_HOST}:{MODBUS_PORT}"
    )

    print(
        f"Device ID : {DEVICE_ID}"
    )

    print_separator()

    client = ModbusTcpClient(
        host=MODBUS_HOST,
        port=MODBUS_PORT,
        timeout=5,
    )

    print()
    print("[CONNECTING TO PLC]")

    if not client.connect():
        print()
        print("[MODBUS CONNECTION FAILED]")
        print(
            "Could not connect to the "
            "GridGuard mock PLC."
        )

        print(
            "Make sure Terminal 4 — "
            "MODBUS SERVER is running."
        )

        client.close()
        sys.exit(1)

    print("[MODBUS CONNECTED]")

    try:
        print()
        print("[READING HOLDING REGISTERS]")

        response = (
            client.read_holding_registers(
                address=(
                    REGISTER_START_ADDRESS
                ),
                count=REGISTER_COUNT,
                device_id=DEVICE_ID,
            )
        )

        if response.isError():
            print()
            print("[MODBUS READ ERROR]")
            print(response)

            sys.exit(1)

        registers = response.registers

        print()
        print("[RAW REGISTERS]")
        print(registers)

        payload = decode_registers(
            registers
        )

        print()
        print("[DECODED TELEMETRY]")

        print(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            )
        )

        success = send_to_gridguard(
            payload
        )

        if success:
            print()
            print_separator()

            print(
                "[MODBUS → GRIDGUARD "
                "PIPELINE SUCCESS]"
            )

            print_separator()

        else:
            sys.exit(1)

    except Exception as exc:
        print()
        print("[ADAPTER ERROR]")
        print(exc)

        sys.exit(1)

    finally:
        client.close()


if __name__ == "__main__":
    main()