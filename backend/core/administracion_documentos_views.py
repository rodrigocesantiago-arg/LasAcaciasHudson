from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .administracion_views import superuser_required
from .models import Documento


def _datos_post(request):
    return {
        "titulo": request.POST.get("titulo", "").strip(),
        "descripcion": request.POST.get("descripcion", "").strip(),
        "categoria": request.POST.get("categoria", "").strip(),
        "activo": request.POST.get("activo") == "on",
    }


@superuser_required
def administracion_documentos(request):
    categoria = request.GET.get("categoria", "").strip()
    estado = request.GET.get("estado", "").strip()
    q = request.GET.get("q", "").strip()

    documentos = Documento.objects.all()
    categorias_validas = dict(Documento.CATEGORIAS)

    if categoria in categorias_validas:
        documentos = documentos.filter(categoria=categoria)
    else:
        categoria = ""

    if estado == "activos":
        documentos = documentos.filter(activo=True)
    elif estado == "inactivos":
        documentos = documentos.filter(activo=False)
    else:
        estado = ""

    if q:
        documentos = documentos.filter(
            Q(titulo__icontains=q) | Q(descripcion__icontains=q)
        )

    documentos = documentos.order_by("-fecha_publicacion")

    return render(
        request,
        "core/administracion_documentos.html",
        {
            "documentos": documentos,
            "categorias": Documento.CATEGORIAS,
            "filtros": {"categoria": categoria, "estado": estado, "q": q},
            "total": documentos.count(),
            "activos": documentos.filter(activo=True).count(),
            "inactivos": documentos.filter(activo=False).count(),
        },
    )


@superuser_required
def administracion_documento_nuevo(request):
    if request.method == "POST":
        datos = _datos_post(request)
        archivo = request.FILES.get("archivo")

        if (
            not datos["titulo"]
            or datos["categoria"] not in dict(Documento.CATEGORIAS)
            or not archivo
        ):
            messages.error(request, "Título, categoría y archivo son obligatorios.")
            return render(
                request,
                "core/administracion_documento_form.html",
                {
                    "modo": "nuevo",
                    "datos": datos,
                    "categorias": Documento.CATEGORIAS,
                },
            )

        documento = Documento.objects.create(
            titulo=datos["titulo"],
            descripcion=datos["descripcion"],
            categoria=datos["categoria"],
            archivo=archivo,
            activo=datos["activo"],
        )
        messages.success(request, "Documento publicado correctamente.")
        return redirect(
            "administracion_documento_editar",
            documento_id=documento.id,
        )

    return render(
        request,
        "core/administracion_documento_form.html",
        {
            "modo": "nuevo",
            "datos": {"activo": True},
            "categorias": Documento.CATEGORIAS,
        },
    )


@superuser_required
def administracion_documento_editar(request, documento_id):
    documento = get_object_or_404(Documento, pk=documento_id)

    if request.method == "POST":
        datos = _datos_post(request)

        if (
            not datos["titulo"]
            or datos["categoria"] not in dict(Documento.CATEGORIAS)
        ):
            messages.error(request, "Título y categoría son obligatorios.")
            return render(
                request,
                "core/administracion_documento_form.html",
                {
                    "modo": "editar",
                    "documento": documento,
                    "datos": datos,
                    "categorias": Documento.CATEGORIAS,
                },
            )

        documento.titulo = datos["titulo"]
        documento.descripcion = datos["descripcion"]
        documento.categoria = datos["categoria"]
        documento.activo = datos["activo"]

        if request.FILES.get("archivo"):
            documento.archivo = request.FILES["archivo"]

        documento.save()
        messages.success(request, "Documento actualizado correctamente.")
        return redirect(
            "administracion_documento_editar",
            documento_id=documento.id,
        )

    return render(
        request,
        "core/administracion_documento_form.html",
        {
            "modo": "editar",
            "documento": documento,
            "datos": {
                "titulo": documento.titulo,
                "descripcion": documento.descripcion,
                "categoria": documento.categoria,
                "activo": documento.activo,
            },
            "categorias": Documento.CATEGORIAS,
        },
    )


@superuser_required
def administracion_documento_eliminar(request, documento_id):
    documento = get_object_or_404(Documento, pk=documento_id)

    if request.method == "POST":
        titulo = documento.titulo
        documento.delete()
        messages.success(request, f'El documento "{titulo}" fue eliminado.')
        return redirect("administracion_documentos")

    return redirect(
        "administracion_documento_editar",
        documento_id=documento.id,
    )