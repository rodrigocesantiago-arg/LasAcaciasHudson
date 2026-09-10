from datetime import datetime

from django.db.models import Q
from django.shortcuts import render

from .administracion_views import superuser_required
from .models import Emergencia


@superuser_required
def administracion_emergencias(request):
    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    fecha_desde = request.GET.get("desde", "").strip()
    fecha_hasta = request.GET.get("hasta", "").strip()

    emergencias = Emergencia.objects.select_related(
        "lote",
        "usuario",
        "atendida_por",
        "cerrada_por",
    ).all()

    if busqueda:
        emergencias = emergencias.filter(
            Q(lote__numero__icontains=busqueda)
            | Q(lote__apellido_familia__icontains=busqueda)
            | Q(descripcion__icontains=busqueda)
            | Q(observaciones_porteria__icontains=busqueda)
            | Q(usuario__username__icontains=busqueda)
            | Q(atendida_por__username__icontains=busqueda)
            | Q(cerrada_por__username__icontains=busqueda)
        )

    estados_validos = {codigo for codigo, nombre in Emergencia.ESTADOS}
    if estado in estados_validos:
        emergencias = emergencias.filter(estado=estado)

    tipos_validos = {codigo for codigo, nombre in Emergencia.TIPOS}
    if tipo in tipos_validos:
        emergencias = emergencias.filter(tipo=tipo)

    if fecha_desde:
        try:
            desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
            emergencias = emergencias.filter(fecha_creacion__date__gte=desde)
        except ValueError:
            pass

    if fecha_hasta:
        try:
            hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
            emergencias = emergencias.filter(fecha_creacion__date__lte=hasta)
        except ValueError:
            pass

    emergencias = emergencias.order_by("-fecha_creacion")[:1000]

    resumen = {
        "activas": Emergencia.objects.filter(estado="activa").count(),
        "atendidas": Emergencia.objects.filter(estado="atendida").count(),
        "cerradas": Emergencia.objects.filter(estado="cerrada").count(),
        "comunitarias_abiertas": Emergencia.objects.filter(
            tipo__in=["robo", "incendio"],
            estado__in=["activa", "atendida"],
        ).count(),
    }

    return render(
        request,
        "core/administracion_emergencias.html",
        {
            "emergencias": emergencias,
            "resumen": resumen,
            "busqueda": busqueda,
            "estado_seleccionado": estado,
            "tipo_seleccionado": tipo,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "estados": Emergencia.ESTADOS,
            "tipos": Emergencia.TIPOS,
        },
    )