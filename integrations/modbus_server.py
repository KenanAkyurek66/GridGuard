from pymodbus.server import StartTcpServer
from pymodbus.simulator import DataType, SimData, SimDevice


MODBUS_HOST = "127.0.0.1"
MODBUS_PORT = 5020
DEVICE_ID = 1


# ---------------------------------------------------------
# GridGuard demo register map
# ---------------------------------------------------------
#
# Holding Register 0 -> Current x10
# Holding Register 1 -> Cable temperature x10
# Holding Register 2 -> Ambient temperature x10
# Holding Register 3 -> Humidity x10
# Holding Register 4 -> Partial discharge index x10
# Holding Register 5 -> Arc detected
#                       0 = CLEAR
#                       1 = DETECTED
# Holding Register 6 -> Data quality
#                       0 = BAD
#                       1 = DEGRADED
#                       2 = GOOD
#
# Example:
# Current = 3000 -> 300.0 A
# Cable temperature = 440 -> 44.0 °C
# ---------------------------------------------------------


REGISTER_VALUES = [
    3000,  # Current = 300.0 A
    440,   # Cable temperature = 44.0 °C
    300,   # Ambient temperature = 30.0 °C
    440,   # Humidity = 44.0 %
    120,   # PD index = 12.0
    0,     # Arc detection = CLEAR
    2,     # Data quality = GOOD
]


def build_device() -> SimDevice:
    """
    Build a single Modbus device using shared registers.

    Shared-register mode avoids the need to define separate
    coil/discrete/input-register blocks for this GridGuard demo.
    """

    register_block = SimData(
        address=0,
        values=REGISTER_VALUES,
        datatype=DataType.REGISTERS,
    )

    device = SimDevice(
        id=DEVICE_ID,
        simdata=[
            register_block,
        ],
    )

    return device


def print_register_map() -> None:
    print()
    print("=" * 72)
    print(" GridGuard Mock Modbus PLC")
    print("=" * 72)

    print(f"Host      : {MODBUS_HOST}")
    print(f"Port      : {MODBUS_PORT}")
    print(f"Device ID : {DEVICE_ID}")

    print()
    print("Simulated asset: LV-060")

    print()
    print("Holding Register Map")
    print("-" * 72)

    print(
        f"HR0  Current             : "
        f"{REGISTER_VALUES[0] / 10:.1f} A"
    )

    print(
        f"HR1  Cable Temperature   : "
        f"{REGISTER_VALUES[1] / 10:.1f} °C"
    )

    print(
        f"HR2  Ambient Temperature : "
        f"{REGISTER_VALUES[2] / 10:.1f} °C"
    )

    print(
        f"HR3  Humidity            : "
        f"{REGISTER_VALUES[3] / 10:.1f} %"
    )

    print(
        f"HR4  PD Index            : "
        f"{REGISTER_VALUES[4] / 10:.1f}"
    )

    print(
        f"HR5  Arc Detection       : "
        f"{'DETECTED' if REGISTER_VALUES[5] else 'CLEAR'}"
    )

    quality_labels = {
        0: "BAD",
        1: "DEGRADED",
        2: "GOOD",
    }

    print(
        f"HR6  Data Quality        : "
        f"{quality_labels.get(REGISTER_VALUES[6], 'UNKNOWN')}"
    )

    print("-" * 72)

    print()
    print("[MODBUS SERVER READY]")
    print(
        f"Listening on "
        f"{MODBUS_HOST}:{MODBUS_PORT}"
    )

    print()
    print(
        "Press Ctrl+C to stop the server."
    )

    print("=" * 72)
    print()


def main() -> None:
    device = build_device()

    print_register_map()

    try:
        StartTcpServer(
            context=device,
            address=(
                MODBUS_HOST,
                MODBUS_PORT,
            ),
        )

    except KeyboardInterrupt:
        print()
        print(
            "GridGuard Modbus server stopped."
        )


if __name__ == "__main__":
    main()