from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .models import Solicitud, AuditoriaSolicitud
from .forms import SolicitudForm
from .forms_resolucion import ResolucionForm  # HU-07
from convocatorias.models import Convocatoria
from usuarios.models import Usuario

User = get_user_model()

# Verificación para asegurarnos de que solo el personal/evaluador/admin acceda
def es_evaluador_o_staff(user):
    return user.is_staff or user.is_superuser or user.rol in ['EVALUADOR', 'ADMIN'] or user.groups.filter(name='ComiteEvaluador').exists()


# --- VISTA RESTAURADA DE POSTULACIÓN (HU-05) ---
@login_required
def crear_solicitud(request, convocatoria_id):
    convocatoria = get_object_or_404(Convocatoria, pk=convocatoria_id)
    
    if request.method == 'POST':
        form = SolicitudForm(request.POST, request.FILES) 
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.estudiante = request.user
            solicitud.convocatoria = convocatoria
            solicitud.save()
            
            messages.success(request, '¡Tu solicitud ha sido enviada con éxito!')
            return redirect('convocatorias:catalogo')
    else:
        form = SolicitudForm()
        
    return render(request, 'solicitudes/crear_solicitud.html', {
        'form': form,
        'convocatoria': convocatoria
    })


# --- VISTAS PARA HU-06 (Comité y Evaluación con Doble Firma para > Q10,000) ---
@login_required
@user_passes_test(es_evaluador_o_staff)
def lista_solicitudes_comite(request):
    """
    HU-06: Muestra la lista de solicitudes. 
    Los Administradores ven todas; los Evaluadores ven solo las asignadas a ellos o pendientes.
    """
    if request.user.is_staff or request.user.is_superuser or request.user.rol == 'ADMIN':
        solicitudes = Solicitud.objects.all().select_related('estudiante', 'convocatoria', 'evaluador', 'autorizador_final')
    else:
        solicitudes = Solicitud.objects.filter(evaluador=request.user).select_related('estudiante', 'convocatoria', 'evaluador', 'autorizador_final')
    
    evaluadores = Usuario.objects.filter(rol=Usuario.Rol.EVALUADOR)

    return render(request, 'solicitudes/lista_comite.html', {
        'solicitudes': solicitudes,
        'evaluadores': evaluadores
    })


@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser or u.rol == 'ADMIN')
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
            solicitud.evaluador = None
            solicitud.save()
            messages.info(request, f"Se removió el evaluador de la solicitud #{solicitud.id}.")
            
    return redirect('solicitudes:lista_solicitudes_comite')


@login_required
@user_passes_test(es_evaluador_o_staff)
def evaluar_solicitud(request, pk):
    """
    HU-06 & Requerimiento de Mayor Monto (> Q10,000):
    Procesa las evaluaciones aplicando reglas de doble firma para solicitudes mayores a Q10,000.
    """
    solicitud = get_object_or_404(Solicitud, pk=pk)

    if request.method == 'POST':
        decision = request.POST.get('estado')  # 'APROBADA', 'RECHAZADA', 'EN_REVISION'
        observaciones = request.POST.get('observaciones', '')

        if decision not in ['APROBADA', 'RECHAZADA', 'EN_REVISION']:
            messages.error(request, "Estado no válido seleccionado.")
            return redirect('solicitudes:evaluar_solicitud', pk=pk)

        # Caso 1: Rechazo inmediato (aplica a cualquier monto)
        if decision == 'RECHAZADA':
            solicitud.estado = 'RECHAZADA'
            solicitud.observaciones = observaciones
            if not solicitud.evaluador:
                solicitud.evaluador = request.user
                solicitud.fecha_evaluacion_tecnica = timezone.now()
            elif not solicitud.autorizador_final:
                solicitud.autorizador_final = request.user
                solicitud.fecha_autorizacion_final = timezone.now()

            solicitud.save()

            AuditoriaSolicitud.objects.create(
                solicitud=solicitud,
                usuario=request.user,
                accion=f"Rechazo: la solicitud #{solicitud.id} fue rechazada definitivamente."
            )
            messages.error(request, f"La solicitud #{solicitud.id} ha sido rechazada.")
            return redirect('solicitudes:lista_solicitudes_comite')

        # Caso 2: Aprobación / Evaluación
        if decision == 'APROBADA':
            solicitud.observaciones = observaciones

            if solicitud.requiere_doble_firma:
                # Regla de seguridad: Impedir que la misma persona firme dos veces
                if request.user == solicitud.evaluador or request.user == solicitud.autorizador_final:
                    messages.error(request, "No puedes realizar ambas aprobaciones. Se requiere una segunda autoridad diferente.")
                    return redirect('solicitudes:evaluar_solicitud', pk=pk)

                # Si es la primera firma (Evaluador Técnico)
                if not solicitud.evaluador:
                    solicitud.evaluador = request.user
                    solicitud.fecha_evaluacion_tecnica = timezone.now()
                    solicitud.estado = 'PENDIENTE_AUTORIZACION_FINAL'
                    messages.info(request, f"Aprobación técnica registrada para la solicitud #{solicitud.id}. Pendiente de la firma de la autoridad autorizadora (> Q10,000).")

                # Si es la segunda firma (Autoridad Autorizadora / Admin)
                elif not solicitud.autorizador_final:
                    solicitud.autorizador_final = request.user
                    solicitud.fecha_autorizacion_final = timezone.now()
                    solicitud.estado = 'APROBADA'
                    messages.success(request, f"Aprobación final completada con doble firma para la solicitud #{solicitud.id}.")

            else:
                # Montos <= Q10,000 (Aprobación en flujo normal de una sola firma)
                solicitud.evaluador = request.user
                solicitud.fecha_evaluacion_tecnica = timezone.now()
                solicitud.estado = 'APROBADA'
                messages.success(request, f"Solicitud #{solicitud.id} aprobada exitosamente.")

            try:
                solicitud.clean()  # Ejecuta la validación del modelo
                solicitud.save()

                AuditoriaSolicitud.objects.create(
                    solicitud=solicitud,
                    usuario=request.user,
                    accion=f"Evaluación: cambio de estado a '{solicitud.get_estado_display()}'"
                )
            except ValidationError as e:
                messages.error(request, f"Error de validación: {e.message}")
                return redirect('solicitudes:evaluar_solicitud', pk=pk)

            return redirect('solicitudes:lista_solicitudes_comite')

        # Caso 3: Dejar en revisión
        if decision == 'EN_REVISION':
            solicitud.estado = 'EN_REVISION'
            solicitud.observaciones = observaciones
            solicitud.save()

            AuditoriaSolicitud.objects.create(
                solicitud=solicitud,
                usuario=request.user,
                accion=f"Evaluación: marcada 'En Revisión'"
            )
            messages.warning(request, f"La solicitud #{solicitud.id} quedó en revisión.")
            return redirect('solicitudes:lista_solicitudes_comite')

    return render(request, 'solicitudes/evaluar_solicitud.html', {
        'solicitud': solicitud
    })


# --- VISTAS PARA HU-07 (Resolución final del Administrador) ---
def es_admin_resolucion(user):
    return user.is_staff or user.is_superuser or user.rol == 'ADMIN'


@login_required
@user_passes_test(es_admin_resolucion)
def lista_resoluciones(request):
    """
    HU-07: Lista las solicitudes que el comité ya dictaminó
    (APROBADA o RECHAZADA) y que aún no tienen resolución final.
    """
    base = Solicitud.objects.select_related('estudiante', 'convocatoria', 'evaluador')
    pendientes = base.filter(
        estado__in=['APROBADA', 'RECHAZADA'],
        resolucion_final__isnull=True
    )
    resueltas = base.filter(resolucion_final__isnull=False)

    return render(request, 'solicitudes/resoluciones_lista.html', {
        'pendientes': pendientes,
        'resueltas': resueltas,
    })


@login_required
@user_passes_test(es_admin_resolucion)
def resolver_solicitud(request, pk):
    """
    HU-07: El Administrador registra la resolución final.
    """
    solicitud = get_object_or_404(
        Solicitud,
        pk=pk,
        estado__in=['APROBADA', 'RECHAZADA'],
        resolucion_final__isnull=True
    )

    if request.method == 'POST':
        form = ResolucionForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()

            AuditoriaSolicitud.objects.create(
                solicitud=solicitud,
                usuario=request.user,
                accion=f"Resolución Admin: registró resolución final como {solicitud.resolucion_final}"
            )

            messages.success(
                request,
                f"Resolución final registrada para la solicitud #{solicitud.id}: "
                f"{solicitud.get_resolucion_final_display()}."
            )
            return redirect('solicitudes:lista_resoluciones')
    else:
        form = ResolucionForm(instance=solicitud)

    return render(request, 'solicitudes/resolver_solicitud.html', {
        'solicitud': solicitud,
        'form': form,
    })


@login_required
def mis_solicitudes(request):
    """
    HU-08: El estudiante consulta el estado de sus propias solicitudes.
    """
    solicitudes = Solicitud.objects.filter(estudiante=request.user).order_by('-fecha_postulacion')
    
    return render(request, 'solicitudes/mis_solicitudes.html', {
        'solicitudes': solicitudes
    })


@login_required
@user_passes_test(lambda u: u.is_staff or u.rol == 'ADMIN')
def dashboard_reportes(request):
    total = Solicitud.objects.count()
    aprobadas = Solicitud.objects.filter(estado='APROBADA').count()
    rechazadas = Solicitud.objects.filter(estado='RECHAZADA').count()
    pendientes = Solicitud.objects.filter(estado__in=['EN_REVISION', 'PENDIENTE', 'PENDIENTE_AUTORIZACION_FINAL']).count()

    return render(request, 'solicitudes/reportes.html', {
        'total': total,
        'aprobadas': aprobadas,
        'rechazadas': rechazadas,
        'pendientes': pendientes
    })