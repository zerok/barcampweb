import datetime

from django.forms.models import ModelForm
from django import forms
from django.conf import settings
from django.utils import dateformat
from django.utils.translation import ugettext_lazy as _

from . import models
from .models import Barcamp, Sponsor, TalkIdea, Talk, TimeSlot

class DateChoiceField(forms.ChoiceField):
    
    FORMAT = '%Y-%m-%d'
    
    def to_python(self, value):
        result =  datetime.datetime.strptime(value, self.FORMAT).date()
        return result
        
    def valid_value(self, value):
        "Check to see if the provided value is a valid choice"
        dvalue = value.strftime(self.FORMAT)
        for k, v in self.choices:
            if isinstance(v, (list, tuple)):
                # This is an optgroup, so look inside the group for options
                for k2, v2 in v:
                    if dvalue == k2:
                        return True
            else:
                if dvalue == k:
                    return True
        return False


class BarcampForm(ModelForm):
    class Meta:
        model = Barcamp
        exclude = ('organizers', 'sponsors', 'places', 'removal_requested_by', 
                   'removal_canceled_by', 'marked_for_removal_at')
                   
class SponsorForm(ModelForm):
    class Meta:
        model = Sponsor
        exclude = ('barcamp')
        
class AnonymousProposalForm(ModelForm):
    class Meta:
        model = TalkIdea
        exclude = ('barcamp', 'votes', 'created_at', 'modified_at', 'user')
        
class ProposalForm(ModelForm):
    class Meta:
        model = TalkIdea
        exclude = ('barcamp', 'votes', 'created_at', 'modified_at', 'user', 'user_name', 'user_email')
        
class CreateSlotForm(forms.Form):
    
    day = DateChoiceField(label=_("Day"))
    start = forms.TimeField(label=_("Start time"))
    end = forms.TimeField(label=_("End time"))
    room = forms.ChoiceField(required=False, label=_("Room"))
    
    def __init__(self, *args, **kwargs):
        if 'barcamp' in kwargs:
            self.barcamp = kwargs['barcamp']
            del kwargs['barcamp']
        super(CreateSlotForm, self).__init__(*args, **kwargs)
        self.fields['day'].choices = [(d.date().strftime(DateChoiceField.FORMAT), dateformat.format(d, settings.DATE_FORMAT)) for d in self.barcamp.days]
        print self.fields['day'].choices
        self.fields['room'].choices = [(p.pk, p.name) for p in self.barcamp.places.all() if p.is_sessionroom]
        self.fields['room'].choices[0:0] = [(0, '')]
    
    def get_start(self):
        return self.combine_dt(self.cleaned_data['day'], self.cleaned_data['start'])
        
    def get_end(self):
        return self.combine_dt(self.cleaned_data['day'], self.cleaned_data['end'])
    
    def combine_dt(self, date, time):
        return datetime.datetime(date.year, date.month, date.day, time.hour, time.minute)
    
    def clean(self):
        _start = self.cleaned_data.get('start')
        _end = self.cleaned_data.get('end')
        _day = self.cleaned_data.get('day')
        _room = self.cleaned_data.get('room')
        if _room is not None:
            _room = int(_room)
        if _start is None or _end is None or _day is None:
            return self.cleaned_data
        if _start >= _end:
            raise forms.ValidationError, _("Start has to be before the the end")
        if self.barcamp is not None:
            # Make sure that this is a unique timeslot for the duration
            # of the camp
            start = self.combine_dt(_day, _start)
            end = self.combine_dt(_day, _end)
            slots = self.barcamp.slots.select_related().all()
            found_intersection = []
            for slot in slots:
                if start >= slot.end or slot.start >= end:
                    continue
                if start >= slot.start and start <= slot.end:
                    found_intersection.append(slot)
                if end <= slot.end and slot.start <= end:
                    found_intersection.append(slot)
            if _room == 0:
                # If no room was specified any intersection is a problem
                pass
            else:
                # If a room was specified check if any given slot has either
                # no room or the same room to violate this constraint
                for slot in found_intersection:
                    if slot.place is None:
                        raise forms.ValidationError, _("A generic slot for this range already exists.")
                    if slot.place.pk == _room:
                        raise forms.ValidationError, _("There already exists a timeslot for this range and this room.")
                pass
            #if len(found_intersection):
            #    raise forms.ValidationError, _("There already exists a timeslot with this range")
        return self.cleaned_data
                    
            
        
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

        if self.timeslot.place is not None and self.timeslot.place != self.room:
            raise forms.ValidationError(_("This timeslot is bound to another place"))
        
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
        slots = kwargs['open_slots']
        self.open_slots = {}
        for sge in slots:
            self.open_slots["%d-%d" % (sge.slot.pk, sge.place.pk)] = sge
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

class CreatePlaceForm(forms.ModelForm):
    class Meta:
        model = models.Place
        exclude = ('barcamp',)

class EditPlaceForm(forms.ModelForm):
    class Meta:
        model = models.Place
        exclude = ('barcamp',)

    def clean(self):
        cleaned_data = super(EditPlaceForm, self).clean()

        # If this place is about to lose its sessionroom status,
        # make sure that there are no exclusive slots or sessions
        # in generic slots associated with this place.
        if self.instance is not None:
            sessionroom = bool(cleaned_data.get('is_sessionroom', False))
            if not sessionroom:
                if 0 != models.TimeSlot.objects.filter(barcamp=self.instance.barcamp, place=self.instance).count():
                    raise forms.ValidationError(_("There are timeslots bound to this place. Please unbind them before proceeding."))
                if 0 != models.Talk.objects.filter(place=self.instance).count():
                    raise forms.ValidationError(_("There are still talks associated with this place. Please assign them to another room."))
        return cleaned_data
