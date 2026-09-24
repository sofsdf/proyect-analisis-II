from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import SolicitudForm

class DocumentosValidacionTests(TestCase):
    def test_rechazar_archivo_no_pdf(self):
        """Verifica que subir un archivo que no sea PDF sea rechazado con el error esperado."""
        # Creamos un archivo simulado .txt o imagen
        archivo_invalido = SimpleUploadedFile(
            name="documento_prueba.txt",
            content=b"Contenido simulado no valido",
            content_type="text/plain"
        )
        
        # Instanciamos el formulario con el archivo no permitido
        form = SolicitudForm(data={}, files={'archivo_pdf': archivo_invalido})
        
        # Validaciones de QA
        self.assertFalse(form.is_valid(), "El formulario no debería ser válido si el archivo no es PDF.")
        self.assertIn('archivo_pdf', form.errors, "Debe existir un error en el campo archivo_pdf.")
        self.assertIn("El archivo debe estar en formato PDF.", form.errors['archivo_pdf'])

    def test_aceptar_archivo_pdf_valido(self):
        """Verifica que un archivo .pdf dentro del limite de peso sea aceptado."""
        archivo_valido = SimpleUploadedFile(
            name="expediente.pdf",
            content=b"%PDF-1.4 simulando estructura pdf",
            content_type="application/pdf"
        )
        
        form = SolicitudForm(data={}, files={'archivo_pdf': archivo_valido})
        self.assertTrue(form.is_valid(), "El formulario debe ser válido cuando se sube un archivo PDF.")