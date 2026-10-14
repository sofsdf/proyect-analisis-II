from django import forms
from .models import Solicitud


# --- HU-07: Formulario de resolución final del Administrador ---
class ResolucionForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['resolucion_final', 'comentarios_admin']
        widgets = {
            'resolucion_final': forms.RadioSelect,
            'comentarios_admin': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ej. Rechazada por falta de presupuesto.',
            }),
        }
        labels = {
            'resolucion_final': 'Resolución final',
            'comentarios_admin': 'Justificación',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resolucion_final'].choices = [
            ('APROBADA', 'Aprobar'),
            ('RECHAZADA', 'Rechazar'),
        ]
        self.fields['resolucion_final'].required = True
        self.fields['comentarios_admin'].required = True
