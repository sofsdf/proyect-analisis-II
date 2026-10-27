from django import forms
from .models import Solicitud

class SolicitudForm(forms.ModelForm):
    monto_solicitado = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        label="Monto Solicitado (Q)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. 12000.00',
            'min': '0',
            'step': '0.01'
        })
    )

    pdf_requisitos = forms.FileField(
        required=True,
        label="Documento de postulación (PDF)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'})
    )

    class Meta:
        model = Solicitud
        fields = ['monto_solicitado', 'pdf_requisitos']  # Incluye el monto y el archivo PDF

    def clean_pdf_requisitos(self):
        archivo = self.cleaned_data.get('pdf_requisitos')
        if archivo:
            if not archivo.name.lower().endswith('.pdf'):
                raise forms.ValidationError("El archivo debe estar en formato PDF.")
            if archivo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("El archivo no debe superar los 5 MB.")
        return archivo