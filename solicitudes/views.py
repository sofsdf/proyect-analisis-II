from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from convocatorias.models import Convocatoria
from .models import Solicitud, Documento
from .forms import SolicitudForm

@login_required
def crear_solicitud(request, convocatoria_id):
    convocatoria = get_object_or_404(Convocatoria, id=convocatoria_id)

    if request.method == 'POST':
        form = SolicitudForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Crear la solicitud asociando usuario y convocatoria
            solicitud = form.save(commit=False)
            solicitud.estudiante = request.user
            solicitud.convocatoria = convocatoria
            solicitud.promedio_actual = 85.0  # <--- AQUÍ SE AGREGA
            solicitud.save()

            # 2. Guardar el archivo PDF asociado al modelo Documento
            archivo = form.cleaned_data['archivo_pdf']
            Documento.objects.create(
                solicitud=solicitud,
                archivo_pdf=archivo,       # <-- Debe llamarse archivo_pdf
                tipo_documento="NOTAS"     # <-- Usar una opción válida de TIPOS_DOC
            )

            return redirect('solicitudes:exito_solicitud')
    else:
        form = SolicitudForm()

    return render(request, 'solicitudes/crear_solicitud.html', {
        'form': form,
        'convocatoria': convocatoria
    })

@login_required
def exito_solicitud(request):
    return render(request, 'solicitudes/exito.html')