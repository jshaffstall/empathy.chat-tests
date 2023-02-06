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
prop_u2_3to10_in1hr = Proposal(
  user=u, min_size=3, max_size=10, 
  eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
  times=[time1],
)
time2 = ProposalTime(start_date=time1.start_date + port.DEFAULT_NEXT_DELTA)
prop_u2_2to3_in1hr_in2hr = Proposal(
  user=u, min_size=2, max_size=3,
  eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
  times=[time1, time2],
)
prop_u2_2to3_now = Proposal(user=u, min_size=2, max_size=3,
                         eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
                         times=[ProposalTime(start_now=True)])

uA = sm.get_port_user(ADMIN, distance=0, simple=True)
prop_uA_2to2_in1hr = Proposal(
  user=uA, min_size=2, max_size=2,
  eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
  times=[time1],
)
prop_uA_2to3_now = Proposal(
  user=uA, min_size=2, max_size=3,
  eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
  times=[ProposalTime(start_now=True)],
)
prop_uA_2to2_in1hr_size3 = Proposal(
  user=uA, min_size=2, max_size=3,
  eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
  times=[time1],
)

prop_u3_3to10_in1hr = Proposal(
  user=sm.get_port_user(USER3, distance=0, simple=True), min_size=3, max_size=10,
  eligible=2, eligible_users=["u1"], eligible_groups=["g1"], eligible_starred=True,
  times=[time1],
)


class TestNewRequests(unittest.TestCase):
  def test_new_single_later_request(self):
    prop = prop_u2_3to10_in1hr
    requests = tuple(rs.prop_to_requests(prop))
    request = requests[0]
    # self.assertEqual(request.request_id, port_prop.times[0].time_id)
    # self.assertEqual(request.or_group_id, port_prop.prop_id)
    self.assertFalse(request.request_id)
    self.assertTrue(request.or_group_id)
    self.assertEqual(request.eformat.duration, prop.times[0].duration)
    self.assertEqual(request.expire_dt, prop.times[0].expire_date)
    self.assertEqual(request.user, prop.user)
    self.assertEqual(request.start_dt, prop.times[0].start_date)
    self.assertEqual(request.create_dt, request.edit_dt)
    self.assertEqual(request.min_size, prop.min_size)
    self.assertEqual(request.max_size, prop.max_size)
    self.assertEqual(request.eligible, prop.eligible)
    self.assertEqual(request.eligible_users, prop.eligible_users)
    self.assertEqual(request.eligible_groups, prop.eligible_groups)
    self.assertEqual(request.eligible_starred, prop.eligible_starred)
    self.assertEqual(request.current, True)

  def test_new_single_now_request(self):
    prop = prop_u2_2to3_now
    requests = tuple(rs.prop_to_requests(prop))
    request = requests[0]
    # self.assertEqual(request.request_id, port_prop.times[0].time_id)
    # self.assertEqual(request.or_group_id, port_prop.prop_id)
    self.assertFalse(request.request_id)
    self.assertTrue(request.or_group_id)
    self.assertEqual(request.eformat.duration, prop.times[0].duration)
    self.assertEqual(request.expire_dt, request.start_dt + timedelta(seconds=p.WAIT_SECONDS))
    self.assertEqual(request.user, prop.user)
    self.assertTrue(request.start_dt <= sm.now())
    self.assertEqual(request.create_dt, request.edit_dt)
    self.assertEqual(request.min_size, prop.min_size)
    self.assertEqual(request.max_size, prop.max_size)
    self.assertEqual(request.eligible, prop.eligible)
    self.assertEqual(request.eligible_users, prop.eligible_users)
    self.assertEqual(request.eligible_groups, prop.eligible_groups)
    self.assertEqual(request.eligible_starred, prop.eligible_starred)
    self.assertEqual(request.current, True)
    
  def test_new_multiple_later_requests(self):
    requests = tuple(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr))
    for i, request in enumerate(requests):
      # self.assertEqual(request.request_id, port_prop.times[i].time_id)
      # self.assertEqual(request.or_group_id, port_prop.prop_id)
      self.assertFalse(request.request_id)
      self.assertTrue(request.or_group_id)
      self.assertEqual(request.eformat.duration, prop_u2_2to3_in1hr_in2hr.times[i].duration)
      self.assertEqual(request.expire_dt, prop_u2_2to3_in1hr_in2hr.times[i].expire_date)
      self.assertEqual(request.user, prop_u2_2to3_in1hr_in2hr.user)
      self.assertEqual(request.start_dt, prop_u2_2to3_in1hr_in2hr.times[i].start_date)
      self.assertEqual(request.create_dt, request.edit_dt)
      self.assertEqual(request.min_size, prop_u2_2to3_in1hr_in2hr.min_size)
      self.assertEqual(request.max_size, prop_u2_2to3_in1hr_in2hr.max_size)
      self.assertEqual(request.eligible, prop_u2_2to3_in1hr_in2hr.eligible)
      self.assertEqual(request.eligible_users, prop_u2_2to3_in1hr_in2hr.eligible_users)
      self.assertEqual(request.eligible_groups, prop_u2_2to3_in1hr_in2hr.eligible_groups)
      self.assertEqual(request.eligible_starred, prop_u2_2to3_in1hr_in2hr.eligible_starred)
      self.assertEqual(request.current, True)


class TestHaveConflicts(unittest.TestCase):
  def test_new_single_later_request_only_no_conflicts(self):
    requests = tuple(rs.prop_to_requests(prop_u2_3to10_in1hr))
    self.assertFalse(rs.have_conflicts(requests))

  def test_new_single_later_request_conflict(self):
    requests = list(rs.prop_to_requests(prop_u2_3to10_in1hr))
    requests.extend(rs.prop_to_requests(prop_u2_3to10_in1hr))
    self.assertTrue(rs.have_conflicts(requests))

  def test_new_multiple_later_requests_conflict(self):
    requests = list(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr))
    requests.extend(rs.prop_to_requests(prop_u2_3to10_in1hr))
    self.assertTrue(rs.have_conflicts(requests))

    requests = list(rs.prop_to_requests(prop_u2_3to10_in1hr))
    requests.extend(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr))
    self.assertTrue(rs.have_conflicts(requests))

  def test_new_multiple_requests_no_conflict(self):
    requests = list(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr))
    requests.extend(rs.prop_to_requests(prop_u2_2to3_now))
    self.assertFalse(rs.have_conflicts(requests))

    requests = list(rs.prop_to_requests(prop_u2_2to3_now))
    requests.extend(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr))
    self.assertFalse(rs.have_conflicts(requests))

  def test_new_single_later_request_only_no_conflicts(self):
    requests = tuple(rs.prop_to_requests(prop_u2_3to10_in1hr))
    self.assertFalse(rs.have_conflicts(requests))


class TestPotentialMatches(unittest.TestCase):
  def test_new_later_requests_no_match(self):
    new_requests = tuple(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr))
    o_requests = tuple(rs.prop_to_requests(prop_uA_2to3_now))
    self.assertFalse(rs.exchange_formed(new_requests, o_requests))

    new_requests = tuple(rs.prop_to_requests(prop_u2_3to10_in1hr))
    o_requests = tuple(rs.prop_to_requests(prop_uA_2to2_in1hr))
    self.assertFalse(rs.exchange_formed(new_requests, o_requests))

  def test_new_later_requests_match(self):
    new_requests = tuple(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr))
    o_requests = tuple(rs.prop_to_requests(prop_uA_2to2_in1hr))
    self.assertEqual(rs.exchange_formed(new_requests, o_requests),
                     rs.ExchangeProspect({new_requests[0], o_requests[0]}))

    new_requests = tuple(rs.prop_to_requests(prop_u2_3to10_in1hr))
    o_requests = (tuple(rs.prop_to_requests(prop_uA_2to2_in1hr))
                  + tuple(rs.prop_to_requests(prop_u3_3to10_in1hr)))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertIn(rs.ExchangeProspect({new_requests[0], o_requests[1]}),
                  potential_matches)
    self.assertEqual(len(potential_matches), 1)
    self.assertFalse(rs.exchange_formed(new_requests, o_requests))

  def test_new_later_requests_size3_match(self):
    new_requests = tuple(rs.prop_to_requests(prop_u2_3to10_in1hr))
    o_requests = (tuple(rs.prop_to_requests(prop_uA_2to2_in1hr_size3))
                  + tuple(rs.prop_to_requests(prop_u3_3to10_in1hr)))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertEqual(len(potential_matches), 3)
    self.assertEqual(rs.exchange_formed(new_requests, o_requests),
                     rs.ExchangeProspect({new_requests[0], o_requests[0], o_requests[1]}))

    new_requests = tuple(rs.prop_to_requests(prop_u2_3to10_in1hr))
    o_requests = (tuple(rs.prop_to_requests(prop_uA_2to2_in1hr_size3))
                  + tuple(rs.prop_to_requests(prop_u3_3to10_in1hr))
                  + tuple(rs.prop_to_requests(prop_uA_2to2_in1hr)))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertEqual(len(potential_matches), 3)
    self.assertEqual(rs.exchange_formed(new_requests, o_requests),
                     rs.ExchangeProspect({new_requests[0], o_requests[0], o_requests[1]}))

    new_requests = tuple(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr))
    o_requests = (tuple(rs.prop_to_requests(prop_uA_2to2_in1hr_size3))
                  + tuple(rs.prop_to_requests(prop_u3_3to10_in1hr)))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertEqual(len(potential_matches), 3)
    self.assertEqual(rs.exchange_formed(new_requests, o_requests),
                     rs.ExchangeProspect({new_requests[0], o_requests[0], o_requests[1]}))

    new_requests = tuple(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr))
    o_requests = (tuple(rs.prop_to_requests(prop_uA_2to2_in1hr_size3))
                  + tuple(rs.prop_to_requests(prop_u3_3to10_in1hr))
                  + tuple(rs.prop_to_requests(prop_uA_2to2_in1hr)))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertEqual(len(potential_matches), 4)
    self.assertEqual(rs.exchange_formed(new_requests, o_requests),
                     rs.ExchangeProspect({new_requests[0], o_requests[0], o_requests[1]}))

  def test_new_later_requests_no_size3_match(self):
    new_requests = tuple(rs.prop_to_requests(prop_uA_2to2_in1hr))
    o_requests = (tuple(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr))
                  + tuple(rs.prop_to_requests(prop_u3_3to10_in1hr)))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertNotIn({new_requests[0], o_requests[0], o_requests[1]},
                     potential_matches)
    self.assertEqual(len(potential_matches), 1)
    self.assertEqual(rs.exchange_formed(new_requests, o_requests),
                     rs.ExchangeProspect({new_requests[0], o_requests[0]}))
    
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
#     request = next(rs.prop_to_requests(USER2, port_prop))
#     request_record = rg.RequestRecord(request)
#     self.assertFalse(request_record.record_id)
#     request_record.save()
#     self.assertTrue(request_record.record_id)
    