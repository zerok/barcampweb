import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from .models import Barcamp, Sponsor
from .decorators import is_organizer
from .forms import BarcampForm
from ..barcamp import forms

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
        self.data['barcamp'] = self.barcamp
        self.data['sponsors'] = self.barcamp.sponsors.order_by('-level')
        self.data['organizers'] = self.barcamp.organizers.all()
        self.data['is_organizer'] = self.request.user in self.data['organizers']
        
        
    def view(self, *args, **kwargs):
        return render_to_response('barcamp/barcamp.html', self.data, 
            context_instance=RequestContext(self.request))
            
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
        return render_to_response('barcamp/barcamp-proposals.html', self.data, 
            context_instance=RequestContext(self.request)) 

class BarcampScheduleView(BarcampView):
    def view(self, *args, **kwargs):
        self.data['events'] = self.barcamp.events.all()
        return render_to_response('barcamp/barcamp-schedule.html', self.data, 
            context_instance=RequestContext(self.request))

class BarcampVoteProposalView(BarcampView):
    @login_required
    def view(self, *args, **kwargs):
        proposal_pk = kwargs.get('proposal_pk')
        proposal = get_object_or_404(self.barcamp.talkidea_set, pk=proposal_pk)
        proposal.votes.add(self.request.user)
        return HttpResponseRedirect(reverse('barcamp-proposals', args=[self.barcamp.slug]))

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
                return HttpResponseRedirect(reverse('barcamp-proposals', args=[self.barcamp.slug]))
        else:
            form = forms.ProposalForm()
        self.data['form'] = form
        return render_to_response('barcamp/proposal-create.html', self.data, 
            context_instance=RequestContext(self.request))
            
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
                return HttpResponseRedirect(reverse('barcamp-proposals', args=[self.barcamp.slug]))
        else:
            form = forms.ProposalForm(instance=proposal)
        self.data['form'] = form
        return render_to_response('barcamp/proposal-edit.html', self.data, 
            context_instance=RequestContext(self.request))
            
class BarcampDeleteProposalView(BarcampView):
    @login_required
    def view(self, *args, **kwargs):
        proposal_pk = kwargs.get('proposal_pk')
        proposal = get_object_or_404(self.barcamp.talkidea_set, pk=proposal_pk)
        if not (self.request.user == proposal.user or self.request.user in self.barcamp.organizers.all()):
            return HttpResponseForbidden()
        if self.request.method == 'POST':
            proposal.delete()
            return HttpResponseRedirect(reverse('barcamp-proposals', args=[self.barcamp.slug]))
        self.data['proposal'] = proposal
        return render_to_response('barcamp/confirm-delete-proposal.html', self.data, 
            context_instance=RequestContext(self.request))

class BarcampUnvoteProposalView(BarcampView):
    @login_required
    def view(self, *args, **kwargs):
        proposal_pk = kwargs.get('proposal_pk')
        proposal = get_object_or_404(self.barcamp.talkidea_set, pk=proposal_pk)
        proposal.votes.remove(self.request.user)
        return HttpResponseRedirect(reverse('barcamp-proposals', args=[self.barcamp.slug]))

view_barcamp = BarcampView()
view_proposals = BarcampProposalsView()
view_schedule = BarcampScheduleView()
vote_proposal = BarcampVoteProposalView()
unvote_proposal = BarcampUnvoteProposalView()
create_proposal = BarcampCreateProposalView()
delete_proposal = BarcampDeleteProposalView()
edit_proposal = BarcampEditProposalView()

def create_barcamp(request):
    if request.method == 'POST':
        form = BarcampForm(request.POST)
        if form.is_valid():
            barcamp = form.save()
            barcamp.organizers.add(request.user)
            return HttpResponseRedirect(reverse('barcamp-view', args=[barcamp.slug]))
    else:
        form = BarcampForm()
    return render_to_response('barcamp/barcamp-create.html', {
        'form': form,
    }, context_instance=RequestContext(request))

@is_organizer(barcamp_slug_kwarg='slug')
def edit_barcamp(request, slug):
    barcamp = get_object_or_404(Barcamp, slug=slug)
    if request.method == 'POST':
        form = BarcampForm(request.POST, instance=barcamp)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('barcamp-view', args=[barcamp.slug]))
    else:
        form = BarcampForm(instance=barcamp)
    return render_to_response('barcamp/barcamp-edit.html', {
        'form': form,
        'barcamp': barcamp,
    }, context_instance=RequestContext(request))

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

@is_organizer(barcamp_slug_kwarg='slug')
def add_sponsor(request, slug):
    barcamp = get_object_or_404(Barcamp, slug=slug)
    if request.method == 'POST':
        form = forms.SponsorForm(request.POST, request.FILES)
        if form.is_valid():
            sponsor = form.save(commit=False)
            sponsor.barcamp = barcamp
            sponsor.save()
            return HttpResponseRedirect(reverse('barcamp-view', args=[barcamp.slug]))
        pass
    else:
        form = forms.SponsorForm()
    return render_to_response('barcamp/sponsor-add.html', {
        'form': form,
        'barcamp': barcamp,
    }, context_instance=RequestContext(request))
    
@is_organizer(barcamp_slug_kwarg='slug')
def remove_sponsor(request, slug, sponsoring_pk):
    sponsoring = get_object_or_404(Sponsor, pk=sponsoring_pk)
    barcamp = sponsoring.barcamp
    if request.method == 'POST':
        sponsoring.delete()
        return HttpResponseRedirect(reverse('barcamp-view', args=[barcamp.slug]))
    else:
        return render_to_response('barcamp/confirm-remove-sponsor.html', {
            'barcamp': barcamp,
            'sponsoring': sponsoring,
        }, context_instance=RequestContext(request))
        
@is_organizer(barcamp_slug_kwarg='slug')
def edit_sponsor(request, slug, sponsoring_pk):
    sponsoring = get_object_or_404(Sponsor, pk=sponsoring_pk)
    barcamp = sponsoring.barcamp
    if request.method == 'POST':
        form = forms.SponsorForm(request.POST, request.FILES, instance=sponsoring)
        if form.is_valid():
            sponsor = form.save(commit=False)
            sponsor.save()
            return HttpResponseRedirect(reverse('barcamp-view', args=[barcamp.slug]))
        pass
    else:
        form = forms.SponsorForm(instance=sponsoring)
    return render_to_response('barcamp/sponsor-edit.html', {
        'form': form,
        'barcamp': barcamp,
    }, context_instance=RequestContext(request))    