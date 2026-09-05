from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Encomienda, Lote, Reclamo, ReservaSUM, SolicitudModificacionFamilia


def superuser_required(view_func):
    @staff_member_required
    def wrapped(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect("seguridad_dashboard")
        return view_func(request, *args, **kwargs)
    return wrapped


@superuser_required
def administracion_dashboard(request):
    hoy = timezone.localdate()

    context = {
        "lotes_activos": Lote.objects.filter(activo=True).count(),
        "reclamos_abiertos": Reclamo.objects.filter(estado__in=["pendiente", "en_proceso"]).count(),
        "reservas_pendientes": ReservaSUM.objects.filter(estado="pendiente").count(),
        "encomiendas_pendientes": Encomienda.objects.filter(estado="pendiente").count(),
        "solicitudes_pendientes": SolicitudModificacionFamilia.objects.filter(estado="pendiente").count(),
        "ultimos_reclamos": Reclamo.objects.filter(
            estado__in=["pendiente", "en_proceso"]
        ).select_related("lote").order_by("-fecha_creacion")[:5],
        "proximas_reservas": ReservaSUM.objects.filter(
            fecha__gte=hoy
        ).exclude(estado="cancelada").select_related("lote").order_by("fecha", "turno")[:5],
    }
    return render(request, "core/administracion_dashboard.html", context)