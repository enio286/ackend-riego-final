from django.contrib import admin
from .models import (
    Predio,
    ZonaSiembra,
    DispositivoIot,
    Sensor,
    Bateria,
    BombaAgua,
)


@admin.register(Predio)
class PredioAdmin(admin.ModelAdmin):
    list_display = ('id_predio', 'nombre', 'ubicacion', 'activo')
    search_fields = ('nombre', 'ubicacion')
    list_filter = ('activo',)


@admin.register(ZonaSiembra)
class ZonaSiembraAdmin(admin.ModelAdmin):
    list_display = ('id_zona', 'nombre', 'id_predio', 'cultivo', 'activa')
    search_fields = ('nombre', 'cultivo')
    list_filter = ('activa', 'id_predio')


@admin.register(DispositivoIot)
class DispositivoIotAdmin(admin.ModelAdmin):
    list_display = ('id_dispositivo', 'nombre', 'codigo', 'id_zona', 'estado', 'activo')
    search_fields = ('nombre', 'codigo', 'modelo', 'mac_address')
    list_filter = ('estado', 'activo', 'id_zona')


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('id_sensor', 'nombre', 'tipo_sensor', 'id_dispositivo', 'id_zona', 'estado')
    search_fields = ('nombre',)
    list_filter = ('tipo_sensor', 'estado', 'activo')


@admin.register(Bateria)
class BateriaAdmin(admin.ModelAdmin):
    list_display = ('id_bateria', 'id_dispositivo', 'tipo', 'capacidad_mah', 'estado')
    search_fields = ('tipo',)
    list_filter = ('estado',)


@admin.register(BombaAgua)
class BombaAguaAdmin(admin.ModelAdmin):
    list_display = ('id_bomba', 'nombre', 'id_zona', 'id_dispositivo', 'estado_actual', 'activa')
    search_fields = ('nombre',)
    list_filter = ('estado_actual', 'activa')