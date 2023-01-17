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
    requests = tuple(ri._new_requests(poptibo_id, port_prop))
    request = requests[0]
    self.assertEqual(request.request_id, port_prop.times[0].time_id)
    self.assertEqual(request.or_group_id, port_prop.prop_id)
    self.assertEqual(request.eformat.duration, port_prop.times[0].duration)
    self.assertEqual(request.expire_dt, port_prop.times[0].expire_date)
    self.assertEqual(request.user, port_prop.user)
    self.assertEqual(request.start_dt, port_prop.times[0].start_date)
    self.assertEqual(request.create_dt, request.edit_dt)
    self.assertEqual(request.min_size, port_prop.min_size)
    self.assertEqual(request.max_size, port_prop.max_size)
    self.assertEqual(request.eligible, port_prop.eligible)
    self.assertEqual(request.eligible_users, port_prop.eligible_users)
    self.assertEqual(request.eligible_groups, port_prop.eligible_groups)
    self.assertEqual(request.eligible_starred, port_prop.eligible_starred)
    
  def test_add_multiple_later_request(self):
    u = sm.get_port_user(USER2, distance=1, simple=True)
    port_prop = Proposal(user=u, min_size=3, max_size=10, 
                         eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
                         times=[ProposalTime(start_date=0, duration=15, expire_date=20),
                                ProposalTime(start_date=1, duration=15, expire_date=20)])
    requests = tuple(ri._new_requests(poptibo_id, port_prop))
    for i, request in enumerate(requests):
      self.assertEqual(request.request_id, port_prop.times[i].time_id)
      self.assertEqual(request.or_group_id, port_prop.prop_id)
      self.assertEqual(request.eformat.duration, port_prop.times[i].duration)
      self.assertEqual(request.expire_dt, port_prop.times[i].expire_date)
      self.assertEqual(request.user, port_prop.user)
      self.assertEqual(request.start_dt, port_prop.times[i].start_date)
      self.assertEqual(request.create_dt, request.edit_dt)
      self.assertEqual(request.min_size, port_prop.min_size)
      self.assertEqual(request.max_size, port_prop.max_size)
      self.assertEqual(request.eligible, port_prop.eligible)
      self.assertEqual(request.eligible_users, port_prop.eligible_users)
      self.assertEqual(request.eligible_groups, port_prop.eligible_groups)
      self.assertEqual(request.eligible_starred, port_prop.eligible_starred)
      self.assertEqual(request.current, True)    


def _mock_save_requests(requests):
  for r in requests:
    r.or_group_id = 11

class TestAddRequest(unittest.TestCase):
  def setUp(self):
    ri.repo = Mock()
    ri.repo.save_requests = _mock_save_requests
  
  def test_return_prop_id(self):
    port_prop = Proposal()
    prop_id = ri._add_request(USER2, port_prop)
    self.assertTrue(prop_id, 11)

  def tearDown(self):
    ri.reset_repo()
