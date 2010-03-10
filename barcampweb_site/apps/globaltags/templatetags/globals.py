"""
This module contains tags and filters that are supposed to be registered
globally.
"""

from django.template import Library
from django.contrib.markup.templatetags.markup import markdown as django_markdown
register = Library()

@register.filter
def range(int_value):
    return xrange(int_value)
    
@register.filter
def markdown(value):
    return django_markdown(value, "safe")