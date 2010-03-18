import os
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

RESERVATION_STATUS_CHOICES = (
    ('yes', _('Yes')),
    ('no', _('No')),
    ('maybe', _('Maybe')),
)

class Barcamp(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    teaser = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='logos', null=True, blank=True)
    twitter_tag = models.CharField(max_length=50, blank=True, null=True)
    organizers = models.ManyToManyField(User, related_name='organized_barcamps', blank=True, null=True)
    marked_for_removal_at=models.DateTimeField(blank=True, null=True)
    removal_requested_by=models.ForeignKey(User, blank=True, null=True, related_name='requested_barcamp_removals')
    removal_canceled_by=models.ForeignKey(User, blank=True, null=True, related_name='canceled_barcamp_removals')
    places = models.ManyToManyField('Place', related_name='places', null=True, blank=True)
    available = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

class Reservation(models.Model):
    user = models.ForeignKey(User, related_name='reservations')
    barcamp = models.ForeignKey(Barcamp, related_name='reservations')
    status = models.CharField(max_length=10, choices=RESERVATION_STATUS_CHOICES)

class Sponsor(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(verify_exists=False)
    logo = models.ImageField(upload_to='sponsor_logos')
    level = models.IntegerField()
    barcamp = models.ForeignKey('Barcamp', related_name='sponsors')
    
    def delete(self):
        os.remove(self.logo.path)
        super(Sponsor, self).delete()
        
    def save(self, *args, **kwargs):
        if self.pk is not None and self.logo:
            old_instance = self.__class__.objects.get(pk=self.pk)
            if old_instance.logo != self.logo:
                os.unlink(old_instance.logo.path)
        super(Sponsor, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.name

class Place(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=500, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    is_sessionroom = models.BooleanField(default=True)
    
    def __unicode__(self):
        if self.location:
            return u"%s (%s)" % (self.name, self.location)
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    place = models.ForeignKey('Place')
    barcamp = models.ForeignKey('Barcamp', related_name='events')
    start = models.DateTimeField()
    end = models.DateTimeField()
    
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.barcamp)

class Talk(Event):
    resources = models.ManyToManyField('Resource', related_name='talks', null=True, blank=True)
    speakers = models.ManyToManyField(User, related_name='talks')
    timeslot = models.ForeignKey('TimeSlot', related_name='talks')
    
    can_edit = False # View helper
    # TODO: Add unique_together constraint

class SideEvent(Event):
    pass
    
class TimeSlot(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    barcamp = models.ForeignKey('Barcamp', related_name='slots')
    
    def __unicode__(self):
        return u"%s - %s" % (self.start, self.end)
    
class TalkIdea(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, related_name='talkideas')
    barcamp = models.ForeignKey(Barcamp)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    modified_at = models.DateTimeField(blank=True, null=True, auto_now=True)
    votes = models.ManyToManyField(User, related_name='voted_ideas', blank=True, null=True)
    
    already_voted  = False # Used during rendering
    
    _vote_count = None
    def vote_count(self):
        if self._vote_count is None:
            self._vote_count = self.votes.count()
        return self._vote_count
    
    def __unicode__(self):
        return self.name
    
class Resource(models.Model):
    """
    A resource is for instance a set of slides that is linked to a given
    talk or a blog post related to it
    """
    name = models.CharField(max_length=255)
    rtype = models.ForeignKey('ResourceType')
    description = models.TextField(blank=True, null=True)
    url = models.URLField(verify_exists=False, blank=True, null=True)

class ResourceType(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
