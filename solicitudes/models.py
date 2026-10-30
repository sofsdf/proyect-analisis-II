from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from convocatorias.models import Convocatoria

class Solicitud(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Asignación'),
        ('EN_REVISION', 'En Revisión por Comité'),
        ('PENDIENTE_AUTORIZACION_FINAL', 'Pendiente de Autorización Final'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    # --- Relaciones Principales ---
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

    # --- Requerimiento 2: Doble firma para montos mayores a Q10,000 ---
    monto_solicitado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Monto de la beca solicitada. Si supera Q10,000 requiere doble aprobación."
    )

    # 1. Primera Aprobación (Evaluador Técnico)
    evaluador = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='solicitudes_asignadas',
        help_text="Miembro del comité evaluador asignado (Evaluador Técnico)"
    )
    fecha_evaluacion_tecnica = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha y hora de la aprobación técnica"
    )

    # 2. Segunda Aprobación (Autoridad Autorizadora / Admin)
    autorizador_final = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='autorizaciones_finales',
        help_text="Autoridad autorizadora responsable de la firma final para montos > Q10,000"
    )
    fecha_autorizacion_final = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha y hora de la autorización final"
    )

    estado = models.CharField(max_length=30, choices=ESTADOS, default='PENDIENTE')
    observaciones = models.TextField(
        blank=True, 
        null=True, 
        help_text="Resultado y comentarios de la evaluación"
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

    # --- Requerimiento 3: Auditoría automática e inmutable ---
    history = HistoricalRecords()

    class Meta:
        ordering = ['-fecha_postulacion']

    @property
    def requiere_doble_firma(self):
        """Regla de negocio: Montos superiores a Q10,000 requieren dos autorizaciones."""
        return self.monto_solicitado > 10000

    def clean(self):
        """
        Validación de negocio: Impide que la misma persona complete ambas aprobaciones 
        cuando la solicitud requiera doble firma (> Q10,000).
        """
        super().clean()
        if self.requiere_doble_firma:
            if self.evaluador and self.autorizador_final:
                if self.evaluador == self.autorizador_final:
                    raise ValidationError(
                        "El evaluador técnico y la autoridad autorizadora no pueden ser la misma persona para solicitudes mayores a Q10,000."
                    )

    def __str__(self):
        return f"Solicitud #{self.id} - {self.estudiante} ({self.get_estado_display()})"


class AuditoriaSolicitud(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='historial_cambios')
    usuario = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        nombre_usuario = self.usuario.username if self.usuario else "Sistema"
        return f"{nombre_usuario} - {self.accion} ({self.fecha.strftime('%d/%m/%Y %H:%M')})"


class Notificacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones')
    solicitud = models.ForeignKey('Solicitud', on_delete=models.CASCADE, related_name='notificaciones', null=True, blank=True)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Notificación para {self.usuario.username} - Leída: {self.leida}"