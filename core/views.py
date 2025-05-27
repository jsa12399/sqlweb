# Integracion_Proyecto/core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model, logout # Importa 'logout'
from django.contrib.auth.decorators import login_required # Importa el decorador para proteger vistas
from .models import Producto, Comuna, TipoUsuario # Importa también estos modelos para el registro

# Obtiene tu modelo de usuario personalizado definido en settings.py
User = get_user_model() 

# --- Vistas existentes (protegidas y ajustadas) ---

def index(request):
    return render(request, 'core/index.html')

@login_required(login_url='login') # Protege esta vista: requiere login
def nutricionista(request):
    return render(request, 'core/nutricionista.html')

@login_required(login_url='login') # Protege esta vista: requiere login
def preparadorfisico(request):
    # Aquí puedes procesar el formulario si quieres
    return render(request, 'core/preparadorfisico.html')

@login_required(login_url='login') # Protege esta vista: requiere login
def ver_productos(request):
    productos = Producto.objects.all()
    context = {
        'productos': productos
    }
    return render(request, 'core/productos.html', context)

# --- Vistas de Autenticación ---

def login_view(request):
    # Si el usuario ya está autenticado, lo redirige para que no intente loguearse de nuevo
    if request.user.is_authenticated: 
        return redirect('index')

    if request.method == "POST":
        email = request.POST.get('email') # Usa .get() para evitar KeyError si el campo no existe
        password = request.POST.get('password')
        
        # Intenta autenticar al usuario usando 'email' como username
        user = authenticate(request, username=email, password=password) 
        if user:
            # Si la autenticación es exitosa, inicia la sesión
            login(request, user)
            return redirect('index') # Redirige a la página de inicio
        else:
            # Si falla, muestra un mensaje de error
            return render(request, 'core/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'core/login.html') # Muestra el formulario de login

def register_view(request):
    # Si el usuario ya está autenticado, lo redirige para que no intente registrarse de nuevo
    if request.user.is_authenticated: 
        return redirect('index')

    if request.method == "POST":
        # Obtiene los datos del formulario
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        rut = request.POST.get('rut') 
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        telefono = request.POST.get('telefono', '') # El segundo argumento es un valor por defecto si no se envía
        direccion = request.POST.get('direccion', '')
        
        # --- MANEJO DE FOREIGN KEYS (Comuna y TipoUsuario) ---
        # Para que el registro funcione, necesitas que existan en tu DB.
        # Aquí asumimos que ID 1 para Comuna y TipoUsuario son válidos.
        # Asegúrate de que los IDs 1 (o los que elijas) existan en tus tablas COMUNA y TIPO_USUARIO de Oracle.
        try:
            # Busca la instancia de Comuna y TipoUsuario. Esto fallará si no existen en tu DB.
            comuna_default = Comuna.objects.get(id_comuna=1) 
            tipo_usuario_default = TipoUsuario.objects.get(id_tipo_usuario=1) 
        except (Comuna.DoesNotExist, TipoUsuario.DoesNotExist):
            return render(request, 'core/register.html', {'error': 'Error interno: No se encontraron valores por defecto para Comuna o Tipo de Usuario. Asegúrate de que existan registros con ID 1 en tus tablas COMUNA y TIPO_USUARIO en Oracle.'})
        # --- FIN MANEJO FOREIGN KEYS ---

        if password != confirm_password:
            return render(request, 'core/register.html', {'error': 'Las contraseñas no coinciden'})
        
        # Validaciones para que email y RUT sean únicos (muy importante)
        if User.objects.filter(email=email).exists():
            return render(request, 'core/register.html', {'error': 'Este email ya está registrado.'})
        
        if User.objects.filter(rut=rut).exists():
            return render(request, 'core/register.html', {'error': 'Este RUT ya está registrado.'})

        try:
            # Crea el usuario usando el manager personalizado de tu modelo Usuario
            user = User.objects.create_user(
                email=email,
                password=password, # El manager se encarga de hashear esto
                rut=rut,
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                direccion=direccion,
                id_comuna=comuna_default, # Pasa la instancia del objeto Comuna
                id_tipo_usuario=tipo_usuario_default, # Pasa la instancia del objeto TipoUsuario
                is_active=True, # Por defecto, el usuario estará activo al registrarse
                is_staff=False, # No es staff por defecto
                is_superuser=False, # No es superusuario por defecto
            )
            login(request, user) # Inicia sesión automáticamente después del registro
            return redirect('index') # Redirige a la página de inicio
        except Exception as e:
            # Captura cualquier otro error durante la creación del usuario
            return render(request, 'core/register.html', {'error': f'Error al registrar: {e}'})
    
    return render(request, 'core/register.html') # Muestra el formulario de registro (GET request)

def custom_logout_view(request):
    logout(request) # Cierra la sesión del usuario
    return redirect('login') # Redirige a la página de login