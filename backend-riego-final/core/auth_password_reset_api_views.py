from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


token_generator = PasswordResetTokenGenerator()


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password_api(request):
    email = str(request.data.get("email", "")).strip().lower()

    # Respuesta neutra por seguridad
    success_message = {
        "message": "Si el correo existe, se enviará un enlace de recuperación."
    }

    if not email:
        return Response(success_message, status=200)

    try:
        user = User.objects.get(email__iexact=email, is_active=True)
    except User.DoesNotExist:
        return Response(success_message, status=200)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)

    reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password/{uid}/{token}"
    print("RESET LINK LIMPIO:", reset_link)

    subject = "Recuperación de contraseña"
    message = (
        f"Hola {user.username},\n\n"
        f"Recibimos una solicitud para restablecer tu contraseña.\n"
        f"Usa este enlace para crear una nueva:\n\n"
        f"{reset_link}\n\n"
        f"Si no solicitaste este cambio, puedes ignorar este correo."
    )

    stry:
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
except Exception as e:
    print("ERROR SMTP:", repr(e))
    return Response(
        {"error": "No se pudo enviar el correo de recuperación"},
        status=500
    )

    return Response(success_message, status=200)


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_api(request):
    uid = request.data.get("uid")
    token = request.data.get("token")
    password = str(request.data.get("password", "")).strip()
    confirm_password = str(request.data.get("confirm_password", "")).strip()

    if not uid or not token:
        return Response({"error": "Enlace inválido"}, status=400)

    if not password or not confirm_password:
        return Response({"error": "Debes completar ambos campos"}, status=400)

    if password != confirm_password:
        return Response({"error": "Las contraseñas no coinciden"}, status=400)

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id, is_active=True)
    except Exception:
        return Response({"error": "Enlace inválido o expirado"}, status=400)

    if not token_generator.check_token(user, token):
        return Response({"error": "El enlace ya no es válido o expiró"}, status=400)

    user.set_password(password)
    user.save()

    return Response({"message": "Contraseña actualizada correctamente"}, status=200)