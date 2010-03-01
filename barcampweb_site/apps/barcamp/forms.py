from django.forms.models import ModelForm

from .models import Barcamp

class BarcampForm(ModelForm):
    class Meta:
        model = Barcamp
        exclude = ('organizers', 'sponsors', 'places', 'removal_requested_by', 
                   'removal_canceled_by', 'marked_for_removal_at')