from django.conf.urls.defaults import *
from .views import index, view_barcamp, view_proposals, view_schedule, \
    delete_barcamp, undelete_barcamp, edit_barcamp, create_barcamp, \
    add_sponsor, remove_sponsor, edit_sponsor

urlpatterns = patterns('barcampweb_site.apps.barcamp',
    url('^$', index, name='barcamp-index'),
    url('^(?P<slug>[^_][^/]+)/$', view_barcamp, name='barcamp-view'),
    url('^(?P<slug>[^_][^/]+)/proposals/$', view_proposals, name='barcamp-proposals'),
    url('^(?P<slug>[^_][^/]+)/schedule/$', view_schedule, name='barcamp-schedule'),
    url('^(?P<slug>[^_][^/]+)/delete/$', delete_barcamp, name='barcamp-delete'),
    url('^(?P<slug>[^_][^/]+)/edit/$', edit_barcamp, name='barcamp-edit'),
    url('^(?P<slug>[^_][^/]+)/undelete/$', undelete_barcamp, name='barcamp-undelete'),
    url('^(?P<slug>[^_][^/]+)/add-sponsor/$', add_sponsor, name='barcamp-add-sponsor'),
    url('^(?P<slug>[^_][^/]+)/remove-sponsor/(?P<sponsoring_pk>\d+)/$', remove_sponsor, name='barcamp-remove-sponsor'),
    url('^(?P<slug>[^_][^/]+)/edit-sponsor/(?P<sponsoring_pk>\d+)/$', edit_sponsor, name='barcamp-edit-sponsor'),
    url('^_create/$', create_barcamp, name='barcamp-create'),
)
