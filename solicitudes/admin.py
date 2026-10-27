from django.contrib import admin
from .models import Solicitud, AuditoriaSolicitud 

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ('id', 'estudiante', 'convocatoria', 'evaluador', 'estado', 'fecha_postulacion')
    list_filter = ('estado', 'convocatoria')
    search_fields = ('estudiante__username', 'convocatoria__titulo')

@admin.register(AuditoriaSolicitud)
class AuditoriaSolicitudAdmin(admin.ModelAdmin):
    list_display = ('solicitud', 'usuario', 'accion', 'fecha')
    list_filter = ('fecha', 'usuario')
    search_fields = ('solicitud__id', 'accion')