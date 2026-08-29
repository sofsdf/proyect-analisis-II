from django.db import models
from django.conf import settings


class Convocatoria(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    requisitos = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_cierre = models.DateField()
    publicada = models.BooleanField(default=False)
    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['-fecha_inicio']