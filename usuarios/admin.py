from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Cliente, Usuario

class ClienteAdmin(UserAdmin):
    list_display = ('email', 'is_staff', 'es_cliente')
    list_filter = ('is_staff', 'es_cliente', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'run', 'dv', 'region', 'comuna', 'direccion')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'es_cliente', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser', 'es_cliente'),
        }),
    )
    search_fields = ('email', 'run')
    ordering = ('email',)
class UsuarioAdmin(UserAdmin):

    model = Usuario
    list_display = ['email', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permisos', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ['email']
    ordering = ['email']

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Cliente)
