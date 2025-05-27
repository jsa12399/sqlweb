# Integracion_Proyecto/core/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

# --- CustomUserManager para tu modelo Usuario ---
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El campo Email es obligatorio')
        email = self.normalize_email(email)
        
        # IMPORTANTE: NO PASES 'id_usuario' aquí si Oracle es quien lo genera.
        # Django debe crear una instancia sin PK inicialmente (user.pk será None).
        user = self.model(email=email, **extra_fields)
        
        user.set_password(password)
        
        # --- DEBUG: Imprime el ID antes de guardar ---
        print(f"DEBUG (create_user): id_usuario ANTES del save: {user.id_usuario}")
        
        try:
            # Este save() realizará el INSERT en Oracle.
            # Se espera que Oracle genere el ID y, si el driver lo soporta,
            # lo devuelva a Django para que user.id_usuario se actualice.
            user.save(using=self._db)
            
            # --- DEBUG: Imprime el ID después de guardar el objeto Django ---
            print(f"DEBUG (create_user): id_usuario DESPUÉS del save: {user.id_usuario}")

            # Si después de user.save(), user.id_usuario sigue siendo None,
            # significa que el ID generado por Oracle no fue devuelto a Django.
            # En este caso, lo recargaremos de la DB usando un campo único.
            if user.id_usuario is None:
                print("DEBUG (create_user): id_usuario es None después del save. Intentando recargar usuario de la DB.")
                
                # Intentar recargar por RUT primero, ya que es UNIQUE y REQUIRED_FIELDS
                if 'rut' in extra_fields and extra_fields['rut']:
                    try:
                        reloaded_user = self.get(rut=extra_fields['rut'])
                        user.id_usuario = reloaded_user.id_usuario
                        print(f"DEBUG (create_user): id_usuario recargado por RUT: {user.id_usuario}")
                    except self.model.DoesNotExist:
                        print(f"ERROR (create_user): Usuario con RUT {extra_fields['rut']} no encontrado después de la inserción. Esto es un problema grave.")
                        raise
                    except Exception as e:
                        print(f"ERROR (create_user): Falló la recarga por RUT: {e}")
                        raise
                elif user.email: # Si no hay RUT, intentar por Email (que también es UNIQUE)
                    try:
                        reloaded_user = self.get(email=user.email)
                        user.id_usuario = reloaded_user.id_usuario
                        print(f"DEBUG (create_user): id_usuario recargado por EMAIL: {user.id_usuario}")
                    except self.model.DoesNotExist:
                        print(f"ERROR (create_user): Usuario con email {user.email} no encontrado después de la inserción. Esto es un problema grave.")
                        raise
                    except Exception as e:
                        print(f"ERROR (create_user): Falló la recarga por EMAIL: {e}")
                        raise
                else:
                    print("ERROR (create_user): No hay RUT ni EMAIL válidos para recargar el usuario. La PK sigue siendo None.")
                    # Si no tienes un campo único fiable para recargar,
                    # deberás considerar el Enfoque 2 (SQL crudo con RETURNING INTO) como alternativa.
                    raise ValueError("No se pudo obtener el ID de usuario después de la inserción.")

        except Exception as e:
            # Captura cualquier error durante el proceso de guardar o recargar
            print(f"ERROR (create_user): Un error general ocurrió durante el proceso de guardado o recarga: {e}")
            raise # Re-lanzar el error para que Django lo muestre

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # Importa TipoUsuario y Comuna aquí para asegurar que estén disponibles.
        # Esto previene problemas de importación circular si se importan al inicio del archivo.
        from .models import TipoUsuario, Comuna 

        # Asigna un objeto TipoUsuario por defecto para el superusuario
        if 'id_tipo_usuario' not in extra_fields:
            try:
                extra_fields['id_tipo_usuario'] = TipoUsuario.objects.get(id_tipo_usuario=1) 
            except TipoUsuario.DoesNotExist:
                raise ValueError("No se encontró un TipoUsuario con ID 1. Asegúrate de que exista en tu base de datos Oracle.")
        
        # Asigna un objeto Comuna por defecto para el superusuario
        if 'id_comuna' not in extra_fields:
            # Solo asigna un valor por defecto si el campo NO permite nulos en el modelo Django,
            # o si deseas que el superusuario tenga una comuna por defecto incluso si es null=True.
            if not self.model._meta.get_field('id_comuna').null: 
                try:
                    extra_fields['id_comuna'] = Comuna.objects.get(id_comuna=1) 
                except Comuna.DoesNotExist:
                    raise ValueError("No se encontró una Comuna con ID 1. Asegúrate de que exista en tu base de datos Oracle.")
            else:
                pass # Si id_comuna es null=True y no se proporciona, se dejará como None

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # create_user se encarga de la inserción y la recuperación del ID
        return self.create_user(email, password, **extra_fields)

# --- TU MODELO USUARIO ADAPTADO ---
class Usuario(AbstractBaseUser, PermissionsMixin):
    # La clave primaria de tu tabla USUARIO en Oracle.
    # Con 'managed = False', Django no intentará autoincrementarla.
    # Oracle debe manejar la generación de este ID (con secuencia y trigger).
    id_usuario = models.BigIntegerField(primary_key=True, db_column='ID_USUARIO') 

    # Asegúrate de que todos los campos relevantes tengan db_column explícito
    # y que los nombres de las columnas coincidan EXACTAMENTE con tu DB Oracle (generalmente en mayúsculas).
    rut = models.CharField(unique=True, max_length=12, verbose_name=_('RUT'), db_column='RUT')
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre'), db_column='NOMBRE')
    apellido = models.CharField(max_length=100, verbose_name=_('Apellido'), db_column='APELLIDO')
    email = models.EmailField(unique=True, verbose_name=_('Email'), db_column='EMAIL')
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name=_('Teléfono'), db_column='TELEFONO')
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Dirección'), db_column='DIRECCION')

    # Foreign Keys - db_column debe coincidir con el nombre de la columna FK en tu tabla USUARIO de Oracle
    id_comuna = models.ForeignKey('Comuna', on_delete=models.SET_NULL, db_column='ID_COMUNA', null=True, blank=True, verbose_name=_('Comuna'))
    id_tipo_usuario = models.ForeignKey('TipoUsuario', on_delete=models.SET_NULL, db_column='ID_TIPO_USUARIO', null=True, blank=True, verbose_name=_('Tipo de Usuario')) 

    # CAMPOS DE AUTENTICACIÓN DE DJANGO - db_column debe coincidir con los nombres de las columnas en tu tabla USUARIO
    is_active = models.BooleanField(default=True, db_column='IS_ACTIVE')
    is_staff = models.BooleanField(default=False, db_column='IS_STAFF')
    is_superuser = models.BooleanField(default=False, db_column='IS_SUPERUSER')
    last_login = models.DateTimeField(null=True, blank=True, db_column='LAST_LOGIN')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['rut', 'nombre', 'apellido']

    class Meta:
        managed = False
        db_table = 'USUARIO' # Asegúrate del nombre exacto en mayúsculas
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
        return self.is_active and self.is_superuser # Simplificado para superusuario

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return self.is_active and self.is_staff # Simplificado para staff


# --- EL RESTO DE TUS MODELOS (¡TODOS los campos con db_column!) ---

class Ciudad(models.Model):
    id_ciudad = models.BigIntegerField(primary_key=True, db_column='ID_CIUDAD')
    nombre = models.CharField(max_length=100, db_column='NOMBRE')
    class Meta:
        managed = False
        db_table = 'CIUDAD' # Asegúrate del nombre exacto en mayúsculas

    def __str__(self):
        return self.nombre

class Comuna(models.Model):
    id_comuna = models.BigIntegerField(primary_key=True, db_column='ID_COMUNA')
    nombre = models.CharField(max_length=100, db_column='NOMBRE')
    id_ciudad = models.ForeignKey(Ciudad, models.DO_NOTHING, db_column='ID_CIUDAD') 
    class Meta:
        managed = False
        db_table = 'COMUNA' # Asegúrate del nombre exacto en mayúsculas

    def __str__(self):
        return self.nombre

class TipoUsuario(models.Model):
    id_tipo_usuario = models.BigIntegerField(primary_key=True, db_column='ID_TIPO_USUARIO')
    tipo_usuario = models.CharField(max_length=50, unique=True, db_column='TIPO_USUARIO')
    class Meta:
        managed = False
        db_table = 'TIPO_USUARIO' # Asegúrate del nombre exacto en mayúsculas

    def __str__(self):
        return self.tipo_usuario

class Producto(models.Model):
    id_producto = models.BigIntegerField(primary_key=True, db_column='ID_PRODUCTO')
    nombre_producto = models.CharField(max_length=100, db_column='NOMBRE') 
    descripcion = models.CharField(max_length=500, blank=True, null=True, db_column='DESCRIPCION')
    stock = models.BigIntegerField(db_column='STOCK')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, db_column='PRECIO_UNITARIO')
    
    id_categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, db_column='ID_CATEGORIA', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'PRODUCTO' # Asegúrate del nombre exacto en mayúsculas

    def __str__(self):
        return self.nombre_producto

class Categoria(models.Model):
    id_categoria = models.BigIntegerField(primary_key=True, db_column='ID_CATEGORIA')
    nombre_categoria = models.CharField(max_length=100, unique=True, db_column='NOMBRE_CATEGORIA')
    class Meta:
        managed = False
        db_table = 'CATEGORIA' # Asegúrate del nombre exacto en mayúsculas
    def __str__(self):
        return self.nombre_categoria


class ComentarioValoracionProducto(models.Model):
    id_comentario_valoracion = models.BigIntegerField(primary_key=True, db_column='ID_COMENTARIO_VALORACION')
    id_producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='ID_PRODUCTO')
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='ID_USUARIO')
    comentario = models.CharField(max_length=500, db_column='COMENTARIO')
    valoracion = models.BigIntegerField(db_column='VALORACION')
    fecha_comentario = models.DateField(db_column='FECHA_COMENTARIO')
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
    id_detalle_boleta = models.BigIntegerField(primary_key=True, db_column='ID_DETALLE_BOLETA') # Asumiendo que esta es tu PK simple
    id_venta_producto = models.ForeignKey('VentaProducto', models.DO_NOTHING, db_column='ID_VENTA_PRODUCTO')
    id_producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='ID_PRODUCTO')
    cantidad_adquirida = models.BigIntegerField(db_column='CANTIDAD_ADQUIRIDA')
    precio_venta_unitario = models.DecimalField(max_digits=10, decimal_places=2, db_column='PRECIO_VENTA_UNITARIO')
    subtotal_detalle = models.DecimalField(max_digits=10, decimal_places=2, db_column='SUBTOTAL_DETALLE')
    class Meta:
        managed = False
        db_table = 'DETALLE_COMPRA' # Asegúrate del nombre exacto en mayúsculas

class DetalleServicioAdquirido(models.Model):
    id_sa = models.BigIntegerField(primary_key=True, db_column='ID_SA')
    id_cliente = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='ID_CLIENTE')
    id_instancia_servicio = models.ForeignKey('InstanciaServicio', models.DO_NOTHING, db_column='ID_INSTANCIA_SERVICIO')
    fecha_hora_adquisicion = models.DateField(db_column='FECHA_HORA_ADQUISICION')
    precio_pagado = models.DecimalField(max_digits=10, decimal_places=2, db_column='PRECIO_PAGADO')
    id_mp = models.ForeignKey('MetodosDePago', models.DO_NOTHING, db_column='ID_MP')
    class Meta:
        managed = False
        db_table = 'DETALLE_SERVICIO_ADQUIRIDO' # Asegúrate del nombre exacto en mayúsculas

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
        db_table = 'ENVIO' # Asegúrate del nombre exacto en mayúsculas

class InstanciaServicio(models.Model):
    id_instancia_servicio = models.BigIntegerField(primary_key=True, db_column='ID_INSTANCIA_SERVICIO')
    id_servicio = models.ForeignKey('Servicio', models.DO_NOTHING, db_column='ID_SERVICIO')
    id_proveedor_servicio = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='ID_PROVEEDOR_SERVICIO', blank=True, null=True)
    fecha_hora_programada = models.DateField(db_column='FECHA_HORA_PROGRAMADA')
    reservado = models.CharField(max_length=1, db_column='RESERVADO')
    estado_instancia = models.CharField(max_length=50, db_column='ESTADO_INSTANCIA')
    class Meta:
        managed = False
        db_table = 'INSTANCIA_SERVICIO' # Asegúrate del nombre exacto en mayúsculas

class MetodosDePago(models.Model):
    id_mp = models.BigIntegerField(primary_key=True, db_column='ID_MP')
    tipo_pago = models.CharField(max_length=50, db_column='TIPO_PAGO')
    class Meta:
        managed = False
        db_table = 'METODOS_DE_PAGO' # Asegúrate del nombre exacto en mayúsculas

class Servicio(models.Model):
    id_servicio = models.BigIntegerField(primary_key=True, db_column='ID_SERVICIO')
    id_proveedor_servicio = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='ID_PROVEEDOR_SERVICIO')
    nombre_servicio = models.CharField(max_length=100, db_column='NOMBRE_SERVICIO')
    descripcion_servicio = models.CharField(max_length=500, blank=True, null=True, db_column='DESCRIPCION_SERVICIO')
    precio_servicio = models.DecimalField(max_digits=10, decimal_places=2, db_column='PRECIO_SERVICIO')
    duracion_minutos = models.BigIntegerField(blank=True, null=True, db_column='DURACION_MINUTOS')
    disponible = models.CharField(max_length=1, db_column='DISPONIBLE')
    class Meta:
        managed = False
        db_table = 'SERVICIO' # Asegúrate del nombre exacto en mayúsculas

class VentaProducto(models.Model):
    id_venta_producto = models.BigIntegerField(primary_key=True, db_column='ID_VENTA_PRODUCTO')
    id_cliente = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='ID_CLIENTE')
    id_empleado = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='ID_EMPLEADO', related_name='ventaproducto_id_empleado_set', blank=True, null=True)
    fecha_venta = models.DateField(db_column='FECHA_VENTA')
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, db_column='TOTAL_VENTA')
    id_mp = models.ForeignKey(MetodosDePago, models.DO_NOTHING, db_column='ID_MP')
    class Meta:
        managed = False
        db_table = 'VENTA_PRODUCTO' # Asegúrate del nombre exacto en mayúsculas