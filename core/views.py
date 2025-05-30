from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse
import json 
from django.urls import reverse

# Importa todos los modelos y formularios necesarios.
from .models import Servicio, Mensaje, Usuario, MetodosDePago, Producto, Comuna, TipoUsuario, InstanciaServicio, DetalleServicioAdquirido,VentaProducto,DetalleCompra
from .forms import ServicioForm

import requests # Para las integraciones con APIs externas
from django.db import connection # Importación que tenías, mantenida aunque no se usa en el código visible.

# Obtiene el modelo de usuario personalizado que estás usando en Django.
User = get_user_model()

# --- Funciones Auxiliares para Verificación de Tipo de Usuario ---
# Estas funciones se usan con el decorador @user_passes_test para controlar el acceso a vistas.

def is_administrador(user):
    """Verifica si el usuario es un Administrador (ID 1)."""
    return user.is_authenticated and user.id_tipo_usuario_id == 1 if user.id_tipo_usuario_id else False

def is_nutricionista(user):
    """Verifica si el usuario es un Nutricionista (ID 2)."""
    return user.is_authenticated and user.id_tipo_usuario_id == 2 if user.id_tipo_usuario_id else False

def is_preparador_fisico(user):
    """Verifica si el usuario es un Preparador Físico (ID 3)."""
    return user.is_authenticated and user.id_tipo_usuario_id == 3 if user.id_tipo_usuario_id else False

def is_cliente(user):
    """Verifica si el usuario es un Cliente (ID 4)."""
    return user.is_authenticated and user.id_tipo_usuario_id == 4 if user.id_tipo_usuario_id else False

# --- Vistas del Panel del Preparador Físico (Manteniendo la estructura original que tenías) ---
# Nota: Los nombres de estas vistas (panel_nutricionista, lista_servicios_pf, etc.)
# sugieren que estaban siendo reutilizadas o tenían un origen confuso con el rol de nutricionista.
# He mantenido los nombres que tenías para no alterar tus URLs o plantillas.

# Esta vista no tiene decoradores de autenticación o tipo de usuario,
# lo que significa que es accesible públicamente.
# Si debe ser privada, añade @login_required y @user_passes_test.
def lista_servicios_pf(request):
    """Muestra una lista de todos los servicios disponibles para el preparador físico."""
    servicios = Servicio.objects.all()
    return render(request, 'core/preparador/lista_servicios_pf.html', {'servicios': servicios})

def crear_servicio_pf(request):
    """Permite al preparador físico crear un nuevo servicio."""
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_servicios_pf')
    else:
        form = ServicioForm()
    return render(request, 'core/preparador/lista_servicios_pf_crear.html', {'form': form})

def editar_servicio_pf(request):
    """Permite al preparador físico editar un servicio existente."""
    pk = request.GET.get('id') # Obtiene el ID del servicio de los parámetros de la URL (ej. ?id=1)
    servicio = get_object_or_404(Servicio, pk=pk) # Busca el servicio por su clave primaria o devuelve 404
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect('lista_servicios_pf')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'core/preparador/servicio_form_pf.html', {'form': form})

def confirmar_eliminar_pf(request):
    """Muestra una página de confirmación para eliminar un servicio del preparador físico."""
    pk = request.GET.get('id') # Obtiene el ID del servicio de los parámetros de la URL (ej. ?id=1)
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        servicio.delete()
        return redirect('lista_servicios_pf')
    return render(request, 'core/preparador/confirmar_eliminar_pf.html', {'servicio': servicio})

def lista_mensajes_pf(request):
    """Muestra una lista de todos los mensajes (generalmente para el preparador físico)."""
    mensajes = Mensaje.objects.all()
    return render(request, 'core/preparador/lista_mensajes_pf.html', {'mensajes': mensajes})

def detalle_mensaje_pf(request, pk):
    """Muestra el detalle de un mensaje específico."""
    mensaje = get_object_or_404(Mensaje, pk=pk)
    return render(request, 'core/preparador/detalle_mensaje_pf.html', {'mensaje': mensaje})

# --- Vistas Públicas y de Autenticación ---

def index(request):
    """Vista de la página de inicio que muestra productos destacados y depuración de usuario."""
    print(f"DEBUG en index: User autenticado: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        try:
            print(f"DEBUG en index: Tipo de usuario (del modelo): {request.user.id_tipo_usuario.tipo_usuario}")
            print(f"DEBUG en index: ID de tipo de usuario: {request.user.id_tipo_usuario.id_tipo_usuario}")
        except AttributeError:
            print(f"DEBUG en index: Tipo de usuario: N/A (o no disponible, puede que id_tipo_usuario sea None)")

    productos_destacados = Producto.objects.all()[:3] # Obtiene los primeros 3 productos.
    return render(request, 'core/index.html', {'productos': productos_destacados})

@login_required(login_url='login')
def nutricionista_publica(request):
    """Muestra los servicios disponibles ofrecidos por nutricionistas."""
    print(f"DEBUG en nutricionista_publica: User autenticado: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        try:
            print(f"DEBUG en nutricionista_publica: Tipo de usuario (del modelo): {request.user.id_tipo_usuario.tipo_usuario}")
            print(f"DEBUG en nutricionista_publica: ID de tipo de usuario: {request.user.id_tipo_usuario.id_tipo_usuario}")
        except AttributeError:
            print(f"DEBUG en nutricionista_publica: Tipo de usuario: N/A (o no disponible, puede que id_tipo_usuario sea None)")

    servicios_a_mostrar = Servicio.objects.none() # Inicializa un queryset vacío.

    try:
        tipo_nutricionista = TipoUsuario.objects.get(id_tipo_usuario=2) # Obtiene el objeto TipoUsuario 'Nutricionista' (ID 2).
        ids_nutricionistas = Usuario.objects.filter(id_tipo_usuario=tipo_nutricionista).values_list('id_usuario', flat=True) # Obtiene los IDs de los usuarios nutricionistas.
        
        # Filtra los servicios que son de nutricionistas y están disponibles.
        servicios_a_mostrar = Servicio.objects.filter(
            id_proveedor_servicio__in=ids_nutricionistas,
            disponible='S'
        ).order_by('id_proveedor_servicio__nombre', 'nombre_servicio')

        print(f"DEBUG: Se encontraron {servicios_a_mostrar.count()} servicios de nutricionistas disponibles.")
        for s in servicios_a_mostrar:
            print(f"DEBUG: Servicio: {s.nombre_servicio}, Proveedor: {s.id_proveedor_servicio.nombre} {s.id_proveedor_servicio.apellido}, Disponible: {s.disponible}")

    except TipoUsuario.DoesNotExist:
        print("ERROR: El TipoUsuario 'Nutricionista' (ID 2) no existe en la base de datos. No se pueden mostrar servicios de nutricionistas.")
    except Exception as e:
        print(f"ERROR: Ocurrió un error al obtener los servicios de nutricionistas: {e}")

    context = {
        'servicios_nutricionista': servicios_a_mostrar
    }

    if request.method == 'POST':
        print("DEBUG: Datos de inscripción (formulario) recibidos en nutricionista_publica (POST):")
        print(request.POST)
        pass # Lógica para procesar el formulario POST, si existe.

    return render(request, 'core/nutricionista.html', context)

@login_required(login_url='login')
def preparadorfisico_publica(request):
    """Muestra información sobre servicios de preparador físico."""
    # Busca un servicio cuyo nombre contenga 'Preparador Físico' (case-insensitive) y obtiene el primero.
    servicio_preparador_fisico = Servicio.objects.filter(nombre_servicio__icontains='Preparador Físico').first()

    context = {
        'servicio_preparador_fisico': servicio_preparador_fisico
    }
    return render(request, 'core/preparadorfisico.html', context)

@login_required(login_url='login')
def ver_productos(request):
    """Muestra una lista de todos los productos disponibles."""
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

def carrito_view(request):
    """Renderiza la vista del carrito de compras."""
    return render(request, 'core/carrito.html')

@login_required(login_url='login')
def checkout_view(request):
    """Renderiza la vista de checkout y maneja una simulación de POST."""
    if request.method == 'POST':
        print("DEBUG: Solicitud POST recibida en checkout_view (funcionalidad deshabilitada).")
        # Simula una redirección a una página de pago exitoso.
        return redirect('pago_exitoso')
    return render(request, 'core/checkout.html')

def pago_exitoso_view(request):
    """Vista de confirmación de pago exitoso."""
    return render(request, 'core/pago_exitoso.html')

@login_required(login_url='login')
@user_passes_test(is_cliente, login_url='index')
def mis_servicios_view(request):
    """Muestra los servicios que el usuario (cliente) ha adquirido."""
    # Filtra los servicios adquiridos por el cliente actual y optimiza las consultas relacionadas.
    servicios_adquiridos = DetalleServicioAdquirido.objects.filter(id_cliente=request.user).select_related('id_instancia_servicio__id_servicio', 'id_instancia_servicio__id_proveedor_servicio')
    context = {
        'servicios_adquiridos': servicios_adquiridos
    }
    return render(request, 'core/mis_servicios.html', context)

def login_view(request):
    """Maneja el inicio de sesión de usuarios y los redirige según su tipo."""
    if request.user.is_authenticated:
        # Redirige a paneles específicos si el usuario ya está autenticado.
        if is_nutricionista(request.user):
            return redirect('panel_nutricionista')
        elif is_preparador_fisico(request.user):
            return redirect('panel_preparador_fisico')
        else:
            return redirect('index')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password) # Intenta autenticar al usuario.
        if user:
            login(request, user) # Inicia sesión si la autenticación es exitosa.
            # Redirige a paneles específicos según el tipo de usuario.
            if is_nutricionista(user):
                return redirect('panel_nutricionista')
            elif is_preparador_fisico(user):
                return redirect('panel_preparador_fisico')
            else:
                return redirect('index')
        else:
            # Muestra un error si las credenciales son inválidas.
            return render(request, 'core/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'core/login.html')

def register_view(request):
    """Maneja el registro de nuevos usuarios."""
    if request.user.is_authenticated:
        return redirect('index') # Si el usuario ya está autenticado, lo redirige.

    comunas = Comuna.objects.all() # Obtiene todas las comunas para el formulario de registro.
    # Obtiene todos los tipos de usuario, excluyendo al Administrador (ID 1),
    # ya que no debería poder auto-registrarse como administrador.
    tipos_usuario = TipoUsuario.objects.all().exclude(id_tipo_usuario__in=[1])

    if request.method == "POST":
        # Recopila los datos del formulario POST.
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        rut = request.POST.get('rut')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        comuna_id = request.POST.get('comuna_id')
        tipo_usuario_id = request.POST.get('tipo_usuario_id')

        # --- Validación Básica del Formulario ---
        if not email or not password or not rut or not nombre or not apellido or not tipo_usuario_id:
            messages.error(request, 'Por favor, completa todos los campos requeridos.')
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario})

        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario})

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este email ya está registrado.')
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario})

        if Usuario.objects.filter(rut=rut).exists():
            messages.error(request, 'Este RUT ya está registrado.')
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario})

        try:
            # Intenta obtener los objetos Comuna y TipoUsuario.
            comuna = Comuna.objects.get(id_comuna=comuna_id) if comuna_id else None
            selected_tipo_usuario = TipoUsuario.objects.get(id_tipo_usuario=tipo_usuario_id)

        except Comuna.DoesNotExist:
            messages.error(request, 'La comuna seleccionada no es válida.')
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario})
        except TipoUsuario.DoesNotExist:
            messages.error(request, 'El tipo de usuario seleccionado no es válido.')
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario})
        except Exception as e:
            messages.error(request, f'Error al obtener datos de registro: {e}. Asegúrate que la Comuna y el Tipo de Usuario existan.')
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario})

        try:
            # Crea el nuevo usuario utilizando el manager personalizado de tu modelo Usuario.
            user = Usuario.objects.create_user(
                email=email,
                password=password,
                rut=rut,
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                direccion=direccion,
                id_comuna=comuna,
                id_tipo_usuario=selected_tipo_usuario,
                is_active=True, # El usuario está activo por defecto.
                is_staff=False, # No es miembro del staff por defecto.
                is_superuser=False, # No es superusuario por defecto.
            )
            login(request, user) # Inicia sesión al usuario recién registrado.
            messages.success(request, 'Registro exitoso. ¡Bienvenido!')
            return redirect('index') # Redirige al índice después del registro.
        except Exception as e:
            messages.error(request, f'Error al registrar el usuario: {e}')
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario})

    # Para solicitudes GET, renderiza el formulario de registro vacío.
    return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario})

def custom_logout_view(request):
    """Cierra la sesión del usuario y lo redirige a la página de login."""
    logout(request)
    return redirect('login')

# --- VISTA PARA EL PANEL DE NUTRICIONISTA ---
@login_required(login_url='login')
@user_passes_test(is_nutricionista, login_url='index')
def panel_nutricionista(request):
    """Muestra el panel de control para los nutricionistas, incluyendo sus servicios y clientes."""
    print(f"DEBUG en panel_nutricionista: User autenticado: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        try:
            print(f"DEBUG en panel_nutricionista: Tipo de usuario (del modelo): {request.user.id_tipo_usuario.tipo_usuario}")
            print(f"DEBUG en panel_nutricionista: ID de tipo de usuario: {request.user.id_tipo_usuario.id_tipo_usuario}")
        except AttributeError:
            print(f"DEBUG en panel_nutricionista: Tipo de usuario: N/A (o no disponible, puede que id_tipo_usuario sea None)")

    nutricionista_obj = request.user # El usuario autenticado es el nutricionista.
    mis_servicios = Servicio.objects.filter(id_proveedor_servicio=nutricionista_obj).order_by('nombre_servicio') # Servicios que ofrece este nutricionista.
    mis_instancias = InstanciaServicio.objects.filter(id_servicio__in=mis_servicios) # Instancias de esos servicios.
    # Inscripciones de clientes a estas instancias de servicio.
    inscripciones_clientes = DetalleServicioAdquirido.objects.filter(
        id_instancia_servicio__in=mis_instancias
    ).select_related('id_cliente', 'id_instancia_servicio__id_servicio')

    context = {
        'nutricionista': nutricionista_obj,
        'mis_servicios': mis_servicios,
        'mis_instancias': mis_instancias,
        'inscripciones_clientes': inscripciones_clientes,
    }
    return render(request, 'core/panel_nutricionista.html', context)

# --- VISTA PARA EL PANEL DE PREPARADOR FÍSICO ---
@login_required(login_url='login')
@user_passes_test(is_preparador_fisico, login_url='index')
def panel_preparador_fisico(request):
    """Muestra el panel de control para los preparadores físicos, incluyendo sus servicios y clientes."""
    print(f"DEBUG en panel_preparador_fisico: User autenticado: {request.user.is_authenticated}")
    if request.user.is_authenticated:
        try:
            print(f"DEBUG en panel_preparador_fisico: Tipo de usuario (del modelo): {request.user.id_tipo_usuario.tipo_usuario}")
            print(f"DEBUG en panel_preparador_fisico: ID de tipo de usuario: {request.user.id_tipo_usuario.id_tipo_usuario}")
        except AttributeError:
            print(f"DEBUG en panel_preparador_fisico: Tipo de usuario: N/A (o no disponible, puede que id_tipo_usuario sea None)")

    preparador_obj = request.user # El usuario autenticado es el preparador físico.
    mis_servicios = Servicio.objects.filter(id_proveedor_servicio=preparador_obj).order_by('nombre_servicio') # Servicios que ofrece este preparador.
    mis_instancias = InstanciaServicio.objects.filter(id_servicio__in=mis_servicios) # Instancias de esos servicios.
    # Inscripciones de clientes a estas instancias de servicio.
    inscripciones_clientes = DetalleServicioAdquirido.objects.filter(
        id_instancia_servicio__in=mis_instancias
    ).select_related('id_cliente', 'id_instancia_servicio__id_servicio')

    context = {
        'preparador': preparador_obj,
        'mis_servicios': mis_servicios,
        'mis_instancias': mis_instancias,
        'inscripciones_clientes': inscripciones_clientes,
    }
    return render(request, 'core/panel_preparador_fisico.html', context)

# --- Vistas para la Gestión de Servicios del Nutricionista (Específicas del Nutricionista) ---

@login_required(login_url='login')
@user_passes_test(is_nutricionista, login_url='index')
def nutricionista_servicios_list(request):
    """Muestra una lista de los servicios ofrecidos por el nutricionista autenticado."""
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
    """Permite al nutricionista crear un nuevo servicio."""
    print(f"DEBUG: Método de la solicitud: {request.method}")

    if request.method == 'POST':
        form = ServicioForm(request.POST)
        print(f"DEBUG: Datos del formulario recibidos (request.POST): {request.POST}")

        if form.is_valid():
            print("DEBUG: El formulario es válido.")
            servicio = form.save(commit=False) # No guarda la instancia todavía en la base de datos.

            print(f"DEBUG: Servicio.disponible obtenido del formulario (antes de asignar proveedor): {servicio.disponible}")

            servicio.id_proveedor_servicio = request.user # Asigna el usuario actual como proveedor del servicio.
            print(f"DEBUG: Servicio.disponible *después* de form.save(commit=False) y asignación del proveedor: {servicio.disponible}")

            try:
                servicio.save(using=servicio._state.db) # Guarda el servicio en la base de datos.
                print(f"DEBUG: Servicio '{servicio.nombre_servicio}' (ID: {servicio.id_servicio}) guardado exitosamente por {request.user.email} con disponible='{servicio.disponible}'")
                return redirect('nutricionista_servicios_list') # Redirige a la lista de servicios.
            except Exception as e:
                print(f"ERROR: No se pudo guardar el servicio: {e}")
                form.add_error(None, f"Error al guardar el servicio en la base de datos: {e}. Asegúrate de que la secuencia para ID_SERVICIO esté funcionando correctamente en Oracle o el ID se genere automáticamente.")
        else:
            print(f"DEBUG: El formulario NO es válido. Errores: {form.errors}")
    else:
        form = ServicioForm() # Si es GET, crea un formulario vacío.
        print("DEBUG: Solicitud GET, creando formulario vacío.")

    return render(request, 'core/nutricionista_servicio_form.html', {'form': form})

@login_required(login_url='login')
@user_passes_test(is_nutricionista, login_url='index')
def nutricionista_servicio_editar(request, id_servicio):
    """Permite al nutricionista editar un servicio existente."""
    # Obtiene el servicio por ID y se asegura de que el nutricionista autenticado sea el proveedor.
    servicio = get_object_or_404(Servicio, id_servicio=id_servicio, id_proveedor_servicio=request.user)

    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio) # Popula el formulario con los datos POST y la instancia existente.
        if form.is_valid():
            form.save() # Guarda los cambios en el servicio.
            print(f"DEBUG: Servicio '{servicio.nombre_servicio}' (ID: {servicio.id_servicio}) actualizado exitosamente por {request.user.email}")
            return redirect('nutricionista_servicios_list')
        else:
            print(f"DEBUG: El formulario de edición NO es válido. Errores: {form.errors}")
    else:
        form = ServicioForm(instance=servicio) # Si es GET, crea el formulario con los datos actuales del servicio.

    return render(request, 'core/nutricionista_servicio_form.html', {'form': form, 'servicio': servicio})

@login_required(login_url='login')
@user_passes_test(is_nutricionista, login_url='index')
def nutricionista_servicio_eliminar(request, id_servicio):
    """Permite al nutricionista eliminar un servicio existente."""
    # Obtiene el servicio por ID y se asegura de que el nutricionista autenticado sea el proveedor.
    servicio = get_object_or_404(Servicio, id_servicio=id_servicio, id_proveedor_servicio=request.user)

    if request.method == 'POST':
        try:
            print(f"DEBUG: Intentando eliminar servicio ID: {servicio.id_servicio}, Nombre: {servicio.nombre_servicio}")
            servicio.delete() # Elimina el servicio.
            print(f"DEBUG: Servicio '{servicio.nombre_servicio}' (ID: {servicio.id_servicio}) eliminado exitosamente por {request.user.email}")
            return redirect('nutricionista_servicios_list')
        except Exception as e:
            print(f"ERROR: No se pudo eliminar el servicio {servicio.id_servicio}: {e}")
            # Muestra un error si la eliminación falla (ej. por restricciones de clave externa).
            return render(request, 'core/nutricionista_servicio_confirm_delete.html', {'servicio': servicio, 'error': f'Error al eliminar: {e}. Puede haber servicios o instancias relacionadas.'})

    # Para solicitudes GET, muestra la página de confirmación de eliminación.
    return render(request, 'core/nutricionista_servicio_confirm_delete.html', {'servicio': servicio})



# Check Descuento:

def clean_and_split_rut(rut_completo):
    """
    Limpia un RUT chileno (elimina puntos, guiones) y lo separa en número y dígito verificador.
    Asume que el DV es el último carácter y el resto es el número.
    Ejemplo: '12.345.678-K' -> ('12345678', 'K')
             '7654321-0'   -> ('7654321', '0')
             '19876543K'   -> ('19876543', 'K')
    """
    if not rut_completo:
        return None, None

    # Elimina puntos, guiones y espacios
    cleaned_rut = str(rut_completo).replace('.', '').replace('-', '').strip().upper()

    if len(cleaned_rut) < 2: # Necesita al menos un número y un DV
        return None, None

    rut_numerico = cleaned_rut[:-1] # Todos los caracteres excepto el último
    dv_rut = cleaned_rut[-1]        # El último carácter es el DV

    return rut_numerico, dv_rut

def check_rut_in_external_api(user_rut_completo):
    """
    Verifica si un RUT dado (completo, ej. '12345678-9') existe en la API externa de clientes.
    Retorna True si lo encuentra, False en caso contrario o si hay error.
    """
    user_rut_numerico, user_dv_rut = clean_and_split_rut(user_rut_completo)

    if not user_rut_numerico or not user_dv_rut:
        print(f"ERROR (API): El RUT del usuario '{user_rut_completo}' no tiene un formato válido para la verificación.")
        return False

    try:
        response = requests.get("https://api-sabor-latino-chile.onrender.com/clientes")
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP 4xx/5xx
        clientes_api_data = response.json()
        
        print(f"DEBUG (API): Datos de la API externa recibidos: {clientes_api_data}")
        print(f"DEBUG (API): Buscando RUT (numérico-DV): {user_rut_numerico}-{user_dv_rut}")

        for cliente_api in clientes_api_data:
            # Asumo que la API externa también tiene el RUT completo en un solo campo (ej. 'rut')
            api_rut_completo = cliente_api.get('rut') # <-- Ajusta 'rut' si el nombre del campo es diferente en tu API

            api_rut_numerico, api_dv_rut = clean_and_split_rut(api_rut_completo)

            if api_rut_numerico and api_dv_rut and \
               api_rut_numerico == user_rut_numerico and \
               api_dv_rut == user_dv_rut:
                print(f"DEBUG (API): RUT {user_rut_numerico}-{user_dv_rut} ENCONTRADO en la API.")
                return True
        print(f"DEBUG (API): RUT {user_rut_numerico}-{user_dv_rut} NO ENCONTRADO en la API.")
        return False
    except requests.RequestException as e:
        print(f"ERROR (API): Falló la conexión con la API externa de clientes: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR (API): No se pudo decodificar la respuesta JSON de la API: {e}")
        return False
    except Exception as e:
        print(f"ERROR (API): Ocurrió un error inesperado en check_rut_in_external_api: {e}")
        return False

# --- Nueva Vista para Obtener el Estado del Descuento ---
@login_required
def get_discount_status(request):
    """
    Devuelve un JSON indicando si el usuario autenticado (cliente) es elegible
    para un descuento del 20% basado en su RUT en la API externa.
    """
    user = request.user
    # Asume que el campo 'rut' de tu modelo Usuario contiene el RUT completo.
    if is_cliente(user) and hasattr(user, 'rut') and user.rut:
        user_rut_completo = user.rut # Obtiene el RUT completo de tu modelo Usuario
        is_eligible = check_rut_in_external_api(user_rut_completo)
        return JsonResponse({'discount_eligible': is_eligible})
    return JsonResponse({'discount_eligible': False, 'message': 'Usuario no cliente o RUT no disponible.'})

@login_required(login_url='login')
def checkout_view(request):
    """
    Renderiza la vista de checkout y maneja una simulación de POST.
    Aquí es CRÍTICO que la lógica del descuento se aplique del lado del servidor.
    """
    # Si la solicitud no es POST, simplemente renderiza la página de checkout
    if request.method == 'GET':
        return render(request, 'core/checkout.html')

    # Lógica para el procesamiento POST de la compra
    elif request.method == 'POST':
        # Primero, verifica si el usuario está autenticado y si es un cliente
        if not request.user.is_authenticated or not is_cliente(request.user):
            messages.error(request, 'Debes iniciar sesión como cliente para finalizar la compra.')
            return redirect('login')

        user = request.user
        cart_data_json = request.POST.get('cart_data', '[]') # Recibe los datos del carrito del frontend
        
        try:
            cart_items = json.loads(cart_data_json)
        except json.JSONDecodeError:
            messages.error(request, 'Error al procesar los datos del carrito.')
            return redirect('carrito_view') # Redirige de vuelta al carrito

        total_calculated_backend = 0
        discount_applied = False

        # Verifica si el usuario es elegible para el descuento del 20%
        if hasattr(user, 'rut') and user.rut:
            discount_applied = check_rut_in_external_api(user.rut)

        # Calcula el subtotal y el total aplicando el descuento si es elegible
        for item in cart_items:
            item_type = item.get('type')
            item_id = item.get('id')
            quantity = item.get('cantidad')
            price = item.get('precio') # Este precio viene del frontend, DEBERÍAS VALIDARLO con la DB
                                      # Para mayor seguridad, busca el precio real en tu DB

            if item_type == 'producto':
                try:
                    product = Producto.objects.get(id_producto=item_id)
                    # AQUI: VALIDAR STOCK y PRECIO con el que está en la DB
                    if quantity > product.stock:
                        messages.error(request, f'No hay suficiente stock para {product.nombre}.')
                        return redirect('carrito_view')
                    total_calculated_backend += product.precio_unitario * quantity
                except Producto.DoesNotExist:
                    messages.error(request, f'Producto no encontrado: {item.get("nombre")}.')
                    return redirect('carrito_view')
            elif item_type == 'servicio':
                try:
                    service = Servicio.objects.get(id_servicio=item_id)
                    # AQUI: VALIDAR PRECIO con el que está en la DB
                    total_calculated_backend += service.precio_servicio * quantity
                except Servicio.DoesNotExist:
                    messages.error(request, f'Servicio no encontrado: {item.get("nombre")}.')
                    return redirect('carrito_view')

        final_total_backend = total_calculated_backend
        if discount_applied:
            discount_amount = total_calculated_backend * 0.20
            final_total_backend -= discount_amount
            messages.info(request, f'Se aplicó un descuento del 20% (${discount_amount:,.2f}) a tu compra.')

        # --- LÓGICA DE PROCESAMIENTO DE ORDEN REAL ---
        # Esto es un placeholder. Aquí es donde realmente registrarías la venta,
        # reducirías el stock, etc.

        try:
            with transaction.atomic():
                # Ejemplo de creación de VentaProducto (asumiendo que manejas productos)
                # Necesitas definir cómo se asigna id_mp (método de pago)
                # Y también id_empleado (puede ser null o un empleado predeterminado)
                
                # Puedes intentar obtener un método de pago predeterminado
                default_payment_method = MetodosDePago.objects.get(pk=1) # Asumiendo que el ID 1 es 'Efectivo' o similar

                # Crea la VentaProducto (para productos)
                # Si solo vendes servicios, ajusta esto o crea un modelo de "PedidoServicio"
                # O si quieres un sistema de carrito unificado, haz una "Orden" general
                # Que contenga tanto productos como servicios.
                
                # Este ejemplo es muy básico y asume que "VentaProducto"
                # es la entidad principal para una compra.

                # Si el carrito contiene productos:
                if any(item['type'] == 'producto' for item in cart_items):
                    venta_producto = VentaProducto.objects.create(
                        id_cliente=user,
                        fecha_venta=timezone.now().date(),
                        total_venta=final_total_backend,
                        id_mp=default_payment_method,
                        id_empleado=None # O un empleado si aplica
                    )
                    # Crea DetalleCompra para cada producto
                    for item in cart_items:
                        if item['type'] == 'producto':
                            product = Producto.objects.get(id_producto=item['id'])
                            DetalleCompra.objects.create(
                                id_venta_producto=venta_producto,
                                id_producto=product,
                                cantidad_adquirida=item['cantidad'],
                                precio_venta_unitario=product.precio_unitario,
                                subtotal_detalle=product.precio_unitario * item['cantidad']
                            )
                            # Reduce el stock del producto
                            product.stock -= item['cantidad']
                            product.save()

                # Si el carrito contiene servicios:
                if any(item['type'] == 'servicio' for item in cart_items):
                    for item in cart_items:
                        if item['type'] == 'servicio':
                            service = Servicio.objects.get(id_servicio=item['id'])
                            # Crea InstanciaServicio
                            nueva_instancia_servicio = InstanciaServicio.objects.create(
                                id_servicio=service,
                                id_proveedor_servicio=service.id_proveedor_servicio,
                                fecha_hora_programada=timezone.now().date(), # O una fecha seleccionada por el cliente
                                reservado='S', # Marcar como reservado
                                estado_instancia='Comprado' # O 'Pendiente'
                            )
                            # Crea DetalleServicioAdquirido
                            DetalleServicioAdquirido.objects.create(
                                id_cliente=user,
                                id_instancia_servicio=nueva_instancia_servicio,
                                fecha_hora_adquisicion=timezone.now().date(),
                                precio_pagado=service.precio_servicio,
                                id_mp=default_payment_method
                            )

                messages.success(request, 'Compra finalizada con éxito. ¡Gracias por tu compra!')
                return JsonResponse({'success': True, 'redirect_url': reverse('pago_exitoso')})
                # return redirect('pago_exitoso_view') # Redirige a la página de éxito
        except MetodosDePago.DoesNotExist:
            messages.error(request, 'Error en la configuración de métodos de pago. Contacta al soporte.')
            return JsonResponse({'success': False, 'message': 'Error en la configuración de métodos de pago.'})
        except Exception as e:
            print(f"Error al procesar la compra: {e}")
            messages.error(request, f'Ocurrió un error al procesar tu compra: {e}')
            return JsonResponse({'success': False, 'message': f'Error al procesar la compra: {e}'})

# ... (rest of your views.py remains the same) ...

def pago_exitoso_view(request):
    """Vista de confirmación de pago exitoso."""
    return render(request, 'core/pago_exitoso.html')
# --- Integraciones con APIs Externas ---

def listar_clientes(request):
    """Muestra una lista de clientes obtenida de una API externa."""
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
        response.raise_for_status() # Lanza una excepción si la solicitud HTTP no fue exitosa.
        clientes = response.json()
    except requests.RequestException as e:
        print("Error al conectar con la API:", e)
        clientes = [] # Si hay un error, la lista de clientes estará vacía.

    return render(request, 'core/clientes.html', {'clientes': clientes})

# Define la URL base para la API externa.
URL = "https://api-sabor-latino-chile.onrender.com"

def buscarAlumno(numrut):
    """Busca un alumno por RUT en una API externa."""
    respuesta = requests.get(f"{URL}/clientes")
    if respuesta.status_code == 200:
        for e in respuesta.json():
            if int(e['numero_rut']) == numrut:
                return True
        return False
    else:
        print("❌ Error en el servidor de la api")
        return False

# --- Vistas para el Cliente ---

@login_required(login_url='login')
@user_passes_test(is_cliente, login_url='index') # Asegura que solo los clientes autenticados puedan acceder.
def cliente_ver_servicios(request):
    """Permite al cliente ver los servicios disponibles para adquirir."""
    # Obtiene solo los servicios que están 'Disponibles'.
    servicios_disponibles = Servicio.objects.filter(disponible='S').order_by('nombre_servicio')

    context = {
        'servicios_disponibles': servicios_disponibles
    }
    return render(request, 'core/cliente_ver_servicios.html', context)

@login_required(login_url='login')
@user_passes_test(is_cliente, login_url='index')
def cliente_adquirir_servicio(request, servicio_id):
    """Permite al cliente adquirir un servicio específico."""
    # Redirecciona si el usuario no está autenticado o no es un cliente.
    if not request.user.is_authenticated or not is_cliente(request.user):
        messages.error(request, 'Debes iniciar sesión como cliente para adquirir servicios.')
        return redirect('login')

    if request.method == 'POST':
        try:
            servicio = Servicio.objects.get(id_servicio=servicio_id) # Obtiene el servicio a adquirir.
            cliente = request.user # El usuario autenticado es el cliente que adquiere el servicio.

            # --- PASO 1: Crear una InstanciaServicio ---
            nueva_instancia_servicio = InstanciaServicio(
                id_servicio=servicio,
                id_proveedor_servicio=servicio.id_proveedor_servicio,
                fecha_hora_programada=timezone.now().date(), # Usa la fecha actual.
                reservado='N', # Marca como no reservado inicialmente.
                estado_instancia='Programado' # Establece el estado inicial.
            )
            nueva_instancia_servicio.save() # Guarda la instancia para obtener su ID.

            # --- PASO 2: Crear DetalleServicioAdquirido ---
            try:
                # Intenta obtener un método de pago por defecto (ID 1). Ajusta si tu lógica es diferente.
                metodo_pago_default = MetodosDePago.objects.get(pk=1)
            except MetodosDePago.DoesNotExist:
                messages.error(request, 'Método de pago predeterminado no encontrado. Contacte al administrador.')
                nueva_instancia_servicio.delete() # Elimina la instancia de servicio si no se puede registrar el detalle.
                return redirect('nutricionista') # O redirige a una página de error más apropiada.

            detalle_adquirido = DetalleServicioAdquirido(
                id_cliente=cliente,
                id_instancia_servicio=nueva_instancia_servicio, # Usa la instancia recién creada.
                fecha_hora_adquisicion=timezone.now().date(), # Usa la fecha actual de adquisición.
                precio_pagado=servicio.precio_servicio, # Usa el precio del servicio.
                id_mp=metodo_pago_default # Asigna el método de pago por defecto.
            )
            detalle_adquirido.save() # Guarda el detalle de la adquisición.

            messages.success(request, 'Servicio adquirido con éxito.')
            # Redirige al cliente a una página de confirmación o a su lista de servicios.
            return redirect('algun_url_de_confirmacion_o_perfil')

        except Servicio.DoesNotExist:
            messages.error(request, 'El servicio no existe.')
            return redirect('nutricionista') # O redirige a la lista de servicios si el ID no es válido.
        except Exception as e:
            messages.error(request, f'No se pudo adquirir el servicio: {e}')
            return redirect('nutricionista')
    # Si la solicitud no es POST, redirige al cliente a la página de nutricionista o servicios.
    return redirect('nutricionista')

@login_required(login_url='login')
@user_passes_test(is_cliente, login_url='index')
def cliente_mis_servicios(request):
    """Muestra una lista de todos los servicios que el cliente ha adquirido."""
    # Filtra las adquisiciones del cliente actual, ordenadas por fecha.
    mis_adquisiciones = DetalleServicioAdquirido.objects.filter(id_cliente=request.user).order_by('-fecha_adquisicion')

    context = {
        'mis_adquisiciones': mis_adquisiciones
    }
    return render(request, 'core/cliente_mis_servicios.html', context)
    
# Lista de servicios (vista y URL: lista_servicios_pf)
def lista_servicios_pf(request):
    servicios = Servicio.objects.all()
    return render(request, 'core/preparador/lista_servicios_pf.html', {'servicios': servicios})


# Crear servicio (vista y URL: crear_servicio_pf)
def crear_servicio_pf(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_servicios_pf')
    else:
        form = ServicioForm()
    return render(request, 'core/preparador/lista_servicios_pf_crear.html', {'form': form})


# Editar servicio (vista y URL: editar_servicio_pf)
def editar_servicio_pf(request):
    pk = request.GET.get('id')  # Asumiendo que lo pasas por ?id= en la URL
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect('lista_servicios_pf')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'core/preparador/servicio_form_pf.html', {'form': form})


# Eliminar servicio (vista y URL: eliminar_servicio_pf)
def confirmar_eliminar_pf(request):
    pk = request.GET.get('id')  # Asumiendo que lo pasas por ?id= en la URL
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        servicio.delete()
        return redirect('lista_servicios_pf')
    return render(request, 'core/preparador/confirmar_eliminar_pf.html', {'servicio': servicio})


# Lista mensajes (vista y URL: lista_mensajes_pf)
def lista_mensajes_pf(request):
    mensajes = Mensaje.objects.all()
    return render(request, 'core/preparador/lista_mensajes_pf.html', {'mensajes': mensajes})


# Detalle mensaje (vista y URL: detalle_mensaje_pf)
def detalle_mensaje_pf(request, pk):
    mensaje = get_object_or_404(Mensaje, pk=pk)
    return render(request, 'core/preparador/detalle_mensaje_pf.html', {'mensaje': mensaje})    