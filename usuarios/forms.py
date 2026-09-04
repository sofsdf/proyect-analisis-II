from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class RegistroEstudianteForm(UserCreationForm):
    first_name = forms.CharField(label="Nombres", max_length=150, required=True)
    last_name = forms.CharField(label="Apellidos", max_length=150, required=True)
    email = forms.EmailField(label="Correo electrónico", required=True)
    carne = forms.CharField(label="Carné / Matrícula", max_length=20, required=True)
    telefono = forms.CharField(label="Teléfono", max_length=15, required=False)

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'carne', 'telefono']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_carne(self):
        carne = self.cleaned_data.get('carne', '').strip()
        if Usuario.objects.filter(carne=carne).exists():
            raise forms.ValidationError("Este número de carné ya se encuentra registrado.")
        return carne

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.rol = Usuario.Rol.ESTUDIANTE
        usuario.email = self.cleaned_data['email']
        if commit:
            usuario.save()
        return usuario