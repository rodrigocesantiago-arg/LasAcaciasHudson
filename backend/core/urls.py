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
        "logout/",
        views.logout_view,
        name="logout"
    ),
]