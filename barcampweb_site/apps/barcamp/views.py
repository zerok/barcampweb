import datetime
import collections

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import SortedDict

from .models import Barcamp, Sponsor, Talk
from .decorators import is_organizer
from .forms import BarcampForm
from . import forms
from . import utils

APP_NAME='barcamp'

def render(request, tmpl, vars_):
    ctx = RequestContext(request, current_app=APP_NAME)
    return render_to_response(tmpl, vars_, context_instance=ctx)

def index(request):
    barcamps = Barcamp.objects.order_by('start')
    return render(request, 'barcamp/index.html', {
        'barcamps': barcamps,
    })

class BarcampView(object):
    def __init__(self):
        self.data = {}
        
    def load_barcamp(self, slug):
        self.barcamp = get_object_or_404(Barcamp.objects.select_related(), slug=slug)
        self.data['barcamp'] = self.barcamp
        self.data['sponsors'] = self.barcamp.sponsors.order_by('-level')
        self.data['organizers'] = self.barcamp.organizers.all()
        self.data['is_organizer'] = self.request.user in self.data['organizers']
        
    def render(self, tmpl, data=None):
        if data is None:
            data = self.data
        return render(self.request, tmpl, data)
        
    def view(self, *args, **kwargs):
        return self.render('barcamp/barcamp.html')
            
    def __call__(self, *args, **kwargs):
        self.request = args[0]
        self.load_barcamp(kwargs.get('slug'))
        return self.view(*args, **kwargs)

class BarcampProposalsView(BarcampView):
    def view(self, *args, **kwargs):
        self.data['ideas'] = self.barcamp.talkidea_set.select_related().order_by('created_at')
        votes = []
        if not self.request.user.is_anonymous():
            votes = self.request.user.voted_ideas.all()
        for idea in self.data['ideas']:
            if idea in votes:
                idea.already_voted = True
        return self.render('barcamp/barcamp-proposals.html') 

class BarcampScheduleView(BarcampView):
    def view(self, *args, **kwargs):
        rooms = self.barcamp.places.filter(is_sessionroom=True)
        self.grid, self.open_slots = utils.create_slot_grid(self.barcamp)
        utils.mark_talkgrid_permissions(self.grid, self.request.user, self.barcamp)
        slots_per_day = SortedDict() #collections.defaultdict(list)
        for slot, content in self.grid.iteritems():
            if slot.start.date() not in slots_per_day:
                slots_per_day[slot.start.date()] = list()
            slots_per_day[slot.start.date()].append((slot, content))
        detached_talks = Talk.objects.filter(timeslot=None, barcamp=self.barcamp).all()
        utils.mark_talklist_permissions(detached_talks, self.request.user, self.barcamp)
        self.data['rooms'] = rooms
        self.data['slots_per_day'] = dict(slots_per_day)
        self.data['days'] = utils.get_days(self.barcamp.start, self.barcamp.end)
        self.data['detached_talks'] = detached_talks
        return self.render('barcamp/barcamp-schedule.html')

class BarcampVoteProposalView(BarcampView):
    @login_required
    def view(self, *args, **kwargs):
        proposal_pk = kwargs.get('proposal_pk')
        proposal = get_object_or_404(self.barcamp.talkidea_set, pk=proposal_pk)
        if proposal.user == self.request.user:
            return HttpResponseForbidden()
        proposal.votes.add(self.request.user)
        return HttpResponseRedirect(reverse('barcamp:proposals', current_app=APP_NAME, args=[self.barcamp.slug]))

class BarcampCreateProposalView(BarcampView):
    @login_required
    def view(self, *args, **kwargs):
        if self.request.method == 'POST':
            form = forms.ProposalForm(self.request.POST)
            if form.is_valid():
                proposal = form.save(commit=False)
                proposal.barcamp = self.barcamp
                proposal.user = self.request.user
                proposal.save()
                return HttpResponseRedirect(reverse('barcamp:proposals', current_app=APP_NAME, args=[self.barcamp.slug]))
        else:
            form = forms.ProposalForm()
        self.data['form'] = form
        return self.render('barcamp/proposal-create.html')
            
class BarcampEditProposalView(BarcampView):
    @login_required
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
        return self.render('barcamp/proposal-edit.html')
            
class BarcampDeleteProposalView(BarcampView):
    @login_required
    def view(self, *args, **kwargs):
        proposal_pk = kwargs.get('proposal_pk')
        proposal = get_object_or_404(self.barcamp.talkidea_set, pk=proposal_pk)
        if not (self.request.user == proposal.user or self.request.user in self.barcamp.organizers.all()):
            return HttpResponseForbidden()
        if self.request.method == 'POST':
            proposal.delete()
            return HttpResponseRedirect(reverse('barcamp:proposals', current_app=APP_NAME, args=[self.barcamp.slug]))
        self.data['proposal'] = proposal
        return self.render('barcamp/confirm-delete-proposal.html')

class BarcampUnvoteProposalView(BarcampView):
    @login_required
    def view(self, *args, **kwargs):
        proposal_pk = kwargs.get('proposal_pk')
        proposal = get_object_or_404(self.barcamp.talkidea_set, pk=proposal_pk)
        if self.request.user == proposal.user:
            return HttpResponseForbidden()
        proposal.votes.remove(self.request.user)
        return HttpResponseRedirect(reverse('barcamp:proposals', current_app=APP_NAME, args=[self.barcamp.slug]))

class BarcampCreateTalkView(BarcampView):
    @login_required
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
        return self.render('barcamp/create-talk-for-slot.html')
        
class BarcampEditTalkView(BarcampView):
    @login_required
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
        return self.render('barcamp/edit-talk-for-slot.html')
        
class BarcampDeleteTalkView(BarcampView):
    @login_required
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
        return self.render('barcamp/confirm-delete-talk.html')

class BarcampDetachTalkView(BarcampView):
    @login_required
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
        return self.render('barcamp/confirm-detach-talk.html')
        
class BarcampMoveTalkView(BarcampView):
    @login_required
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
        return self.render('barcamp/move-talk.html')
        
        
view_barcamp = BarcampView()
view_proposals = BarcampProposalsView()
view_schedule = BarcampScheduleView()
vote_proposal = BarcampVoteProposalView()
unvote_proposal = BarcampUnvoteProposalView()
create_proposal = BarcampCreateProposalView()
delete_proposal = BarcampDeleteProposalView()
edit_proposal = BarcampEditProposalView()
create_talk = BarcampCreateTalkView()
edit_talk = BarcampEditTalkView()
delete_talk = BarcampDeleteTalkView()
detach_talk = BarcampDetachTalkView()
move_talk = BarcampMoveTalkView()

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
