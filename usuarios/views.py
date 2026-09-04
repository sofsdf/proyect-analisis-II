from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistroEstudianteForm

def registro_estudiante(request):
    if request.method == 'POST':
        form = RegistroEstudianteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
            return redirect('registro_estudiant')  # Raca debe redirigir a la vista de login de Lourdes
    else:
        form = RegistroEstudianteForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})