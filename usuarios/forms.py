from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator  # 1. Importamos el validador por expresión regular
from .models import Usuario

class RegistroEstudianteForm(UserCreationForm):
    # 2. Regla estricta: Solo acepta dígitos enteros (0-9)
    solo_numeros = RegexValidator(r'^\d+$', 'Este campo solo debe contener números sin espacios ni letras.')

    first_name = forms.CharField(label="Nombres", max_length=150, required=True)
    last_name = forms.CharField(label="Apellidos", max_length=150, required=True)
    email = forms.EmailField(label="Correo electrónico", required=True)
    
    # 3. Aplicamos el validador a carne y teléfono
    carne = forms.CharField(
        label="Carné / Matrícula", 
        max_length=20, 
        required=True,
        validators=[solo_numeros]
    )
    telefono = forms.CharField(
        label="Teléfono", 
        max_length=15, 
        required=False,
        validators=[solo_numeros]
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'carne', 'telefono']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inyecta automáticamente clases de Bootstrap a todos los inputs
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control rounded-3'

        # Atributos de Experiencia de Usuario (UX) para celulares y navegadores
        self.fields['carne'].widget.attrs.update({
            'inputmode': 'numeric',
            'oninput': "this.value = this.value.replace(/[^0-9]/g, '')",
            'placeholder': 'Ej. 202600123'
        })
        self.fields['telefono'].widget.attrs.update({
            'inputmode': 'numeric',
            'oninput': "this.value = this.value.replace(/[^0-9]/g, '')",
            'placeholder': 'Ej. 55551234'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_carne(self):
        carne = self.cleaned_data.get('carne', '').strip()
        # Nota: El RegexValidator ya verificó que sean números, aquí solo validamos duplicados
        if Usuario.objects.filter(carne=carne).exists():
            raise forms.ValidationError("Este número de carné ya se encuentra registrado.")
        return carne

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.rol = Usuario.Rol.ESTUDIANTE
        usuario.email = self.cleaned_data['email']
        usuario.email_verificado = False  # <-- Se registra como pendiente de verificación
        if commit:
            usuario.save()
        return usuario