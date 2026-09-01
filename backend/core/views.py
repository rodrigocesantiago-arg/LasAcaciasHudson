from datetime import date, datetime, timedelta

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    InvitadoFrecuenteForm,
    ReclamoForm,
    ReservaSUMForm,
    SolicitudModificacionFamiliaForm,
    VisitaForm,
)

from .models import (
    ContactoUtil,
    Documento,
    Encomienda,
    Integrante,
    InvitadoFrecuente,
    Noticia,
    Reclamo,
    ReservaSUM,
    SolicitudModificacionFamilia,
    Visita,
)


# -------------------------------------------------
# HOME Y LOGIN
# -------------------------------------------------

def home(request):
    return render(request, "core/home.html")


def login_view(request):
    if request.method == "POST":
        numero_lote = request.POST.get("numero_lote")
        password = request.POST.get("password")

        usuario = authenticate(
            request,
            username=numero_lote,
            password=password
        )

        if usuario is not None:
            login(request, usuario)
            return redirect("portal")

        return render(
            request,
            "core/home.html",
            {
                "error": "Número de lote o contraseña incorrectos."
            }
        )

    return render(request, "core/home.html")


# -------------------------------------------------
# CUMPLEAÑOS - FUNCIÓN AUXILIAR
# -------------------------------------------------

def obtener_proximos_cumpleanios(limite=None):
    hoy = timezone.localdate()

    integrantes = Integrante.objects.filter(
        activo=True
    )

    cumpleanios = []

    for integrante in integrantes:
        nacimiento = integrante.fecha_nacimiento

        try:
            proximo = date(
                hoy.year,
                nacimiento.month,
                nacimiento.day
            )

        except ValueError:
            proximo = date(
                hoy.year,
                2,
                28
            )

        if proximo < hoy:

            try:
                proximo = date(
                    hoy.year + 1,
                    nacimiento.month,
                    nacimiento.day
                )

            except ValueError:
                proximo = date(
                    hoy.year + 1,
                    2,
                    28
                )

        dias_faltantes = (
            proximo - hoy
        ).days

        cumpleanios.append(
            {
                "integrante": integrante,
                "fecha": proximo,
                "dias_faltantes": dias_faltantes,
            }
        )

    cumpleanios.sort(
        key=lambda item: item["fecha"]
    )

    if limite:
        cumpleanios = cumpleanios[:limite]

    return cumpleanios


# -------------------------------------------------
# PORTAL
# -------------------------------------------------

def portal(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote
    hoy = timezone.localdate()

    # NOTICIAS

    noticias = Noticia.objects.filter(
        activa=True
    ).order_by(
        "-fecha_publicacion"
    )[:3]

    # RESERVAS DEL SUM

    proximas_reservas = ReservaSUM.objects.filter(
        lote=lote
    ).order_by(
        "-fecha",
        "-fecha_creacion"
    )[:3]

    for reserva in proximas_reservas:

        fecha_limite_cancelacion = (
            reserva.fecha - timedelta(days=7)
        )

        reserva.puede_cancelar = (
            hoy <= fecha_limite_cancelacion
            and reserva.estado != "cancelada"
        )

    # CUMPLEAÑOS DEL MES

    cumpleanios_mes = []

    integrantes_activos = Integrante.objects.filter(
        activo=True
    )

    for integrante in integrantes_activos:

        if integrante.fecha_nacimiento.month == hoy.month:
            cumpleanios_mes.append(integrante)

    cumpleanios_mes.sort(
        key=lambda integrante:
        integrante.fecha_nacimiento.day
    )

    # ENCOMIENDAS PENDIENTES DEL LOTE

    encomiendas_pendientes = Encomienda.objects.filter(
        lote=lote,
        estado="pendiente"
    ).order_by(
        "-fecha_recepcion"
    )

    cantidad_encomiendas_pendientes = (
        encomiendas_pendientes.count()
    )

    ultimas_encomiendas_pendientes = (
        encomiendas_pendientes[:3]
    )

    return render(
        request,
        "core/portal.html",
        {
            "lote": lote,
            "noticias": noticias,
            "proximas_reservas": proximas_reservas,
            "cumpleanios_mes": cumpleanios_mes,
            "cantidad_encomiendas_pendientes":
                cantidad_encomiendas_pendientes,
            "ultimas_encomiendas_pendientes":
                ultimas_encomiendas_pendientes,
        }
    )


# -------------------------------------------------
# NOTICIAS
# -------------------------------------------------

def noticias_view(request):
    if not request.user.is_authenticated:
        return redirect("home")

    noticias = Noticia.objects.filter(
        activa=True
    ).order_by(
        "-fecha_publicacion"
    )

    return render(
        request,
        "core/noticias.html",
        {
            "noticias": noticias
        }
    )


# -------------------------------------------------
# CUMPLEAÑOS
# -------------------------------------------------

def cumpleanios_view(request):
    if not request.user.is_authenticated:
        return redirect("home")

    cumpleanios = obtener_proximos_cumpleanios()

    return render(
        request,
        "core/cumpleanios.html",
        {
            "cumpleanios": cumpleanios,
        }
    )


# -------------------------------------------------
# RESERVAS SUM
# -------------------------------------------------

def mis_reservas_sum(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote
    hoy = timezone.localdate()

    reservas = ReservaSUM.objects.filter(
        lote=lote
    ).order_by(
        "-fecha",
        "-fecha_creacion"
    )

    for reserva in reservas:

        fecha_limite_cancelacion = (
            reserva.fecha - timedelta(days=7)
        )

        reserva.puede_cancelar = (
            hoy <= fecha_limite_cancelacion
            and reserva.estado != "cancelada"
        )

    return render(
        request,
        "core/mis_reservas_sum.html",
        {
            "lote": lote,
            "reservas": reservas,
        }
    )


def disponibilidad_sum(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    fecha_texto = request.GET.get("fecha")

    fecha_consultada = None
    turno_dia_disponible = None
    turno_noche_disponible = None

    if fecha_texto:

        try:

            fecha_consultada = datetime.strptime(
                fecha_texto,
                "%Y-%m-%d"
            ).date()

            turno_dia_ocupado = ReservaSUM.objects.filter(
                fecha=fecha_consultada,
                turno="dia"
            ).exclude(
                estado="cancelada"
            ).exists()

            turno_noche_ocupado = ReservaSUM.objects.filter(
                fecha=fecha_consultada,
                turno="noche"
            ).exclude(
                estado="cancelada"
            ).exists()

            turno_dia_disponible = (
                not turno_dia_ocupado
            )

            turno_noche_disponible = (
                not turno_noche_ocupado
            )

        except ValueError:
            fecha_consultada = None

    return render(
        request,
        "core/disponibilidad_sum.html",
        {
            "lote": lote,
            "fecha_consultada": fecha_consultada,
            "fecha_texto": fecha_texto,
            "turno_dia_disponible": turno_dia_disponible,
            "turno_noche_disponible": turno_noche_disponible,
        }
    )


def reservar_sum(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    fecha_inicial = request.GET.get("fecha")
    turno_inicial = request.GET.get("turno")

    if request.method == "POST":

        form = ReservaSUMForm(
            request.POST
        )

        if form.is_valid():

            reserva = form.save(
                commit=False
            )

            reserva.lote = lote
            reserva.estado = "pendiente"

            try:

                reserva.save()

                return render(
                    request,
                    "core/reserva_sum_ok.html",
                    {
                        "reserva": reserva
                    }
                )

            except Exception:

                form.add_error(
                    None,
                    (
                        "Ese turno ya está reservado "
                        "para la fecha seleccionada."
                    )
                )

    else:

        form = ReservaSUMForm(
            initial={
                "fecha": fecha_inicial,
                "turno": turno_inicial,
            }
        )

    return render(
        request,
        "core/reservar_sum.html",
        {
            "form": form,
            "lote": lote,
        }
    )


def cancelar_reserva_sum(
    request,
    reserva_id
):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    reserva = get_object_or_404(
        ReservaSUM,
        id=reserva_id,
        lote=lote
    )

    if request.method == "POST":

        hoy = timezone.localdate()

        fecha_limite = (
            reserva.fecha - timedelta(days=7)
        )

        if (
            hoy <= fecha_limite
            and reserva.estado != "cancelada"
        ):

            reserva.estado = "cancelada"
            reserva.save()

    return redirect("portal")


# -------------------------------------------------
# MI FAMILIA
# -------------------------------------------------

def mi_familia(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    integrantes = Integrante.objects.filter(
        lote=lote,
        activo=True
    ).order_by(
        "apellido",
        "nombre"
    )

    solicitudes = (
        SolicitudModificacionFamilia.objects
        .filter(
            lote=lote
        )
        .order_by(
            "-fecha_creacion"
        )
    )

    return render(
        request,
        "core/mi_familia.html",
        {
            "lote": lote,
            "integrantes": integrantes,
            "solicitudes": solicitudes,
        }
    )


def solicitar_modificacion_familia(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    if request.method == "POST":

        form = SolicitudModificacionFamiliaForm(
            request.POST,
            lote=lote
        )

        if form.is_valid():

            solicitud = form.save(
                commit=False
            )

            solicitud.lote = lote
            solicitud.estado = "pendiente"

            solicitud.save()

            return redirect(
                "mi_familia"
            )

    else:

        form = SolicitudModificacionFamiliaForm(
            lote=lote
        )

    return render(
        request,
        "core/solicitar_modificacion_familia.html",
        {
            "form": form,
            "lote": lote,
        }
    )


# -------------------------------------------------
# RECLAMOS
# -------------------------------------------------

def mis_reclamos(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    reclamos = Reclamo.objects.filter(
        lote=lote
    ).order_by(
        "-fecha_creacion"
    )

    return render(
        request,
        "core/mis_reclamos.html",
        {
            "lote": lote,
            "reclamos": reclamos,
        }
    )


def nuevo_reclamo(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    if request.method == "POST":

        form = ReclamoForm(
            request.POST
        )

        if form.is_valid():

            reclamo = form.save(
                commit=False
            )

            reclamo.lote = lote
            reclamo.estado = "pendiente"

            reclamo.save()

            return redirect(
                "mis_reclamos"
            )

    else:

        form = ReclamoForm()

    return render(
        request,
        "core/nuevo_reclamo.html",
        {
            "form": form,
            "lote": lote,
        }
    )


# -------------------------------------------------
# ENCOMIENDAS
# -------------------------------------------------

def mis_encomiendas(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    encomiendas = Encomienda.objects.filter(
        lote=lote
    ).order_by(
        "-fecha_recepcion"
    )

    pendientes = encomiendas.filter(
        estado="pendiente"
    )

    cantidad_pendientes = pendientes.count()

    return render(
        request,
        "core/mis_encomiendas.html",
        {
            "lote": lote,
            "encomiendas": encomiendas,
            "cantidad_pendientes": cantidad_pendientes,
        }
    )


# -------------------------------------------------
# DOCUMENTOS
# -------------------------------------------------

def documentos_view(request):
    if not request.user.is_authenticated:
        return redirect("home")

    documentos = Documento.objects.filter(
        activo=True
    ).order_by(
        "categoria",
        "-fecha_publicacion"
    )

    categorias = []

    for codigo, nombre in Documento.CATEGORIAS:

        documentos_categoria = documentos.filter(
            categoria=codigo
        )

        if documentos_categoria.exists():
            categorias.append(
                {
                    "codigo": codigo,
                    "nombre": nombre,
                    "documentos": documentos_categoria,
                }
            )

    return render(
        request,
        "core/documentos.html",
        {
            "documentos": documentos,
            "categorias": categorias,
        }
    )


# -------------------------------------------------
# CONTACTOS ÚTILES
# -------------------------------------------------

def contactos_utiles(request):
    if not request.user.is_authenticated:
        return redirect("home")

    contactos = ContactoUtil.objects.filter(
        activo=True
    ).order_by(
        "orden",
        "categoria",
        "nombre"
    )

    categorias = []

    for codigo, nombre in ContactoUtil.CATEGORIAS:

        contactos_categoria = contactos.filter(
            categoria=codigo
        )

        if contactos_categoria.exists():
            categorias.append(
                {
                    "codigo": codigo,
                    "nombre": nombre,
                    "contactos": contactos_categoria,
                }
            )

    return render(
        request,
        "core/contactos_utiles.html",
        {
            "categorias": categorias,
        }
    )

    # -------------------------------------------------
# VISITAS
# -------------------------------------------------

def visitas_view(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    proximas_visitas = Visita.objects.filter(
        lote=lote,
        fecha__gte=timezone.localdate(),
        estado="autorizada",
    ).order_by(
        "fecha",
        "apellido",
        "nombre",
    )[:10]

    return render(
        request,
        "core/visitas.html",
        {
            "lote": lote,
            "proximas_visitas": proximas_visitas,
        }
    )


def autorizar_visita(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    if request.method == "POST":

        form = VisitaForm(
            request.POST,
            lote=lote,
        )

        if form.is_valid():

            visita = form.save(
                commit=False
            )

            visita.lote = lote
            visita.estado = "autorizada"

            if visita.invitado:

                visita.nombre = visita.invitado.nombre
                visita.apellido = visita.invitado.apellido
                visita.dni = visita.invitado.dni

                if not visita.patente:
                    visita.patente = visita.invitado.patente

            visita.save()

            return redirect(
                "historial_visitas"
            )

    else:

        form = VisitaForm(
            lote=lote
        )

    return render(
        request,
        "core/autorizar_visita.html",
        {
            "form": form,
            "lote": lote,
        }
    )


def historial_visitas(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    visitas = Visita.objects.filter(
        lote=lote
    ).order_by(
        "-fecha",
        "-fecha_creacion",
    )

    return render(
        request,
        "core/historial_visitas.html",
        {
            "lote": lote,
            "visitas": visitas,
        }
    )


def agenda_visitas(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote
    hoy = timezone.localdate()

    visitas = Visita.objects.filter(
        lote=lote,
        fecha__gte=hoy,
        estado="autorizada",
    ).order_by(
        "fecha",
        "apellido",
        "nombre",
    )

    return render(
        request,
        "core/agenda_visitas.html",
        {
            "lote": lote,
            "visitas": visitas,
            "hoy": hoy,
        }
    )


def invitados_frecuentes(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    invitados = InvitadoFrecuente.objects.filter(
        lote=lote,
        activo=True,
    ).order_by(
        "apellido",
        "nombre",
    )

    return render(
        request,
        "core/invitados_frecuentes.html",
        {
            "lote": lote,
            "invitados": invitados,
        }
    )


def nuevo_invitado_frecuente(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    if request.method == "POST":

        form = InvitadoFrecuenteForm(
            request.POST
        )

        if form.is_valid():

            invitado = form.save(
                commit=False
            )

            invitado.lote = lote
            invitado.activo = True

            invitado.save()

            return redirect(
                "invitados_frecuentes"
            )

    else:

        form = InvitadoFrecuenteForm()

    return render(
        request,
        "core/nuevo_invitado_frecuente.html",
        {
            "form": form,
            "lote": lote,
        }
    )


def cancelar_visita(
    request,
    visita_id
):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    visita = get_object_or_404(
        Visita,
        id=visita_id,
        lote=lote,
    )

    if request.method == "POST":

        visita.estado = "cancelada"
        visita.save()

    return redirect(
        "historial_visitas"
    )


# -------------------------------------------------
# LOGOUT
# -------------------------------------------------

def logout_view(request):
    logout(request)

    return redirect("home")