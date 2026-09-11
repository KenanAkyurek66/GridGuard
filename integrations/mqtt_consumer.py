import json
import sys
from typing import Any

import paho.mqtt.client as mqtt
import requests


MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "gridguard/telemetry/#"

GRIDGUARD_API_URL = "http://127.0.0.1:8000/telemetry"

CLIENT_ID = "gridguard-mqtt-consumer"


def print_separator() -> None:
    print("-" * 72)


def forward_to_gridguard(payload: dict[str, Any]) -> None:
    """
    Forward the MQTT telemetry payload to the existing GridGuard
    telemetry REST endpoint.

    The FastAPI telemetry endpoint remains the single ingestion point
    for validation, persistence, risk assessment and alarm handling.
    """

    try:
        response = requests.post(
            GRIDGUARD_API_URL,
            json=payload,
            timeout=5,
        )

    except requests.RequestException as exc:
        print("[API ERROR]")
        print(f"Could not reach GridGuard API: {exc}")
        return

    if response.ok:
        print("[GRIDGUARD ACCEPTED]")

        try:
            result = response.json()
            print(
                json.dumps(
                    result,
                    indent=2,
                    ensure_ascii=False,
                )
            )

        except ValueError:
            print(response.text)

        return

    print("[GRIDGUARD REJECTED]")
    print(f"HTTP {response.status_code}")

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


def on_connect(
    client: mqtt.Client,
    userdata: Any,
    flags: dict[str, Any],
    reason_code: Any,
    properties: Any = None,
) -> None:
    print_separator()

    if reason_code == 0:
        print("[MQTT CONNECTED]")
        print(
            f"Broker : {MQTT_HOST}:{MQTT_PORT}"
        )
        print(
            f"Topic  : {MQTT_TOPIC}"
        )

        client.subscribe(
            MQTT_TOPIC,
            qos=1,
        )

        print("[MQTT SUBSCRIBED]")
        print(
            "Waiting for GridGuard telemetry..."
        )

    else:
        print("[MQTT CONNECTION FAILED]")
        print(
            f"Reason code: {reason_code}"
        )

    print_separator()


def on_disconnect(
    client: mqtt.Client,
    userdata: Any,
    disconnect_flags: Any,
    reason_code: Any,
    properties: Any = None,
) -> None:
    print()
    print("[MQTT DISCONNECTED]")
    print(
        f"Reason code: {reason_code}"
    )


def on_message(
    client: mqtt.Client,
    userdata: Any,
    message: mqtt.MQTTMessage,
) -> None:
    print()
    print_separator()

    print("[MQTT MESSAGE]")
    print(
        f"Topic : {message.topic}"
    )
    print(
        f"QoS   : {message.qos}"
    )

    try:
        raw_payload = (
            message.payload.decode(
                "utf-8"
            )
        )

    except UnicodeDecodeError:
        print("[INVALID PAYLOAD]")
        print(
            "Payload is not valid UTF-8."
        )
        print_separator()
        return

    try:
        payload = json.loads(
            raw_payload
        )

    except json.JSONDecodeError as exc:
        print("[INVALID JSON]")
        print(exc)
        print_separator()
        return

    if not isinstance(
        payload,
        dict,
    ):
        print("[INVALID PAYLOAD]")
        print(
            "Telemetry payload must be "
            "a JSON object."
        )
        print_separator()
        return

    print("[PAYLOAD]")

    print(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
    )

    forward_to_gridguard(
        payload
    )

    print_separator()


def build_client() -> mqtt.Client:
    client = mqtt.Client(
        callback_api_version=(
            mqtt.CallbackAPIVersion.VERSION2
        ),
        client_id=CLIENT_ID,
        protocol=mqtt.MQTTv311,
    )

    client.on_connect = (
        on_connect
    )

    client.on_disconnect = (
        on_disconnect
    )

    client.on_message = (
        on_message
    )

    return client


def main() -> None:
    print()
    print("=" * 72)
    print(
        " GridGuard MQTT Telemetry Consumer"
    )
    print("=" * 72)

    client = build_client()

    try:
        client.connect(
            MQTT_HOST,
            MQTT_PORT,
            keepalive=60,
        )

        client.loop_forever()

    except KeyboardInterrupt:
        print()
        print(
            "Stopping MQTT consumer..."
        )

        client.disconnect()

    except ConnectionRefusedError:
        print()
        print("[BROKER ERROR]")
        print(
            "Could not connect to Mosquitto "
            f"at {MQTT_HOST}:{MQTT_PORT}."
        )
        print(
            "Make sure Terminal 4 — MQTT BROKER "
            "is running."
        )

        sys.exit(1)

    except Exception as exc:
        print()
        print("[UNEXPECTED ERROR]")
        print(exc)

        sys.exit(1)


if __name__ == "__main__":
    main()