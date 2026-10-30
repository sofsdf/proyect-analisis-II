from django.urls import path
from . import views

app_name = 'solicitudes'

urlpatterns = [
    path('nueva/<int:convocatoria_id>/', views.crear_solicitud, name='crear_solicitud'),
    path('comite/', views.lista_solicitudes_comite, name='lista_solicitudes_comite'),
    path('evaluar/<int:pk>/', views.evaluar_solicitud, name='evaluar_solicitud'),
    path('asignar/<int:pk>/', views.asignar_evaluador, name='asignar_evaluador'),
    # HU-07: Resolución final del Administrador
    path('resoluciones/', views.lista_resoluciones, name='lista_resoluciones'),
    path('resolver/<int:pk>/', views.resolver_solicitud, name='resolver_solicitud'),
    path('mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
    path('reportes/', views.dashboard_reportes, name='reportes'),
    path('notificaciones/marcar-leidas/', views.marcar_notificaciones_leidas, name='marcar_notificaciones_leidas'),
]