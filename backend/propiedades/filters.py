"""
propiedades/filters.py
======================
FilterSets para la API de Remolina Inmobiliaria.

Permite al frontend filtrar propiedades via query params, por ejemplo:
    GET /api/propiedades/?tipo=apartamento&estado=disponible&precio_min=200000000&precio_max=500000000
    GET /api/propiedades/?ciudad=Ibagué&estrato=4&ordering=-precio
    GET /api/propiedades/?search=laureles
"""

import django_filters
from .models import Propiedad


class PropiedadFilter(django_filters.FilterSet):
    """Filtros avanzados para el endpoint de propiedades."""

    # Rango de precio
    precio_min = django_filters.NumberFilter(field_name='precio', lookup_expr='gte',
                                             label='Precio mínimo')
    precio_max = django_filters.NumberFilter(field_name='precio', lookup_expr='lte',
                                             label='Precio máximo')

    # Rango de área
    area_min = django_filters.NumberFilter(field_name='area', lookup_expr='gte',
                                           label='Área mínima (m²)')
    area_max = django_filters.NumberFilter(field_name='area', lookup_expr='lte',
                                           label='Área máxima (m²)')

    # Filtros exactos con choices
    tipo   = django_filters.ChoiceFilter(choices=Propiedad.TIPO_CHOICES)
    estado = django_filters.ChoiceFilter(choices=Propiedad.ESTADO_CHOICES)

    # Ciudad: insensible a mayúsculas
    ciudad = django_filters.CharFilter(lookup_expr='icontains', label='Ciudad')

    # Características
    habitaciones = django_filters.NumberFilter(field_name='habitaciones',
                                               lookup_expr='gte',
                                               label='Mínimo de habitaciones')
    banos        = django_filters.NumberFilter(field_name='banos',
                                               lookup_expr='gte',
                                               label='Mínimo de baños')
    estrato      = django_filters.NumberFilter(label='Estrato exacto')
    parqueadero  = django_filters.BooleanFilter(label='Con parqueadero')

    class Meta:
        model  = Propiedad
        fields = [
            'tipo', 'estado', 'ciudad',
            'precio_min', 'precio_max',
            'area_min', 'area_max',
            'habitaciones', 'banos', 'estrato', 'parqueadero',
        ]