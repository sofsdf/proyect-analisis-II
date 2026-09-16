from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView  # 1. Agrega esta importación
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('convocatorias/', include('convocatorias.urls')),
    path('solicitudes/', include('solicitudes.urls')),
    path('', RedirectView.as_view(url='/usuarios/login/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    