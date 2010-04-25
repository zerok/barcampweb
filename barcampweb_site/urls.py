from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    url(r'^', include('barcampweb_site.apps.barcamp.urls', namespace='barcamp', app_name='barcamp')),
    url(r'^account/login', login, {'template_name': 'account/login.html'}, name="login"),
    url(r'^account/logout', logout, name="logout"),
    url(r'^account/', include('barcampweb_site.apps.account.urls', namespace='account', app_name='account')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )