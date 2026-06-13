from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        import os
        import sys

        if "runserver" in sys.argv and os.environ.get("RUN_MAIN") != "true":
            return

        skip_commands = {
            "check",
            "collectstatic",
            "createsuperuser",
            "makemigrations",
            "migrate",
            "mqtt_listener",
            "shell",
            "showmigrations",
            "test",
        }
        if len(sys.argv) > 1 and sys.argv[1] in skip_commands:
            return

        from core.mqtt_client import start_mqtt_listener

        start_mqtt_listener()
