from django.contrib import admin
from .models import Solicitud  

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ('id', 'estudiante', 'convocatoria', 'evaluador', 'estado', 'fecha_postulacion')
    list_filter = ('estado', 'convocatoria')
    search_fields = ('estudiante__username', 'convocatoria__titulo')

