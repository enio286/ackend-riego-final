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
    return Response({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email,
        "is_superuser": request.user.is_superuser,
        "is_staff": request.user.is_staff,
    })