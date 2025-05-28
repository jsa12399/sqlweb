# Integracion_Proyecto/core/forms.py

from django import forms
from .models import Servicio, Usuario

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = [
            'nombre_servicio',
            'descripcion_servicio',
            'precio_servicio',
            'duracion_minutos',
            'disponible',
        ]
        labels = {
            'nombre_servicio': 'Nombre del Servicio',
            'descripcion_servicio': 'Descripción',
            'precio_servicio': 'Precio ($)',
            'duracion_minutos': 'Duración (minutos)',
            'disponible': '¿Está disponible?',
        }
        widgets = {
            'descripcion_servicio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe brevemente tu servicio'}),
            'precio_servicio': forms.NumberInput(attrs={'placeholder': 'Ej: 25000.00'}),
            'duracion_minutos': forms.NumberInput(attrs={'placeholder': 'Ej: 60'}),
            # CAMBIO CRÍTICO AQUÍ: Ajusta estos valores para que coincidan con tu restricción de Oracle
            'disponible': forms.RadioSelect(choices=[('S', 'Sí'), ('N', 'No')]), # <-- ¡Cambia '1' y '0' por 'S' y 'N'!
        }