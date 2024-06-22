import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import unittest
from datetime import datetime
from empathy_chat import helper as h


class Seconds2WordsTest(unittest.TestCase):
  def test_day(self):
    self.assertEqual(h.seconds_to_words(3600*24), "1 day, 0 seconds")
  
  def test_day_no_seconds(self):
    self.assertEqual(h.seconds_to_words(3600*24, include_seconds=False), "1 day, 0 minutes")
    
  def test_minus(self):
    self.assertEqual(h.seconds_to_words(-1), "minus 1 second")

    
class DatetimeFormatTest(unittest.TestCase):
  def test_remove_zeros(self):
    dt = datetime(2021, 1, 1, 1, 1)
    self.assertEqual(h.time_str(dt), "1:01AM")
    self.assertEqual(h.dow_date_str(dt), "Friday, Jan 1, 2021")
    self.assertEqual(h.day_time_str(dt), "Fri, Jan 1 1:01AM")
    self.assertEqual(h.short_date_str(dt), "1/1/2021")
    
  def test_no_change(self):
    dt = datetime(2020, 12, 31, 10, 10)
    self.assertEqual(h.time_str(dt), "10:10AM")
    self.assertEqual(h.dow_date_str(dt), "Thursday, Dec 31, 2020")
    self.assertEqual(h.day_time_str(dt), "Thu, Dec 31 10:10AM")
    self.assertEqual(h.short_date_str(dt), "12/31/2020")


class RoundUpDatetimeTest(unittest.TestCase):
  def test_round_up(self):
    dt = datetime(2021, 1, 1, 1, 1, 1)
    self.assertEqual(h.round_up_datetime(dt), datetime(2021, 1, 1, 1, 15))
    self.assertEqual(h.round_up_datetime(dt, 30), datetime(2021, 1, 1, 1, 30))
