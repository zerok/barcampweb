from django.conf.urls.defaults import *
from .views import index, view_barcamp, view_proposals, view_schedule

urlpatterns = patterns('barcampweb_site.apps.barcamp',
    url('^$', index, name='barcamp-index'),
    url('^(?P<slug>[^/]+)/$', view_barcamp, name='barcamp-view'),
    url('^(?P<slug>[^/]+)/proposals/$', view_proposals, name='barcamp-proposals'),
    url('^(?P<slug>[^/]+)/schedule/$', view_schedule, name='barcamp-schedule'),
)
