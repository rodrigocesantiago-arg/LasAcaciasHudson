from django.urls import path

from . import views
from . import password_reset_views
from . import administracion_views


urlpatterns = [
    # -------------------------------------------------
    # HOME Y LOGIN
    # -------------------------------------------------
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),

    # -------------------------------------------------
    # RECUPERACIÓN DE CONTRASEÑA
    # -------------------------------------------------
    path(
        "recuperar-password/",
        password_reset_views.recuperar_password,
        name="recuperar_password"
    ),
    path(
        "recuperar-password/enviado/",
        password_reset_views.recuperar_password_enviado,
        name="recuperar_password_enviado"
    ),
    path(
        "recuperar-password/<uidb64>/<token>/",
        password_reset_views.restablecer_password,
        name="restablecer_password"
    ),
    path(
        "password-restaurada/",
        password_reset_views.password_restaurada,
        name="password_restaurada"
    ),

    # -------------------------------------------------
    # ADMINISTRACIÓN
    # -------------------------------------------------
    path(
        "administracion/",
        administracion_views.administracion_dashboard,
        name="administracion_dashboard"
    ),

    # -------------------------------------------------
    # PORTAL DEL VECINO
    # -------------------------------------------------
    path("portal/", views.portal, name="portal"),
    path("noticias/", views.noticias_view, name="noticias"),
    path("cumpleanios/", views.cumpleanios_view, name="cumpleanios"),

    # MI FAMILIA
    path("mi-familia/", views.mi_familia, name="mi_familia"),
    path(
        "mi-familia/solicitar-modificacion/",
        views.solicitar_modificacion_familia,
        name="solicitar_modificacion_familia"
    ),

    # -------------------------------------------------
    # SUM
    # -------------------------------------------------
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

    # -------------------------------------------------
    # RECLAMOS
    # -------------------------------------------------
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

    # -------------------------------------------------
    # ENCOMIENDAS DEL VECINO
    # -------------------------------------------------
    path(
        "mis-encomiendas/",
        views.mis_encomiendas,
        name="mis_encomiendas"
    ),

    # -------------------------------------------------
    # DOCUMENTOS Y CONTACTOS
    # -------------------------------------------------
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

    # -------------------------------------------------
    # CARGA MASIVA DE VISITAS
    # -------------------------------------------------
    path(
        "visitas/carga-masiva/",
        views.carga_masiva_visitas,
        name="carga_masiva_visitas"
    ),
    path(
        "visitas/carga-masiva/confirmar/",
        views.confirmar_carga_masiva_visitas,
        name="confirmar_carga_masiva_visitas"
    ),
    path(
        "visitas/carga-masiva/plantilla/",
        views.descargar_plantilla_visitas,
        name="descargar_plantilla_visitas"
    ),

    # -------------------------------------------------
    # SEGURIDAD / PORTERÍA
    # -------------------------------------------------
    path(
        "seguridad/",
        views.seguridad_dashboard,
        name="seguridad_dashboard"
    ),
    path(
        "seguridad/visitas/",
        views.seguridad_visitas,
        name="seguridad_visitas"
    ),
    path(
        "seguridad/historial/",
        views.historial_seguridad,
        name="historial_seguridad"
    ),
    path(
        "seguridad/visita-espontanea/",
        views.visita_espontanea,
        name="visita_espontanea"
    ),

    # ENCOMIENDAS DE PORTERÍA
    path(
        "seguridad/encomiendas/",
        views.seguridad_encomiendas,
        name="seguridad_encomiendas"
    ),
    path(
        "seguridad/encomiendas/nueva/",
        views.registrar_encomienda,
        name="registrar_encomienda"
    ),
    path(
        "seguridad/encomiendas/<int:encomienda_id>/entregar/",
        views.entregar_encomienda,
        name="entregar_encomienda"
    ),

    # INGRESO / SALIDA DE VISITAS
    path(
        "seguridad/visitas/<int:visita_id>/ingreso/",
        views.registrar_ingreso,
        name="registrar_ingreso"
    ),
    path(
        "seguridad/visitas/<int:visita_id>/salida/",
        views.registrar_salida,
        name="registrar_salida"
    ),

    # -------------------------------------------------
    # LOGOUT
    # -------------------------------------------------
    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),
]