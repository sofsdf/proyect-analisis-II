from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro_estudiante, name='registro_estudiante'),
]