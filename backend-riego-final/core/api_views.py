import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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
# HELPERS
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


# =========================================================
# PREDIOS
# =========================================================

@csrf_exempt
def predios_api(request):
    if request.method == "GET":
        predios = Predio.objects.all().order_by("id_predio")
        data = [predio_to_dict(predio) for predio in predios]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            nombre = body.get("nombre", "").strip()
            ubicacion = body.get("ubicacion", "").strip()
            descripcion = body.get("descripcion", "").strip()
            activo = body.get("activo", True)

            if not nombre:
                return JsonResponse({"error": "El nombre es obligatorio"}, status=400)

            predio = Predio.objects.create(
                nombre=nombre,
                ubicacion=ubicacion or None,
                descripcion=descripcion or None,
                activo=activo,
            )

            return JsonResponse(predio_to_dict(predio), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def predio_detail_api(request, id_predio):
    try:
        predio = Predio.objects.get(id_predio=id_predio)
    except Predio.DoesNotExist:
        return JsonResponse({"error": "Predio no encontrado"}, status=404)

    if request.method == "GET":
        return JsonResponse(predio_to_dict(predio))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            nombre = body.get("nombre", predio.nombre)
            ubicacion = body.get("ubicacion", predio.ubicacion)
            descripcion = body.get("descripcion", predio.descripcion)
            activo = body.get("activo", predio.activo)

            nombre = nombre.strip() if isinstance(nombre, str) else nombre

            if not nombre:
                return JsonResponse({"error": "El nombre es obligatorio"}, status=400)

            predio.nombre = nombre
            predio.ubicacion = ubicacion
            predio.descripcion = descripcion
            predio.activo = activo
            predio.save()

            return JsonResponse(predio_to_dict(predio))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        predio.delete()
        return JsonResponse({"message": "Predio eliminado correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# ZONAS
# =========================================================

@csrf_exempt
def zonas_api(request):
    if request.method == "GET":
        zonas = ZonaSiembra.objects.select_related("predio").all().order_by("id_zona")
        data = [zona_to_dict(zona) for zona in zonas]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            predio_id = body.get("id_predio")
            nombre = body.get("nombre", "").strip()
            cultivo = body.get("cultivo", "").strip()
            descripcion = body.get("descripcion", "").strip()
            area_m2 = body.get("area_m2")
            activa = body.get("activa", True)

            if not predio_id:
                return JsonResponse({"error": "El predio es obligatorio"}, status=400)

            if not nombre:
                return JsonResponse({"error": "El nombre es obligatorio"}, status=400)

            try:
                predio = Predio.objects.get(id_predio=predio_id)
            except Predio.DoesNotExist:
                return JsonResponse({"error": "Predio no encontrado"}, status=404)

            existe = ZonaSiembra.objects.filter(predio_id=predio_id, nombre=nombre).exists()
            if existe:
                return JsonResponse(
                    {"error": "Ya existe una zona con ese nombre en ese predio"},
                    status=400
                )

            zona = ZonaSiembra.objects.create(
                predio=predio,
                nombre=nombre,
                cultivo=cultivo or None,
                descripcion=descripcion or None,
                area_m2=area_m2 if area_m2 not in ("", None) else None,
                activa=activa,
            )

            zona = ZonaSiembra.objects.select_related("predio").get(id_zona=zona.id_zona)
            return JsonResponse(zona_to_dict(zona), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def zona_detail_api(request, id_zona):
    try:
        zona = ZonaSiembra.objects.select_related("predio").get(id_zona=id_zona)
    except ZonaSiembra.DoesNotExist:
        return JsonResponse({"error": "Zona no encontrada"}, status=404)

    if request.method == "GET":
        return JsonResponse(zona_to_dict(zona))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            predio_id = body.get("id_predio", zona.predio.id_predio)
            nombre = body.get("nombre", zona.nombre)
            cultivo = body.get("cultivo", zona.cultivo)
            descripcion = body.get("descripcion", zona.descripcion)
            area_m2 = body.get("area_m2", zona.area_m2)
            activa = body.get("activa", zona.activa)

            nombre = nombre.strip() if isinstance(nombre, str) else nombre

            if not predio_id:
                return JsonResponse({"error": "El predio es obligatorio"}, status=400)

            if not nombre:
                return JsonResponse({"error": "El nombre es obligatorio"}, status=400)

            try:
                predio = Predio.objects.get(id_predio=predio_id)
            except Predio.DoesNotExist:
                return JsonResponse({"error": "Predio no encontrado"}, status=404)

            existe = ZonaSiembra.objects.filter(
                predio_id=predio_id,
                nombre=nombre
            ).exclude(id_zona=zona.id_zona).exists()

            if existe:
                return JsonResponse(
                    {"error": "Ya existe otra zona con ese nombre en ese predio"},
                    status=400
                )

            zona.predio = predio
            zona.nombre = nombre
            zona.cultivo = cultivo
            zona.descripcion = descripcion
            zona.area_m2 = area_m2 if area_m2 not in ("", None) else None
            zona.activa = activa
            zona.save()

            zona = ZonaSiembra.objects.select_related("predio").get(id_zona=zona.id_zona)
            return JsonResponse(zona_to_dict(zona))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        zona.delete()
        return JsonResponse({"message": "Zona eliminada correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# DISPOSITIVOS
# =========================================================

@csrf_exempt
def dispositivos_api(request):
    if request.method == "GET":
        dispositivos = DispositivoIot.objects.select_related("zona").all().order_by("id_dispositivo")
        data = [dispositivo_to_dict(dispositivo) for dispositivo in dispositivos]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            zona_id = body.get("id_zona")
            codigo = body.get("codigo", "").strip()
            nombre = body.get("nombre", "").strip()
            modelo = body.get("modelo", "").strip()
            direccion_ip = body.get("direccion_ip", "").strip()
            mac_address = body.get("mac_address", "").strip()
            estado = body.get("estado", "ACTIVO")
            activo = body.get("activo", True)

            if not zona_id:
                return JsonResponse({"error": "La zona es obligatoria"}, status=400)

            if not codigo:
                return JsonResponse({"error": "El código es obligatorio"}, status=400)

            if not nombre:
                return JsonResponse({"error": "El nombre es obligatorio"}, status=400)

            try:
                zona = ZonaSiembra.objects.get(id_zona=zona_id)
            except ZonaSiembra.DoesNotExist:
                return JsonResponse({"error": "Zona no encontrada"}, status=404)

            if DispositivoIot.objects.filter(codigo=codigo).exists():
                return JsonResponse({"error": "Ya existe un dispositivo con ese código"}, status=400)

            if mac_address and DispositivoIot.objects.filter(mac_address=mac_address).exists():
                return JsonResponse({"error": "Ya existe un dispositivo con esa MAC"}, status=400)

            dispositivo = DispositivoIot.objects.create(
                zona=zona,
                codigo=codigo,
                nombre=nombre,
                modelo=modelo or None,
                direccion_ip=direccion_ip or None,
                mac_address=mac_address or None,
                estado=estado,
                activo=activo,
            )

            dispositivo = DispositivoIot.objects.select_related("zona").get(id_dispositivo=dispositivo.id_dispositivo)
            return JsonResponse(dispositivo_to_dict(dispositivo), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def dispositivo_detail_api(request, id_dispositivo):
    try:
        dispositivo = DispositivoIot.objects.select_related("zona").get(id_dispositivo=id_dispositivo)
    except DispositivoIot.DoesNotExist:
        return JsonResponse({"error": "Dispositivo no encontrado"}, status=404)

    if request.method == "GET":
        return JsonResponse(dispositivo_to_dict(dispositivo))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            zona_id = body.get("id_zona", dispositivo.zona.id_zona)
            codigo = body.get("codigo", dispositivo.codigo)
            nombre = body.get("nombre", dispositivo.nombre)
            modelo = body.get("modelo", dispositivo.modelo)
            direccion_ip = body.get("direccion_ip", dispositivo.direccion_ip)
            mac_address = body.get("mac_address", dispositivo.mac_address)
            estado = body.get("estado", dispositivo.estado)
            activo = body.get("activo", dispositivo.activo)

            codigo = codigo.strip() if isinstance(codigo, str) else codigo
            nombre = nombre.strip() if isinstance(nombre, str) else nombre
            modelo = modelo.strip() if isinstance(modelo, str) else modelo
            direccion_ip = direccion_ip.strip() if isinstance(direccion_ip, str) else direccion_ip
            mac_address = mac_address.strip() if isinstance(mac_address, str) else mac_address

            if not zona_id:
                return JsonResponse({"error": "La zona es obligatoria"}, status=400)

            if not codigo:
                return JsonResponse({"error": "El código es obligatorio"}, status=400)

            if not nombre:
                return JsonResponse({"error": "El nombre es obligatorio"}, status=400)

            try:
                zona = ZonaSiembra.objects.get(id_zona=zona_id)
            except ZonaSiembra.DoesNotExist:
                return JsonResponse({"error": "Zona no encontrada"}, status=404)

            existe_codigo = DispositivoIot.objects.filter(codigo=codigo).exclude(
                id_dispositivo=dispositivo.id_dispositivo
            ).exists()
            if existe_codigo:
                return JsonResponse({"error": "Ya existe otro dispositivo con ese código"}, status=400)

            if mac_address:
                existe_mac = DispositivoIot.objects.filter(mac_address=mac_address).exclude(
                    id_dispositivo=dispositivo.id_dispositivo
                ).exists()
                if existe_mac:
                    return JsonResponse({"error": "Ya existe otro dispositivo con esa MAC"}, status=400)

            dispositivo.zona = zona
            dispositivo.codigo = codigo
            dispositivo.nombre = nombre
            dispositivo.modelo = modelo or None
            dispositivo.direccion_ip = direccion_ip or None
            dispositivo.mac_address = mac_address or None
            dispositivo.estado = estado
            dispositivo.activo = activo
            dispositivo.save()

            dispositivo = DispositivoIot.objects.select_related("zona").get(id_dispositivo=dispositivo.id_dispositivo)
            return JsonResponse(dispositivo_to_dict(dispositivo))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        dispositivo.delete()
        return JsonResponse({"message": "Dispositivo eliminado correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)

# =========================================================
# HELPERS BLOQUE 2
# =========================================================

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


# =========================================================
# SENSORES
# =========================================================

@csrf_exempt
def sensores_api(request):
    if request.method == "GET":
        sensores = Sensor.objects.select_related("dispositivo", "zona").all().order_by("id_sensor")
        data = [sensor_to_dict(sensor) for sensor in sensores]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            id_dispositivo = body.get("id_dispositivo")
            id_zona = body.get("id_zona")
            nombre = body.get("nombre", "").strip()
            tipo_sensor = body.get("tipo_sensor", "HUMEDAD")
            unidad_medida = body.get("unidad_medida", "%").strip()
            estado = body.get("estado", "ACTIVO")
            activo = body.get("activo", True)

            if not id_dispositivo:
                return JsonResponse({"error": "El dispositivo es obligatorio"}, status=400)

            if not id_zona:
                return JsonResponse({"error": "La zona es obligatoria"}, status=400)

            if not nombre:
                return JsonResponse({"error": "El nombre es obligatorio"}, status=400)

            try:
                dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
            except DispositivoIot.DoesNotExist:
                return JsonResponse({"error": "Dispositivo no encontrado"}, status=404)

            try:
                zona = ZonaSiembra.objects.get(id_zona=id_zona)
            except ZonaSiembra.DoesNotExist:
                return JsonResponse({"error": "Zona no encontrada"}, status=404)

            existe = Sensor.objects.filter(dispositivo=dispositivo, nombre=nombre).exists()
            if existe:
                return JsonResponse(
                    {"error": "Ya existe un sensor con ese nombre en ese dispositivo"},
                    status=400
                )

            sensor = Sensor.objects.create(
                dispositivo=dispositivo,
                zona=zona,
                nombre=nombre,
                tipo_sensor=tipo_sensor,
                unidad_medida=unidad_medida,
                estado=estado,
                activo=activo,
            )

            sensor = Sensor.objects.select_related("dispositivo", "zona").get(id_sensor=sensor.id_sensor)
            return JsonResponse(sensor_to_dict(sensor), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def sensor_detail_api(request, id_sensor):
    try:
        sensor = Sensor.objects.select_related("dispositivo", "zona").get(id_sensor=id_sensor)
    except Sensor.DoesNotExist:
        return JsonResponse({"error": "Sensor no encontrado"}, status=404)

    if request.method == "GET":
        return JsonResponse(sensor_to_dict(sensor))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            id_dispositivo = body.get("id_dispositivo", sensor.dispositivo.id_dispositivo)
            id_zona = body.get("id_zona", sensor.zona.id_zona)
            nombre = body.get("nombre", sensor.nombre)
            tipo_sensor = body.get("tipo_sensor", sensor.tipo_sensor)
            unidad_medida = body.get("unidad_medida", sensor.unidad_medida)
            estado = body.get("estado", sensor.estado)
            activo = body.get("activo", sensor.activo)

            nombre = nombre.strip() if isinstance(nombre, str) else nombre
            unidad_medida = unidad_medida.strip() if isinstance(unidad_medida, str) else unidad_medida

            if not id_dispositivo:
                return JsonResponse({"error": "El dispositivo es obligatorio"}, status=400)

            if not id_zona:
                return JsonResponse({"error": "La zona es obligatoria"}, status=400)

            if not nombre:
                return JsonResponse({"error": "El nombre es obligatorio"}, status=400)

            try:
                dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
            except DispositivoIot.DoesNotExist:
                return JsonResponse({"error": "Dispositivo no encontrado"}, status=404)

            try:
                zona = ZonaSiembra.objects.get(id_zona=id_zona)
            except ZonaSiembra.DoesNotExist:
                return JsonResponse({"error": "Zona no encontrada"}, status=404)

            existe = Sensor.objects.filter(
                dispositivo=dispositivo,
                nombre=nombre
            ).exclude(id_sensor=sensor.id_sensor).exists()

            if existe:
                return JsonResponse(
                    {"error": "Ya existe otro sensor con ese nombre en ese dispositivo"},
                    status=400
                )

            sensor.dispositivo = dispositivo
            sensor.zona = zona
            sensor.nombre = nombre
            sensor.tipo_sensor = tipo_sensor
            sensor.unidad_medida = unidad_medida
            sensor.estado = estado
            sensor.activo = activo
            sensor.save()

            sensor = Sensor.objects.select_related("dispositivo", "zona").get(id_sensor=sensor.id_sensor)
            return JsonResponse(sensor_to_dict(sensor))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        sensor.delete()
        return JsonResponse({"message": "Sensor eliminado correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# BOMBAS DE AGUA
# =========================================================

@csrf_exempt
def bombas_api(request):
    if request.method == "GET":
        bombas = BombaAgua.objects.select_related("zona", "dispositivo").all().order_by("id_bomba")
        data = [bomba_to_dict(bomba) for bomba in bombas]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            id_zona = body.get("id_zona")
            id_dispositivo = body.get("id_dispositivo")
            nombre = body.get("nombre", "").strip()
            caudal_litros_min = body.get("caudal_litros_min")
            estado_actual = body.get("estado_actual", "APAGADA")
            activa = body.get("activa", True)

            if not id_zona:
                return JsonResponse({"error": "La zona es obligatoria"}, status=400)

            if not nombre:
                return JsonResponse({"error": "El nombre es obligatorio"}, status=400)

            try:
                zona = ZonaSiembra.objects.get(id_zona=id_zona)
            except ZonaSiembra.DoesNotExist:
                return JsonResponse({"error": "Zona no encontrada"}, status=404)

            dispositivo = None
            if id_dispositivo:
                try:
                    dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
                except DispositivoIot.DoesNotExist:
                    return JsonResponse({"error": "Dispositivo no encontrado"}, status=404)

            existe = BombaAgua.objects.filter(zona=zona, nombre=nombre).exists()
            if existe:
                return JsonResponse(
                    {"error": "Ya existe una bomba con ese nombre en esa zona"},
                    status=400
                )

            bomba = BombaAgua.objects.create(
                zona=zona,
                dispositivo=dispositivo,
                nombre=nombre,
                caudal_litros_min=caudal_litros_min if caudal_litros_min not in ("", None) else None,
                estado_actual=estado_actual,
                activa=activa,
            )

            bomba = BombaAgua.objects.select_related("zona", "dispositivo").get(id_bomba=bomba.id_bomba)
            return JsonResponse(bomba_to_dict(bomba), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def bomba_detail_api(request, id_bomba):
    try:
        bomba = BombaAgua.objects.select_related("zona", "dispositivo").get(id_bomba=id_bomba)
    except BombaAgua.DoesNotExist:
        return JsonResponse({"error": "Bomba no encontrada"}, status=404)

    if request.method == "GET":
        return JsonResponse(bomba_to_dict(bomba))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            id_zona = body.get("id_zona", bomba.zona.id_zona)
            id_dispositivo = body.get("id_dispositivo", bomba.dispositivo.id_dispositivo if bomba.dispositivo else None)
            nombre = body.get("nombre", bomba.nombre)
            caudal_litros_min = body.get("caudal_litros_min", bomba.caudal_litros_min)
            estado_actual = body.get("estado_actual", bomba.estado_actual)
            activa = body.get("activa", bomba.activa)

            nombre = nombre.strip() if isinstance(nombre, str) else nombre

            if not id_zona:
                return JsonResponse({"error": "La zona es obligatoria"}, status=400)

            if not nombre:
                return JsonResponse({"error": "El nombre es obligatorio"}, status=400)

            try:
                zona = ZonaSiembra.objects.get(id_zona=id_zona)
            except ZonaSiembra.DoesNotExist:
                return JsonResponse({"error": "Zona no encontrada"}, status=404)

            dispositivo = None
            if id_dispositivo:
                try:
                    dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
                except DispositivoIot.DoesNotExist:
                    return JsonResponse({"error": "Dispositivo no encontrado"}, status=404)

            existe = BombaAgua.objects.filter(
                zona=zona,
                nombre=nombre
            ).exclude(id_bomba=bomba.id_bomba).exists()

            if existe:
                return JsonResponse(
                    {"error": "Ya existe otra bomba con ese nombre en esa zona"},
                    status=400
                )

            bomba.zona = zona
            bomba.dispositivo = dispositivo
            bomba.nombre = nombre
            bomba.caudal_litros_min = caudal_litros_min if caudal_litros_min not in ("", None) else None
            bomba.estado_actual = estado_actual
            bomba.activa = activa
            bomba.save()

            bomba = BombaAgua.objects.select_related("zona", "dispositivo").get(id_bomba=bomba.id_bomba)
            return JsonResponse(bomba_to_dict(bomba))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        bomba.delete()
        return JsonResponse({"message": "Bomba eliminada correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# LECTURAS DE HUMEDAD
# =========================================================

@csrf_exempt
def lecturas_humedad_api(request):
    if request.method == "GET":
        lecturas = LecturaHumedad.objects.select_related("sensor", "zona").all().order_by("-id_lectura_humedad")
        data = [lectura_humedad_to_dict(lectura) for lectura in lecturas]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            id_sensor = body.get("id_sensor")
            id_zona = body.get("id_zona")
            valor_humedad = body.get("valor_humedad")
            temperatura = body.get("temperatura")

            if not id_sensor:
                return JsonResponse({"error": "El sensor es obligatorio"}, status=400)

            if not id_zona:
                return JsonResponse({"error": "La zona es obligatoria"}, status=400)

            if valor_humedad in ("", None):
                return JsonResponse({"error": "El valor de humedad es obligatorio"}, status=400)

            try:
                sensor = Sensor.objects.get(id_sensor=id_sensor)
            except Sensor.DoesNotExist:
                return JsonResponse({"error": "Sensor no encontrado"}, status=404)

            try:
                zona = ZonaSiembra.objects.get(id_zona=id_zona)
            except ZonaSiembra.DoesNotExist:
                return JsonResponse({"error": "Zona no encontrada"}, status=404)

            lectura = LecturaHumedad.objects.create(
                sensor=sensor,
                zona=zona,
                valor_humedad=valor_humedad,
                temperatura=temperatura if temperatura not in ("", None) else None,
            )

            lectura = LecturaHumedad.objects.select_related("sensor", "zona").get(
                id_lectura_humedad=lectura.id_lectura_humedad
            )
            return JsonResponse(lectura_humedad_to_dict(lectura), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def lectura_humedad_detail_api(request, id_lectura_humedad):
    try:
        lectura = LecturaHumedad.objects.select_related("sensor", "zona").get(
            id_lectura_humedad=id_lectura_humedad
        )
    except LecturaHumedad.DoesNotExist:
        return JsonResponse({"error": "Lectura no encontrada"}, status=404)

    if request.method == "GET":
        return JsonResponse(lectura_humedad_to_dict(lectura))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            id_sensor = body.get("id_sensor", lectura.sensor.id_sensor)
            id_zona = body.get("id_zona", lectura.zona.id_zona)
            valor_humedad = body.get("valor_humedad", lectura.valor_humedad)
            temperatura = body.get("temperatura", lectura.temperatura)

            if not id_sensor:
                return JsonResponse({"error": "El sensor es obligatorio"}, status=400)

            if not id_zona:
                return JsonResponse({"error": "La zona es obligatoria"}, status=400)

            if valor_humedad in ("", None):
                return JsonResponse({"error": "El valor de humedad es obligatorio"}, status=400)

            try:
                sensor = Sensor.objects.get(id_sensor=id_sensor)
            except Sensor.DoesNotExist:
                return JsonResponse({"error": "Sensor no encontrado"}, status=404)

            try:
                zona = ZonaSiembra.objects.get(id_zona=id_zona)
            except ZonaSiembra.DoesNotExist:
                return JsonResponse({"error": "Zona no encontrada"}, status=404)

            lectura.sensor = sensor
            lectura.zona = zona
            lectura.valor_humedad = valor_humedad
            lectura.temperatura = temperatura if temperatura not in ("", None) else None
            lectura.save()

            lectura = LecturaHumedad.objects.select_related("sensor", "zona").get(
                id_lectura_humedad=lectura.id_lectura_humedad
            )
            return JsonResponse(lectura_humedad_to_dict(lectura))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        lectura.delete()
        return JsonResponse({"message": "Lectura eliminada correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# CONFIGURACION RIEGO
# =========================================================

@csrf_exempt
def configuraciones_riego_api(request):
    if request.method == "GET":
        configuraciones = ConfiguracionRiego.objects.select_related("zona").all().order_by("id_configuracion")
        data = [configuracion_riego_to_dict(config) for config in configuraciones]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            id_zona = body.get("id_zona")
            umbral_humedad = body.get("umbral_humedad")
            tiempo_riego_segundos = body.get("tiempo_riego_segundos")
            modo_riego = body.get("modo_riego", "AUTOMATICO")
            intervalo_lectura_segundos = body.get("intervalo_lectura_segundos", 60)
            riego_habilitado = body.get("riego_habilitado", True)
            vigente = body.get("vigente", True)

            if not id_zona:
                return JsonResponse({"error": "La zona es obligatoria"}, status=400)

            if umbral_humedad in ("", None):
                return JsonResponse({"error": "El umbral de humedad es obligatorio"}, status=400)

            if tiempo_riego_segundos in ("", None):
                return JsonResponse({"error": "El tiempo de riego es obligatorio"}, status=400)

            try:
                zona = ZonaSiembra.objects.get(id_zona=id_zona)
            except ZonaSiembra.DoesNotExist:
                return JsonResponse({"error": "Zona no encontrada"}, status=404)

            config = ConfiguracionRiego.objects.create(
                zona=zona,
                umbral_humedad=umbral_humedad,
                tiempo_riego_segundos=tiempo_riego_segundos,
                modo_riego=modo_riego,
                intervalo_lectura_segundos=intervalo_lectura_segundos,
                riego_habilitado=riego_habilitado,
                vigente=vigente,
            )

            config = ConfiguracionRiego.objects.select_related("zona").get(id_configuracion=config.id_configuracion)
            return JsonResponse(configuracion_riego_to_dict(config), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def configuracion_riego_detail_api(request, id_configuracion):
    try:
        config = ConfiguracionRiego.objects.select_related("zona").get(id_configuracion=id_configuracion)
    except ConfiguracionRiego.DoesNotExist:
        return JsonResponse({"error": "Configuración no encontrada"}, status=404)

    if request.method == "GET":
        return JsonResponse(configuracion_riego_to_dict(config))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            id_zona = body.get("id_zona", config.zona.id_zona)
            umbral_humedad = body.get("umbral_humedad", config.umbral_humedad)
            tiempo_riego_segundos = body.get("tiempo_riego_segundos", config.tiempo_riego_segundos)
            modo_riego = body.get("modo_riego", config.modo_riego)
            intervalo_lectura_segundos = body.get("intervalo_lectura_segundos", config.intervalo_lectura_segundos)
            riego_habilitado = body.get("riego_habilitado", config.riego_habilitado)
            vigente = body.get("vigente", config.vigente)

            if not id_zona:
                return JsonResponse({"error": "La zona es obligatoria"}, status=400)

            if umbral_humedad in ("", None):
                return JsonResponse({"error": "El umbral de humedad es obligatorio"}, status=400)

            if tiempo_riego_segundos in ("", None):
                return JsonResponse({"error": "El tiempo de riego es obligatorio"}, status=400)

            try:
                zona = ZonaSiembra.objects.get(id_zona=id_zona)
            except ZonaSiembra.DoesNotExist:
                return JsonResponse({"error": "Zona no encontrada"}, status=404)

            config.zona = zona
            config.umbral_humedad = umbral_humedad
            config.tiempo_riego_segundos = tiempo_riego_segundos
            config.modo_riego = modo_riego
            config.intervalo_lectura_segundos = intervalo_lectura_segundos
            config.riego_habilitado = riego_habilitado
            config.vigente = vigente
            config.save()

            config = ConfiguracionRiego.objects.select_related("zona").get(id_configuracion=config.id_configuracion)
            return JsonResponse(configuracion_riego_to_dict(config))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        config.delete()
        return JsonResponse({"message": "Configuración eliminada correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# ESTADO BOMBA
# =========================================================

@csrf_exempt
def estados_bomba_api(request):
    if request.method == "GET":
        estados = EstadoBomba.objects.select_related("bomba").all().order_by("-id_estado_bomba")
        data = [estado_bomba_to_dict(estado) for estado in estados]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            id_bomba = body.get("id_bomba")
            estado = body.get("estado")
            origen = body.get("origen", "MANUAL")
            observacion = body.get("observacion", "").strip()

            if not id_bomba:
                return JsonResponse({"error": "La bomba es obligatoria"}, status=400)

            if not estado:
                return JsonResponse({"error": "El estado es obligatorio"}, status=400)

            try:
                bomba = BombaAgua.objects.get(id_bomba=id_bomba)
            except BombaAgua.DoesNotExist:
                return JsonResponse({"error": "Bomba no encontrada"}, status=404)

            estado_bomba = EstadoBomba.objects.create(
                bomba=bomba,
                estado=estado,
                origen=origen,
                observacion=observacion or None,
            )

            estado_bomba = EstadoBomba.objects.select_related("bomba").get(
                id_estado_bomba=estado_bomba.id_estado_bomba
            )
            return JsonResponse(estado_bomba_to_dict(estado_bomba), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def estado_bomba_detail_api(request, id_estado_bomba):
    try:
        estado_bomba = EstadoBomba.objects.select_related("bomba").get(id_estado_bomba=id_estado_bomba)
    except EstadoBomba.DoesNotExist:
        return JsonResponse({"error": "Estado de bomba no encontrado"}, status=404)

    if request.method == "GET":
        return JsonResponse(estado_bomba_to_dict(estado_bomba))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            id_bomba = body.get("id_bomba", estado_bomba.bomba.id_bomba)
            estado = body.get("estado", estado_bomba.estado)
            origen = body.get("origen", estado_bomba.origen)
            observacion = body.get("observacion", estado_bomba.observacion)

            if not id_bomba:
                return JsonResponse({"error": "La bomba es obligatoria"}, status=400)

            if not estado:
                return JsonResponse({"error": "El estado es obligatorio"}, status=400)

            try:
                bomba = BombaAgua.objects.get(id_bomba=id_bomba)
            except BombaAgua.DoesNotExist:
                return JsonResponse({"error": "Bomba no encontrada"}, status=404)

            estado_bomba.bomba = bomba
            estado_bomba.estado = estado
            estado_bomba.origen = origen
            estado_bomba.observacion = observacion
            estado_bomba.save()

            estado_bomba = EstadoBomba.objects.select_related("bomba").get(
                id_estado_bomba=estado_bomba.id_estado_bomba
            )
            return JsonResponse(estado_bomba_to_dict(estado_bomba))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        estado_bomba.delete()
        return JsonResponse({"message": "Estado de bomba eliminado correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# HELPERS BLOQUE FINAL
# =========================================================

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
# LECTURAS DE BATERIA
# =========================================================

@csrf_exempt
def lecturas_bateria_api(request):
    if request.method == "GET":
        lecturas = LecturaBateria.objects.select_related("bateria", "bateria__dispositivo").all().order_by("-id_lectura_bateria")
        data = [lectura_bateria_to_dict(lectura) for lectura in lecturas]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            id_bateria = body.get("id_bateria")
            porcentaje = body.get("porcentaje")
            voltaje = body.get("voltaje")

            if not id_bateria:
                return JsonResponse({"error": "La batería es obligatoria"}, status=400)

            if porcentaje in ("", None):
                return JsonResponse({"error": "El porcentaje es obligatorio"}, status=400)

            try:
                bateria = Bateria.objects.get(id_bateria=id_bateria)
            except Bateria.DoesNotExist:
                return JsonResponse({"error": "Batería no encontrada"}, status=404)

            lectura = LecturaBateria.objects.create(
                bateria=bateria,
                porcentaje=porcentaje,
                voltaje=voltaje if voltaje not in ("", None) else None,
            )

            lectura = LecturaBateria.objects.select_related("bateria", "bateria__dispositivo").get(
                id_lectura_bateria=lectura.id_lectura_bateria
            )
            return JsonResponse(lectura_bateria_to_dict(lectura), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def lectura_bateria_detail_api(request, id_lectura_bateria):
    try:
        lectura = LecturaBateria.objects.select_related("bateria", "bateria__dispositivo").get(
            id_lectura_bateria=id_lectura_bateria
        )
    except LecturaBateria.DoesNotExist:
        return JsonResponse({"error": "Lectura de batería no encontrada"}, status=404)

    if request.method == "GET":
        return JsonResponse(lectura_bateria_to_dict(lectura))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            id_bateria = body.get("id_bateria", lectura.bateria.id_bateria)
            porcentaje = body.get("porcentaje", lectura.porcentaje)
            voltaje = body.get("voltaje", lectura.voltaje)

            if not id_bateria:
                return JsonResponse({"error": "La batería es obligatoria"}, status=400)

            if porcentaje in ("", None):
                return JsonResponse({"error": "El porcentaje es obligatorio"}, status=400)

            try:
                bateria = Bateria.objects.get(id_bateria=id_bateria)
            except Bateria.DoesNotExist:
                return JsonResponse({"error": "Batería no encontrada"}, status=404)

            lectura.bateria = bateria
            lectura.porcentaje = porcentaje
            lectura.voltaje = voltaje if voltaje not in ("", None) else None
            lectura.save()

            lectura = LecturaBateria.objects.select_related("bateria", "bateria__dispositivo").get(
                id_lectura_bateria=lectura.id_lectura_bateria
            )
            return JsonResponse(lectura_bateria_to_dict(lectura))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        lectura.delete()
        return JsonResponse({"message": "Lectura de batería eliminada correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# ESTADOS DE RIEGO
# =========================================================

@csrf_exempt
def estados_riego_api(request):
    if request.method == "GET":
        estados = EstadoRiego.objects.select_related("zona", "bomba").all().order_by("-id_estado_riego")
        data = [estado_riego_to_dict(estado) for estado in estados]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            id_zona = body.get("id_zona")
            id_bomba = body.get("id_bomba")
            estado_riego = body.get("estado_riego")
            motivo = body.get("motivo", "").strip()
            duracion_segundos = body.get("duracion_segundos")
            fecha_fin = body.get("fecha_fin")

            if not id_zona:
                return JsonResponse({"error": "La zona es obligatoria"}, status=400)

            if not estado_riego:
                return JsonResponse({"error": "El estado de riego es obligatorio"}, status=400)

            try:
                zona = ZonaSiembra.objects.get(id_zona=id_zona)
            except ZonaSiembra.DoesNotExist:
                return JsonResponse({"error": "Zona no encontrada"}, status=404)

            bomba = None
            if id_bomba:
                try:
                    bomba = BombaAgua.objects.get(id_bomba=id_bomba)
                except BombaAgua.DoesNotExist:
                    return JsonResponse({"error": "Bomba no encontrada"}, status=404)

            estado = EstadoRiego.objects.create(
                zona=zona,
                bomba=bomba,
                estado_riego=estado_riego,
                motivo=motivo or None,
                duracion_segundos=duracion_segundos if duracion_segundos not in ("", None) else None,
                fecha_fin=fecha_fin if fecha_fin not in ("", None) else None,
            )

            estado = EstadoRiego.objects.select_related("zona", "bomba").get(id_estado_riego=estado.id_estado_riego)
            return JsonResponse(estado_riego_to_dict(estado), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def estado_riego_detail_api(request, id_estado_riego):
    try:
        estado = EstadoRiego.objects.select_related("zona", "bomba").get(id_estado_riego=id_estado_riego)
    except EstadoRiego.DoesNotExist:
        return JsonResponse({"error": "Estado de riego no encontrado"}, status=404)

    if request.method == "GET":
        return JsonResponse(estado_riego_to_dict(estado))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            id_zona = body.get("id_zona", estado.zona.id_zona)
            id_bomba = body.get("id_bomba", estado.bomba.id_bomba if estado.bomba else None)
            estado_riego = body.get("estado_riego", estado.estado_riego)
            motivo = body.get("motivo", estado.motivo)
            duracion_segundos = body.get("duracion_segundos", estado.duracion_segundos)
            fecha_fin = body.get("fecha_fin", estado.fecha_fin)

            if not id_zona:
                return JsonResponse({"error": "La zona es obligatoria"}, status=400)

            if not estado_riego:
                return JsonResponse({"error": "El estado de riego es obligatorio"}, status=400)

            try:
                zona = ZonaSiembra.objects.get(id_zona=id_zona)
            except ZonaSiembra.DoesNotExist:
                return JsonResponse({"error": "Zona no encontrada"}, status=404)

            bomba = None
            if id_bomba:
                try:
                    bomba = BombaAgua.objects.get(id_bomba=id_bomba)
                except BombaAgua.DoesNotExist:
                    return JsonResponse({"error": "Bomba no encontrada"}, status=404)

            estado.zona = zona
            estado.bomba = bomba
            estado.estado_riego = estado_riego
            estado.motivo = motivo
            estado.duracion_segundos = duracion_segundos if duracion_segundos not in ("", None) else None
            estado.fecha_fin = fecha_fin if fecha_fin not in ("", None) else None
            estado.save()

            estado = EstadoRiego.objects.select_related("zona", "bomba").get(id_estado_riego=estado.id_estado_riego)
            return JsonResponse(estado_riego_to_dict(estado))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        estado.delete()
        return JsonResponse({"message": "Estado de riego eliminado correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# ALERTAS
# =========================================================

@csrf_exempt
def alertas_api(request):
    if request.method == "GET":
        alertas = Alerta.objects.select_related("zona", "dispositivo").all().order_by("-id_alerta")
        data = [alerta_to_dict(alerta) for alerta in alertas]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            id_zona = body.get("id_zona")
            id_dispositivo = body.get("id_dispositivo")
            tipo_alerta = body.get("tipo_alerta")
            nivel = body.get("nivel", "WARNING")
            mensaje = body.get("mensaje", "").strip()
            atendida = body.get("atendida", False)

            if not id_zona:
                return JsonResponse({"error": "La zona es obligatoria"}, status=400)

            if not tipo_alerta:
                return JsonResponse({"error": "El tipo de alerta es obligatorio"}, status=400)

            if not mensaje:
                return JsonResponse({"error": "El mensaje es obligatorio"}, status=400)

            try:
                zona = ZonaSiembra.objects.get(id_zona=id_zona)
            except ZonaSiembra.DoesNotExist:
                return JsonResponse({"error": "Zona no encontrada"}, status=404)

            dispositivo = None
            if id_dispositivo:
                try:
                    dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
                except DispositivoIot.DoesNotExist:
                    return JsonResponse({"error": "Dispositivo no encontrado"}, status=404)

            alerta = Alerta.objects.create(
                zona=zona,
                dispositivo=dispositivo,
                tipo_alerta=tipo_alerta,
                nivel=nivel,
                mensaje=mensaje,
                atendida=atendida,
            )

            alerta = Alerta.objects.select_related("zona", "dispositivo").get(id_alerta=alerta.id_alerta)
            return JsonResponse(alerta_to_dict(alerta), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def alerta_detail_api(request, id_alerta):
    try:
        alerta = Alerta.objects.select_related("zona", "dispositivo").get(id_alerta=id_alerta)
    except Alerta.DoesNotExist:
        return JsonResponse({"error": "Alerta no encontrada"}, status=404)

    if request.method == "GET":
        return JsonResponse(alerta_to_dict(alerta))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            id_zona = body.get("id_zona", alerta.zona.id_zona)
            id_dispositivo = body.get("id_dispositivo", alerta.dispositivo.id_dispositivo if alerta.dispositivo else None)
            tipo_alerta = body.get("tipo_alerta", alerta.tipo_alerta)
            nivel = body.get("nivel", alerta.nivel)
            mensaje = body.get("mensaje", alerta.mensaje)
            atendida = body.get("atendida", alerta.atendida)

            mensaje = mensaje.strip() if isinstance(mensaje, str) else mensaje

            if not id_zona:
                return JsonResponse({"error": "La zona es obligatoria"}, status=400)

            if not tipo_alerta:
                return JsonResponse({"error": "El tipo de alerta es obligatorio"}, status=400)

            if not mensaje:
                return JsonResponse({"error": "El mensaje es obligatorio"}, status=400)

            try:
                zona = ZonaSiembra.objects.get(id_zona=id_zona)
            except ZonaSiembra.DoesNotExist:
                return JsonResponse({"error": "Zona no encontrada"}, status=404)

            dispositivo = None
            if id_dispositivo:
                try:
                    dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
                except DispositivoIot.DoesNotExist:
                    return JsonResponse({"error": "Dispositivo no encontrado"}, status=404)

            alerta.zona = zona
            alerta.dispositivo = dispositivo
            alerta.tipo_alerta = tipo_alerta
            alerta.nivel = nivel
            alerta.mensaje = mensaje
            alerta.atendida = atendida
            alerta.save()

            alerta = Alerta.objects.select_related("zona", "dispositivo").get(id_alerta=alerta.id_alerta)
            return JsonResponse(alerta_to_dict(alerta))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        alerta.delete()
        return JsonResponse({"message": "Alerta eliminada correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# USUARIOS
# =========================================================

@csrf_exempt
def usuarios_api(request):
    if request.method == "GET":
        usuarios = Usuario.objects.all().order_by("id_usuario")
        data = [usuario_to_dict(usuario) for usuario in usuarios]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            username = body.get("username", "").strip()
            correo = body.get("correo", "").strip()
            password_hash = body.get("password_hash", "").strip()
            activo = body.get("activo", True)

            if not username:
                return JsonResponse({"error": "El username es obligatorio"}, status=400)

            if not password_hash:
                return JsonResponse({"error": "El password_hash es obligatorio"}, status=400)

            if Usuario.objects.filter(username=username).exists():
                return JsonResponse({"error": "Ya existe un usuario con ese username"}, status=400)

            if correo and Usuario.objects.filter(correo=correo).exists():
                return JsonResponse({"error": "Ya existe un usuario con ese correo"}, status=400)

            usuario = Usuario.objects.create(
                username=username,
                correo=correo or None,
                password_hash=password_hash,
                activo=activo,
            )

            return JsonResponse(usuario_to_dict(usuario), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def usuario_detail_api(request, id_usuario):
    try:
        usuario = Usuario.objects.get(id_usuario=id_usuario)
    except Usuario.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)

    if request.method == "GET":
        return JsonResponse(usuario_to_dict(usuario))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            username = body.get("username", usuario.username)
            correo = body.get("correo", usuario.correo)
            password_hash = body.get("password_hash", usuario.password_hash)
            activo = body.get("activo", usuario.activo)

            username = username.strip() if isinstance(username, str) else username
            correo = correo.strip() if isinstance(correo, str) else correo
            password_hash = password_hash.strip() if isinstance(password_hash, str) else password_hash

            if not username:
                return JsonResponse({"error": "El username es obligatorio"}, status=400)

            if not password_hash:
                return JsonResponse({"error": "El password_hash es obligatorio"}, status=400)

            existe_username = Usuario.objects.filter(username=username).exclude(id_usuario=usuario.id_usuario).exists()
            if existe_username:
                return JsonResponse({"error": "Ya existe otro usuario con ese username"}, status=400)

            if correo:
                existe_correo = Usuario.objects.filter(correo=correo).exclude(id_usuario=usuario.id_usuario).exists()
                if existe_correo:
                    return JsonResponse({"error": "Ya existe otro usuario con ese correo"}, status=400)

            usuario.username = username
            usuario.correo = correo or None
            usuario.password_hash = password_hash
            usuario.activo = activo
            usuario.save()

            return JsonResponse(usuario_to_dict(usuario))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        usuario.delete()
        return JsonResponse({"message": "Usuario eliminado correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# ROLES
# =========================================================

@csrf_exempt
def roles_api(request):
    if request.method == "GET":
        roles = Rol.objects.all().order_by("id_rol")
        data = [rol_to_dict(rol) for rol in roles]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            nombre = body.get("nombre", "").strip()
            descripcion = body.get("descripcion", "").strip()

            if not nombre:
                return JsonResponse({"error": "El nombre del rol es obligatorio"}, status=400)

            if Rol.objects.filter(nombre=nombre).exists():
                return JsonResponse({"error": "Ya existe un rol con ese nombre"}, status=400)

            rol = Rol.objects.create(
                nombre=nombre,
                descripcion=descripcion or None,
            )

            return JsonResponse(rol_to_dict(rol), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def rol_detail_api(request, id_rol):
    try:
        rol = Rol.objects.get(id_rol=id_rol)
    except Rol.DoesNotExist:
        return JsonResponse({"error": "Rol no encontrado"}, status=404)

    if request.method == "GET":
        return JsonResponse(rol_to_dict(rol))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            nombre = body.get("nombre", rol.nombre)
            descripcion = body.get("descripcion", rol.descripcion)

            nombre = nombre.strip() if isinstance(nombre, str) else nombre
            descripcion = descripcion.strip() if isinstance(descripcion, str) else descripcion

            if not nombre:
                return JsonResponse({"error": "El nombre del rol es obligatorio"}, status=400)

            existe = Rol.objects.filter(nombre=nombre).exclude(id_rol=rol.id_rol).exists()
            if existe:
                return JsonResponse({"error": "Ya existe otro rol con ese nombre"}, status=400)

            rol.nombre = nombre
            rol.descripcion = descripcion or None
            rol.save()

            return JsonResponse(rol_to_dict(rol))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        rol.delete()
        return JsonResponse({"message": "Rol eliminado correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# USUARIO ROL
# =========================================================

@csrf_exempt
def usuarios_roles_api(request):
    if request.method == "GET":
        usuarios_roles = UsuarioRol.objects.select_related("usuario", "rol").all().order_by("id_usuario_rol")
        data = [usuario_rol_to_dict(item) for item in usuarios_roles]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            id_usuario = body.get("id_usuario")
            id_rol = body.get("id_rol")

            if not id_usuario:
                return JsonResponse({"error": "El usuario es obligatorio"}, status=400)

            if not id_rol:
                return JsonResponse({"error": "El rol es obligatorio"}, status=400)

            try:
                usuario = Usuario.objects.get(id_usuario=id_usuario)
            except Usuario.DoesNotExist:
                return JsonResponse({"error": "Usuario no encontrado"}, status=404)

            try:
                rol = Rol.objects.get(id_rol=id_rol)
            except Rol.DoesNotExist:
                return JsonResponse({"error": "Rol no encontrado"}, status=404)

            existe = UsuarioRol.objects.filter(usuario=usuario, rol=rol).exists()
            if existe:
                return JsonResponse({"error": "Ese usuario ya tiene ese rol"}, status=400)

            usuario_rol = UsuarioRol.objects.create(
                usuario=usuario,
                rol=rol,
            )

            usuario_rol = UsuarioRol.objects.select_related("usuario", "rol").get(
                id_usuario_rol=usuario_rol.id_usuario_rol
            )
            return JsonResponse(usuario_rol_to_dict(usuario_rol), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def usuario_rol_detail_api(request, id_usuario_rol):
    try:
        usuario_rol = UsuarioRol.objects.select_related("usuario", "rol").get(id_usuario_rol=id_usuario_rol)
    except UsuarioRol.DoesNotExist:
        return JsonResponse({"error": "Relación usuario-rol no encontrada"}, status=404)

    if request.method == "GET":
        return JsonResponse(usuario_rol_to_dict(usuario_rol))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            id_usuario = body.get("id_usuario", usuario_rol.usuario.id_usuario)
            id_rol = body.get("id_rol", usuario_rol.rol.id_rol)

            if not id_usuario:
                return JsonResponse({"error": "El usuario es obligatorio"}, status=400)

            if not id_rol:
                return JsonResponse({"error": "El rol es obligatorio"}, status=400)

            try:
                usuario = Usuario.objects.get(id_usuario=id_usuario)
            except Usuario.DoesNotExist:
                return JsonResponse({"error": "Usuario no encontrado"}, status=404)

            try:
                rol = Rol.objects.get(id_rol=id_rol)
            except Rol.DoesNotExist:
                return JsonResponse({"error": "Rol no encontrado"}, status=404)

            existe = UsuarioRol.objects.filter(
                usuario=usuario,
                rol=rol
            ).exclude(id_usuario_rol=usuario_rol.id_usuario_rol).exists()

            if existe:
                return JsonResponse({"error": "Ya existe esa relación usuario-rol"}, status=400)

            usuario_rol.usuario = usuario
            usuario_rol.rol = rol
            usuario_rol.save()

            usuario_rol = UsuarioRol.objects.select_related("usuario", "rol").get(
                id_usuario_rol=usuario_rol.id_usuario_rol
            )
            return JsonResponse(usuario_rol_to_dict(usuario_rol))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        usuario_rol.delete()
        return JsonResponse({"message": "Relación usuario-rol eliminada correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# COMANDOS REMOTOS
# =========================================================

@csrf_exempt
def comandos_remotos_api(request):
    if request.method == "GET":
        comandos = ComandoRemoto.objects.select_related("dispositivo", "bomba", "usuario").all().order_by("-id_comando")
        data = [comando_remoto_to_dict(comando) for comando in comandos]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            id_dispositivo = body.get("id_dispositivo")
            id_bomba = body.get("id_bomba")
            id_usuario = body.get("id_usuario")
            accion = body.get("accion")
            estado = body.get("estado", "PENDIENTE")
            parametros_texto = body.get("parametros_texto", "").strip()

            if not id_dispositivo:
                return JsonResponse({"error": "El dispositivo es obligatorio"}, status=400)

            if not accion:
                return JsonResponse({"error": "La acción es obligatoria"}, status=400)

            try:
                dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
            except DispositivoIot.DoesNotExist:
                return JsonResponse({"error": "Dispositivo no encontrado"}, status=404)

            bomba = None
            if id_bomba:
                try:
                    bomba = BombaAgua.objects.get(id_bomba=id_bomba)
                except BombaAgua.DoesNotExist:
                    return JsonResponse({"error": "Bomba no encontrada"}, status=404)

            usuario = None
            if id_usuario:
                try:
                    usuario = Usuario.objects.get(id_usuario=id_usuario)
                except Usuario.DoesNotExist:
                    return JsonResponse({"error": "Usuario no encontrado"}, status=404)

            comando = ComandoRemoto.objects.create(
                dispositivo=dispositivo,
                bomba=bomba,
                usuario=usuario,
                accion=accion,
                estado=estado,
                parametros_texto=parametros_texto or None,
            )

            comando = ComandoRemoto.objects.select_related("dispositivo", "bomba", "usuario").get(
                id_comando=comando.id_comando
            )
            return JsonResponse(comando_remoto_to_dict(comando), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def comando_remoto_detail_api(request, id_comando):
    try:
        comando = ComandoRemoto.objects.select_related("dispositivo", "bomba", "usuario").get(id_comando=id_comando)
    except ComandoRemoto.DoesNotExist:
        return JsonResponse({"error": "Comando remoto no encontrado"}, status=404)

    if request.method == "GET":
        return JsonResponse(comando_remoto_to_dict(comando))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            id_dispositivo = body.get("id_dispositivo", comando.dispositivo.id_dispositivo)
            id_bomba = body.get("id_bomba", comando.bomba.id_bomba if comando.bomba else None)
            id_usuario = body.get("id_usuario", comando.usuario.id_usuario if comando.usuario else None)
            accion = body.get("accion", comando.accion)
            estado = body.get("estado", comando.estado)
            parametros_texto = body.get("parametros_texto", comando.parametros_texto)

            if not id_dispositivo:
                return JsonResponse({"error": "El dispositivo es obligatorio"}, status=400)

            if not accion:
                return JsonResponse({"error": "La acción es obligatoria"}, status=400)

            try:
                dispositivo = DispositivoIot.objects.get(id_dispositivo=id_dispositivo)
            except DispositivoIot.DoesNotExist:
                return JsonResponse({"error": "Dispositivo no encontrado"}, status=404)

            bomba = None
            if id_bomba:
                try:
                    bomba = BombaAgua.objects.get(id_bomba=id_bomba)
                except BombaAgua.DoesNotExist:
                    return JsonResponse({"error": "Bomba no encontrada"}, status=404)

            usuario = None
            if id_usuario:
                try:
                    usuario = Usuario.objects.get(id_usuario=id_usuario)
                except Usuario.DoesNotExist:
                    return JsonResponse({"error": "Usuario no encontrado"}, status=404)

            comando.dispositivo = dispositivo
            comando.bomba = bomba
            comando.usuario = usuario
            comando.accion = accion
            comando.estado = estado
            comando.parametros_texto = parametros_texto
            comando.save()

            comando = ComandoRemoto.objects.select_related("dispositivo", "bomba", "usuario").get(
                id_comando=comando.id_comando
            )
            return JsonResponse(comando_remoto_to_dict(comando))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        comando.delete()
        return JsonResponse({"message": "Comando remoto eliminado correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# RESPUESTAS DE COMANDO
# =========================================================

@csrf_exempt
def respuestas_comando_api(request):
    if request.method == "GET":
        respuestas = RespuestaComando.objects.select_related("comando").all().order_by("-id_respuesta")
        data = [respuesta_comando_to_dict(respuesta) for respuesta in respuestas]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            id_comando = body.get("id_comando")
            codigo_respuesta = body.get("codigo_respuesta", "").strip()
            mensaje = body.get("mensaje", "").strip()
            exitoso = body.get("exitoso", True)

            if not id_comando:
                return JsonResponse({"error": "El comando es obligatorio"}, status=400)

            try:
                comando = ComandoRemoto.objects.get(id_comando=id_comando)
            except ComandoRemoto.DoesNotExist:
                return JsonResponse({"error": "Comando no encontrado"}, status=404)

            respuesta = RespuestaComando.objects.create(
                comando=comando,
                codigo_respuesta=codigo_respuesta or None,
                mensaje=mensaje or None,
                exitoso=exitoso,
            )

            respuesta = RespuestaComando.objects.select_related("comando").get(id_respuesta=respuesta.id_respuesta)
            return JsonResponse(respuesta_comando_to_dict(respuesta), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def respuesta_comando_detail_api(request, id_respuesta):
    try:
        respuesta = RespuestaComando.objects.select_related("comando").get(id_respuesta=id_respuesta)
    except RespuestaComando.DoesNotExist:
        return JsonResponse({"error": "Respuesta de comando no encontrada"}, status=404)

    if request.method == "GET":
        return JsonResponse(respuesta_comando_to_dict(respuesta))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            id_comando = body.get("id_comando", respuesta.comando.id_comando)
            codigo_respuesta = body.get("codigo_respuesta", respuesta.codigo_respuesta)
            mensaje = body.get("mensaje", respuesta.mensaje)
            exitoso = body.get("exitoso", respuesta.exitoso)

            codigo_respuesta = codigo_respuesta.strip() if isinstance(codigo_respuesta, str) else codigo_respuesta
            mensaje = mensaje.strip() if isinstance(mensaje, str) else mensaje

            if not id_comando:
                return JsonResponse({"error": "El comando es obligatorio"}, status=400)

            try:
                comando = ComandoRemoto.objects.get(id_comando=id_comando)
            except ComandoRemoto.DoesNotExist:
                return JsonResponse({"error": "Comando no encontrado"}, status=404)

            respuesta.comando = comando
            respuesta.codigo_respuesta = codigo_respuesta or None
            respuesta.mensaje = mensaje or None
            respuesta.exitoso = exitoso
            respuesta.save()

            respuesta = RespuestaComando.objects.select_related("comando").get(id_respuesta=respuesta.id_respuesta)
            return JsonResponse(respuesta_comando_to_dict(respuesta))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        respuesta.delete()
        return JsonResponse({"message": "Respuesta de comando eliminada correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)


# =========================================================
# AUDITORIA SISTEMA
# =========================================================

@csrf_exempt
def auditorias_api(request):
    if request.method == "GET":
        auditorias = AuditoriaSistema.objects.select_related("usuario").all().order_by("-id_auditoria")
        data = [auditoria_to_dict(auditoria) for auditoria in auditorias]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)

            id_usuario = body.get("id_usuario")
            accion = body.get("accion", "").strip()
            tabla_afectada = body.get("tabla_afectada", "").strip()
            id_registro_afectado = body.get("id_registro_afectado")
            detalle = body.get("detalle", "").strip()
            ip_origen = body.get("ip_origen", "").strip()

            if not accion:
                return JsonResponse({"error": "La acción es obligatoria"}, status=400)

            usuario = None
            if id_usuario:
                try:
                    usuario = Usuario.objects.get(id_usuario=id_usuario)
                except Usuario.DoesNotExist:
                    return JsonResponse({"error": "Usuario no encontrado"}, status=404)

            auditoria = AuditoriaSistema.objects.create(
                usuario=usuario,
                accion=accion,
                tabla_afectada=tabla_afectada or None,
                id_registro_afectado=id_registro_afectado if id_registro_afectado not in ("", None) else None,
                detalle=detalle or None,
                ip_origen=ip_origen or None,
            )

            auditoria = AuditoriaSistema.objects.select_related("usuario").get(id_auditoria=auditoria.id_auditoria)
            return JsonResponse(auditoria_to_dict(auditoria), status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def auditoria_detail_api(request, id_auditoria):
    try:
        auditoria = AuditoriaSistema.objects.select_related("usuario").get(id_auditoria=id_auditoria)
    except AuditoriaSistema.DoesNotExist:
        return JsonResponse({"error": "Auditoría no encontrada"}, status=404)

    if request.method == "GET":
        return JsonResponse(auditoria_to_dict(auditoria))

    if request.method == "PUT":
        try:
            body = json.loads(request.body)

            id_usuario = body.get("id_usuario", auditoria.usuario.id_usuario if auditoria.usuario else None)
            accion = body.get("accion", auditoria.accion)
            tabla_afectada = body.get("tabla_afectada", auditoria.tabla_afectada)
            id_registro_afectado = body.get("id_registro_afectado", auditoria.id_registro_afectado)
            detalle = body.get("detalle", auditoria.detalle)
            ip_origen = body.get("ip_origen", auditoria.ip_origen)

            accion = accion.strip() if isinstance(accion, str) else accion
            tabla_afectada = tabla_afectada.strip() if isinstance(tabla_afectada, str) else tabla_afectada
            detalle = detalle.strip() if isinstance(detalle, str) else detalle
            ip_origen = ip_origen.strip() if isinstance(ip_origen, str) else ip_origen

            if not accion:
                return JsonResponse({"error": "La acción es obligatoria"}, status=400)

            usuario = None
            if id_usuario:
                try:
                    usuario = Usuario.objects.get(id_usuario=id_usuario)
                except Usuario.DoesNotExist:
                    return JsonResponse({"error": "Usuario no encontrado"}, status=404)

            auditoria.usuario = usuario
            auditoria.accion = accion
            auditoria.tabla_afectada = tabla_afectada or None
            auditoria.id_registro_afectado = id_registro_afectado if id_registro_afectado not in ("", None) else None
            auditoria.detalle = detalle or None
            auditoria.ip_origen = ip_origen or None
            auditoria.save()

            auditoria = AuditoriaSistema.objects.select_related("usuario").get(id_auditoria=auditoria.id_auditoria)
            return JsonResponse(auditoria_to_dict(auditoria))

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if request.method == "DELETE":
        auditoria.delete()
        return JsonResponse({"message": "Auditoría eliminada correctamente"})

    return JsonResponse({"error": "Método no permitido"}, status=405)