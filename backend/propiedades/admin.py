from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario


class PerfilInline(admin.StackedInline):
    model   = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')


# Re-registrar User con el admin extendido
admin.site.unregister(User)
admin.site.register(User, UserAdmin)