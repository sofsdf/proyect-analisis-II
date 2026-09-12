from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView  # 1. Agrega esta importación

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('convocatorias/', include('convocatorias.urls')),
    
    # 2. Agrega esta línea para redirigir la raíz al login:
    path('', RedirectView.as_view(url='/usuarios/login/', permanent=False)),
]