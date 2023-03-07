import unittest
from unittest.mock import Mock
from anvil.tables import app_tables
import anvil.tables.query as q
from .misc_server_test import ADMIN, USER2, USER3
from . import request_test as rt
from empathy_chat import request_interactor as ri
from empathy_chat import request_gateway as rg
from empathy_chat import requests as rs
from empathy_chat import server_misc as sm
from empathy_chat import portable as port
from empathy_chat import notifies as n


class TestPropRequestProp(unittest.TestCase):
  def test_new_single_later_request(self):
    prop = rt.prop_u2_3to10_in1hr
    requests = tuple(rs.prop_to_requests(prop))
    _prop = list(ri.requests_to_props(requests, USER2))[0]
    self.assertTrue(_prop.prop_id)
    _prop.prop_id = None
    # for proptime in _prop.times:
    #   proptime.proptime_id = None
    _prop.eligible_users = [port.User(user_id=u.user_id) for u in _prop.eligible_users]
    for key in _prop.__dict__:
      if key == 'times':
        for i, time in enumerate(_prop.times):
          for tkey in time.__dict__:
            self.assertEqual(getattr(time, tkey), getattr(prop.times[i], tkey))
      else:
        self.assertEqual(getattr(_prop, key), getattr(prop, key))
    # self.assertEqual(_prop, prop)

  def test_new_single_now_request(self):
    prop = rt.prop_u2_2to3_now
    requests = tuple(rs.prop_to_requests(prop))
    _prop = list(ri.requests_to_props(requests, USER2))[0]
    self.assertTrue(_prop.prop_id)
    _prop.prop_id = None
    # for proptime in _prop.times:
    #   proptime.proptime_id = None
    _prop.eligible_users = [port.User(user_id=u.user_id) for u in _prop.eligible_users]
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
    _prop.eligible_users = [port.User(user_id=u.user_id) for u in _prop.eligible_users]
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
    self.request_records_created = []
    self.request_rows_created = []
    self._email_send = n.email_send
    n.email_send = Mock()
    self._send_sms = n.send_sms
    n.send_sms = Mock()
  
  def test_request_record_save(self):
    prop = rt.prop_u2_3to10_in1hr
    request = next(rs.prop_to_requests(prop, with_users=[rt.admin_id]))
    request_record = rg.RequestRecord(request)
    self.assertFalse(request_record.record_id)
    request_record.save()
    self.request_records_created.append(request_record)
    self.assertTrue(request_record.record_id)
    saved_requests = [r for r in rg.requests_by_user(USER2) 
                      if r.request_id == request_record.record_id]
    self.assertEqual(len(saved_requests), 1)
    request = saved_requests[0]
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
    self.assertEqual(request.pref_order, 0)
    self.assertEqual(request.current, True)
    self.assertEqual(tuple(request.with_users), (rt.admin_id,))

  def test_add_request_and_partially_matching_requests(self):
    or_group_id = ri._add_request(USER2, rt.prop_u2_2to3_in1hr_in2hr)
    self.request_rows_created.extend(app_tables.requests.search(or_group_id=or_group_id))
    requests = rs.prop_to_requests(rt.prop_u3_3to10_in1hr)
    pmrrs = list(ri.potential_matching_request_records(requests, sm.now()))
    self.assertEqual(len(pmrrs), 1)
    self.assertEqual(pmrrs[0].entity.or_group_id, or_group_id)
    self.assertEqual(pmrrs[0].entity.start_dt, rt.prop_u2_2to3_in1hr_in2hr.times[0].start_date)

  def test_edit_request(self):
    or_group_id0 = ri._add_request(USER3, rt.prop_u3_3to10_in1hr)
    requests = list(rg.current_requests(records=False))
    self.assertEqual(len(requests), 1)
    self.assertEqual(requests[0].max_size, 10)
    request_id0 = requests[0].request_id
    self.assertTrue(request_id0)
    requests[0].max_size = 3
    _prop = list(ri.requests_to_props(requests, USER3))[0]
    or_group_id1 = ri._edit_request(USER3, _prop)
    self.request_rows_created.extend(app_tables.requests.search(or_group_id=or_group_id0))
    edited_requests = list(rg.current_requests(records=False))
    request_id1 = edited_requests[0].request_id
    self.assertEqual(or_group_id0, or_group_id1)
    self.assertEqual(request_id0, request_id1)
    self.assertEqual(len(edited_requests), 1)
    self.assertEqual(edited_requests[0].or_group_id, or_group_id1)
    self.assertEqual(edited_requests[0].max_size, 3)

  def test_edit_request_change_eligible(self):
    or_group_id0 = ri._add_request(USER3, rt.prop_u3_3to10_in1hr)
    self.request_rows_created.extend(app_tables.requests.search(or_group_id=or_group_id0))
    requests = list(rg.current_requests(records=False))
    self.assertEqual(len(requests), 1)
    request_id0 = requests[0].request_id
    self.assertTrue(request_id0)
    requests[0].eligible = 0
    requests[0].eligible_users = [rt.admin_id]
    requests[0].eformat.duration = 15
    _prop = list(ri.requests_to_props(requests, USER3))[0]
    or_group_id1 = ri._edit_request(USER3, _prop)
    edited_requests = list(rg.current_requests(records=False))
    request_id1 = edited_requests[0].request_id
    self.assertEqual(or_group_id0, or_group_id1)
    self.assertEqual(request_id0, request_id1)
    self.assertEqual(len(edited_requests), 1)
    self.assertEqual(edited_requests[0].or_group_id, or_group_id1)
  
  def test_visible_requests(self):
    or_group_id0 = ri._add_request(USER3, rt.prop_u3_3to10_in1hr)
    or_group_id1 = ri._add_request(ADMIN, rt.prop_uA_2to2_in1hr)
    self.request_rows_created.extend(app_tables.requests.search(or_group_id=q.any_of(or_group_id0, or_group_id1)))
    visible_requests = ri.current_visible_requests(USER2, list(rg.current_requests(records=True)))
    self.assertEqual(len(visible_requests), 1)
    self.assertEqual(visible_requests[0].or_group_id, or_group_id1)

  def test_visible_request_with(self):
    or_group_id0 = ri._add_request(USER3, rt.prop_u3_3to10_in1hr)
    self.request_rows_created.extend(app_tables.requests.search(or_group_id=q.any_of(or_group_id0)))
    request = next(rs.prop_to_requests(rt.prop_uA_2to2_in1hr, with_users=[rt.u2.user_id]))
    request_record = rg.RequestRecord(request)
    request_record.save()
    self.request_records_created.append(request_record)
    visible_requests = ri.current_visible_requests(USER2, list(rg.current_requests(records=True)))
    self.assertEqual(len(visible_requests), 1)
    self.assertEqual(visible_requests[0].or_group_id, request.or_group_id)

  def test_not_visible_request_with(self):
    or_group_id0 = ri._add_request(USER3, rt.prop_u3_3to10_in1hr)
    self.request_rows_created.extend(app_tables.requests.search(or_group_id=q.any_of(or_group_id0)))
    request = next(rs.prop_to_requests(rt.prop_uA_2to2_in1hr, with_users=[rt.u3.user_id]))
    request_record = rg.RequestRecord(request)
    request_record.save()
    self.request_records_created.append(request_record)
    visible_requests = ri.current_visible_requests(USER2, list(rg.current_requests(records=True)))
    self.assertFalse(visible_requests)
  
  def tearDown(self):
    n.email_send = self._email_send
    n.send_sms = self._send_sms
    for rr in self.request_records_created:
      rr._row.delete()
    for row in self.request_rows_created:
      row.delete()