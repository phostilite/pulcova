from django import template

register = template.Library()

@register.filter
def lookup(d, key):
    """
    Template filter to lookup dictionary values by key.
    Usage: {{ dict|lookup:key }}
    """
    if isinstance(d, dict):
        return d.get(key, '')
    return ''

@register.filter
def replace(value, arg):
    """
    Template filter to replace characters in a string.
    Usage: {{ value|replace:"_,space" }}
    """
    if not isinstance(value, str):
        return value
    
    old, new = arg.split(',', 1) if ',' in arg else (arg, '')
    return value.replace(old, new)