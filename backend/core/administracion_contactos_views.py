from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .administracion_views import superuser_required
from .models import ContactoUtil


def _datos_post(request):
    orden_raw = request.POST.get("orden", "0").strip()
    try:
        orden = int(orden_raw)
        if orden < 0:
            raise ValueError
    except ValueError:
        orden = None

    return {
        "categoria": request.POST.get("categoria", "").strip(),
        "nombre": request.POST.get("nombre", "").strip(),
        "descripcion": request.POST.get("descripcion", "").strip(),
        "telefono": request.POST.get("telefono", "").strip(),
        "whatsapp": request.POST.get("whatsapp", "").strip(),
        "orden": orden,
        "orden_raw": orden_raw,
        "activo": request.POST.get("activo") == "on",
    }


@superuser_required
def administracion_contactos(request):
    categoria = request.GET.get("categoria", "").strip()
    estado = request.GET.get("estado", "").strip()
    q = request.GET.get("q", "").strip()

    contactos = ContactoUtil.objects.all()
    categorias_validas = dict(ContactoUtil.CATEGORIAS)

    if categoria in categorias_validas:
        contactos = contactos.filter(categoria=categoria)
    else:
        categoria = ""

    if estado == "activos":
        contactos = contactos.filter(activo=True)
    elif estado == "inactivos":
        contactos = contactos.filter(activo=False)
    else:
        estado = ""

    if q:
        contactos = contactos.filter(
            Q(nombre__icontains=q)
            | Q(descripcion__icontains=q)
            | Q(telefono__icontains=q)
            | Q(whatsapp__icontains=q)
        )

    contactos = contactos.order_by("orden", "categoria", "nombre")

    return render(
        request,
        "core/administracion_contactos.html",
        {
            "contactos": contactos,
            "categorias": ContactoUtil.CATEGORIAS,
            "filtros": {"categoria": categoria, "estado": estado, "q": q},
            "total": contactos.count(),
            "activos": contactos.filter(activo=True).count(),
            "inactivos": contactos.filter(activo=False).count(),
        },
    )


@superuser_required
def administracion_contacto_nuevo(request):
    if request.method == "POST":
        datos = _datos_post(request)

        if (
            datos["categoria"] not in dict(ContactoUtil.CATEGORIAS)
            or not datos["nombre"]
            or not datos["telefono"]
            or datos["orden"] is None
        ):
            messages.error(
                request,
                "Categoría, nombre, teléfono y un orden válido son obligatorios.",
            )
            return render(
                request,
                "core/administracion_contacto_form.html",
                {
                    "modo": "nuevo",
                    "datos": datos,
                    "categorias": ContactoUtil.CATEGORIAS,
                },
            )

        contacto = ContactoUtil.objects.create(
            categoria=datos["categoria"],
            nombre=datos["nombre"],
            descripcion=datos["descripcion"],
            telefono=datos["telefono"],
            whatsapp=datos["whatsapp"],
            orden=datos["orden"],
            activo=datos["activo"],
        )
        messages.success(request, "Contacto creado correctamente.")
        return redirect("administracion_contacto_editar", contacto_id=contacto.id)

    return render(
        request,
        "core/administracion_contacto_form.html",
        {
            "modo": "nuevo",
            "datos": {"activo": True, "orden": 0},
            "categorias": ContactoUtil.CATEGORIAS,
        },
    )


@superuser_required
def administracion_contacto_editar(request, contacto_id):
    contacto = get_object_or_404(ContactoUtil, pk=contacto_id)

    if request.method == "POST":
        datos = _datos_post(request)

        if (
            datos["categoria"] not in dict(ContactoUtil.CATEGORIAS)
            or not datos["nombre"]
            or not datos["telefono"]
            or datos["orden"] is None
        ):
            messages.error(
                request,
                "Categoría, nombre, teléfono y un orden válido son obligatorios.",
            )
            return render(
                request,
                "core/administracion_contacto_form.html",
                {
                    "modo": "editar",
                    "contacto": contacto,
                    "datos": datos,
                    "categorias": ContactoUtil.CATEGORIAS,
                },
            )

        contacto.categoria = datos["categoria"]
        contacto.nombre = datos["nombre"]
        contacto.descripcion = datos["descripcion"]
        contacto.telefono = datos["telefono"]
        contacto.whatsapp = datos["whatsapp"]
        contacto.orden = datos["orden"]
        contacto.activo = datos["activo"]
        contacto.save()

        messages.success(request, "Contacto actualizado correctamente.")
        return redirect("administracion_contacto_editar", contacto_id=contacto.id)

    return render(
        request,
        "core/administracion_contacto_form.html",
        {
            "modo": "editar",
            "contacto": contacto,
            "datos": {
                "categoria": contacto.categoria,
                "nombre": contacto.nombre,
                "descripcion": contacto.descripcion,
                "telefono": contacto.telefono,
                "whatsapp": contacto.whatsapp,
                "orden": contacto.orden,
                "activo": contacto.activo,
            },
            "categorias": ContactoUtil.CATEGORIAS,
        },
    )


@superuser_required
def administracion_contacto_eliminar(request, contacto_id):
    contacto = get_object_or_404(ContactoUtil, pk=contacto_id)

    if request.method == "POST":
        nombre = contacto.nombre
        contacto.delete()
        messages.success(request, f'El contacto "{nombre}" fue eliminado.')
        return redirect("administracion_contactos")

    return redirect("administracion_contacto_editar", contacto_id=contacto.id)