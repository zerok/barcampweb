import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from .models import Barcamp, Sponsoring
from .decorators import is_organizer

def index(request):
    barcamps = Barcamp.objects.order_by('start')
    return render_to_response('barcamp/index.html', {
        'barcamps': barcamps,
    }, context_instance=RequestContext(request))

class BarcampView(object):
    def __init__(self):
        self.data = {}
        
    def load_barcamp(self, slug):
        self.barcamp = get_object_or_404(Barcamp.objects.select_related(), slug=slug)
        self.sponsors = Sponsoring.objects.select_related().filter(barcamp=self.barcamp).order_by('-level')
        self.data['barcamp'] = self.barcamp
        self.data['sponsors'] = self.sponsors
        
    def view(self, *args, **kwargs):
        return render_to_response('barcamp/barcamp.html', self.data, 
            context_instance=RequestContext(self.request))
            
    def __call__(self, *args, **kwargs):
        self.request = args[0]
        self.load_barcamp(kwargs.get('slug'))
        return self.view(*args, **kwargs)

class BarcampProposalsView(BarcampView):
    def view(self, *args, **kwargs):
        self.data['ideas'] = self.barcamp.talkidea_set.all()
        return render_to_response('barcamp/barcamp-proposals.html', self.data, 
            context_instance=RequestContext(self.request)) 

class BarcampScheduleView(BarcampView):
    def view(self, *args, **kwargs):
        self.data['events'] = self.barcamp.events.all()
        return render_to_response('barcamp/barcamp-schedule.html', self.data, 
            context_instance=RequestContext(self.request))

view_barcamp = BarcampView()
view_proposals = BarcampProposalsView()
view_schedule = BarcampScheduleView()

def create_barcamp(request):
    """
    Every registered user should be able to create a barcamp. The creator
    also becomes part of the organization team.
    """
    pass

def edit_barcamp(request, pk):
    pass

@is_organizer(barcamp_slug_kwarg='slug')
def delete_barcamp(request, slug):
    """
    This marks a given barcamp for removal. Once set, the barcamp will stay
    online for the next 24h. During this time an organizer or admin can cancel
    the removal.
    """
    barcamp = get_object_or_404(Barcamp, slug=slug)
    if request.method == 'POST':
        barcamp.marked_for_removal_at = datetime.datetime.now()
        barcamp.removal_requested_by = request.user
        barcamp.save()
        return HttpResponseRedirect(reverse('barcamp-view', args=[barcamp.slug]))
    return render_to_response('barcamp/confirm-delete-barcamp.html', {
        'barcamp': barcamp,
    }, context_instance=RequestContext(request))

@is_organizer(barcamp_slug_kwarg='slug')
def undelete_barcamp(request, slug):
    barcamp = get_object_or_404(Barcamp, slug=slug)
    if request.method == 'POST':
        barcamp.marked_for_removal_at = None
        barcamp.removal_canceled_by = request.user
        barcamp.save()
        return HttpResponseRedirect(reverse('barcamp-view', args=[barcamp.slug]))
    return render_to_response('barcamp/confirm-undelete-barcamp.html', {
        'barcamp': barcamp,
    }, context_instance=RequestContext(request))