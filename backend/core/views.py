from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import Noticia


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

    return render(
        request,
        "core/portal.html",
        {
            "lote": lote,
            "noticias": noticias,
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


def logout_view(request):
    logout(request)
    return redirect("home")