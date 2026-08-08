from django.contrib.auth.models import User
from django.db import models


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
        return f"{self.nombre} {self.apellido}"


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