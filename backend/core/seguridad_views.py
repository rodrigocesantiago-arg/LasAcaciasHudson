from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    EncomiendaForm,
    EntregaEncomiendaForm,
    VisitaEspontaneaForm,
)
from .models import Emergencia, Encomienda, ReservaSUM, Visita
from .role_required import porteria_required


@porteria_required
def seguridad_dashboard(request):
    hoy = timezone.localdate()

    personas_dentro = Visita.objects.filter(
        estado="autorizada",
        fecha_hora_ingreso__isnull=False,
        fecha_hora_salida__isnull=True,
    ).count()

    visitas_hoy_pendientes = Visita.objects.filter(
        estado="autorizada",
        fecha=hoy,
        fecha_hora_ingreso__isnull=True,
    ).count()

    proximas_visitas = Visita.objects.filter(
        estado="autorizada",
        fecha__gt=hoy,
        fecha_hora_ingreso__isnull=True,
    ).count()

    encomiendas_pendientes = Encomienda.objects.filter(
        estado="pendiente"
    ).count()

    reservas_sum_hoy = ReservaSUM.objects.filter(
        fecha=hoy
    ).exclude(
        estado="cancelada"
    ).select_related(
        "lote"
    ).order_by("turno")

    emergencias_activas = Emergencia.objects.filter(
        estado__in=["activa", "atendida"]
    ).select_related(
        "lote",
        "usuario",
        "atendida_por",
    ).order_by(
        "fecha_creacion"
    )

    cantidad_emergencias_activas = emergencias_activas.count()

    return render(
        request,
        "core/seguridad_dashboard.html",
        {
            "hoy": hoy,
            "personas_dentro": personas_dentro,
            "visitas_hoy_pendientes": visitas_hoy_pendientes,
            "proximas_visitas": proximas_visitas,
            "encomiendas_pendientes": encomiendas_pendientes,
            "reservas_sum_hoy": reservas_sum_hoy,
            "emergencias_activas": emergencias_activas,
            "cantidad_emergencias_activas": cantidad_emergencias_activas,
        }
    )


@porteria_required
def tomar_emergencia(request, emergencia_id):
    if request.method != "POST":
        return redirect("seguridad_dashboard")

    emergencia = get_object_or_404(
        Emergencia,
        id=emergencia_id,
        estado__in=["activa", "atendida"],
    )

    if emergencia.estado == "activa":
        emergencia.estado = "atendida"
        emergencia.fecha_atencion = timezone.now()
        emergencia.atendida_por = request.user
        emergencia.save(
            update_fields=[
                "estado",
                "fecha_atencion",
                "atendida_por",
            ]
        )

    return redirect("seguridad_dashboard")


@porteria_required
def cerrar_emergencia(request, emergencia_id):
    if request.method != "POST":
        return redirect("seguridad_dashboard")

    emergencia = get_object_or_404(
        Emergencia,
        id=emergencia_id,
        estado__in=["activa", "atendida"],
    )

    observaciones = request.POST.get(
        "observaciones_porteria",
        ""
    ).strip()

    if emergencia.estado == "activa":
        emergencia.fecha_atencion = timezone.now()
        emergencia.atendida_por = request.user

    emergencia.estado = "cerrada"
    emergencia.fecha_cierre = timezone.now()
    emergencia.cerrada_por = request.user
    emergencia.observaciones_porteria = observaciones

    emergencia.save(
        update_fields=[
            "estado",
            "fecha_atencion",
            "atendida_por",
            "fecha_cierre",
            "cerrada_por",
            "observaciones_porteria",
        ]
    )

    return redirect("seguridad_dashboard")


@porteria_required
def estado_emergencias(request):
    """
    Endpoint liviano para el dashboard de Portería.
    Permite detectar nuevas emergencias sin recargar manualmente toda la página.
    """
    emergencias = Emergencia.objects.filter(
        estado__in=["activa", "atendida"]
    ).select_related(
        "lote",
        "atendida_por",
    ).order_by(
        "fecha_creacion"
    )

    datos = []

    for emergencia in emergencias:
        datos.append(
            {
                "id": emergencia.id,
                "tipo": emergencia.tipo,
                "tipo_display": emergencia.get_tipo_display(),
                "estado": emergencia.estado,
                "lote": emergencia.lote.numero,
                "familia": emergencia.lote.apellido_familia,
                "fecha_creacion": timezone.localtime(
                    emergencia.fecha_creacion
                ).strftime("%d/%m/%Y %H:%M:%S"),
                "es_comunitaria": emergencia.es_comunitaria,
            }
        )

    return JsonResponse(
        {
            "cantidad": len(datos),
            "emergencias": datos,
        }
    )


@porteria_required
def seguridad_visitas(request):
    hoy = timezone.localdate()
    busqueda = request.GET.get("q", "").strip()

    personas_dentro = Visita.objects.filter(
        estado="autorizada",
        fecha_hora_ingreso__isnull=False,
        fecha_hora_salida__isnull=True,
    ).select_related(
        "lote"
    ).order_by(
        "fecha_hora_ingreso"
    )

    visitas_hoy = Visita.objects.filter(
        estado="autorizada",
        fecha=hoy,
        fecha_hora_ingreso__isnull=True,
    ).select_related(
        "lote"
    ).order_by(
        "apellido",
        "nombre",
    )

    proximas_visitas = Visita.objects.filter(
        estado="autorizada",
        fecha__gt=hoy,
        fecha_hora_ingreso__isnull=True,
    ).select_related(
        "lote"
    ).order_by(
        "fecha",
        "apellido",
        "nombre",
    )

    if busqueda:
        filtro = (
            Q(dni__icontains=busqueda)
            | Q(patente__icontains=busqueda)
            | Q(apellido__icontains=busqueda)
        )
        personas_dentro = personas_dentro.filter(filtro)
        visitas_hoy = visitas_hoy.filter(filtro)
        proximas_visitas = proximas_visitas.filter(filtro)

    proximas_visitas = proximas_visitas[:100]

    return render(
        request,
        "core/seguridad_visitas.html",
        {
            "personas_dentro": personas_dentro,
            "visitas_hoy": visitas_hoy,
            "proximas_visitas": proximas_visitas,
            "busqueda": busqueda,
            "hoy": hoy,
        }
    )


@porteria_required
def historial_seguridad(request):
    busqueda = request.GET.get("q", "").strip()
    fecha_desde = request.GET.get("desde", "").strip()
    fecha_hasta = request.GET.get("hasta", "").strip()

    movimientos = Visita.objects.filter(
        Q(fecha_hora_ingreso__isnull=False)
        | Q(fecha_hora_salida__isnull=False)
    ).select_related("lote")

    if busqueda:
        movimientos = movimientos.filter(
            Q(dni__icontains=busqueda)
            | Q(patente__icontains=busqueda)
            | Q(apellido__icontains=busqueda)
            | Q(nombre__icontains=busqueda)
            | Q(lote__numero__icontains=busqueda)
        )

    if fecha_desde:
        movimientos = movimientos.filter(
            fecha_hora_ingreso__date__gte=fecha_desde
        )

    if fecha_hasta:
        movimientos = movimientos.filter(
            fecha_hora_ingreso__date__lte=fecha_hasta
        )

    movimientos = movimientos.order_by(
        "-fecha_hora_ingreso",
        "-fecha",
    )[:500]

    return render(
        request,
        "core/historial_seguridad.html",
        {
            "movimientos": movimientos,
            "busqueda": busqueda,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
        }
    )


@porteria_required
def visita_espontanea(request):
    if request.method == "POST":
        form = VisitaEspontaneaForm(request.POST)

        if form.is_valid():
            visita = form.save(commit=False)
            visita.fecha = timezone.localdate()
            visita.estado = "autorizada"
            visita.fecha_hora_ingreso = timezone.now()
            visita.save()

            return redirect("seguridad_visitas")
    else:
        form = VisitaEspontaneaForm()

    return render(
        request,
        "core/visita_espontanea.html",
        {"form": form},
    )


@porteria_required
def seguridad_encomiendas(request):
    busqueda = request.GET.get("q", "").strip()

    pendientes = Encomienda.objects.filter(
        estado="pendiente"
    ).select_related(
        "lote"
    ).order_by(
        "-fecha_recepcion"
    )

    recientes = Encomienda.objects.filter(
        estado="entregada"
    ).select_related(
        "lote"
    ).order_by(
        "-fecha_entrega"
    )

    if busqueda:
        filtro = (
            Q(lote__numero__icontains=busqueda)
            | Q(lote__apellido_familia__icontains=busqueda)
            | Q(remitente__icontains=busqueda)
            | Q(descripcion__icontains=busqueda)
        )
        pendientes = pendientes.filter(filtro)
        recientes = recientes.filter(filtro)

    recientes = recientes[:50]

    return render(
        request,
        "core/seguridad_encomiendas.html",
        {
            "pendientes": pendientes,
            "recientes": recientes,
            "busqueda": busqueda,
        }
    )


@porteria_required
def registrar_encomienda(request):
    if request.method == "POST":
        form = EncomiendaForm(request.POST)

        if form.is_valid():
            encomienda = form.save(commit=False)
            encomienda.estado = "pendiente"
            encomienda.save()

            return redirect("seguridad_encomiendas")
    else:
        form = EncomiendaForm()

    return render(
        request,
        "core/registrar_encomienda.html",
        {"form": form},
    )


@porteria_required
def entregar_encomienda(request, encomienda_id):
    encomienda = get_object_or_404(
        Encomienda,
        id=encomienda_id,
        estado="pendiente",
    )

    if request.method == "POST":
        form = EntregaEncomiendaForm(
            request.POST,
            lote=encomienda.lote,
        )

        if form.is_valid():
            tipo_retiro = form.cleaned_data["tipo_retiro"]

            if tipo_retiro == "familia":
                integrante = form.cleaned_data["integrante"]
                retirado_por = f"{integrante.apellido}, {integrante.nombre}"
            else:
                retirado_por = form.cleaned_data["otro_nombre"].strip()

            encomienda.estado = "entregada"
            encomienda.fecha_entrega = timezone.now()
            encomienda.retirado_por = retirado_por
            encomienda.save(
                update_fields=[
                    "estado",
                    "fecha_entrega",
                    "retirado_por",
                ]
            )

            return redirect("seguridad_encomiendas")
    else:
        form = EntregaEncomiendaForm(
            lote=encomienda.lote,
        )

    return render(
        request,
        "core/entregar_encomienda.html",
        {
            "encomienda": encomienda,
            "form": form,
        }
    )


@porteria_required
def registrar_ingreso(request, visita_id):
    visita = get_object_or_404(
        Visita,
        id=visita_id,
        estado="autorizada",
    )

    if (
        request.method == "POST"
        and visita.fecha_hora_ingreso is None
        and visita.fecha == timezone.localdate()
    ):
        visita.fecha_hora_ingreso = timezone.now()
        visita.save(update_fields=["fecha_hora_ingreso"])

    return redirect("seguridad_visitas")


@porteria_required
def registrar_salida(request, visita_id):
    visita = get_object_or_404(
        Visita,
        id=visita_id,
        estado="autorizada",
    )

    if (
        request.method == "POST"
        and visita.fecha_hora_ingreso is not None
        and visita.fecha_hora_salida is None
    ):
        visita.fecha_hora_salida = timezone.now()
        visita.save(update_fields=["fecha_hora_salida"])

    return redirect("seguridad_visitas")