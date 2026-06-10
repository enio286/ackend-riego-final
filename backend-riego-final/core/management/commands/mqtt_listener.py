from django.core.management.base import BaseCommand
from django.conf import settings

from core.mqtt_client import build_mqtt_client


class Command(BaseCommand):
    help = "Escucha telemetría MQTT del ESP32"

    def handle(self, *args, **kwargs):
        client = build_mqtt_client()

        self.stdout.write(
            self.style.SUCCESS(
                f"Conectando a MQTT {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}"
            )
        )

        client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
        client.loop_forever()