from django.forms.models import ModelForm
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Barcamp, Sponsor, TalkIdea

class BarcampForm(ModelForm):
    class Meta:
        model = Barcamp
        exclude = ('organizers', 'sponsors', 'places', 'removal_requested_by', 
                   'removal_canceled_by', 'marked_for_removal_at')
                   
class SponsorForm(ModelForm):
    class Meta:
        model = Sponsor
        exclude = ('barcamp')
        
class ProposalForm(ModelForm):
    class Meta:
        model = TalkIdea
        exclude = ('barcamp', 'votes', 'created_at', 'modified_at', 'user')
        