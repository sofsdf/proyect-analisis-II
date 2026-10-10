from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Solicitud
from .forms import SolicitudForm
from convocatorias.models import Convocatoria  #  importar el modelo de Convocatoria
from django.contrib.auth import get_user_model
User = get_user_model()

# Verificación para asegurarnos de que solo el personal/evaluador acceda
def es_evaluador_o_staff(user):
    return user.is_staff or user.is_superuser or user.groups.filter(name='ComiteEvaluador').exists()

# --- VISTA RESTAURADA DE POSTULACIÓN (HU-05) ---
@login_required
def crear_solicitud(request, convocatoria_id):
    convocatoria = get_object_or_404(Convocatoria, pk=convocatoria_id)
    
    if request.method == 'POST':
        # request.FILES es súper importante para que guarde el PDF
        form = SolicitudForm(request.POST, request.FILES) 
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.estudiante = request.user
            solicitud.convocatoria = convocatoria
            solicitud.save()
            
            messages.success(request, '¡Tu solicitud ha sido enviada con éxito!')
            return redirect('convocatorias:catalogo')  # Te regresa al catálogo tras postularse
    else:
        form = SolicitudForm()
        
    return render(request, 'solicitudes/crear_solicitud.html', {
        'form': form,
        'convocatoria': convocatoria
    })


# --- VISTAS PARA HU-06 (Comité y Evaluación) ---
@login_required
@user_passes_test(es_evaluador_o_staff)
def lista_solicitudes_comite(request):
    """
    HU-06: Muestra la lista de solicitudes. 
    Los Administradores ven todas; los Evaluadores ven solo las asignadas a ellos.
    """
    if request.user.is_staff or request.user.is_superuser:
        # El Admin ve todo
        solicitudes = Solicitud.objects.all().select_related('estudiante', 'convocatoria', 'evaluador')
    else:
        # El Evaluador ve solo lo suyo
        solicitudes = Solicitud.objects.filter(evaluador=request.user).select_related('estudiante', 'convocatoria', 'evaluador')
    
    # Consultar integrantes del comité (para el dropdown de asignación)
    evaluadores = User.objects.filter(groups__name='ComiteEvaluador')

    return render(request, 'solicitudes/lista_comite.html', {
        'solicitudes': solicitudes,
        'evaluadores': evaluadores
    })


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser) # Solo Admins pueden asignar
def asignar_evaluador(request, pk):
    """
    HU-06: Permite al Administrador asignar un evaluador a una solicitud.
    """
    solicitud = get_object_or_404(Solicitud, pk=pk)
    if request.method == 'POST':
        evaluador_id = request.POST.get('evaluador_id')
        if evaluador_id:
            evaluador = get_object_or_404(User, pk=evaluador_id)
            solicitud.evaluador = evaluador
            solicitud.save()
            messages.success(request, f"¡Solicitud #{solicitud.id} asignada a {evaluador.username} con éxito!")
        else:
            # Si seleccionan "Sin asignar"
            solicitud.evaluador = None
            solicitud.save()
            messages.info(request, f"Se removió el evaluador de la solicitud #{solicitud.id}.")
            
    return redirect('solicitudes:lista_solicitudes_comite')


@login_required
@user_passes_test(es_evaluador_o_staff)
def evaluar_solicitud(request, pk):
    """
    HU-06: Permite consultar la documentación en PDF y registrar el dictamen.
    """
    solicitud = get_object_or_404(Solicitud, pk=pk)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        observaciones = request.POST.get('observaciones')

        if nuevo_estado in ['APROBADA', 'RECHAZADA', 'EN_REVISION']:
            solicitud.estado = nuevo_estado
            solicitud.observaciones = observaciones
            solicitud.evaluador = request.user  # Asigna al usuario actual como evaluador
            solicitud.save()  # <--- Patrón Observer en signals.py!

            messages.success(request, f"La solicitud #{solicitud.id} fue actualizada a estado '{solicitud.get_estado_display()}' con éxito.")
            # corrigí agregando el namespace 'solicitudes:'
            return redirect('solicitudes:lista_solicitudes_comite') 
        else:
            messages.error(request, "Estado no válido seleccionado.")

    return render(request, 'solicitudes/evaluar_solicitud.html', {
        'solicitud': solicitud
    })