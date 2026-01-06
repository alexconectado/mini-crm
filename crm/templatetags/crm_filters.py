from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Template filter para acessar items de dicionário."""
    if dictionary is None:
        return []
    result = dictionary.get(key)
    return result if result is not None else []
