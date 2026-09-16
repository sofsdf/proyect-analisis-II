from django.db import models
from django.conf import settings

class Solicitud(models.Model):
    ESTADOS = [
        ('REVISION', 'En Revisión'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    # Relaciones (Foreign Keys)
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitudes')
    convocatoria = models.ForeignKey('convocatorias.Convocatoria', on_delete=models.CASCADE, related_name='solicitudes')
    
    # Atributos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='REVISION')
    promedio_actual = models.DecimalField(max_digits=5, decimal_places=2, help_text="Ejemplo: 85.50")

    def __str__(self):
        return f"Solicitud de {self.estudiante.email} - {self.estado}"


class Documento(models.Model):
    TIPOS_DOC = [
        ('DPI', 'DPI'),
        ('NOTAS', 'Certificado de Notas'),
        ('RECIBO', 'Recibo de Servicios'),
    ]

    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='documentos')
    tipo_documento = models.CharField(max_length=50, choices=TIPOS_DOC)
    archivo_pdf = models.FileField(upload_to='documentos_solicitudes/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_documento} - Solicitud #{self.solicitud.id}"