import datetime

from django.test import TestCase

from . import utils, models

class UtilsTests(TestCase):
    def test_get_days(self):
        start = datetime.datetime(2009, 11, 1)
        end = datetime.datetime(2009, 11, 2)
        result = list(utils.get_days(start, end))
        self.assertEqual(2, len(result))
        
class GridTests(TestCase):
    def test_complex_grid(self):
        """
        A complex grid is one that contains slots that are
        not completely aligned. In such a case only parallel
        slots should be positioned in the same table row while
        even a minimally later start time forces the creation
        of a new row.

        The test case presented here should produce a grid like
        this one::
            
            a1 | b1 |
           ----+----+----
               | b2 | 
           ----+----+----
            a2 | b3 | c1
           ----+----+----
            a3 |    | c2

        """
        barcamp = models.Barcamp(name="barcamp", start=datetime.datetime(2010,5,1), end=datetime.datetime(2010,5,2))
        barcamp.save()
        room_a = models.Place(name="a")
        room_b = models.Place(name="b")
        room_c = models.Place(name="c")
        room_a.save()
        room_b.save()
        room_c.save()
        barcamp.places.add(room_a)
        barcamp.places.add(room_b)
        barcamp.places.add(room_c)

        slot_a1 = models.TimeSlot(start=datetime.datetime(2010,5,1,9,0), end=datetime.datetime(2010,05,1,9,30), place=room_a, barcamp=barcamp)
        slot_a2 = models.TimeSlot(start=datetime.datetime(2010,5,1,9,30), end=datetime.datetime(2010,05,1,10,0), place=room_a, barcamp=barcamp)
        slot_a3 = models.TimeSlot(start=datetime.datetime(2010,5,1,10,0), end=datetime.datetime(2010,05,1,10,30), place=room_a, barcamp=barcamp)
        slot_a1.save()
        slot_a2.save()
        slot_a3.save()

        slot_b1 = models.TimeSlot(start=datetime.datetime(2010,5,1,9,0), end=datetime.datetime(2010,05,1,9,15), place=room_b, barcamp=barcamp)
        slot_b2 = models.TimeSlot(start=datetime.datetime(2010,5,1,9,15), end=datetime.datetime(2010,05,1,9,30), place=room_b, barcamp=barcamp)
        slot_b3 = models.TimeSlot(start=datetime.datetime(2010,5,1,9,30), end=datetime.datetime(2010,05,1,10,0), place=room_b, barcamp=barcamp)
        slot_b1.save()
        slot_b2.save()
        slot_b3.save()

        slot_c1 = models.TimeSlot(start=datetime.datetime(2010,5,1,9,30), end=datetime.datetime(2010,05,1,10,0), place=room_c, barcamp=barcamp)
        slot_c2 = models.TimeSlot(start=datetime.datetime(2010,5,1,10,0), end=datetime.datetime(2010,05,1,10,30), place=room_c, barcamp=barcamp)
        slot_c1.save()
        slot_c2.save()
        grid = utils.SlotGrid.create_from_barcamp(barcamp).grid
        self.assertEqual(slot_a1, grid[0][0])
        self.assertEqual(slot_a2, grid[2][0])
        self.assertEqual(slot_a3, grid[3][0])
        self.assertEqual(slot_b1, grid[0][1])
        self.assertEqual(slot_b2, grid[1][1])
        self.assertEqual(slot_b3, grid[2][1])
        self.assertEqual(slot_c1, grid[2][2])
        self.assertEqual(slot_c2, grid[3][2])
