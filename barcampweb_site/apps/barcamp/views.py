import datetime
import collections
import logging

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import SortedDict

from barcampweb_site.utils import render as _render

from .models import Barcamp, Sponsor, Talk
from .decorators import is_organizer
from .forms import BarcampForm
from . import forms, models, utils

APP_NAME='barcamp'
LOG = logging.getLogger(__name__)

def render(request, tmpl, vars_):
    return _render(request, tmpl, vars_, APP_NAME)

def index(request):
    barcamps = Barcamp.objects.order_by('start')
    return render(request, 'barcamp/index.html', {
        'barcamps': barcamps,
    })

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
        self.barcamp = get_object_or_404(Barcamp.objects.select_related(), slug=slug)
        self.data['barcamp'] = self.barcamp
        self.data['sponsors'] = self.barcamp.sponsors.order_by('-level')
        self.data['organizers'] = self.barcamp.organizers.all()
        self.data['is_organizer'] = self.request.user in self.data['organizers'] or self.request.user.is_staff

class BarcampView(BarcampBaseView):
    
    template_name = 'barcamp/barcamp.html'
    template_name_iphone = 'barcamp/iphone/barcamp.html'
        
    def view(self, *args, **kwargs):
        return self.render()
    
    def view_iphone(self, *args, **kwargs):
        return self.render()

class BarcampProposalsView(BarcampBaseView):
    
    template_name = 'barcamp/barcamp-proposals.html'
    
    def view(self, *args, **kwargs):
        self.data['ideas'] = self.barcamp.talkidea_set.select_related().order_by('created_at')
        votes = []
        if not self.request.user.is_anonymous():
            votes = self.request.user.voted_ideas.all()
        for idea in self.data['ideas']:
            if idea in votes:
                idea.already_voted = True
        return self.render(self.template_name) 

class BarcampScheduleView(BarcampBaseView):
    
    template_name = 'barcamp/barcamp-schedule.html'
    template_name_iphone = 'barcamp/iphone/barcamp-schedule.html'
    
    def prepare(self, *args, **kwargs):
        super(BarcampScheduleView, self).prepare(*args, **kwargs)
        self.days = utils.get_days(self.barcamp.start, self.barcamp.end)
        self.rooms = self.barcamp.places.filter(is_sessionroom=True)
        
    def view(self, *args, **kwargs):
        rooms = self.rooms
        self.dict_grid, self.open_slots = utils.create_slot_grid(self.barcamp)
        utils.mark_talkgrid_permissions(self.dict_grid, self.request.user, self.barcamp)
        slots_per_day = SortedDict() #collections.defaultdict(list)
        for slot, content in self.dict_grid.iteritems():
            if slot.start.date() not in slots_per_day:
                slots_per_day[slot.start.date()] = list()
            slots_per_day[slot.start.date()].append((slot, content))
        detached_talks = Talk.objects.filter(timeslot=None, barcamp=self.barcamp).all()
        utils.mark_talklist_permissions(detached_talks, self.request.user, self.barcamp)
        self.data['rooms'] = rooms
        self.data['slots_per_day'] = [(k, slots_per_day[k]) for  k in sorted(dict(slots_per_day).keys())]
        self.data['days'] = self.days
        self.data['detached_talks'] = detached_talks
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
        for talk in Talk.objects.filter(barcamp=self.barcamp).order_by('start'):
            days[talk.start.date()][talk.place].append(talk)
        
        self.data['talks_per_day'] = [{'day': day, 'rooms': rooms} for day, rooms in days.items()]
        return self.render()

class BarcampNowView(BarcampBaseView):
    
    template_name_iphone = 'barcamp/iphone/now.html'
    
    def view(self, *args, **kwargs):
        now = datetime.datetime.now()
        self.data['events'] = self.barcamp.events.filter(start__lte=now, end__gte=now)
        return self.render()

class BarcampUpcomingView(BarcampBaseView):
    template_name_iphone = 'barcamp/iphone/upcoming.html'
    
    def view(self, *args, **kwargs):
        now = datetime.datetime.now()
        self.data['events'] = self.barcamp.events.filter(start__gte=now)[:self.barcamp.places.count()]
        return self.render()


class BarcampVoteProposalView(BarcampBaseView):
    def view(self, *args, **kwargs):
        proposal_pk = kwargs.get('proposal_pk')
        proposal = get_object_or_404(self.barcamp.talkidea_set, pk=proposal_pk)
        if proposal.user == self.request.user:
            return HttpResponseForbidden()
        proposal.votes.add(self.request.user)
        return HttpResponseRedirect(reverse('barcamp:proposals', current_app=APP_NAME, args=[self.barcamp.slug]))

class BarcampCreateProposalView(BarcampBaseView):
    
    template_name = 'barcamp/proposal-create.html'
    
    def view(self, *args, **kwargs):
        LOG.debug("Logged in: " + str(self.request.user.is_authenticated()))
        form_cls = self.request.user.is_authenticated() and forms.ProposalForm or forms.AnonymousProposalForm
        if self.request.method == 'POST':
            form = form_cls(self.request.POST)
            if form.is_valid():
                proposal = form.save(commit=False)
                proposal.barcamp = self.barcamp
                if self.request.user.is_authenticated():
                    proposal.user = self.request.user
                proposal.save()
                return HttpResponseRedirect(reverse('barcamp:proposals', current_app=APP_NAME, args=[self.barcamp.slug]))
        else:
            form = form_cls()
        self.data['form'] = form
        return self.render(self.template_name)
            
class BarcampEditProposalView(BarcampBaseView):
    
    template_name = 'barcamp/proposal-edit.html'
    
    def view(self, *args, **kwargs):
        proposal_pk = kwargs.get('proposal_pk')
        proposal = get_object_or_404(self.barcamp.talkidea_set, pk=proposal_pk)
        if proposal.user != self.request.user or proposal.user not in self.barcamp.organizers.all():
            return HttpResponseForbidden()
        if self.request.method == 'POST':
            form = forms.ProposalForm(self.request.POST, instance=proposal)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('barcamp:proposals', args=[self.barcamp.slug]))
        else:
            form = forms.ProposalForm(instance=proposal)
        self.data['form'] = form
        return self.render(self.template_name)
            
class BarcampDeleteProposalView(BarcampBaseView):
    
    template_name = 'barcamp/confirm-delete-proposal.html'
    
    def view(self, *args, **kwargs):
        proposal_pk = kwargs.get('proposal_pk')
        proposal = get_object_or_404(self.barcamp.talkidea_set, pk=proposal_pk)
        if not (self.request.user == proposal.user or self.request.user in self.barcamp.organizers.all()):
            return HttpResponseForbidden()
        if self.request.method == 'POST':
            proposal.delete()
            return HttpResponseRedirect(reverse('barcamp:proposals', current_app=APP_NAME, args=[self.barcamp.slug]))
        self.data['proposal'] = proposal
        return self.render(self.template_name)

class BarcampUnvoteProposalView(BarcampBaseView):
    def view(self, *args, **kwargs):
        proposal_pk = kwargs.get('proposal_pk')
        proposal = get_object_or_404(self.barcamp.talkidea_set, pk=proposal_pk)
        if self.request.user == proposal.user:
            return HttpResponseForbidden()
        proposal.votes.remove(self.request.user)
        return HttpResponseRedirect(reverse('barcamp:proposals', current_app=APP_NAME, args=[self.barcamp.slug]))

class BarcampCreateSlotView(BarcampBaseView):
    template_name = 'barcamp/create-slot.html'
    def view(self, *args, **kwargs):
        if self.request.method == 'POST':
            form = forms.CreateSlotForm(self.request.POST, barcamp=self.barcamp)
            if form.is_valid():
                obj = models.TimeSlot()
                obj.barcamp = self.barcamp
                obj.start = form.get_start()
                obj.end = form.get_end()
                obj.save()
                return HttpResponseRedirect(reverse('barcamp:schedule', current_app=APP_NAME, args=[self.barcamp.slug]))
        else:
            form = forms.CreateSlotForm(barcamp=self.barcamp)
        self.data['form'] = form
        return self.render()
        
class BarcampDeleteSlotView(BarcampBaseView):

    template_name = 'barcamp/confirm-delete-slot.html'

    def view(self, *args, **kwargs):
        slot_pk = kwargs.get('slot_pk')
        slot = get_object_or_404(self.barcamp.slots, pk=slot_pk)
        if not (self.request.user in self.barcamp.organizers.all()):
            return HttpResponseForbidden()
        if self.request.method == 'POST':
            slot.talks.clear()
            slot.delete()
            return HttpResponseRedirect(reverse('barcamp:schedule', current_app=APP_NAME, args=[self.barcamp.slug]))
        self.data['slot'] = slot
        return self.render()

class BarcampCreateTalkView(BarcampBaseView):
    
    template_name = 'barcamp/create-talk-for-slot.html'
    
    def view(self, *args, **kwargs):
        slot = get_object_or_404(self.barcamp.slots, pk=kwargs['slot_pk'])
        room = get_object_or_404(self.barcamp.places, pk=kwargs['room_pk'])
        
        # Make sure, that the room is still free
        if 0 < Talk.objects.filter(place=room, timeslot=slot).count():
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
                talk.speakers.add(self.request.user)
                talk.save()
                return HttpResponseRedirect(reverse('barcamp:schedule', current_app=APP_NAME, args=[self.barcamp.slug]))
        else:
            form = forms.TalkForSlotForm()
        
        self.data.update({
            'form': form,
            'slot': slot,
            'room': room
        })
        return self.render(self.template_name)
        
class BarcampEditTalkView(BarcampBaseView):
    
    template_name = 'barcamp/edit-talk-for-slot.html'
    
    def view(self, *args, **kwargs):
        talk = get_object_or_404(Talk.objects.select_related(), pk=kwargs['talk_pk'], barcamp=self.barcamp)
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
                return HttpResponseRedirect(reverse('barcamp:schedule', args=[self.barcamp.slug], current_app=APP_NAME))
        else:
            form = forms.TalkForSlotForm(instance=talk)
        self.data.update({
            'talk': talk,
            'form': form,
        })
        return self.render(self.template_name)
        
class BarcampDeleteTalkView(BarcampBaseView):
    
    template_name = 'barcamp/confirm-delete-talk.html'
    
    def view(self, *args, **kwargs):
        talk = get_object_or_404(Talk.objects.select_related(), pk=kwargs['talk_pk'], barcamp=self.barcamp)
        if not (self.request.user.is_staff or self.request.user.is_superuser 
                or self.request.user in talk.speakers.all()
                or self.request.user in self.organizers):
            raise Http404
        if self.request.method == 'POST':
            talk.delete()
            return HttpResponseRedirect(reverse('barcamp:schedule', args=[self.barcamp.slug], current_app=APP_NAME))
        self.data['talk'] = talk
        return self.render(self.template_name)

class BarcampDetachTalkView(BarcampBaseView):
    
    template_name = 'barcamp/confirm-detach-talk.html'
    
    def view(self, *args, **kwargs):
        talk = get_object_or_404(Talk.objects.select_related(), pk=kwargs['talk_pk'], barcamp=self.barcamp)
        if not (self.request.user.is_staff or self.request.user.is_superuser 
                or self.request.user in talk.speakers.all()
                or self.request.user in self.organizers):
            raise Http404
        if self.request.method == 'POST':
            talk.timeslot=None
            talk.save()
            return HttpResponseRedirect(reverse('barcamp:schedule', args=[self.barcamp.slug], current_app=APP_NAME))
        self.data['talk'] = talk
        return self.render(self.template_name)
        
class BarcampMoveTalkView(BarcampBaseView):
    
    template_name = 'barcamp/move-talk.html'
    
    def view(self, *args, **kwargs):
        talk = get_object_or_404(Talk.objects.select_related(), pk=kwargs['talk_pk'], barcamp=self.barcamp)
        if not (self.request.user.is_staff or self.request.user.is_superuser 
                or self.request.user in talk.speakers.all()
                or self.request.user in self.organizers):
            raise Http404
        self.grid, self.open_slots = utils.create_slot_grid(self.barcamp)
        if self.request.method == 'POST':
            form = forms.MoveTalkForm(self.request.POST, instance=talk, open_slots=self.open_slots)
            if form.is_valid():
                slot = self.open_slots[form.cleaned_data['slot']]
                talk.place = slot.place
                talk.timeslot = slot.slot
                talk.save()
                return HttpResponseRedirect(reverse('barcamp:schedule', args=[self.barcamp.slug], current_app=APP_NAME))
                pass
        else:
            form = forms.MoveTalkForm(instance=talk, open_slots=self.open_slots)
        self.data.update({
            'form': form,
            'talk': talk,
        })
        return self.render(self.template_name)
    
class BarcampEventView(BarcampBaseView):
    template_name = 'barcamp/barcamp-event.html'
    
    def view(self, *args, **kwargs):
        event = get_object_or_404(models.Event.objects.select_related(), pk=kwargs['event_pk'], barcamp=self.barcamp)
        self.data['event'] = event
        return self.render()
        
        
view_barcamp = BarcampView.create_view()
view_proposals = BarcampProposalsView.create_view()
create_slot = is_organizer(BarcampCreateSlotView.create_view(), barcamp_slug_kwarg='slug')
delete_slot = is_organizer(BarcampDeleteSlotView.create_view(), barcamp_slug_kwarg='slug')
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
        form = BarcampForm(request.POST)
        if form.is_valid():
            barcamp = form.save()
            barcamp.organizers.add(request.user)
            return HttpResponseRedirect(reverse('barcamp:view', current_app=APP_NAME, args=[barcamp.slug]))
    else:
        form = BarcampForm()
    return render(request, 'barcamp/barcamp-create.html', {
        'form': form,
    })

@is_organizer(barcamp_slug_kwarg='slug')
def edit_barcamp(request, slug):
    barcamp = get_object_or_404(Barcamp, slug=slug)
    if request.method == 'POST':
        form = BarcampForm(request.POST, instance=barcamp)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('barcamp:view', current_app=APP_NAME, args=[barcamp.slug]))
    else:
        form = BarcampForm(instance=barcamp)
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
    barcamp = get_object_or_404(Barcamp, slug=slug)
    if request.method == 'POST':
        barcamp.marked_for_removal_at = datetime.datetime.now()
        barcamp.removal_requested_by = request.user
        barcamp.save()
        return HttpResponseRedirect(reverse('barcamp:view', current_app=APP_NAME, args=[barcamp.slug]))
    return render('barcamp/confirm-delete-barcamp.html', {
        'barcamp': barcamp,
    })

@is_organizer(barcamp_slug_kwarg='slug')
def undelete_barcamp(request, slug):
    barcamp = get_object_or_404(Barcamp, slug=slug)
    if request.method == 'POST':
        barcamp.marked_for_removal_at = None
        barcamp.removal_canceled_by = request.user
        barcamp.save()
        return HttpResponseRedirect(reverse('barcamp:view', current_app=APP_NAME, args=[barcamp.slug]))
    return render('barcamp/confirm-undelete-barcamp.html', {
        'barcamp': barcamp,
    })

@is_organizer(barcamp_slug_kwarg='slug')
def add_sponsor(request, slug):
    barcamp = get_object_or_404(Barcamp, slug=slug)
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
    sponsoring = get_object_or_404(Sponsor, pk=sponsoring_pk)
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
    sponsoring = get_object_or_404(Sponsor, pk=sponsoring_pk)
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
