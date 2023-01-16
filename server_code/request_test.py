import unittest
from unittest.mock import Mock
from .misc_server_test import ADMIN, USER2
from empathy_chat import request_interactor as ri
from empathy_chat.portable import Proposal


poptibo_id = USER2.get_id()


class TestNewRequest(unittest.TestCase):
  def test_add_single_later_request(self):
    port_prop = Proposal()
    request = ri._new_request(poptibo_id, port_prop)
    self.assertEqual(request.id, port_prop.times[0].proptime_id)
    self.assertEqual(request.or_group_id, port_prop.prop_id)
    self.assertEqual(request.eformat.duration, port_prop.times[0].duration)
    self.assertEqual(request.expire_dt, port_prop.times[0].expire_date)
    self.assertEqual(request.user, port_prop.user)
    
    

class TestAddRequest(unittest.TestCase):
  def startUp(self):
    ri.repo = Mock()
  
  def test_return_prop_id(self):
    port_prop = Proposal()
    prop_id = ri._add_request(USER2, port_prop)
    self.assertTrue(prop_id)

  def tearDown(self):
    ri.reset_repo()
