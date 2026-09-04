from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Datos Adicionales', {'fields': ('rol', 'carne', 'telefono')}),
    )
    list_display = ['username', 'email', 'rol', 'carne', 'is_staff']