from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.models import TelemetriaESP32
from core.mqtt_client import publish_command


@api_view(["GET"])
@permission_classes([AllowAny])
def telemetria_latest_api(request):
    item = TelemetriaESP32.objects.order_by("-fecha_hora").first()

    if not item:
        return Response({
            "message": "No hay telemetría todavía"
        })

    return Response({
        "id": item.id,
        "dispositivo_codigo": item.dispositivo_codigo,
        "humedad_suelo": item.humedad_suelo,
        "temperatura_ambiente": item.temperatura_ambiente,
        "humedad_ambiente": item.humedad_ambiente,
        "distancia_cm": item.distancia_cm,
        "nivel_tanque_pct": item.nivel_tanque_pct,
        "bomba_activa": item.bomba_activa,
        "modo": item.modo,
        "fecha_hora": item.fecha_hora,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def enviar_comando_mqtt_api(request):
    accion = request.data.get("accion")

    if not accion:
        return Response({"error": "La acción es obligatoria"}, status=400)

    payload = {
        "accion": accion
    }

    publish_command(payload)

    return Response({
        "message": "Comando enviado por MQTT",
        "payload": payload
    })