from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_estudiante, name='registro'),
    path('confirmacion-registro/', views.confirmacion_registro, name='confirmacion_registro'),
    path('verificar-correo/<str:uidb64>/<str:token>/', views.verificar_correo, name='verificar_correo'),
    path('vista-previa/', views.alternar_vista_previa, name='alternar_vista_previa'),
]