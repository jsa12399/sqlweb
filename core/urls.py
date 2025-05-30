# Integracion_Proyecto/core/urls.py

from django.urls import path
from . import views # Importa todas tus vistas desde el mismo directorio

# No es necesario importar listar_clientes directamente si ya importas 'views'
# from .views import listar_clientes 

urlpatterns = [
    path('', views.index, name='index'), # Página de inicio


      # URLs preparador físico
     path('panel_preparadorfisico/', views.panel_nutricionista, name='panel_preparadorfisico'),  
    path('lista_servicios_pf/', views.lista_servicios_pf, name='lista_servicios_pf'),
    path('crear_servicio_pf/', views.crear_servicio_pf, name='crear_servicio_pf'),
    path('editar_servicio_pf/', views.editar_servicio_pf, name='editar_servicio_pf'),
    path('eliminar_servicio_pf/', views.confirmar_eliminar_pf, name='eliminar_servicio_pf'),

    path('lista_mensajes_pf/', views.lista_servicios_pf, name='lista_mensajes_pf'),
    path('detalle_mensaje_pf/', views.detalle_mensaje_pf, name='detalle_mensaje_pf'),

    # <<-- ¡CAMBIO CRÍTICO! Vistas renombradas para evitar conflictos
    path('nutricionista/', views.nutricionista_publica, name='nutricionista'), 
    path('preparadorfisico/', views.preparadorfisico_publica, name='preparadorfisico'), 

    # Rutas de autenticación
    path('login/', views.login_view, name='login'),  # Ruta para iniciar sesión
    path('register/', views.register_view, name='register'), # Ruta para registrarse
    path('logout/', views.custom_logout_view, name='logout'), # Ruta para cerrar sesión

    path('productos/', views.ver_productos, name='productos'), # Vista de productos

    # <<-- Consistencia: usando views.listar_clientes
    path('clientes/', views.listar_clientes, name='listar_clientes'), 

    # --- NUEVA RUTA PARA EL PANEL DE NUTRICIONISTA ---
    path('nutricionista/panel/', views.panel_nutricionista, name='panel_nutricionista'),
    path('nutricionista/servicios/', views.nutricionista_servicios_list, name='nutricionista_servicios_list'),
    path('nutricionista/servicios/crear/', views.nutricionista_servicio_crear, name='nutricionista_servicio_crear'),
    path('nutricionista/servicios/editar/<int:id_servicio>/', views.nutricionista_servicio_editar, name='nutricionista_servicio_editar'),
    path('nutricionista/servicios/eliminar/<int:id_servicio>/', views.nutricionista_servicio_eliminar, name='nutricionista_servicio_eliminar'),
    path('carrito/', views.carrito_view, name='carrito'),
    path('cliente/servicios/', views.cliente_ver_servicios, name='cliente_ver_servicios'),
    path('cliente/servicios/adquirir/<int:servicio_id>/', views.cliente_adquirir_servicio, name='cliente_adquirir_servicio'),
   path('mis-servicios/', views.mis_servicios_view, name='mis_servicios'),# Para que el cliente vea sus compras
    
]