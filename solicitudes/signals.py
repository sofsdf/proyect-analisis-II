from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Solicitud

@receiver(post_save, sender=Solicitud)
def notificar_postulacion_creada(sender, instance, created, **kwargs):
    if created:
        # Detecta automáticamente el campo de usuario o postulante
        usuario_relacionado = getattr(instance, 'usuario', None) or \
                              getattr(instance, 'postulante', None) or \
                              getattr(instance, 'estudiante', None)
        
        nombre_usuario = usuario_relacionado.username if usuario_relacionado else "Estudiante"
        titulo_convocatoria = getattr(instance.convocatoria, 'titulo', 'Convocatoria')

        print("\n" + "="*55)
        print(" [PATRÓN OBSERVER / SIGNAL ACTIVADO]")
        print(f" Evento: Nueva Solicitud #{instance.pk} guardada en BD")
        print(f" Postulante notificado: {nombre_usuario}")
        print(f" Convocatoria: {titulo_convocatoria}")
        print(" Acción desacoplada: Notificación/correo simulado con éxito.")
        print("="*55 + "\n")