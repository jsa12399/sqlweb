# Integracion_Proyecto/core/urls.py

from django.urls import path
from django.contrib import admin
from . import views # Importa todas tus vistas desde el mismo directorio
from django.urls import path, include 
urlpatterns = [
    
    path('', views.index, name='index'),

    # URLs preparador físico
    path('panel_preparador_fisico/', views.panel_preparador_fisico, name='panel_preparador_fisico'),
    path('preparador/servicios/', views.preparador_servicios_list, name='preparador_servicios_list'), # Esta vista ya existe, pero asegúrate de que esté definida.
    path('preparador/servicios/crear/', views.preparador_servicio_crear, name='preparador_servicio_crear'), # Esta vista ya existe, pero asegúrate de que esté definida.
    path('preparador/servicios/editar/<int:id_servicio>/', views.preparador_servicio_editar, name='preparador_servicio_editar'), # Usa id_servicio como parámetro
    path('preparador/servicios/eliminar/<int:id_servicio>/', views.preparador_servicio_eliminar, name='preparador_servicio_eliminar'), # Usa id_servicio como parámetro
    

    
    path('preparador/instancias/', views.preparador_instancias_programadas, name='preparador_instancias_programadas'), # Agregada esta URL

    

    # Vistas públicas para nutricionista y preparador físico
    path('nutricionista/', views.nutricionista_publica, name='nutricionista'),
    path('preparadorfisico/', views.preparadorfisico_publica, name='preparadorfisico'),

    # Rutas de autenticación
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.custom_logout_view, name='logout'),

    path('productos/', views.ver_productos, name='productos'),

    path('clientes/', views.listar_clientes, name='listar_clientes'),

    # Rutas del panel de nutricionista
    path('nutricionista/panel/', views.panel_nutricionista, name='panel_nutricionista'),
    path('nutricionista/servicios/', views.nutricionista_servicios_list, name='nutricionista_servicios_list'),
    path('nutricionista/servicios/crear/', views.nutricionista_servicio_crear, name='nutricionista_servicio_crear'),
    path('nutricionista/servicios/editar/<int:id_servicio>/', views.nutricionista_servicio_editar, name='nutricionista_servicio_editar'),
    path('nutricionista/servicios/eliminar/<int:id_servicio>/', views.nutricionista_servicio_eliminar, name='nutricionista_servicio_eliminar'),
    path('nutricionista/instancias/', views.nutricionista_instancias_programadas, name='nutricionista_instancias_programadas'),
    # Rutas del carrito y checkout
    path('carrito/', views.carrito_view, name='carrito'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('pago_exitoso/', views.pago_exitoso_view, name='pago_exitoso'),
    path('pago-exitoso/<int:venta_id>/', views.pago_exitoso_view, name='pago_exitoso'),
    # Rutas para el cliente
    path('cliente/servicios/', views.cliente_ver_servicios, name='cliente_ver_servicios'),
    path('mis-servicios/', views.mis_servicios_view, name='mis_servicios'),

    # Nueva ruta para el estado del descuento (API endpoint)
    path('get-discount-status/', views.get_discount_status, name='get_discount_status'),
    #valoracion producto
    path('productos/<int:id_producto>/', views.detalle_producto, name='detalle_producto'),
    #seguimiento
    path('seguimiento/<int:venta_id>/', views.seguimiento_pedido, name='seguimiento_pedido'),

    
   
]