from django.contrib import admin

from .models import (
    Integrante,
    Lote,
    Noticia,
    ReservaSUM,
    SolicitudModificacionFamilia,
)


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
        "apellido",
        "nombre",
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


@admin.register(ReservaSUM)
class ReservaSUMAdmin(admin.ModelAdmin):
    list_display = (
        "fecha",
        "turno",
        "lote",
        "cantidad_personas",
        "estado",
        "fecha_creacion",
    )

    list_filter = (
        "turno",
        "estado",
        "fecha",
    )

    search_fields = (
        "lote__numero",
        "lote__apellido_familia",
    )

    readonly_fields = (
        "fecha_creacion",
    )


@admin.register(SolicitudModificacionFamilia)
class SolicitudModificacionFamiliaAdmin(admin.ModelAdmin):
    list_display = (
        "fecha_creacion",
        "lote",
        "tipo",
        "integrante",
        "estado",
        "aplicada",
    )

    list_filter = (
        "tipo",
        "estado",
        "aplicada",
        "fecha_creacion",
    )

    search_fields = (
        "lote__numero",
        "lote__apellido_familia",
        "integrante__nombre",
        "integrante__apellido",
        "detalle",
        "nuevo_valor",
    )

    readonly_fields = (
        "fecha_creacion",
        "aplicada",
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.estado == "aprobada" and not obj.aplicada:
            obj.aplicar_cambio()