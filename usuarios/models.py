from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ESTUDIANTE = 'ESTUDIANTE', 'Estudiante'
        ADMIN = 'ADMIN', 'Administrador'
        EVALUADOR = 'EVALUADOR', 'Evaluador'

    email = models.EmailField('Correo electrónico', unique=True)
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.ESTUDIANTE,
        verbose_name='Rol'
    )
    carne = models.CharField('Carné / Matrícula', max_length=20, blank=True, null=True, unique=True)
    telefono = models.CharField('Teléfono', max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"