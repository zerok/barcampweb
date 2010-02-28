from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden

from .models import Barcamp

def is_organizer(func=None, barcamp_pk_kwarg=None, barcamp_slug_kwarg=None):
    """
    Makes sure, that the currently logged-in user is one of the organizers
    of the requested barcamp.
    """
    def decorated(func):
        def wrapped(*args, **kwargs):
            request = args[0]
            if barcamp_pk_kwarg is not None:
                pk = kwargs.get(barcamp_pk_kwarg)
                barcamp = get_object_or_404(Barcamp, pk=pk)
            if barcamp_slug_kwarg is not None:
                barcamp = get_object_or_404(Barcamp, slug=kwargs.get(barcamp_slug_kwarg))
            if request.user not in barcamp.organizers.all():
                return HttpResponseForbidden()
            return func(*args, **kwargs)
        return wrapped
    if func is None:
        def decorator(func):
            return decorated(func)
        return decorator
    return decorated(func)