from dateutil import rrule
import sys
import logging

from django.utils.datastructures import SortedDict

LOG = logging.getLogger(__name__)

class PlaceSlot(object):
    def __init__(self, place, slot):
        self.place = place
        self.slot = slot
    def __unicode__(self):
        return u"%s: %s" % (self.slot, self.place.name)

def get_days(start, end):
    return rrule.rrule(rrule.DAILY, dtstart=start, until=end)

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

    @classmethod
    def create_from_barcamp(cls, barcamp, room_order=None):
        grid = cls()
        if room_order is not None:
            grid.places = room_order
        else:
            grid.places = [x for x in barcamp.places.filter(is_sessionroom=True).order_by('pk')]
        slots = barcamp.slots.all().order_by('start')
        start_grid = {}
        for slot in slots:
            if slot.start not in start_grid:
                start_grid[slot.start]=[None for x in grid.places]
            if slot.place is None:
                start_grid[slot.start] = [slot for x in grid.places]
            else:
                start_grid[slot.start][grid.places.index(slot.place)]=slot
        for k in sorted(start_grid.keys()):
            grid.grid.append(start_grid[k])

        return grid
    
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
