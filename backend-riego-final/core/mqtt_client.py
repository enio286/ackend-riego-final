import json
import paho.mqtt.client as mqtt

from django.conf import settings

from core.models import TelemetriaESP32


def on_connect(client, userdata, flags, reason_code, properties=None):
    print("MQTT conectado con código:", reason_code)
    client.subscribe(settings.MQTT_TOPIC_TELEMETRIA)
    print("Suscrito a:", settings.MQTT_TOPIC_TELEMETRIA)


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        TelemetriaESP32.objects.create(
            dispositivo_codigo=data.get("dispositivo_codigo", "esp32-01"),
            humedad_suelo=data.get("humedad_suelo"),
            temperatura_ambiente=data.get("temperatura_ambiente"),
            humedad_ambiente=data.get("humedad_ambiente"),
            distancia_cm=data.get("distancia_cm"),
            nivel_tanque_pct=data.get("nivel_tanque_pct"),
            bomba_activa=data.get("bomba_activa", False),
            modo=data.get("modo", "AUTO"),
            payload_raw=data,
        )

        print("Telemetría guardada:", data)

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
    client.on_message = on_message

    return client


def publish_command(payload: dict):
    client = build_mqtt_client()
    client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
    client.loop_start()
    client.publish(settings.MQTT_TOPIC_COMANDO, json.dumps(payload))
    client.loop_stop()
    client.disconnect()