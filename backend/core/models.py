from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from django.utils.dateparse import parse_date


class Lote(models.Model):
    numero = models.PositiveIntegerField(unique=True)

    apellido_familia = models.CharField(
        "Apellido de la familia",
        max_length=100
    )

    email = models.EmailField(blank=True)

    telefono = models.CharField(
        max_length=30,
        blank=True
    )

    activo = models.BooleanField(default=True)

    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lote"
    )

    def __str__(self):
        return f"Lote {self.numero} - {self.apellido_familia}"


class Integrante(models.Model):
    lote = models.ForeignKey(
        Lote,
        on_delete=models.CASCADE,
        related_name="integrantes"
    )

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()

    parentesco = models.CharField(
        max_length=30,
        help_text="Titular, Cónyuge, Hijo, Hija, etc."
    )

    email = models.EmailField(blank=True)

    telefono = models.CharField(
        max_length=30,
        blank=True
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"


class Noticia(models.Model):
    titulo = models.CharField(
        "Título",
        max_length=200
    )

    contenido = models.TextField(
        "Contenido"
    )

    imagen = models.ImageField(
        "Imagen",
        upload_to="noticias/",
        blank=True,
        null=True
    )

    fecha_publicacion = models.DateTimeField(
        "Fecha de publicación",
        auto_now_add=True
    )

    destacada = models.BooleanField(
        "Noticia destacada",
        default=False
    )

    activa = models.BooleanField(
        "Noticia activa",
        default=True
    )

    autor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="noticias"
    )

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ["-fecha_publicacion"]
        verbose_name = "Noticia"
        verbose_name_plural = "Noticias"


class ReservaSUM(models.Model):

    TURNOS = [
        ("dia", "Turno Día"),
        ("noche", "Turno Noche"),
    ]

    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
    ]

    lote = models.ForeignKey(
        Lote,
        on_delete=models.CASCADE,
        related_name="reservas_sum"
    )

    solicitado_por = models.ForeignKey(
        Integrante,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reservas_sum_solicitadas",
        verbose_name="Solicitado por"
    )

    fecha = models.DateField(
        "Fecha de reserva"
    )

    turno = models.CharField(
        "Turno",
        max_length=10,
        choices=TURNOS
    )

    cantidad_personas = models.PositiveIntegerField(
        "Cantidad estimada de personas",
        default=1
    )

    observaciones = models.TextField(
        "Observaciones",
        blank=True
    )

    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADOS,
        default="pendiente"
    )

    fecha_creacion = models.DateTimeField(
        "Fecha de creación",
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"SUM - Lote {self.lote.numero} - "
            f"{self.fecha} - {self.get_turno_display()}"
        )

    class Meta:
        ordering = ["fecha", "turno"]
        verbose_name = "Reserva del SUM"
        verbose_name_plural = "Reservas del SUM"

        constraints = [
            models.UniqueConstraint(
                fields=["fecha", "turno"],
                condition=~models.Q(estado="cancelada"),
                name="reserva_sum_fecha_turno_activo_unico"
            )
        ]


class SolicitudModificacionFamilia(models.Model):

    TIPOS = [
        ("modificar", "Modificar datos"),
        ("alta", "Agregar integrante"),
        ("baja", "Dar de baja integrante"),
        ("otro", "Otro"),
    ]

    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("aprobada", "Aprobada"),
        ("rechazada", "Rechazada"),
    ]

    CAMPOS_MODIFICABLES = [
        ("nombre", "Nombre"),
        ("apellido", "Apellido"),
        ("fecha_nacimiento", "Fecha de nacimiento"),
        ("parentesco", "Parentesco"),
        ("email", "Email"),
        ("telefono", "Teléfono"),
    ]

    lote = models.ForeignKey(
        Lote,
        on_delete=models.CASCADE,
        related_name="solicitudes_familia"
    )

    integrante = models.ForeignKey(
        Integrante,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitudes_modificacion"
    )

    tipo = models.CharField(
        "Tipo de solicitud",
        max_length=20,
        choices=TIPOS
    )

    detalle = models.TextField(
        "Detalle / comentario",
        blank=True
    )

    campo_modificar = models.CharField(
        "Dato a modificar",
        max_length=30,
        choices=CAMPOS_MODIFICABLES,
        blank=True
    )

    nuevo_valor = models.CharField(
        "Nuevo valor",
        max_length=255,
        blank=True
    )

    nuevo_nombre = models.CharField(
        "Nombre del nuevo integrante",
        max_length=100,
        blank=True
    )

    nuevo_apellido = models.CharField(
        "Apellido del nuevo integrante",
        max_length=100,
        blank=True
    )

    nueva_fecha_nacimiento = models.DateField(
        "Fecha de nacimiento del nuevo integrante",
        null=True,
        blank=True
    )

    nuevo_parentesco = models.CharField(
        "Parentesco del nuevo integrante",
        max_length=30,
        blank=True
    )

    nuevo_email = models.EmailField(
        "Email del nuevo integrante",
        blank=True
    )

    nuevo_telefono = models.CharField(
        "Teléfono del nuevo integrante",
        max_length=30,
        blank=True
    )

    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADOS,
        default="pendiente"
    )

    fecha_creacion = models.DateTimeField(
        "Fecha de creación",
        auto_now_add=True
    )

    respuesta_administracion = models.TextField(
        "Respuesta de administración",
        blank=True
    )

    aplicada = models.BooleanField(
        "Modificación aplicada",
        default=False
    )

    def clean(self):
        errores = {}

        if self.tipo == "modificar":
            if not self.integrante:
                errores["integrante"] = (
                    "Debe seleccionar el integrante a modificar."
                )

            if not self.campo_modificar:
                errores["campo_modificar"] = (
                    "Debe indicar qué dato desea modificar."
                )

            if not self.nuevo_valor:
                errores["nuevo_valor"] = (
                    "Debe indicar el nuevo valor."
                )

            if (
                self.campo_modificar == "email"
                and self.nuevo_valor
            ):
                try:
                    validate_email(self.nuevo_valor)
                except ValidationError:
                    errores["nuevo_valor"] = (
                        "Ingrese una dirección de email válida."
                    )

            if (
                self.campo_modificar == "fecha_nacimiento"
                and self.nuevo_valor
                and parse_date(self.nuevo_valor) is None
            ):
                errores["nuevo_valor"] = (
                    "Para la fecha use el formato AAAA-MM-DD."
                )

        elif self.tipo == "alta":
            if not self.nuevo_nombre:
                errores["nuevo_nombre"] = "Debe indicar el nombre."

            if not self.nuevo_apellido:
                errores["nuevo_apellido"] = "Debe indicar el apellido."

            if not self.nueva_fecha_nacimiento:
                errores["nueva_fecha_nacimiento"] = (
                    "Debe indicar la fecha de nacimiento."
                )

            if not self.nuevo_parentesco:
                errores["nuevo_parentesco"] = (
                    "Debe indicar el parentesco."
                )

        elif self.tipo == "baja":
            if not self.integrante:
                errores["integrante"] = (
                    "Debe seleccionar el integrante a dar de baja."
                )

        if errores:
            raise ValidationError(errores)

    def aplicar_cambio(self):
        if self.aplicada:
            return

        if self.estado != "aprobada":
            return

        if self.tipo == "modificar":
            integrante = self.integrante

            if self.campo_modificar == "fecha_nacimiento":
                valor = parse_date(self.nuevo_valor)
            else:
                valor = self.nuevo_valor

            setattr(
                integrante,
                self.campo_modificar,
                valor
            )

            integrante.save()

        elif self.tipo == "alta":
            integrante = Integrante.objects.create(
                lote=self.lote,
                nombre=self.nuevo_nombre,
                apellido=self.nuevo_apellido,
                fecha_nacimiento=self.nueva_fecha_nacimiento,
                parentesco=self.nuevo_parentesco,
                email=self.nuevo_email,
                telefono=self.nuevo_telefono,
                activo=True
            )

            self.integrante = integrante

        elif self.tipo == "baja":
            self.integrante.activo = False
            self.integrante.save()

        elif self.tipo == "otro":
            return

        self.aplicada = True

        self.save(
            update_fields=[
                "aplicada",
                "integrante",
            ]
        )

    def __str__(self):
        return (
            f"Lote {self.lote.numero} - "
            f"{self.get_tipo_display()} - "
            f"{self.get_estado_display()}"
        )

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name = "Solicitud de modificación familiar"
        verbose_name_plural = "Solicitudes de modificación familiar"


class Reclamo(models.Model):

    CATEGORIAS = [
        ("iluminacion", "Iluminación"),
        ("seguridad", "Seguridad"),
        ("calles", "Calles y circulación"),
        ("espacios_comunes", "Espacios comunes"),
        ("residuos", "Residuos"),
        ("mantenimiento", "Mantenimiento"),
        ("administracion", "Administración"),
        ("otro", "Otro"),
    ]

    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("en_proceso", "En proceso"),
        ("resuelto", "Resuelto"),
        ("rechazado", "Rechazado"),
    ]

    lote = models.ForeignKey(
        Lote,
        on_delete=models.CASCADE,
        related_name="reclamos"
    )

    categoria = models.CharField(
        "Categoría",
        max_length=30,
        choices=CATEGORIAS
    )

    asunto = models.CharField(
        "Asunto",
        max_length=150
    )

    descripcion = models.TextField(
        "Descripción"
    )

    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADOS,
        default="pendiente"
    )

    fecha_creacion = models.DateTimeField(
        "Fecha de creación",
        auto_now_add=True
    )

    fecha_actualizacion = models.DateTimeField(
        "Última actualización",
        auto_now=True
    )

    respuesta_administracion = models.TextField(
        "Respuesta de Administración",
        blank=True
    )

    def __str__(self):
        return (
            f"Reclamo #{self.id} - "
            f"Lote {self.lote.numero} - "
            f"{self.asunto}"
        )

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name = "Reclamo"
        verbose_name_plural = "Reclamos"


class Encomienda(models.Model):

    ESTADOS = [
        ("pendiente", "Pendiente de retiro"),
        ("entregada", "Entregada"),
    ]

    lote = models.ForeignKey(
        Lote,
        on_delete=models.CASCADE,
        related_name="encomiendas"
    )

    remitente = models.CharField(
        "Empresa / Remitente",
        max_length=150
    )

    descripcion = models.CharField(
        "Descripción del paquete",
        max_length=255,
        blank=True
    )

    fecha_recepcion = models.DateTimeField(
        "Fecha y hora de recepción",
        auto_now_add=True
    )

    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADOS,
        default="pendiente"
    )

    fecha_entrega = models.DateTimeField(
        "Fecha y hora de entrega",
        null=True,
        blank=True
    )

    retirado_por = models.CharField(
        "Retirado por",
        max_length=150,
        blank=True
    )

    observaciones = models.TextField(
        "Observaciones",
        blank=True
    )

    def __str__(self):
        return (
            f"Encomienda #{self.id} - "
            f"Lote {self.lote.numero} - "
            f"{self.remitente}"
        )

    class Meta:
        ordering = ["-fecha_recepcion"]
        verbose_name = "Encomienda"
        verbose_name_plural = "Encomiendas"


class Documento(models.Model):

    CATEGORIAS = [
        ("reglamento", "Reglamento"),
        ("administracion", "Administración"),
        ("sum", "SUM"),
        ("seguridad", "Seguridad"),
        ("obras", "Obras"),
        ("expensas", "Expensas"),
        ("otro", "Otro"),
    ]

    titulo = models.CharField(
        "Título",
        max_length=200
    )

    descripcion = models.TextField(
        "Descripción",
        blank=True
    )

    categoria = models.CharField(
        "Categoría",
        max_length=30,
        choices=CATEGORIAS
    )

    archivo = models.FileField(
        "Archivo",
        upload_to="documentos/"
    )

    fecha_publicacion = models.DateTimeField(
        "Fecha de publicación",
        auto_now_add=True
    )

    activo = models.BooleanField(
        "Visible para los vecinos",
        default=True
    )

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ["-fecha_publicacion"]
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"


class ContactoUtil(models.Model):

    CATEGORIAS = [
        ("seguridad", "Seguridad"),
        ("emergencias", "Emergencias"),
        ("administracion", "Administración"),
        ("mantenimiento", "Mantenimiento"),
        ("servicios", "Servicios"),
        ("otro", "Otro"),
    ]

    categoria = models.CharField(
        "Categoría",
        max_length=30,
        choices=CATEGORIAS
    )

    nombre = models.CharField(
        "Nombre",
        max_length=150
    )

    descripcion = models.CharField(
        "Descripción",
        max_length=255,
        blank=True
    )

    telefono = models.CharField(
        "Teléfono",
        max_length=50
    )

    whatsapp = models.CharField(
        "WhatsApp",
        max_length=50,
        blank=True
    )

    orden = models.PositiveIntegerField(
        "Orden",
        default=0
    )

    activo = models.BooleanField(
        "Visible para los vecinos",
        default=True
    )

    def __str__(self):
        return f"{self.get_categoria_display()} - {self.nombre}"

    class Meta:
        ordering = [
            "orden",
            "categoria",
            "nombre",
        ]
        verbose_name = "Contacto útil"
        verbose_name_plural = "Contactos útiles"


# -------------------------------------------------
# VISITAS
# -------------------------------------------------

class InvitadoFrecuente(models.Model):
    lote = models.ForeignKey(
        Lote,
        on_delete=models.CASCADE,
        related_name="invitados_frecuentes"
    )
    nombre = models.CharField("Nombre", max_length=100)
    apellido = models.CharField("Apellido", max_length=100)
    dni = models.CharField("DNI", max_length=20)
    patente = models.CharField("Patente", max_length=20, blank=True)
    observaciones = models.TextField("Observaciones", blank=True)
    activo = models.BooleanField("Activo", default=True)

    def __str__(self):
        return f"{self.apellido}, {self.nombre} - DNI {self.dni}"

    class Meta:
        ordering = ["apellido", "nombre"]
        verbose_name = "Invitado frecuente"
        verbose_name_plural = "Invitados frecuentes"


class Visita(models.Model):
    ESTADOS = [
        ("autorizada", "Autorizada"),
        ("cancelada", "Cancelada"),
    ]

    lote = models.ForeignKey(
        Lote,
        on_delete=models.CASCADE,
        related_name="visitas"
    )
    invitado = models.ForeignKey(
        InvitadoFrecuente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visitas"
    )
    nombre = models.CharField("Nombre", max_length=100)
    apellido = models.CharField("Apellido", max_length=100)
    dni = models.CharField("DNI", max_length=20)
    patente = models.CharField("Patente", max_length=20, blank=True)
    fecha = models.DateField("Fecha de visita")
    evento = models.CharField("Evento / Motivo", max_length=150, blank=True)
    observaciones = models.TextField("Observaciones", blank=True)
    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=ESTADOS,
        default="autorizada"
    )
    fecha_creacion = models.DateTimeField("Fecha de creación", auto_now_add=True)
    fecha_hora_ingreso = models.DateTimeField(
        "Fecha y hora de ingreso",
        null=True,
        blank=True
    )
    fecha_hora_salida = models.DateTimeField(
        "Fecha y hora de salida",
        null=True,
        blank=True
    )

    def __str__(self):
        return (
            f"{self.apellido}, {self.nombre} - "
            f"Lote {self.lote.numero} - {self.fecha}"
        )

    class Meta:
        ordering = ["-fecha", "-fecha_creacion"]
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"