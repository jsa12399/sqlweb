# Integracion_Proyecto/core/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings # ¡Importante: para settings.AUTH_USER_MODEL!
from django.utils import timezone

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
                # Asigna el ID 1 por defecto para el superusuario
                extra_fields['id_tipo_usuario'] = TipoUsuario.objects.get(id_tipo_usuario=1) 
            except TipoUsuario.DoesNotExist:
                raise ValueError("No se encontró un TipoUsuario con ID 1 para el superusuario. Asegúrate de que exista en tu base de datos Oracle.")
        
        if 'id_comuna' not in extra_fields:
            if not self.model._meta.get_field('id_comuna').null: # Si id_comuna no es null en el modelo
                try:
                    # Asigna la Comuna con ID 1 por defecto si no es null
                    extra_fields['id_comuna'] = Comuna.objects.get(id_comuna=1) 
                except Comuna.DoesNotExist:
                    # Este error solo se lanzará si id_comuna NO es null y el ID 1 no existe
                    raise ValueError("No se encontró una Comuna con ID 1 para el superusuario. Asegúrate de que exista en tu base de datos Oracle.")
            else:
                pass # id_comuna puede ser null, no asigna nada

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# --- CORREGIDO: MENSAJE_SERVICIO AHORA APUNTA AL MODELO DE USUARIO PERSONALIZADO ---


    class Meta:
        managed = False
        db_table = 'MENSAJE_SERVICIO'

    def __str__(self):
        return f"Mensaje de {self.cliente.email} para {self.servicio.nombre_servicio}"


# --- TU MODELO USUARIO ADAPTADO (GYMLIFEUser) ---
class Usuario(AbstractBaseUser, PermissionsMixin):
    # Usamos BigAutoField para id_usuario, asumiendo que tu secuencia en Oracle puede generar IDs grandes
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
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always for superuser
        return self.is_active and self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always for staff
        return self.is_active and self.is_staff

# --- EL RESTO DE TUS MODELOS (con ajustes para consistencia y db_column) ---

class Ciudad(models.Model):
    id_ciudad = models.BigIntegerField(primary_key=True, db_column='ID_CIUDAD')
    nombre = models.CharField(max_length=100, db_column='NOMBRE')
    class Meta:
        managed = False
        db_table = 'CIUDAD'

    def __str__(self):
        return self.nombre

class Comuna(models.Model):
    # Si id_comuna es autoincremental en Oracle y puede ser grande, usa BigAutoField
    id_comuna = models.BigIntegerField(primary_key=True, db_column='ID_COMUNA') # Añadido db_column
    nombre = models.CharField(max_length=100, db_column='NOMBRE') # Añadido db_column

    class Meta:
        managed = False
        db_table = 'COMUNA'

    def __str__(self):
        return self.nombre

class TipoUsuario(models.Model):
    # Si id_tipo_usuario es autoincremental en Oracle y puede ser grande, usa BigAutoField
    id_tipo_usuario = models.BigIntegerField(primary_key=True, db_column='ID_TIPO_USUARIO') # Añadido db_column
    tipo_usuario = models.CharField(max_length=50, db_column='TIPO_USUARIO') # Añadido db_column

    class Meta:
        managed = False
        db_table = 'TIPO_USUARIO'

    def __str__(self):
        return self.tipo_usuario

class Producto(models.Model):
    id_producto = models.BigIntegerField(primary_key=True, db_column='ID_PRODUCTO')
    nombre = models.CharField(max_length=100, db_column='NOMBRE') # Asumo 'NOMBRE' para el producto
    descripcion = models.CharField(max_length=500, blank=True, null=True, db_column='DESCRIPCION')
    stock = models.BigIntegerField(db_column='STOCK')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, db_column='PRECIO_UNITARIO')
    
    id_categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, db_column='ID_CATEGORIA', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'PRODUCTO'

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    id_categoria = models.BigIntegerField(primary_key=True, db_column='ID_CATEGORIA')
    nombre_categoria = models.CharField(max_length=100, unique=True, db_column='NOMBRE_CATEGORIA')
    class Meta:
        managed = False
        db_table = 'CATEGORIA'
    def __str__(self):
        return self.nombre_categoria


class ComentarioValoracionProducto(models.Model):
    id_comentario_valoracion = models.BigIntegerField(primary_key=True, db_column='ID_COMENTARIO_VALORACION')
    id_producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='ID_PRODUCTO')
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='ID_USUARIO') # Apunta a tu modelo Usuario
    comentario = models.CharField(max_length=500, db_column='COMENTARIO')
    valoracion = models.BigIntegerField(db_column='VALORACION')
    fecha_comentario = models.DateField(db_column='FECHA_COMENTARIO')
    class Meta:
        managed = False
        db_table = 'COMENTARIO_VALORACION_PRODUCTO'

class DetalleCompra(models.Model):
    # Asumo que ID_DETALLE_BOLETA es el PK y es BigIntegerField en Oracle
    id_detalle_boleta = models.BigIntegerField(primary_key=True, db_column='ID_DETALLE_BOLETA')
    id_venta_producto = models.ForeignKey('VentaProducto', models.DO_NOTHING, db_column='ID_VENTA_PRODUCTO')
    id_producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='ID_PRODUCTO')
    cantidad_adquirida = models.BigIntegerField(db_column='CANTIDAD_ADQUIRIDA')
    precio_venta_unitario = models.DecimalField(max_digits=10, decimal_places=2, db_column='PRECIO_VENTA_UNITARIO')
    subtotal_detalle = models.DecimalField(max_digits=10, decimal_places=2, db_column='SUBTOTAL_DETALLE')
    class Meta:
        managed = False
        db_table = 'DETALLE_COMPRA'

class DetalleServicioAdquirido(models.Model):
    # AutoField o BigAutoField si es secuencia en Oracle.
    # Si no tienes una secuencia o es un campo autoincremental de Oracle, usa BigAutoField y PrimaryKey=True.
    id_sa = models.BigAutoField(primary_key=True, db_column='ID_SA') # Asumimos este nombre de columna PK
    id_cliente = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='ID_CLIENTE')
    id_instancia_servicio = models.ForeignKey('InstanciaServicio', models.DO_NOTHING, db_column='ID_INSTANCIA_SERVICIO')
    fecha_hora_adquisicion = models.DateTimeField(db_column='FECHA_HORA_ADQUISICION', default=timezone.now) # Usa DateTimeField
    precio_pagado = models.DecimalField(max_digits=10, decimal_places=2, db_column='PRECIO_PAGADO')
    id_mp = models.ForeignKey('MetodosDePago', models.DO_NOTHING, db_column='ID_MP') # 'MetodosDePago' como string

    class Meta:
        managed = False
        db_table = 'DETALLE_SERVICIO_ADQUIRIDO'

    def __str__(self):
        return f"Servicio Adquirido por {self.id_cliente.email} - {self.id_instancia_servicio.id_servicio.nombre_servicio}"


class Envio(models.Model):
    id_envio = models.BigIntegerField(primary_key=True, db_column='ID_ENVIO')
    id_venta_producto = models.OneToOneField('VentaProducto', models.DO_NOTHING, db_column='ID_VENTA_PRODUCTO')
    fecha_envio = models.DateField(db_column='FECHA_ENVIO')
    fecha_estimada_entrega = models.DateField(blank=True, null=True, db_column='FECHA_ESTIMADA_ENTREGA')
    fecha_entrega_real = models.DateField(blank=True, null=True, db_column='FECHA_ENTREGA_REAL')
    estado_envio = models.CharField(max_length=50, db_column='ESTADO_ENVIO')
    codigo_rastreo = models.CharField(unique=True, max_length=100, blank=True, null=True, db_column='CODIGO_RASTREO')
    nombre_transportista = models.CharField(max_length=100, blank=True, null=True, db_column='NOMBRE_TRANSPORTISTA')
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, db_column='COSTO_ENVIO')
    class Meta:
        managed = False
        db_table = 'ENVIO'

class InstanciaServicio(models.Model):
    # Si tu secuencia de Oracle genera IDs grandes, BigAutoField es preferible
    id_instancia_servicio = models.BigAutoField(primary_key=True, db_column='ID_INSTANCIA_SERVICIO')
    id_servicio = models.ForeignKey('Servicio', models.DO_NOTHING, db_column='ID_SERVICIO')
    id_proveedor_servicio = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='ID_PROVEEDOR_SERVICIO', blank=True, null=True)
    fecha_hora_programada = models.DateTimeField(db_column='FECHA_HORA_PROGRAMADA') # Cambiado a DateTimeField
    reservado = models.CharField(max_length=1, db_column='RESERVADO', default='N')
    estado_instancia = models.CharField(max_length=50, db_column='ESTADO_INSTANCIA', default='Programado') # Usamos 'Programado' por defecto
    class Meta:
        managed = False
        db_table = 'INSTANCIA_SERVICIO'
    
    def __str__(self):
        return f"Instancia de {self.id_servicio.nombre_servicio} el {self.fecha_hora_programada.strftime('%Y-%m-%d %H:%M')}"

class MetodosDePago(models.Model):
    id_mp = models.BigIntegerField(primary_key=True, db_column='ID_MP')
    tipo_pago = models.CharField(max_length=50, db_column='TIPO_PAGO')
    class Meta:
        managed = False
        db_table = 'METODOS_DE_PAGO'
    def __str__(self):
        return self.tipo_pago

class Servicio(models.Model): # Este es el modelo SERVICIO CORRECTO
    id_servicio = models.BigIntegerField(primary_key=True, db_column='ID_SERVICIO')
    id_proveedor_servicio = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='ID_PROVEEDOR_SERVICIO') # Apunta a tu modelo Usuario
    nombre_servicio = models.CharField(max_length=100, db_column='NOMBRE_SERVICIO')
    descripcion_servicio = models.CharField(max_length=500, blank=True, null=True, db_column='DESCRIPCION_SERVICIO')
    precio_servicio = models.DecimalField(max_digits=10, decimal_places=2, db_column='PRECIO_SERVICIO')
    duracion_minutos = models.BigIntegerField(blank=True, null=True, db_column='DURACION_MINUTOS')
    disponible = models.CharField(max_length=1, db_column='DISPONIBLE') # 'S' o 'N'

    class Meta:
        managed = False
        db_table = 'SERVICIO'

    def __str__(self):
        return self.nombre_servicio

class VentaProducto(models.Model):
    # Asumo que ID_VENTA_PRODUCTO es el PK y es BigIntegerField en Oracle
    id_venta_producto = models.BigAutoField(primary_key=True, db_column='ID_VENTA_PRODUCTO')
    id_cliente = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='ID_CLIENTE') # Apunta a tu modelo Usuario
    # El related_name se mantiene para evitar conflictos en relaciones FK con el mismo modelo.
    id_empleado = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='ID_EMPLEADO', related_name='ventaproducto_id_empleado_set', blank=True, null=True)
    fecha_venta = models.DateTimeField(db_column='FECHA_VENTA', default=timezone.now) # Usar DateTimeField para fecha y hora
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, db_column='TOTAL_VENTA')
    id_mp = models.ForeignKey('MetodosDePago', models.DO_NOTHING, db_column='ID_MP') # 'MetodosDePago' como string

    class Meta:
        managed = False
        db_table = 'VENTA_PRODUCTO'

    def __str__(self):
        return f"Venta {self.id_venta_producto} - Total: {self.total_venta}"

# MODELOS PARA SERVICIOS Y MENSAJES DEL PREPARADOR FÍSICO (Si aplican aparte)
# El modelo Mensaje que tenías definido no parece estar mapeado a tu DB Oracle
# y no tiene db_column ni managed=False. Si esta tabla existe en Oracle,
# necesitas ajustarla de la misma manera que los otros modelos.
# Si solo es para mensajes internos de Django, puedes dejarlo así.
class Mensaje(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    mensaje = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.correo}"