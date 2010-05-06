import datetime
import collections
import logging

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

from ..decorators import is_organizer
from .. import forms, models, utils
from .base import BarcampBaseView, render, APP_NAME

from .proposals import *
from .schedule import *


def index(request):
    barcamps = models.Barcamp.objects.order_by('start')
    return render(request, 'barcamp/index.html', {
        'barcamps': barcamps,
    })

class BarcampView(BarcampBaseView):
    
    template_name = 'barcamp/barcamp.html'
    template_name_iphone = 'barcamp/iphone/barcamp.html'
        
    def view(self, *args, **kwargs):
        return self.render()
    
    def view_iphone(self, *args, **kwargs):
        return self.render()

class BarcampCreatePlaceView(BarcampBaseView):
    template_name = 'barcamp/create-place.html'
    
    def view(self, *args, **kwargs):
        form = forms.CreatePlaceForm()
        if self.request.method == 'POST':
            form = forms.CreatePlaceForm(self.request.POST)
            form.barcamp = self.barcamp
            if form.is_valid():
                place = form.save(commit=False)
                place.barcamp = self.barcamp
                place.save()
                return self.redirect_to_schedule()
        self.data['form'] = form
        return self.render()
        
class BarcampEditPlaceView(BarcampBaseView):
    template_name = 'barcamp/edit-place.html'
    
    def view(self, *args, **kwargs):
        place = get_object_or_404(models.Place.objects.select_related(), pk=kwargs.get('place_pk'))
        form = forms.EditPlaceForm(instance=place)
        if self.request.method == 'POST':
            form = forms.EditPlaceForm(self.request.POST, instance=place)
            if form.is_valid():
                place = form.save(commit=False)
                place.barcamp = self.barcamp
                place.save()
                return self.redirect_to_schedule()
        self.data['form'] = form
        return self.render()

class BarcampDeletePlaceView(BarcampBaseView):

    template_name = 'barcamp/confirm-delete-place.html'

    def view(self, *args, **kwargs):
        place = get_object_or_404(models.Place.objects.select_related(), pk=kwargs.get('place_pk'))
        if self.request.method == 'POST':
            # Make sure that this place has no associations
            if models.TimeSlot.objects.filter(place=place).count():
                messages.error(self.request, _("There are slots associated with this place. Please reassign them first."))
            elif models.Event.objects.filter(place=place).count():
                messages.error(self.request, _("There are events associated with this place. Please reassign them first."))
            else:
                place.delete()
            return self.redirect_to_schedule()
        self.data['place'] = place
        return self.render()

class BarcampPlaceView(BarcampBaseView):
    template_name_iphone = 'barcamp/iphone/place.html'
    def view(self, *args, **kwargs):
        place = get_object_or_404(models.Place.objects.select_related(), pk=kwargs.get('place_pk'))
        self.data['place'] = place
        return self.render()

class BarcampListPlacesView(BarcampBaseView):
    template_name_iphone = 'barcamp/iphone/places.html'

    def view(self, *args, **kwargs):
        return self.render()

class BarcampListSideEventsView(BarcampBaseView):
    template_name_iphone = 'barcamp/iphone/side-events.html'

    def view(self, *args, **kwargs):
        self.data['events'] = models.SideEvent.objects.filter(barcamp=self.barcamp).order_by('start')
        return self.render()

view_barcamp = BarcampView.create_view()
view_proposals = BarcampProposalsView.create_view()
view_place = BarcampPlaceView.create_view()
list_places = BarcampListPlacesView.create_view()
list_sideevents = BarcampListSideEventsView.create_view()
create_slot = is_organizer(BarcampCreateSlotView.create_view(), barcamp_slug_kwarg='slug')
delete_slot = is_organizer(BarcampDeleteSlotView.create_view(), barcamp_slug_kwarg='slug')
create_place = is_organizer(BarcampCreatePlaceView.create_view(), barcamp_slug_kwarg='slug')
edit_place = is_organizer(BarcampEditPlaceView.create_view(), barcamp_slug_kwarg='slug')
delete_place = is_organizer(BarcampDeletePlaceView.create_view(), barcamp_slug_kwarg='slug')
view_schedule = BarcampScheduleView.create_view()
view_now = BarcampNowView.create_view()
view_upcoming = BarcampUpcomingView.create_view()
view_event = BarcampEventView.create_view()
vote_proposal = login_required(BarcampVoteProposalView.create_view())
unvote_proposal = login_required(BarcampUnvoteProposalView.create_view())
create_proposal = BarcampCreateProposalView.create_view()
delete_proposal = login_required(BarcampDeleteProposalView.create_view())
edit_proposal = login_required(BarcampEditProposalView.create_view())
create_talk = login_required(BarcampCreateTalkView.create_view())
edit_talk = login_required(BarcampEditTalkView.create_view())
delete_talk = login_required(BarcampDeleteTalkView.create_view())
detach_talk = login_required(BarcampDetachTalkView.create_view())
move_talk = login_required(BarcampMoveTalkView.create_view())

def create_barcamp(request):
    if request.method == 'POST':
        form = forms.BarcampForm(request.POST)
        if form.is_valid():
            barcamp = form.save()
            barcamp.organizers.add(request.user)
            return HttpResponseRedirect(reverse('barcamp:view', current_app=APP_NAME, args=[barcamp.slug]))
    else:
        form = forms.BarcampForm()
    return render(request, 'barcamp/barcamp-create.html', {
        'form': form,
    })

@is_organizer(barcamp_slug_kwarg='slug')
def edit_barcamp(request, slug):
    barcamp = get_object_or_404(models.Barcamp, slug=slug)
    if request.method == 'POST':
        form = forms.BarcampForm(request.POST, instance=barcamp)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('barcamp:view', current_app=APP_NAME, args=[barcamp.slug]))
    else:
        form = forms.BarcampForm(instance=barcamp)
    return render(request, 'barcamp/barcamp-edit.html', {
        'form': form,
        'barcamp': barcamp,
    })

@is_organizer(barcamp_slug_kwarg='slug')
def delete_barcamp(request, slug):
    """
    This marks a given barcamp for removal. Once set, the barcamp will stay
    online for the next 24h. During this time an organizer or admin can cancel
    the removal.
    """
    barcamp = get_object_or_404(models.Barcamp, slug=slug)
    if request.method == 'POST':
        barcamp.marked_for_removal_at = datetime.datetime.now()
        barcamp.removal_requested_by = request.user
        barcamp.save()
        return HttpResponseRedirect(reverse('barcamp:view', current_app=APP_NAME, args=[barcamp.slug]))
    return render(request, 'barcamp/confirm-delete-barcamp.html', {
        'barcamp': barcamp,
    })

@is_organizer(barcamp_slug_kwarg='slug')
def undelete_barcamp(request, slug):
    barcamp = get_object_or_404(models.Barcamp, slug=slug)
    if request.method == 'POST':
        barcamp.marked_for_removal_at = None
        barcamp.removal_canceled_by = request.user
        barcamp.save()
        return HttpResponseRedirect(reverse('barcamp:view', current_app=APP_NAME, args=[barcamp.slug]))
    return render(request, 'barcamp/confirm-undelete-barcamp.html', {
        'barcamp': barcamp,
    })

@is_organizer(barcamp_slug_kwarg='slug')
def add_sponsor(request, slug):
    barcamp = get_object_or_404(models.Barcamp, slug=slug)
    if request.method == 'POST':
        form = forms.SponsorForm(request.POST, request.FILES)
        if form.is_valid():
            sponsor = form.save(commit=False)
            sponsor.barcamp = barcamp
            sponsor.save()
            return HttpResponseRedirect(reverse('barcamp:view', current_app=APP_NAME, args=[barcamp.slug]))
        pass
    else:
        form = forms.SponsorForm()
    return render(request, 'barcamp/sponsor-add.html', {
        'form': form,
        'barcamp': barcamp,
    })
    
@is_organizer(barcamp_slug_kwarg='slug')
def remove_sponsor(request, slug, sponsoring_pk):
    sponsoring = get_object_or_404(models.Sponsor, pk=sponsoring_pk)
    barcamp = sponsoring.barcamp
    if request.method == 'POST':
        sponsoring.delete()
        return HttpResponseRedirect(reverse('barcamp:view', current_app=APP_NAME, args=[barcamp.slug]))
    else:
        return render(request, 'barcamp/confirm-remove-sponsor.html', {
            'barcamp': barcamp,
            'sponsoring': sponsoring,
        })
        
@is_organizer(barcamp_slug_kwarg='slug')
def edit_sponsor(request, slug, sponsoring_pk):
    sponsoring = get_object_or_404(models.Sponsor, pk=sponsoring_pk)
    barcamp = sponsoring.barcamp
    if request.method == 'POST':
        form = forms.SponsorForm(request.POST, request.FILES, instance=sponsoring)
        if form.is_valid():
            sponsor = form.save(commit=False)
            sponsor.save()
            return HttpResponseRedirect(reverse('barcamp:view', current_app=APP_NAME, args=[barcamp.slug]))
        pass
    else:
        form = forms.SponsorForm(instance=sponsoring)
    return render(request, 'barcamp/sponsor-edit.html', {
        'form': form,
        'barcamp': barcamp,
    })
