from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .administracion_views import superuser_required
from .models import Encomienda, Lote


@superuser_required
def administracion_encomiendas(request):
    estado = request.GET.get("estado", "").strip()
    lote_id = request.GET.get("lote", "").strip()
    q = request.GET.get("q", "").strip()

    encomiendas = Encomienda.objects.select_related("lote").all()

    if estado in dict(Encomienda.ESTADOS):
        encomiendas = encomiendas.filter(estado=estado)
    else:
        estado = ""

    if lote_id.isdigit():
        encomiendas = encomiendas.filter(lote_id=int(lote_id))
    else:
        lote_id = ""

    if q:
        filtro = (
            Q(remitente__icontains=q)
            | Q(descripcion__icontains=q)
            | Q(retirado_por__icontains=q)
            | Q(observaciones__icontains=q)
            | Q(lote__apellido_familia__icontains=q)
        )
        if q.isdigit():
            filtro |= Q(lote__numero=int(q))
        encomiendas = encomiendas.filter(filtro)

    encomiendas = encomiendas.order_by("-fecha_recepcion")

    return render(
        request,
        "core/administracion_encomiendas.html",
        {
            "encomiendas": encomiendas,
            "lotes": Lote.objects.filter(activo=True).order_by("numero"),
            "estados": Encomienda.ESTADOS,
            "filtros": {
                "estado": estado,
                "lote": int(lote_id) if lote_id else "",
                "q": q,
            },
            "total": encomiendas.count(),
            "pendientes": encomiendas.filter(estado="pendiente").count(),
            "entregadas": encomiendas.filter(estado="entregada").count(),
        },
    )


@superuser_required
def administracion_encomienda_detalle(request, encomienda_id):
    encomienda = get_object_or_404(
        Encomienda.objects.select_related("lote"),
        pk=encomienda_id,
    )

    return render(
        request,
        "core/administracion_encomienda_detalle.html",
        {"encomienda": encomienda},
    )