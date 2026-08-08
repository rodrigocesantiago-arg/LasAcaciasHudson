from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),

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
        "logout/",
        views.logout_view,
        name="logout"
    ),
]