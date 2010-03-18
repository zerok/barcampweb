from dateutil import rrule

from django.utils.datastructures import SortedDict

def get_days(start, end):
    return rrule.rrule(rrule.DAILY, dtstart=start, until=end)
    
def create_slot_grid(barcamp):
    from .models import Talk
    
    talks = Talk.objects.filter(barcamp=barcamp).select_related().all()
    slots = barcamp.slots.order_by('start').all()
    rooms = barcamp.places.all()
    
    result = SortedDict() # Grid with slots as first and room as second dim.
    for slot in slots:
        if slot not in result:
            result[slot] = {}
        for room in rooms:
            result[slot][room] = None
    
    for talk in talks:
        result[talk.timeslot][talk.place] = talk
    
    return result
    
def mark_talk_permissions(grid, user, barcamp):
    organizers = barcamp.organizers.all()
    user_talks = hasattr(user, 'talks') and user.talks.all() or []
    for slot, rooms in grid.items():
        for room, talk in rooms.items():
            if talk is None:
                continue
            if user.is_superuser or user.is_staff:
                talk.can_edit = True
            elif talk in user_talks:
                talk.can_edit = True
            else:
                talk.can_edit = False
            