from pathlib import Path

path = Path("core/views.py")
text = path.read_text(encoding="utf-8")

old = """def login_view(request):
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

            if usuario.is_staff:
                return redirect("seguridad_dashboard")

            return redirect("portal")

        return render(
            request,
            "core/home.html",
            {
                "error": "Número de lote o contraseña incorrectos."
            }
        )

    return render(request, "core/home.html")
"""

new = """def login_view(request):
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

            if usuario.is_superuser:
                return redirect("administracion_dashboard")

            if usuario.is_staff:
                return redirect("seguridad_dashboard")

            return redirect("portal")

        return render(
            request,
            "core/home.html",
            {
                "error": "Número de lote o contraseña incorrectos."
            }
        )

    return render(request, "core/home.html")
"""

if old not in text:
    raise SystemExit("No se encontró exactamente la función login_view esperada. No se modificó ningún archivo.")

backup = Path("core/views.py.bak_login")
backup.write_text(text, encoding="utf-8")

path.write_text(text.replace(old, new, 1), encoding="utf-8")

print("OK: login_view actualizado.")
print(f"Backup creado en: {backup}")