import json
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883

PANEL_ID = "LV-050"

MQTT_TOPIC = f"gridguard/telemetry/{PANEL_ID}"

CLIENT_ID = "gridguard-mqtt-test-publisher"


def build_payload() -> dict:
    return {
        "panel_id": PANEL_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_a": 300.0,
        "cable_temperature_c": 44.0,
        "ambient_temperature_c": 30.0,
        "humidity_pct": 44.0,
        "pd_index": 12.0,
        "arc_detected": False,
        "data_quality": "GOOD",
    }


def main() -> None:
    print()
    print("=" * 68)
    print(" GridGuard MQTT Telemetry Publisher")
    print("=" * 68)

    payload = build_payload()

    client = mqtt.Client(
        callback_api_version=(
            mqtt.CallbackAPIVersion.VERSION2
        ),
        client_id=CLIENT_ID,
        protocol=mqtt.MQTTv311,
    )

    print(
        f"Connecting to MQTT broker "
        f"{MQTT_HOST}:{MQTT_PORT}..."
    )

    client.connect(
        MQTT_HOST,
        MQTT_PORT,
        keepalive=60,
    )

    client.loop_start()

    print("[CONNECTED]")
    print()
    print(f"Topic: {MQTT_TOPIC}")
    print()
    print("Payload:")
    print(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
    )

    result = client.publish(
        MQTT_TOPIC,
        payload=json.dumps(payload),
        qos=1,
    )

    result.wait_for_publish()

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print()
        print("[MQTT PUBLISHED]")
        print(
            f"Telemetry sent for {PANEL_ID}."
        )
    else:
        print()
        print("[MQTT PUBLISH FAILED]")
        print(f"Result code: {result.rc}")

    client.disconnect()
    client.loop_stop()

    print("=" * 68)


if __name__ == "__main__":
    main()