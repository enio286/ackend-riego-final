from django.db import models


class Predio(models.Model):
    id_predio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    ubicacion = models.CharField(max_length=180, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'predio'
        verbose_name = 'Predio'
        verbose_name_plural = 'Predios'

    def __str__(self):
        return self.nombre


class ZonaSiembra(models.Model):
    id_zona = models.AutoField(primary_key=True)
    id_predio = models.ForeignKey(
        Predio,
        models.DO_NOTHING,
        db_column='id_predio',
        related_name='zonas'
    )
    nombre = models.CharField(max_length=120)
    cultivo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    area_m2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'zona_siembra'
        verbose_name = 'Zona de siembra'
        verbose_name_plural = 'Zonas de siembra'
        unique_together = (('id_predio', 'nombre'),)

    def __str__(self):
        return f"{self.nombre} - {self.id_predio.nombre}"


class DispositivoIot(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('MANTENIMIENTO', 'Mantenimiento'),
    ]

    id_dispositivo = models.AutoField(primary_key=True)
    id_zona = models.ForeignKey(
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
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'dispositivo_iot'
        verbose_name = 'Dispositivo IoT'
        verbose_name_plural = 'Dispositivos IoT'

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


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
    id_dispositivo = models.ForeignKey(
        DispositivoIot,
        models.DO_NOTHING,
        db_column='id_dispositivo',
        related_name='sensores'
    )
    id_zona = models.ForeignKey(
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
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sensor'
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensores'
        unique_together = (('id_dispositivo', 'nombre'),)

    def __str__(self):
        return f"{self.nombre} - {self.id_dispositivo.nombre}"


class Bateria(models.Model):
    ESTADO_CHOICES = [
        ('BUENA', 'Buena'),
        ('MEDIA', 'Media'),
        ('BAJA', 'Baja'),
        ('CRITICA', 'Crítica'),
    ]

    id_bateria = models.AutoField(primary_key=True)
    id_dispositivo = models.OneToOneField(
        DispositivoIot,
        models.DO_NOTHING,
        db_column='id_dispositivo',
        related_name='bateria'
    )
    tipo = models.CharField(max_length=60, blank=True, null=True)
    capacidad_mah = models.IntegerField(blank=True, null=True)
    voltaje_nominal = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'bateria'
        verbose_name = 'Batería'
        verbose_name_plural = 'Baterías'

    def __str__(self):
        return f"Batería de {self.id_dispositivo.nombre}"


class BombaAgua(models.Model):
    ESTADO_ACTUAL_CHOICES = [
        ('ENCENDIDA', 'Encendida'),
        ('APAGADA', 'Apagada'),
        ('MANTENIMIENTO', 'Mantenimiento'),
    ]

    id_bomba = models.AutoField(primary_key=True)
    id_zona = models.ForeignKey(
        ZonaSiembra,
        models.DO_NOTHING,
        db_column='id_zona',
        related_name='bombas'
    )
    id_dispositivo = models.ForeignKey(
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
    fecha_creacion = models.DateTimeField()
    fecha_actualizacion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'bomba_agua'
        verbose_name = 'Bomba de agua'
        verbose_name_plural = 'Bombas de agua'
        unique_together = (('id_zona', 'nombre'),)

    def __str__(self):
        return f"{self.nombre} - {self.id_zona.nombre}"