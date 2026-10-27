from django.db import models
from django.conf import settings
from convocatorias.models import Convocatoria
from django.contrib.auth import get_user_model

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

    # --- NUEVO: Requerimiento de aprobación para montos mayores a Q10,000 ---
    monto_solicitado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Monto de la beca solicitada. Si supera Q10,000 requiere doble aprobación."
    )

    # --- HU-07: Resolución final del Administrador ---
    resolucion_final = models.CharField(
        max_length=20,
        choices=[('APROBADA', 'Aprobada'), ('RECHAZADA', 'Rechazada')],
        null=True,
        blank=True,
        help_text="Decisión final del Administrador"
    )
    comentarios_admin = models.TextField(
        blank=True,
        null=True,
        help_text="Justificación de la resolución final"
    )

    class Meta:
        ordering = ['-fecha_postulacion']

    def __str__(self):
        return f"Solicitud #{self.id} - {self.estudiante} ({self.get_estado_display()})"

class AuditoriaSolicitud(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='historial_cambios')
    usuario = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.accion} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"