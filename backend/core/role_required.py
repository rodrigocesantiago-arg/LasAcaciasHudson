from functools import wraps

from django.shortcuts import redirect


def _redirect_segun_rol(request):
    if not request.user.is_authenticated:
        return redirect("home")
    if request.user.is_superuser:
        return redirect("administracion_dashboard")
    if request.user.is_staff:
        return redirect("seguridad_dashboard")
    return redirect("portal")


def administrador_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("home")
        if not request.user.is_superuser:
            return _redirect_segun_rol(request)
        return view_func(request, *args, **kwargs)
    return wrapped


def porteria_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("home")
        if request.user.is_superuser or not request.user.is_staff:
            return _redirect_segun_rol(request)
        return view_func(request, *args, **kwargs)
    return wrapped


def vecino_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("home")
        if request.user.is_staff or request.user.is_superuser:
            return _redirect_segun_rol(request)
        return view_func(request, *args, **kwargs)
    return wrapped