import requests
from django.shortcuts import render

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