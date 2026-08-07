from django.db import models


class Lote(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    apellido_familia = models.CharField("Apellido de la familia", max_length=100)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    activo = models.BooleanField(default=True)

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