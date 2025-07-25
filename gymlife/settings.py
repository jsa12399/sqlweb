# settings.py

from pathlib import Path
import os
 # Importa oracledb aquí

# Si tienes problemas con Instant Client o quieres forzar el modo Thin,
# puedes inicializar oracledb aquí.
# Si NO tienes Instant Client instalado, oracledb intentará conectarse en modo Thin por defecto.
# Si el modo Thin NO te funciona y tienes Instant Client, deberías quitar esta línea y
# asegurarte de que Instant Client esté en tu PATH o especificar lib_dir.
# En la mayoría de los casos, si usas `oracledb` sin Instant Client,
# no necesitas `oracledb.init_oracle_client()` explícitamente.
# La remoción de 'thin_mode' de OPTIONS es la clave.
#try:
    # Esto es más para casos donde el modo Thick es necesario y el cliente no está en PATH
    # Si estás usando el modo Thin (sin Instant Client), generalmente NO es necesario.
    # oracledb.init_oracle_client()
    #pass
#except oracledb.Error as e:
    # Puedes manejar el error si oracledb no puede encontrar las librerías cliente,
    # aunque para el modo Thin no suele ser un problema de este tipo.
    #print(f"Error al inicializar oracledb: {e}")
    #pass


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-!rg+*xwv-7z#qr5@%hxr&rd=6)kmgde+8li9^rnq_a+d+%z*p)'

DEBUG = True

DISCOUNT_API_URL = "https://api-sabor-latino-chile.onrender.com/clientes"

ALLOWED_HOSTS = []

# Apps instaladas
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize', # Ya lo tienes, ¡bien!
    'django.contrib.staticfiles',
    'core', # Tu aplicación 'core' - ¡Esto es CRÍTICO!
]

# ** ------------------- INICIO DE LAS LÍNEAS A AÑADIR/VERIFICAR ------------------- **

# Configuración del modelo de usuario personalizado
AUTH_USER_MODEL = 'core.Usuario' # ¡Esta línea es FUNDAMENTAL para usar tu modelo!

# URLs a donde Django redirige para login/logout
LOGIN_URL = '/iniciar-sesion/' 
LOGIN_REDIRECT_URL = '/' # Después de iniciar sesión, va a la página de inicio
LOGOUT_REDIRECT_URL = '/iniciar-sesion/' # Después de cerrar sesión, va a la página de login

# Configuración de localización para números (Chile) - Ya las tienes abajo, pero las muevo aquí para agrupar
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_L10N = True # USE_L10N es True para usar el formato local de números/fechas

# Para el formato numérico chileno (punto para miles, coma para decimales)
DECIMAL_SEPARATOR = ','
THOUSAND_SEPARATOR = '.'
USE_THOUSAND_SEPARATOR = True 

# ** -------------------- FIN DE LAS LÍNEAS A AÑADIR/VERIFICAR -------------------- **


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gymlife.urls'

# Configuración de plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Asegúrate de que esta ruta sea correcta para tus templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gymlife.wsgi.application'

# Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'WEBFIT_DB',
        'HOST': r'.\SQLEXPRESS', # Usa r'' para cadena sin procesar
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'MARS_Connection': True,
            'Trusted_Connection': 'yes',
        }
    }
}

# Validaciones de contraseña
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Las movimos arriba para agrupar las configuraciones de localización, pero si las dejas aquí, también funcionarán.
# LANGUAGE_CODE = 'es-cl'
# TIME_ZONE = 'America/Santiago'
# USE_I18N = True
# USE_TZ = True 

# Archivos estáticos (CSS, JS, imágenes)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'core', 'static')]

# Archivos multimedia (si usas imágenes cargadas por usuarios en el futuro)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PAYPAL_API_URL = "https://api-m.sandbox.paypal.com" # Para pruebas en Sandbox
PAYPAL_CLIENT_ID = "ASv3Tlw7XzUwvewH2xz9Yd3OJxVj9YbGayAebI4AvdabehIiOtbkR5vFqAbT8lAMTD32ihppxzIIcF2P"
PAYPAL_CLIENT_SECRET = "EIJsXoyfLc5cnhKXMKRarDL4xjaSfvq_ErpUmbZyAGTQKAWoMFhQm0AgmbxS1vS682jiElUqphs6x1ph"

import paypalrestsdk

paypalrestsdk.configure({
    "mode": "sandbox",  # o "live" para producción
    "client_id": "ASv3Tlw7XzUwvewH2xz9Yd3OJxVj9YbGayAebI4AvdabehIiOtbkR5vFqAbT8lAMTD32ihppxzIIcF2P",
    "client_secret": "EIJsXoyfLc5cnhKXMKRarDL4xjaSfvq_ErpUmbZyAGTQKAWoMFhQm0AgmbxS1vS682jiElUqphs6x1ph"
})

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'core.views': {  # Logger específico para tus vistas en la app 'core'
            'handlers': ['console'],
            'level': 'INFO',  # O 'DEBUG' si quieres ver más detalles
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}