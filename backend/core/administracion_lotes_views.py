from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, render

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