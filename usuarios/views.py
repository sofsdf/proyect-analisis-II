from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from .forms import RegistroEstudianteForm
from .models import Usuario


def registro_estudiante(request):
    if request.method == 'POST':
        form = RegistroEstudianteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
            return redirect('usuarios:login')
    else:
        form = RegistroEstudianteForm()
    return render(request, 'usuarios/registro.html', {'form': form})


class CustomLoginView(View):
    template_name = 'usuarios/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return self.redirigir_por_rol(request.user)
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"¡Bienvenido/a {user.first_name or user.username}!")
                    return self.redirigir_por_rol(user)
                else:
                    messages.error(request, "Tu cuenta se encuentra inactiva.")
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
        else:
            messages.error(request, "Credenciales inválidas. Revisa los datos ingresados.")

        return render(request, self.template_name, {'form': form})

    def redirigir_por_rol(self, user):
        """Redirección según el rol definido en el sistema."""
        if user.is_superuser or user.is_staff or (hasattr(user, 'rol') and user.rol == Usuario.Rol.ADMIN):
            return redirect('solicitudes:lista_solicitudes_comite')
        else:
            return redirect('convocatorias:catalogo')


def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('usuarios:login')


# --- VISTA PARA VISTA PREVIA / SIMULACIÓN DE ROL ---
def alternar_vista_previa(request):
    """
    Permite a los administradores alternar entre la vista de Admin y la vista de Estudiante.
    """
    if request.user.is_staff or request.user.is_superuser:
        estado_actual = request.session.get('modo_vista_estudiante', False)
        request.session['modo_vista_estudiante'] = not estado_actual
        
        if request.session['modo_vista_estudiante']:
            messages.info(request, "Has cambiado a 'Vista Previa de Estudiante'.")
            return redirect('convocatorias:catalogo')
        else:
            messages.success(request, "🛠️ Has regresado al modo Administrador.")
            return redirect('solicitudes:lista_solicitudes_comite')
            
    return redirect('convocatorias:catalogo')