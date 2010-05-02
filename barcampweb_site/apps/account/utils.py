import random

from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from django import template


def send_welcome_mail(user, password):
    subject = _("Welcome to barcampweb")
    tmpl = template.loader.get_template('account/email/welcome.txt')
    msg = tmpl.render(template.Context({'user': user, 'password': password}))
    sender = settings.DEFAULT_FROM_EMAIL
    recipients = [user.email]
    send_mail(subject, msg, sender, recipients)
    
def generate_password(length=None):
    if length is None:
        length = 6
    chars = 'abcdefghjklmnpqrstuvw0123456789'
    rand = random.Random()
    return ''.join([random.choice(chars) for x in range(length)])