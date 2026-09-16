from django import forms
from .models import Solicitud, Documento

class SolicitudForm(forms.ModelForm):
    archivo_pdf = forms.FileField(
        required=True,
        label="Documento de postulación (PDF)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'})
    )

    class Meta:
        model = Solicitud
        fields = []  # Los campos como estudiante y convocatoria se asignan automáticamente en la vista

    def clean_archivo_pdf(self):
        archivo = self.cleaned_data.get('archivo_pdf')
        if archivo:
            if not archivo.name.lower().endswith('.pdf'):
                raise forms.ValidationError("El archivo debe estar en formato PDF.")
            if archivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("El archivo no debe superar los 5 MB.")
        return archivo