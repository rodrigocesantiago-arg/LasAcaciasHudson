
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from .models import Lote


def activar_cuenta(request, uidb64, token):
    usuario = None

    try:
        usuario_id = force_str(urlsafe_base64_decode(uidb64))
        usuario = User.objects.get(pk=usuario_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass

    cuenta_valida = (
        usuario is not None
        and not usuario.is_active
        and usuario.has_usable_password() is False
        and Lote.objects.filter(
            usuario=usuario,
            activo=True
        ).exists()
        and default_token_generator.check_token(usuario, token)
    )

    if not cuenta_valida:
        return render(
            request,
            "core/activar_cuenta.html",
            {"valido": False}
        )

    if request.method == "POST":
        formulario = SetPasswordForm(usuario, request.POST)

        if formulario.is_valid():
            usuario = formulario.save(commit=False)
            usuario.is_active = True
            usuario.save()
            return redirect("login")
    else:
        formulario = SetPasswordForm(usuario)

    for campo in formulario.fields.values():
        campo.widget.attrs.update({
            "class": "form-control"
        })

    return render(
        request,
        "core/activar_cuenta.html",
        {
            "valido": True,
            "formulario": formulario,
        }
    )
