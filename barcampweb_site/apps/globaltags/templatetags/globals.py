"""
This module contains tags and filters that are supposed to be registered
globally.
"""

from django.template import Library

register = Library()

@register.filter
def range(int_value):
    return xrange(int_value)