# Integracion_Proyecto/core/urls.py

from django.urls import path
from . import views # Importa todas tus vistas desde el mismo directorio

urlpatterns = [
    path('', views.index, name='index'), # Página de inicio
    path('nutricionista/', views.nutricionista, name='nutricionista'), # Vista de nutricionista
    path('preparadorfisico/', views.preparadorfisico, name='preparadorfisico'), # Vista de preparador físico
    
    # Rutas de autenticación
    path('login/', views.login_view, name='login'),         # Ruta para iniciar sesión
    path('register/', views.register_view, name='register'), # Ruta para registrarse
    path('logout/', views.custom_logout_view, name='logout'), # ¡NUEVA RUTA para cerrar sesión!
    
    path('productos/', views.ver_productos, name='productos'), # Vista de productos
]