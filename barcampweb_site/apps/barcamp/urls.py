from django.conf.urls.defaults import *
from .views import index, view_barcamp, view_proposals, view_schedule, \
    delete_barcamp, undelete_barcamp, edit_barcamp, create_barcamp, \
    add_sponsor, remove_sponsor, edit_sponsor, vote_proposal, unvote_proposal, \
    create_proposal, delete_proposal, edit_proposal, create_talk

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
    url('^(?P<slug>[^_][^/]+)/create-proposal/$', create_proposal, name='barcamp-create-proposal'),
    url('^(?P<slug>[^_][^/]+)/proposals/(?P<proposal_pk>\d+)/vote/$', vote_proposal, name='barcamp-vote-proposal'),
    url('^(?P<slug>[^_][^/]+)/proposals/(?P<proposal_pk>\d+)/unvote/$', unvote_proposal, name='barcamp-unvote-proposal'),
    url('^(?P<slug>[^_][^/]+)/proposals/(?P<proposal_pk>\d+)/delete/$', delete_proposal, name='barcamp-delete-proposal'),
    url('^(?P<slug>[^_][^/]+)/proposals/(?P<proposal_pk>\d+)/edit/$', edit_proposal, name='barcamp-edit-proposal'),
    url('^(?P<slug>[^_][^/]+)/schedule/create-talk/(?P<slot_pk>\d+)-(?P<room_pk>\d+)/$', create_talk, name='barcamp-create-talk'),
    url('^_create/$', create_barcamp, name='barcamp-create'),
)
