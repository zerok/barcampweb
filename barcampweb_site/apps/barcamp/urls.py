from django.conf.urls.defaults import *
from .views import index, view_barcamp, view_proposals, view_schedule, \
    delete_barcamp, undelete_barcamp, edit_barcamp, create_barcamp, \
    add_sponsor, remove_sponsor, edit_sponsor, vote_proposal, unvote_proposal, \
    create_proposal, delete_proposal, edit_proposal, create_talk, edit_talk, \
    delete_talk, detach_talk, move_talk

urlpatterns = patterns('barcampweb_site.apps.barcamp',
    url('^$', index, name='index'),
    url('^(?P<slug>[^_][^/]+)/$', view_barcamp, name='view'),
    url('^(?P<slug>[^_][^/]+)/proposals/$', view_proposals, name='proposals'),
    url('^(?P<slug>[^_][^/]+)/schedule/$', view_schedule, name='schedule'),
    url('^(?P<slug>[^_][^/]+)/delete/$', delete_barcamp, name='delete'),
    url('^(?P<slug>[^_][^/]+)/edit/$', edit_barcamp, name='edit'),
    url('^(?P<slug>[^_][^/]+)/undelete/$', undelete_barcamp, name='undelete'),
    url('^(?P<slug>[^_][^/]+)/add-sponsor/$', add_sponsor, name='add-sponsor'),
    url('^(?P<slug>[^_][^/]+)/remove-sponsor/(?P<sponsoring_pk>\d+)/$', remove_sponsor, name='remove-sponsor'),
    url('^(?P<slug>[^_][^/]+)/edit-sponsor/(?P<sponsoring_pk>\d+)/$', edit_sponsor, name='edit-sponsor'),
    url('^(?P<slug>[^_][^/]+)/create-proposal/$', create_proposal, name='create-proposal'),
    url('^(?P<slug>[^_][^/]+)/proposals/(?P<proposal_pk>\d+)/vote/$', vote_proposal, name='vote-proposal'),
    url('^(?P<slug>[^_][^/]+)/proposals/(?P<proposal_pk>\d+)/unvote/$', unvote_proposal, name='unvote-proposal'),
    url('^(?P<slug>[^_][^/]+)/proposals/(?P<proposal_pk>\d+)/delete/$', delete_proposal, name='delete-proposal'),
    url('^(?P<slug>[^_][^/]+)/proposals/(?P<proposal_pk>\d+)/edit/$', edit_proposal, name='edit-proposal'),
    url('^(?P<slug>[^_][^/]+)/schedule/create-talk/(?P<slot_pk>\d+)-(?P<room_pk>\d+)/$', create_talk, name='create-talk'),
    url('^(?P<slug>[^_][^/]+)/schedule/edit-talk/(?P<talk_pk>\d+)/$', edit_talk, name='edit-talk'),
    url('^(?P<slug>[^_][^/]+)/schedule/delete-talk/(?P<talk_pk>\d+)/$', delete_talk, name='delete-talk'),
    url('^(?P<slug>[^_][^/]+)/schedule/detach-talk/(?P<talk_pk>\d+)/$', detach_talk, name='detach-talk'),
    url('^(?P<slug>[^_][^/]+)/schedule/move-talk/(?P<talk_pk>\d+)/$', move_talk, name='move-talk'),
    url('^_create/$', create_barcamp, name='create'),
)
