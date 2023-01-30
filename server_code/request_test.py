import unittest
from unittest.mock import Mock
from datetime import datetime, timedelta
from .misc_server_test import ADMIN, USER2, USER3
from empathy_chat import request_interactor as ri
from empathy_chat import request_gateway as rg
from empathy_chat.portable import Proposal, ProposalTime
import empathy_chat.portable as port
import empathy_chat.parameters as p
from empathy_chat import server_misc as sm
from empathy_chat import requests as rs


admin_id = ADMIN.get_id()
user2_id = USER2.get_id()
user3_id = USER3.get_id()

u = sm.get_port_user(USER2, distance=0, simple=True)
time1 = ProposalTime()
port_prop1 = Proposal(user=u, min_size=3, max_size=10, 
                      eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
                      times=[time1])
start_1 = sm.now() if time1.start_now else time1.start_date
time2 = ProposalTime(start_date=start_1 + port.DEFAULT_NEXT_DELTA)
port_prop2 = Proposal(user=u, min_size=2, max_size=3, 
                      eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
                      times=[time1, time2])
port_prop_now = Proposal(user=u, min_size=2, max_size=3,
                         eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
                         times=[ProposalTime(start_now=True)])

o_port_prop1 = Proposal(user=sm.get_port_user(ADMIN, distance=0, simple=True), min_size=2, max_size=2,
                   eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
                   times=[time1])
o_port_prop_now = Proposal(user=sm.get_port_user(ADMIN, distance=0, simple=True), min_size=2, max_size=3,
                         eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
                         times=[ProposalTime(start_now=True)])
o_port_prop1_size3 = Proposal(user=sm.get_port_user(ADMIN, distance=0, simple=True), min_size=2, max_size=2,
                   eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
                   times=[time1])

o3_port_prop1 = Proposal(user=sm.get_port_user(USER3, distance=0, simple=True), min_size=3, max_size=10,
                   eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
                   times=[time1])


class TestNewRequest(unittest.TestCase):
  def test_new_single_later_request(self):
    requests = tuple(ri._new_requests(user2_id, port_prop1))
    request = requests[0]
    # self.assertEqual(request.request_id, port_prop.times[0].time_id)
    # self.assertEqual(request.or_group_id, port_prop.prop_id)
    self.assertFalse(request.request_id)
    self.assertTrue(request.or_group_id)
    self.assertEqual(request.eformat.duration, port_prop1.times[0].duration)
    self.assertEqual(request.expire_dt, port_prop1.times[0].expire_date)
    self.assertEqual(request.user, port_prop1.user)
    self.assertEqual(request.start_dt, port_prop1.times[0].start_date)
    self.assertEqual(request.create_dt, request.edit_dt)
    self.assertEqual(request.min_size, port_prop1.min_size)
    self.assertEqual(request.max_size, port_prop1.max_size)
    self.assertEqual(request.eligible, port_prop1.eligible)
    self.assertEqual(request.eligible_users, port_prop1.eligible_users)
    self.assertEqual(request.eligible_groups, port_prop1.eligible_groups)
    self.assertEqual(request.eligible_starred, port_prop1.eligible_starred)
    self.assertEqual(request.current, True)

  def test_new_single_now_request(self):
    requests = tuple(ri._new_requests(user2_id, port_prop_now))
    request = requests[0]
    # self.assertEqual(request.request_id, port_prop.times[0].time_id)
    # self.assertEqual(request.or_group_id, port_prop.prop_id)
    self.assertFalse(request.request_id)
    self.assertTrue(request.or_group_id)
    self.assertEqual(request.eformat.duration, port_prop_now.times[0].duration)
    self.assertEqual(request.expire_dt, request.start_dt + timedelta(seconds=p.WAIT_SECONDS))
    self.assertEqual(request.user, port_prop_now.user)
    self.assertTrue(request.start_dt <= sm.now())
    self.assertEqual(request.create_dt, request.edit_dt)
    self.assertEqual(request.min_size, port_prop_now.min_size)
    self.assertEqual(request.max_size, port_prop_now.max_size)
    self.assertEqual(request.eligible, port_prop_now.eligible)
    self.assertEqual(request.eligible_users, port_prop_now.eligible_users)
    self.assertEqual(request.eligible_groups, port_prop_now.eligible_groups)
    self.assertEqual(request.eligible_starred, port_prop_now.eligible_starred)
    self.assertEqual(request.current, True)
    
  def test_new_multiple_later_requests(self):
    requests = tuple(ri._new_requests(user2_id, port_prop2))
    for i, request in enumerate(requests):
      # self.assertEqual(request.request_id, port_prop.times[i].time_id)
      # self.assertEqual(request.or_group_id, port_prop.prop_id)
      self.assertFalse(request.request_id)
      self.assertTrue(request.or_group_id)
      self.assertEqual(request.eformat.duration, port_prop2.times[i].duration)
      self.assertEqual(request.expire_dt, port_prop2.times[i].expire_date)
      self.assertEqual(request.user, port_prop2.user)
      self.assertEqual(request.start_dt, port_prop2.times[i].start_date)
      self.assertEqual(request.create_dt, request.edit_dt)
      self.assertEqual(request.min_size, port_prop2.min_size)
      self.assertEqual(request.max_size, port_prop2.max_size)
      self.assertEqual(request.eligible, port_prop2.eligible)
      self.assertEqual(request.eligible_users, port_prop2.eligible_users)
      self.assertEqual(request.eligible_groups, port_prop2.eligible_groups)
      self.assertEqual(request.eligible_starred, port_prop2.eligible_starred)
      self.assertEqual(request.current, True)

  def test_new_single_later_request_only_no_conflicts(self):
    requests = tuple(ri._new_requests(user2_id, port_prop1))
    self.assertFalse(rs.have_conflicts(requests))

  def test_new_single_later_request_conflict(self):
    requests = list(ri._new_requests(user2_id, port_prop1))
    requests.extend(ri._new_requests(user2_id, port_prop1))
    self.assertTrue(rs.have_conflicts(requests))

  def test_new_multiple_later_requests_conflict(self):
    requests = list(ri._new_requests(user2_id, port_prop2))
    requests.extend(ri._new_requests(user2_id, port_prop1))
    self.assertTrue(rs.have_conflicts(requests))

    requests = list(ri._new_requests(user2_id, port_prop1))
    requests.extend(ri._new_requests(user2_id, port_prop2))
    self.assertTrue(rs.have_conflicts(requests))

  def test_new_multiple_requests_no_conflict(self):
    requests = list(ri._new_requests(user2_id, port_prop2))
    requests.extend(ri._new_requests(user2_id, port_prop_now))
    self.assertFalse(rs.have_conflicts(requests))

    requests = list(ri._new_requests(user2_id, port_prop_now))
    requests.extend(ri._new_requests(user2_id, port_prop2))
    self.assertFalse(rs.have_conflicts(requests))

  def test_new_single_later_request_only_no_conflicts(self):
    requests = tuple(ri._new_requests(user2_id, port_prop1))
    self.assertFalse(rs.have_conflicts(requests))

  def test_new_later_requests_no_match(self):
    new_requests = tuple(ri._new_requests(user2_id, port_prop2))
    o_requests = tuple(ri._new_requests(admin_id, o_port_prop_now))
    self.assertFalse(rs.potential_matches(new_requests, o_requests))

    new_requests = tuple(ri._new_requests(user2_id, port_prop1))
    o_requests = tuple(ri._new_requests(admin_id, o_port_prop1))
    self.assertFalse(rs.potential_matches(new_requests, o_requests))

  def test_new_later_requests_match(self):
    new_requests = tuple(ri._new_requests(user2_id, port_prop2))
    o_requests = tuple(ri._new_requests(admin_id, o_port_prop1))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertIn({new_requests[0], o_requests[0]},
                  potential_matches)
    self.assertEqual(len(potential_matches), 1)

    new_requests = tuple(ri._new_requests(user2_id, port_prop1))
    o_requests = (tuple(ri._new_requests(admin_id, o_port_prop1))
                  + tuple(ri._new_requests(user3_id, o3_port_prop1)))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertIn({new_requests[0], o_requests[1]},
                  potential_matches)
    self.assertEqual(len(potential_matches), 1)

  def test_new_later_requests_size3_match(self):
    new_requests = tuple(ri._new_requests(user2_id, port_prop1))
    o_requests = (tuple(ri._new_requests(admin_id, o_port_prop1_size3))
                  + tuple(ri._new_requests(user3_id, o3_port_prop1)))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertIn({new_requests[0], o_requests[0], o_requests[1]},
                  potential_matches)
    self.assertEqual(len(potential_matches), 3)
    
# def _mock_save_requests(requests):
#   for r in requests:
#     r.or_group_id = 11


class TestAddRequest(unittest.TestCase):
  def setUp(self):
    ri.repo = Mock()
    # ri.repo.save_requests = _mock_save_requests
    # ri.repo.requests_by_user = lambda x: []
    ri.repo.current_requests = lambda : []
  
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
    