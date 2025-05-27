# Integracion_Proyecto/core/urls.py

from django.urls import path
from . import views # Importa todas tus vistas desde el mismo directorio

# No es necesario importar listar_clientes directamente si ya importas 'views'
# from .views import listar_clientes 

urlpatterns = [
    path('', views.index, name='index'), # Página de inicio

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
]