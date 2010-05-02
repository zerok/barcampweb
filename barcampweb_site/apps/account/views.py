import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db import transaction
from django.contrib.auth import authenticate, login as auth_login

from barcampweb_site.utils import render as _render

from . import forms, utils


APP_NAME = 'account'
LOG = logging.getLogger(__name__)

def render(request, tmpl, vars_):
    return _render(request, tmpl, vars_, APP_NAME)

@transaction.commit_on_success
def register(request):
    """
    The user registration is a bit simplified here. A user only has to
    specify a name and email address. The password will be auto-generated
    and set to her using that address but also shown right after the 
    registration. 
    
    Also, the user is logged in right after the registration.
    """
    form = forms.RegistrationForm()
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            pwd = utils.generate_password()
            new_user.set_password(pwd)
            new_user.save()
            utils.send_welcome_mail(new_user, pwd)
            messages.info(request, "Danke, dass du dich registriert hast. Dein Passwort lautet %s. Es wurde dir auch an deine E-Mail-Adresse geschickt" % pwd)
            authenticated_user = authenticate(username=new_user.username, password=pwd)
            LOG.debug(authenticated_user.backend)
            auth_login(request, authenticated_user)
            return HttpResponseRedirect(request.REQUEST.get('next', '/'))
    return render(request, 'account/registration.html', {'form': form})
    
def simple_login(request):
    """
    Simple login allows a user to store his/her name is the session.
    """
    if request.user.is_authenticated():
        messages.info(request, "You are already logged in")
        return HttpResponseRedirect(request.REQUEST.get('next', '/'))
    form = forms.SimpleLoginForm()
    if request.method == 'POST':
        form = forms.SimpleLoginForm(request.POST)
        if form.is_valid():
            request.username = form.cleaned_data['username']
            return HttpResponseRedirect(request.REQUEST.get('next', '/'))
    return render(request, 'account/simple_login.html', {'form': form})
    
def simple_logout(request):
    request.username = None
    return HttpResponseRedirect(request.REQUEST.get('next', '/'))