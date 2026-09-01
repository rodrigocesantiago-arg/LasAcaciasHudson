from django.urls import path
from . import views


urlpatterns = [
    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "portal/",
        views.portal,
        name="portal"
    ),

    path(
        "noticias/",
        views.noticias_view,
        name="noticias"
    ),

    path(
        "cumpleanios/",
        views.cumpleanios_view,
        name="cumpleanios"
    ),

    path(
        "mi-familia/",
        views.mi_familia,
        name="mi_familia"
    ),

    path(
        "mi-familia/solicitar-modificacion/",
        views.solicitar_modificacion_familia,
        name="solicitar_modificacion_familia"
    ),

    path(
        "mis-reservas-sum/",
        views.mis_reservas_sum,
        name="mis_reservas_sum"
    ),

    path(
        "disponibilidad-sum/",
        views.disponibilidad_sum,
        name="disponibilidad_sum"
    ),

    path(
        "reservar-sum/",
        views.reservar_sum,
        name="reservar_sum"
    ),

    path(
        "cancelar-reserva-sum/<int:reserva_id>/",
        views.cancelar_reserva_sum,
        name="cancelar_reserva_sum"
    ),

    path(
        "reclamos/",
        views.mis_reclamos,
        name="mis_reclamos"
    ),

    path(
        "reclamos/nuevo/",
        views.nuevo_reclamo,
        name="nuevo_reclamo"
    ),

    path(
        "mis-encomiendas/",
        views.mis_encomiendas,
        name="mis_encomiendas"
    ),

    path(
        "documentos/",
        views.documentos_view,
        name="documentos"
    ),

    path(
        "contactos-utiles/",
        views.contactos_utiles,
        name="contactos_utiles"
    ),

    # -------------------------------------------------
    # VISITAS
    # -------------------------------------------------

    path(
        "visitas/",
        views.visitas_view,
        name="visitas"
    ),

    path(
        "visitas/autorizar/",
        views.autorizar_visita,
        name="autorizar_visita"
    ),

    path(
        "visitas/historial/",
        views.historial_visitas,
        name="historial_visitas"
    ),

    path(
        "visitas/agenda/",
        views.agenda_visitas,
        name="agenda_visitas"
    ),

    path(
        "visitas/invitados-frecuentes/",
        views.invitados_frecuentes,
        name="invitados_frecuentes"
    ),

    path(
        "visitas/invitados-frecuentes/nuevo/",
        views.nuevo_invitado_frecuente,
        name="nuevo_invitado_frecuente"
    ),

    path(
        "visitas/<int:visita_id>/cancelar/",
        views.cancelar_visita,
        name="cancelar_visita"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),
]