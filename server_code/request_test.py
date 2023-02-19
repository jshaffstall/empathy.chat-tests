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
from empathy_chat import groups
from anvil.tables import app_tables


admin_id = ADMIN.get_id()
user2_id = USER2.get_id()
user3_id = USER3.get_id()

group0_row = app_tables.groups.search()[0]
group0 = groups.Group(group0_row['name'], group_id=group0_row.get_id())
u2 = sm.get_port_user(USER2, distance=0, simple=True)
time1 = ProposalTime()
prop_u2_3to10_in1hr = Proposal(
  user=u2, min_size=3, max_size=10, 
  eligible=2, eligible_users=[port.User(user_id=user3_id)], eligible_groups=[group0], eligible_starred=True,
  times=[time1],
)
time2 = ProposalTime(start_date=time1.start_date + port.DEFAULT_NEXT_DELTA)
prop_u2_2to3_in1hr_in2hr = Proposal(
  user=u2, min_size=2, max_size=3,
  eligible=2, eligible_users=[port.User(user_id=user3_id)], eligible_groups=[group0], eligible_starred=True,
  times=[time1, time2],
)
prop_u2_2to3_now = Proposal(
  user=u2, min_size=2, max_size=3,
  eligible=2, eligible_users=[port.User(user_id=user3_id)], eligible_groups=[group0], eligible_starred=True,
  times=[ProposalTime(start_now=True)]
)

uA = sm.get_port_user(ADMIN, distance=0, simple=True)
prop_uA_3to10_in1hr = Proposal(
  user=uA, min_size=3, max_size=10,
  eligible=2, eligible_users=[u2], eligible_groups=[], eligible_starred=True,
  times=[ProposalTime(duration=15)]
)
prop_uA_2to2_in1hr = Proposal(
  user=uA, min_size=2, max_size=2,
  eligible=2, eligible_users=[u2], eligible_groups=[], eligible_starred=True,
  times=[time1],
)
prop_uA_2to3_now = Proposal(
  user=uA, min_size=2, max_size=3,
  eligible=2, eligible_users=[], eligible_groups=[], eligible_starred=True,
  times=[ProposalTime(start_now=True)],
)
prop_uA_2to2_in1hr_size3 = Proposal(
  user=uA, min_size=2, max_size=3,
  eligible=2, eligible_users=[], eligible_groups=[], eligible_starred=True,
  times=[time1],
)

u3 = sm.get_port_user(USER3, distance=0, simple=True)
prop_u3_3to10_in1hr = Proposal(
  user=u3, min_size=3, max_size=10,
  eligible=2, eligible_users=[], eligible_groups=[], eligible_starred=True,
  times=[time1],
)


class TestNewRequests(unittest.TestCase):
  def test_new_single_later_request(self):
    prop = prop_u2_3to10_in1hr
    requests = tuple(rs.prop_to_requests(prop, with_users=[admin_id]))
    request = requests[0]
    # self.assertEqual(request.request_id, port_prop.times[0].time_id)
    # self.assertEqual(request.or_group_id, port_prop.prop_id)
    self.assertFalse(request.request_id)
    self.assertTrue(request.or_group_id)
    self.assertEqual(request.eformat.duration, prop.times[0].duration)
    self.assertEqual(request.expire_dt, prop.times[0].expire_date)
    self.assertEqual(request.user, prop.user.user_id)
    self.assertEqual(request.start_dt, prop.times[0].start_date)
    self.assertEqual(request.create_dt, request.edit_dt)
    self.assertEqual(request.min_size, prop.min_size)
    self.assertEqual(request.max_size, prop.max_size)
    self.assertEqual(request.eligible, prop.eligible)
    self.assertEqual(request.eligible_users, [pu.user_id for pu in prop.eligible_users])
    self.assertEqual(request.eligible_groups, prop.eligible_groups)
    self.assertEqual(request.eligible_starred, prop.eligible_starred)
    self.assertEqual(request.current, True)
    self.assertEqual(tuple(request.with_users), (admin_id,))

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
    self.assertEqual(request.user, prop.user.user_id)
    self.assertTrue(request.start_dt <= sm.now())
    self.assertEqual(request.create_dt, request.edit_dt)
    self.assertEqual(request.min_size, prop.min_size)
    self.assertEqual(request.max_size, prop.max_size)
    self.assertEqual(request.eligible, prop.eligible)
    self.assertEqual(request.eligible_users, [pu.user_id for pu in prop.eligible_users])
    self.assertEqual(request.eligible_groups, prop.eligible_groups)
    self.assertEqual(request.eligible_starred, prop.eligible_starred)
    self.assertEqual(request.current, True)
    
  def test_new_multiple_later_requests(self):
    prop = prop_u2_2to3_in1hr_in2hr
    requests = tuple(rs.prop_to_requests(prop))
    for i, request in enumerate(requests):
      # self.assertEqual(request.request_id, port_prop.times[i].time_id)
      # self.assertEqual(request.or_group_id, port_prop.prop_id)
      self.assertFalse(request.request_id)
      self.assertTrue(request.or_group_id)
      self.assertEqual(request.eformat.duration, prop.times[i].duration)
      self.assertEqual(request.expire_dt, prop.times[i].expire_date)
      self.assertEqual(request.user, prop.user.user_id)
      self.assertEqual(request.start_dt, prop.times[i].start_date)
      self.assertEqual(request.create_dt, request.edit_dt)
      self.assertEqual(request.min_size, prop.min_size)
      self.assertEqual(request.max_size, prop.max_size)
      self.assertEqual(request.eligible, prop.eligible)
      self.assertEqual(request.eligible_users, [pu.user_id for pu in prop.eligible_users])
      self.assertEqual(request.eligible_groups, prop.eligible_groups)
      self.assertEqual(request.eligible_starred, prop.eligible_starred)
      self.assertEqual(request.current, True)
    self.assertTrue(requests[0].pref_order < requests[1].pref_order)


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
    self.assertFalse(rs.exchange_to_save(new_requests, o_requests))

    new_requests = tuple(rs.prop_to_requests(prop_u2_3to10_in1hr))
    o_requests = tuple(rs.prop_to_requests(prop_uA_2to2_in1hr))
    self.assertFalse(rs.exchange_to_save(new_requests, o_requests))

    new_requests = tuple(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr, with_users=[user3_id]))
    o_requests = tuple(rs.prop_to_requests(prop_uA_2to2_in1hr))
    self.assertFalse(rs.exchange_to_save(new_requests, o_requests))
  
  def test_new_later_requests_match(self):
    new_requests = tuple(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr, with_users=[admin_id]))
    o_requests = tuple(rs.prop_to_requests(prop_uA_2to2_in1hr, with_users=[user2_id]))
    ep = rs.ExchangeProspect({new_requests[0], o_requests[0]})
    self.assertEqual(rs.exchange_to_save(new_requests, o_requests), ep)

    new_requests = tuple(rs.prop_to_requests(prop_u2_3to10_in1hr))
    o_requests = (tuple(rs.prop_to_requests(prop_uA_2to2_in1hr))
                  + tuple(rs.prop_to_requests(prop_u3_3to10_in1hr)))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertIn(rs.ExchangeProspect({new_requests[0], o_requests[1]}),
                  potential_matches)
    self.assertEqual(len(potential_matches), 1)
    self.assertFalse(rs.exchange_to_save(new_requests, o_requests))

  def test_new_later_requests_size3_match(self):
    new_requests = tuple(rs.prop_to_requests(prop_u2_3to10_in1hr))
    o_requests = (tuple(rs.prop_to_requests(prop_uA_2to2_in1hr_size3))
                  + tuple(rs.prop_to_requests(prop_u3_3to10_in1hr)))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertEqual(len(potential_matches), 3)
    self.assertEqual(rs.exchange_to_save(new_requests, o_requests),
                     rs.ExchangeProspect({new_requests[0], o_requests[0], o_requests[1]}))

    new_requests = tuple(rs.prop_to_requests(prop_u2_3to10_in1hr))
    o_requests = (tuple(rs.prop_to_requests(prop_uA_2to2_in1hr_size3))
                  + tuple(rs.prop_to_requests(prop_u3_3to10_in1hr))
                  + tuple(rs.prop_to_requests(prop_uA_2to2_in1hr)))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertEqual(len(potential_matches), 3)
    self.assertEqual(rs.exchange_to_save(new_requests, o_requests),
                     rs.ExchangeProspect({new_requests[0], o_requests[0], o_requests[1]}))

    new_requests = tuple(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr))
    o_requests = (tuple(rs.prop_to_requests(prop_uA_2to2_in1hr_size3))
                  + tuple(rs.prop_to_requests(prop_u3_3to10_in1hr)))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertEqual(len(potential_matches), 3)
    self.assertEqual(rs.exchange_to_save(new_requests, o_requests),
                     rs.ExchangeProspect({new_requests[0], o_requests[0], o_requests[1]}))

    new_requests = tuple(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr))
    o_requests = (tuple(rs.prop_to_requests(prop_uA_2to2_in1hr_size3))
                  + tuple(rs.prop_to_requests(prop_u3_3to10_in1hr))
                  + tuple(rs.prop_to_requests(prop_uA_2to2_in1hr)))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertEqual(len(potential_matches), 4)
    self.assertEqual(rs.exchange_to_save(new_requests, o_requests),
                     rs.ExchangeProspect({new_requests[0], o_requests[0], o_requests[1]}))

  def test_new_later_requests_no_size3_match(self):
    new_requests = tuple(rs.prop_to_requests(prop_uA_2to2_in1hr))
    o_requests = (tuple(rs.prop_to_requests(prop_u2_2to3_in1hr_in2hr))
                  + tuple(rs.prop_to_requests(prop_u3_3to10_in1hr)))
    potential_matches = rs.potential_matches(new_requests, o_requests)
    self.assertNotIn({new_requests[0], o_requests[0], o_requests[1]},
                     potential_matches)
    self.assertEqual(len(potential_matches), 1)
    self.assertEqual(rs.exchange_to_save(new_requests, o_requests),
                     rs.ExchangeProspect({new_requests[0], o_requests[0]}))
    
# def _mock_save_requests(requests):
#   for r in requests:
#     r.or_group_id = 11


class TestAddRequest(unittest.TestCase):
  def setUp(self):
    ri.repo = Mock()
    # ri.repo.save_requests = _mock_save_requests
    ri.repo.requests_by_user = lambda x: []
    ri.repo.partially_matching_requests = lambda x, y, records=False: []
    def cr(records=False):
      return []
    ri.repo.current_requests = cr
  
  def test_return_prop_id(self):
    port_prop = Proposal(user=u2)
    prop_id = ri._add_request(USER2, port_prop)
    self.assertTrue(prop_id)
    ri.repo.RequestRecord.assert_called_once()

  def tearDown(self):
    ri.reset_repo()
