from .models import Notificacion

def notificaciones_usuario(request):
    if request.user.is_authenticated:
        qs = Notificacion.objects.filter(usuario=request.user)
        return {
            'notificaciones_list': qs[:5],
            'notificaciones_no_leidas_count': qs.filter(leida=False).count()
        }
    return {}