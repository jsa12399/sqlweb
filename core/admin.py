# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # Importa UserAdmin para tu modelo de usuario personalizado
from .models import (
    Usuario, # Tu modelo de usuario personalizado
    VentaProducto,
    Envio,
    Producto,
    Servicio,
    DetalleCompra,
    DetalleServicioAdquirido,
    MetodosDePago,
    InstanciaServicio,
    Ciudad,
    Comuna,
    TipoUsuario,
    Categoria,
    ComentarioValoracionProducto,
    Mensaje, # Si Mensaje es un modelo nativo de Django
     # Si MensajeServicio es una tabla mapeada en Oracle
)

# ----------------------------------------------------------------------
# Clases ModelAdmin para una interfaz de administración detallada
# ----------------------------------------------------------------------

# Clase Admin para tu modelo de usuario personalizado (Usuario)
# Extiende UserAdmin si quieres mantener la funcionalidad de usuarios de Django
class UsuarioAdmin(UserAdmin):
    # Campos que se mostrarán en la lista de usuarios en el admin
    list_display = ('email', 'rut', 'nombre', 'apellido', 'is_staff', 'is_active', 'id_tipo_usuario')
    # Campos por los que se puede filtrar la lista
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'id_tipo_usuario')
    # Campos por los que se puede buscar
    search_fields = ('email', 'rut', 'nombre', 'apellido')
    # Campos de solo lectura (no editables)
    readonly_fields = ('last_login',)
    # Campos que se usarán para ordenar por defecto
    ordering = ('email',)

    # Definición de los fieldsets (grupos de campos) para la página de edición de usuario
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('rut', 'nombre', 'apellido', 'telefono', 'direccion', 'id_comuna', 'id_tipo_usuario')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login',)}),
    )

    # Campos que se añadirán al formulario para crear un nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2', 'rut', 'nombre', 'apellido', 'telefono', 'direccion', 'id_comuna', 'id_tipo_usuario', 'is_staff', 'is_superuser', 'is_active'),
        }),
    )
    # Define los campos para la creación de un nuevo superusuario
    add_form_template = 'admin/auth/user/add_form.html'


class VentaProductoAdmin(admin.ModelAdmin):
    list_display = ('id_venta_producto', 'get_cliente_email', 'get_empleado_email', 'fecha_venta', 'total_venta', 'id_mp')
    list_filter = ('fecha_venta', 'id_mp')
    search_fields = ('id_venta_producto__exact', 'id_cliente__email', 'id_empleado__email')
    ordering = ('-fecha_venta',)
    # Usa raw_id_fields para FKs a modelos con muchos registros para mejorar la UX
    raw_id_fields = ('id_cliente', 'id_empleado', 'id_mp')

    def get_cliente_email(self, obj):
        return obj.id_cliente.email if obj.id_cliente else "N/A"
    get_cliente_email.short_description = 'Cliente'

    def get_empleado_email(self, obj):
        return obj.id_empleado.email if obj.id_empleado else "N/A"
    get_empleado_email.short_description = 'Empleado'


class EnvioAdmin(admin.ModelAdmin):
    list_display = ('id_envio', 'id_venta_producto', 'fecha_envio', 'estado_envio', 'codigo_rastreo', 'nombre_transportista', 'costo_envio')
    list_filter = ('estado_envio', 'fecha_envio', 'nombre_transportista')
    search_fields = ('id_venta_producto__id_venta_producto__exact', 'codigo_rastreo')
    # Nota: id_venta_producto es un OneToOneField, raw_id_fields no es estrictamente necesario pero es útil
    raw_id_fields = ('id_venta_producto',)


class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'nombre', 'precio_unitario', 'stock', 'id_categoria')
    list_filter = ('stock', 'id_categoria')
    search_fields = ('nombre', 'descripcion')
    raw_id_fields = ('id_categoria',)


class ServicioAdmin(admin.ModelAdmin):
    list_display = ('id_servicio', 'nombre_servicio', 'precio_servicio', 'duracion_minutos', 'disponible', 'id_proveedor_servicio')
    list_filter = ('disponible', 'id_proveedor_servicio')
    search_fields = ('nombre_servicio', 'descripcion_servicio', 'id_proveedor_servicio__email') # Asumiendo que proveedor es un Usuario
    raw_id_fields = ('id_proveedor_servicio',)


class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = ('id_detalle_boleta', 'id_venta_producto', 'id_producto', 'cantidad_adquirida', 'precio_venta_unitario', 'subtotal_detalle')
    list_filter = ('id_producto',)
    search_fields = ('id_venta_producto__id_venta_producto__exact', 'id_producto__nombre')
    raw_id_fields = ('id_venta_producto', 'id_producto')


class DetalleServicioAdquiridoAdmin(admin.ModelAdmin):
    list_display = ('id_sa', 'id_cliente', 'id_instancia_servicio', 'fecha_hora_adquisicion', 'precio_pagado', 'id_mp', 'id_venta_producto')
    list_filter = ('fecha_hora_adquisicion', 'id_mp', 'id_instancia_servicio__id_servicio')
    search_fields = ('id_cliente__email', 'id_instancia_servicio__id_servicio__nombre_servicio', 'id_venta_producto__id_venta_producto__exact')
    raw_id_fields = ('id_cliente', 'id_instancia_servicio', 'id_mp', 'id_venta_producto')


class MetodosDePagoAdmin(admin.ModelAdmin):
    list_display = ('id_mp', 'tipo_pago')
    search_fields = ('tipo_pago',)


class InstanciaServicioAdmin(admin.ModelAdmin):
    list_display = ('id_instancia_servicio', 'id_servicio', 'id_proveedor_servicio', 'fecha_hora_programada', 'reservado', 'estado_instancia')
    list_filter = ('reservado', 'estado_instancia', 'id_servicio', 'id_proveedor_servicio')
    search_fields = ('id_servicio__nombre_servicio', 'id_proveedor_servicio__email') # Asumiendo que proveedor es un Usuario
    raw_id_fields = ('id_servicio', 'id_proveedor_servicio')


class CiudadAdmin(admin.ModelAdmin):
    list_display = ('id_ciudad', 'nombre')
    search_fields = ('nombre',)


class ComunaAdmin(admin.ModelAdmin):
    list_display = ('id_comuna', 'nombre')
    search_fields = ('nombre',)


class TipoUsuarioAdmin(admin.ModelAdmin):
    list_display = ('id_tipo_usuario', 'tipo_usuario')
    search_fields = ('tipo_usuario',)


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id_categoria', 'nombre_categoria')
    search_fields = ('nombre_categoria',)


class ComentarioValoracionProductoAdmin(admin.ModelAdmin):
    list_display = ('id_comentario_valoracion', 'id_producto', 'id_usuario', 'valoracion', 'fecha_comentario')
    list_filter = ('valoracion', 'fecha_comentario', 'id_producto')
    search_fields = ('id_producto__nombre', 'id_usuario__email', 'comentario')
    raw_id_fields = ('id_producto', 'id_usuario')


# Si el modelo Mensaje es una tabla de Django (no mapeada a Oracle directamente)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'creado')
    list_filter = ('creado',)
    search_fields = ('nombre', 'correo', 'mensaje')




# ----------------------------------------------------------------------
# Registro de los modelos en el panel de administración con sus clases ModelAdmin
# ----------------------------------------------------------------------

admin.site.register(Usuario, UsuarioAdmin) # ¡Importante registrar tu modelo de usuario con su Admin!
admin.site.register(VentaProducto, VentaProductoAdmin)
admin.site.register(Envio, EnvioAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(DetalleCompra, DetalleCompraAdmin)
admin.site.register(DetalleServicioAdquirido, DetalleServicioAdquiridoAdmin)
admin.site.register(MetodosDePago, MetodosDePagoAdmin)
admin.site.register(InstanciaServicio, InstanciaServicioAdmin)
admin.site.register(Ciudad, CiudadAdmin)
admin.site.register(Comuna, ComunaAdmin)
admin.site.register(TipoUsuario, TipoUsuarioAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(ComentarioValoracionProducto, ComentarioValoracionProductoAdmin)
admin.site.register(Mensaje, MensajeAdmin) # Solo si este modelo existe y es necesario
