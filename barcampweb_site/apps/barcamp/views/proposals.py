"""
Proposal related views.
"""
import logging

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from .base import BarcampBaseView, APP_NAME
from .. import forms


LOG = logging.getLogger(__name__)

class BarcampProposalsView(BarcampBaseView):
    """List all session proposals."""
    
    template_name = 'barcamp/barcamp-proposals.html'
    
    def view(self, *args, **kwargs):
        self.data['ideas'] = self.barcamp.talkidea_set.select_related()\
                .order_by('created_at')
        votes = []
        if not self.request.user.is_anonymous():
            votes = self.request.user.voted_ideas.all()
        for idea in self.data['ideas']:
            if idea in votes:
                idea.already_voted = True
        return self.render(self.template_name) 

class BarcampVoteProposalView(BarcampBaseView):
    """Vote for a proposal"""
    def view(self, *args, **kwargs):
        proposal_pk = kwargs.get('proposal_pk')
        proposal = get_object_or_404(self.barcamp.talkidea_set, pk=proposal_pk)
        if proposal.user == self.request.user:
            return HttpResponseForbidden()
        proposal.votes.add(self.request.user)
        return HttpResponseRedirect(reverse('barcamp:proposals', 
            current_app=APP_NAME, args=[self.barcamp.slug]))

class BarcampCreateProposalView(BarcampBaseView):
    """Create a proposal. Every user should be able to create
    session proposals."""
    
    template_name = 'barcamp/proposal-create.html'
    
    def view(self, *args, **kwargs):
        LOG.debug("Logged in: " + str(self.request.user.is_authenticated()))
        form_cls = self.request.user.is_authenticated() and forms.ProposalForm\
                or forms.AnonymousProposalForm
        if self.request.method == 'POST':
            form = form_cls(self.request.POST)
            if form.is_valid():
                proposal = form.save(commit=False)
                proposal.barcamp = self.barcamp
                if self.request.user.is_authenticated():
                    proposal.user = self.request.user
                proposal.save()
                return HttpResponseRedirect(reverse('barcamp:proposals', 
                    current_app=APP_NAME, args=[self.barcamp.slug]))
        else:
            form = form_cls()
        self.data['form'] = form
        return self.render(self.template_name)
            
class BarcampEditProposalView(BarcampBaseView):
    """Authors and organizers should be able to edit proposals."""
    
    template_name = 'barcamp/proposal-edit.html'
    
    def view(self, *args, **kwargs):
        proposal_pk = kwargs.get('proposal_pk')
        proposal = get_object_or_404(self.barcamp.talkidea_set, pk=proposal_pk)
        if proposal.user != self.request.user\
                and proposal.user not in self.barcamp.organizers.all():
            return HttpResponseForbidden()
        if self.request.method == 'POST':
            form = forms.ProposalForm(self.request.POST, instance=proposal)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('barcamp:proposals',
                    args=[self.barcamp.slug]))
        else:
            form = forms.ProposalForm(instance=proposal)
        self.data['form'] = form
        return self.render(self.template_name)
            
class BarcampDeleteProposalView(BarcampBaseView):
    """Authors and organizers should be able to delete proposals."""
    
    template_name = 'barcamp/confirm-delete-proposal.html'
    
    def view(self, *args, **kwargs):
        proposal_pk = kwargs.get('proposal_pk')
        proposal = get_object_or_404(self.barcamp.talkidea_set, pk=proposal_pk)
        if not (self.request.user == proposal.user\
                or self.request.user in self.barcamp.organizers.all()):
            return HttpResponseForbidden()
        if self.request.method == 'POST':
            proposal.delete()
            return HttpResponseRedirect(reverse('barcamp:proposals', 
                current_app=APP_NAME, args=[self.barcamp.slug]))
        self.data['proposal'] = proposal
        return self.render(self.template_name)

class BarcampUnvoteProposalView(BarcampBaseView):
    """Users should be able to undo votes."""

    def view(self, *args, **kwargs):
        proposal_pk = kwargs.get('proposal_pk')
        proposal = get_object_or_404(self.barcamp.talkidea_set, pk=proposal_pk)
        if self.request.user == proposal.user:
            return HttpResponseForbidden()
        proposal.votes.remove(self.request.user)
        return HttpResponseRedirect(reverse('barcamp:proposals', 
            current_app=APP_NAME, args=[self.barcamp.slug]))

