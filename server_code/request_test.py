import unittest
from unittest.mock import Mock
from datetime import datetime
from .misc_server_test import ADMIN, USER2
from empathy_chat import request_interactor as ri
from empathy_chat import request_gateway as rg
from empathy_chat.portable import Proposal, ProposalTime
import empathy_chat.portable as port
from empathy_chat import server_misc as sm


poptibo_id = USER2.get_id()


class TestNewRequest(unittest.TestCase):
  def test_new_single_later_request(self):
    u = sm.get_port_user(USER2, distance=0, simple=True)
    port_prop = Proposal(user=u, min_size=3, max_size=10, 
                         eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
                         times=[ProposalTime()])
    requests = tuple(ri._new_requests(poptibo_id, port_prop))
    request = requests[0]
    # self.assertEqual(request.request_id, port_prop.times[0].time_id)
    # self.assertEqual(request.or_group_id, port_prop.prop_id)
    self.assertFalse(request.request_id)
    self.assertTrue(request.or_group_id)
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
    self.assertEqual(request.current, True)
    
  def test_new_multiple_later_requests(self):
    u = sm.get_port_user(USER2, distance=1, simple=True)
    # start_1 = h.now() if self.item['start_now'] else self.item['start_date']
    #   if self.item['cancel_buffer'] == 0:
    #     cancel_buffer = t.CANCEL_DEFAULT_MINUTES
    #   else:
    #     cancel_buffer = self.item['cancel_buffer']
    #   self.item['alt'] = [{'start_date': (start_1 + t.DEFAULT_NEXT_DELTA)
    time1 = ProposalTime()
    start_1 = sm.now() if time1.start_now else time1.start_date
    time2 = ProposalTime(start_date=start_1 + port.DEFAULT_NEXT_DELTA)
    port_prop = Proposal(user=u, min_size=3, max_size=10, 
                         eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
                         times=[time1, time2])
    requests = tuple(ri._new_requests(poptibo_id, port_prop))
    for i, request in enumerate(requests):
      # self.assertEqual(request.request_id, port_prop.times[i].time_id)
      # self.assertEqual(request.or_group_id, port_prop.prop_id)
      self.assertFalse(request.request_id)
      self.assertTrue(request.or_group_id)
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


# def _mock_save_requests(requests):
#   for r in requests:
#     r.or_group_id = 11

class TestAddRequest(unittest.TestCase):
  def setUp(self):
    ri.repo = Mock()
    # ri.repo.save_requests = _mock_save_requests
  
  def test_return_prop_id(self):
    port_prop = Proposal()
    prop_id = ri._add_request(USER2, port_prop)
    self.assertTrue(prop_id)
    ri.repo.RequestRecord.assert_called_once()

  def tearDown(self):
    ri.reset_repo()


# class TestRequestRecord(unittest.TestCase):
#   def test_save_request(self):
#     u = sm.get_port_user(USER2, distance=1, simple=True)
#     port_prop = Proposal(user=u, min_size=3, max_size=10, 
#                          eligible=2, eligible_users=[sm.get_port_user(ADMIN, distance=1, simple=True)], eligible_groups=[], eligible_starred=True,
#                          times=[ProposalTime(start_date=datetime.now(), duration=15, expire_date=datetime.now())])
#     request = next(ri._new_requests(USER2, port_prop))
#     request_record = rg.RequestRecord(request)
#     self.assertFalse(request_record.record_id)
#     request_record.save()
#     self.assertTrue(request_record.record_id)
    