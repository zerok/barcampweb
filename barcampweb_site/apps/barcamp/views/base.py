import logging

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404

from barcampweb_site.utils import render as _render

from .. import models


APP_NAME='barcamp'
LOG = logging.getLogger(__name__)

def render(request, tmpl, vars_):
    return _render(request, tmpl, vars_, APP_NAME)

class BaseView(object):
    def __init__(self):
        self.data = {}
    
    @classmethod
    def create_view(cls, *args, **kwargs):
        def _func(*request_args, **request_kwargs):
            obj = cls(*args, **kwargs)
            return obj(*request_args, **request_kwargs)
        return _func
    
    def render(self, tmpl=None, data=None):
        if tmpl is None:
            tmpl_name = getattr(self, 'template_name_%s' % self.request.platform, getattr(self, 'template_name', None))
            tmpl = tmpl_name
            if tmpl is None:
                raise Exception, "No template available"
        if data is None:
            data = self.data
        return render(self.request, tmpl, data)

    def __call__(self, request, *args, **kwargs):
        self.request = request
        self.prepare(*args, **kwargs)
        # Make the distinction between platforms
        platform = getattr(request, 'platform', 'default')
        view_meth = getattr(self, 'view_%s' % platform, None)
        if view_meth is not None:
            return view_meth(*args, **kwargs)
        return self.view(*args, **kwargs)

class BarcampBaseView(BaseView):
    def prepare(self, *args, **kwargs):
        self.load_barcamp(kwargs.get('slug'))
    
    def load_barcamp(self, slug):
        self.barcamp = get_object_or_404(models.Barcamp.objects.select_related(), slug=slug)
        self.data['barcamp'] = self.barcamp
        self.data['sponsors'] = self.barcamp.sponsors.order_by('-level')
        self.data['organizers'] = self.barcamp.organizers.all()
        self.data['places'] = self.barcamp.places.all()
        self.data['is_organizer'] = self.request.user in self.data['organizers'] or self.request.user.is_staff

    def redirect_to_schedule(self):
        return self.redirect_to(reverse('barcamp:schedule', args=[self.barcamp.slug]))

    def redirect_to(self, url=None):
        if 'next' not in self.request.REQUEST:
            return HttpResponseRedirect(url)
        return HttpResponseRedirect(self.request.REQUEST['next'])


