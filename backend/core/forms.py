from django import forms

from .models import (
    Encomienda,
    Integrante,
    InvitadoFrecuente,
    Lote,
    Reclamo,
    ReservaSUM,
    SolicitudModificacionFamilia,
    Visita,
)


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
                    "placeholder": "Información adicional sobre la reserva...",
                }
            ),
        }


class SolicitudModificacionFamiliaForm(forms.ModelForm):

    class Meta:
        model = SolicitudModificacionFamilia

        fields = [
            "tipo",
            "integrante",
            "campo_modificar",
            "nuevo_valor",
            "nuevo_nombre",
            "nuevo_apellido",
            "nueva_fecha_nacimiento",
            "nuevo_parentesco",
            "nuevo_email",
            "nuevo_telefono",
            "detalle",
        ]

        widgets = {
            "tipo": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_tipo",
                }
            ),
            "integrante": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "campo_modificar": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "nuevo_valor": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ingresá el nuevo valor",
                }
            ),
            "nuevo_nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "nuevo_apellido": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "nueva_fecha_nacimiento": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "nuevo_parentesco": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Hijo, Cónyuge, Titular",
                }
            ),
            "nuevo_email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "nuevo_telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "detalle": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Comentario adicional para Administración",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        lote = kwargs.pop("lote", None)
        super().__init__(*args, **kwargs)

        if lote is not None:
            self.fields["integrante"].queryset = lote.integrantes.all()

        self.fields["integrante"].required = False
        self.fields["campo_modificar"].required = False
        self.fields["nuevo_valor"].required = False
        self.fields["nuevo_nombre"].required = False
        self.fields["nuevo_apellido"].required = False
        self.fields["nueva_fecha_nacimiento"].required = False
        self.fields["nuevo_parentesco"].required = False
        self.fields["nuevo_email"].required = False
        self.fields["nuevo_telefono"].required = False
        self.fields["detalle"].required = False


class ReclamoForm(forms.ModelForm):

    class Meta:
        model = Reclamo

        fields = [
            "categoria",
            "asunto",
            "descripcion",
        ]

        widgets = {
            "categoria": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "asunto": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Luminaria apagada en calle principal",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Describí el problema con el mayor detalle posible...",
                }
            ),
        }


class InvitadoFrecuenteForm(forms.ModelForm):

    class Meta:
        model = InvitadoFrecuente

        fields = [
            "nombre",
            "apellido",
            "dni",
            "patente",
            "observaciones",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido": forms.TextInput(attrs={"class": "form-control"}),
            "dni": forms.TextInput(attrs={"class": "form-control"}),
            "patente": forms.TextInput(attrs={"class": "form-control"}),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }


class VisitaForm(forms.ModelForm):

    class Meta:
        model = Visita

        fields = [
            "invitado",
            "nombre",
            "apellido",
            "dni",
            "patente",
            "fecha",
            "evento",
            "observaciones",
        ]

        widgets = {
            "invitado": forms.Select(attrs={"class": "form-select"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido": forms.TextInput(attrs={"class": "form-control"}),
            "dni": forms.TextInput(attrs={"class": "form-control"}),
            "patente": forms.TextInput(attrs={"class": "form-control"}),
            "fecha": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "evento": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Cumpleaños, visita familiar, proveedor",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        lote = kwargs.pop("lote", None)
        super().__init__(*args, **kwargs)

        if lote is not None:
            self.fields["invitado"].queryset = (
                InvitadoFrecuente.objects.filter(
                    lote=lote,
                    activo=True,
                )
            )

        self.fields["invitado"].required = False


class VisitaEspontaneaForm(forms.ModelForm):

    class Meta:
        model = Visita

        fields = [
            "lote",
            "nombre",
            "apellido",
            "dni",
            "patente",
            "evento",
            "observaciones",
        ]

        labels = {
            "lote": "Lote al que visita",
            "evento": "Motivo de la visita",
        }

        widgets = {
            "lote": forms.Select(attrs={"class": "form-select form-select-lg"}),
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                }
            ),
            "apellido": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                }
            ),
            "dni": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                }
            ),
            "patente": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                    "placeholder": "Opcional",
                }
            ),
            "evento": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: visita familiar, proveedor, servicio técnico",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observaciones opcionales",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["lote"].queryset = Lote.objects.filter(
            activo=True
        ).order_by("numero")

        self.fields["lote"].empty_label = "Seleccioná el lote"

    def clean_patente(self):
        return self.cleaned_data.get("patente", "").strip().upper()



class EncomiendaForm(forms.ModelForm):

    class Meta:
        model = Encomienda

        fields = [
            "lote",
            "remitente",
            "descripcion",
            "observaciones",
        ]

        labels = {
            "lote": "Lote destinatario",
            "remitente": "Empresa / Remitente",
            "descripcion": "Descripción del paquete",
            "observaciones": "Observaciones",
        }

        widgets = {
            "lote": forms.Select(
                attrs={
                    "class": "form-select form-select-lg",
                }
            ),
            "remitente": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Mercado Libre, Correo Argentino, Andreani",
                    "autocomplete": "off",
                }
            ),
            "descripcion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Caja mediana, sobre, paquete",
                    "autocomplete": "off",
                }
            ),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Observaciones opcionales",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["lote"].queryset = Lote.objects.filter(
            activo=True
        ).order_by("numero")

        self.fields["lote"].empty_label = "Seleccioná el lote"


class EntregaEncomiendaForm(forms.Form):

    TIPO_RETIRO = [
        ("familia", "Miembro de la familia"),
        ("otro", "Otra persona"),
    ]

    tipo_retiro = forms.ChoiceField(
        label="Quién retira",
        choices=TIPO_RETIRO,
        widget=forms.RadioSelect(),
        initial="familia",
    )

    integrante = forms.ModelChoiceField(
        label="Miembro de la familia",
        queryset=Integrante.objects.none(),
        required=False,
        empty_label="Seleccioná una persona de la familia",
        widget=forms.Select(
            attrs={
                "class": "form-select form-select-lg",
            }
        ),
    )

    otro_nombre = forms.CharField(
        label="Apellido y nombre",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Ej: Pérez Juan",
                "autocomplete": "off",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        lote = kwargs.pop("lote", None)
        super().__init__(*args, **kwargs)

        if lote is not None:
            self.fields["integrante"].queryset = Integrante.objects.filter(
                lote=lote,
                activo=True,
            ).order_by(
                "apellido",
                "nombre",
            )

    def clean(self):
        cleaned_data = super().clean()

        tipo_retiro = cleaned_data.get("tipo_retiro")
        integrante = cleaned_data.get("integrante")
        otro_nombre = (cleaned_data.get("otro_nombre") or "").strip()

        if tipo_retiro == "familia" and not integrante:
            self.add_error(
                "integrante",
                "Seleccioná qué integrante de la familia retira la encomienda.",
            )

        if tipo_retiro == "otro" and not otro_nombre:
            self.add_error(
                "otro_nombre",
                "Ingresá el apellido y nombre de la persona que retira.",
            )

        return cleaned_data