import datetime

from django.test import TestCase

from . import utils

class UtilsTests(TestCase):
    def test_get_days(self):
        start = datetime.datetime(2009, 11, 1)
        end = datetime.datetime(2009, 11, 2)
        result = list(utils.get_days(start, end))
        self.assertEqual(2, len(result))
        
        