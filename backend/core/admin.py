from django.contrib import admin
from django.utils import timezone

from .models import (
    ContactoUtil,
    Documento,
    Encomienda,
    Integrante,
    Lote,
    Noticia,
    Reclamo,
    ReservaSUM,
    SolicitudModificacionFamilia,
)


# -------------------------------------------------
# LOTES
# -------------------------------------------------

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

    list_filter = (
        "activo",
    )


# -------------------------------------------------
# INTEGRANTES
# -------------------------------------------------

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
        "lote__numero",
        "lote__apellido_familia",
    )


# -------------------------------------------------
# NOTICIAS
# -------------------------------------------------

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


# -------------------------------------------------
# RESERVAS SUM
# -------------------------------------------------

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


# -------------------------------------------------
# SOLICITUDES DE MODIFICACIÓN DE FAMILIA
# -------------------------------------------------

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
        super().save_model(
            request,
            obj,
            form,
            change
        )

        if (
            obj.estado == "aprobada"
            and not obj.aplicada
        ):
            obj.aplicar_cambio()


# -------------------------------------------------
# RECLAMOS
# -------------------------------------------------

@admin.register(Reclamo)
class ReclamoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fecha_creacion",
        "lote",
        "categoria",
        "asunto",
        "estado",
        "fecha_actualizacion",
    )

    list_editable = (
        "estado",
    )

    list_filter = (
        "estado",
        "categoria",
        "fecha_creacion",
    )

    search_fields = (
        "asunto",
        "descripcion",
        "lote__numero",
        "lote__apellido_familia",
    )

    readonly_fields = (
        "lote",
        "categoria",
        "asunto",
        "descripcion",
        "fecha_creacion",
        "fecha_actualizacion",
    )

    fieldsets = (
        (
            "Datos del reclamo",
            {
                "fields": (
                    "lote",
                    "categoria",
                    "asunto",
                    "descripcion",
                    "fecha_creacion",
                )
            },
        ),
        (
            "Respuesta de Administración",
            {
                "fields": (
                    "estado",
                    "respuesta_administracion",
                ),
                "description": (
                    "Actualizá el estado y escribí aquí la respuesta "
                    "que verá el vecino en su portal."
                ),
            },
        ),
        (
            "Seguimiento",
            {
                "fields": (
                    "fecha_actualizacion",
                )
            },
        ),
    )


# -------------------------------------------------
# ENCOMIENDAS
# -------------------------------------------------

@admin.register(Encomienda)
class EncomiendaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fecha_recepcion",
        "lote",
        "remitente",
        "estado",
        "retirado_por",
        "fecha_entrega",
    )

    list_editable = (
        "estado",
    )

    list_filter = (
        "estado",
        "fecha_recepcion",
    )

    search_fields = (
        "lote__numero",
        "lote__apellido_familia",
        "remitente",
        "descripcion",
        "retirado_por",
    )

    readonly_fields = (
        "fecha_recepcion",
        "fecha_entrega",
    )

    fieldsets = (
        (
            "Datos de la encomienda",
            {
                "fields": (
                    "lote",
                    "remitente",
                    "descripcion",
                    "fecha_recepcion",
                )
            },
        ),
        (
            "Entrega",
            {
                "fields": (
                    "estado",
                    "retirado_por",
                    "fecha_entrega",
                ),
                "description": (
                    "Cuando la encomienda pase a estado Entregada, "
                    "la fecha y hora de entrega se completarán automáticamente."
                ),
            },
        ),
        (
            "Observaciones",
            {
                "fields": (
                    "observaciones",
                )
            },
        ),
    )

    def save_model(self, request, obj, form, change):

        if obj.estado == "entregada":
            if not obj.fecha_entrega:
                obj.fecha_entrega = timezone.now()
        else:
            obj.fecha_entrega = None

        super().save_model(
            request,
            obj,
            form,
            change
        )


# -------------------------------------------------
# DOCUMENTOS
# -------------------------------------------------

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "categoria",
        "fecha_publicacion",
        "activo",
    )

    list_editable = (
        "activo",
    )

    list_filter = (
        "categoria",
        "activo",
        "fecha_publicacion",
    )

    search_fields = (
        "titulo",
        "descripcion",
    )

    readonly_fields = (
        "fecha_publicacion",
    )

    fieldsets = (
        (
            "Datos del documento",
            {
                "fields": (
                    "titulo",
                    "descripcion",
                    "categoria",
                    "archivo",
                )
            },
        ),
        (
            "Publicación",
            {
                "fields": (
                    "activo",
                    "fecha_publicacion",
                ),
                "description": (
                    "Si el documento está activo, será visible "
                    "para los vecinos en Comunidad360."
                ),
            },
        ),
    )


# -------------------------------------------------
# CONTACTOS ÚTILES
# -------------------------------------------------

@admin.register(ContactoUtil)
class ContactoUtilAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "categoria",
        "telefono",
        "whatsapp",
        "orden",
        "activo",
    )

    list_editable = (
        "orden",
        "activo",
    )

    list_filter = (
        "categoria",
        "activo",
    )

    search_fields = (
        "nombre",
        "descripcion",
        "telefono",
        "whatsapp",
    )

    fieldsets = (
        (
            "Datos del contacto",
            {
                "fields": (
                    "categoria",
                    "nombre",
                    "descripcion",
                )
            },
        ),
        (
            "Contacto",
            {
                "fields": (
                    "telefono",
                    "whatsapp",
                )
            },
        ),
        (
            "Publicación",
            {
                "fields": (
                    "orden",
                    "activo",
                ),
                "description": (
                    "El campo Orden define la posición del contacto "
                    "en el listado. Los números más bajos aparecen primero."
                ),
            },
        ),
    )