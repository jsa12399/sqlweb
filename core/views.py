from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
import json
import os
from django.urls import reverse
import decimal
import traceback # Para depuración
from django.conf import settings

TASA_CAMBIO_USD_CLP = decimal.Decimal('950.00') # Define esto en settings.py si es global

# Importa todos los modelos y formularios necesarios.
from .models import Servicio,Envio, Mensaje, ComentarioValoracionProducto,Usuario, MetodosDePago, Producto, Comuna, TipoUsuario, InstanciaServicio, DetalleServicioAdquirido, VentaProducto, DetalleCompra
from .forms import ServicioForm, ComentarioValoracionForm # Asegúrate de que este ServicioForm sea genérico o crea uno específico para PF si necesitas campos distintos.

import requests # Para las integraciones con APIs externas
from django.db import connection

TASA_CAMBIO_USD_CLP = decimal.Decimal('950.00')

# Importa todos los modelos y formularios necesarios.
from .models import Servicio, Mensaje, Usuario, MetodosDePago, Producto, Comuna, TipoUsuario, InstanciaServicio, DetalleServicioAdquirido,VentaProducto,DetalleCompra
from .forms import ServicioForm

import requests # Para las integraciones con APIs externas
from django.db import connection # Importación que tenías, mantenida aunque no se usa en el código visible.

# Integracion_Proyecto/core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction # Importante para las transacciones atómicas
from django.contrib import messages
import json
import decimal # Para manejar Decimal correctamente
from django.urls import reverse # Para construir URLs dinámicamente

# Importa todos los modelos y formularios necesarios.
from .models import (
    Servicio, Mensaje, Usuario, MetodosDePago, Producto, Comuna, TipoUsuario,
    InstanciaServicio, DetalleServicioAdquirido, VentaProducto, DetalleCompra,
)
from .forms import ServicioForm

import requests # Para las integraciones con APIs externas
# from django.db import connection # Importación no utilizada en el código visible.

# Obtiene el modelo de usuario personalizado que estás usando en Django.
User = get_user_model()

# --- Funciones Auxiliares para Verificación de Tipo de Usuario ---
# Estas funciones se usan con el decorador @user_passes_test para controlar el acceso a vistas.

def is_administrador(user):
    """Verifica si el usuario es un Administrador (ID 1)."""
    return user.is_authenticated and hasattr(user, 'id_tipo_usuario') and user.id_tipo_usuario_id == 1

def is_nutricionista(user):
    """Verifica si el usuario es un Nutricionista (ID 2)."""
    return user.is_authenticated and hasattr(user, 'id_tipo_usuario') and user.id_tipo_usuario_id == 2

def is_preparador_fisico(user):
    """Verifica si el usuario es un Preparador Físico (ID 3)."""
    return user.is_authenticated and hasattr(user, 'id_tipo_usuario') and user.id_tipo_usuario_id == 3

def is_cliente(user):
    """Verifica si el usuario es un Cliente (ID 4)."""
    return user.is_authenticated and hasattr(user, 'id_tipo_usuario') and user.id_tipo_usuario_id == 4



# --- Vistas del Panel del Preparador Físico (Manteniendo la estructura original que tenías) ---
# Nota: Los nombres de estas vistas (panel_nutricionista, lista_servicios_pf, etc.)
# sugieren que estaban siendo reutilizadas o tenían un origen confuso con el rol de nutricionista.
# He mantenido los nombres que tenías para no alterar tus URLs o plantillas.



@login_required(login_url='login')
@user_passes_test(is_preparador_fisico, login_url='index')
def preparador_servicios_list(request):
    """Muestra una lista de los servicios ofrecidos por el preparador físico autenticado."""
    mis_servicios = Servicio.objects.filter(
        id_proveedor_servicio=request.user,
        id_proveedor_servicio__id_tipo_usuario__tipo_usuario='Preparador Físico'
    ).order_by('nombre_servicio')
    context = {
        'mis_servicios': mis_servicios
    }
    return render(request, 'core/preparador_servicios_list.html', context)

@login_required
@user_passes_test(is_preparador_fisico, login_url='index')
def preparador_servicio_crear(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            servicio = form.save(commit=False)
            servicio.id_proveedor_servicio = request.user
            # Asignar el Tipo de Servicio "Preparador Físico"
            tipo_servicio_pf = TipoUsuario.objects.get(tipo_usuario='Preparador Físico') # Asegúrate de que existe este tipo en tu DB
            servicio.id_tipo_servicio = tipo_servicio_pf
            servicio.save()
            messages.success(request, 'Servicio de preparación física creado exitosamente.')
            return redirect('preparador_servicios_list')
        else:
            messages.error(request, 'Error al crear el servicio. Por favor, revisa los datos.')
    else:
        form = ServicioForm()
    return render(request, 'core/preparador_servicio_form.html', {'form': form})

@login_required
@user_passes_test(is_preparador_fisico, login_url='index')
def preparador_servicio_editar(request, id_servicio):
    servicio = get_object_or_404(Servicio, id_servicio=id_servicio, id_proveedor_servicio=request.user)
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio de preparación física actualizado exitosamente.')
            return redirect('preparador_servicios_list')
        else:
            messages.error(request, 'Error al actualizar el servicio. Por favor, revisa los datos.')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'core/preparador_servicio_form.html', {'form': form, 'servicio': servicio})

@login_required
@user_passes_test(is_preparador_fisico, login_url='index')
def preparador_servicio_eliminar(request, id_servicio):
    servicio = get_object_or_404(Servicio, id_servicio=id_servicio, id_proveedor_servicio=request.user)
    if request.method == 'POST':
        try:
            servicio.delete()
            messages.success(request, 'Servicio de preparación física eliminado exitosamente.')
            print("DEBUG: Servicio PF eliminado exitosamente. Redirigiendo...")
            return redirect('preparador_servicios_list')
        except Exception as e:
            messages.error(request, f'Error al eliminar el servicio PF: {e}.')
            print(f"DEBUG: Error al eliminar servicio PF: {e}")
            return render(request, 'core/preparador_servicio_confirm_delete.html', {'servicio': servicio, 'error': f'Error al eliminar: {e}.'})
    print("DEBUG: Solicitud GET para confirmar eliminación (PF).")
    return render(request, 'core/preparador_servicio_confirm_delete.html', {'servicio': servicio})



@login_required
@user_passes_test(is_preparador_fisico, login_url='index')
def preparador_instancias_programadas(request):
    """Muestra una lista de las instancias de servicio programadas para el preparador físico autenticado."""
    instancias = InstanciaServicio.objects.filter(
        id_proveedor_servicio=request.user,
        # ELIMINAMOS LA LÍNEA PROBLEMÁTICA AQUÍ:
        # id_servicio__id_tipo_servicio__tipo_usuario='Preparador Físico'
        # Porque el decorador ya asegura que request.user es un preparador físico.
    ).select_related('id_servicio', 'id_proveedor_servicio').order_by('fecha_hora_programada')

    # Para cargar los clientes que adquirieron el servicio (y su RUT)
    instancias_con_clientes = instancias.prefetch_related(
        'detalleservicioadquirido_set__id_cliente' # Asegúrate que 'id_cliente' es el campo ForeignKey a tu modelo Cliente en DetalleServicioAdquirido
    )

    context = {
        'instancias': instancias_con_clientes
    }
    return render(request, 'core/preparador_instancias_programadas.html', context)


@login_required(login_url='login')
@user_passes_test(is_preparador_fisico, login_url='index') # Si solo preparadores deben verlos
def lista_mensajes_pf(request):
    """Muestra una lista de todos los mensajes (generalmente para el preparador físico)."""
    mensajes = Mensaje.objects.all().order_by('-creado') # Ordena por fecha de creación
    return render(request, 'core/preparador/lista_mensajes_pf.html', {'mensajes': mensajes})

@login_required(login_url='login')
@user_passes_test(is_preparador_fisico, login_url='index') # Si solo preparadores deben verlos
def detalle_mensaje_pf(request, pk):
    """Muestra el detalle de un mensaje específico."""
    mensaje = get_object_or_404(Mensaje, pk=pk)
    return render(request, 'core/preparador/detalle_mensaje_pf.html', {'mensaje': mensaje})

# --- Vistas Públicas y de Autenticación ---

def index(request):
    """Vista de la página de inicio que muestra productos destacados."""
    productos_destacados = Producto.objects.all()[:3] # Obtiene los primeros 3 productos.
    return render(request, 'core/index.html', {'productos': productos_destacados})

@login_required(login_url='login')
def nutricionista_publica(request):
    """Muestra los servicios disponibles ofrecidos por nutricionistas."""
    servicios_a_mostrar = Servicio.objects.none()

    try:
        tipo_nutricionista = TipoUsuario.objects.get(id_tipo_usuario=2)
        ids_nutricionistas = Usuario.objects.filter(id_tipo_usuario=tipo_nutricionista).values_list('id_usuario', flat=True)

        servicios_a_mostrar = Servicio.objects.filter(
            id_proveedor_servicio__in=ids_nutricionistas,
            disponible='S'
        ).order_by('id_proveedor_servicio__nombre', 'nombre_servicio')

    except TipoUsuario.DoesNotExist:
        messages.error(request, "Error: El Tipo de Usuario 'Nutricionista' no existe en la base de datos.")
    except Exception as e:
        messages.error(request, f"Error al cargar servicios de nutricionistas: {e}")

    context = {
        'servicios_nutricionista': servicios_a_mostrar
    }
    return render(request, 'core/nutricionista.html', context)


@login_required(login_url='login')
def preparadorfisico_publica(request):
    """Muestra los servicios disponibles ofrecidos por preparadores físicos."""
    try:
        tipo_pf = TipoUsuario.objects.get(id_tipo_usuario=3)
        ids_pf = Usuario.objects.filter(id_tipo_usuario=tipo_pf).values_list('id_usuario', flat=True)
        servicios = Servicio.objects.filter(
            id_proveedor_servicio__in=ids_pf,
            disponible='S'
        ).order_by('id_proveedor_servicio__nombre', 'nombre_servicio')

        context = {
            'servicios_preparador_fisico': servicios,
            'tasa_cambio': TASA_CAMBIO_USD_CLP
        }
    except TipoUsuario.DoesNotExist:
        messages.error(request, "Error: El Tipo de Usuario 'Preparador Físico' no existe en la base de datos.")
        context = {'servicios_preparador_fisico': []}
    except Exception as e:
        messages.error(request, f"Error al cargar servicios de preparadores físicos: {e}")
        context = {'servicios_preparador_fisico': []}

    return render(request, 'core/preparadorfisico.html', context)
@login_required(login_url='login')
def ver_productos(request):
    """Muestra una lista de todos los productos disponibles."""
    productos = Producto.objects.all()
    context = {
        'productos': productos
    }
    return render(request, 'core/productos.html', context)

@login_required(login_url='login') # Solo usuarios autenticados pueden ver su carrito
def carrito_view(request):
    """Renderiza la vista del carrito de compras (frontend-driven)."""
    return render(request, 'core/carrito.html')

# core/views.py

# ... (otras importaciones existentes) ...
from django.conf import settings # <<--- ¡Asegúrate de que esta línea esté presente!

# ... (el resto de tus funciones y vistas) ...
def obtener_costo_envio_del_carrito():
    # Lógica para calcular o recuperar el costo de envío.
    # Puede ser un valor fijo, basado en el peso, la ubicación, etc.
    return Decimal('5.00') # Ejemplo de costo de envío


@login_required(login_url='login')
@user_passes_test(is_cliente, login_url='index')
def checkout_view(request):
    paypal_client_id = settings.PAYPAL_CLIENT_ID # Asegúrate de que PAYPAL_CLIENT_ID esté en settings.py

    if request.method == 'POST':
        try:
            cart_data = json.loads(request.POST.get('cart_data', '[]'))
            paypal_transaction_id = request.POST.get('paypal_transaction_id')
            total_frontend = Decimal(request.POST.get('total_frontend', '0.00').replace(',', '.'))
            payment_method_id = request.POST.get('payment_method_id')

            if not payment_method_id:
                return JsonResponse({'success': False, 'error': 'ID de método de pago no recibido'}, status=400)
            if not cart_data:
                return JsonResponse({'success': False, 'error': 'El carrito está vacío'}, status=400)

            backend_total_sin_descuento = Decimal('0.00')
            has_physical_products = False # Bandera para saber si hay productos físicos

            for item in cart_data:
                if item['type'] == 'producto':
                    try:
                        product = Producto.objects.get(id_producto=item['id'])
                        backend_total_sin_descuento += product.precio_unitario * item['cantidad']
                        has_physical_products = True # Si hay al menos un producto, se requiere envío
                    except Producto.DoesNotExist:
                        return JsonResponse({'success': False, 'error': f"Producto con ID {item['id']} no existe"}, status=400)
                elif item['type'] == 'servicio':
                    try:
                        servicio = Servicio.objects.get(id_servicio=item['id'])
                        backend_total_sin_descuento += servicio.precio_servicio * item['cantidad']
                    except Servicio.DoesNotExist:
                        return JsonResponse({'success': False, 'error': f"Servicio con ID {item['id']} no existe"}, status=400)

            # Verificar elegibilidad para descuento
            user_rut = request.user.rut if hasattr(request.user, 'rut') else None
            user_has_discount = False
            if user_rut:
                user_has_discount = check_rut_in_external_api(user_rut)

            descuento_aplicado = Decimal('0.00')
            backend_total_con_descuento = backend_total_sin_descuento

            if user_has_discount:
                tasa_descuento = Decimal('0.20') # 20% de descuento
                descuento_aplicado = backend_total_sin_descuento * tasa_descuento
                backend_total_con_descuento -= descuento_aplicado
                print(f"DEBUG: Descuento del {tasa_descuento * 100}% aplicado: -${descuento_aplicado}")
            else:
                print("DEBUG: El usuario no es elegible para descuento.")

            print(f"Backend Total (sin descuento): {backend_total_sin_descuento}")
            print(f"Backend Total (con descuento): {backend_total_con_descuento}")
            print(f"Frontend Total: {total_frontend}")

            # Comparar con el total del frontend con una tolerancia
            if abs(backend_total_con_descuento - total_frontend) > Decimal('0.01'): # Usa Decimal para comparación
                return JsonResponse({'success': False, 'error': 'El total enviado no coincide con el calculado en el backend (con descuento)' if user_has_discount else 'El total enviado no coincide con el calculado en el backend'}, status=400)

            with transaction.atomic():
                try:
                    metodo_pago = MetodosDePago.objects.get(id_mp=payment_method_id)
                except MetodosDePago.DoesNotExist:
                    return JsonResponse({'success': False, 'error': f'Método de pago con ID "{payment_method_id}" no configurado'}, status=400)

                # 1. Crear la VentaProducto
                venta = VentaProducto.objects.create(
                    id_cliente=request.user, # Asumiendo que VentaProducto.id_cliente es un FK a tu modelo CustomUser/User de Django
                    fecha_venta=timezone.now(),
                    total_venta=backend_total_con_descuento,
                    id_mp=metodo_pago
                )

                # 2. Iterar sobre los ítems del carrito para crear DetalleCompra e InstanciaServicio
                for item in cart_data:
                    if item['type'] == 'producto':
                        product = Producto.objects.get(id_producto=item['id'])
                        quantity = item['cantidad']
                        DetalleCompra.objects.create(
                            id_venta_producto=venta,
                            id_producto=product,
                            cantidad_adquirida=quantity,
                            precio_venta_unitario=product.precio_unitario,
                            subtotal_detalle=product.precio_unitario * quantity
                        )
                        product.stock -= quantity
                        product.save()
                    elif item['type'] == 'servicio':
                        servicio_obj = Servicio.objects.get(id_servicio=item['id'])
                        for _ in range(item['cantidad']):
                            instancia = InstanciaServicio.objects.create(
                                id_servicio=servicio_obj,
                                id_proveedor_servicio=servicio_obj.id_proveedor_servicio,
                                fecha_hora_programada=timezone.now(), # O una fecha/hora de tu lógica de servicios
                                reservado='S',
                                estado_instancia='Programado'
                            )
                            # CRÍTICO: Si quieres asociar DetalleServicioAdquirido a VentaProducto,
                            # el modelo DetalleServicioAdquirido DEBE tener un FK a VentaProducto.
                            # Si no lo tiene, estos servicios no se "unirán" a la venta específica en tu DB.
                            DetalleServicioAdquirido.objects.create(
                                id_cliente=request.user, # Asumiendo que id_cliente aquí también apunta a User
                                id_instancia_servicio=instancia,
                                fecha_hora_adquisicion=timezone.now(),
                                precio_pagado=servicio_obj.precio_servicio,
                                id_mp=metodo_pago
                                # Si tu modelo DetalleServicioAdquirido tiene id_venta_producto:
                                # id_venta_producto=venta
                            )

                # 3. CREAR EL REGISTRO DE ENVIO SI HAY PRODUCTOS FÍSICOS
                # El código_rastreo y nombre_transportista se deben asignar *posteriormente*
                # cuando el paquete sea realmente enviado y tengas esa info.
                envio_creado = False
                if has_physical_products:
                    try:
                        Envio.objects.create(
                            id_venta_producto=venta,
                            fecha_envio=timezone.localdate(),
                            estado_envio="Pendiente", # Estado inicial del envío
                            costo_envio=obtener_costo_envio_del_carrito(), # Tu función para calcular el costo
                            # codigo_rastreo y nombre_transportista se dejan nulos aquí por ahora
                        )
                        envio_creado = True
                    except Exception as e:
                        print(f"ERROR: No se pudo crear el registro de envío para la venta {venta.id_venta_producto}: {e}")
                        # Si este error es crítico para tu negocio, puedes relanzar la excepción
                        # para que la transacción se revierta:
                        raise # Revertir la transacción si el envío no se puede crear

                # VACÍA EL CARRITO (importante después de la transacción exitosa)
                # Esto es crucial para que el carrito se borre después de una compra exitosa
                request.session['cart'] = {}
                request.session.modified = True
                print("DEBUG: Carrito vaciado de la sesión.")

                # --- ¡REDIRECCIÓN FINAL PARA TODOS LOS CASOS DE ÉXITO! ---
                # Siempre redirige a pago_exitoso con el ID de la venta
                redirect_url = reverse('pago_exitoso', args=[venta.id_venta_producto])
                print(f"DEBUG CHECKOUT: Redirigiendo a: {redirect_url}")
                return JsonResponse({'success': True, 'redirect_url': redirect_url})

        except MetodosDePago.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'El método de pago seleccionado no existe'}, status=400)
        except Producto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Uno de los productos en el carrito no existe'}, status=400)
        except Servicio.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Uno de los servicios en el carrito no existe'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Error al decodificar los datos del carrito'}, status=400)
        except Exception as e:
            # Captura cualquier otra excepción no manejada y la loguea/devuelve un error general
            print(f"ERROR FATAL al procesar el checkout: {e}")
            return JsonResponse({'success': False, 'error': f'Error interno al procesar la compra: {e}'}, status=500)

    else: # GET request
        return render(request, 'core/checkout.html', {'paypal_client_id': paypal_client_id})


@login_required(login_url='login')
def pago_exitoso_view(request, venta_id=None):
    venta = None
    if venta_id:
        try:
            # Asegúrate de que esta venta pertenezca al usuario logueado
            venta = VentaProducto.objects.get(id_venta_producto=venta_id, id_cliente=request.user)

            # --- CORRECCIÓN AQUÍ ---
            # Reemplaza .username con el campo correcto de tu modelo Usuario
            # Por ejemplo, si tu modelo Usuario usa 'email' como identificador:
            user_identifier = request.user.email
            # O si tu modelo Usuario tiene un campo 'rut':
            # user_identifier = request.user.rut
            # O si usa el método get_username() de AbstractUser (que devolverá el campo definido en USERNAME_FIELD):
            # user_identifier = request.user.get_username()

            print(f"DEBUG PAGO_EXITOSO: Venta ID {venta_id} encontrada para el usuario {user_identifier}.")
        except VentaProducto.DoesNotExist:
            venta = None
            # También corrige aquí para evitar el error si la venta no se encuentra
            # o si request.user ya es anónimo por alguna razón (aunque login_required debería evitarlo)
            user_identifier = request.user.email if hasattr(request.user, 'email') else 'Usuario Desconocido' # Fallback seguro
            print(f"DEBUG PAGO_EXITOSO: Venta ID {venta_id} NO encontrada o no pertenece al usuario {user_identifier}.")

    context = {
        'venta': venta,
    }
    return render(request, 'core/pago_exitoso.html', context)



# --- FUNCIONES Y LÓGICA PARA LA API DE AFTERSHIP ---
def get_aftership_tracking_info(tracking_number, courier_slug):
    """
    Función para obtener información de seguimiento de AfterShip.
    Retorna la información del tracking o un error.
    """
    # Asegúrate de que AFTERSHIP_API_KEY y AFTERSHIP_BASE_URL estén definidos en settings.py
    # o aquí directamente si no los tienes en settings.
    aftership_api_key = getattr(settings, 'AFTERSHIP_API_KEY', None)
    aftership_base_url = getattr(settings, 'AFTERSHIP_BASE_URL', "https://api.aftership.com/v4/trackings")

    if not aftership_api_key:
        return None, "Clave API de AfterShip no configurada."

    headers = {
        "aftership-api-key": aftership_api_key,
        "Content-Type": "application/json"
    }

    # Endpoint para obtener un tracking existente.
    # AfterShip lo crea si no existe al hacer el GET, o lo actualiza si ya existe.
    url = f"{aftership_base_url}/{courier_slug}/{tracking_number}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Lanza una excepción si el código de estado es un error (4xx o 5xx)
        data = response.json()

        if data and 'data' in data and 'tracking' in data['data']:
            return data['data']['tracking'], None # Retorna la info de tracking y no hay error
        elif data and 'meta' in data and data['meta'].get('code') == 404:
             return None, "Número de rastreo o transportista no encontrado en AfterShip."
        else:
            # Manejo de otros posibles errores de la API o formato de respuesta inesperado
            return None, data.get('meta', {}).get('message', 'Respuesta inesperada de AfterShip.')

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_message = f"Error HTTP {status_code} al consultar AfterShip: {e.response.text}"
        print(error_message)
        if status_code == 401:
            return None, "Error de autenticación con AfterShip. Revisa tu clave API."
        elif status_code == 400:
            return None, "Solicitud inválida a AfterShip. Revisa los datos de rastreo."
        else:
            return None, f"Error del servidor de AfterShip: {error_message}"
    except requests.exceptions.ConnectionError:
        return None, "No se pudo conectar con el servidor de AfterShip."
    except requests.exceptions.Timeout:
        return None, "Tiempo de espera agotado al conectar con AfterShip."
    except requests.exceptions.RequestException as e:
        return None, f"Error desconocido de conexión con AfterShip: {e}"
    except json.JSONDecodeError:
        return None, "Respuesta no JSON de AfterShip."

@login_required(login_url='login')
@user_passes_test(is_cliente, login_url='index')
def mis_servicios_view(request):
    """Muestra los servicios que el usuario (cliente) ha adquirido."""
    # Filtra los servicios adquiridos por el cliente actual y optimiza las consultas relacionadas.
    servicios_adquiridos = DetalleServicioAdquirido.objects.filter(
        id_cliente=request.user
    ).select_related(
        
        'id_instancia_servicio__id_servicio',
        'id_instancia_servicio__id_proveedor_servicio',
        'id_mp' # Para mostrar el método de pago si es necesario
    ).order_by('-fecha_hora_adquisicion') # Ordena los más recientes primero

    # También puedes obtener las compras de productos
    compras_productos = VentaProducto.objects.filter(
        id_cliente=request.user
    ).select_related(
        'id_mp'
    ).prefetch_related(
        'detallecompra_set__id_producto' # Para obtener los detalles de cada producto en la venta
    ).order_by('-fecha_venta')

    context = {
        'servicios_adquiridos': servicios_adquiridos,
        'compras_productos': compras_productos
    }
    return render(request, 'core/mis_servicios.html', context)

def login_view(request):
    """Maneja el inicio de sesión de usuarios y los redirige según su tipo."""
    if request.user.is_authenticated:
        if is_nutricionista(request.user):
            return redirect('panel_nutricionista')
        elif is_preparador_fisico(request.user):
            return redirect('panel_preparador_fisico') # Corregido a panel_preparador_fisico
        else: # Si es cliente o admin
            return redirect('index')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Bienvenido de nuevo, {user.nombre}!')
            if is_nutricionista(user):
                return redirect('panel_nutricionista')
            elif is_preparador_fisico(user):
                return redirect('panel_preparador_fisico') # Corregido a panel_preparador_fisico
            else:
                return redirect('index')
        else:
            messages.error(request, 'Email o contraseña inválidos.')
    return render(request, 'core/login.html')

def register_view(request):
    """Maneja el registro de nuevos usuarios."""
    if request.user.is_authenticated:
        return redirect('index')

    comunas = Comuna.objects.all()
    # Excluye Administrador (ID 1) para el registro de usuarios normales
    tipos_usuario = TipoUsuario.objects.all().exclude(id_tipo_usuario__in=[1])

    if request.method == "POST":
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

        if not all([email, password, rut, nombre, apellido, tipo_usuario_id]):
            messages.error(request, 'Por favor, completa todos los campos requeridos.')
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario, 'data': request.POST})

        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario, 'data': request.POST})

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este email ya está registrado.')
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario, 'data': request.POST})

        if Usuario.objects.filter(rut=rut).exists():
            messages.error(request, 'Este RUT ya está registrado.')
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario, 'data': request.POST})

        try:
            comuna = Comuna.objects.get(id_comuna=comuna_id) if comuna_id else None
            selected_tipo_usuario = TipoUsuario.objects.get(id_tipo_usuario=tipo_usuario_id)
        except (Comuna.DoesNotExist, TipoUsuario.DoesNotExist) as e:
            messages.error(request, f'Error de selección de comuna o tipo de usuario: {e}.')
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario, 'data': request.POST})
        except Exception as e:
            messages.error(request, f'Error al obtener datos de registro: {e}. Asegúrate que la Comuna y el Tipo de Usuario existan.')
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario, 'data': request.POST})

        try:
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
            )
            login(request, user)
            messages.success(request, 'Registro exitoso. ¡Bienvenido!')
            return redirect('index')
        except Exception as e:
            messages.error(request, f'Error al registrar el usuario: {e}')
            print(f"DEBUG: Error al registrar: {e}") # Para depuración interna
            return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario, 'data': request.POST})

    return render(request, 'core/register.html', {'comunas': comunas, 'tipos_usuario': tipos_usuario})

def custom_logout_view(request):
    """Cierra la sesión del usuario y lo redirige a la página de login."""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login')

# --- VISTA PARA EL PANEL DE NUTRICIONISTA ---
@login_required
@user_passes_test(is_nutricionista, login_url='index')
def nutricionista_instancias_programadas(request):
    """Muestra una lista de las instancias de servicio programadas para el nutricionista autenticado."""
    instancias = InstanciaServicio.objects.filter(
        id_proveedor_servicio=request.user,
        # ELIMINA CUALQUIER FILTRO SIMILAR AQUÍ SI LO TENÍAS:
        # id_servicio__id_tipo_servicio__tipo_usuario='Nutricionista' (o similar)
        # Por la misma razón que en la vista del preparador físico.
    ).select_related('id_servicio', 'id_proveedor_servicio').order_by('fecha_hora_programada')

    instancias_con_clientes = instancias.prefetch_related(
        'detalleservicioadquirido_set__id_cliente'
    )

    context = {
        'instancias': instancias_con_clientes
    }
    return render(request, 'core/nutricionista_instancias_programadas.html', context)


@login_required(login_url='login')
@user_passes_test(is_nutricionista, login_url='index')
def panel_nutricionista(request):
    """Muestra el panel de control para los nutricionistas, incluyendo sus servicios y clientes."""
    nutricionista_obj = request.user
    mis_servicios = Servicio.objects.filter(id_proveedor_servicio=nutricionista_obj).order_by('nombre_servicio')
    mis_instancias = InstanciaServicio.objects.filter(id_servicio__in=mis_servicios).order_by('fecha_hora_programada')
    inscripciones_clientes = DetalleServicioAdquirido.objects.filter(
        id_instancia_servicio__in=mis_instancias
    ).select_related('id_cliente', 'id_instancia_servicio__id_servicio').order_by('id_cliente__nombre', 'id_instancia_servicio__fecha_hora_programada')

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
    preparador_obj = request.user
    mis_servicios = Servicio.objects.filter(id_proveedor_servicio=preparador_obj).order_by('nombre_servicio')
    mis_instancias = InstanciaServicio.objects.filter(id_servicio__in=mis_servicios).order_by('fecha_hora_programada')
    inscripciones_clientes = DetalleServicioAdquirido.objects.filter(
        id_instancia_servicio__in=mis_instancias
    ).select_related('id_cliente', 'id_instancia_servicio__id_servicio').order_by('id_cliente__nombre', 'id_instancia_servicio__fecha_hora_programada')

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
    mis_servicios = Servicio.objects.filter(id_proveedor_servicio=request.user).order_by('nombre_servicio')
    context = {
        'mis_servicios': mis_servicios
    }
    return render(request, 'core/nutricionista_servicios_list.html', context)

@login_required(login_url='login')
@user_passes_test(is_nutricionista, login_url='index')
def nutricionista_servicio_crear(request):
    """Permite al nutricionista crear un nuevo servicio."""
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            servicio = form.save(commit=False)
            servicio.id_proveedor_servicio = request.user # Asigna el usuario actual como proveedor
            try:
                servicio.save()
                messages.success(request, 'Servicio creado exitosamente.')
                return redirect('nutricionista_servicios_list')
            except Exception as e:
                messages.error(request, f"Error al guardar el servicio: {e}. Asegúrate que la secuencia para ID_SERVICIO esté funcionando correctamente en Oracle o el ID se genere automáticamente.")
        else:
            messages.error(request, f"Error en el formulario: {form.errors.as_text()}")
    else:
        form = ServicioForm()
    return render(request, 'core/nutricionista_servicio_form.html', {'form': form, 'action': 'Crear'})

@login_required(login_url='login')
@user_passes_test(is_nutricionista, login_url='index')
def nutricionista_servicio_editar(request, id_servicio):
    """Permite al nutricionista editar un servicio existente."""
    servicio = get_object_or_404(Servicio, id_servicio=id_servicio, id_proveedor_servicio=request.user)

    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio actualizado exitosamente.')
            return redirect('nutricionista_servicios_list')
        else:
            messages.error(request, f"Error en el formulario: {form.errors.as_text()}")
    else:
        form = ServicioForm(instance=servicio)

    return render(request, 'core/nutricionista_servicio_form.html', {'form': form, 'servicio': servicio, 'action': 'Editar'})

@login_required(login_url='login')
@user_passes_test(is_nutricionista, login_url='index')
def nutricionista_servicio_eliminar(request, id_servicio):
    """Permite al nutricionista eliminar un servicio existente."""
    servicio = get_object_or_404(Servicio, id_servicio=id_servicio, id_proveedor_servicio=request.user)

    if request.method == 'POST':
        try:
            servicio.delete()
            messages.success(request, 'Servicio eliminado exitosamente.')
            print("DEBUG: Servicio de nutricionista eliminado. Redirigiendo...")
            return redirect('nutricionista_servicios_list')
        except Exception as e:
            messages.error(request, f'Error al eliminar el servicio: {e}. Puede haber servicios o instancias relacionadas que impidan la eliminación.')
            print(f"DEBUG: Error al eliminar servicio de nutricionista: {e}")
            return render(request, 'core/nutricionista_servicio_confirm_delete.html', {'servicio': servicio, 'error': f'Error al eliminar: {e}. Puede haber servicios o instancias relacionadas.'})

    print("DEBUG: Solicitud GET para confirmar eliminación (nutricionista).")
    return render(request, 'core/nutricionista_servicio_confirm_delete.html', {'servicio': servicio})


# Vistas para la API externa de clientes (Sabor Latino)
def listar_clientes(request):
    """
    Función que consume la API externa de clientes y muestra los datos.
    Esto es solo un ejemplo, no directamente relacionado con el carrito.
    """
    url = "https://api-sabor-latino-chile.onrender.com/clientes"
    clientes = []
    try:
        response = requests.get(url)
        response.raise_for_status() # Lanza un error para estados HTTP 4xx/5xx
        clientes = response.json()
    except requests.RequestException as e:
        print(f"Error al conectar con la API de clientes: {e}")
        messages.error(request, f"Error al cargar clientes desde la API externa: {e}")
    except json.JSONDecodeError:
        print("Error: No se pudo decodificar la respuesta JSON de la API de clientes.")
        messages.error(request, "Error al procesar datos de la API externa de clientes.")
    return render(request, 'core/clientes.html', {'clientes': clientes}) # Asegúrate de tener 'core/clientes.html'


def clean_and_split_rut(rut_completo):
    """Limpia y separa el RUT."""
    cleaned_rut = str(rut_completo).replace('.', '').replace('-', '').strip().upper()
    if len(cleaned_rut) < 2 or not cleaned_rut[:-1].isdigit():
        return None, None
    return cleaned_rut[:-1], cleaned_rut[-1]

def check_rut_in_external_api(user_rut_completo):
    """Verifica el RUT en la API externa."""
    user_rut_numerico, user_dv_rut = clean_and_split_rut(user_rut_completo)
    print(f"DEBUG (API): Verificando RUT usuario: Num='{user_rut_numerico}', DV='{user_dv_rut}'") # <--- AÑADIDO
    if not user_rut_numerico or not user_dv_rut:
        print(f"DEBUG (API): RUT inválido para verificación: {user_rut_completo}")
        return False
    try:
        response = requests.get(settings.DISCOUNT_API_URL)
        response.raise_for_status()
        clientes_api_data = response.json()
        for cliente_api in clientes_api_data:
            api_rut_completo = cliente_api.get('numero_rut')
            api_dv_api = cliente_api.get('dv_rut') # <--- ASUMO QUE ESTE CAMPO EXISTE
            print(f"DEBUG (API): RUT API: Num='{api_rut_completo}', DV='{api_dv_api}'") # <--- AÑADIDO
            if api_rut_completo == user_rut_numerico and api_dv_api == user_dv_rut:
                print(f"DEBUG (API): RUT {user_rut_completo} encontrado en la API.")
                return True
        print(f"DEBUG (API): RUT {user_rut_completo} no encontrado en la API.")
        return False
    except requests.RequestException as e:
        print(f"ERROR (API): Fallo al conectar con la API de descuentos: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR (API): Error al decodificar JSON de la API de descuentos: {e}")
        return False
    except Exception as e:
        print(f"ERROR (API): Error inesperado al verificar RUT: {e}")
        return False

import requests
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Nueva Vista para Obtener el Estado del Descuento (para JS en frontend)
@login_required
@user_passes_test(is_cliente) # Solo clientes pueden consultar su descuento
def get_discount_status(request):
    print(f"DEBUG: ID del usuario logueado: {request.user.rut}")
    print("DEBUG: Entrando a get_discount_status")
    user = request.user
    rut_usuario_completo = user.rut.replace('-', '') if user.rut else None
    print(f"DEBUG: RUT del usuario (sin guion): {rut_usuario_completo}")

    api_url = settings.DISCOUNT_API_URL
    try:
        print(f"DEBUG: Consultando API en: {api_url}")
        response = requests.get(api_url)
        response.raise_for_status()
        api_clientes = response.json()
        print(f"DEBUG: Respuesta de la API (primer cliente): {api_clientes[0] if api_clientes else '[]'}")

        ruts_con_descuento_api = [f"{cliente['numero_rut']}{cliente['dv_rut']}" for cliente in api_clientes]
        print(f"DEBUG: RUTs con descuento de la API: {ruts_con_descuento_api}")

        if rut_usuario_completo in ruts_con_descuento_api:
            print("DEBUG: Descuento aplicable")
            return JsonResponse({'discount_eligible': True})
        else:
            print("DEBUG: Descuento no aplicable")
            return JsonResponse({'discount_eligible': False})
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Error de API: {e}")
        return JsonResponse({'discount_eligible': False})
    except Exception as e:
        print(f"DEBUG: Error inesperado: {e}")
        return JsonResponse({'discount_eligible': False})


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
        return render(request, 'core/lista_servicios_pf.html', {'servicios': servicios})


def crear_servicio_pf(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_servicios_pf')
    else:
        form = ServicioForm()  # <-- Definir el form cuando no es POST

    return render(request, 'core/crear_servicio_pf.html', {'form': form})

    # Editar servicio (vista y URL: editar_servicio_pf)
def editar_servicio_pf(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect('lista_servicios_pf')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'core/lista_servicios_pf_crear.html', {'form': form})



    # Eliminar servicio (vista y URL: eliminar_servicio_pf)
def confirmar_eliminar_pf(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        servicio.delete()   
        return redirect('lista_servicios_pf')
    return render(request, 'core/confirmar_eliminar_pf.html', {'servicio': servicio})


    # Lista mensajes (vista y URL: lista_mensajes_pf)
   



# API PAYPAL:

import json
from decimal import Decimal
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json
from decimal import Decimal
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# URL de la API externa (global o en settings)

@csrf_exempt
@csrf_exempt
def crear_orden_paypal(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            total = Decimal(data.get('total', '0.00'))

            paypal_api_url = "https://api-m.sandbox.paypal.com"
            paypal_client_id = "ASv3Tlw7XzUwvewH2xz9Yd3OJxVj9YbGayAebI4AvdabehIiOtbkR5vFqAbT8lAMTD32ihppxzIIcF2P"
            paypal_client_secret = "EIJsXoyfLc5cnhKXMKRarDL4xjaSfvq_ErpUmbZyAGTQKAWoMFhQm0AgmbxS1vS682jiElUqphs6x1ph"

            auth_response = requests.post(
                f"{paypal_api_url}/v1/oauth2/token",
                auth=(paypal_client_id, paypal_client_secret),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={'grant_type': 'client_credentials'}
            )
            auth_response.raise_for_status()
            auth_json = auth_response.json()
            access_token = auth_json['access_token']

            headers = {
                'Content-Type': 'application/json',
                f'Authorization': f'Bearer {access_token}'
            }
            order_payload = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": "USD", # Se mantiene en USD
                        "value": f"{total:.2f}"
                    }
                }]
            }

            print("Payload enviado a PayPal (Crear Orden):", json.dumps(order_payload, indent=4))

            order_response = requests.post(
                f"{paypal_api_url}/v2/checkout/orders",
                headers=headers,
                json=order_payload
            )
            order_response.raise_for_status()
            order_data = order_response.json()

            print("Respuesta de PayPal (Crear Orden):", json.dumps(order_data, indent=4))

            return JsonResponse({'id': order_data['id']})

        except requests.exceptions.RequestException as e:
            print(f"Error al contactar la API de PayPal (Crear Orden): {e}")
            return JsonResponse({'error': 'Error al crear la orden en PayPal'}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
        except Exception as e:
            print(f"Error inesperado al crear la orden: {e}")
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


# Función auxiliar para calcular el total desde los datos del carrito
def calculate_total_from_cart(cart_data):
    total = Decimal('0.00')
    for item in cart_data:
        total += Decimal(item['precio']) * item['cantidad']
    return total

# detalle producto

def detalle_producto(request, id_producto):
    # Ya estás obteniendo el objeto Producto correctamente aquí
    # Siempre usa 'pk' para la clave primaria, o el nombre real del campo si no es 'id'
    producto = get_object_or_404(Producto, pk=id_producto)

    # Filtra los comentarios por el objeto 'producto' (no solo el ID)
    comentarios = ComentarioValoracionProducto.objects.filter(id_producto=producto).order_by('-fecha_comentario')

    if request.method == 'POST':
        form = ComentarioValoracionForm(request.POST)
        if form.is_valid():
            # Crea una instancia del comentario pero NO la guarda todavía en la base de datos
            # Esto nos permite asignarle las claves foráneas antes de guardarla.
            nuevo_comentario = form.save(commit=False) 
            
            # Asigna el objeto Producto (la instancia completa) al campo id_producto
            nuevo_comentario.id_producto = producto 
            
            # Asigna el objeto Usuario actual (request.user) al campo id_usuario.
            # Asegúrate de que 'request.user' sea una instancia de tu modelo de Usuario.
            nuevo_comentario.id_usuario = request.user 
            
            # Ahora sí, guarda el comentario con las relaciones correctas en la base de datos
            nuevo_comentario.save() 

            return redirect('detalle_producto', id_producto=id_producto)
    else:
        form = ComentarioValoracionForm()

    return render(request, 'core/detalle_producto.html', {
        'producto': producto,
        'comentarios': comentarios,
        'form': form
    })


#seguimiento
try:
    from gymlife.config import AFTERSHIP_API_KEY, AFTERSHIP_API_BASE_URL
except ImportError:
        # Asegúrate de que estas variables de entorno estén configuradas en tu sistema
        AFTERSHIP_API_KEY = os.environ.get('AFTERSHIP_API_KEY', '')
        AFTERSHIP_API_BASE_URL = os.environ.get('AFTERSHIP_API_BASE_URL', 'https://api.aftership.com/v4')


@login_required(login_url='login')
def seguimiento_pedido(request, venta_id):
    venta = None
    envio = None
    detalles_compra = []
    detalles_servicios = []
    info_seguimiento = None
    error_seguimiento = None

    try:
        # Intenta obtener la VentaProducto y asegurar que pertenece al usuario
        venta = get_object_or_404(VentaProducto, id_venta_producto=venta_id, id_cliente=request.user)
        # Ajusta la línea anterior según tu modelo de usuario y VentaProducto.id_cliente

        # Obtener detalles de productos
        detalles_compra = DetalleCompra.objects.filter(id_venta_producto=venta)

        # Obtener detalles de servicios
        # Si DetalleServicioAdquirido tiene FK a VentaProducto, es más directo:
        # detalles_servicios = DetalleServicioAdquirido.objects.filter(id_venta_producto=venta)
        # Si no, esto es más complejo. Por ahora, asumiré una relación indirecta o que no se muestran por venta específica.
        # Ajusta esta parte si necesitas filtrar servicios por venta específica
        detalles_servicios = DetalleServicioAdquirido.objects.filter(id_cliente=request.user) # Esto obtiene todos los servicios del usuario

        # Intentar obtener el registro de envío
        try:
            envio = Envio.objects.get(id_venta_producto=venta)
        except Envio.DoesNotExist:
            envio = None # No hay envío para esta venta

        # Si hay un envío y tiene código de rastreo y transportista, consultar AfterShip
        if envio and envio.codigo_rastreo and envio.nombre_transportista:
            info_seguimiento, error_seguimiento = get_aftership_tracking_info(
                envio.codigo_rastreo, envio.nombre_transportista
            )
            if error_seguimiento:
                print(f"Error al obtener seguimiento de AfterShip para Venta ID {venta_id}: {error_seguimiento}")
        # --- ESTE ES EL CAMBIO CLAVE PARA ELIMINAR EL ERROR DE DEFINICIÓN ---
        # Si hay un envío pero no tiene código de rastreo (aún no se ha asignado)
        elif envio and not envio.codigo_rastreo:
            error_seguimiento = "Pedido con productos físicos, pero el código de rastreo aún no está disponible."
        # No necesitas un 'elif has_physical_products and not envio' aquí,
        # la ausencia de 'envio' ya indica que no hay seguimiento físico en la DB.
        # Puedes añadir un mensaje si quieres, pero no es estrictamente necesario para el error.


    except VentaProducto.DoesNotExist:
        error_seguimiento = "Pedido no encontrado o no tienes permiso para verlo."
        print(f"DEBUG SEGUIMIENTO: Venta ID {venta_id} no encontrada o no pertenece al usuario {request.user.username}.")
    except Exception as e:
        error_seguimiento = f"Ocurrió un error al cargar los detalles del pedido: {e}"
        print(f"ERROR SEGUIMIENTO: Error inesperado para Venta ID {venta_id}: {e}")

    context = {
        'venta': venta,
        'detalles_compra': detalles_compra,
        'detalles_servicios': detalles_servicios,
        'envio': envio,
        'info_seguimiento': info_seguimiento,
        'error_seguimiento': error_seguimiento,
    }
    return render(request, 'core/seguimiento_pedido.html', context)




@login_required
def detalle_venta_producto(request, venta_id): # RENOMBRADA LA FUNCIÓN
    """
    Vista para mostrar los detalles de una VentaProducto específica.
    """
    venta = get_object_or_404(VentaProducto, id_venta_producto=venta_id, id_cliente=request.user.id_usuario)

    envio = None
    try:
        envio = Envio.objects.get(id_venta_producto=venta)
    except Envio.DoesNotExist:
        pass

    detalles_compra = DetalleCompra.objects.filter(id_venta_producto=venta)

    context = {
        'venta': venta,
        'envio': envio,
        'detalles_compra': detalles_compra,
        'from_mis_compras': True # Agregamos un contexto para la plantilla, útil si la vista se usa también como "pago exitoso" inicial
    }
    return render(request, 'core/pago_exitoso.html', context) # Sigue usando tu plantilla pago_exitoso.html