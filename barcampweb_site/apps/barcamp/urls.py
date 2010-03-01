from django.conf.urls.defaults import *
from .views import index, view_barcamp, view_proposals, view_schedule, \
    delete_barcamp, undelete_barcamp, edit_barcamp, create_barcamp

urlpatterns = patterns('barcampweb_site.apps.barcamp',
    url('^$', index, name='barcamp-index'),
    url('^(?P<slug>[^_][^/]+)/$', view_barcamp, name='barcamp-view'),
    url('^(?P<slug>[^_][^/]+)/proposals/$', view_proposals, name='barcamp-proposals'),
    url('^(?P<slug>[^_][^/]+)/schedule/$', view_schedule, name='barcamp-schedule'),
    url('^(?P<slug>[^_][^/]+)/delete/$', delete_barcamp, name='barcamp-delete'),
    url('^(?P<slug>[^_][^/]+)/edit/$', edit_barcamp, name='barcamp-edit'),
    url('^(?P<slug>[^_][^/]+)/undelete/$', undelete_barcamp, name='barcamp-undelete'),
    url('^_create/$', create_barcamp, name='barcamp-create'),
)
