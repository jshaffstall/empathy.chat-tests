import unittest
from unittest.mock import Mock
from .misc_server_test import ADMIN, USER2
from empathy_chat import request_interactor as ri
from empathy_chat.portable import Proposal, ProposalTime
from empathy_chat import server_misc as sm


poptibo_id = USER2.get_id()


class TestNewRequest(unittest.TestCase):
  def test_add_single_later_request(self):
    u = sm.get_port_user(USER2, distance=1, simple=True)
    port_prop = Proposal(user=u, min_size=3, max_size=10, 
                         eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
                         times=[ProposalTime(start_date=5, duration=15, expire_date=20)])
    request = ri._new_request(poptibo_id, port_prop)
    self.assertEqual(request.request_id, port_prop.times[0].time_id)
    self.assertEqual(request.or_group_id, port_prop.prop_id)
    self.assertEqual(request.eformat.duration, port_prop.times[0].duration)
    self.assertEqual(request.expire_dt, port_prop.times[0].expire_date)
    self.assertEqual(request.user, port_prop.user)
    self.assertEqual(request.start_dt, port_prop.times[0].start_date)
    # self.assertEqual(request.create_dt, port_prop.times[0]
    # self.assertEqual(request.edit_dt, port_prop.times[0]
    self.assertEqual(request.min_size, port_prop.min_size)
    self.assertEqual(request.max_size, port_prop.max_size)
    self.assertEqual(request.eligible, port_prop.eligible)
    self.assertEqual(request.eligible_users, port_prop.eligible_users)
    self.assertEqual(request.eligible_groups, port_prop.eligible_groups)
    self.assertEqual(request.eligible_starred, port_prop.eligible_starred)
    
    

class TestAddRequest(unittest.TestCase):
  def startUp(self):
    ri.repo = Mock()
  
  def test_return_prop_id(self):
    port_prop = Proposal()
    prop_id = ri._add_request(USER2, port_prop)
    self.assertTrue(prop_id)

  def tearDown(self):
    ri.reset_repo()
