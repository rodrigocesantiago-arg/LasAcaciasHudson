from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .administracion_views import superuser_required
from .models import Lote, SolicitudModificacionFamilia


@superuser_required
def administracion_solicitudes_familiares(request):
    estado = request.GET.get("estado", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    lote_id = request.GET.get("lote", "").strip()
    q = request.GET.get("q", "").strip()

    solicitudes = SolicitudModificacionFamilia.objects.select_related(
        "lote", "integrante"
    ).all()

    if estado in dict(SolicitudModificacionFamilia.ESTADOS):
        solicitudes = solicitudes.filter(estado=estado)
    else:
        estado = ""

    if tipo in dict(SolicitudModificacionFamilia.TIPOS):
        solicitudes = solicitudes.filter(tipo=tipo)
    else:
        tipo = ""

    if lote_id.isdigit():
        solicitudes = solicitudes.filter(lote_id=int(lote_id))
    else:
        lote_id = ""

    if q:
        filtro = (
            Q(lote__apellido_familia__icontains=q)
            | Q(detalle__icontains=q)
            | Q(integrante__nombre__icontains=q)
            | Q(integrante__apellido__icontains=q)
            | Q(nuevo_nombre__icontains=q)
            | Q(nuevo_apellido__icontains=q)
        )
        if q.isdigit():
            filtro |= Q(lote__numero=int(q))
        solicitudes = solicitudes.filter(filtro)

    solicitudes = solicitudes.order_by("-fecha_creacion")

    return render(
        request,
        "core/administracion_solicitudes_familiares.html",
        {
            "solicitudes": solicitudes,
            "lotes": Lote.objects.filter(activo=True).order_by("numero"),
            "estados": SolicitudModificacionFamilia.ESTADOS,
            "tipos": SolicitudModificacionFamilia.TIPOS,
            "filtros": {
                "estado": estado,
                "tipo": tipo,
                "lote": int(lote_id) if lote_id else "",
                "q": q,
            },
            "total": solicitudes.count(),
            "pendientes": solicitudes.filter(estado="pendiente").count(),
            "aprobadas": solicitudes.filter(estado="aprobada").count(),
            "rechazadas": solicitudes.filter(estado="rechazada").count(),
        },
    )


@superuser_required
def administracion_solicitud_familiar_detalle(request, solicitud_id):
    solicitud = get_object_or_404(
        SolicitudModificacionFamilia.objects.select_related("lote", "integrante"),
        pk=solicitud_id,
    )
    return render(
        request,
        "core/administracion_solicitud_familiar_detalle.html",
        {"solicitud": solicitud},
    )


@superuser_required
@transaction.atomic
def administracion_solicitud_familiar_resolver(request, solicitud_id):
    solicitud = get_object_or_404(
        SolicitudModificacionFamilia.objects.select_for_update(),
        pk=solicitud_id,
    )

    if request.method != "POST":
        return redirect(
            "administracion_solicitud_familiar_detalle",
            solicitud_id=solicitud.id,
        )

    if solicitud.estado != "pendiente" or solicitud.aplicada:
        messages.info(request, "Esta solicitud ya fue resuelta y no puede modificarse.")
        return redirect(
            "administracion_solicitud_familiar_detalle",
            solicitud_id=solicitud.id,
        )

    accion = request.POST.get("accion", "").strip()
    respuesta = request.POST.get("respuesta_administracion", "").strip()

    if accion not in {"aprobar", "rechazar"}:
        messages.error(request, "La acción solicitada no es válida.")
        return redirect(
            "administracion_solicitud_familiar_detalle",
            solicitud_id=solicitud.id,
        )

    solicitud.respuesta_administracion = respuesta

    if accion == "rechazar":
        solicitud.estado = "rechazada"
        solicitud.save(update_fields=["estado", "respuesta_administracion"])
        messages.success(request, "Solicitud rechazada correctamente.")
    else:
        solicitud.estado = "aprobada"
        solicitud.save(update_fields=["estado", "respuesta_administracion"])
        solicitud.aplicar_cambio()

        if solicitud.tipo == "otro":
            messages.success(
                request,
                "Solicitud aprobada. El tipo 'Otro' no realiza cambios automáticos.",
            )
        else:
            messages.success(
                request,
                "Solicitud aprobada y cambio familiar aplicado correctamente.",
            )

    return redirect(
        "administracion_solicitud_familiar_detalle",
        solicitud_id=solicitud.id,
    )