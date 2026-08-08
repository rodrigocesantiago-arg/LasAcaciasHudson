from django import forms
from .models import ReservaSUM


class ReservaSUMForm(forms.ModelForm):

    class Meta:
        model = ReservaSUM

        fields = [
            "fecha",
            "turno",
            "cantidad_personas",
            "observaciones",
        ]

        widgets = {

            "fecha": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "turno": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "cantidad_personas": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),

            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Información adicional sobre la reserva..."
                }
            ),
        }