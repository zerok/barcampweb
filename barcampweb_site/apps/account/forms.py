from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')
    
    def clean(self):
        username = self.cleaned_data['username']
        others = User.objects.filter(username=username)
        if len(others):
            raise forms.ValidationError, _("This username is already taken")
        return self.cleaned_data

class SimpleLoginForm(forms.Form):
    username = forms.CharField()