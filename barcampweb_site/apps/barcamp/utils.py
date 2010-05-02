from dateutil import rrule
import sys
import logging

from django.utils.datastructures import SortedDict

from . import models

LOG = logging.getLogger(__name__)

class PlaceSlot(object):
    def __init__(self, place, slot):
        self.place = place
        self.slot = slot
    def __unicode__(self):
        return u"%s: %s" % (self.slot, self.place.name)

def get_days(start, end):
    return rrule.rrule(rrule.DAILY, dtstart=start, until=end)

class SlotGridElement(object):
    def __init__(self, slot=None, place=None):
        self.slot = slot is not None and slot or None
        self.place = place is not None and place or None
        self.events = []

    def __unicode__(self):
        return unicode(self.slot.start) + u" - " + unicode(self.slot.end) + " (" + self.place.name + ")"

class SlotGrid(object):
    """
    A slotgrid represents a matrix of slots associated with
    a room. Internally it is a 2dim array where columns are
    associated with place objects.

    If all slots are synchronized then the row dimension
    as a whole has an additional slot association.
    """
    def __init__(self):
        self.grid = []
        self.places = []
        self.slots = []
        self.date = None
    
    @classmethod
    def create_from_barcamp(cls, barcamp, room_order=None, per_day=False, mark_for_user=None):
        if room_order is not None:
            places = room_order
        else:
            places = [x for x in barcamp.places.filter(is_sessionroom=True).order_by('pk')]
        slots = barcamp.slots.all().order_by('start')
        sge_index = {}
        start_grid = {}
        for slot in slots:
            if slot.start not in start_grid:
                start_grid[slot.start]=[None for x in places]
            if slot.place is None:
                start_grid[slot.start] = []
                for p in places:
                    sge = SlotGridElement(slot=slot, place=p)
                    start_grid[slot.start].append(sge)
                    sge_index["%d-%d" % (sge.slot.pk, sge.place.pk)] = sge
            else:
                sge = SlotGridElement(slot=slot, place=slot.place)
                start_grid[slot.start][places.index(slot.place)] = sge
                sge_index["%d-%d" % (sge.slot.pk, sge.place.pk)] = sge

        # Fill the sges with events
        events =  models.Talk.objects.filter(barcamp=barcamp,timeslot__isnull=False, place__isnull=False)
        if mark_for_user is not None:
            mark_talklist_permissions(events, mark_for_user, barcamp)
        for ev in events:
            sge_index["%d-%d" % (ev.timeslot.pk, ev.place.pk)].events.append(ev)
        open_elems = [sge for sge in sge_index.values() if len(sge.events) == 0]

        if per_day:
            date_grids = []
            grid = None
            last_date = None
            for k in sorted(start_grid.keys()):
                date = k.date()
                if date != last_date:
                    if grid is not None:
                        date_grids.append(grid)
                    grid = SlotGrid()
                    grid.places = places
                    grid.date = date
                grid.grid.append(start_grid[k])
                last_date = date
            if grid is not None:
                date_grids.append(grid)
            return date_grids, open_elems
        else:
            grid = SlotGrid()
            grid.places=places
            for k in sorted(start_grid.keys()):
                grid.grid.append(start_grid[k])

        return grid, open_elems
    
def create_slot_grid(barcamp):
    from .models import Talk
    
    talks = Talk.objects.filter(barcamp=barcamp).select_related().all()
    slots = barcamp.slots.order_by('start').all()
    rooms = barcamp.places.all()
    open_slots = {}
    
    result = SortedDict() # Grid with slots as first and room as second dim.
    for slot in slots:
        if slot not in result:
            result[slot] = {}
        for room in rooms:
            open_slots['r%d-s%d' % (room.pk, slot.pk)] = PlaceSlot(room, slot)
            result[slot][room] = None
    
    for talk in talks:
        if talk.timeslot is None or talk.place is None:
            continue
        result[talk.timeslot][talk.place] = talk
        del open_slots['r%d-s%d' % (talk.place.pk, talk.timeslot.pk)]
    
    return result, open_slots
    
def mark_talkgrid_permissions(grid, user, barcamp):
    organizers = barcamp.organizers.all()
    user_talks = hasattr(user, 'talks') and user.talks.all() or []
    for slot, rooms in grid.items():
        for room, talk in rooms.items():
            if talk is None:
                continue
            _mark_talk_permissions(talk, user, barcamp, user_talks)

def mark_talklist_permissions(talks, user, barcamp):
    user_talks = hasattr(user, 'talks') and user.talks.all() or []
    for talk in talks:
        if talk is None:
            continue
        _mark_talk_permissions(talk, user, barcamp, user_talks)
    
def _mark_talk_permissions(talk, user, barcamp, user_talks):
    if user.is_superuser or user.is_staff:
        talk.can_edit = True
    elif talk in user_talks:
        talk.can_edit = True
    else:
        talk.can_edit = False   
