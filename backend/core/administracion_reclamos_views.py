from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .administracion_views import superuser_required
from .models import Lote, Reclamo


@superuser_required
def administracion_reclamos(request):
    estado = request.GET.get("estado", "").strip()
    categoria = request.GET.get("categoria", "").strip()
    lote_id = request.GET.get("lote", "").strip()
    q = request.GET.get("q", "").strip()

    reclamos = Reclamo.objects.select_related("lote").all()

    if estado in dict(Reclamo.ESTADOS):
        reclamos = reclamos.filter(estado=estado)
    else:
        estado = ""

    if categoria in dict(Reclamo.CATEGORIAS):
        reclamos = reclamos.filter(categoria=categoria)
    else:
        categoria = ""

    if lote_id.isdigit():
        reclamos = reclamos.filter(lote_id=int(lote_id))
    else:
        lote_id = ""

    if q:
        filtro = (
            Q(asunto__icontains=q)
            | Q(descripcion__icontains=q)
            | Q(respuesta_administracion__icontains=q)
            | Q(lote__apellido_familia__icontains=q)
        )
        if q.isdigit():
            filtro |= Q(lote__numero=int(q))
        reclamos = reclamos.filter(filtro)

    reclamos = reclamos.order_by("-fecha_creacion")

    return render(
        request,
        "core/administracion_reclamos.html",
        {
            "reclamos": reclamos,
            "lotes": Lote.objects.filter(activo=True).order_by("numero"),
            "estados": Reclamo.ESTADOS,
            "categorias": Reclamo.CATEGORIAS,
            "filtros": {
                "estado": estado,
                "categoria": categoria,
                "lote": int(lote_id) if lote_id else "",
                "q": q,
            },
            "total": reclamos.count(),
            "pendientes": reclamos.filter(estado="pendiente").count(),
            "en_proceso": reclamos.filter(estado="en_proceso").count(),
            "resueltos": reclamos.filter(estado="resuelto").count(),
            "rechazados": reclamos.filter(estado="rechazado").count(),
        },
    )


@superuser_required
def administracion_reclamo_detalle(request, reclamo_id):
    reclamo = get_object_or_404(
        Reclamo.objects.select_related("lote"),
        pk=reclamo_id,
    )

    if request.method == "POST":
        estado = request.POST.get("estado", "").strip()
        respuesta = request.POST.get("respuesta_administracion", "").strip()

        if estado not in dict(Reclamo.ESTADOS):
            messages.error(request, "El estado seleccionado no es válido.")
        else:
            reclamo.estado = estado
            reclamo.respuesta_administracion = respuesta
            reclamo.save()
            messages.success(request, "Reclamo actualizado correctamente.")
            return redirect(
                "administracion_reclamo_detalle",
                reclamo_id=reclamo.id,
            )

    return render(
        request,
        "core/administracion_reclamo_detalle.html",
        {
            "reclamo": reclamo,
            "estados": Reclamo.ESTADOS,
        },
    )