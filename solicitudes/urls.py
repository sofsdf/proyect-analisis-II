from django.urls import path
from . import views

app_name = 'solicitudes'

urlpatterns = [
    path('nueva/<int:convocatoria_id>/', views.crear_solicitud, name='crear_solicitud'),
    path('exito/', views.exito_solicitud, name='exito_solicitud'),
]