from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


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

    return render(
        request,
        "core/portal.html",
        {"lote": lote}
    )


def logout_view(request):
    logout(request)
    return redirect("home")