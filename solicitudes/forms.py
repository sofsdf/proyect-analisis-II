from django import forms
from .models import Solicitud

class SolicitudForm(forms.ModelForm):
    pdf_requisitos = forms.FileField(
        required=True,
        label="Documento de postulación (PDF)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'})
    )

    class Meta:
        model = Solicitud
        fields = ['pdf_requisitos']  # Vinculamos el campo directamente con el modelo

    def clean_pdf_requisitos(self):
        archivo = self.cleaned_data.get('pdf_requisitos')
        if archivo:
            if not archivo.name.lower().endswith('.pdf'):
                raise forms.ValidationError("El archivo debe estar en formato PDF.")
            if archivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("El archivo no debe superar los 5 MB.")
        return archivo