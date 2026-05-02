from django.utils import timezone
from django.utils.dateparse import parse_datetime

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.response import Response

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


# =========================================================
# PERMISOS
# =========================================================

class IsAuthenticatedReadAdminWrite(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return request.user.is_staff or request.user.is_superuser


class IsAdminOnlyCustom(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        )


# =========================================================
# HELPERS GENERALES
# =========================================================

def now_dt():
    return timezone.now()


def parse_dt_or_none(value):
    if value in ("", None):
        return None
    if hasattr(value, "tzinfo"):
        return value
    parsed = parse_datetime(str(value))
    return parsed


def parse_dt_or_now(value):
    parsed = parse_dt_or_none(value)
    return parsed if parsed else now_dt()


# =========================================================
# SERIALIZADORES MANUALES / TO_DICT
# =========================================================

def predio_to_dict(predio):
    return {
        "id_predio": predio.id_predio,
        "nombre": predio.nombre,
        "ubicacion": predio.ubicacion,
        "descripcion": predio.descripcion,
        "activo": predio.activo,
    }


def zona_to_dict(zona):
    return {
        "id_zona": zona.id_zona,
        "nombre": zona.nombre,
        "cultivo": zona.cultivo,
        "descripcion": zona.descripcion,
        "area_m2": float(zona.area_m2) if zona.area_m2 is not None else None,
        "activa": zona.activa,
        "predio": {
            "id_predio": zona.predio.id_predio,
            "nombre": zona.predio.nombre,
        }
    }


def dispositivo_to_dict(dispositivo):
    return {
        "id_dispositivo": dispositivo.id_dispositivo,
        "codigo": dispositivo.codigo,
        "nombre": dispositivo.nombre,
        "modelo": dispositivo.modelo,
        "direccion_ip": dispositivo.direccion_ip,
        "mac_address": dispositivo.mac_address,
        "estado": dispositivo.estado,
        "ultima_conexion": dispositivo.ultima_conexion.isoformat() if dispositivo.ultima_conexion else None,
        "activo": dispositivo.activo,
        "zona": {
            "id_zona": dispositivo.zona.id_zona,
            "nombre": dispositivo.zona.nombre,
        }
    }


def sensor_to_dict(sensor):
    return {
        "id_sensor": sensor.id_sensor,
        "nombre": sensor.nombre,
        "tipo_sensor": sensor.tipo_sensor,
        "unidad_medida": sensor.unidad_medida,
        "estado": sensor.estado,
        "activo": sensor.activo,
        "dispositivo": {
            "id_dispositivo": sensor.dispositivo.id_dispositivo,
            "nombre": sensor.dispositivo.nombre,
        },
        "zona": {
            "id_zona": sensor.zona.id_zona,
            "nombre": sensor.zona.nombre,
        }
    }


def bomba_to_dict(bomba):
    return {
        "id_bomba": bomba.id_bomba,
        "nombre": bomba.nombre,
        "caudal_litros_min": float(bomba.caudal_litros_min) if bomba.caudal_litros_min is not None else None,
        "estado_actual": bomba.estado_actual,
        "activa": bomba.activa,
        "zona": {
            "id_zona": bomba.zona.id_zona,
            "nombre": bomba.zona.nombre,
        },
        "dispositivo": {
            "id_dispositivo": bomba.dispositivo.id_dispositivo,
            "nombre": bomba.dispositivo.nombre,
        } if bomba.dispositivo else None,
    }


def lectura_humedad_to_dict(lectura):
    return {
        "id_lectura_humedad": lectura.id_lectura_humedad,
        "valor_humedad": float(lectura.valor_humedad),
        "temperatura": float(lectura.temperatura) if lectura.temperatura is not None else None,
        "fecha_hora": lectura.fecha_hora.isoformat() if lectura.fecha_hora else None,
        "sensor": {
            "id_sensor": lectura.sensor.id_sensor,
            "nombre": lectura.sensor.nombre,
        },
        "zona": {
            "id_zona": lectura.zona.id_zona,
            "nombre": lectura.zona.nombre,
        }
    }


def configuracion_riego_to_dict(config):
    return {
        "id_configuracion": config.id_configuracion,
        "umbral_humedad": float(config.umbral_humedad),
        "tiempo_riego_segundos": config.tiempo_riego_segundos,
        "modo_riego": config.modo_riego,
        "intervalo_lectura_segundos": config.intervalo_lectura_segundos,
        "riego_habilitado": config.riego_habilitado,
        "vigente": config.vigente,
        "zona": {
            "id_zona": config.zona.id_zona,
            "nombre": config.zona.nombre,
        }
    }


def estado_bomba_to_dict(estado_bomba):
    return {
        "id_estado_bomba": estado_bomba.id_estado_bomba,
        "estado": estado_bomba.estado,
        "origen": estado_bomba.origen,
        "observacion": estado_bomba.observacion,
        "fecha_hora": estado_bomba.fecha_hora.isoformat() if estado_bomba.fecha_hora else None,
        "bomba": {
            "id_bomba": estado_bomba.bomba.id_bomba,
            "nombre": estado_bomba.bomba.nombre,
        }
    }


def lectura_bateria_to_dict(lectura):
    return {
        "id_lectura_bateria": lectura.id_lectura_bateria,
        "porcentaje": float(lectura.porcentaje),
        "voltaje": float(lectura.voltaje) if lectura.voltaje is not None else None,
        "fecha_hora": lectura.fecha_hora.isoformat() if lectura.fecha_hora else None,
        "bateria": {
            "id_bateria": lectura.bateria.id_bateria,
            "dispositivo": lectura.bateria.dispositivo.nombre,
        }
    }


def estado_riego_to_dict(estado):
    return {
        "id_estado_riego": estado.id_estado_riego,
        "estado_riego": estado.estado_riego,
        "motivo": estado.motivo,
        "duracion_segundos": estado.duracion_segundos,
        "fecha_inicio": estado.fecha_inicio.isoformat() if estado.fecha_inicio else None,
        "fecha_fin": estado.fecha_fin.isoformat() if estado.fecha_fin else None,
        "zona": {
            "id_zona": estado.zona.id_zona,
            "nombre": estado.zona.nombre,
        },
        "bomba": {
            "id_bomba": estado.bomba.id_bomba,
            "nombre": estado.bomba.nombre,
        } if estado.bomba else None,
    }


def alerta_to_dict(alerta):
    return {
        "id_alerta": alerta.id_alerta,
        "tipo_alerta": alerta.tipo_alerta,
        "nivel": alerta.nivel,
        "mensaje": alerta.mensaje,
        "atendida": alerta.atendida,
        "fecha_hora": alerta.fecha_hora.isoformat() if alerta.fecha_hora else None,
        "zona": {
            "id_zona": alerta.zona.id_zona,
            "nombre": alerta.zona.nombre,
        },
        "dispositivo": {
            "id_dispositivo": alerta.dispositivo.id_dispositivo,
            "nombre": alerta.dispositivo.nombre,
        } if alerta.dispositivo else None,
    }


def usuario_to_dict(usuario):
    return {
        "id_usuario": usuario.id_usuario,
        "username": usuario.username,
        "correo": usuario.correo,
        "activo": usuario.activo,
        "fecha_creacion": usuario.fecha_creacion.isoformat() if usuario.fecha_creacion else None,
        "ultimo_acceso": usuario.ultimo_acceso.isoformat() if usuario.ultimo_acceso else None,
    }


def rol_to_dict(rol):
    return {
        "id_rol": rol.id_rol,
        "nombre": rol.nombre,
        "descripcion": rol.descripcion,
    }


def usuario_rol_to_dict(usuario_rol):
    return {
        "id_usuario_rol": usuario_rol.id_usuario_rol,
        "fecha_asignacion": usuario_rol.fecha_asignacion.isoformat() if usuario_rol.fecha_asignacion else None,
        "usuario": {
            "id_usuario": usuario_rol.usuario.id_usuario,
            "username": usuario_rol.usuario.username,
        },
        "rol": {
            "id_rol": usuario_rol.rol.id_rol,
            "nombre": usuario_rol.rol.nombre,
        }
    }


def comando_remoto_to_dict(comando):
    return {
        "id_comando": comando.id_comando,
        "accion": comando.accion,
        "estado": comando.estado,
        "parametros_texto": comando.parametros_texto,
        "fecha_hora_envio": comando.fecha_hora_envio.isoformat() if comando.fecha_hora_envio else None,
        "dispositivo": {
            "id_dispositivo": comando.dispositivo.id_dispositivo,
            "nombre": comando.dispositivo.nombre,
        },
        "bomba": {
            "id_bomba": comando.bomba.id_bomba,
            "nombre": comando.bomba.nombre,
        } if comando.bomba else None,
        "usuario": {
            "id_usuario": comando.usuario.id_usuario,
            "username": comando.usuario.username,
        } if comando.usuario else None,
    }


def respuesta_comando_to_dict(respuesta):
    return {
        "id_respuesta": respuesta.id_respuesta,
        "codigo_respuesta": respuesta.codigo_respuesta,
        "mensaje": respuesta.mensaje,
        "exitoso": respuesta.exitoso,
        "fecha_hora_respuesta": respuesta.fecha_hora_respuesta.isoformat() if respuesta.fecha_hora_respuesta else None,
        "comando": {
            "id_comando": respuesta.comando.id_comando,
            "accion": respuesta.comando.accion,
        }
    }


def auditoria_to_dict(auditoria):
    return {
        "id_auditoria": auditoria.id_auditoria,
        "accion": auditoria.accion,
        "tabla_afectada": auditoria.tabla_afectada,
        "id_registro_afectado": auditoria.id_registro_afectado,
        "detalle": auditoria.detalle,
        "ip_origen": auditoria.ip_origen,
        "fecha_hora": auditoria.fecha_hora.isoformat() if auditoria.fecha_hora else None,
        "usuario": {
            "id_usuario": auditoria.usuario.id_usuario,
            "username": auditoria.usuario.username,
        } if auditoria.usuario else None,
    }


# =========================================================
# PREDIOS
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def predios_api(request):
    if request.method == 'GET':
        predios = Predio.objects.all().order_by("id_predio")
        data = [predio_to_dict(predio) for predio in predios]
        return Response(data, status=status.HTTP_200_OK)

    nombre = request.data.get("nombre", "").strip()
    ubicacion = request.data.get("ubicacion", "").strip()
    descripcion = request.data.get("descripcion", "").strip()
    activo = request.data.get("activo", True)

    if not nombre:
        return Response({"error": "El nombre es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    predio = Predio.objects.create(
        nombre=nombre,
        ubicacion=ubicacion or None,
        descripcion=descripcion or None,
        activo=activo,
        fecha_creacion=now_dt(),
        fecha_actualizacion=now_dt(),
    )

    return Response(predio_to_dict(predio), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def predio_detail_api(request, id_predio):
    try:
        predio = Predio.objects.get(id_predio=id_predio)
    except Predio.DoesNotExist:
        return Response({"error": "Predio no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(predio_to_dict(predio), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        nombre = request.data.get("nombre", predio.nombre)
        ubicacion = request.data.get("ubicacion", predio.ubicacion)
        descripcion = request.data.get("descripcion", predio.descripcion)
        activo = request.data.get("activo", predio.activo)

        nombre = nombre.strip() if isinstance(nombre, str) else nombre

        if not nombre:
            return Response({"error": "El nombre es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        predio.nombre = nombre
        predio.ubicacion = ubicacion
        predio.descripcion = descripcion
        predio.activo = activo
        predio.fecha_actualizacion = now_dt()
        predio.save()

        return Response(predio_to_dict(predio), status=status.HTTP_200_OK)

    predio.delete()
    return Response({"message": "Predio eliminado correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# ZONAS
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def zonas_api(request):
    if request.method == 'GET':
        zonas = ZonaSiembra.objects.select_related("predio").all().order_by("id_zona")
        data = [zona_to_dict(zona) for zona in zonas]
        return Response(data, status=status.HTTP_200_OK)

    predio_id = request.data.get("id_predio")
    nombre = request.data.get("nombre", "").strip()
    cultivo = request.data.get("cultivo", "").strip()
    descripcion = request.data.get("descripcion", "").strip()
    area_m2 = request.data.get("area_m2")
    activa = request.data.get("activa", True)

    if not predio_id:
        return Response({"error": "El predio es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    if not nombre:
        return Response({"error": "El nombre es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        predio = Predio.objects.get(id_predio=predio_id)
    except Predio.DoesNotExist:
        return Response({"error": "Predio no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    existe = ZonaSiembra.objects.filter(predio_id=predio_id, nombre=nombre).exists()
    if existe:
        return Response({"error": "Ya existe una zona con ese nombre en ese predio"}, status=status.HTTP_400_BAD_REQUEST)

    zona = ZonaSiembra.objects.create(
        predio=predio,
        nombre=nombre,
        cultivo=cultivo or None,
        descripcion=descripcion or None,
        area_m2=area_m2 if area_m2 not in ("", None) else None,
        activa=activa,
        fecha_creacion=now_dt(),
        fecha_actualizacion=now_dt(),
    )

    zona = ZonaSiembra.objects.select_related("predio").get(id_zona=zona.id_zona)
    return Response(zona_to_dict(zona), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def zona_detail_api(request, id_zona):
    try:
        zona = ZonaSiembra.objects.select_related("predio").get(id_zona=id_zona)
    except ZonaSiembra.DoesNotExist:
        return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(zona_to_dict(zona), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        predio_id = request.data.get("id_predio", zona.predio.id_predio)
        nombre = request.data.get("nombre", zona.nombre)
        cultivo = request.data.get("cultivo", zona.cultivo)
        descripcion = request.data.get("descripcion", zona.descripcion)
        area_m2 = request.data.get("area_m2", zona.area_m2)
        activa = request.data.get("activa", zona.activa)

        nombre = nombre.strip() if isinstance(nombre, str) else nombre

        if not predio_id:
            return Response({"error": "El predio es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        if not nombre:
            return Response({"error": "El nombre es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            predio = Predio.objects.get(id_predio=predio_id)
        except Predio.DoesNotExist:
            return Response({"error": "Predio no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        existe = ZonaSiembra.objects.filter(
            predio_id=predio_id,
            nombre=nombre
        ).exclude(id_zona=zona.id_zona).exists()

        if existe:
            return Response({"error": "Ya existe otra zona con ese nombre en ese predio"}, status=status.HTTP_400_BAD_REQUEST)

        zona.predio = predio
        zona.nombre = nombre
        zona.cultivo = cultivo
        zona.descripcion = descripcion
        zona.area_m2 = area_m2 if area_m2 not in ("", None) else None
        zona.activa = activa
        zona.fecha_actualizacion = now_dt()
        zona.save()

        zona = ZonaSiembra.objects.select_related("predio").get(id_zona=zona.id_zona)
        return Response(zona_to_dict(zona), status=status.HTTP_200_OK)

    zona.delete()
    return Response({"message": "Zona eliminada correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# DISPOSITIVOS
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def dispositivos_api(request):
    if request.method == 'GET':
        dispositivos = DispositivoIot.objects.select_related("zona").all().order_by("id_dispositivo")
        data = [dispositivo_to_dict(dispositivo) for dispositivo in dispositivos]
        return Response(data, status=status.HTTP_200_OK)

    zona_id = request.data.get("id_zona")
    codigo = request.data.get("codigo", "").strip()
    nombre = request.data.get("nombre", "").strip()
    modelo = request.data.get("modelo", "").strip()
    direccion_ip = request.data.get("direccion_ip", "").strip()
    mac_address = request.data.get("mac_address", "").strip()
    estado_valor = request.data.get("estado", "ACTIVO")
    activo = request.data.get("activo", True)

    if not zona_id:
        return Response({"error": "La zona es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

    if not codigo:
        return Response({"error": "El código es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    if not nombre:
        return Response({"error": "El nombre es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        zona = ZonaSiembra.objects.get(id_zona=zona_id)
    except ZonaSiembra.DoesNotExist:
        return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if DispositivoIot.objects.filter(codigo=codigo).exists():
        return Response({"error": "Ya existe un dispositivo con ese código"}, status=status.HTTP_400_BAD_REQUEST)

    if mac_address and DispositivoIot.objects.filter(mac_address=mac_address).exists():
        return Response({"error": "Ya existe un dispositivo con esa MAC"}, status=status.HTTP_400_BAD_REQUEST)

    dispositivo = DispositivoIot.objects.create(
        zona=zona,
        codigo=codigo,
        nombre=nombre,
        modelo=modelo or None,
        direccion_ip=direccion_ip or None,
        mac_address=mac_address or None,
        estado=estado_valor,
        activo=activo,
        fecha_creacion=now_dt(),
        fecha_actualizacion=now_dt(),
    )

    dispositivo = DispositivoIot.objects.select_related("zona").get(id_dispositivo=dispositivo.id_dispositivo)
    return Response(dispositivo_to_dict(dispositivo), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def dispositivo_detail_api(request, id_dispositivo):
    try:
        dispositivo = DispositivoIot.objects.select_related("zona").get(id_dispositivo=id_dispositivo)
    except DispositivoIot.DoesNotExist:
        return Response({"error": "Dispositivo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(dispositivo_to_dict(dispositivo), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        zona_id = request.data.get("id_zona", dispositivo.zona.id_zona)
        codigo = request.data.get("codigo", dispositivo.codigo)
        nombre = request.data.get("nombre", dispositivo.nombre)
        modelo = request.data.get("modelo", dispositivo.modelo)
        direccion_ip = request.data.get("direccion_ip", dispositivo.direccion_ip)
        mac_address = request.data.get("mac_address", dispositivo.mac_address)
        estado_valor = request.data.get("estado", dispositivo.estado)
        activo = request.data.get("activo", dispositivo.activo)

        codigo = codigo.strip() if isinstance(codigo, str) else codigo
        nombre = nombre.strip() if isinstance(nombre, str) else nombre
        modelo = modelo.strip() if isinstance(modelo, str) else modelo
        direccion_ip = direccion_ip.strip() if isinstance(direccion_ip, str) else direccion_ip
        mac_address = mac_address.strip() if isinstance(mac_address, str) else mac_address

        if not zona_id:
            return Response({"error": "La zona es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

        if not codigo:
            return Response({"error": "El código es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        if not nombre:
            return Response({"error": "El nombre es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            zona = ZonaSiembra.objects.get(id_zona=zona_id)
        except ZonaSiembra.DoesNotExist:
            return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        existe_codigo = DispositivoIot.objects.filter(codigo=codigo).exclude(
            id_dispositivo=dispositivo.id_dispositivo
        ).exists()
        if existe_codigo:
            return Response({"error": "Ya existe otro dispositivo con ese código"}, status=status.HTTP_400_BAD_REQUEST)

        if mac_address:
            existe_mac = DispositivoIot.objects.filter(mac_address=mac_address).exclude(
                id_dispositivo=dispositivo.id_dispositivo
            ).exists()
            if existe_mac:
                return Response({"error": "Ya existe otro dispositivo con esa MAC"}, status=status.HTTP_400_BAD_REQUEST)

        dispositivo.zona = zona
        dispositivo.codigo = codigo
        dispositivo.nombre = nombre
        dispositivo.modelo = modelo or None
        dispositivo.direccion_ip = direccion_ip or None
        dispositivo.mac_address = mac_address or None
        dispositivo.estado = estado_valor
        dispositivo.activo = activo
        dispositivo.fecha_actualizacion = now_dt()
        dispositivo.save()

        dispositivo = DispositivoIot.objects.select_related("zona").get(id_dispositivo=dispositivo.id_dispositivo)
        return Response(dispositivo_to_dict(dispositivo), status=status.HTTP_200_OK)

    dispositivo.delete()
    return Response({"message": "Dispositivo eliminado correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# SENSORES
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def sensores_api(request):
    if request.method == 'GET':
        sensores = Sensor.objects.select_related("dispositivo", "zona").all().order_by("id_sensor")
        data = [sensor_to_dict(sensor) for sensor in sensores]
        return Response(data, status=status.HTTP_200_OK)

    id_dispositivo = request.data.get("id_dispositivo")
    id_zona = request.data.get("id_zona")
    nombre = request.data.get("nombre", "").strip()
    tipo_sensor = request.data.get("tipo_sensor", "HUMEDAD")
    unidad_medida = request.data.get("unidad_medida", "%").strip()
    estado = request.data.get("estado", "ACTIVO")
    activo = request.data.get("activo", True)

    if not id_dispositivo:
        return Response({"error": "El dispositivo es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    if not id_zona:
        return Response({"error": "La zona es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

    if not nombre:
        return Response({"error": "El nombre es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
    except DispositivoIot.DoesNotExist:
        return Response({"error": "Dispositivo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    try:
        zona = ZonaSiembra.objects.get(id_zona=id_zona)
    except ZonaSiembra.DoesNotExist:
        return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    existe = Sensor.objects.filter(dispositivo=dispositivo, nombre=nombre).exists()
    if existe:
        return Response({"error": "Ya existe un sensor con ese nombre en ese dispositivo"}, status=status.HTTP_400_BAD_REQUEST)

    sensor = Sensor.objects.create(
        dispositivo=dispositivo,
        zona=zona,
        nombre=nombre,
        tipo_sensor=tipo_sensor,
        unidad_medida=unidad_medida,
        estado=estado,
        activo=activo,
        fecha_creacion=now_dt(),
        fecha_actualizacion=now_dt(),
    )

    sensor = Sensor.objects.select_related("dispositivo", "zona").get(id_sensor=sensor.id_sensor)
    return Response(sensor_to_dict(sensor), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def sensor_detail_api(request, id_sensor):
    try:
        sensor = Sensor.objects.select_related("dispositivo", "zona").get(id_sensor=id_sensor)
    except Sensor.DoesNotExist:
        return Response({"error": "Sensor no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(sensor_to_dict(sensor), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        id_dispositivo = request.data.get("id_dispositivo", sensor.dispositivo.id_dispositivo)
        id_zona = request.data.get("id_zona", sensor.zona.id_zona)
        nombre = request.data.get("nombre", sensor.nombre)
        tipo_sensor = request.data.get("tipo_sensor", sensor.tipo_sensor)
        unidad_medida = request.data.get("unidad_medida", sensor.unidad_medida)
        estado = request.data.get("estado", sensor.estado)
        activo = request.data.get("activo", sensor.activo)

        nombre = nombre.strip() if isinstance(nombre, str) else nombre
        unidad_medida = unidad_medida.strip() if isinstance(unidad_medida, str) else unidad_medida

        if not id_dispositivo:
            return Response({"error": "El dispositivo es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        if not id_zona:
            return Response({"error": "La zona es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

        if not nombre:
            return Response({"error": "El nombre es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
        except DispositivoIot.DoesNotExist:
            return Response({"error": "Dispositivo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        try:
            zona = ZonaSiembra.objects.get(id_zona=id_zona)
        except ZonaSiembra.DoesNotExist:
            return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        existe = Sensor.objects.filter(
            dispositivo=dispositivo,
            nombre=nombre
        ).exclude(id_sensor=sensor.id_sensor).exists()

        if existe:
            return Response({"error": "Ya existe otro sensor con ese nombre en ese dispositivo"}, status=status.HTTP_400_BAD_REQUEST)

        sensor.dispositivo = dispositivo
        sensor.zona = zona
        sensor.nombre = nombre
        sensor.tipo_sensor = tipo_sensor
        sensor.unidad_medida = unidad_medida
        sensor.estado = estado
        sensor.activo = activo
        sensor.fecha_actualizacion = now_dt()
        sensor.save()

        sensor = Sensor.objects.select_related("dispositivo", "zona").get(id_sensor=sensor.id_sensor)
        return Response(sensor_to_dict(sensor), status=status.HTTP_200_OK)

    sensor.delete()
    return Response({"message": "Sensor eliminado correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# BOMBAS DE AGUA
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def bombas_api(request):
    if request.method == 'GET':
        bombas = BombaAgua.objects.select_related("zona", "dispositivo").all().order_by("id_bomba")
        data = [bomba_to_dict(bomba) for bomba in bombas]
        return Response(data, status=status.HTTP_200_OK)

    id_zona = request.data.get("id_zona")
    id_dispositivo = request.data.get("id_dispositivo")
    nombre = request.data.get("nombre", "").strip()
    caudal_litros_min = request.data.get("caudal_litros_min")
    estado_actual = request.data.get("estado_actual", "APAGADA")
    activa = request.data.get("activa", True)

    if not id_zona:
        return Response({"error": "La zona es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

    if not nombre:
        return Response({"error": "El nombre es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        zona = ZonaSiembra.objects.get(id_zona=id_zona)
    except ZonaSiembra.DoesNotExist:
        return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    dispositivo = None
    if id_dispositivo:
        try:
            dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
        except DispositivoIot.DoesNotExist:
            return Response({"error": "Dispositivo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    existe = BombaAgua.objects.filter(zona=zona, nombre=nombre).exists()
    if existe:
        return Response({"error": "Ya existe una bomba con ese nombre en esa zona"}, status=status.HTTP_400_BAD_REQUEST)

    bomba = BombaAgua.objects.create(
        zona=zona,
        dispositivo=dispositivo,
        nombre=nombre,
        caudal_litros_min=caudal_litros_min if caudal_litros_min not in ("", None) else None,
        estado_actual=estado_actual,
        activa=activa,
        fecha_creacion=now_dt(),
        fecha_actualizacion=now_dt(),
    )

    bomba = BombaAgua.objects.select_related("zona", "dispositivo").get(id_bomba=bomba.id_bomba)
    return Response(bomba_to_dict(bomba), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def bomba_detail_api(request, id_bomba):
    try:
        bomba = BombaAgua.objects.select_related("zona", "dispositivo").get(id_bomba=id_bomba)
    except BombaAgua.DoesNotExist:
        return Response({"error": "Bomba no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(bomba_to_dict(bomba), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        id_zona = request.data.get("id_zona", bomba.zona.id_zona)
        id_dispositivo = request.data.get("id_dispositivo", bomba.dispositivo.id_dispositivo if bomba.dispositivo else None)
        nombre = request.data.get("nombre", bomba.nombre)
        caudal_litros_min = request.data.get("caudal_litros_min", bomba.caudal_litros_min)
        estado_actual = request.data.get("estado_actual", bomba.estado_actual)
        activa = request.data.get("activa", bomba.activa)

        nombre = nombre.strip() if isinstance(nombre, str) else nombre

        if not id_zona:
            return Response({"error": "La zona es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

        if not nombre:
            return Response({"error": "El nombre es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            zona = ZonaSiembra.objects.get(id_zona=id_zona)
        except ZonaSiembra.DoesNotExist:
            return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        dispositivo = None
        if id_dispositivo:
            try:
                dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
            except DispositivoIot.DoesNotExist:
                return Response({"error": "Dispositivo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        existe = BombaAgua.objects.filter(
            zona=zona,
            nombre=nombre
        ).exclude(id_bomba=bomba.id_bomba).exists()

        if existe:
            return Response({"error": "Ya existe otra bomba con ese nombre en esa zona"}, status=status.HTTP_400_BAD_REQUEST)

        bomba.zona = zona
        bomba.dispositivo = dispositivo
        bomba.nombre = nombre
        bomba.caudal_litros_min = caudal_litros_min if caudal_litros_min not in ("", None) else None
        bomba.estado_actual = estado_actual
        bomba.activa = activa
        bomba.fecha_actualizacion = now_dt()
        bomba.save()

        bomba = BombaAgua.objects.select_related("zona", "dispositivo").get(id_bomba=bomba.id_bomba)
        return Response(bomba_to_dict(bomba), status=status.HTTP_200_OK)

    bomba.delete()
    return Response({"message": "Bomba eliminada correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# LECTURAS DE HUMEDAD
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def lecturas_humedad_api(request):
    if request.method == 'GET':
        lecturas = LecturaHumedad.objects.select_related("sensor", "zona").all().order_by("-id_lectura_humedad")
        data = [lectura_humedad_to_dict(lectura) for lectura in lecturas]
        return Response(data, status=status.HTTP_200_OK)

    id_sensor = request.data.get("id_sensor")
    id_zona = request.data.get("id_zona")
    valor_humedad = request.data.get("valor_humedad")
    temperatura = request.data.get("temperatura")
    fecha_hora = request.data.get("fecha_hora")

    if not id_sensor:
        return Response({"error": "El sensor es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    if not id_zona:
        return Response({"error": "La zona es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

    if valor_humedad in ("", None):
        return Response({"error": "El valor de humedad es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        sensor = Sensor.objects.get(id_sensor=id_sensor)
    except Sensor.DoesNotExist:
        return Response({"error": "Sensor no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    try:
        zona = ZonaSiembra.objects.get(id_zona=id_zona)
    except ZonaSiembra.DoesNotExist:
        return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    lectura = LecturaHumedad.objects.create(
        sensor=sensor,
        zona=zona,
        valor_humedad=valor_humedad,
        temperatura=temperatura if temperatura not in ("", None) else None,
        fecha_hora=parse_dt_or_now(fecha_hora),
    )

    lectura = LecturaHumedad.objects.select_related("sensor", "zona").get(
        id_lectura_humedad=lectura.id_lectura_humedad
    )
    return Response(lectura_humedad_to_dict(lectura), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def lectura_humedad_detail_api(request, id_lectura_humedad):
    try:
        lectura = LecturaHumedad.objects.select_related("sensor", "zona").get(id_lectura_humedad=id_lectura_humedad)
    except LecturaHumedad.DoesNotExist:
        return Response({"error": "Lectura no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(lectura_humedad_to_dict(lectura), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        id_sensor = request.data.get("id_sensor", lectura.sensor.id_sensor)
        id_zona = request.data.get("id_zona", lectura.zona.id_zona)
        valor_humedad = request.data.get("valor_humedad", lectura.valor_humedad)
        temperatura = request.data.get("temperatura", lectura.temperatura)
        fecha_hora = request.data.get("fecha_hora", lectura.fecha_hora)

        if not id_sensor:
            return Response({"error": "El sensor es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        if not id_zona:
            return Response({"error": "La zona es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

        if valor_humedad in ("", None):
            return Response({"error": "El valor de humedad es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sensor = Sensor.objects.get(id_sensor=id_sensor)
        except Sensor.DoesNotExist:
            return Response({"error": "Sensor no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        try:
            zona = ZonaSiembra.objects.get(id_zona=id_zona)
        except ZonaSiembra.DoesNotExist:
            return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        lectura.sensor = sensor
        lectura.zona = zona
        lectura.valor_humedad = valor_humedad
        lectura.temperatura = temperatura if temperatura not in ("", None) else None
        lectura.fecha_hora = parse_dt_or_now(fecha_hora)
        lectura.save()

        lectura = LecturaHumedad.objects.select_related("sensor", "zona").get(id_lectura_humedad=lectura.id_lectura_humedad)
        return Response(lectura_humedad_to_dict(lectura), status=status.HTTP_200_OK)

    lectura.delete()
    return Response({"message": "Lectura eliminada correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# CONFIGURACIONES DE RIEGO
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def configuraciones_riego_api(request):
    if request.method == 'GET':
        configuraciones = ConfiguracionRiego.objects.select_related("zona").all().order_by("id_configuracion")
        data = [configuracion_riego_to_dict(config) for config in configuraciones]
        return Response(data, status=status.HTTP_200_OK)

    id_zona = request.data.get("id_zona")
    umbral_humedad = request.data.get("umbral_humedad")
    tiempo_riego_segundos = request.data.get("tiempo_riego_segundos")
    modo_riego = request.data.get("modo_riego", "AUTOMATICO")
    intervalo_lectura_segundos = request.data.get("intervalo_lectura_segundos", 60)
    riego_habilitado = request.data.get("riego_habilitado", True)
    vigente = request.data.get("vigente", True)

    if not id_zona:
        return Response({"error": "La zona es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

    if umbral_humedad in ("", None):
        return Response({"error": "El umbral de humedad es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    if tiempo_riego_segundos in ("", None):
        return Response({"error": "El tiempo de riego es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        zona = ZonaSiembra.objects.get(id_zona=id_zona)
    except ZonaSiembra.DoesNotExist:
        return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    config = ConfiguracionRiego.objects.create(
        zona=zona,
        umbral_humedad=umbral_humedad,
        tiempo_riego_segundos=tiempo_riego_segundos,
        modo_riego=modo_riego,
        intervalo_lectura_segundos=intervalo_lectura_segundos,
        riego_habilitado=riego_habilitado,
        vigente=vigente,
        fecha_creacion=now_dt(),
        fecha_actualizacion=now_dt(),
    )

    config = ConfiguracionRiego.objects.select_related("zona").get(id_configuracion=config.id_configuracion)
    return Response(configuracion_riego_to_dict(config), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def configuracion_riego_detail_api(request, id_configuracion):
    try:
        config = ConfiguracionRiego.objects.select_related("zona").get(id_configuracion=id_configuracion)
    except ConfiguracionRiego.DoesNotExist:
        return Response({"error": "Configuración no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(configuracion_riego_to_dict(config), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        id_zona = request.data.get("id_zona", config.zona.id_zona)
        umbral_humedad = request.data.get("umbral_humedad", config.umbral_humedad)
        tiempo_riego_segundos = request.data.get("tiempo_riego_segundos", config.tiempo_riego_segundos)
        modo_riego = request.data.get("modo_riego", config.modo_riego)
        intervalo_lectura_segundos = request.data.get("intervalo_lectura_segundos", config.intervalo_lectura_segundos)
        riego_habilitado = request.data.get("riego_habilitado", config.riego_habilitado)
        vigente = request.data.get("vigente", config.vigente)

        if not id_zona:
            return Response({"error": "La zona es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

        if umbral_humedad in ("", None):
            return Response({"error": "El umbral de humedad es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        if tiempo_riego_segundos in ("", None):
            return Response({"error": "El tiempo de riego es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            zona = ZonaSiembra.objects.get(id_zona=id_zona)
        except ZonaSiembra.DoesNotExist:
            return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        config.zona = zona
        config.umbral_humedad = umbral_humedad
        config.tiempo_riego_segundos = tiempo_riego_segundos
        config.modo_riego = modo_riego
        config.intervalo_lectura_segundos = intervalo_lectura_segundos
        config.riego_habilitado = riego_habilitado
        config.vigente = vigente
        config.fecha_actualizacion = now_dt()
        config.save()

        config = ConfiguracionRiego.objects.select_related("zona").get(id_configuracion=config.id_configuracion)
        return Response(configuracion_riego_to_dict(config), status=status.HTTP_200_OK)

    config.delete()
    return Response({"message": "Configuración eliminada correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# ESTADOS DE BOMBA
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def estados_bomba_api(request):
    if request.method == 'GET':
        estados = EstadoBomba.objects.select_related("bomba").all().order_by("-id_estado_bomba")
        data = [estado_bomba_to_dict(estado) for estado in estados]
        return Response(data, status=status.HTTP_200_OK)

    id_bomba = request.data.get("id_bomba")
    estado = request.data.get("estado")
    origen = request.data.get("origen", "MANUAL")
    observacion = request.data.get("observacion", "").strip()
    fecha_hora = request.data.get("fecha_hora")

    if not id_bomba:
        return Response({"error": "La bomba es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

    if not estado:
        return Response({"error": "El estado es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        bomba = BombaAgua.objects.get(id_bomba=id_bomba)
    except BombaAgua.DoesNotExist:
        return Response({"error": "Bomba no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    estado_bomba = EstadoBomba.objects.create(
        bomba=bomba,
        estado=estado,
        origen=origen,
        observacion=observacion or None,
        fecha_hora=parse_dt_or_now(fecha_hora),
    )

    # sincroniza estado actual en la bomba
    if estado in ("ENCENDIDA", "APAGADA"):
        bomba.estado_actual = estado
        bomba.fecha_actualizacion = now_dt()
        bomba.save()

    estado_bomba = EstadoBomba.objects.select_related("bomba").get(id_estado_bomba=estado_bomba.id_estado_bomba)
    return Response(estado_bomba_to_dict(estado_bomba), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def estado_bomba_detail_api(request, id_estado_bomba):
    try:
        estado_bomba = EstadoBomba.objects.select_related("bomba").get(id_estado_bomba=id_estado_bomba)
    except EstadoBomba.DoesNotExist:
        return Response({"error": "Estado de bomba no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(estado_bomba_to_dict(estado_bomba), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        id_bomba = request.data.get("id_bomba", estado_bomba.bomba.id_bomba)
        estado = request.data.get("estado", estado_bomba.estado)
        origen = request.data.get("origen", estado_bomba.origen)
        observacion = request.data.get("observacion", estado_bomba.observacion)
        fecha_hora = request.data.get("fecha_hora", estado_bomba.fecha_hora)

        if not id_bomba:
            return Response({"error": "La bomba es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

        if not estado:
            return Response({"error": "El estado es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bomba = BombaAgua.objects.get(id_bomba=id_bomba)
        except BombaAgua.DoesNotExist:
            return Response({"error": "Bomba no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        estado_bomba.bomba = bomba
        estado_bomba.estado = estado
        estado_bomba.origen = origen
        estado_bomba.observacion = observacion
        estado_bomba.fecha_hora = parse_dt_or_now(fecha_hora)
        estado_bomba.save()

        if estado in ("ENCENDIDA", "APAGADA"):
            bomba.estado_actual = estado
            bomba.fecha_actualizacion = now_dt()
            bomba.save()

        estado_bomba = EstadoBomba.objects.select_related("bomba").get(id_estado_bomba=estado_bomba.id_estado_bomba)
        return Response(estado_bomba_to_dict(estado_bomba), status=status.HTTP_200_OK)

    estado_bomba.delete()
    return Response({"message": "Estado de bomba eliminado correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# LECTURAS DE BATERÍA
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def lecturas_bateria_api(request):
    if request.method == 'GET':
        lecturas = LecturaBateria.objects.select_related("bateria", "bateria__dispositivo").all().order_by("-id_lectura_bateria")
        data = [lectura_bateria_to_dict(lectura) for lectura in lecturas]
        return Response(data, status=status.HTTP_200_OK)

    id_bateria = request.data.get("id_bateria")
    porcentaje = request.data.get("porcentaje")
    voltaje = request.data.get("voltaje")
    fecha_hora = request.data.get("fecha_hora")

    if not id_bateria:
        return Response({"error": "La batería es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

    if porcentaje in ("", None):
        return Response({"error": "El porcentaje es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        bateria = Bateria.objects.get(id_bateria=id_bateria)
    except Bateria.DoesNotExist:
        return Response({"error": "Batería no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    lectura = LecturaBateria.objects.create(
        bateria=bateria,
        porcentaje=porcentaje,
        voltaje=voltaje if voltaje not in ("", None) else None,
        fecha_hora=parse_dt_or_now(fecha_hora),
    )

    lectura = LecturaBateria.objects.select_related("bateria", "bateria__dispositivo").get(id_lectura_bateria=lectura.id_lectura_bateria)
    return Response(lectura_bateria_to_dict(lectura), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def lectura_bateria_detail_api(request, id_lectura_bateria):
    try:
        lectura = LecturaBateria.objects.select_related("bateria", "bateria__dispositivo").get(id_lectura_bateria=id_lectura_bateria)
    except LecturaBateria.DoesNotExist:
        return Response({"error": "Lectura de batería no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(lectura_bateria_to_dict(lectura), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        id_bateria = request.data.get("id_bateria", lectura.bateria.id_bateria)
        porcentaje = request.data.get("porcentaje", lectura.porcentaje)
        voltaje = request.data.get("voltaje", lectura.voltaje)
        fecha_hora = request.data.get("fecha_hora", lectura.fecha_hora)

        if not id_bateria:
            return Response({"error": "La batería es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

        if porcentaje in ("", None):
            return Response({"error": "El porcentaje es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            bateria = Bateria.objects.get(id_bateria=id_bateria)
        except Bateria.DoesNotExist:
            return Response({"error": "Batería no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        lectura.bateria = bateria
        lectura.porcentaje = porcentaje
        lectura.voltaje = voltaje if voltaje not in ("", None) else None
        lectura.fecha_hora = parse_dt_or_now(fecha_hora)
        lectura.save()

        lectura = LecturaBateria.objects.select_related("bateria", "bateria__dispositivo").get(id_lectura_bateria=lectura.id_lectura_bateria)
        return Response(lectura_bateria_to_dict(lectura), status=status.HTTP_200_OK)

    lectura.delete()
    return Response({"message": "Lectura de batería eliminada correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# ESTADOS DE RIEGO
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def estados_riego_api(request):
    if request.method == 'GET':
        estados = EstadoRiego.objects.select_related("zona", "bomba").all().order_by("-id_estado_riego")
        data = [estado_riego_to_dict(estado) for estado in estados]
        return Response(data, status=status.HTTP_200_OK)

    id_zona = request.data.get("id_zona")
    id_bomba = request.data.get("id_bomba")
    estado_riego = request.data.get("estado_riego")
    motivo = request.data.get("motivo", "").strip()
    duracion_segundos = request.data.get("duracion_segundos")
    fecha_inicio = request.data.get("fecha_inicio")
    fecha_fin = request.data.get("fecha_fin")

    if not id_zona:
        return Response({"error": "La zona es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

    if not estado_riego:
        return Response({"error": "El estado de riego es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        zona = ZonaSiembra.objects.get(id_zona=id_zona)
    except ZonaSiembra.DoesNotExist:
        return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    bomba = None
    if id_bomba:
        try:
            bomba = BombaAgua.objects.get(id_bomba=id_bomba)
        except BombaAgua.DoesNotExist:
            return Response({"error": "Bomba no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    estado = EstadoRiego.objects.create(
        zona=zona,
        bomba=bomba,
        estado_riego=estado_riego,
        motivo=motivo or None,
        duracion_segundos=duracion_segundos if duracion_segundos not in ("", None) else None,
        fecha_inicio=parse_dt_or_now(fecha_inicio),
        fecha_fin=parse_dt_or_none(fecha_fin),
    )

    estado = EstadoRiego.objects.select_related("zona", "bomba").get(id_estado_riego=estado.id_estado_riego)
    return Response(estado_riego_to_dict(estado), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def estado_riego_detail_api(request, id_estado_riego):
    try:
        estado = EstadoRiego.objects.select_related("zona", "bomba").get(id_estado_riego=id_estado_riego)
    except EstadoRiego.DoesNotExist:
        return Response({"error": "Estado de riego no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(estado_riego_to_dict(estado), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        id_zona = request.data.get("id_zona", estado.zona.id_zona)
        id_bomba = request.data.get("id_bomba", estado.bomba.id_bomba if estado.bomba else None)
        estado_riego_valor = request.data.get("estado_riego", estado.estado_riego)
        motivo = request.data.get("motivo", estado.motivo)
        duracion_segundos = request.data.get("duracion_segundos", estado.duracion_segundos)
        fecha_inicio = request.data.get("fecha_inicio", estado.fecha_inicio)
        fecha_fin = request.data.get("fecha_fin", estado.fecha_fin)

        if not id_zona:
            return Response({"error": "La zona es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

        if not estado_riego_valor:
            return Response({"error": "El estado de riego es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            zona = ZonaSiembra.objects.get(id_zona=id_zona)
        except ZonaSiembra.DoesNotExist:
            return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        bomba = None
        if id_bomba:
            try:
                bomba = BombaAgua.objects.get(id_bomba=id_bomba)
            except BombaAgua.DoesNotExist:
                return Response({"error": "Bomba no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        estado.zona = zona
        estado.bomba = bomba
        estado.estado_riego = estado_riego_valor
        estado.motivo = motivo
        estado.duracion_segundos = duracion_segundos if duracion_segundos not in ("", None) else None
        estado.fecha_inicio = parse_dt_or_now(fecha_inicio)
        estado.fecha_fin = parse_dt_or_none(fecha_fin)
        estado.save()

        estado = EstadoRiego.objects.select_related("zona", "bomba").get(id_estado_riego=estado.id_estado_riego)
        return Response(estado_riego_to_dict(estado), status=status.HTTP_200_OK)

    estado.delete()
    return Response({"message": "Estado de riego eliminado correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# ALERTAS
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def alertas_api(request):
    if request.method == 'GET':
        alertas = Alerta.objects.select_related("zona", "dispositivo").all().order_by("-id_alerta")
        data = [alerta_to_dict(alerta) for alerta in alertas]
        return Response(data, status=status.HTTP_200_OK)

    id_zona = request.data.get("id_zona")
    id_dispositivo = request.data.get("id_dispositivo")
    tipo_alerta = request.data.get("tipo_alerta")
    nivel = request.data.get("nivel", "WARNING")
    mensaje = request.data.get("mensaje", "").strip()
    atendida = request.data.get("atendida", False)
    fecha_hora = request.data.get("fecha_hora")

    if not id_zona:
        return Response({"error": "La zona es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

    if not tipo_alerta:
        return Response({"error": "El tipo de alerta es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    if not mensaje:
        return Response({"error": "El mensaje es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        zona = ZonaSiembra.objects.get(id_zona=id_zona)
    except ZonaSiembra.DoesNotExist:
        return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    dispositivo = None
    if id_dispositivo:
        try:
            dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
        except DispositivoIot.DoesNotExist:
            return Response({"error": "Dispositivo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    alerta = Alerta.objects.create(
        zona=zona,
        dispositivo=dispositivo,
        tipo_alerta=tipo_alerta,
        nivel=nivel,
        mensaje=mensaje,
        atendida=atendida,
        fecha_hora=parse_dt_or_now(fecha_hora),
    )

    alerta = Alerta.objects.select_related("zona", "dispositivo").get(id_alerta=alerta.id_alerta)
    return Response(alerta_to_dict(alerta), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def alerta_detail_api(request, id_alerta):
    try:
        alerta = Alerta.objects.select_related("zona", "dispositivo").get(id_alerta=id_alerta)
    except Alerta.DoesNotExist:
        return Response({"error": "Alerta no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(alerta_to_dict(alerta), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        id_zona = request.data.get("id_zona", alerta.zona.id_zona)
        id_dispositivo = request.data.get("id_dispositivo", alerta.dispositivo.id_dispositivo if alerta.dispositivo else None)
        tipo_alerta = request.data.get("tipo_alerta", alerta.tipo_alerta)
        nivel = request.data.get("nivel", alerta.nivel)
        mensaje = request.data.get("mensaje", alerta.mensaje)
        atendida = request.data.get("atendida", alerta.atendida)
        fecha_hora = request.data.get("fecha_hora", alerta.fecha_hora)

        mensaje = mensaje.strip() if isinstance(mensaje, str) else mensaje

        if not id_zona:
            return Response({"error": "La zona es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

        if not tipo_alerta:
            return Response({"error": "El tipo de alerta es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        if not mensaje:
            return Response({"error": "El mensaje es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            zona = ZonaSiembra.objects.get(id_zona=id_zona)
        except ZonaSiembra.DoesNotExist:
            return Response({"error": "Zona no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        dispositivo = None
        if id_dispositivo:
            try:
                dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
            except DispositivoIot.DoesNotExist:
                return Response({"error": "Dispositivo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        alerta.zona = zona
        alerta.dispositivo = dispositivo
        alerta.tipo_alerta = tipo_alerta
        alerta.nivel = nivel
        alerta.mensaje = mensaje
        alerta.atendida = atendida
        alerta.fecha_hora = parse_dt_or_now(fecha_hora)
        alerta.save()

        alerta = Alerta.objects.select_related("zona", "dispositivo").get(id_alerta=alerta.id_alerta)
        return Response(alerta_to_dict(alerta), status=status.HTTP_200_OK)

    alerta.delete()
    return Response({"message": "Alerta eliminada correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# USUARIOS DEL MODELO DE NEGOCIO
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAdminOnlyCustom])
def usuarios_api(request):
    if request.method == 'GET':
        usuarios = Usuario.objects.all().order_by("id_usuario")
        data = [usuario_to_dict(usuario) for usuario in usuarios]
        return Response(data, status=status.HTTP_200_OK)

    username = request.data.get("username", "").strip()
    correo = request.data.get("correo", "").strip()
    password_hash = request.data.get("password_hash", "").strip()
    activo = request.data.get("activo", True)

    if not username:
        return Response({"error": "El username es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    if not password_hash:
        return Response({"error": "El password_hash es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    if Usuario.objects.filter(username=username).exists():
        return Response({"error": "Ya existe un usuario con ese username"}, status=status.HTTP_400_BAD_REQUEST)

    if correo and Usuario.objects.filter(correo=correo).exists():
        return Response({"error": "Ya existe un usuario con ese correo"}, status=status.HTTP_400_BAD_REQUEST)

    usuario = Usuario.objects.create(
        username=username,
        correo=correo or None,
        password_hash=password_hash,
        activo=activo,
        fecha_creacion=now_dt(),
        ultimo_acceso=None,
    )

    return Response(usuario_to_dict(usuario), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminOnlyCustom])
def usuario_detail_api(request, id_usuario):
    try:
        usuario = Usuario.objects.get(id_usuario=id_usuario)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(usuario_to_dict(usuario), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        username = request.data.get("username", usuario.username)
        correo = request.data.get("correo", usuario.correo)
        password_hash = request.data.get("password_hash", usuario.password_hash)
        activo = request.data.get("activo", usuario.activo)
        ultimo_acceso = request.data.get("ultimo_acceso", usuario.ultimo_acceso)

        username = username.strip() if isinstance(username, str) else username
        correo = correo.strip() if isinstance(correo, str) else correo
        password_hash = password_hash.strip() if isinstance(password_hash, str) else password_hash

        if not username:
            return Response({"error": "El username es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        if not password_hash:
            return Response({"error": "El password_hash es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        existe_username = Usuario.objects.filter(username=username).exclude(id_usuario=usuario.id_usuario).exists()
        if existe_username:
            return Response({"error": "Ya existe otro usuario con ese username"}, status=status.HTTP_400_BAD_REQUEST)

        if correo:
            existe_correo = Usuario.objects.filter(correo=correo).exclude(id_usuario=usuario.id_usuario).exists()
            if existe_correo:
                return Response({"error": "Ya existe otro usuario con ese correo"}, status=status.HTTP_400_BAD_REQUEST)

        usuario.username = username
        usuario.correo = correo or None
        usuario.password_hash = password_hash
        usuario.activo = activo
        usuario.ultimo_acceso = parse_dt_or_none(ultimo_acceso)
        usuario.save()

        return Response(usuario_to_dict(usuario), status=status.HTTP_200_OK)

    usuario.delete()
    return Response({"message": "Usuario eliminado correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# ROLES
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAdminOnlyCustom])
def roles_api(request):
    if request.method == 'GET':
        roles = Rol.objects.all().order_by("id_rol")
        data = [rol_to_dict(rol) for rol in roles]
        return Response(data, status=status.HTTP_200_OK)

    nombre = request.data.get("nombre", "").strip()
    descripcion = request.data.get("descripcion", "").strip()

    if not nombre:
        return Response({"error": "El nombre del rol es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    if Rol.objects.filter(nombre=nombre).exists():
        return Response({"error": "Ya existe un rol con ese nombre"}, status=status.HTTP_400_BAD_REQUEST)

    rol = Rol.objects.create(
        nombre=nombre,
        descripcion=descripcion or None,
    )

    return Response(rol_to_dict(rol), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminOnlyCustom])
def rol_detail_api(request, id_rol):
    try:
        rol = Rol.objects.get(id_rol=id_rol)
    except Rol.DoesNotExist:
        return Response({"error": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(rol_to_dict(rol), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        nombre = request.data.get("nombre", rol.nombre)
        descripcion = request.data.get("descripcion", rol.descripcion)

        nombre = nombre.strip() if isinstance(nombre, str) else nombre
        descripcion = descripcion.strip() if isinstance(descripcion, str) else descripcion

        if not nombre:
            return Response({"error": "El nombre del rol es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        existe = Rol.objects.filter(nombre=nombre).exclude(id_rol=rol.id_rol).exists()
        if existe:
            return Response({"error": "Ya existe otro rol con ese nombre"}, status=status.HTTP_400_BAD_REQUEST)

        rol.nombre = nombre
        rol.descripcion = descripcion or None
        rol.save()

        return Response(rol_to_dict(rol), status=status.HTTP_200_OK)

    rol.delete()
    return Response({"message": "Rol eliminado correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# USUARIO_ROL
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAdminOnlyCustom])
def usuarios_roles_api(request):
    if request.method == 'GET':
        usuarios_roles = UsuarioRol.objects.select_related("usuario", "rol").all().order_by("id_usuario_rol")
        data = [usuario_rol_to_dict(item) for item in usuarios_roles]
        return Response(data, status=status.HTTP_200_OK)

    id_usuario = request.data.get("id_usuario")
    id_rol = request.data.get("id_rol")

    if not id_usuario:
        return Response({"error": "El usuario es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    if not id_rol:
        return Response({"error": "El rol es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(id_usuario=id_usuario)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    try:
        rol = Rol.objects.get(id_rol=id_rol)
    except Rol.DoesNotExist:
        return Response({"error": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    existe = UsuarioRol.objects.filter(usuario=usuario, rol=rol).exists()
    if existe:
        return Response({"error": "Ese usuario ya tiene ese rol"}, status=status.HTTP_400_BAD_REQUEST)

    usuario_rol = UsuarioRol.objects.create(
        usuario=usuario,
        rol=rol,
        fecha_asignacion=now_dt(),
    )

    usuario_rol = UsuarioRol.objects.select_related("usuario", "rol").get(id_usuario_rol=usuario_rol.id_usuario_rol)
    return Response(usuario_rol_to_dict(usuario_rol), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminOnlyCustom])
def usuario_rol_detail_api(request, id_usuario_rol):
    try:
        usuario_rol = UsuarioRol.objects.select_related("usuario", "rol").get(id_usuario_rol=id_usuario_rol)
    except UsuarioRol.DoesNotExist:
        return Response({"error": "Relación usuario-rol no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(usuario_rol_to_dict(usuario_rol), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        id_usuario = request.data.get("id_usuario", usuario_rol.usuario.id_usuario)
        id_rol = request.data.get("id_rol", usuario_rol.rol.id_rol)

        if not id_usuario:
            return Response({"error": "El usuario es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        if not id_rol:
            return Response({"error": "El rol es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = Usuario.objects.get(id_usuario=id_usuario)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        try:
            rol = Rol.objects.get(id_rol=id_rol)
        except Rol.DoesNotExist:
            return Response({"error": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        existe = UsuarioRol.objects.filter(
            usuario=usuario,
            rol=rol
        ).exclude(id_usuario_rol=usuario_rol.id_usuario_rol).exists()

        if existe:
            return Response({"error": "Ya existe esa relación usuario-rol"}, status=status.HTTP_400_BAD_REQUEST)

        usuario_rol.usuario = usuario
        usuario_rol.rol = rol
        usuario_rol.save()

        usuario_rol = UsuarioRol.objects.select_related("usuario", "rol").get(id_usuario_rol=usuario_rol.id_usuario_rol)
        return Response(usuario_rol_to_dict(usuario_rol), status=status.HTTP_200_OK)

    usuario_rol.delete()
    return Response({"message": "Relación usuario-rol eliminada correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# COMANDOS REMOTOS
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def comandos_remotos_api(request):
    if request.method == 'GET':
        comandos = ComandoRemoto.objects.select_related("dispositivo", "bomba", "usuario").all().order_by("-id_comando")
        data = [comando_remoto_to_dict(comando) for comando in comandos]
        return Response(data, status=status.HTTP_200_OK)

    id_dispositivo = request.data.get("id_dispositivo")
    id_bomba = request.data.get("id_bomba")
    id_usuario = request.data.get("id_usuario")
    accion = request.data.get("accion")
    estado = request.data.get("estado", "PENDIENTE")
    parametros_texto = request.data.get("parametros_texto", "").strip()
    fecha_hora_envio = request.data.get("fecha_hora_envio")

    if not id_dispositivo:
        return Response({"error": "El dispositivo es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    if not accion:
        return Response({"error": "La acción es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
    except DispositivoIot.DoesNotExist:
        return Response({"error": "Dispositivo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    bomba = None
    if id_bomba:
        try:
            bomba = BombaAgua.objects.get(id_bomba=id_bomba)
        except BombaAgua.DoesNotExist:
            return Response({"error": "Bomba no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    usuario = None
    if id_usuario:
        try:
            usuario = Usuario.objects.get(id_usuario=id_usuario)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    comando = ComandoRemoto.objects.create(
        dispositivo=dispositivo,
        bomba=bomba,
        usuario=usuario,
        accion=accion,
        estado=estado,
        parametros_texto=parametros_texto or None,
        fecha_hora_envio=parse_dt_or_now(fecha_hora_envio),
    )

    comando = ComandoRemoto.objects.select_related("dispositivo", "bomba", "usuario").get(id_comando=comando.id_comando)
    return Response(comando_remoto_to_dict(comando), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def comando_remoto_detail_api(request, id_comando):
    try:
        comando = ComandoRemoto.objects.select_related("dispositivo", "bomba", "usuario").get(id_comando=id_comando)
    except ComandoRemoto.DoesNotExist:
        return Response({"error": "Comando remoto no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(comando_remoto_to_dict(comando), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        id_dispositivo = request.data.get("id_dispositivo", comando.dispositivo.id_dispositivo)
        id_bomba = request.data.get("id_bomba", comando.bomba.id_bomba if comando.bomba else None)
        id_usuario = request.data.get("id_usuario", comando.usuario.id_usuario if comando.usuario else None)
        accion = request.data.get("accion", comando.accion)
        estado_valor = request.data.get("estado", comando.estado)
        parametros_texto = request.data.get("parametros_texto", comando.parametros_texto)
        fecha_hora_envio = request.data.get("fecha_hora_envio", comando.fecha_hora_envio)

        if not id_dispositivo:
            return Response({"error": "El dispositivo es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        if not accion:
            return Response({"error": "La acción es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
        except DispositivoIot.DoesNotExist:
            return Response({"error": "Dispositivo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        bomba = None
        if id_bomba:
            try:
                bomba = BombaAgua.objects.get(id_bomba=id_bomba)
            except BombaAgua.DoesNotExist:
                return Response({"error": "Bomba no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        usuario = None
        if id_usuario:
            try:
                usuario = Usuario.objects.get(id_usuario=id_usuario)
            except Usuario.DoesNotExist:
                return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        comando.dispositivo = dispositivo
        comando.bomba = bomba
        comando.usuario = usuario
        comando.accion = accion
        comando.estado = estado_valor
        comando.parametros_texto = parametros_texto
        comando.fecha_hora_envio = parse_dt_or_now(fecha_hora_envio)
        comando.save()

        comando = ComandoRemoto.objects.select_related("dispositivo", "bomba", "usuario").get(id_comando=comando.id_comando)
        return Response(comando_remoto_to_dict(comando), status=status.HTTP_200_OK)

    comando.delete()
    return Response({"message": "Comando remoto eliminado correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# RESPUESTAS DE COMANDO
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def respuestas_comando_api(request):
    if request.method == 'GET':
        respuestas = RespuestaComando.objects.select_related("comando").all().order_by("-id_respuesta")
        data = [respuesta_comando_to_dict(respuesta) for respuesta in respuestas]
        return Response(data, status=status.HTTP_200_OK)

    id_comando = request.data.get("id_comando")
    codigo_respuesta = request.data.get("codigo_respuesta", "").strip()
    mensaje = request.data.get("mensaje", "").strip()
    exitoso = request.data.get("exitoso", True)
    fecha_hora_respuesta = request.data.get("fecha_hora_respuesta")

    if not id_comando:
        return Response({"error": "El comando es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        comando = ComandoRemoto.objects.get(id_comando=id_comando)
    except ComandoRemoto.DoesNotExist:
        return Response({"error": "Comando no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    respuesta = RespuestaComando.objects.create(
        comando=comando,
        codigo_respuesta=codigo_respuesta or None,
        mensaje=mensaje or None,
        exitoso=exitoso,
        fecha_hora_respuesta=parse_dt_or_now(fecha_hora_respuesta),
    )

    respuesta = RespuestaComando.objects.select_related("comando").get(id_respuesta=respuesta.id_respuesta)
    return Response(respuesta_comando_to_dict(respuesta), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedReadAdminWrite])
def respuesta_comando_detail_api(request, id_respuesta):
    try:
        respuesta = RespuestaComando.objects.select_related("comando").get(id_respuesta=id_respuesta)
    except RespuestaComando.DoesNotExist:
        return Response({"error": "Respuesta de comando no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(respuesta_comando_to_dict(respuesta), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        id_comando = request.data.get("id_comando", respuesta.comando.id_comando)
        codigo_respuesta = request.data.get("codigo_respuesta", respuesta.codigo_respuesta)
        mensaje = request.data.get("mensaje", respuesta.mensaje)
        exitoso = request.data.get("exitoso", respuesta.exitoso)
        fecha_hora_respuesta = request.data.get("fecha_hora_respuesta", respuesta.fecha_hora_respuesta)

        codigo_respuesta = codigo_respuesta.strip() if isinstance(codigo_respuesta, str) else codigo_respuesta
        mensaje = mensaje.strip() if isinstance(mensaje, str) else mensaje

        if not id_comando:
            return Response({"error": "El comando es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            comando = ComandoRemoto.objects.get(id_comando=id_comando)
        except ComandoRemoto.DoesNotExist:
            return Response({"error": "Comando no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        respuesta.comando = comando
        respuesta.codigo_respuesta = codigo_respuesta or None
        respuesta.mensaje = mensaje or None
        respuesta.exitoso = exitoso
        respuesta.fecha_hora_respuesta = parse_dt_or_now(fecha_hora_respuesta)
        respuesta.save()

        respuesta = RespuestaComando.objects.select_related("comando").get(id_respuesta=respuesta.id_respuesta)
        return Response(respuesta_comando_to_dict(respuesta), status=status.HTTP_200_OK)

    respuesta.delete()
    return Response({"message": "Respuesta de comando eliminada correctamente"}, status=status.HTTP_200_OK)


# =========================================================
# AUDITORÍA
# =========================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAdminOnlyCustom])
def auditorias_api(request):
    if request.method == 'GET':
        auditorias = AuditoriaSistema.objects.select_related("usuario").all().order_by("-id_auditoria")
        data = [auditoria_to_dict(auditoria) for auditoria in auditorias]
        return Response(data, status=status.HTTP_200_OK)

    id_usuario = request.data.get("id_usuario")
    accion = request.data.get("accion", "").strip()
    tabla_afectada = request.data.get("tabla_afectada", "").strip()
    id_registro_afectado = request.data.get("id_registro_afectado")
    detalle = request.data.get("detalle", "").strip()
    ip_origen = request.data.get("ip_origen", "").strip()
    fecha_hora = request.data.get("fecha_hora")

    if not accion:
        return Response({"error": "La acción es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

    usuario = None
    if id_usuario:
        try:
            usuario = Usuario.objects.get(id_usuario=id_usuario)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    auditoria = AuditoriaSistema.objects.create(
        usuario=usuario,
        accion=accion,
        tabla_afectada=tabla_afectada or None,
        id_registro_afectado=id_registro_afectado if id_registro_afectado not in ("", None) else None,
        detalle=detalle or None,
        ip_origen=ip_origen or None,
        fecha_hora=parse_dt_or_now(fecha_hora),
    )

    auditoria = AuditoriaSistema.objects.select_related("usuario").get(id_auditoria=auditoria.id_auditoria)
    return Response(auditoria_to_dict(auditoria), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminOnlyCustom])
def auditoria_detail_api(request, id_auditoria):
    try:
        auditoria = AuditoriaSistema.objects.select_related("usuario").get(id_auditoria=id_auditoria)
    except AuditoriaSistema.DoesNotExist:
        return Response({"error": "Auditoría no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(auditoria_to_dict(auditoria), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        id_usuario = request.data.get("id_usuario", auditoria.usuario.id_usuario if auditoria.usuario else None)
        accion = request.data.get("accion", auditoria.accion)
        tabla_afectada = request.data.get("tabla_afectada", auditoria.tabla_afectada)
        id_registro_afectado = request.data.get("id_registro_afectado", auditoria.id_registro_afectado)
        detalle = request.data.get("detalle", auditoria.detalle)
        ip_origen = request.data.get("ip_origen", auditoria.ip_origen)
        fecha_hora = request.data.get("fecha_hora", auditoria.fecha_hora)

        accion = accion.strip() if isinstance(accion, str) else accion
        tabla_afectada = tabla_afectada.strip() if isinstance(tabla_afectada, str) else tabla_afectada
        detalle = detalle.strip() if isinstance(detalle, str) else detalle
        ip_origen = ip_origen.strip() if isinstance(ip_origen, str) else ip_origen

        if not accion:
            return Response({"error": "La acción es obligatoria"}, status=status.HTTP_400_BAD_REQUEST)

        usuario = None
        if id_usuario:
            try:
                usuario = Usuario.objects.get(id_usuario=id_usuario)
            except Usuario.DoesNotExist:
                return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        auditoria.usuario = usuario
        auditoria.accion = accion
        auditoria.tabla_afectada = tabla_afectada or None
        auditoria.id_registro_afectado = id_registro_afectado if id_registro_afectado not in ("", None) else None
        auditoria.detalle = detalle or None
        auditoria.ip_origen = ip_origen or None
        auditoria.fecha_hora = parse_dt_or_now(fecha_hora)
        auditoria.save()

        auditoria = AuditoriaSistema.objects.select_related("usuario").get(id_auditoria=auditoria.id_auditoria)
        return Response(auditoria_to_dict(auditoria), status=status.HTTP_200_OK)

    auditoria.delete()
    return Response({"message": "Auditoría eliminada correctamente"}, status=status.HTTP_200_OK)