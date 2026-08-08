from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from .forms import ReservaSUMForm
from .models import Noticia, ReservaSUM


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
            {"error": "Número de lote o contraseña incorrectos."}
        )

    return render(request, "core/home.html")


def portal(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    noticias = Noticia.objects.filter(
        activa=True
    ).order_by(
        "-fecha_publicacion"
    )[:3]

    proximas_reservas = ReservaSUM.objects.filter(
        lote=lote
    ).order_by(
        "-fecha",
        "-fecha_creacion"
    )[:3]

    return render(
        request,
        "core/portal.html",
        {
            "lote": lote,
            "noticias": noticias,
            "proximas_reservas": proximas_reservas,
        }
    )


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
        {"noticias": noticias}
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

            turno_dia_disponible = not turno_dia_ocupado
            turno_noche_disponible = not turno_noche_ocupado

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

    # Recibimos la fecha y el turno desde la pantalla
    # de disponibilidad.
    fecha_inicial = request.GET.get("fecha")
    turno_inicial = request.GET.get("turno")

    if request.method == "POST":
        form = ReservaSUMForm(request.POST)

        if form.is_valid():
            reserva = form.save(commit=False)

            # El lote se obtiene automáticamente
            # del usuario que inició sesión.
            reserva.lote = lote

            # Toda reserva nueva comienza pendiente.
            reserva.estado = "pendiente"

            try:
                reserva.save()

                return render(
                    request,
                    "core/reserva_sum_ok.html",
                    {"reserva": reserva}
                )

            except Exception:
                form.add_error(
                    None,
                    "Ese turno ya está reservado para la fecha seleccionada."
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


def logout_view(request):
    logout(request)
    return redirect("home")