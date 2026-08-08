from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("portal/", views.portal, name="portal"),
    path("noticias/", views.noticias_view, name="noticias"),
    path("reservar-sum/", views.reservar_sum, name="reservar_sum"),
    path("logout/", views.logout_view, name="logout"),
]