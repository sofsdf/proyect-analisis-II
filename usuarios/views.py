from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.views import View
from .forms import RegistroEstudianteForm
from .models import Usuario


def registro_estudiante(request):
    if request.method == 'POST':
        form = RegistroEstudianteForm(request.POST)
        if form.is_valid():
            usuario = form.save()

            # 1. Generar token único de verificación
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)

            # 2. Construir enlace
            url_verificacion = request.build_absolute_uri(
                reverse('usuarios:verificar_correo', kwargs={'uidb64': uid, 'token': token})
            )

            # 3. Enviar correo
            asunto = "Verifica tu correo electrónico - Sistema de Becas"
            mensaje = (
                f"Hola {usuario.first_name or usuario.username},\n\n"
                f"Gracias por registrarte en el Sistema de Becas.\n"
                f"Para confirmar tu correo y activar tu cuenta, haz clic en el siguiente enlace:\n\n"
                f"{url_verificacion}\n\n"
                f"Si tú no solicitaste este registro, por favor ignora este mensaje."
            )

            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=True
            )

            return redirect('usuarios:confirmacion_registro')
    else:
        form = RegistroEstudianteForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def confirmacion_registro(request):
    """Pantalla informativa que solicita revisar la bandeja de entrada."""
    return render(request, 'usuarios/confirmacion_registro.html')


def verificar_correo(request, uidb64, token):
    """Procesa la confirmación desde el enlace enviado al correo."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None

    if usuario is not None and default_token_generator.check_token(usuario, token):
        usuario.email_verificado = True
        usuario.save()
        messages.success(request, '¡Tu correo ha sido verificado exitosamente! Ya puedes iniciar sesión.')
    else:
        messages.error(request, 'El enlace de verificación es inválido o ha expirado.')

    return redirect('usuarios:login')


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
                # 🔒 Restricción de verificación de correo
                if not user.email_verificado and not user.is_staff and not user.is_superuser:
                    messages.warning(request, "Tu correo aún no ha sido verificado. Revisa tu bandeja de entrada.")
                    return render(request, self.template_name, {'form': form})

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
        if user.is_superuser or user.is_staff or (hasattr(user, 'rol') and user.rol == Usuario.Rol.ADMIN):
            return redirect('solicitudes:lista_solicitudes_comite')
        else:
            return redirect('convocatorias:catalogo')


def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('usuarios:login')


def alternar_vista_previa(request):
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