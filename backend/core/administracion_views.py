from django.shortcuts import render
from django.utils import timezone

from .models import (
    Encomienda,
    Lote,
    Reclamo,
    ReservaSUM,
    SolicitudModificacionFamilia,
)
from .role_required import administrador_required


# Compatibilidad temporal con los módulos administrativos existentes.
# Los archivos como administracion_sum_views.py todavía importan
# "superuser_required" desde este módulo.
superuser_required = administrador_required


@administrador_required
def administracion_dashboard(request):
    hoy = timezone.localdate()

    context = {
        "lotes_activos": Lote.objects.filter(activo=True).count(),
        "reclamos_abiertos": Reclamo.objects.filter(
            estado__in=["pendiente", "en_proceso"]
        ).count(),
        "reservas_pendientes": ReservaSUM.objects.filter(
            estado="pendiente"
        ).count(),
        "encomiendas_pendientes": Encomienda.objects.filter(
            estado="pendiente"
        ).count(),
        "solicitudes_pendientes": SolicitudModificacionFamilia.objects.filter(
            estado="pendiente"
        ).count(),
        "ultimos_reclamos": Reclamo.objects.filter(
            estado__in=["pendiente", "en_proceso"]
        ).select_related("lote").order_by("-fecha_creacion")[:5],
        "proximas_reservas": ReservaSUM.objects.filter(
            fecha__gte=hoy
        ).exclude(
            estado="cancelada"
        ).select_related("lote").order_by("fecha", "turno")[:5],
    }

    return render(
        request,
        "core/administracion_dashboard.html",
        context,
    )