from django.forms.models import ModelForm
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Barcamp, Sponsor, TalkIdea, Talk

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
        
class TalkForSlotForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(TalkForSlotForm, self).__init__(*args, **kwargs)
        self.barcamp = None
        self.timeslot = None
        self.room = None
    
    def clean(self):
        super(TalkForSlotForm, self).clean()
        
        assert(self.barcamp)
        assert(self.timeslot)
        assert(self.room)
        
        # Make sure, that this slot isn't already taken
        if 0 < Talk.objects.filter(barcamp=self.barcamp, timeslot=self.timeslot, place=self.place).count():
            raise forms.ValidationException(_("This slot is already taken"))
        
    class Meta:
        model = Talk
        exclude = ('barcamp', 'timeslot', 'start', 'end', 'place', 'resources', 'speakers')
        