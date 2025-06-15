# Integracion_Proyecto/core/forms.py

from django import forms
from .models import Servicio, Usuario, ComentarioValoracionProducto, Envio # Asegúrate de que Envio esté importado

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = [
            'nombre_servicio',
            'descripcion_servicio',
            'precio_servicio',
            'duracion_minutos',
            'disponible',
            # No es necesario incluir 'id_proveedor_servicio' aquí si es asignado automáticamente
            # o manejado en la vista, ya que el DDL lo requiere.
            # Si un proveedor debe seleccionarse en el formulario, añádelo aquí y en labels/widgets
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
            # CAMBIO APLICADO: Ajusta estos valores para que coincidan con 'S' y 'N'
            'disponible': forms.RadioSelect(choices=[('S', 'Sí'), ('N', 'No')]), 
        }


class ComentarioValoracionForm(forms.ModelForm):
    class Meta:
        model = ComentarioValoracionProducto
        fields = ['comentario', 'valoracion'] 
        # Si 'id_producto' y 'id_usuario' no se seleccionan en el formulario,
        # asegúrate de asignarlos en tu vista antes de guardar.


class ActualizarEstadoEnvioForm(forms.ModelForm):
    class Meta:
        model = Envio
        fields = ['estado_envio', 'codigo_rastreo', 'nombre_transportista']
        # Si 'fecha_envio', 'fecha_estimada_entrega', 'fecha_entrega_real', 'id_venta_producto', 'costo_envio'
        # deben ser gestionados por el formulario, añádelos a 'fields' y configura sus widgets/labels.