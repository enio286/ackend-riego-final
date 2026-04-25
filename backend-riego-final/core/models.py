from django.db import models


# =========================================================
# 1. PREDIO
# =========================================================
class Predio(models.Model):
    id_predio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    ubicacion = models.CharField(max_length=180, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'predio'
        verbose_name = 'Predio'
        verbose_name_plural = 'Predios'

    def __str__(self):
        return self.nombre


# =========================================================
# 2. ZONA SIEMBRA
# =========================================================
class ZonaSiembra(models.Model):
    id_zona = models.AutoField(primary_key=True)
    predio = models.ForeignKey(
        Predio,
        models.DO_NOTHING,
        db_column='id_predio',
        related_name='zonas_siembra'
    )
    nombre = models.CharField(max_length=120)
    cultivo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    area_m2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'zona_siembra'
        verbose_name = 'Zona de siembra'
        verbose_name_plural = 'Zonas de siembra'
        unique_together = (('predio', 'nombre'),)

    def __str__(self):
        return f"{self.nombre} - {self.predio.nombre}"


# =========================================================
# 3. DISPOSITIVO IOT
# =========================================================
class DispositivoIot(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('MANTENIMIENTO', 'Mantenimiento'),
    ]

    id_dispositivo = models.AutoField(primary_key=True)
    zona = models.ForeignKey(
        ZonaSiembra,
        models.DO_NOTHING,
        db_column='id_zona',
        related_name='dispositivos'
    )
    codigo = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=120)
    modelo = models.CharField(max_length=80, blank=True, null=True)
    direccion_ip = models.CharField(max_length=45, blank=True, null=True)
    mac_address = models.CharField(max_length=50, unique=True, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    ultima_conexion = models.DateTimeField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dispositivo_iot'
        verbose_name = 'Dispositivo IoT'
        verbose_name_plural = 'Dispositivos IoT'

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


# =========================================================
# 4. SENSOR
# =========================================================
class Sensor(models.Model):
    TIPO_SENSOR_CHOICES = [
        ('HUMEDAD', 'Humedad'),
        ('TEMPERATURA', 'Temperatura'),
        ('OTRO', 'Otro'),
    ]

    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('FALLA', 'Falla'),
        ('MANTENIMIENTO', 'Mantenimiento'),
    ]

    id_sensor = models.AutoField(primary_key=True)
    dispositivo = models.ForeignKey(
        DispositivoIot,
        models.DO_NOTHING,
        db_column='id_dispositivo',
        related_name='sensores'
    )
    zona = models.ForeignKey(
        ZonaSiembra,
        models.DO_NOTHING,
        db_column='id_zona',
        related_name='sensores'
    )
    tipo_sensor = models.CharField(max_length=20, choices=TIPO_SENSOR_CHOICES)
    nombre = models.CharField(max_length=120)
    unidad_medida = models.CharField(max_length=30)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensor'
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensores'
        unique_together = (('dispositivo', 'nombre'),)

    def __str__(self):
        return f"{self.nombre} - {self.dispositivo.nombre}"


# =========================================================
# 5. BATERIA
# =========================================================
class Bateria(models.Model):
    ESTADO_CHOICES = [
        ('BUENA', 'Buena'),
        ('MEDIA', 'Media'),
        ('BAJA', 'Baja'),
        ('CRITICA', 'Crítica'),
    ]

    id_bateria = models.AutoField(primary_key=True)
    dispositivo = models.OneToOneField(
        DispositivoIot,
        models.DO_NOTHING,
        db_column='id_dispositivo',
        related_name='bateria'
    )
    tipo = models.CharField(max_length=60, blank=True, null=True)
    capacidad_mah = models.IntegerField(blank=True, null=True)
    voltaje_nominal = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bateria'
        verbose_name = 'Batería'
        verbose_name_plural = 'Baterías'

    def __str__(self):
        return f"Batería de {self.dispositivo.nombre}"


# =========================================================
# 6. BOMBA AGUA
# =========================================================
class BombaAgua(models.Model):
    ESTADO_ACTUAL_CHOICES = [
        ('ENCENDIDA', 'Encendida'),
        ('APAGADA', 'Apagada'),
        ('MANTENIMIENTO', 'Mantenimiento'),
    ]

    id_bomba = models.AutoField(primary_key=True)
    zona = models.ForeignKey(
        ZonaSiembra,
        models.DO_NOTHING,
        db_column='id_zona',
        related_name='bombas'
    )
    dispositivo = models.ForeignKey(
        DispositivoIot,
        models.DO_NOTHING,
        db_column='id_dispositivo',
        blank=True,
        null=True,
        related_name='bombas'
    )
    nombre = models.CharField(max_length=120)
    caudal_litros_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estado_actual = models.CharField(max_length=20, choices=ESTADO_ACTUAL_CHOICES)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bomba_agua'
        verbose_name = 'Bomba de agua'
        verbose_name_plural = 'Bombas de agua'
        unique_together = (('zona', 'nombre'),)

    def __str__(self):
        return f"{self.nombre} - {self.zona.nombre}"


# =========================================================
# 7. LECTURA HUMEDAD
# =========================================================
class LecturaHumedad(models.Model):
    id_lectura_humedad = models.AutoField(primary_key=True)
    sensor = models.ForeignKey(
        Sensor,
        models.DO_NOTHING,
        db_column='id_sensor',
        related_name='lecturas_humedad'
    )
    zona = models.ForeignKey(
        ZonaSiembra,
        models.DO_NOTHING,
        db_column='id_zona',
        related_name='lecturas_humedad'
    )
    valor_humedad = models.DecimalField(max_digits=5, decimal_places=2)
    temperatura = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    fecha_hora = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lectura_humedad'
        verbose_name = 'Lectura de humedad'
        verbose_name_plural = 'Lecturas de humedad'

    def __str__(self):
        return f"{self.valor_humedad}% - {self.zona.nombre}"


# =========================================================
# 8. ESTADO BOMBA
# =========================================================
class EstadoBomba(models.Model):
    ESTADO_CHOICES = [
        ('ENCENDIDA', 'Encendida'),
        ('APAGADA', 'Apagada'),
    ]

    ORIGEN_CHOICES = [
        ('AUTOMATICO', 'Automático'),
        ('MANUAL', 'Manual'),
        ('WEB', 'Web'),
        ('ESP32', 'ESP32'),
    ]

    id_estado_bomba = models.AutoField(primary_key=True)
    bomba = models.ForeignKey(
        BombaAgua,
        models.DO_NOTHING,
        db_column='id_bomba',
        related_name='historial_estados'
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    origen = models.CharField(max_length=20, choices=ORIGEN_CHOICES)
    observacion = models.CharField(max_length=255, blank=True, null=True)
    fecha_hora = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estado_bomba'
        verbose_name = 'Estado de bomba'
        verbose_name_plural = 'Estados de bomba'

    def __str__(self):
        return f"{self.bomba.nombre} - {self.estado}"


# =========================================================
# 9. ESTADO RIEGO
# =========================================================
class EstadoRiego(models.Model):
    ESTADO_RIEGO_CHOICES = [
        ('INICIADO', 'Iniciado'),
        ('EN_CURSO', 'En curso'),
        ('FINALIZADO', 'Finalizado'),
        ('FALLIDO', 'Fallido'),
        ('CANCELADO', 'Cancelado'),
    ]

    id_estado_riego = models.AutoField(primary_key=True)
    zona = models.ForeignKey(
        ZonaSiembra,
        models.DO_NOTHING,
        db_column='id_zona',
        related_name='estados_riego'
    )
    bomba = models.ForeignKey(
        BombaAgua,
        models.DO_NOTHING,
        db_column='id_bomba',
        blank=True,
        null=True,
        related_name='estados_riego'
    )
    estado_riego = models.CharField(max_length=20, choices=ESTADO_RIEGO_CHOICES)
    motivo = models.CharField(max_length=255, blank=True, null=True)
    duracion_segundos = models.IntegerField(blank=True, null=True)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estado_riego'
        verbose_name = 'Estado de riego'
        verbose_name_plural = 'Estados de riego'

    def __str__(self):
        return f"{self.zona.nombre} - {self.estado_riego}"


# =========================================================
# 10. LECTURA BATERIA
# =========================================================
class LecturaBateria(models.Model):
    id_lectura_bateria = models.AutoField(primary_key=True)
    bateria = models.ForeignKey(
        Bateria,
        models.DO_NOTHING,
        db_column='id_bateria',
        related_name='lecturas_bateria'
    )
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    voltaje = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    fecha_hora = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lectura_bateria'
        verbose_name = 'Lectura de batería'
        verbose_name_plural = 'Lecturas de batería'

    def __str__(self):
        return f"{self.porcentaje}% - {self.bateria.dispositivo.nombre}"


# =========================================================
# 11. CONFIGURACION RIEGO
# =========================================================
class ConfiguracionRiego(models.Model):
    MODO_RIEGO_CHOICES = [
        ('MANUAL', 'Manual'),
        ('AUTOMATICO', 'Automático'),
    ]

    id_configuracion = models.AutoField(primary_key=True)
    zona = models.ForeignKey(
        ZonaSiembra,
        models.DO_NOTHING,
        db_column='id_zona',
        related_name='configuraciones_riego'
    )
    umbral_humedad = models.DecimalField(max_digits=5, decimal_places=2)
    tiempo_riego_segundos = models.IntegerField()
    modo_riego = models.CharField(max_length=20, choices=MODO_RIEGO_CHOICES)
    intervalo_lectura_segundos = models.IntegerField()
    riego_habilitado = models.BooleanField(default=True)
    vigente = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'configuracion_riego'
        verbose_name = 'Configuración de riego'
        verbose_name_plural = 'Configuraciones de riego'

    def __str__(self):
        return f"Config - {self.zona.nombre}"


# =========================================================
# 12. ALERTA
# =========================================================
class Alerta(models.Model):
    TIPO_ALERTA_CHOICES = [
        ('HUMEDAD_BAJA', 'Humedad baja'),
        ('BATERIA_BAJA', 'Batería baja'),
        ('SIN_CONEXION', 'Sin conexión'),
        ('ERROR_BOMBA', 'Error de bomba'),
        ('GENERAL', 'General'),
    ]

    NIVEL_CHOICES = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('CRITICA', 'Crítica'),
    ]

    id_alerta = models.AutoField(primary_key=True)
    zona = models.ForeignKey(
        ZonaSiembra,
        models.DO_NOTHING,
        db_column='id_zona',
        related_name='alertas'
    )
    dispositivo = models.ForeignKey(
        DispositivoIot,
        models.DO_NOTHING,
        db_column='id_dispositivo',
        blank=True,
        null=True,
        related_name='alertas'
    )
    tipo_alerta = models.CharField(max_length=20, choices=TIPO_ALERTA_CHOICES)
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    mensaje = models.CharField(max_length=255)
    atendida = models.BooleanField(default=False)
    fecha_hora = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alerta'
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'

    def __str__(self):
        return self.mensaje


# =========================================================
# 13. USUARIO
# =========================================================
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    username = models.CharField(max_length=80, unique=True)
    correo = models.CharField(max_length=120, unique=True, blank=True, null=True)
    password_hash = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    ultimo_acceso = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.username


# =========================================================
# 14. ROL
# =========================================================
class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


# =========================================================
# 15. USUARIO ROL
# =========================================================
class UsuarioRol(models.Model):
    id_usuario_rol = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario,
        models.DO_NOTHING,
        db_column='id_usuario',
        related_name='roles_asignados'
    )
    rol = models.ForeignKey(
        Rol,
        models.DO_NOTHING,
        db_column='id_rol',
        related_name='usuarios_asignados'
    )
    fecha_asignacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario_rol'
        verbose_name = 'Usuario-Rol'
        verbose_name_plural = 'Usuarios-Roles'
        unique_together = (('usuario', 'rol'),)

    def __str__(self):
        return f"{self.usuario.username} - {self.rol.nombre}"


# =========================================================
# 16. COMANDO REMOTO
# =========================================================
class ComandoRemoto(models.Model):
    ACCION_CHOICES = [
        ('ENCENDER', 'Encender'),
        ('APAGAR', 'Apagar'),
        ('REINICIAR', 'Reiniciar'),
        ('ACTUALIZAR_CONFIG', 'Actualizar config'),
    ]

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('ENVIADO', 'Enviado'),
        ('EJECUTADO', 'Ejecutado'),
        ('FALLIDO', 'Fallido'),
    ]

    id_comando = models.AutoField(primary_key=True)
    dispositivo = models.ForeignKey(
        DispositivoIot,
        models.DO_NOTHING,
        db_column='id_dispositivo',
        related_name='comandos_remotos'
    )
    bomba = models.ForeignKey(
        BombaAgua,
        models.DO_NOTHING,
        db_column='id_bomba',
        blank=True,
        null=True,
        related_name='comandos_remotos'
    )
    usuario = models.ForeignKey(
        Usuario,
        models.DO_NOTHING,
        db_column='id_usuario',
        blank=True,
        null=True,
        related_name='comandos_remotos'
    )
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    parametros_texto = models.TextField(blank=True, null=True)
    fecha_hora_envio = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comando_remoto'
        verbose_name = 'Comando remoto'
        verbose_name_plural = 'Comandos remotos'

    def __str__(self):
        return f"{self.accion} - {self.dispositivo.nombre}"


# =========================================================
# 17. RESPUESTA COMANDO
# =========================================================
class RespuestaComando(models.Model):
    id_respuesta = models.AutoField(primary_key=True)
    comando = models.ForeignKey(
        ComandoRemoto,
        models.DO_NOTHING,
        db_column='id_comando',
        related_name='respuestas'
    )
    codigo_respuesta = models.CharField(max_length=50, blank=True, null=True)
    mensaje = models.CharField(max_length=255, blank=True, null=True)
    exitoso = models.BooleanField(default=True)
    fecha_hora_respuesta = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'respuesta_comando'
        verbose_name = 'Respuesta de comando'
        verbose_name_plural = 'Respuestas de comando'

    def __str__(self):
        return f"Respuesta comando {self.comando.id_comando}"


# =========================================================
# 18. AUDITORIA SISTEMA
# =========================================================
class AuditoriaSistema(models.Model):
    id_auditoria = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario,
        models.DO_NOTHING,
        db_column='id_usuario',
        blank=True,
        null=True,
        related_name='auditorias'
    )
    accion = models.CharField(max_length=120)
    tabla_afectada = models.CharField(max_length=120, blank=True, null=True)
    id_registro_afectado = models.IntegerField(blank=True, null=True)
    detalle = models.TextField(blank=True, null=True)
    ip_origen = models.CharField(max_length=45, blank=True, null=True)
    fecha_hora = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auditoria_sistema'
        verbose_name = 'Auditoría del sistema'
        verbose_name_plural = 'Auditoría del sistema'

    def __str__(self):
        return f"{self.accion} - {self.fecha_hora}"