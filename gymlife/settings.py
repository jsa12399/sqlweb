# settings.py

from pathlib import Path
import os
import oracledb # Importa oracledb aquí

# Si tienes problemas con Instant Client o quieres forzar el modo Thin,
# puedes inicializar oracledb aquí.
# Si NO tienes Instant Client instalado, oracledb intentará conectarse en modo Thin por defecto.
# Si el modo Thin NO te funciona y tienes Instant Client, deberías quitar esta línea y
# asegurarte de que Instant Client esté en tu PATH o especificar lib_dir.
# En la mayoría de los casos, si usas `oracledb` sin Instant Client,
# no necesitas `oracledb.init_oracle_client()` explícitamente.
# La remoción de 'thin_mode' de OPTIONS es la clave.
try:
    # Esto es más para casos donde el modo Thick es necesario y el cliente no está en PATH
    # Si estás usando el modo Thin (sin Instant Client), generalmente NO es necesario.
    # oracledb.init_oracle_client()
    pass
except oracledb.Error as e:
    # Puedes manejar el error si oracledb no puede encontrar las librerías cliente,
    # aunque para el modo Thin no suele ser un problema de este tipo.
    print(f"Error al inicializar oracledb: {e}")
    pass


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-!rg+*xwv-7z#qr5@%hxr&rd=6)kmgde+8li9^rnq_a+d+%z*p)'

DEBUG = True

ALLOWED_HOSTS = []

# Apps instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
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
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'XE', # Confirma que 'XE' es tu SID o Service Name
        'USER': 'WEBFIT', # Tu nombre de usuario de Oracle
        'PASSWORD': 'hola123', # Tu contraseña de Oracle
        'HOST': 'localhost', # La IP o nombre de host de tu servidor Oracle
        'PORT': '1521', # El puerto de tu base de datos Oracle (por defecto 1521)
        'OPTIONS': {
            # Hemos quitado 'encoding' y 'thin_mode' de aquí porque causan TypeError
            # oracledb usa UTF-8 por defecto en modo Thin.
            # Si tu base de datos está en otro charset o tienes problemas con caracteres,
            # considera configurar la variable de entorno NLS_LANG en tu sistema.
            # Ejemplo (para Windows, antes de ejecutar manage.py): set NLS_LANG=SPANISH_SPAIN.AL32UTF8
            # Para Linux/macOS: export NLS_LANG=SPANISH_SPAIN.AL32UTF8
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
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'core', 'static')]

# Archivos multimedia (si usas imágenes cargadas por usuarios en el futuro)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'