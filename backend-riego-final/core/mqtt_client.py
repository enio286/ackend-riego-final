import json
import threading

import paho.mqtt.client as mqtt
from django.conf import settings

from core.models import TelemetriaESP32


_client = None
_client_lock = threading.Lock()
_is_connected = False


def _first_present(data, *keys, default=None):
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return default


def _as_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "on", "encendida", "encendido", "si", "sí")
    return bool(value)


def on_connect(client, userdata, flags, reason_code, properties=None):
    global _is_connected
    _is_connected = True
    print("MQTT conectado con codigo:", reason_code)
    client.subscribe(settings.MQTT_TOPIC_TELEMETRIA)
    print("Suscrito a:", settings.MQTT_TOPIC_TELEMETRIA)


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties=None):
    global _is_connected
    _is_connected = False
    print("MQTT desconectado con codigo:", reason_code)


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        TelemetriaESP32.objects.create(
            dispositivo_codigo=_first_present(data, "dispositivo_codigo", "device", "device_id", "id", default="esp32-01"),
            humedad_suelo=_first_present(data, "humedad_suelo", "humedad", "soil_moisture", "soilMoisture"),
            temperatura_ambiente=_first_present(data, "temperatura_ambiente", "temperatura", "temperature", "temp"),
            humedad_ambiente=_first_present(data, "humedad_ambiente", "humedad_amb", "humidity", "air_humidity"),
            distancia_cm=_first_present(data, "distancia_cm", "distancia", "distance", "distance_cm"),
            nivel_tanque_pct=_first_present(data, "nivel_tanque_pct", "nivel_tanque", "tank_level", "tankLevel"),
            bomba_activa=_as_bool(_first_present(data, "bomba_activa", "bomba", "pump", "pump_on"), False),
            modo=_first_present(data, "modo", "mode", default="AUTO"),
            payload_raw=data,
        )

        print("Telemetria guardada:", data)

    except Exception as e:
        print("Error procesando mensaje MQTT:", e)


def build_mqtt_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    if settings.MQTT_USERNAME:
        client.username_pw_set(
            settings.MQTT_USERNAME,
            settings.MQTT_PASSWORD
        )

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    return client


def start_mqtt_listener():
    global _client

    if not getattr(settings, "MQTT_AUTO_START", True):
        print("MQTT auto-start deshabilitado")
        return None

    with _client_lock:
        if _client is not None:
            return _client

        client = build_mqtt_client()
        client.connect_async(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
        client.loop_start()
        _client = client
        print(
            "MQTT listener iniciado en segundo plano:",
            f"{settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}",
            "topic:",
            settings.MQTT_TOPIC_TELEMETRIA,
        )
        return client


def get_mqtt_status():
    return {
        "auto_start": getattr(settings, "MQTT_AUTO_START", True),
        "connected": _is_connected,
        "broker_host": settings.MQTT_BROKER_HOST,
        "broker_port": settings.MQTT_BROKER_PORT,
        "topic_telemetria": settings.MQTT_TOPIC_TELEMETRIA,
        "topic_comando": settings.MQTT_TOPIC_COMANDO,
        "listener_started": _client is not None,
    }


def publish_command(payload: dict):
    client = build_mqtt_client()
    client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
    client.loop_start()
    result = client.publish(settings.MQTT_TOPIC_COMANDO, json.dumps(payload))
    result.wait_for_publish(timeout=5)
    client.loop_stop()
    client.disconnect()
