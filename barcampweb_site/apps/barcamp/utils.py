from dateutil import rrule

from django.utils.datastructures import SortedDict

class PlaceSlot(object):
    def __init__(self, place, slot):
        self.place = place
        self.slot = slot
    def __unicode__(self):
        return u"%s: %s" % (self.slot, self.place.name)

def get_days(start, end):
    return rrule.rrule(rrule.DAILY, dtstart=start, until=end)
    
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