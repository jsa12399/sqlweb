# Integracion_Proyecto/core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required, user_passes_test # <<-- ¡MUY IMPORTANTE: user_passes_test!
# Asegúrate de importar TODOS los modelos que usas o podrías usar en tus vistas.
# Si tienes más modelos relacionados, añádelos aquí.
from .models import Producto, Comuna, TipoUsuario, Servicio, InstanciaServicio, DetalleServicioAdquirido 

# Para la API de clientes, si aún la necesitas
import requests

User = get_user_model() # Obtiene tu modelo de usuario personalizado

# --- Funciones de Test para Decoradores (para roles) ---
# ESTAS FUNCIONES SON CLAVE PARA EL CONTROL DE ACCESO.
# Utilizan los IDs de TipoUsuario que definimos en la Fase 1 de la DB:
# 1 = Administrador, 2 = Nutricionista, 3 = Preparador Físico, 4 = Cliente

def is_administrador(user):
    """Verifica si el usuario es un Administrador (ID 1)."""
    try:
        return user.is_authenticated and user.id_tipo_usuario.id_tipo_usuario == 1
    except AttributeError: 
        return False

def is_nutricionista(user):
    """Verifica si el usuario es un Nutricionista (ID 2)."""
    try:
        return user.is_authenticated and user.id_tipo_usuario.id_tipo_usuario == 2
    except AttributeError:
        return False

def is_preparador_fisico(user):
    """Verifica si el usuario es un Preparador Físico (ID 3)."""
    try:
        return user.is_authenticated and user.id_tipo_usuario.id_tipo_usuario == 3
    except AttributeError:
        return False

def is_cliente(user):
    """Verifica si el usuario es un Cliente (ID 4)."""
    try:
        return user.is_authenticated and user.id_tipo_usuario.id_tipo_usuario == 4
    except AttributeError:
        return False

# --- Vistas Públicas y de Autenticación (con ajustes CRÍTICOS) ---

def index(request):
    return render(request, 'core/index.html')

@login_required(login_url='login') # Protege esta vista: requiere login
def nutricionista_publica(request): # <<-- ¡RENOMBRADO!
    return render(request, 'core/nutricionista.html')

@login_required(login_url='login') # Protege esta vista: requiere login
def preparadorfisico_publica(request): # <<-- ¡RENOMBRADO!
    return render(request, 'core/preparadorfisico.html')

@login_required(login_url='login') # Protege esta vista: requiere login
def ver_productos(request):
    productos = Producto.objects.all()
    context = {
        'productos': productos
    }
    return render(request, 'core/productos.html', context)

def login_view(request):
    # Si el usuario ya está autenticado, lo redirige para que no intente loguearse de nuevo
    if request.user.is_authenticated: 
        # Redirección específica por rol después de iniciar sesión
        if is_nutricionista(request.user):
            return redirect('panel_nutricionista')
        # Puedes añadir más redirecciones para otros roles aquí
        # elif is_preparador_fisico(request.user):
        #     return redirect('panel_preparadorfisico') 
        # elif is_administrador(request.user):
        #     return redirect('panel_admin') 
        else: # Por defecto (cliente o roles no definidos sin panel específico)
            return redirect('index')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password) 
        if user:
            login(request, user)
            # Redirección específica por rol después de iniciar sesión (post-autenticación)
            if is_nutricionista(user):
                return redirect('panel_nutricionista')
            # elif is_preparador_fisico(user):
            #     return redirect('panel_preparadorfisico')
            # elif is_administrador(user):
            #     return redirect('panel_admin')
            else:
                return redirect('index') # Redirige a la página de inicio por defecto
        else:
            return render(request, 'core/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'core/login.html') # Muestra el formulario de login

def register_view(request):
    # Si el usuario ya está autenticado, lo redirige para que no intente registrarse de nuevo
    if request.user.is_authenticated: 
        return redirect('index')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        rut = request.POST.get('rut') 
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        telefono = request.POST.get('telefono', '')
        direccion = request.POST.get('direccion', '')

        # --- MANEJO DE FOREIGN KEYS (Comuna y TipoUsuario) ---
        # ¡IMPORTANTE! Aquí se asigna el TipoUsuario por defecto para un NUEVO CLIENTE
        # Basado en la configuración de la DB que hicimos en la Fase 1: ID 4 para 'Cliente'
        try:
            comuna_default = Comuna.objects.get(id_comuna=1) 
            tipo_usuario_default = TipoUsuario.objects.get(id_tipo_usuario=4) # <<-- ¡CAMBIO CRÍTICO!
        except (Comuna.DoesNotExist, TipoUsuario.DoesNotExist):
            return render(request, 'core/register.html', {'error': 'Error interno: No se encontraron valores por defecto para Comuna o Tipo de Usuario. Asegúrate de que existan registros con ID 1 en COMUNA y ID 4 en TIPO_USUARIO en Oracle.'})
        # --- FIN MANEJO FOREIGN KEYS ---

        if password != confirm_password:
            return render(request, 'core/register.html', {'error': 'Las contraseñas no coinciden'})

        if User.objects.filter(email=email).exists():
            return render(request, 'core/register.html', {'error': 'Este email ya está registrado.'})

        if User.objects.filter(rut=rut).exists():
            return render(request, 'core/register.html', {'error': 'Este RUT ya está registrado.'})

        try:
            user = User.objects.create_user(
                email=email,
                password=password, # El manager se encarga de hashear esto
                rut=rut,
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                direccion=direccion,
                id_comuna=comuna_default, # Pasa la instancia del objeto Comuna
                id_tipo_usuario=tipo_usuario_default, # Pasa la instancia del objeto TipoUsuario (¡ahora Cliente!)
                is_active=True,
                is_staff=False,
                is_superuser=False,
            )
            login(request, user) # Inicia sesión automáticamente después del registro
            return redirect('index') # Redirige a la página de inicio
        except Exception as e:
            return render(request, 'core/register.html', {'error': f'Error al registrar: {e}'})

    return render(request, 'core/register.html') # Muestra el formulario de registro (GET request)

def custom_logout_view(request):
    logout(request) # Cierra la sesión del usuario
    return redirect('login') # Redirige a la página de login

# --- NUEVA VISTA PARA EL PANEL DE NUTRICIONISTA ---
# ESTA VISTA ES LA QUE PROTEGE Y MUESTRA EL PANEL AL NUTRICIONISTA

@login_required(login_url='login') # Requiere que el usuario esté logueado
@user_passes_test(is_nutricionista, login_url='index') # <<-- ¡CLAVE! Solo Nutricionistas (ID 2) pueden acceder
def panel_nutricionista(request):
    nutricionista_obj = request.user # El usuario autenticado es el nutricionista (una instancia de tu modelo Usuario)

    # Obtener los servicios que este nutricionista ha publicado
    # Asegúrate de que el campo en tu modelo Servicio sea 'id_proveedor_servicio'
    mis_servicios = Servicio.objects.filter(id_proveedor_servicio=nutricionista_obj).order_by('nombre_servicio')

    # Obtener las instancias de servicio (citas/horarios) programadas por este nutricionista
    # Asegúrate de que el campo en tu modelo InstanciaServicio sea 'id_proveedor_servicio'
    mis_instancias = InstanciaServicio.objects.filter(id_proveedor_servicio=nutricionista_obj).order_by('fecha_hora_programada')

    context = {
        'nutricionista': nutricionista_obj,
        'mis_servicios': mis_servicios,
        'mis_instancias': mis_instancias,
    }
    return render(request, 'core/panel_nutricionista.html', context)


# --- APIS (Las que ya tenías) ---
def listar_clientes(request):
    try:
        url = "https://api-sabor-latino-chile.onrender.com/clientes"
        response = requests.get(url)
        response.raise_for_status()
        clientes = response.json()
    except requests.RequestException as e:
        print("Error al conectar con la API:", e)
        clientes = []

    return render(request, 'core/clientes.html', {'clientes': clientes})