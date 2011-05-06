"""
Collection of views related to how talks and events in general are scheduled
on barcamps.
"""
import datetime
import collections
import logging

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404

from .. import forms, models, utils
from .base import BarcampBaseView, APP_NAME


LOG = logging.getLogger(__name__)

class BarcampScheduleView(BarcampBaseView):
    """
    The schedule view presents all the talks and side events of the
    barcamp. The normal web version renders a grid with slots and
    places (i.e. rooms) as dimensions while the iphone version just
    provides a simple listening per day and room.
    """
    
    template_name = 'barcamp/barcamp-schedule.html'
    template_name_iphone = 'barcamp/iphone/barcamp-schedule.html'

    def __init__(self, *args, **kwargs):
        super(BarcampScheduleView, self).__init__(*args, **kwargs)
        self.dict_grid = None
        self.open_slots = None
        self.days = None
        self.rooms = None
    
    def prepare(self, *args, **kwargs):
        super(BarcampScheduleView, self).prepare(*args, **kwargs)
        self.days = utils.get_days(self.barcamp.start, self.barcamp.end)
        self.rooms = self.barcamp.places.filter(is_sessionroom=True)
        
    def view(self, *args, **kwargs):
        """Provide a full grid of talks as well as the side events."""
        rooms = self.rooms
        detached_talks = models.Talk.objects.filter(timeslot=None, 
                barcamp=self.barcamp).all()
        sideevents = models.SideEvent.objects.filter(barcamp=self.barcamp)\
                .order_by('start')
        se_per_day = collections.defaultdict(list)
        for event in sideevents:
            se_per_day[event.start.date()].append(event)
        utils.mark_talklist_permissions(detached_talks, self.request.user, 
                self.barcamp)
        self.data['detached_talks'] = detached_talks
        self.data['sideevents'] = [
                (k, se_per_day[k]) for k in sorted(se_per_day.keys())
                ]
        self.data['grid'] = utils.SlotGrid.create_from_barcamp(self.barcamp,
                list(rooms), per_day=True, mark_for_user=self.request.user)[0]
        return self.render()
    
    def view_iphone(self, *args, **kwargs):
        """
        Here we only require a simple list of talks per room per day
        """
        days = {}
        for day in self.days:
            days[day.date()] = {}
            for room in self.rooms:
                days[day.date()][room] = []
        self.data['days'] = self.days
        for talk in models.Talk.objects.filter(barcamp=self.barcamp)\
                .order_by('start'):
            days[talk.start.date()][talk.place].append(talk)
        
        self.data['talks_per_day'] = [
                {'day': day, 'rooms': rooms} for day, rooms in days.items()
                ]
        return self.render()


class BarcampNowView(BarcampBaseView):
    """
    For the iPhone version this provides a simple listing of all
    the currently active events.
    """
    
    template_name_iphone = 'barcamp/iphone/now.html'
    
    def view(self, *args, **kwargs):
        now = datetime.datetime.now()
        self.data['events'] = self.barcamp.events.filter(start__lte=now,
                end__gte=now)
        return self.render()

class BarcampUpcomingView(BarcampBaseView):
    """
    Again for the iPhone version this provides a list of the upcoming
    events. The number of listed events is based on the number of available
    places.
    """

    template_name_iphone = 'barcamp/iphone/upcoming.html'
    
    def view(self, *args, **kwargs):
        now = datetime.datetime.now()
        self.data['events'] = self.barcamp.events.filter(start__gte=now)\
            .order_by('start')[:self.barcamp.places.count()]
        return self.render()

class BarcampCreateSlotView(BarcampBaseView):
    """
    Organizers can create a timeslot for one of the days of the barcamp
    with this view.
    """

    template_name = 'barcamp/create-slot.html'
    def view(self, *args, **kwargs):
        if self.request.method == 'POST':
            form = forms.CreateSlotForm(self.request.POST, 
                    barcamp=self.barcamp)
            if form.is_valid():
                obj = models.TimeSlot()
                obj.barcamp = self.barcamp
                obj.start = form.get_start()
                obj.end = form.get_end()
                if form.cleaned_data['room'] != u'0':
                    obj.place = self.barcamp.places.get(
                            pk=form.cleaned_data['room'])
                obj.save()
                return HttpResponseRedirect(reverse('barcamp:schedule', 
                    current_app=APP_NAME, args=[self.barcamp.slug]))
        else:
            form = forms.CreateSlotForm(barcamp=self.barcamp)
        self.data['form'] = form
        return self.render()
        
class BarcampDeleteSlotView(BarcampBaseView):
    """
    Allows organizers to delete a given slot.
    """

    template_name = 'barcamp/confirm-delete-slot.html'

    def view(self, *args, **kwargs):
        slot_pk = kwargs.get('slot_pk')
        slot = get_object_or_404(self.barcamp.slots, pk=slot_pk)
        if self.request.method == 'POST':
            slot.talks.clear()
            slot.delete()
            return HttpResponseRedirect(reverse('barcamp:schedule', 
                current_app=APP_NAME, args=[self.barcamp.slug]))
        self.data['slot'] = slot
        return self.render()

class BarcampCreateTalkView(BarcampBaseView):
    """
    Create a talk within a given slot.
    """
    
    template_name = 'barcamp/create-talk-for-slot.html'
    
    def view(self, *args, **kwargs):
        slot = get_object_or_404(self.barcamp.slots.select_related(), 
                pk=kwargs['slot_pk'])
        room = get_object_or_404(self.barcamp.places, pk=kwargs['room_pk'])
        
        # Make sure, that the room is still free
        if 0 < models.Talk.objects.filter(place=room, timeslot=slot).count():
            return render_to_response('barcamp/slot-taken.html', self.data,
                context_instance=RequestContext(self.request))
                
        if self.request.method == 'POST':
            form = forms.TalkForSlotForm(self.request.POST)
            form.barcamp = self.barcamp
            form.timeslot = slot
            form.room = room
            if form.is_valid():
                talk = form.save(commit=False)
                talk.barcamp = self.barcamp
                talk.timeslot = slot
                talk.place = room
                talk.start = slot.start
                talk.end = slot.end
                talk.save()
                return HttpResponseRedirect(reverse('barcamp:schedule', 
                    current_app=APP_NAME, args=[self.barcamp.slug]))
        else:
            form = forms.TalkForSlotForm()
        
        self.data.update({
            'form': form,
            'slot': slot,
            'room': room
        })
        return self.render(self.template_name)
        
class BarcampEditTalkView(BarcampBaseView):
    """
    Edit a talk without changing its slot, start and end time.
    """
    
    template_name = 'barcamp/edit-talk-for-slot.html'
    
    def view(self, *args, **kwargs):
        talk = get_object_or_404(models.Talk.objects.select_related(), 
                pk=kwargs['talk_pk'], barcamp=self.barcamp)
        if not (self.request.user.is_staff or self.request.user.is_superuser 
                or self.request.user in talk.speakers.all()
                or self.request.user in self.organizers):
            raise Http404
        if self.request.method == 'POST':
            form = forms.TalkForSlotForm(self.request.POST, instance=talk)
            form.barcamp = self.barcamp
            form.timeslot = talk.timeslot
            form.room = talk.place
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('barcamp:schedule', 
                    args=[self.barcamp.slug], current_app=APP_NAME))
        else:
            form = forms.TalkForSlotForm(instance=talk)
        self.data.update({
            'talk': talk,
            'form': form,
        })
        return self.render(self.template_name)
        
class BarcampDeleteTalkView(BarcampBaseView):
    """
    Delete a talk.
    """
    
    template_name = 'barcamp/confirm-delete-talk.html'
    
    def view(self, *args, **kwargs):
        talk = get_object_or_404(models.Talk.objects.select_related(), 
                pk=kwargs['talk_pk'], barcamp=self.barcamp)
        if not (self.request.user.is_staff or self.request.user.is_superuser 
                or self.request.user in talk.speakers.all()
                or self.request.user in self.organizers):
            raise Http404
        if self.request.method == 'POST':
            talk.delete()
            return HttpResponseRedirect(reverse('barcamp:schedule', 
                args=[self.barcamp.slug], current_app=APP_NAME))
        self.data['talk'] = talk
        return self.render(self.template_name)

class BarcampDetachTalkView(BarcampBaseView):
    """
    Detach a talk from its timeslot.
    """
    
    template_name = 'barcamp/confirm-detach-talk.html'
    
    def view(self, *args, **kwargs):
        talk = get_object_or_404(models.Talk.objects.select_related(), 
                pk=kwargs['talk_pk'], barcamp=self.barcamp)
        if not (self.request.user.is_staff or self.request.user.is_superuser 
                or self.request.user in talk.speakers.all()
                or self.request.user in self.organizers):
            raise Http404
        if self.request.method == 'POST':
            talk.timeslot = None
            talk.save()
            return HttpResponseRedirect(reverse('barcamp:schedule', 
                args=[self.barcamp.slug], current_app=APP_NAME))
        self.data['talk'] = talk
        return self.render(self.template_name)
        
class BarcampMoveTalkView(BarcampBaseView):
    """
    Move talks between (available) timeslots.
    """
    
    template_name = 'barcamp/move-talk.html'
    
    def view(self, *args, **kwargs):
        talk = get_object_or_404(models.Talk.objects.select_related(), 
                pk=kwargs['talk_pk'], barcamp=self.barcamp)
        if not (self.request.user.is_staff or self.request.user.is_superuser 
                or self.request.user in talk.speakers.all()
                or self.request.user in self.organizers):
            raise Http404
        open_slots = utils.SlotGrid.create_from_barcamp(
                self.barcamp)[1]
        if self.request.method == 'POST':
            form = forms.MoveTalkForm(self.request.POST, instance=talk, 
                    open_slots=open_slots)
            if form.is_valid():
                slot = form.open_slots[form.cleaned_data['slot']]
                talk.place = slot.place
                talk.timeslot = slot.slot
                talk.start = slot.slot.start
                talk.end = slot.slot.end
                talk.save()
                return HttpResponseRedirect(reverse('barcamp:schedule', 
                    args=[self.barcamp.slug], current_app=APP_NAME))
        else:
            form = forms.MoveTalkForm(instance=talk, 
                    open_slots=open_slots)
        self.data.update({
            'form': form,
            'talk': talk,
        })
        return self.render(self.template_name)
    
class BarcampEventView(BarcampBaseView):
    """Show the details of a single event."""

    template_name = 'barcamp/barcamp-event.html'
    template_name_iphone = 'barcamp/iphone/barcamp-event.html'
    
    def view(self, *args, **kwargs):
        event = get_object_or_404(models.Event.objects.select_related(), 
                pk=kwargs['event_pk'], barcamp=self.barcamp)
        self.data['event'] = event
        return self.render()

class BarcampCreateSideEventView(BarcampBaseView):
    """Create a side event."""

    template_name = 'barcamp/create-sideevent.html'

    def view(self, *args, **kwargs):
        form = forms.CreateSideEventForm(barcamp=self.barcamp)
        if self.request.method == 'POST':
            form = forms.CreateSideEventForm(self.request.POST, barcamp=self.barcamp)
            if form.is_valid():
                event = form.save(commit=False)
                event.barcamp = self.barcamp
                event.save()
                return self.redirect_to_schedule()
        self.data['form'] = form
        return self.render()

class BarcampEditSideEventView(BarcampBaseView):
    """Edit the details of a side event."""

    template_name = 'barcamp/edit-sideevent.html'

    def view(self, *args, **kwargs):
        event = get_object_or_404(models.SideEvent.objects.filter(
            barcamp=self.barcamp, pk=kwargs['event_pk']))
        form = forms.CreateSideEventForm(instance=event)
        if self.request.method == 'POST':
            form = forms.CreateSideEventForm(self.request.POST, instance=event)
            form.barcamp = self.barcamp
            if form.is_valid():
                event = form.save(commit=False)
                event.barcamp = self.barcamp
                event.save()
                return self.redirect_to_schedule()
        self.data['form'] = form
        return self.render()

class BarcampDeleteSideEventView(BarcampDeleteTalkView):
    """Delete a side event."""

    def view(self, *args, **kwargs):
        event = get_object_or_404(models.SideEvent.objects.filter(
            barcamp=self.barcamp, pk=kwargs['event_pk']))
        if self.request.method == 'POST':
            event.delete()
            return self.redirect_to_schedule()
        self.data['event'] = event
        return self.render()

