from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .administracion_views import superuser_required
from .models import Noticia


def _datos_post(request):
    return {
        "titulo": request.POST.get("titulo", "").strip(),
        "contenido": request.POST.get("contenido", "").strip(),
        "activa": request.POST.get("activa") == "on",
        "destacada": request.POST.get("destacada") == "on",
    }


@superuser_required
def administracion_noticias(request):
    estado = request.GET.get("estado", "").strip()
    q = request.GET.get("q", "").strip()

    noticias = Noticia.objects.select_related("autor").all()

    if estado == "activas":
        noticias = noticias.filter(activa=True)
    elif estado == "inactivas":
        noticias = noticias.filter(activa=False)
    elif estado == "destacadas":
        noticias = noticias.filter(destacada=True)
    else:
        estado = ""

    if q:
        noticias = noticias.filter(
            Q(titulo__icontains=q)
            | Q(contenido__icontains=q)
            | Q(autor__username__icontains=q)
        )

    noticias = noticias.order_by("-fecha_publicacion")

    return render(
        request,
        "core/administracion_noticias.html",
        {
            "noticias": noticias,
            "filtros": {"estado": estado, "q": q},
            "total": noticias.count(),
            "activas": noticias.filter(activa=True).count(),
            "destacadas": noticias.filter(destacada=True).count(),
        },
    )


@superuser_required
def administracion_noticia_nueva(request):
    if request.method == "POST":
        datos = _datos_post(request)

        if not datos["titulo"] or not datos["contenido"]:
            messages.error(request, "El título y el contenido son obligatorios.")
            return render(
                request,
                "core/administracion_noticia_form.html",
                {"modo": "nueva", "datos": datos},
            )

        noticia = Noticia.objects.create(
            titulo=datos["titulo"],
            contenido=datos["contenido"],
            imagen=request.FILES.get("imagen"),
            destacada=datos["destacada"],
            activa=datos["activa"],
            autor=request.user,
        )
        messages.success(request, "Noticia creada correctamente.")
        return redirect("administracion_noticia_editar", noticia_id=noticia.id)

    return render(
        request,
        "core/administracion_noticia_form.html",
        {"modo": "nueva", "datos": {"activa": True, "destacada": False}},
    )


@superuser_required
def administracion_noticia_editar(request, noticia_id):
    noticia = get_object_or_404(Noticia, pk=noticia_id)

    if request.method == "POST":
        datos = _datos_post(request)

        if not datos["titulo"] or not datos["contenido"]:
            messages.error(request, "El título y el contenido son obligatorios.")
            return render(
                request,
                "core/administracion_noticia_form.html",
                {"modo": "editar", "noticia": noticia, "datos": datos},
            )

        noticia.titulo = datos["titulo"]
        noticia.contenido = datos["contenido"]
        noticia.activa = datos["activa"]
        noticia.destacada = datos["destacada"]

        if request.FILES.get("imagen"):
            noticia.imagen = request.FILES["imagen"]

        if request.POST.get("eliminar_imagen") == "on":
            noticia.imagen = None

        noticia.save()
        messages.success(request, "Noticia actualizada correctamente.")
        return redirect("administracion_noticia_editar", noticia_id=noticia.id)

    return render(
        request,
        "core/administracion_noticia_form.html",
        {
            "modo": "editar",
            "noticia": noticia,
            "datos": {
                "titulo": noticia.titulo,
                "contenido": noticia.contenido,
                "activa": noticia.activa,
                "destacada": noticia.destacada,
            },
        },
    )


@superuser_required
def administracion_noticia_eliminar(request, noticia_id):
    noticia = get_object_or_404(Noticia, pk=noticia_id)

    if request.method == "POST":
        titulo = noticia.titulo
        noticia.delete()
        messages.success(request, f'La noticia "{titulo}" fue eliminada.')
        return redirect("administracion_noticias")

    return redirect("administracion_noticia_editar", noticia_id=noticia.id)