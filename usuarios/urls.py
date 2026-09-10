from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    
    path('registro/', views.registro_estudiante, name='registro_estudiante'),
    
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
]