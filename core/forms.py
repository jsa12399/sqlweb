# Integracion_Proyecto/core/forms.py

from django import forms
from .models import Servicio # Asegúrate de que Servicio está importado

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        # Incluye solo los campos que REALMENTE existen en tu modelo Servicio.
        # Si 'duracion_servicio_minutos' no existe en tu modelo, LO ELIMINAMOS de aquí.
        # id_proveedor_servicio es mejor que lo asignes en la vista (request.user).
        fields = [
            'nombre_servicio',
            'descripcion_servicio',
            'precio_servicio',
            # 'id_proveedor_servicio', # Generalmente se asigna en la vista, no se pide al usuario
        ]
        # Si quieres excluir campos explícitamente:
        # exclude = ['id_servicio', 'id_proveedor_servicio', 'duracion_servicio_minutos'] # Ejemplo
        labels = {
            'nombre_servicio': 'Nombre del Servicio',
            'descripcion_servicio': 'Descripción',
            'precio_servicio': 'Precio',
            # 'id_proveedor_servicio': 'Proveedor del Servicio',
        }
        widgets = {
            'descripcion_servicio': forms.Textarea(attrs={'rows': 4}),
        }