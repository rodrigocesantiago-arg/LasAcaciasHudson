from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .forms import InvitacionVecinoForm

from .administracion_views import superuser_required
from .models import Lote, Integrante, SolicitudModificacionFamilia


@superuser_required
def administracion_lotes(request):
    estado = request.GET.get("estado", "").strip()
    q = request.GET.get("q", "").strip()

    lotes = (
        Lote.objects.select_related("usuario")
        .annotate(
            integrantes_activos=Count(
                "integrantes",
                filter=Q(integrantes__activo=True),
                distinct=True,
            )
        )
        .all()
    )

    if estado == "activos":
        lotes = lotes.filter(activo=True)
    elif estado == "inactivos":
        lotes = lotes.filter(activo=False)
    else:
        estado = ""

    if q:
        filtro = (
            Q(apellido_familia__icontains=q)
            | Q(email__icontains=q)
            | Q(telefono__icontains=q)
        )
        if q.isdigit():
            filtro |= Q(numero=int(q))
        lotes = lotes.filter(filtro)

    lotes = lotes.order_by("numero")

    total = lotes.count()
    activos = lotes.filter(activo=True).count()
    inactivos = lotes.filter(activo=False).count()
    con_usuario = lotes.exclude(usuario__isnull=True).count()

    return render(
        request,
        "core/administracion_lotes.html",
        {
            "lotes": lotes,
            "filtros": {"estado": estado, "q": q},
            "total": total,
            "activos": activos,
            "inactivos": inactivos,
            "con_usuario": con_usuario,
        },
    )


@superuser_required
def administracion_lote_detalle(request, lote_id):
    lote = get_object_or_404(
        Lote.objects.select_related("usuario"),
        pk=lote_id,
    )

    integrantes = lote.integrantes.all().order_by(
        "-activo", "apellido", "nombre"
    )

    solicitudes = (
        SolicitudModificacionFamilia.objects
        .select_related("integrante")
        .filter(lote=lote)
        .order_by("-fecha_creacion")[:10]
    )

    return render(
        request,
        "core/administracion_lote_detalle.html",
        {
            "lote": lote,
            "integrantes": integrantes,
            "solicitudes": solicitudes,
            "integrantes_activos": integrantes.filter(activo=True).count(),
            "integrantes_inactivos": integrantes.filter(activo=False).count(),
        },
    )


@superuser_required
def enviar_invitacion_vecino(request, lote_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    lote = get_object_or_404(
        Lote.objects.select_related("usuario"),
        pk=lote_id,
    )

    form = InvitacionVecinoForm(request.POST)

    if not form.is_valid():
        messages.error(request, "Ingresá un correo electrónico válido.")
        return redirect("administracion_lote_detalle", lote_id=lote.id)

    if not lote.activo:
        messages.error(request, "No se puede invitar a un lote inactivo.")
        return redirect("administracion_lote_detalle", lote_id=lote.id)

    email = form.cleaned_data["email"]
    usuario = lote.usuario

    if usuario:
        if usuario.is_active or usuario.has_usable_password():
            messages.error(
                request,
                "Este lote ya tiene una cuenta configurada."
            )
            return redirect("administracion_lote_detalle", lote_id=lote.id)
    else:
        username = str(lote.numero)

        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                "Ya existe un usuario con ese número de lote."
            )
            return redirect("administracion_lote_detalle", lote_id=lote.id)

    # En desarrollo mostramos el correo en los registros de Docker.
    from django.core.mail import get_connection

    conexion = get_connection(
        backend="django.core.mail.backends.console.EmailBackend"
    )

    try:
        with transaction.atomic():
            if usuario is None:
                usuario = User(username=str(lote.numero), email=email)
                usuario.set_unusable_password()
                usuario.is_active = False
                usuario.save()

                lote.usuario = usuario
                lote.email = email
                lote.save(update_fields=["usuario", "email"])
            else:
                usuario.email = email
                usuario.save(update_fields=["email"])
                lote.email = email
                lote.save(update_fields=["email"])

            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)

            url_activacion = request.build_absolute_uri(
                reverse(
                    "activar_cuenta",
                    kwargs={"uidb64": uid, "token": token},
                )
            )

            EmailMessage(
                subject="Activá tu cuenta de Comunidad360",
                body=(
                    f"Bienvenido a Comunidad360 - Las Acacias Hudson.\n\n"
                    f"Tu usuario es el número de lote: {lote.numero}\n\n"
                    f"Para crear tu contraseña ingresá aquí:\n"
                    f"{url_activacion}\n\n"
                    f"Si no esperabas esta invitación, "
                    f"contactá a la administración."
                ),
                from_email="Comunidad360 <no-reply@lasacaciashudson.local>",
                to=[email],
                connection=conexion,
            ).send(fail_silently=False)

    except Exception:
        messages.error(
            request,
            "No se pudo generar la invitación. No se guardaron los cambios."
        )
        return redirect("administracion_lote_detalle", lote_id=lote.id)

    messages.success(
        request,
        "Invitación generada correctamente. Revisá los registros de Docker."
    )
    return redirect("administracion_lote_detalle", lote_id=lote.id)
