import json
import os
import ssl

import paho.mqtt.client as mqtt

from app.core.config import get_settings

BROKER = get_settings().mqtt_broker
PORT = int(get_settings().mqtt_port)
USERNAME = get_settings().mqtt_username
PASSWORD = get_settings().mqtt_password

from PIL import Image

mqtt_client: mqtt.Client | None = None


# ===== MQTT CALLBACKS =====

def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("[MQTT] Connected to EMQX successfully")
        client.publish("test/alive", "backend-started", qos=1)
    else:
        print(f"[MQTT] Connection failed, reason_code={reason_code}")


def on_disconnect(client, userdata, reason_code, properties=None):
    print(f"[MQTT] Disconnected, reason_code={reason_code}")


# ===== MQTT CLIENT FACTORY =====

def get_mqtt_client() -> mqtt.Client:
    global mqtt_client

    if mqtt_client:
        return mqtt_client

    client = mqtt.Client(
        client_id="",  # EMQX recommends auto-generated ID
        protocol=mqtt.MQTTv311
    )

    client.username_pw_set(
        USERNAME,
        PASSWORD
    )

    # ===== EMQX TLS CONFIG (CORRECT) =====
    client.tls_set(
        tls_version=ssl.PROTOCOL_TLS_CLIENT
    )
    client.tls_insecure_set(False)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    client.connect(
        BROKER,
        int(PORT),
        keepalive=60
    )

    client.loop_start()
    mqtt_client = client
    return client


def convert_for_oled(upload_file) -> bytes:
    img = Image.open(upload_file).convert("L")
    img = img.resize((128, 64))
    img = img.convert("1")  # monochrome

    pixels = img.load()
    buffer = bytearray(1024)  # 128*64/8

    for y in range(64):
        for x in range(128):
            if pixels[x, y] == 0:
                index = x + (y // 8) * 128
                buffer[index] |= (1 << (y % 8))

    return bytes(buffer)


def push_latest(device_id: str, image_id: str):
    msg = json.dumps({"image_id": image_id})
    mqtt_client.publish(f"keychain/{device_id}/image", msg, qos=1)

async def notify_device(device_id: str, version: int):
    msg = json.dumps({"type": "image_update", "version": version})
    mqtt_client.publish(f"keychain/{device_id}/cmd", msg, qos=1)


def send_pair_code(device_id: str, passcode: str):
    """
    Send pairing passcode to the device
    """
    msg = json.dumps({
        "type": "pair_request",
        "code": passcode
    })
    response = mqtt_client.publish(f"keychain/{device_id}/pair", msg, qos=1)
    return "success"


def send_device_token(device_id: str, token: str):
    """
    Send authentication token to the device after pairing verified
    """
    msg = json.dumps({
        "type": "auth",
        "token": token
    })
    mqtt_client.publish(f"keychain/{device_id}/auth", msg, qos=1)