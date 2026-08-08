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


def reservar_sum(request):
    if not request.user.is_authenticated:
        return redirect("home")

    lote = request.user.lote

    if request.method == "POST":
        form = ReservaSUMForm(request.POST)

        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.lote = lote
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
        form = ReservaSUMForm()

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