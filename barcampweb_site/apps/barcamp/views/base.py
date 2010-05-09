"""
The (mostly abstract) base views for the rest of the barcamp
app.
"""
import logging

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from barcampweb_site.utils import render as _render

from .. import models


APP_NAME = 'barcamp'
LOG = logging.getLogger(__name__)

def render(request, tmpl, vars_):
    """
    A helper for rendering templates with the current APP_NAME.
    """
    return _render(request, tmpl, vars_, APP_NAME)

class BaseView(object):
    """
    Most of the views of this application require some kind of state
    switch based on the user's platform. Since most of the other logic
    can also be clusted using a class-based approach for views should
    make that much simpler.
    """

    def __init__(self):
        self.data = {}
        self.request = None
    
    @classmethod
    def create_view(cls, *args, **kwargs):
        """
        This acts as a factor for view objects, i.e. instantiating
        one object per view call.
        """
        def _func(*request_args, **request_kwargs):
            """
            Initialize the view and execute it at request-time.
            """
            obj = cls(*args, **kwargs)
            return obj(*request_args, **request_kwargs)
        return _func
    
    def render(self, tmpl=None, data=None):
        """
        A simple render shortcut that select the view based on the
        current platform and the template vars out of self.data.
        """
        if tmpl is None:
            tmpl_name = getattr(self, 
                    'template_name_%s' % self.request.platform, 
                    getattr(self, 'template_name', None))
            tmpl = tmpl_name
            if tmpl is None:
                raise Exception, "No template available"
        if data is None:
            data = self.data
        return render(self.request, tmpl, data)

    def __call__(self, request, *args, **kwargs):
        """
        The call method dispatches to the view logic based on the
        current architecture.
        """
        self.request = request
        self.prepare(*args, **kwargs)
        # Make the distinction between platforms
        platform = getattr(request, 'platform', 'default')
        view_meth = getattr(self, 'view_%s' % platform, None)
        if view_meth is not None:
            return view_meth(*args, **kwargs)
        return self.view(*args, **kwargs)

    def prepare(self, *args, **kwargs):
        """
        Implement this method to provide logic independent of
        the used platform.
        """
        raise NotImplementedError, "Provide a prepare method"

    def view(self, *args, **kwargs):
        """
        This is the fallback view method used if no platform
        dependent logic is required.
        """
        raise NotImplementedError, "Provide a view method."

class BarcampBaseView(BaseView):
    """
    Many of the required views are directly related to a single barcamp, 
    which is fetched from the db within the prepare/load_barcamp method.
    Also offered are a few redirect helpers.
    """
    
    def __init__(self, *args, **kwargs):
        super(BarcampBaseView, self).__init__(*args, **kwargs)
        self.barcamp = None

    def prepare(self, *args, **kwargs):
        """
        Loads the current barcamp.
        """
        self.load_barcamp(kwargs.get('slug'))
    
    def load_barcamp(self, slug):
        """
        Loads the barcamp with the given slugs and prepares a handful of 
        template variables related to it.
        """
        self.barcamp = get_object_or_404(
                models.Barcamp.objects.select_related(), 
                slug=slug)
        self.data['barcamp'] = self.barcamp
        self.data['sponsors'] = self.barcamp.sponsors.order_by('-level')
        self.data['organizers'] = self.barcamp.organizers.all()
        self.data['places'] = self.barcamp.places.all()
        is_organizer = self.request.user in self.data['organizers']\
                or self.request.user.is_staff
        self.data['is_organizer'] = is_organizer

    def redirect_to_schedule(self):
        """
        Shortcut for redirecting to the schedule page of the current barcamp.
        """
        return self.redirect_to(reverse('barcamp:schedule', 
            args=[self.barcamp.slug]))

    def redirect_to(self, url=None):
        """
        A thin wrapper that first checks if the "next" request param is
        present before using the given url.
        """
        if 'next' not in self.request.REQUEST:
            return HttpResponseRedirect(url)
        return HttpResponseRedirect(self.request.REQUEST['next'])

    def view(self, *args, **kwargs):
        """
        You have to implement this method in the concrete views or
        provide implementations for all provided platforms.
        """
        raise NotImplementedError, "Provide a view method"

