from django.db.models import Q, Sum
from django.shortcuts import render
from django.utils import timezone

from .administracion_views import superuser_required
from .models import Lote, ReservaSUM


MESES = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
    (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
]


def _entero(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


@superuser_required
def administracion_sum_historial(request):
    hoy = timezone.localdate()

    mes = _entero(request.GET.get("mes"))
    anio = _entero(request.GET.get("anio"))
    lote_id = _entero(request.GET.get("lote"))
    estado = request.GET.get("estado", "").strip()
    turno = request.GET.get("turno", "").strip()
    q = request.GET.get("q", "").strip()

    reservas = ReservaSUM.objects.select_related("lote", "solicitado_por").all()

    if mes:
        reservas = reservas.filter(fecha__month=mes)
    if anio:
        reservas = reservas.filter(fecha__year=anio)
    if lote_id:
        reservas = reservas.filter(lote_id=lote_id)

    if estado in dict(ReservaSUM.ESTADOS):
        reservas = reservas.filter(estado=estado)
    else:
        estado = ""

    if turno in dict(ReservaSUM.TURNOS):
        reservas = reservas.filter(turno=turno)
    else:
        turno = ""

    if q:
        filtro_q = (
            Q(lote__apellido_familia__icontains=q)
            | Q(solicitado_por__nombre__icontains=q)
            | Q(solicitado_por__apellido__icontains=q)
        )
        if q.isdigit():
            filtro_q |= Q(lote__numero=int(q))
        reservas = reservas.filter(filtro_q)

    reservas = reservas.order_by("-fecha", "-fecha_creacion")

    personas = reservas.aggregate(total=Sum("cantidad_personas"))["total"] or 0
    total = reservas.count()
    confirmadas = reservas.filter(estado="confirmada").count()
    pendientes = reservas.filter(estado="pendiente").count()
    canceladas = reservas.filter(estado="cancelada").count()

    anios = [fecha.year for fecha in ReservaSUM.objects.dates("fecha", "year", order="DESC")]
    if hoy.year not in anios:
        anios.insert(0, hoy.year)

    return render(
        request,
        "core/administracion_sum_historial.html",
        {
            "reservas": reservas,
            "lotes": Lote.objects.filter(activo=True).order_by("numero"),
            "meses": MESES,
            "anios": anios,
            "estados": ReservaSUM.ESTADOS,
            "turnos": ReservaSUM.TURNOS,
            "filtros": {
                "mes": mes or "",
                "anio": anio or "",
                "lote": lote_id or "",
                "estado": estado,
                "turno": turno,
                "q": q,
            },
            "total": total,
            "confirmadas": confirmadas,
            "pendientes": pendientes,
            "canceladas": canceladas,
            "personas": personas,
        }
    )