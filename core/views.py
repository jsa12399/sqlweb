# Integracion_Proyecto/core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone # Aunque no lo uses ahora, es bueno tenerlo si trabajas con fechas/horas

# Asegúrate de importar TODOS los modelos y formularios que usas.
from .models import Producto, Comuna, TipoUsuario, Servicio, InstanciaServicio, DetalleServicioAdquirido
from .forms import ServicioForm

# Para la API de clientes, si aún la necesitas
import requests

User = get_user_model() # Obtiene tu modelo de usuario personalizado

# --- Funciones de Test para Decoradores (para roles) ---
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

# --- Vistas Públicas y de Autenticación ---

def index(request):
    print(f"DEBUG en index: User autenticado: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        try:
            print(f"DEBUG en index: Tipo de usuario (del modelo): {request.user.id_tipo_usuario.tipo_usuario}")
            print(f"DEBUG en index: ID de tipo de usuario: {request.user.id_tipo_usuario.id_tipo_usuario}")
        except AttributeError:
            print(f"DEBUG en index: Tipo de usuario: N/A (o no disponible, puede que id_tipo_usuario sea None)")
    return render(request, 'core/index.html')

@login_required(login_url='login')
def nutricionista_publica(request):
    return render(request, 'core/nutricionista.html')

@login_required(login_url='login')
def preparadorfisico_publica(request):
    return render(request, 'core/preparadorfisico.html')

@login_required(login_url='login')
def ver_productos(request):
    print(f"DEBUG en ver_productos: User autenticado: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        try:
            print(f"DEBUG en ver_productos: Tipo de usuario (del modelo): {request.user.id_tipo_usuario.tipo_usuario}")
            print(f"DEBUG en ver_productos: ID de tipo de usuario: {request.user.id_tipo_usuario.id_tipo_usuario}")
        except AttributeError:
            print(f"DEBUG en ver_productos: Tipo de usuario: N/A (o no disponible, puede que id_tipo_usuario sea None)")
    productos = Producto.objects.all()
    context = {
        'productos': productos
    }
    return render(request, 'core/productos.html', context)

def login_view(request):
    if request.user.is_authenticated:
        if is_nutricionista(request.user):
            return redirect('panel_nutricionista')
        else:
            return redirect('index')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            if is_nutricionista(user):
                return redirect('panel_nutricionista')
            else:
                return redirect('index')
        else:
            return render(request, 'core/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'core/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        rut = request.POST.get('rut')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')

        try:
            comuna_default = Comuna.objects.get(id_comuna=1)
            tipo_usuario_default = TipoUsuario.objects.get(id_tipo_usuario=4) # Cliente por defecto
        except (Comuna.DoesNotExist, TipoUsuario.DoesNotExist):
            return render(request, 'core/register.html', {'error': 'Error interno: No se encontraron valores por defecto para Comuna o Tipo de Usuario. Asegúrate de que existan registros con ID 1 en COMUNA y ID 4 en TIPO_USUARIO en Oracle.'})

        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                rut=rut,
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                direccion=direccion,
                id_comuna=comuna_default,
                id_tipo_usuario=tipo_usuario_default,
                is_active=True,
                is_staff=False,
                is_superuser=False,
            )
            login(request, user)
            return redirect('index')
        except Exception as e:
            return render(request, 'core/register.html', {'error': f'Error al registrar: {e}'})

    return render(request, 'core/register.html')

def custom_logout_view(request):
    logout(request)
    return redirect('login')

# --- VISTA PARA EL PANEL DE NUTRICIONISTA ---
@login_required(login_url='login')
@user_passes_test(is_nutricionista, login_url='index')
def panel_nutricionista(request):
    print(f"DEBUG en panel_nutricionista: User autenticado: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        try:
            print(f"DEBUG en panel_nutricionista: Tipo de usuario (del modelo): {request.user.id_tipo_usuario.tipo_usuario}")
            print(f"DEBUG en panel_nutricionista: ID de tipo de usuario: {request.user.id_tipo_usuario.id_tipo_usuario}")
        except AttributeError:
            print(f"DEBUG en panel_nutricionista: Tipo de usuario: N/A (o no disponible, puede que id_tipo_usuario sea None)")

    nutricionista_obj = request.user
    mis_servicios = Servicio.objects.filter(id_proveedor_servicio=nutricionista_obj).order_by('nombre_servicio')
    mis_instancias = InstanciaServicio.objects.filter(id_proveedor_servicio=nutricionista_obj).order_by('fecha_hora_programada')

    context = {
        'nutricionista': nutricionista_obj,
        'mis_servicios': mis_servicios,
        'mis_instancias': mis_instancias,
    }
    return render(request, 'core/panel_nutricionista.html', context)


# --- Vistas para la Gestión de Servicios del Nutricionista ---

@login_required(login_url='login')
@user_passes_test(is_nutricionista, login_url='index')
def nutricionista_servicios_list(request):
    print(f"DEBUG en nutricionista_servicios_list: User autenticado: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        try:
            print(f"DEBUG en nutricionista_servicios_list: Tipo de usuario (del modelo): {request.user.id_tipo_usuario.tipo_usuario}")
            print(f"DEBUG en nutricionista_servicios_list: ID de tipo de usuario: {request.user.id_tipo_usuario.id_tipo_usuario}")
        except AttributeError:
            print(f"DEBUG en nutricionista_servicios_list: Tipo de usuario: N/A (o no disponible, puede que id_tipo_usuario sea None)")

    mis_servicios = Servicio.objects.filter(id_proveedor_servicio=request.user).order_by('nombre_servicio')
    context = {
        'mis_servicios': mis_servicios
    }
    return render(request, 'core/nutricionista_servicios_list.html', context)


@login_required(login_url='login')
@user_passes_test(is_nutricionista, login_url='index')
def nutricionista_servicio_crear(request):
    print(f"DEBUG: Método de la solicitud: {request.method}")

    if request.method == 'POST':
        form = ServicioForm(request.POST)
        print(f"DEBUG: Datos del formulario recibidos (request.POST): {request.POST}") # Ver qué se envía desde el formulario

        if form.is_valid():
            print("DEBUG: El formulario es válido.")
            servicio = form.save(commit=False) # Crea el objeto Servicio, pero no lo guarda aún en la DB

            print(f"DEBUG: Servicio.disponible obtenido del formulario (antes de asignar proveedor): {servicio.disponible}")

            servicio.id_proveedor_servicio = request.user # Asigna el nutricionista logueado
            
            # ¡VERIFICACIÓN CRÍTICA! Asegúrate de que no haya ninguna línea aquí que sobrescriba servicio.disponible.
            # Si ves algo como:
            # servicio.disponible = 'N'
            # servicio.disponible = '0'
            # O alguna condición que lo fuerce, DEBÉS ELIMINARLA O COMENTARLA.

            print(f"DEBUG: Servicio.disponible *después* de form.save(commit=False) y asignación del proveedor: {servicio.disponible}")

            try:
                servicio.save(using=servicio._state.db) # Guarda el servicio en la DB Oracle
                print(f"DEBUG: Servicio '{servicio.nombre_servicio}' (ID: {servicio.id_servicio}) guardado exitosamente por {request.user.email} con disponible='{servicio.disponible}'")
                return redirect('nutricionista_servicios_list')
            except Exception as e:
                print(f"ERROR: No se pudo guardar el servicio: {e}")
                form.add_error(None, f"Error al guardar el servicio en la base de datos: {e}")
        else:
            print(f"DEBUG: El formulario NO es válido. Errores: {form.errors}")
    else:
        form = ServicioForm()
        print("DEBUG: Solicitud GET, creando formulario vacío.")
    
    return render(request, 'core/nutricionista_servicio_form.html', {'form': form})



# --- APIS (Las que ya tenías) ---
def listar_clientes(request):
    print(f"DEBUG en listar_clientes: User autenticado: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        try:
            print(f"DEBUG en listar_clientes: Tipo de usuario (del modelo): {request.user.id_tipo_usuario.tipo_usuario}")
            print(f"DEBUG en listar_clientes: ID de tipo de usuario: {request.user.id_tipo_usuario.id_tipo_usuario}")
        except AttributeError:
            print(f"DEBUG en listar_clientes: Tipo de usuario: N/A (o no disponible, puede que id_tipo_usuario sea None)")

    try:
        url = "https://api-sabor-latino-chile.onrender.com/clientes"
        response = requests.get(url)
        response.raise_for_status()
        clientes = response.json()
    except requests.RequestException as e:
        print("Error al conectar con la API:", e)
        clientes = []

    return render(request, 'core/clientes.html', {'clientes': clientes})


URL = "https://api-sabor-latino-chile.onrender.com"

def buscarAlumno(numrut):
    respuesta = requests.get(f"{URL}/clientes")
    if respuesta.status_code == 200:
        
        for e in respuesta.json():
            if int(e['numero_rut'])==numrut:
                return True
        return False
    else:
        print("❌ Error en el servidor de la api")
        return False

# print(buscarAlumno(1)) # Comenté esta línea ya que no debería ejecutarse en cada carga de vistas.