from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings # ¡Importante: para settings.AUTH_USER_MODEL!
from django.utils import timezone # Para timezone.now en MensajeServicio

# NO NECESITAS ESTA IMPORTACIÓN: from django.contrib.auth.models import User
# Estás usando tu modelo Usuario personalizado, no el de Django.


# --- CustomUserManager para tu modelo Usuario ---
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El campo Email es obligatorio')
        email = self.normalize_email(email)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # Importa TipoUsuario y Comuna aquí para asegurar que estén disponibles.
        # Ya que están en el mismo models.py, 'self.model' también puede referenciarlos.
        from .models import TipoUsuario, Comuna 

        if 'id_tipo_usuario' not in extra_fields:
            try:
                extra_fields['id_tipo_usuario'] = TipoUsuario.objects.get(id_tipo_usuario=1) 
            except TipoUsuario.DoesNotExist:
                raise ValueError("No se encontró un TipoUsuario con ID 1 para el superusuario. Asegúrate de que exista en tu base de datos Oracle.")
        
        if 'id_comuna' not in extra_fields:
             if not self.model._meta.get_field('id_comuna').null: 
                try:
                    extra_fields['id_comuna'] = Comuna.objects.get(id_comuna=1) 
                except Comuna.DoesNotExist:
                    raise ValueError("No se encontró una Comuna con ID 1 para el superusuario. Asegúrate de que exista en tu base de datos Oracle.")
             else:
                 pass

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# --- ELIMINADO EL MODELO 'Servicio' DUPLICADO DE AQUÍ ---
# El Servicio correcto es el que está abajo con managed = False.

# --- CORREGIDO: MENSAJE_SERVICIO AHORA APUNTA AL MODELO DE USUARIO PERSONALIZADO ---
class MensajeServicio(models.Model):
    id_mensaje_servicio = models.IntegerField(primary_key=True, db_column='ID_MENSAJE_SERVICIO')
    # Apunta a settings.AUTH_USER_MODEL para el modelo de usuario personalizado
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, # ¡CORREGIDO!
        on_delete=models.CASCADE, 
        related_name='mensajes_enviados', # Nombre de related_name para evitar conflictos
        db_column='ID_CLIENTE'
    )
    # Servicio se referencia como cadena de texto 'Servicio' para asegurar que apunte al modelo correcto
    servicio = models.ForeignKey(
        'Servicio', # ¡CORREGIDO: Referencia como cadena de texto!
        on_delete=models.CASCADE, 
        related_name='mensajes_servicio', # Nombre de related_name para evitar conflictos
        db_column='ID_SERVICIO'
    )
    mensaje = models.TextField(db_column='MENSAJE') # Asegúrate que el db_column sea el correcto
    fecha_envio = models.DateTimeField(auto_now_add=True, db_column='FECHA_ENVIO') # Añadido db_column
    leido = models.CharField(max_length=1, db_column='LEIDO', default='N') # Asumiendo 'S'/'N' en Oracle, no bool

    class Meta:
        managed = False
        db_table = 'MENSAJE_SERVICIO'

    def __str__(self):
        return f"Mensaje de {self.cliente.email} para {self.servicio.nombre_servicio}"


# --- TU MODELO USUARIO ADAPTADO (GYMLIFEUser) ---
class Usuario(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.BigAutoField(primary_key=True, db_column='ID_USUARIO')

    rut = models.CharField(unique=True, max_length=12, verbose_name=_('RUT'), db_column='RUT')
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre'), db_column='NOMBRE')
    apellido = models.CharField(max_length=100, verbose_name=_('Apellido'), db_column='APELLIDO')
    email = models.EmailField(unique=True, verbose_name=_('Email'), db_column='EMAIL')
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name=_('Teléfono'), db_column='TELEFONO')
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Dirección'), db_column='DIRECCION')

    id_comuna = models.ForeignKey('Comuna', on_delete=models.SET_NULL, db_column='ID_COMUNA', null=True, blank=True, verbose_name=_('Comuna'))
    id_tipo_usuario = models.ForeignKey('TipoUsuario', on_delete=models.SET_NULL, db_column='ID_TIPO_USUARIO', null=True, blank=True, verbose_name=_('Tipo de Usuario')) 

    is_active = models.BooleanField(default=True, db_column='IS_ACTIVE')
    is_staff = models.BooleanField(default=False, db_column='IS_STAFF')
    is_superuser = models.BooleanField(default=False, db_column='IS_SUPERUSER')
    last_login = models.DateTimeField(null=True, blank=True, db_column='LAST_LOGIN')

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

    def has_perm(self, perm, obj=None):
        return self.is_active and self.is_superuser 

    def has_module_perms(self, app_label):
        return self.is_active and self.is_staff

# --- EL RESTO DE TUS MODELOS (con ajustes para consistencia y db_column) ---

class Ciudad(models.Model):
    id_ciudad = models.BigIntegerField(primary_key=True, db_column='ID_CIUDAD') # Añadido db_column
    nombre = models.CharField(max_length=100, db_column='NOMBRE') # Añadido db_column
    class Meta:
        managed = False
        db_table = 'CIUDAD' 

    def __str__(self):
        return self.nombre

class Comuna(models.Model):
    id_comuna = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = False # O True
        db_table = 'COMUNA'

    def __str__(self):
        return self.nombre

class TipoUsuario(models.Model):
    id_tipo_usuario = models.IntegerField(primary_key=True)
    tipo_usuario = models.CharField(max_length=50)

    class Meta:
        managed = False # O True, dependiendo de si Django gestiona esta tabla
        db_table = 'TIPO_USUARIO'

    def __str__(self):
        return self.tipo_usuario

class Producto(models.Model):
    id_producto = models.BigIntegerField(primary_key=True, db_column='ID_PRODUCTO') # Añadido db_column
    nombre = models.CharField(max_length=100, db_column='NOMBRE') # Usé NOMBRE_PRODUCTO para evitar confusión con NOMBRE
    descripcion = models.CharField(max_length=500, blank=True, null=True, db_column='DESCRIPCION') # Añadido db_column
    stock = models.BigIntegerField(db_column='STOCK') # Añadido db_column
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, db_column='PRECIO_UNITARIO') # Añadido db_column
    
    id_categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, db_column='ID_CATEGORIA', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'PRODUCTO' 

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    id_categoria = models.BigIntegerField(primary_key=True, db_column='ID_CATEGORIA') # Añadido db_column
    nombre_categoria = models.CharField(max_length=100, unique=True, db_column='NOMBRE_CATEGORIA') # Añadido db_column
    class Meta:
        managed = False
        db_table = 'CATEGORIA'
    def __str__(self):
        return self.nombre_categoria


class ComentarioValoracionProducto(models.Model):
    id_comentario_valoracion = models.BigIntegerField(primary_key=True, db_column='ID_COMENTARIO_VALORACION') # Añadido db_column
    id_producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='ID_PRODUCTO') 
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='ID_USUARIO') # ¡CORREGIDO: Apunta a tu modelo Usuario!
    comentario = models.CharField(max_length=500, db_column='COMENTARIO') # Añadido db_column
    valoracion = models.BigIntegerField(db_column='VALORACION') # Añadido db_column
    fecha_comentario = models.DateField(db_column='FECHA_COMENTARIO') # Añadido db_column
    class Meta:
        managed = False
        db_table = 'COMENTARIO_VALORACION_PRODUCTO' 

class DetalleCompra(models.Model):
    id_detalle_boleta = models.BigIntegerField(primary_key=True, db_column='ID_DETALLE_BOLETA') # Añadido db_column
    id_venta_producto = models.ForeignKey('VentaProducto', models.DO_NOTHING, db_column='ID_VENTA_PRODUCTO') 
    id_producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='ID_PRODUCTO') 
    cantidad_adquirida = models.BigIntegerField(db_column='CANTIDAD_ADQUIRIDA') # Añadido db_column
    precio_venta_unitario = models.DecimalField(max_digits=10, decimal_places=2, db_column='PRECIO_VENTA_UNITARIO') # Añadido db_column
    subtotal_detalle = models.DecimalField(max_digits=10, decimal_places=2, db_column='SUBTOTAL_DETALLE') # Añadido db_column
    class Meta:
        managed = False
        db_table = 'DETALLE_COMPRA' 

class DetalleServicioAdquirido(models.Model):
    id_sa = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='ID_CLIENTE')
    id_instancia_servicio = models.ForeignKey('InstanciaServicio', models.DO_NOTHING, db_column='ID_INSTANCIA_SERVICIO')
    fecha_hora_adquisicion = models.DateField(db_column='FECHA_HORA_ADQUISICION')
    precio_pagado = models.DecimalField(max_digits=10, decimal_places=2, db_column='PRECIO_PAGADO')
    id_mp = models.ForeignKey('MetodosDePago', models.DO_NOTHING, db_column='ID_MP')
    class Meta:
        managed = False
        db_table = 'DETALLE_SERVICIO_ADQUIRIDO'

class Envio(models.Model):
    id_envio = models.BigIntegerField(primary_key=True, db_column='ID_ENVIO') # Añadido db_column
    id_venta_producto = models.OneToOneField('VentaProducto', models.DO_NOTHING, db_column='ID_VENTA_PRODUCTO') 
    fecha_envio = models.DateField(db_column='FECHA_ENVIO') # Añadido db_column
    fecha_estimada_entrega = models.DateField(blank=True, null=True, db_column='FECHA_ESTIMADA_ENTREGA') # Añadido db_column
    fecha_entrega_real = models.DateField(blank=True, null=True, db_column='FECHA_ENTREGA_REAL') # Añadido db_column
    estado_envio = models.CharField(max_length=50, db_column='ESTADO_ENVIO') # Añadido db_column
    codigo_rastreo = models.CharField(unique=True, max_length=100, blank=True, null=True, db_column='CODIGO_RASTREO') # Añadido db_column
    nombre_transportista = models.CharField(max_length=100, blank=True, null=True, db_column='NOMBRE_TRANSPORTISTA') # Añadido db_column
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, db_column='COSTO_ENVIO') # Añadido db_column
    class Meta:
        managed = False
        db_table = 'ENVIO' 

class InstanciaServicio(models.Model):
    id_instancia_servicio = models.BigAutoField(
        primary_key=True,
        db_column='ID_INSTANCIA_SERVICIO'
    )
    id_servicio = models.ForeignKey('Servicio', models.DO_NOTHING, db_column='ID_SERVICIO') 
    id_proveedor_servicio = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='ID_PROVEEDOR_SERVICIO', blank=True, null=True)
    fecha_hora_programada = models.DateField(db_column='FECHA_HORA_PROGRAMADA')
    reservado = models.CharField(max_length=1, db_column='RESERVADO', default='N') 
    # ¡CAMBIO AQUÍ! Usamos 'Programado'
    estado_instancia = models.CharField(max_length=50, db_column='ESTADO_INSTANCIA', default='Programado')
    class Meta:
        managed = False
        db_table = 'INSTANCIA_SERVICIO'

class MetodosDePago(models.Model):
    id_mp = models.BigIntegerField(primary_key=True, db_column='ID_MP') # Añadido db_column
    tipo_pago = models.CharField(max_length=50, db_column='TIPO_PAGO') # Añadido db_column
    class Meta:
        managed = False
        db_table = 'METODOS_DE_PAGO' 

class Servicio(models.Model): # Este es el modelo SERVICIO CORRECTO
    id_servicio = models.BigIntegerField(primary_key=True, db_column='ID_SERVICIO')
    id_proveedor_servicio = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='ID_PROVEEDOR_SERVICIO') # ¡CORREGIDO: Apunta a tu modelo Usuario!
    nombre_servicio = models.CharField(max_length=100, db_column='NOMBRE_SERVICIO') # Añadido db_column (asumo este nombre en DB)
    descripcion_servicio = models.CharField(max_length=500, blank=True, null=True, db_column='DESCRIPCION_SERVICIO') # Añadido db_column
    precio_servicio = models.DecimalField(max_digits=10, decimal_places=2, db_column='PRECIO_SERVICIO') # Añadido db_column
    duracion_minutos = models.BigIntegerField(blank=True, null=True, db_column='DURACION_MINUTOS') # Añadido db_column
    disponible = models.CharField(max_length=1, db_column='DISPONIBLE') 
    class Meta:
        managed = False
        db_table = 'SERVICIO' 

    def __str__(self):
        return self.nombre_servicio

class VentaProducto(models.Model):
    id_venta_producto = models.BigIntegerField(primary_key=True, db_column='ID_VENTA_PRODUCTO') # Añadido db_column
    id_cliente = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='ID_CLIENTE') # ¡CORREGIDO: Apunta a tu modelo Usuario!
    # El related_name se mantiene para evitar conflictos en relaciones FK con el mismo modelo.
    id_empleado = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='ID_EMPLEADO', related_name='ventaproducto_id_empleado_set', blank=True, null=True) 
    fecha_venta = models.DateField(db_column='FECHA_VENTA') # Añadido db_column
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, db_column='TOTAL_VENTA') # Añadido db_column
    id_mp = models.ForeignKey('MetodosDePago', models.DO_NOTHING, db_column='ID_MP') # 'MetodosDePago' como string es mejor aquí
    class Meta:
        managed = False
        db_table = 'VENTA_PRODUCTO'

       # MODELOS PARA SERVICIOS Y MENSAJES DEL PREPARADOR FÍSICO


class Mensaje(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    mensaje = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.correo}"