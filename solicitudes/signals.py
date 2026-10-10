from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Solicitud

@receiver(post_save, sender=Solicitud)
def notificar_evento_solicitud(sender, instance, created, **kwargs):
    """
    Patrón Observer:
    - Escucha la señal 'post_save' emitida por el modelo Solicitud.
    - Se dispara automáticamente tanto al crear (HU-05) como al evaluar (HU-06).
    """
    print("\n" + "="*60)
    print(" [PATRÓN OBSERVER / SIGNAL ACTIVADO]")

    if created:
        print(f" Evento: Nueva Solicitud #{instance.id} registrada en la BD")
        print(f" Postulante: {instance.estudiante.username}")
        print(f" Convocatoria: {instance.convocatoria.titulo}")
        print(" Acción desacoplada: Simulación de correo de confirmación enviado.")
    else:
        print(f" Evento: Dictamen registrado en Solicitud #{instance.id}")
        print(f" Nuevo Estado: {instance.get_estado_display()}")
        print(f" Evaluado por: {instance.evaluador.username if instance.evaluador else 'Administrador'}")
        print(f" Postulante notificado: {instance.estudiante.username}")
        print(f" Observaciones: {instance.observaciones or 'Sin observaciones'}")
        print(" Acción desacoplada: Notificación/correo de dictamen enviado con éxito.")

    print("="*60 + "\n")