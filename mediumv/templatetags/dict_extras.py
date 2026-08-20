
from django import template
register = template.Library()

@register.filter
def get_item(d, key):
    """Return a dict item by key prefix (used with add in template)."""
    return d.get(key)
