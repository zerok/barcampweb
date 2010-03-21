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
        other_talks = Talk.objects.filter(barcamp=self.barcamp, timeslot=self.timeslot, place=self.room)
        if len(other_talks) > 0 and not (self.instance is None or other_talks[0].pk == self.instance.pk):
            raise forms.ValidationError(_("This slot is already taken"))
        
        return self.cleaned_data
        
    class Meta:
        model = Talk
        exclude = ('barcamp', 'timeslot', 'start', 'end', 'place', 'resources')

class MoveTalkForm(forms.Form):
    slot = forms.ChoiceField(label=_('Timeslot'))
    
    def __init__(self, *args, **kwargs):
        self.open_slots = kwargs['open_slots']
        self.instance = kwargs['instance']
        del kwargs['open_slots']
        del kwargs['instance']
        super(MoveTalkForm, self).__init__(*args, **kwargs)
        self.fields['slot'].choices = [(k, unicode(v)) for k, v in self.open_slots.items()]
    
    def clean_slot(self):
        value = self.cleaned_data['slot']
        # Check if the slot is still available
        slot = self.open_slots[value]
        if 0 != Talk.objects.filter(barcamp=self.instance.barcamp, place=slot.place, timeslot=slot.slot).count():
            raise forms.ValidationError(_("This slot is already taken"))
        return value