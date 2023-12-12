import unittest
from unittest.mock import Mock
from anvil.tables import app_tables
import anvil.tables.query as q
import anvil.tables
from .misc_server_test import ADMIN, USER2, USER3
from . import request_test as rt
from empathy_chat import request_interactor as ri
from empathy_chat import request_gateway as rg
from empathy_chat import requests as rs
from empathy_chat import server_misc as sm
from empathy_chat import portable as port
from empathy_chat import notifies as n
from empathy_chat import invites


def add_request(user, port_prop):
  requests = rs.Requests(rs.prop_to_requests(port_prop, user_id=user.get_id()))
  return ri.add_requests(user, requests)


def edit_request(user, port_prop):
  requests = rs.Requests(rs.prop_to_requests(port_prop, user_id=user.get_id()))
  return ri.edit_requests(user, requests)


class TestPropRequestProp(unittest.TestCase):
  def test_new_single_later_request(self):
    prop = rt.prop_u2_3to10_in1hr
    prop.eligible_invites = invites.Invite(rel_to_inviter="father-in-law", link_key="123456")
    requests = tuple(rs.prop_to_requests(prop))
    _prop = list(ri.requests_to_props(requests, USER2))[0]
    self.assertTrue(_prop.prop_id)
    _prop.prop_id = None
    # for proptime in _prop.times:
    #   proptime.proptime_id = None
    # _prop.eligible_users = [port.User(user_id=u.user_id) for u in _prop.eligible_users]
    for key in _prop.__dict__:
      if key == 'times':
        for i, time in enumerate(_prop.times):
          for tkey in time.__dict__:
            self.assertEqual(getattr(time, tkey), getattr(prop.times[i], tkey))
      elif key == 'eligible_invites':
        self.assertEqual(str(getattr(_prop, key)), str(getattr(prop, key)))
      else:
        self.assertEqual(getattr(_prop, key), getattr(prop, key))
    # self.assertEqual(_prop, prop)
    prop.eligible_invites = [] # reseting

  def test_new_single_now_request(self):
    prop = rt.prop_u2_2to3_now
    requests = tuple(rs.prop_to_requests(prop))
    _prop = list(ri.requests_to_props(requests, USER2))[0]
    self.assertTrue(_prop.prop_id)
    _prop.prop_id = None
    # for proptime in _prop.times:
    #   proptime.proptime_id = None
    # _prop.eligible_users = [port.User(user_id=u.user_id) for u in _prop.eligible_users]
    for key in _prop.__dict__:
      if key == 'times':
        for i, time in enumerate(_prop.times):
          for tkey in time.__dict__:
            if tkey == 'expire_date':
              self.assertTrue(getattr(time, tkey))
              self.assertFalse(getattr(prop.times[i], tkey))
            else:
              self.assertEqual(getattr(time, tkey), getattr(prop.times[i], tkey))
      else:
        self.assertEqual(getattr(_prop, key), getattr(prop, key))
    # self.assertEqual(_prop, prop)
    
  def test_new_multiple_later_requests(self):
    prop = rt.prop_u2_2to3_in1hr_in2hr
    requests = tuple(rs.prop_to_requests(prop))
    _prop = list(ri.requests_to_props(requests, USER2))[0]
    self.assertTrue(_prop.prop_id)
    _prop.prop_id = None
    # for proptime in _prop.times:
    #   proptime.proptime_id = None
    # _prop.eligible_users = [port.User(user_id=u.user_id) for u in _prop.eligible_users]
    for key in _prop.__dict__:
      if key == 'times':
        for i, time in enumerate(_prop.times):
          for tkey in time.__dict__:
            self.assertEqual(getattr(time, tkey), getattr(prop.times[i], tkey))
      else:
        self.assertEqual(getattr(_prop, key), getattr(prop, key))
    # self.assertEqual(_prop, prop)


class TestRequestGateway(unittest.TestCase):
  def setUp(self):
    self.request_records_saved = []
    self.are_rows_to_delete = False
    self.test_start_dt = sm.now()
    self._email_send = n.email_send
    n.email_send = Mock()
    self._send_sms = n.send_sms
    n.send_sms = Mock()
    self._notify_edit = ri.RequestManager.notify_edit
    ri.RequestManager.notify_edit = Mock()
  
  def test_request_record_save(self):
    prop = rt.prop_u2_3to10_in1hr
    request = next(rs.prop_to_requests(prop, with_users=[rt.admin_id]))
    request_record = rg.RequestRecord(request)
    self.assertFalse(request_record.record_id)
    self.request_records_saved.append(request_record)
    request_record.save()
    self.assertTrue(request_record.record_id)
    saved_requests = [r for r in rg.requests_by_user(USER2) 
                      if r.request_id == request_record.record_id]
    self.assertEqual(len(saved_requests), 1)
    request = saved_requests[0]
    self.assertTrue(request.or_group_id)
    self.assertEqual(request.exchange_format.duration, prop.times[0].duration)
    self.assertEqual(request.expire_dt, prop.times[0].expire_date)
    self.assertEqual(request.user, prop.user.user_id)
    self.assertEqual(request.start_dt, prop.times[0].start_date)
    self.assertEqual(request.create_dt, request.edit_dt)
    self.assertEqual(request.min_size, prop.min_size)
    self.assertEqual(request.max_size, prop.max_size)
    self.assertEqual(request.eligible_all, prop.eligible_all)
    self.assertEqual(request.eligible, prop.eligible)
    self.assertEqual(request.eligible_users, prop.eligible_users)
    self.assertEqual(request.eligible_groups, prop.eligible_groups)
    self.assertEqual(request.eligible_starred, prop.eligible_starred)
    self.assertEqual(request.pref_order, 0)
    self.assertEqual(request.current, True)
    self.assertEqual(tuple(request.with_users), (rt.admin_id,))

  def test_cancel_request(self):
    self.are_rows_to_delete = True
    or_group_id0 = add_request(USER3, rt.prop_u3_3to10_in1hr)
    requests = list(rg.current_requests(records=False))
    self.assertEqual(len(requests), 1)
    ri.cancel_request(USER3, requests[0].request_id)
    edited_requests = list(rg.current_requests(records=False))
    self.assertEqual(len(edited_requests), 0)
  
  def test_edit_request(self):
    self.are_rows_to_delete = True
    or_group_id0 = add_request(USER3, rt.prop_u3_3to10_in1hr)
    requests = list(rg.current_requests(records=False))
    self.assertEqual(len(requests), 1)
    self.assertEqual(requests[0].max_size, 10)
    request_id0 = requests[0].request_id
    self.assertTrue(request_id0)
    requests[0].max_size = 3
    _prop = list(ri.requests_to_props(requests, USER3))[0]
    or_group_id1 = edit_request(USER3, _prop)
    edited_requests = list(rg.current_requests(records=False))
    request_id1 = edited_requests[0].request_id
    self.assertEqual(or_group_id0, or_group_id1)
    self.assertEqual(request_id0, request_id1)
    self.assertEqual(len(edited_requests), 1)
    self.assertEqual(edited_requests[0].or_group_id, or_group_id1)
    self.assertEqual(edited_requests[0].max_size, 3)

  def test_edit_request_change_eligible(self):
    self.are_rows_to_delete = True
    or_group_id0 = add_request(USER3, rt.prop_u3_3to10_in1hr)
    requests = list(rg.current_requests(records=False))
    self.assertEqual(len(requests), 1)
    request_id0 = requests[0].request_id
    self.assertTrue(request_id0)
    requests[0].eligible = 0
    requests[0].eligible_users = [rt.admin_id]
    requests[0].exchange_format.duration = 15
    _prop = list(ri.requests_to_props(requests, USER3))[0]
    or_group_id1 = edit_request(USER3, _prop)
    edited_requests = list(rg.current_requests(records=False))
    request_id1 = edited_requests[0].request_id
    self.assertEqual(or_group_id0, or_group_id1)
    self.assertEqual(request_id0, request_id1)
    self.assertEqual(len(edited_requests), 1)
    self.assertEqual(edited_requests[0].or_group_id, or_group_id1)
  
  def test_visible_requests(self):
    self.are_rows_to_delete = True
    or_group_id0 = add_request(USER3, rt.prop_u3_3to10_in1hr)
    or_group_id1 = add_request(ADMIN, rt.prop_uA_2to2_in1hr)
    visible_requests = ri.current_visible_requests(USER2, list(rg.current_requests(records=True)))
    self.assertEqual(len(visible_requests), 1)
    self.assertEqual(visible_requests[0].or_group_id, or_group_id1)

  def test_visible_request_with(self):
    self.are_rows_to_delete = True
    or_group_id0 = add_request(USER3, rt.prop_u3_3to10_in1hr)
    request = next(rs.prop_to_requests(rt.prop_uA_2to2_in1hr, with_users=[rt.u2.user_id]))
    request_record = rg.RequestRecord(request)
    request_record.save()
    visible_requests = ri.current_visible_requests(USER2, list(rg.current_requests(records=True)))
    self.assertEqual(len(visible_requests), 1)
    self.assertEqual(visible_requests[0].or_group_id, request.or_group_id)

  def test_not_visible_request_with(self):
    self.are_rows_to_delete = True
    or_group_id0 = add_request(USER3, rt.prop_u3_3to10_in1hr)
    request = next(rs.prop_to_requests(rt.prop_uA_2to2_in1hr, with_users=[rt.u3.user_id]))
    request_record = rg.RequestRecord(request)
    request_record.save()
    visible_requests = ri.current_visible_requests(USER2, list(rg.current_requests(records=True)))
    self.assertFalse(visible_requests)
  
  def tearDown(self):
    n.email_send = self._email_send
    n.send_sms = self._send_sms
    ri.RequestManager.notify_edit = self._notify_edit
    if self.are_rows_to_delete:
      rows_created = app_tables.requests.search(rg.requests_fetch, create_dt=q.greater_than_or_equal_to(self.test_start_dt))
    with anvil.tables.batch_delete:
      for rr in self.request_records_saved:
        rr._row.delete()
      if self.are_rows_to_delete:
        for row in rows_created:
          row.delete()


class TestExchangeProspectMisc(unittest.TestCase):
  def test_exchange_prospects_to_props(self):
    new_requests = tuple(rs.prop_to_requests(rt.prop_u2_2to3_in1hr_in2hr, with_users=[rt.admin_id]))
    o_requests = tuple(rs.prop_to_requests(rt.prop_uA_2to2_in1hr, with_users=[rt.user2_id]))
    ep = rs.ExchangeProspect({new_requests[0], o_requests[0]}, temp=True)
    props = list(ri.eps_to_props([ep], USER2))
    self.assertEqual(props[0].user.user_id, rt.user2_id)
