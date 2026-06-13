from django.urls import path
from .mqtt_api_views import telemetria_latest_api, enviar_comando_mqtt_api
from .auth_password_reset_api_views import forgot_password_api, reset_password_api


from .api_views import (
    predios_api,
    predio_detail_api,
    zonas_api,
    zona_detail_api,
    dispositivos_api,
    dispositivo_detail_api,
    sensores_api,
    sensor_detail_api,
    bombas_api,
    bomba_detail_api,
    lecturas_humedad_api,
    lectura_humedad_detail_api,
    configuraciones_riego_api,
    configuracion_riego_detail_api,
    estados_bomba_api,
    estado_bomba_detail_api,
    lecturas_bateria_api,
    lectura_bateria_detail_api,
    estados_riego_api,
    estado_riego_detail_api,
    alertas_api,
    alerta_detail_api,
    usuarios_api,
    usuario_detail_api,
    roles_api,
    rol_detail_api,
    usuarios_roles_api,
    usuario_rol_detail_api,
    comandos_remotos_api,
    comando_remoto_detail_api,
    respuestas_comando_api,
    respuesta_comando_detail_api,
    auditorias_api,
    auditoria_detail_api,
)
from .auth_api_views import auth_ping_api, auth_me_api
from .auth_admin_api_views import (
    access_roles_api,
    access_users_api,
    access_user_detail_api,
)

urlpatterns = [
    # AUTH
    path("auth/ping/", auth_ping_api, name="api_auth_ping"),
    path("auth/me/", auth_me_api, name="api_auth_me"),

    # ACCESS CONTROL REAL
    path("access-roles/", access_roles_api, name="api_access_roles"),
    path("access-users/", access_users_api, name="api_access_users"),
    path("access-users/<int:user_id>/", access_user_detail_api, name="api_access_user_detail"),

    # PREDIOS
    path("predios/", predios_api, name="api_predios"),
    path("predios/<int:id_predio>/", predio_detail_api, name="api_predio_detail"),

    # ZONAS
    path("zonas/", zonas_api, name="api_zonas"),
    path("zonas/<int:id_zona>/", zona_detail_api, name="api_zona_detail"),

    # DISPOSITIVOS
    path("dispositivos/", dispositivos_api, name="api_dispositivos"),
    path("dispositivos/<int:id_dispositivo>/", dispositivo_detail_api, name="api_dispositivo_detail"),

    # SENSORES
    path("sensores/", sensores_api, name="api_sensores"),
    path("sensores/<int:id_sensor>/", sensor_detail_api, name="api_sensor_detail"),

    # BOMBAS
    path("bombas/", bombas_api, name="api_bombas"),
    path("bombas/<int:id_bomba>/", bomba_detail_api, name="api_bomba_detail"),

    # LECTURAS HUMEDAD
    path("lecturas-humedad/", lecturas_humedad_api, name="api_lecturas_humedad"),
    path("lecturas-humedad/<int:id_lectura_humedad>/", lectura_humedad_detail_api, name="api_lectura_humedad_detail"),

    # CONFIGURACIONES RIEGO
    path("configuraciones-riego/", configuraciones_riego_api, name="api_configuraciones_riego"),
    path("configuraciones-riego/<int:id_configuracion>/", configuracion_riego_detail_api, name="api_configuracion_riego_detail"),

    # ESTADOS BOMBA
    path("estados-bomba/", estados_bomba_api, name="api_estados_bomba"),
    path("estados-bomba/<int:id_estado_bomba>/", estado_bomba_detail_api, name="api_estado_bomba_detail"),

    # LECTURAS BATERIA
    path("lecturas-bateria/", lecturas_bateria_api, name="api_lecturas_bateria"),
    path("lecturas-bateria/<int:id_lectura_bateria>/", lectura_bateria_detail_api, name="api_lectura_bateria_detail"),

    # ESTADOS RIEGO
    path("estados-riego/", estados_riego_api, name="api_estados_riego"),
    path("estados-riego/<int:id_estado_riego>/", estado_riego_detail_api, name="api_estado_riego_detail"),

    # ALERTAS
    path("alertas/", alertas_api, name="api_alertas"),
    path("alertas/<int:id_alerta>/", alerta_detail_api, name="api_alerta_detail"),

    # LEGACY NEGOCIO
    path("usuarios/", usuarios_api, name="api_usuarios"),
    path("usuarios/<int:id_usuario>/", usuario_detail_api, name="api_usuario_detail"),
    path("roles/", roles_api, name="api_roles"),
    path("roles/<int:id_rol>/", rol_detail_api, name="api_rol_detail"),
    path("usuarios-roles/", usuarios_roles_api, name="api_usuarios_roles"),
    path("usuarios-roles/<int:id_usuario_rol>/", usuario_rol_detail_api, name="api_usuario_rol_detail"),

    # COMANDOS REMOTOS
    path("comandos-remotos/", comandos_remotos_api, name="api_comandos_remotos"),
    path("comandos-remotos/<int:id_comando>/", comando_remoto_detail_api, name="api_comando_remoto_detail"),

    # RESPUESTAS COMANDO
    path("respuestas-comando/", respuestas_comando_api, name="api_respuestas_comando"),
    path("respuestas-comando/<int:id_respuesta>/", respuesta_comando_detail_api, name="api_respuesta_comando_detail"),

    # AUDITORIA
    path("auditorias/", auditorias_api, name="api_auditorias"),
    path("auditorias/<int:id_auditoria>/", auditoria_detail_api, name="api_auditoria_detail"),

    # mtqq
    path("iot/telemetria/latest/", telemetria_latest_api, name="api_iot_telemetria_latest"),
    path("iot/comando/", enviar_comando_mqtt_api, name="api_iot_comando"),

    #contraseña olvido

    path("auth/forgot-password/", forgot_password_api, name="api_auth_forgot_password"),
    path("auth/reset-password/", reset_password_api, name="api_auth_reset_password"),


]