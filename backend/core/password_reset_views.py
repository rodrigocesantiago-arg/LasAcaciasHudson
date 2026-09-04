from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import EmailMessage, get_connection
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import Lote


def recuperar_password(request):
    if request.method == "POST":
        numero_lote = request.POST.get("numero_lote", "").strip()

        try:
            lote = Lote.objects.select_related("usuario").get(
                numero=numero_lote,
                activo=True
            )
        except (Lote.DoesNotExist, ValueError):
            lote = None

        if lote and lote.usuario and lote.email:
            usuario = lote.usuario

            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)

            reset_url = request.build_absolute_uri(
                reverse(
                    "restablecer_password",
                    kwargs={
                        "uidb64": uid,
                        "token": token,
                    },
                )
            )

            asunto = "Recuperación de contraseña - Las Acacias"
            cuerpo = (
                f"Hola,\n\n"
                f"Recibimos una solicitud para restablecer la contraseña "
                f"del Lote {lote.numero}.\n\n"
                f"Usá el siguiente enlace para crear una nueva contraseña:\n"
                f"{reset_url}\n\n"
                f"Si no solicitaste este cambio, podés ignorar este mensaje.\n\n"
                f"Las Acacias Hudson · Comunidad360"
            )

            # Durante desarrollo se usa el backend de consola.
            # El email completo aparecerá en la terminal donde corre runserver.
            connection = get_connection(
                backend="django.core.mail.backends.console.EmailBackend"
            )

            EmailMessage(
                subject=asunto,
                body=cuerpo,
                from_email="Comunidad360 <no-reply@lasacaciashudson.local>",
                to=[lote.email],
                connection=connection,
            ).send(fail_silently=True)

        # Siempre mostramos el mismo resultado para no revelar si un lote existe.
        return redirect("recuperar_password_enviado")

    return render(request, "core/recuperar_password.html")


def recuperar_password_enviado(request):
    return render(request, "core/recuperar_password_enviado.html")


def restablecer_password(request, uidb64, token):
    usuario = None

    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        usuario = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        usuario = None

    token_valido = (
        usuario is not None
        and default_token_generator.check_token(usuario, token)
    )

    if not token_valido:
        return render(
            request,
            "core/restablecer_password.html",
            {"valido": False},
        )

    if request.method == "POST":
        form = SetPasswordForm(usuario, request.POST)

        if form.is_valid():
            form.save()
            return redirect("password_restaurada")
    else:
        form = SetPasswordForm(usuario)

    for campo in form.fields.values():
        campo.widget.attrs.update({"class": "form-control"})

    return render(
        request,
        "core/restablecer_password.html",
        {
            "valido": True,
            "form": form,
        },
    )


def password_restaurada(request):
    return render(request, "core/password_restaurada.html")