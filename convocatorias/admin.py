from django.contrib import admin
from .models import Convocatoria


@admin.register(Convocatoria)
class ConvocatoriaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_cierre', 'publicada')
    list_filter = ('publicada',)
    search_fields = ('titulo',)