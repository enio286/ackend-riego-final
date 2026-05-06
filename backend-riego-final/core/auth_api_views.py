from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_ping_api(request):
    return Response({"message": "JWT configurado"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_me_api(request):
    role_names = list(request.user.groups.values_list("name", flat=True))

    primary_role = None
    if request.user.is_superuser:
        primary_role = "SUPERADMIN"
    elif "ADMIN" in role_names or request.user.is_staff:
        primary_role = "ADMIN"
    elif "OPERADOR" in role_names:
        primary_role = "OPERADOR"
    elif "VISOR" in role_names:
        primary_role = "VISOR"
    elif role_names:
        primary_role = role_names[0]

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