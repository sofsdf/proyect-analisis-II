from django.db import models
from django.conf import settings
from convocatorias.models import Convocatoria

class Solicitud(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Asignación'),
        ('EN_REVISION', 'En Revisión por Comité'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    # Usamos settings.AUTH_USER_MODEL en lugar de User directamente
    estudiante = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='solicitudes'
    )
    convocatoria = models.ForeignKey(
        Convocatoria, 
        on_delete=models.CASCADE, 
        related_name='solicitudes'
    )
    pdf_requisitos = models.FileField(upload_to='requisitos_pdfs/')
    fecha_postulacion = models.DateTimeField(auto_now_add=True)

    evaluador = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='solicitudes_asignadas',
        help_text="Miembro del comité evaluador asignado"
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    observaciones = models.TextField(
        blank=True, 
        null=True, 
        help_text="Resultado y comentarios de la evaluación"
    )

    class Meta:
        ordering = ['-fecha_postulacion']

    def __str__(self):
        return f"Solicitud #{self.id} - {self.estudiante} ({self.get_estado_display()})"