from django.contrib.auth.models import User, Group

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.response import Response


class IsAccessAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser or user.is_staff:
            return True

        return user.groups.filter(name="ADMIN").exists()


def group_to_dict(group):
    return {
        "id": group.id,
        "name": group.name,
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
        "roles": list(user.groups.values_list("name", flat=True)),
    }


def get_groups_from_names(role_names):
    if not isinstance(role_names, list):
        return None, "role_names debe ser una lista"

    clean_names = [str(name).strip().upper() for name in role_names if str(name).strip()]
    groups = list(Group.objects.filter(name__in=clean_names))

    found_names = {group.name for group in groups}
    missing = [name for name in clean_names if name not in found_names]

    if missing:
        return None, f"No existen estos roles: {', '.join(missing)}"

    return groups, None


@api_view(['GET', 'POST'])
@permission_classes([IsAccessAdmin])
def access_roles_api(request):
    if request.method == 'GET':
        roles = Group.objects.all().order_by("name")
        data = [group_to_dict(role) for role in roles]
        return Response(data, status=status.HTTP_200_OK)

    name = str(request.data.get("name", "")).strip().upper()

    if not name:
        return Response(
            {"error": "El nombre del rol es obligatorio"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if Group.objects.filter(name=name).exists():
        return Response(
            {"error": "Ya existe un rol con ese nombre"},
            status=status.HTTP_400_BAD_REQUEST
        )

    role = Group.objects.create(name=name)
    return Response(group_to_dict(role), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAccessAdmin])
def access_role_detail_api(request, role_id):
    try:
        role = Group.objects.get(id=role_id)
    except Group.DoesNotExist:
        return Response(
            {"error": "Rol no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        return Response(group_to_dict(role), status=status.HTTP_200_OK)

    if request.method == 'PUT':
        name = str(request.data.get("name", role.name)).strip().upper()

        if not name:
            return Response(
                {"error": "El nombre del rol es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST
            )

        exists = Group.objects.filter(name=name).exclude(id=role.id).exists()
        if exists:
            return Response(
                {"error": "Ya existe otro rol con ese nombre"},
                status=status.HTTP_400_BAD_REQUEST
            )

        role.name = name
        role.save()
        return Response(group_to_dict(role), status=status.HTTP_200_OK)

    role.delete()
    return Response(
        {"message": "Rol eliminado correctamente"},
        status=status.HTTP_200_OK
    )


@api_view(['GET', 'POST'])
@permission_classes([IsAccessAdmin])
def access_users_api(request):
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
    role_names = request.data.get("role_names", [])

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

    groups, error = get_groups_from_names(role_names)
    if error:
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    role_names_upper = [group.name for group in groups]
    is_staff = "ADMIN" in role_names_upper

    user = User.objects.create_user(
        username=username,
        email=email or "",
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=bool(is_active),
        is_staff=is_staff,
    )

    user.groups.set(groups)
    return Response(user_to_dict(user), status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAccessAdmin])
def access_user_detail_api(request, user_id):
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
        role_names = request.data.get("role_names", list(user.groups.values_list("name", flat=True)))

        if not username:
            return Response(
                {"error": "El username es obligatorio"},
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

        groups, error = get_groups_from_names(role_names)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        role_names_upper = [group.name for group in groups]
        is_staff = "ADMIN" in role_names_upper

        user.username = username
        user.email = email or ""
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = bool(is_active)
        user.is_staff = is_staff

        if password:
            user.set_password(password)

        user.save()
        user.groups.set(groups)

        return Response(user_to_dict(user), status=status.HTTP_200_OK)

    user.delete()
    return Response(
        {"message": "Usuario eliminado correctamente"},
        status=status.HTTP_200_OK
    )