from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


FIXED_ROLES = ["ADMIN", "OPERADOR", "VISOR"]


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_ping_api(request):
    return Response({"message": "JWT configurado"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_me_api(request):
    raw_roles = list(request.user.groups.values_list("name", flat=True))
    role_names = [role.upper() for role in raw_roles]

    primary_role = None
    if request.user.is_superuser or request.user.is_staff:
        primary_role = "ADMIN"
    else:
        for role in FIXED_ROLES:
            if role in role_names:
                primary_role = role
                break

    return Response({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "is_superuser": request.user.is_superuser,
        "is_staff": request.user.is_staff,
        "is_active": request.user.is_active,
        "roles": role_names,
        "primary_role": primary_role,
    })