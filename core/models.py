# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Ciudad(models.Model):
    id_ciudad = models.BigIntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'ciudad'


class ComentarioValoracionProducto(models.Model):
    id_comentario_valoracion = models.BigIntegerField(primary_key=True)
    id_producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='id_producto')
    id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario')
    comentario = models.CharField(max_length=500)
    valoracion = models.BigIntegerField()
    fecha_comentario = models.DateField()

    class Meta:
        managed = False
        db_table = 'comentario_valoracion_producto'


class Comuna(models.Model):
    id_comuna = models.BigIntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    id_ciudad = models.ForeignKey(Ciudad, models.DO_NOTHING, db_column='id_ciudad')

    class Meta:
        managed = False
        db_table = 'comuna'


class DetalleCompra(models.Model):
    pk = models.CompositePrimaryKey('id_detalle_boleta', 'id_venta_producto')
    id_detalle_boleta = models.BigIntegerField()
    id_venta_producto = models.ForeignKey('VentaProducto', models.DO_NOTHING, db_column='id_venta_producto')
    id_producto = models.ForeignKey('Producto', models.DO_NOTHING, db_column='id_producto')
    cantidad_adquirida = models.BigIntegerField()
    precio_venta_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal_detalle = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'detalle_compra'


class DetalleServicioAdquirido(models.Model):
    id_sa = models.BigIntegerField(primary_key=True)
    id_cliente = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_cliente')
    id_instancia_servicio = models.ForeignKey('InstanciaServicio', models.DO_NOTHING, db_column='id_instancia_servicio')
    fecha_hora_adquisicion = models.DateField()
    precio_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    id_mp = models.ForeignKey('MetodosDePago', models.DO_NOTHING, db_column='id_mp')

    class Meta:
        managed = False
        db_table = 'detalle_servicio_adquirido'


class Envio(models.Model):
    id_envio = models.BigIntegerField(primary_key=True)
    id_venta_producto = models.OneToOneField('VentaProducto', models.DO_NOTHING, db_column='id_venta_producto')
    fecha_envio = models.DateField()
    fecha_estimada_entrega = models.DateField(blank=True, null=True)
    fecha_entrega_real = models.DateField(blank=True, null=True)
    estado_envio = models.CharField(max_length=50)
    codigo_rastreo = models.CharField(unique=True, max_length=100, blank=True, null=True)
    nombre_transportista = models.CharField(max_length=100, blank=True, null=True)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'envio'


class InstanciaServicio(models.Model):
    id_instancia_servicio = models.BigIntegerField(primary_key=True)
    id_servicio = models.ForeignKey('Servicio', models.DO_NOTHING, db_column='id_servicio')
    id_proveedor_servicio = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_proveedor_servicio', blank=True, null=True)
    fecha_hora_programada = models.DateField()
    reservado = models.CharField(max_length=1)
    estado_instancia = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'instancia_servicio'


class MetodosDePago(models.Model):
    id_mp = models.BigIntegerField(primary_key=True)
    tipo_pago = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'metodos_de_pago'


class Producto(models.Model):
    id_producto = models.BigIntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=500, blank=True, null=True)
    stock = models.BigIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'producto'


class Servicio(models.Model):
    id_servicio = models.BigIntegerField(primary_key=True)
    id_proveedor_servicio = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_proveedor_servicio', to_field='rut')
    nombre_servicio = models.CharField(max_length=100)
    descripcion_servicio = models.CharField(max_length=500, blank=True, null=True)
    precio_servicio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_minutos = models.BigIntegerField(blank=True, null=True)
    disponible = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'servicio'


class TipoUsuario(models.Model):
    id_tipo_usuario = models.BigIntegerField(primary_key=True)
    tipo_usuario = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'tipo_usuario'


class Usuario(models.Model):
    id_usuario = models.BigIntegerField(primary_key=True)
    rut = models.CharField(unique=True, max_length=20)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    id_comuna = models.ForeignKey(Comuna, models.DO_NOTHING, db_column='id_comuna', blank=True, null=True)
    id_tipo_usuario = models.ForeignKey(TipoUsuario, models.DO_NOTHING, db_column='id_tipo_usuario')

    class Meta:
        managed = False
        db_table = 'usuario'


class VentaProducto(models.Model):
    id_venta_producto = models.BigIntegerField(primary_key=True)
    id_cliente = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_cliente')
    id_empleado = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_empleado', related_name='ventaproducto_id_empleado_set', blank=True, null=True)
    fecha_venta = models.DateField()
    total_venta = models.DecimalField(max_digits=10, decimal_places=2)
    id_mp = models.ForeignKey(MetodosDePago, models.DO_NOTHING, db_column='id_mp')

    class Meta:
        managed = False
        db_table = 'venta_producto'
