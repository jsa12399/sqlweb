from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from .models import Producto  # ¡Asegúrate de agregar esta línea para importar Producto!

User = get_user_model()

def index(request):
    return render(request, 'core/index.html')

def nutricionista(request):
    return render(request, 'core/nutricionista.html')

def preparadorfisico(request):
    if request.method == 'POST':
        # Aquí puedes procesar el formulario si quieres
        pass
    return render(request, 'core/preparadorfisico.html')

def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'core/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'core/login.html')

def register_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            User.objects.create_user(username=email, email=email, password=password)
            return redirect('login')
        else:
            return render(request, 'core/register.html', {'error': 'Las contraseñas no coinciden'})
    return render(request, 'core/register.html')

def ver_productos(request):
    # Obtener todos los productos de la base de datos
    productos = Producto.objects.all()

    # Crear un diccionario de contexto para pasar los productos a la plantilla
    context = {
        'productos': productos
    }

    # Renderizar la plantilla 'productos.html' y pasar el contexto
    return render(request, 'core/productos.html', context)