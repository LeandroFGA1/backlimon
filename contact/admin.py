from django.contrib import admin
from .models import ContactMessage


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'email', 'telefono', 'tipo_contacto', 'fecha_envio', 'recaptcha_score')
    list_filter = ('tipo_contacto', 'fecha_envio', 'recaptcha_score')
    search_fields = ('nombre', 'apellidos', 'email', 'telefono', 'mensaje', 'ip_address')
    readonly_fields = ('nombre', 'apellidos', 'email', 'telefono', 'tipo_contacto',
                       'mensaje', 'fecha_envio', 'ip_address', 'recaptcha_score')
    ordering = ('-fecha_envio',)

    def has_module_permission(self, request):
        # Allows the app label (Contact Messages) to appear in the admin index
        return request.user.has_perm('contact.view_contactmessage')

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('contact.view_contactmessage')

    def has_change_permission(self, request, obj=None):
        # Disallow changing messages
        return False

    def has_add_permission(self, request):
        # Disallow adding messages from the admin
        return False


admin.site.register(ContactMessage, ContactMessageAdmin)
