from django.contrib.auth.models import User, Group

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.response import Response


FIXED_ROLES = {
    "ADMIN": "Acceso total al sistema y administración completa.",
    "OPERADOR": "Acceso operativo a módulos del sistema.",
    "VISOR": "Acceso de solo lectura al dashboard.",
}


class IsAccessAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser or user.is_staff:
            return True

        return user.groups.filter(name__iexact="ADMIN").exists()


def ensure_fixed_roles():
    for role_name in FIXED_ROLES.keys():
        Group.objects.get_or_create(name=role_name)


def normalize_roles(user):
    raw_roles = list(user.groups.values_list("name", flat=True))
    return [role.upper() for role in raw_roles]


def get_primary_role(user):
    roles = normalize_roles(user)

    if user.is_superuser or user.is_staff:
        return "ADMIN"

    for role in FIXED_ROLES.keys():
        if role in roles:
            return role

    return None


def group_to_dict(group):
    return {
        "id": group.id,
        "name": group.name.upper(),
        "description": FIXED_ROLES.get(group.name.upper(), ""),
    }


def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "roles": normalize_roles(user),
        "primary_role": get_primary_role(user),
    }


def get_group_from_role_name(role_name):
    ensure_fixed_roles()

    role_name = str(role_name).strip().upper()
    if role_name not in FIXED_ROLES:
        return None, f"Rol inválido. Usa uno de estos: {', '.join(FIXED_ROLES.keys())}"

    try:
        group = Group.objects.get(name=role_name)
    except Group.DoesNotExist:
        return None, f"No existe el rol {role_name}"

    return group, None


@api_view(['GET'])
@permission_classes([IsAccessAdmin])
def access_roles_api(request):
    ensure_fixed_roles()
    roles = Group.objects.filter(name__in=FIXED_ROLES.keys()).order_by("name")
    data = [group_to_dict(role) for role in roles]
    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAccessAdmin])
def access_users_api(request):
    ensure_fixed_roles()

    if request.method == 'GET':
        users = User.objects.all().order_by("id")
        data = [user_to_dict(user) for user in users]
        return Response(data, status=status.HTTP_200_OK)

    username = str(request.data.get("username", "")).strip()
    email = str(request.data.get("email", "")).strip()
    first_name = str(request.data.get("first_name", "")).strip()
    last_name = str(request.data.get("last_name", "")).strip()
    password = str(request.data.get("password", "")).strip()
    is_active = request.data.get("is_active", True)
    role_name = str(request.data.get("role_name", "")).strip().upper()

    if not username:
        return Response(
            {"error": "El username es obligatorio"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not password:
        return Response(
            {"error": "La contraseña es obligatoria"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not role_name:
        return Response(
            {"error": "El rol es obligatorio"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Ya existe un usuario con ese username"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if email and User.objects.filter(email=email).exists():
        return Response(
            {"error": "Ya existe un usuario con ese email"},
            status=status.HTTP_400_BAD_REQUEST
        )

    group, error = get_group_from_role_name(role_name)
    if error:
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    is_staff = role_name == "ADMIN"

    user = User.objects.create_user(
        username=username,
        email=email or "",
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=bool(is_active),
        is_staff=is_staff,
    )

    user.groups.set([group])

    return Response(user_to_dict(user), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAccessAdmin])
def access_user_detail_api(request, user_id):
    ensure_fixed_roles()

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "Usuario no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        return Response(user_to_dict(user), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        username = str(request.data.get("username", user.username)).strip()
        email = str(request.data.get("email", user.email)).strip()
        first_name = str(request.data.get("first_name", user.first_name)).strip()
        last_name = str(request.data.get("last_name", user.last_name)).strip()
        password = str(request.data.get("password", "")).strip()
        is_active = request.data.get("is_active", user.is_active)
        role_name = str(
            request.data.get("role_name", get_primary_role(user) or "")
        ).strip().upper()

        if not username:
            return Response(
                {"error": "El username es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not role_name:
            return Response(
                {"error": "El rol es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST
            )

        exists_username = User.objects.filter(username=username).exclude(id=user.id).exists()
        if exists_username:
            return Response(
                {"error": "Ya existe otro usuario con ese username"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if email:
            exists_email = User.objects.filter(email=email).exclude(id=user.id).exists()
            if exists_email:
                return Response(
                    {"error": "Ya existe otro usuario con ese email"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        group, error = get_group_from_role_name(role_name)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        user.username = username
        user.email = email or ""
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = bool(is_active)
        user.is_staff = role_name == "ADMIN"

        if password:
            user.set_password(password)

        user.save()
        user.groups.set([group])

        return Response(user_to_dict(user), status=status.HTTP_200_OK)

    user.delete()
    return Response(
        {"message": "Usuario eliminado correctamente"},
        status=status.HTTP_200_OK
    )