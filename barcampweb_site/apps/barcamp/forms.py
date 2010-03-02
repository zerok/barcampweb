from django.forms.models import ModelForm
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Barcamp, Sponsor

class BarcampForm(ModelForm):
    class Meta:
        model = Barcamp
        exclude = ('organizers', 'sponsors', 'places', 'removal_requested_by', 
                   'removal_canceled_by', 'marked_for_removal_at')

class AddSponsorForm(forms.Form):
    existing_company = forms.ChoiceField(required=False)
    level = forms.IntegerField()
    name = forms.CharField(required=False)
    url = forms.URLField(required=False)
    logo = forms.ImageField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(AddSponsorForm, self).__init__(*args, **kwargs)
        # Init the existing companies field with all available sponsors
        self.fields['existing_company'].choices = [('', _('Create new sponsor ...'))] + [(c.pk, c.name) for c in Sponsor.objects.all()]
        
    def clean(self):
        if not self.cleaned_data.get('existing_company'):
            # Name, url and logo are now required fields
            msg = _('This field is required if no existing sponsor is used.')
            if not self.cleaned_data['name']:
                self._errors['name'] = forms.util.ErrorList([msg])
            if not self.cleaned_data['url']:
                self._errors['url'] = forms.util.ErrorList([msg])
            if not self.cleaned_data['logo']:
                self._errors['logo'] = forms.util.ErrorList([msg])
        return self.cleaned_data