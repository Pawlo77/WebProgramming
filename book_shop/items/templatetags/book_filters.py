from django import template

register = template.Library()


@register.filter(name="hash")
def hash(h, key):
    """Access a dictionary's value by key."""
    return h.get(key, "")
