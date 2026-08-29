from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Convocatoria
from .forms import ConvocatoriaForm


def es_admin(user):
    return user.is_staff


# --- Vista para Estudiante: ver catálogo ---
@login_required
def catalogo_convocatorias(request):
    convocatorias = Convocatoria.objects.filter(publicada=True)
    return render(request, 'convocatorias/catalogo.html', {
        'convocatorias': convocatorias
    })


# --- Vista para Admin: listar todas (publicadas o no) ---
@login_required
@user_passes_test(es_admin)
def lista_convocatorias_admin(request):
    convocatorias = Convocatoria.objects.all()
    return render(request, 'convocatorias/admin_lista.html', {
        'convocatorias': convocatorias
    })


# --- Vista para Admin: crear/publicar convocatoria ---
@login_required
@user_passes_test(es_admin)
def crear_convocatoria(request):
    if request.method == 'POST':
        form = ConvocatoriaForm(request.POST)
        if form.is_valid():
            convocatoria = form.save(commit=False)
            convocatoria.creada_por = request.user
            convocatoria.save()
            messages.success(request, 'Convocatoria creada correctamente.')
            return redirect('convocatorias:admin_lista')
    else:
        form = ConvocatoriaForm()
    return render(request, 'convocatorias/crear.html', {'form': form})