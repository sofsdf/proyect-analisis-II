from django import forms
from .models import Convocatoria


class ConvocatoriaForm(forms.ModelForm):
    class Meta:
        model = Convocatoria
        fields = ['titulo', 'descripcion', 'requisitos', 'fecha_inicio', 'fecha_cierre', 'publicada']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_cierre': forms.DateInput(attrs={'type': 'date'}),
        }