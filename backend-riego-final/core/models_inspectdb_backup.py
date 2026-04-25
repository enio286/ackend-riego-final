# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Predio(models.Model):
    id_predio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    ubicacion = models.CharField(max_length=180, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    activo = models.IntegerField()
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'predio'


class ZonaSiembra(models.Model):
    id_zona = models.AutoField(primary_key=True)
    id_predio = models.ForeignKey(Predio, models.DO_NOTHING, db_column='id_predio')
    nombre = models.CharField(max_length=120)
    cultivo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    area_m2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    activa = models.IntegerField()
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'zona_siembra'
        unique_together = (('id_predio', 'nombre'),)


class DispositivoIot(models.Model):
    id_dispositivo = models.AutoField(primary_key=True)
    id_zona = models.ForeignKey(ZonaSiembra, models.DO_NOTHING, db_column='id_zona')
    codigo = models.CharField(unique=True, max_length=100)
    nombre = models.CharField(max_length=120)
    modelo = models.CharField(max_length=80, blank=True, null=True)
    direccion_ip = models.CharField(max_length=45, blank=True, null=True)
    mac_address = models.CharField(unique=True, max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=13)
    ultima_conexion = models.DateTimeField(blank=True, null=True)
    activo = models.IntegerField()
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'dispositivo_iot'


class Sensor(models.Model):
    id_sensor = models.AutoField(primary_key=True)
    id_dispositivo = models.ForeignKey(DispositivoIot, models.DO_NOTHING, db_column='id_dispositivo')
    id_zona = models.ForeignKey(ZonaSiembra, models.DO_NOTHING, db_column='id_zona')
    tipo_sensor = models.CharField(max_length=11)
    nombre = models.CharField(max_length=120)
    unidad_medida = models.CharField(max_length=30)
    estado = models.CharField(max_length=13)
    activo = models.IntegerField()
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sensor'
        unique_together = (('id_dispositivo', 'nombre'),)


class LecturaHumedad(models.Model):
    id_lectura_humedad = models.AutoField(primary_key=True)
    id_sensor = models.ForeignKey(Sensor, models.DO_NOTHING, db_column='id_sensor')
    id_zona = models.ForeignKey(ZonaSiembra, models.DO_NOTHING, db_column='id_zona')
    valor_humedad = models.DecimalField(max_digits=5, decimal_places=2)
    temperatura = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    fecha_hora = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'lectura_humedad'


class EstadoRiego(models.Model):
    id_estado_riego = models.AutoField(primary_key=True)
    id_zona = models.ForeignKey(ZonaSiembra, models.DO_NOTHING, db_column='id_zona')
    id_bomba = models.ForeignKey('BombaAgua', models.DO_NOTHING, db_column='id_bomba', blank=True, null=True)
    estado_riego = models.CharField(max_length=10)
    motivo = models.CharField(max_length=255, blank=True, null=True)
    duracion_segundos = models.IntegerField(blank=True, null=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estado_riego'


class BombaAgua(models.Model):
    id_bomba = models.AutoField(primary_key=True)
    id_zona = models.ForeignKey(ZonaSiembra, models.DO_NOTHING, db_column='id_zona')
    id_dispositivo = models.ForeignKey(DispositivoIot, models.DO_NOTHING, db_column='id_dispositivo', blank=True, null=True)
    nombre = models.CharField(max_length=120)
    caudal_litros_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estado_actual = models.CharField(max_length=13)
    activa = models.IntegerField()
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'bomba_agua'
        unique_together = (('id_zona', 'nombre'),)


class EstadoBomba(models.Model):
    id_estado_bomba = models.AutoField(primary_key=True)
    id_bomba = models.ForeignKey(BombaAgua, models.DO_NOTHING, db_column='id_bomba')
    estado = models.CharField(max_length=9)
    origen = models.CharField(max_length=10)
    observacion = models.CharField(max_length=255, blank=True, null=True)
    fecha_hora = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'estado_bomba'


class Bateria(models.Model):
    id_bateria = models.AutoField(primary_key=True)
    id_dispositivo = models.OneToOneField(DispositivoIot, models.DO_NOTHING, db_column='id_dispositivo')
    tipo = models.CharField(max_length=60, blank=True, null=True)
    capacidad_mah = models.IntegerField(blank=True, null=True)
    voltaje_nominal = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    estado = models.CharField(max_length=7)
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'bateria'


class LecturaBateria(models.Model):
    id_lectura_bateria = models.AutoField(primary_key=True)
    id_bateria = models.ForeignKey(Bateria, models.DO_NOTHING, db_column='id_bateria')
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    voltaje = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    fecha_hora = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'lectura_bateria'


class ConfiguracionRiego(models.Model):
    id_configuracion = models.AutoField(primary_key=True)
    id_zona = models.ForeignKey(ZonaSiembra, models.DO_NOTHING, db_column='id_zona')
    umbral_humedad = models.DecimalField(max_digits=5, decimal_places=2)
    tiempo_riego_segundos = models.IntegerField()
    modo_riego = models.CharField(max_length=10)
    intervalo_lectura_segundos = models.IntegerField()
    riego_habilitado = models.IntegerField()
    vigente = models.IntegerField()
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'configuracion_riego'


class Alerta(models.Model):
    id_alerta = models.AutoField(primary_key=True)
    id_zona = models.ForeignKey(ZonaSiembra, models.DO_NOTHING, db_column='id_zona')
    id_dispositivo = models.ForeignKey(DispositivoIot, models.DO_NOTHING, db_column='id_dispositivo', blank=True, null=True)
    tipo_alerta = models.CharField(max_length=12)
    nivel = models.CharField(max_length=7)
    mensaje = models.CharField(max_length=255)
    atendida = models.IntegerField()
    fecha_hora = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'alerta'


class ComandoRemoto(models.Model):
    id_comando = models.AutoField(primary_key=True)
    id_dispositivo = models.ForeignKey(DispositivoIot, models.DO_NOTHING, db_column='id_dispositivo')
    id_bomba = models.ForeignKey(BombaAgua, models.DO_NOTHING, db_column='id_bomba', blank=True, null=True)
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    accion = models.CharField(max_length=17)
    estado = models.CharField(max_length=9)
    parametros_texto = models.TextField(blank=True, null=True)
    fecha_hora_envio = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'comando_remoto'


class RespuestaComando(models.Model):
    id_respuesta = models.AutoField(primary_key=True)
    id_comando = models.ForeignKey(ComandoRemoto, models.DO_NOTHING, db_column='id_comando')
    codigo_respuesta = models.CharField(max_length=50, blank=True, null=True)
    mensaje = models.CharField(max_length=255, blank=True, null=True)
    exitoso = models.IntegerField()
    fecha_hora_respuesta = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'respuesta_comando'


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=80)
    correo = models.CharField(unique=True, max_length=120, blank=True, null=True)
    password_hash = models.CharField(max_length=255)
    activo = models.IntegerField()
    fecha_creacion = models.DateTimeField()
    ultimo_acceso = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario'


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rol'


class UsuarioRol(models.Model):
    id_usuario_rol = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_usuario')
    id_rol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='id_rol')
    fecha_asignacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'usuario_rol'
        unique_together = (('id_usuario', 'id_rol'),)


class AuditoriaSistema(models.Model):
    id_auditoria = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    accion = models.CharField(max_length=120)
    tabla_afectada = models.CharField(max_length=120, blank=True, null=True)
    id_registro_afectado = models.IntegerField(blank=True, null=True)
    detalle = models.TextField(blank=True, null=True)
    ip_origen = models.CharField(max_length=45, blank=True, null=True)
    fecha_hora = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auditoria_sistema'
