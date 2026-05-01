"""
propiedades/admin.py
====================
Configuración del panel de administración Django para Remolina Inmobiliaria.

Incluye:
  - UserAdmin extendido con PerfilUsuario inline
  - PropiedadAdmin con list_display, filtros, búsqueda e imágenes en miniatura
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html

from .models import PerfilUsuario, Propiedad


# ── PerfilUsuario inline ──────────────────────────────────────────────────────

class PerfilInline(admin.StackedInline):
    model              = PerfilUsuario
    can_delete         = False
    verbose_name       = 'Perfil'
    verbose_name_plural = 'Perfil extendido'
    fields             = ('telefono', 'ciudad', 'creado')
    readonly_fields    = ('creado',)


@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    # ── Lista ─────────────────────────────────────────────────────────────────
    list_display = (
        'id', 'titulo', 'tipo', 'estado', 'ciudad',
        'precio_formateado', 'area', 'estrato',
        'habitaciones', 'banos', 'parqueadero',
        'thumbnail', 'fecha',
    )
    list_display_links = ('id', 'titulo')
    list_filter        = ('tipo', 'estado', 'ciudad', 'parqueadero', 'estrato')
    search_fields      = ('titulo', 'descripcion', 'ciudad', 'ubicacion')
    ordering           = ('-id',)
    list_per_page      = 20
    date_hierarchy     = 'fecha'

    # ── Formulario de edición ─────────────────────────────────────────────────
    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'descripcion', 'tipo', 'estado'),
        }),
        ('Ubicación', {
            'fields': ('ciudad', 'ubicacion'),
        }),
        ('Características', {
            'fields': (
                'precio', 'area', 'habitaciones',
                'banos', 'parqueadero', 'estrato',
            ),
        }),
        ('Imagen', {
            'fields': ('imagen', 'imagen_url', 'imagen_preview'),
        }),
        ('Fechas', {
            'fields': ('fecha',),
        }),
    )
    readonly_fields = ('imagen_preview',)

    # ── Métodos de visualización ──────────────────────────────────────────────

    @admin.display(description='Precio')
    def precio_formateado(self, obj):
        if obj.precio is None:
            return '—'
        return f'${obj.precio:,.0f}'.replace(',', '.')

    @admin.display(description='Miniatura')
    def thumbnail(self, obj):
        url = obj.imagen_url or (obj.imagen.url if obj.imagen else None)
        if not url:
            return '—'
        return format_html(
            '<img src="{}" style="height:40px; border-radius:4px; object-fit:cover;" />',
            url,
        )

    @admin.display(description='Vista previa')
    def imagen_preview(self, obj):
        url = obj.imagen_url or (obj.imagen.url if obj.imagen else None)
        if not url:
            return 'Sin imagen'
        return format_html(
            '<img src="{}" style="max-height:200px; border-radius:8px;" />',
            url,
        )

    # ── Acciones masivas ──────────────────────────────────────────────────────

    actions = ['marcar_disponible', 'marcar_vendido', 'marcar_reservado']

    @admin.action(description='Marcar como Disponible')
    def marcar_disponible(self, request, queryset):
        updated = queryset.update(estado='disponible')
        self.message_user(request, f'{updated} propiedad(es) marcadas como disponible.')

    @admin.action(description='Marcar como Vendido')
    def marcar_vendido(self, request, queryset):
        updated = queryset.update(estado='vendido')
        self.message_user(request, f'{updated} propiedad(es) marcadas como vendido.')

    @admin.action(description='Marcar como Reservado')
    def marcar_reservado(self, request, queryset):
        updated = queryset.update(estado='reservado')
        self.message_user(request, f'{updated} propiedad(es) marcadas como reservado.')


# ── User admin extendido ──────────────────────────────────────────────────────

class UserAdmin(BaseUserAdmin):
    inlines      = (PerfilInline,)
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_staff', 'is_active', 'date_joined',
    )
    list_filter  = ('is_staff', 'is_active', 'date_joined')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)