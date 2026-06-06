# SadaqahEase/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def to_int(value):
    """Converts the value to integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

@register.filter
def until(value, end):
    """Generates a range from value to end (exclusive)."""
    return range(int(value), int(end))
