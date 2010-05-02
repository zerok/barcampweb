from django.conf.urls.defaults import *

urlpatterns = patterns('barcampweb_site.apps.account.views',
    url(r'^slogin', 'simple_login', name='simple_login'),
    url(r'^slogout', 'simple_logout', name='simple_logout'),
    url(r'^register', 'register', name='register'),
)