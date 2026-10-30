from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Solicitud, Notificacion

User = get_user_model()

@receiver(pre_save, sender=Solicitud)
def capturar_estado_anterior(sender, instance, **kwargs):
    """Guarda en memoria el estado previo antes de aplicar la actualización."""
    if instance.pk:
        try:
            vieja_solicitud = Solicitud.objects.get(pk=instance.pk)
            instance._estado_anterior = vieja_solicitud.estado
        except Solicitud.DoesNotExist:
            instance._estado_anterior = None
    else:
        instance._estado_anterior = None

@receiver(post_save, sender=Solicitud)
def notificar_cambio_estado(sender, instance, created, **kwargs):
    """Genera la notificación en BD (campanita) y envía el correo por Mailtrap."""
    
    # 1. CASO: Solicitud Nueva Creada
    if created:
        if instance.estudiante:
            mensaje_notif = f"Tu solicitud para '{instance.convocatoria.titulo}' ha sido recibida y está PENDIENTE."
            Notificacion.objects.create(usuario=instance.estudiante, solicitud=instance, mensaje=mensaje_notif)
            
            if instance.estudiante.email:
                send_mail(
                    subject=f"Solicitud Recibida - {instance.convocatoria.titulo}",
                    message=f"Hola {instance.estudiante.username},\n\n{mensaje_notif}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.estudiante.email],
                    fail_silently=True,
                )
        return

    # 2. CASO: Cambio de estado (Evaluación)
    if hasattr(instance, '_estado_anterior') and instance._estado_anterior != instance.estado:
        estudiante = instance.estudiante
        
        # A. NOTIFICACIÓN PARA EL ADMIN (> Q10,000)
        if instance.estado == 'PENDIENTE_AUTORIZACION_FINAL':
            mensaje_admin = f"URGENTE: La solicitud #{instance.id} de {estudiante.username} requiere tu AUTORIZACIÓN FINAL (> Q10k)."
            admins = User.objects.filter(rol='ADMIN')
            
            for admin in admins:
                Notificacion.objects.create(usuario=admin, solicitud=instance, mensaje=mensaje_admin)
            
            admin_emails = list(admins.values_list('email', flat=True))
            if admin_emails:
                send_mail(
                    subject=f"ACCIÓN REQUERIDA: Segunda Firma - Solicitud #{instance.id}",
                    message=f"El comité ha aprobado la solicitud de {estudiante.username} por Q{instance.monto_solicitado}.\n\nAl superar los Q10,000, requiere su AUTORIZACIÓN FINAL.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=admin_emails,
                    fail_silently=True,
                )

        # B. NOTIFICACIONES PARA EL ESTUDIANTE (Aprobada / Rechazada)
        if instance.estado in ['APROBADA', 'RECHAZADA']:
            nuevo_estado_texto = instance.get_estado_display()
            mensaje_notif = f"Tu solicitud #{instance.id} para '{instance.convocatoria.titulo}' ha cambiado al estado: {nuevo_estado_texto}."

            if estudiante:
                Notificacion.objects.create(usuario=estudiante, solicitud=instance, mensaje=mensaje_notif)
                
            if estudiante and estudiante.email:
                send_mail(
                    subject=f"Actualización de Solicitud - {instance.convocatoria.titulo}",
                    message=f"Hola {estudiante.username},\n\n{mensaje_notif}\n\nObservaciones: {instance.observaciones}\n\nRevisa el portal para más detalles.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[estudiante.email],
                    fail_silently=True,
                )