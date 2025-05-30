# core/templatetags/user_tags.py

from django import template

register = template.Library()

@register.filter(name='is_administrador')
def is_administrador(user):
    """
    Verifica si el usuario es de tipo 'Administrador'.
    Asume que id_tipo_usuario para Administrador es 1.
    """
    if user.is_authenticated:
        try:
            return user.id_tipo_usuario.id_tipo_usuario == 1
        except AttributeError:
            return False
    return False

@register.filter(name='is_nutricionista')
def is_nutricionista(user):
    """
    Verifica si el usuario es de tipo 'Nutricionista'.
    Asume que id_tipo_usuario para Nutricionista es 2.
    """
    if user.is_authenticated:
        try:
            return user.id_tipo_usuario.id_tipo_usuario == 2
        except AttributeError:
            return False
    return False

@register.filter(name='is_preparador_fisico')
def is_preparador_fisico(user):
    """
    Verifica si el usuario es de tipo 'Preparador Físico'.
    Asume que id_tipo_usuario para Preparador Físico es 3.
    """
    if user.is_authenticated:
        try:
            return user.id_tipo_usuario.id_tipo_usuario == 3
        except AttributeError:
            return False
    return False

@register.filter(name='is_cliente')
def is_cliente(user):
    """
    Verifica si el usuario es de tipo 'Cliente'.
    Asume que id_tipo_usuario para Cliente es 4.
    """
    if user.is_authenticated:
        try:
            return user.id_tipo_usuario.id_tipo_usuario == 4
        except AttributeError:
            return False
    return False