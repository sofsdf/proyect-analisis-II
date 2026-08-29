from django.urls import path
from . import views

app_name = 'convocatorias'

urlpatterns = [
    path('', views.catalogo_convocatorias, name='catalogo'),
    path('admin/', views.lista_convocatorias_admin, name='admin_lista'),
    path('admin/crear/', views.crear_convocatoria, name='crear'),
]