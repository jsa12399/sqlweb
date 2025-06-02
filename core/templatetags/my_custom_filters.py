from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replaces all occurrences of a substring with another.
    Usage: {{ value|replace:"old_string,new_string" }}
    Example: {{ "Hello world"|replace:"world,Django" }} outputs "Hello Django"
    """
    if isinstance(value, str) and isinstance(arg, str) and ',' in arg:
        old_s, new_s = arg.split(',', 1)
        return value.replace(old_s, new_s)
    return value