
from django import forms
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render

from .administracion_views import superuser_required
from .models import Lote


class NuevoLoteForm(forms.ModelForm):
    class Meta:
        model = Lote

        fields = [
            "numero",
            "apellido_familia",
            "email",
            "telefono",
            "activo",
        ]

        labels = {
            "numero": "Número de lote",
            "apellido_familia": "Apellido de la familia",
            "email": "Correo electrónico",
            "telefono": "Teléfono",
            "activo": "Lote activo",
        }

        widgets = {
            "numero": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
            "apellido_familia": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Apellido familiar",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "vecino@ejemplo.com",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Teléfono de contacto",
                }
            ),
            "activo": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean_numero(self):
        numero = self.cleaned_data["numero"]

        if numero < 1:
            raise forms.ValidationError(
                "El número de lote debe ser mayor que cero."
            )

        return numero

    def clean_apellido_familia(self):
        apellido = self.cleaned_data[
            "apellido_familia"
        ].strip()

        if not apellido:
            raise forms.ValidationError(
                "Ingresá el apellido de la familia."
            )

        return apellido


@superuser_required
def crear_lote(request):
    if request.method == "POST":
        formulario = NuevoLoteForm(request.POST)

        if formulario.is_valid():
            try:
                with transaction.atomic():
                    lote = formulario.save(commit=False)

                    # El alta del lote no crea usuarios.
                    # La invitación se enviará por separado.
                    lote.usuario = None
                    lote.save()

            except IntegrityError:
                formulario.add_error(
                    "numero",
                    "Ya existe un lote con ese número."
                )
            else:
                messages.success(
                    request,
                    f"El lote {lote.numero} se creó correctamente."
                )

                return redirect(
                    "administracion_lote_detalle",
                    lote_id=lote.id
                )

    else:
        formulario = NuevoLoteForm(
            initial={"activo": True}
        )

    return render(
        request,
        "core/administracion_lote_nuevo.html",
        {
            "formulario": formulario,
        }
    )
