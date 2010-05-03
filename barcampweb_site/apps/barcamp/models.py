import os
import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

RESERVATION_STATUS_CHOICES = (
    ('yes', _('Yes')),
    ('no', _('No')),
    ('maybe', _('Maybe')),
)

class Barcamp(models.Model):
    name = models.CharField(_("name"), max_length=255)
    slug = models.SlugField(_("slug"), unique=True)
    start = models.DateTimeField(_("start time"))
    end = models.DateTimeField(_("end time"))
    teaser = models.TextField(_("teaser"), blank=True, null=True)
    description = models.TextField(_("description"), blank=True, null=True)
    logo = models.ImageField(_("logo"), upload_to='logos', null=True, blank=True)
    twitter_tag = models.CharField(_("Twitter tag"), max_length=50, blank=True, null=True)
    organizers = models.ManyToManyField(User, verbose_name=_("organizers"), 
            related_name='organized_barcamps', blank=True, null=True)
    marked_for_removal_at=models.DateTimeField(_("marked for removal"), 
            blank=True, null=True)
    removal_requested_by=models.ForeignKey(User, 
            verbose_name=_("removal requested by"), blank=True, null=True,
            related_name='requested_barcamp_removals')
    removal_canceled_by=models.ForeignKey(User, 
            verbose_name=_("removal canceled by"),
            blank=True, null=True, related_name='canceled_barcamp_removals')
    available = models.BooleanField(_("available?"), default=False)

    class Meta:
        verbose_name = _("barcamp")
        verbose_name_plural = _("barcamps")

    def __unicode__(self):
        return self.name
    
    def _get_days(self):
        from .utils import get_days
        return get_days(self.start, self.end)
    days = property(_get_days)
    

class Sponsor(models.Model):
    name = models.CharField(_("name"), max_length=255)
    url = models.URLField(_("URL"), verify_exists=False)
    logo = models.ImageField(_("logo"), upload_to='sponsor_logos')
    level = models.IntegerField(_("level"))
    barcamp = models.ForeignKey('barcamp', verbose_name=_("Barcamp"), related_name='sponsors')

    class Meta:
        verbose_name = _("sponsor")
        verbose_name_plural = _("sponsors")
    
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
    """
    Places are for one barcamp only in order not to allow modifications
    of one barcamp's location by another organizer.
    """
    name = models.CharField(_("name"), max_length=255)
    location = models.CharField(_("location"), max_length=500, blank=True, null=True)
    address = models.CharField(_("address"), max_length=500, blank=True, null=True)
    barcamp = models.ForeignKey(Barcamp, verbose_name=_("barcamp"), related_name='places')
    is_sessionroom = models.BooleanField(_("is session room?"), default=True)

    class Meta:
        verbose_name = _('place')
        verbose_name_plural = _('places')
    
    def __unicode__(self):
        if self.location:
            return u"%s (%s)" % (self.name, self.location)
        return self.name

class Event(models.Model):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)
    place = models.ForeignKey('Place', verbose_name=_("place"))
    barcamp = models.ForeignKey('Barcamp', verbose_name=_("barcamp"), related_name='events')
    start = models.DateTimeField(_("start time"))
    end = models.DateTimeField(_("end time"))

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")
    
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.barcamp)

class Talk(Event):
    resources = models.ManyToManyField('Resource', verbose_name=_("resources"),
            related_name='talks', null=True, blank=True)
    speakers = models.CharField(_("speakers"), max_length=255) #models.ManyToManyField(User, related_name='talks')
    timeslot = models.ForeignKey('TimeSlot', verbose_name=_("time slot"), 
            related_name='talks', blank=True, null=True)
    
    can_edit = False # View helper

    class Meta:
        verbose_name = _("talk")
        verbose_name_plural = _("talks")

    # TODO: Add unique_together constraint

class SideEvent(Event):
    pass
    
class TimeSlot(models.Model):
    start = models.DateTimeField(_("start time"))
    end = models.DateTimeField(_("end time"))
    barcamp = models.ForeignKey('Barcamp', verbose_name=_("barcamp"), 
            related_name='slots')
    place = models.ForeignKey('Place', verbose_name=_("place"),
            related_name='roomslots', blank=True, null=True)

    class Meta:
        verbose_name = _("time slot")
        verbose_name_plural = _("time slots")
    
    def __unicode__(self):
        return u"%s - %s" % (self.start, self.end)
    
class TalkIdea(models.Model):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), null=True, blank=True)
    user = models.ForeignKey(User, verbose_name=_("user"), related_name='talkideas', blank=True, null=True)
    user_name = models.CharField(_("username"), max_length=255, blank=True, null=True)
    user_email = models.EmailField(_("e-mail address"), blank=True, null=True)
    barcamp = models.ForeignKey(Barcamp, verbose_name=_("barcamp"))
    created_at = models.DateTimeField(_("created at"), default=datetime.datetime.now)
    modified_at = models.DateTimeField(_("modified at"), blank=True, null=True, auto_now=True)
    votes = models.ManyToManyField(User, verbose_name=_("votes"), 
            related_name='voted_ideas', blank=True, null=True)
    
    already_voted  = False # Used during rendering
    
    _vote_count = None

    class Meta:
        verbose_name = _("talk idea")
        verbose_name_plural = _("talk ideas")

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
    name = models.CharField(_("name"), max_length=255)
    rtype = models.ForeignKey('ResourceType', verbose_name=_("resource type"))
    description = models.TextField(_("description"), blank=True, null=True)
    url = models.URLField(_("URL"), verify_exists=False, blank=True, null=True)

    class Meta:
        verbose_name = _("resource")
        verbose_name_plural = _("resources")

class ResourceType(models.Model):
    name = models.CharField(_("name"), max_length=255)
    slug = models.SlugField(_("slug"))

    class Meta:
        verbose_name = _("resource type")
        verbose_name_plural = _("resource types")
