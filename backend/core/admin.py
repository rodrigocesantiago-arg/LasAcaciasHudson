from django.contrib import admin
from .models import Integrante, Lote, Noticia


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "apellido_familia",
        "usuario",
        "activo",
    )

    search_fields = (
        "numero",
        "apellido_familia",
    )


@admin.register(Integrante)
class IntegranteAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "apellido",
        "lote",
        "parentesco",
        "activo",
    )

    list_filter = (
        "parentesco",
        "activo",
    )

    search_fields = (
        "nombre",
        "apellido",
    )


@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "fecha_publicacion",
        "destacada",
        "activa",
        "autor",
    )

    list_filter = (
        "destacada",
        "activa",
    )

    search_fields = (
        "titulo",
        "contenido",
    )

    readonly_fields = (
        "fecha_publicacion",
    )