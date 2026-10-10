from django.urls import path
from . import views

app_name = 'solicitudes'

urlpatterns = [
    path('nueva/<int:convocatoria_id>/', views.crear_solicitud, name='crear_solicitud'),
    path('comite/', views.lista_solicitudes_comite, name='lista_solicitudes_comite'),
    path('evaluar/<int:pk>/', views.evaluar_solicitud, name='evaluar_solicitud'),
    path('asignar/<int:pk>/', views.asignar_evaluador, name='asignar_evaluador'),
]