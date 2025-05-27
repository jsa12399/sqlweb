# Integracion_Proyecto/core/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

# --- CustomUserManager para tu modelo Usuario ---
# Este manager le dice a Django cómo crear y gestionar usuarios con tu modelo.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El campo Email es obligatorio')
        email = self.normalize_email(email)
        
        # IMPORTANTE: NO PASES 'id_usuario' aquí si Oracle es quien lo genera.
        # Django debe crear una instancia sin PK inicialmente.
        user = self.model(email=email, **extra_fields)
        
        user.set_password(password)
        
        # La clave está en el 'save()'. Si el objeto no tiene PK, Django hará un INSERT.
        # Si tiene PK, intentará un UPDATE. Para un nuevo usuario, user.pk debe ser None.
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # Importa TipoUsuario y Comuna aquí dentro del manager
        # para asegurar que estén disponibles cuando se necesiten.
        from .models import TipoUsuario, Comuna 

        # Asigna un ID de TipoUsuario por defecto para el superusuario
        if 'id_tipo_usuario' not in extra_fields:
            try:
                extra_fields['id_tipo_usuario'] = TipoUsuario.objects.get(id_tipo_usuario=1) 
            except TipoUsuario.DoesNotExist:
                raise ValueError("No se encontró un TipoUsuario con ID 1 para el superusuario. Asegúrate de que exista en tu base de datos Oracle.")
        
        # Asigna un ID de Comuna por defecto para el superusuario (si id_comuna es NOT NULL en la DB)
        # Comprobamos si el campo es nulo en el modelo de Django para decidir si asignar un valor por defecto.
        # Si tu columna ID_COMUNA en Oracle es NOT NULL, y no estás pidiéndola en REQUIRED_FIELDS,
        # debes darle un valor por defecto aquí.
        if 'id_comuna' not in extra_fields:
             # Usa self.model._meta.get_field('id_comuna').null para verificar si el campo es null=True o null=False
             # en el modelo de Django. Si null=False (o si es null=True pero quieres un valor por defecto para superuser)
             if not self.model._meta.get_field('id_comuna').null: # Si el campo NO es nulo en el modelo
                try:
                    extra_fields['id_comuna'] = Comuna.objects.get(id_comuna=1) 
                except Comuna.DoesNotExist:
                    raise ValueError("No se encontró una Comuna con ID 1 para el superusuario. Asegúrate de que exista en tu base de datos Oracle.")
             else:
                 # Si id_comuna es null=True en tu modelo, puedes no asignarle nada aquí si quieres que sea NULL por defecto
                 # para el superusuario, o asignar un valor específico si lo prefieres.
                 # Para asegurar consistencia, si existe un valor por defecto deseado, se podría asignar.
                 # Por ahora, si es null=True, simplemente no lo asignamos si no se proporciona.
                 pass # No hagas nada si id_comuna puede ser NULL en la DB y no se ha proporcionado

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# --- TU MODELO USUARIO ADAPTADO ---
class Usuario(AbstractBaseUser, PermissionsMixin):
    # La clave primaria de tu tabla USUARIO en Oracle.
    # Con 'managed = False', Django no intentará autoincrementarla.
    # Oracle debe manejar la generación de este ID (con secuencia y trigger).
    # Agregamos db_column explícitamente y nos aseguramos que Oracle lo genere.
    id_usuario = models.BigIntegerField(primary_key=True, db_column='ID_USUARIO') 

    # ... el resto de tus campos ...

    # Asegúrate de que todos los campos relevantes tengan db_column explícito
    rut = models.CharField(unique=True, max_length=12, verbose_name=_('RUT'), db_column='RUT')
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre'), db_column='NOMBRE')
    apellido = models.CharField(max_length=100, verbose_name=_('Apellido'), db_column='APELLIDO')
    email = models.EmailField(unique=True, verbose_name=_('Email'), db_column='EMAIL')
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name=_('Teléfono'), db_column='TELEFONO')
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Dirección'), db_column='DIRECCION')

    # Foreign Keys
    id_comuna = models.ForeignKey('Comuna', on_delete=models.SET_NULL, db_column='ID_COMUNA', null=True, blank=True, verbose_name=_('Comuna'))
    id_tipo_usuario = models.ForeignKey('TipoUsuario', on_delete=models.SET_NULL, db_column='ID_TIPO_USUARIO', null=True, blank=True, verbose_name=_('Tipo de Usuario')) 

    # CAMPOS DE AUTENTICACIÓN DE DJANGO
    is_active = models.BooleanField(default=True, db_column='IS_ACTIVE') # Agregué db_column
    is_staff = models.BooleanField(default=False, db_column='IS_STAFF') # Agregué db_column
    is_superuser = models.BooleanField(default=False, db_column='IS_SUPERUSER') # Agregué db_column
    last_login = models.DateTimeField(null=True, blank=True, db_column='LAST_LOGIN') # Agregué db_column

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['rut', 'nombre', 'apellido']

    class Meta:
        managed = False
        db_table = 'USUARIO'
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"

    def get_short_name(self):
        return self.nombre

    # Métodos requeridos por PermissionsMixin para manejar permisos en Django
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplificado: superusuario tiene todos los permisos
        return self.is_active and self.is_superuser 

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplificado: superusuario tiene permisos en todas las apps si es staff
        return self.is_active and self.is_staff 

# --- EL RESTO DE TUS MODELOS (con ajustes para consistencia y db_column) ---

class Ciudad(models.Model):
    id_ciudad = models.BigIntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'CIUDAD' # Asegúrate del nombre exacto en mayúsculas

    def __str__(self):
        return self.nombre

class Comuna(models.Model):
    id_comuna = models.BigIntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    # db_column debe coincidir con el nombre de la columna FK en tu tabla COMUNA de Oracle
    id_ciudad = models.ForeignKey(Ciudad, models.DO_NOTHING, db_column='ID_CIUDAD') 
    class Meta:
        managed = False
        db_table = 'COMUNA' # Asegúrate del nombre exacto en mayúsculas

    def __str__(self):
        return self.nombre

class TipoUsuario(models.Model):
    id_tipo_usuario = models.BigIntegerField(primary_key=True)
    tipo_usuario = models.CharField(max_length=50, unique=True) # Añadí unique=True
    class Meta:
        managed = False
        db_table = 'TIPO_USUARIO' # Asegúrate del nombre exacto en mayúsculas

    def __str__(self):
        return self.tipo_usuario

class Producto(models.Model):
    id_producto = models.BigIntegerField(primary_key=True)
    nombre_producto = models.CharField(max_length=100, db_column='NOMBRE') # Renombré de 'nombre' a 'nombre_producto' para claridad
    descripcion = models.CharField(max_length=500, blank=True, null=True)
    stock = models.BigIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Asumo que tienes una tabla CATEGORIA y un campo ID_CATEGORIA en PRODUCTO
    id_categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, db_column='ID_CATEGORIA', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'PRODUCTO' # Asegúrate del nombre exacto en mayúsculas

    def __str__(self):
        return self.nombre_producto

class Categoria(models.Model):
    id_categoria = models.BigIntegerField(primary_key=True)
    nombre_categoria = models.CharField(max_length=100, unique=True)
    class Meta:
        managed = False
        db_table = 'CATEGORIA'
    def __str__(self):
        return self.nombre_categoria


class ComentarioValoracionProducto(models.Model):
    id_comentario_valoracion = models.BigIntegerField(primary_key=True)
    id_producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='ID_PRODUCTO') # Cambié a ID_PRODUCTO
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='ID_USUARIO') # Cambié a ID_USUARIO
    comentario = models.CharField(max_length=500)
    valoracion = models.BigIntegerField()
    fecha_comentario = models.DateField()
    class Meta:
        managed = False
        db_table = 'COMENTARIO_VALORACION_PRODUCTO' # Asegúrate del nombre exacto en mayúsculas

class DetalleCompra(models.Model):
    # NOTA MUY IMPORTANTE SOBRE CLAVES COMPUESTAS:
    # Django NO soporta claves primarias compuestas con 'managed=False' de forma nativa y fácil.
    # Si DETALLE_COMPRA tiene una PK compuesta en Oracle (ej. PK(ID_VENTA_PRODUCTO, ID_PRODUCTO)),
    # vas a tener problemas con Django.
    # Las soluciones son:
    # 1. Modificar tu tabla Oracle para tener una CLAVE PRIMARIA SIMPLE (ej. un ID_DETALLE_COMPRA auto-generado).
    # 2. Si no puedes modificar la DB, y no necesitas que Django gestione estas inserciones directamente,
    #    podrías necesitar usar SQL puro para las operaciones en esta tabla, o revisar librerías de terceros.
    #    Por ahora, asumiré que tienes una PK simple.
    id_detalle_boleta = models.BigIntegerField(primary_key=True) # Asumiendo que esta es tu PK simple
    id_venta_producto = models.ForeignKey('VentaProducto', models.DO_NOTHING, db_column='ID_VENTA_PRODUCTO') # Cambié a ID_VENTA_PRODUCTO
    id_producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='ID_PRODUCTO') # Cambié a ID_PRODUCTO
    cantidad_adquirida = models.BigIntegerField()
    precio_venta_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal_detalle = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        managed = False
        db_table = 'DETALLE_COMPRA' # Asegúrate del nombre exacto en mayúsculas

class DetalleServicioAdquirido(models.Model):
    id_sa = models.BigIntegerField(primary_key=True)
    id_cliente = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='ID_CLIENTE') # Cambié a ID_CLIENTE
    id_instancia_servicio = models.ForeignKey('InstanciaServicio', models.DO_NOTHING, db_column='ID_INSTANCIA_SERVICIO') # Cambié a ID_INSTANCIA_SERVICIO
    fecha_hora_adquisicion = models.DateField()
    precio_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    id_mp = models.ForeignKey('MetodosDePago', models.DO_NOTHING, db_column='ID_MP') # Cambié a ID_MP
    class Meta:
        managed = False
        db_table = 'DETALLE_SERVICIO_ADQUIRIDO' # Asegúrate del nombre exacto en mayúsculas

class Envio(models.Model):
    id_envio = models.BigIntegerField(primary_key=True)
    id_venta_producto = models.OneToOneField('VentaProducto', models.DO_NOTHING, db_column='ID_VENTA_PRODUCTO') # Cambié a ID_VENTA_PRODUCTO
    fecha_envio = models.DateField()
    fecha_estimada_entrega = models.DateField(blank=True, null=True)
    fecha_entrega_real = models.DateField(blank=True, null=True)
    estado_envio = models.CharField(max_length=50)
    codigo_rastreo = models.CharField(unique=True, max_length=100, blank=True, null=True)
    nombre_transportista = models.CharField(max_length=100, blank=True, null=True)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'ENVIO' # Asegúrate del nombre exacto en mayúsculas

class InstanciaServicio(models.Model):
    id_instancia_servicio = models.BigIntegerField(primary_key=True)
    id_servicio = models.ForeignKey('Servicio', models.DO_NOTHING, db_column='ID_SERVICIO') # Cambié a ID_SERVICIO
    id_proveedor_servicio = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='ID_PROVEEDOR_SERVICIO', blank=True, null=True) # Cambié a ID_PROVEEDOR_SERVICIO
    fecha_hora_programada = models.DateField()
    reservado = models.CharField(max_length=1)
    estado_instancia = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'INSTANCIA_SERVICIO' # Asegúrate del nombre exacto en mayúsculas

class MetodosDePago(models.Model):
    id_mp = models.BigIntegerField(primary_key=True)
    tipo_pago = models.CharField(max_length=50)
    class Meta:
        managed = False
        db_table = 'METODOS_DE_PAGO' # Asegúrate del nombre exacto en mayúsculas

class Servicio(models.Model):
    id_servicio = models.BigIntegerField(primary_key=True)
    # Aquí asumo que id_proveedor_servicio en Oracle se refiere al ID_USUARIO de la tabla USUARIO.
    # Si se refiere al RUT, tendrías que haberlo definido como unique en Usuario y usar to_field='rut'.
    # Pero lo más común es que se use la PK.
    id_proveedor_servicio = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='ID_PROVEEDOR_SERVICIO') # Cambié a ID_PROVEEDOR_SERVICIO y quité to_field='rut'
    nombre_servicio = models.CharField(max_length=100)
    descripcion_servicio = models.CharField(max_length=500, blank=True, null=True)
    precio_servicio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_minutos = models.BigIntegerField(blank=True, null=True)
    disponible = models.CharField(max_length=1) # Asumo que es 'S'/'N' o '0'/'1'
    class Meta:
        managed = False
        db_table = 'SERVICIO' # Asegúrate del nombre exacto en mayúsculas

class VentaProducto(models.Model):
    id_venta_producto = models.BigIntegerField(primary_key=True)
    id_cliente = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='ID_CLIENTE') # Cambié a ID_CLIENTE
    id_empleado = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='ID_EMPLEADO', related_name='ventaproducto_id_empleado_set', blank=True, null=True) # Cambié a ID_EMPLEADO
    fecha_venta = models.DateField()
    total_venta = models.DecimalField(max_digits=10, decimal_places=2)
    id_mp = models.ForeignKey(MetodosDePago, models.DO_NOTHING, db_column='ID_MP') # Cambié a ID_MP
    class Meta:
        managed = False
        db_table = 'VENTA_PRODUCTO' # Asegúrate del nombre exacto en mayúsculas