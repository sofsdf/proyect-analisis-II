from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse

from .forms import SolicitudForm
from solicitudes.models import Solicitud
from convocatorias.models import Convocatoria 

User = get_user_model()

# --- 1. PRUEBAS DE VALIDACIÓN DE DOCUMENTOS (QA) ---
class DocumentosValidacionTests(TestCase):
    def setUp(self):
        hoy = timezone.now().date()
        # Se envían AMBAS fechas para cumplir con el modelo Convocatoria
        self.convocatoria = Convocatoria.objects.create(
            titulo="Beca Prueba",
            fecha_inicio=hoy,
            fecha_cierre=hoy + timedelta(days=30)
        )

    def test_rechazar_archivo_no_pdf(self):
        """Verifica que subir un archivo que no sea PDF sea rechazado."""
        archivo_invalido = SimpleUploadedFile(
            name="documento_prueba.txt",
            content=b"Contenido simulado no valido",
            content_type="text/plain"
        )
        
        form = SolicitudForm(
            data={'monto_solicitado': 5000.00, 'convocatoria': self.convocatoria.id}, 
            files={'pdf_requisitos': archivo_invalido}
        )
        
        self.assertFalse(form.is_valid(), "El formulario no debería ser válido si el archivo no es PDF.")
        self.assertIn('pdf_requisitos', form.errors, "Debe existir un error en el campo pdf_requisitos.")

    def test_aceptar_archivo_pdf_valido(self):
        """Verifica que un archivo .pdf válido sea aceptado."""
        archivo_valido = SimpleUploadedFile(
            name="expediente.pdf",
            content=b"%PDF-1.4 simulando estructura pdf",
            content_type="application/pdf"
        )
        
        form = SolicitudForm(
            data={'monto_solicitado': 5000.00, 'convocatoria': self.convocatoria.id}, 
            files={'pdf_requisitos': archivo_valido}
        )
        self.assertTrue(form.is_valid(), f"El formulario debe ser válido. Errores: {form.errors}")


# --- 2. PRUEBAS DE SEGURIDAD, REGLAS DE NEGOCIO Y AUDITORÍA ---
class SolicitudTestCase(TestCase):
    def setUp(self):
        self.estudiante = User.objects.create_user(
            username='estudiante_test', email='estudiante@test.com', password='123', rol='ESTUDIANTE'
        )
        self.evaluador = User.objects.create_user(
            username='evaluador_test', email='evaluador@test.com', password='123', rol='EVALUADOR'
        )
        self.admin = User.objects.create_user(
            username='admin_test', email='admin@test.com', password='123', rol='ADMIN'
        )
        
        hoy = timezone.now().date()
        self.convocatoria = Convocatoria.objects.create(
            titulo="Beca Excelencia 2026",
            fecha_inicio=hoy,
            fecha_cierre=hoy + timedelta(days=30)
        )
        
        self.solicitud = Solicitud.objects.create(
            estudiante=self.estudiante,
            convocatoria=self.convocatoria,
            monto_solicitado=15000.00,
            estado='EN_REVISION'
        )

    def test_seguridad_acceso_comite(self):
        """Prueba de Seguridad: Un estudiante no debe poder ver el panel del comité."""
        self.client.login(username='estudiante_test', password='123')
        
        url = reverse('solicitudes:lista_solicitudes_comite') 
        response = self.client.get(url)
        
        self.assertNotEqual(response.status_code, 200)

    def test_doble_firma_mismo_usuario_rechazada(self):
        """Prueba de Negocio: Rechaza si el evaluador y autorizador son la misma persona para > Q10,000."""
        self.solicitud.evaluador = self.evaluador
        self.solicitud.autorizador_final = self.evaluador
        
        with self.assertRaises(ValidationError):
            self.solicitud.clean()

    def test_auditoria_historial_creado(self):
        """Prueba de Auditoría: Verifica que simple-history registre los cambios de estado."""
        self.solicitud.estado = 'APROBADA'
        self.solicitud.save()
        
        self.assertEqual(self.solicitud.history.count(), 2)