from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import unittest
import time

    
# class MyGroupsTest(unittest.TestCase):
#   def setUp(self):
#     pass
#     #self.my_groups = groups.MyGroups()
#     #self.my_groups = anvil.server.call('load_my_groups)
    
#   def test_get_items(self):
#     items = self.my_groups.drop_down_items()
    
#   def test_add_group(self):
#     new_group = self.my_groups.add_group()
#     self.assertEqual(new_group['name'], "New Group")


def client_auto_tests():
  from anvil_extras.utils import timed
  from . import invited_test as it
  
  @timed
  def tests_run_client_side():
    it.Invited1Test().main()
    it.InvitedTest().main()
  tests_run_client_side()
  
  
def client_slow_tests():
  from anvil_extras.utils import timed
  from . import invited_test as it
  from . import portable_test as pt
  
  @timed
  def tests_run_client_side():
    it.InvitedSlowTest().main()
    pt.PortUserTest().main()
  tests_run_client_side()


def test_alert(content, handler):
  content.set_event_handler('x-close-alert', handler)
  