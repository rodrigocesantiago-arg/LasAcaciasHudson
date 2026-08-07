from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("portal/", views.portal, name="portal"),
    path("logout/", views.logout_view, name="logout"),
]