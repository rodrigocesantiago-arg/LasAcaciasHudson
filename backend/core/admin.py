from django.contrib import admin
from .models import Lote, Integrante


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "apellido_familia",
        "email",
        "telefono",
        "activo",
    )

    search_fields = (
        "numero",
        "apellido_familia",
        "email",
    )

    list_filter = ("activo",)


@admin.register(Integrante)
class IntegranteAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "apellido",
        "lote",
        "parentesco",
        "activo",
    )

    search_fields = (
        "nombre",
        "apellido",
    )

    list_filter = (
        "parentesco",
        "activo",
    )