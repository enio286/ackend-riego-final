from django.contrib import admin
from .models import (
    Predio,
    ZonaSiembra,
    DispositivoIot,
    Sensor,
    Bateria,
    BombaAgua,
    LecturaHumedad,
    EstadoBomba,
    EstadoRiego,
    LecturaBateria,
    ConfiguracionRiego,
    Alerta,
    Usuario,
    Rol,
    UsuarioRol,
    ComandoRemoto,
    RespuestaComando,
    AuditoriaSistema,
)


@admin.register(Predio)
class PredioAdmin(admin.ModelAdmin):
    list_display = ('id_predio', 'nombre', 'ubicacion', 'activo')
    search_fields = ('nombre', 'ubicacion')
    list_filter = ('activo',)


@admin.register(ZonaSiembra)
class ZonaSiembraAdmin(admin.ModelAdmin):
    list_display = ('id_zona', 'nombre', 'predio', 'cultivo', 'activa')
    search_fields = ('nombre', 'cultivo')
    list_filter = ('activa', 'predio')


@admin.register(DispositivoIot)
class DispositivoIotAdmin(admin.ModelAdmin):
    list_display = ('id_dispositivo', 'nombre', 'codigo', 'zona', 'estado', 'activo')
    search_fields = ('nombre', 'codigo', 'modelo', 'mac_address')
    list_filter = ('estado', 'activo', 'zona')


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('id_sensor', 'nombre', 'tipo_sensor', 'dispositivo', 'zona', 'estado')
    search_fields = ('nombre',)
    list_filter = ('tipo_sensor', 'estado', 'activo')


@admin.register(Bateria)
class BateriaAdmin(admin.ModelAdmin):
    list_display = ('id_bateria', 'dispositivo', 'tipo', 'capacidad_mah', 'estado')
    search_fields = ('tipo',)
    list_filter = ('estado',)


@admin.register(BombaAgua)
class BombaAguaAdmin(admin.ModelAdmin):
    list_display = ('id_bomba', 'nombre', 'zona', 'dispositivo', 'estado_actual', 'activa')
    search_fields = ('nombre',)
    list_filter = ('estado_actual', 'activa')


@admin.register(LecturaHumedad)
class LecturaHumedadAdmin(admin.ModelAdmin):
    list_display = ('id_lectura_humedad', 'zona', 'sensor', 'valor_humedad', 'temperatura', 'fecha_hora')
    search_fields = ('zona__nombre', 'sensor__nombre')
    list_filter = ('zona', 'sensor')


@admin.register(EstadoBomba)
class EstadoBombaAdmin(admin.ModelAdmin):
    list_display = ('id_estado_bomba', 'bomba', 'estado', 'origen', 'fecha_hora')
    search_fields = ('bomba__nombre',)
    list_filter = ('estado', 'origen')


@admin.register(EstadoRiego)
class EstadoRiegoAdmin(admin.ModelAdmin):
    list_display = ('id_estado_riego', 'zona', 'bomba', 'estado_riego', 'duracion_segundos', 'fecha_inicio')
    search_fields = ('zona__nombre', 'motivo')
    list_filter = ('estado_riego', 'zona')


@admin.register(LecturaBateria)
class LecturaBateriaAdmin(admin.ModelAdmin):
    list_display = ('id_lectura_bateria', 'bateria', 'porcentaje', 'voltaje', 'fecha_hora')
    search_fields = ('bateria__dispositivo__nombre',)
    list_filter = ('bateria',)


@admin.register(ConfiguracionRiego)
class ConfiguracionRiegoAdmin(admin.ModelAdmin):
    list_display = ('id_configuracion', 'zona', 'umbral_humedad', 'tiempo_riego_segundos', 'modo_riego', 'vigente')
    search_fields = ('zona__nombre',)
    list_filter = ('modo_riego', 'riego_habilitado', 'vigente')


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('id_alerta', 'zona', 'dispositivo', 'tipo_alerta', 'nivel', 'atendida', 'fecha_hora')
    search_fields = ('mensaje', 'zona__nombre')
    list_filter = ('tipo_alerta', 'nivel', 'atendida')


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'username', 'correo', 'activo', 'ultimo_acceso')
    search_fields = ('username', 'correo')
    list_filter = ('activo',)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id_rol', 'nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ('id_usuario_rol', 'usuario', 'rol', 'fecha_asignacion')
    search_fields = ('usuario__username', 'rol__nombre')
    list_filter = ('rol',)


@admin.register(ComandoRemoto)
class ComandoRemotoAdmin(admin.ModelAdmin):
    list_display = ('id_comando', 'dispositivo', 'bomba', 'usuario', 'accion', 'estado', 'fecha_hora_envio')
    search_fields = ('dispositivo__nombre', 'usuario__username')
    list_filter = ('accion', 'estado')


@admin.register(RespuestaComando)
class RespuestaComandoAdmin(admin.ModelAdmin):
    list_display = ('id_respuesta', 'comando', 'codigo_respuesta', 'exitoso', 'fecha_hora_respuesta')
    search_fields = ('codigo_respuesta', 'mensaje')
    list_filter = ('exitoso',)


@admin.register(AuditoriaSistema)
class AuditoriaSistemaAdmin(admin.ModelAdmin):
    list_display = ('id_auditoria', 'usuario', 'accion', 'tabla_afectada', 'id_registro_afectado', 'fecha_hora')
    search_fields = ('accion', 'tabla_afectada', 'detalle')
    list_filter = ('tabla_afectada',)