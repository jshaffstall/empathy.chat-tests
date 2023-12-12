import unittest
from unittest.mock import Mock
import datetime
from anvil.tables import app_tables
import anvil.tables.query as q
import anvil.tables
from .misc_server_test import ADMIN, USER2, USER3
from . import request_test as rt
from . import request_slow_test as rst
from empathy_chat import request_interactor as ri
from empathy_chat import request_gateway as rg
from empathy_chat import exchange_gateway as eg
from empathy_chat import exchange_interactor as ei
from empathy_chat import requests as rs
from empathy_chat import server_misc as sm
from empathy_chat import portable as port
from empathy_chat import exchanges as es
from empathy_chat import notifies as n
from anvil_extras.logging import TimerLogger

class TestExchangeGateway(unittest.TestCase):
  def setUp(self):
    self.request_records_saved = []
    self.exchange_records_saved = []
    self.are_request_rows_to_delete = False
    self.test_start_dt = sm.now()
    self._email_send = n.email_send
    n.email_send = Mock()
    self._send_sms = n.send_sms
    n.send_sms = Mock()
    self._notify_edit = ri.RequestManager.notify_edit
    ri.RequestManager.notify_edit = Mock()
    self._ping = ei.ping
    ei.ping = Mock()
  
  def test_exchange_record_save(self):
    prop = rt.prop_u2_2to3_now
    request = next(rs.prop_to_requests(prop))
    request_record = rg.RequestRecord(request)
    self.request_records_saved.append(request_record)
    request_record.save()
    request.request_id = request_record.record_id
    exchange = es.Exchange.from_exchange_prospect(rs.ExchangeProspect([request]))
    exchange_record = eg.ExchangeRecord(exchange)
    self.assertFalse(exchange_record.record_id)
    self.exchange_records_saved.append(exchange_record)
    exchange_record.save()
    self.assertTrue(exchange_record.record_id)
    exchange.exchange_id = exchange_record.record_id
    saved_exchange = eg.ExchangeRecord.from_id(exchange_record.record_id).entity
    for attribute in ['exchange_format', 
                      'room_code',
                      'current',
                      'start_dt',
                      'start_now',
                     ]:
      self.assertEqual(getattr(exchange, attribute), getattr(saved_exchange, attribute))
    for key in ['user_id',
                'request_id',
               ]:
      self.assertEqual(exchange.participants[0][key], saved_exchange.participants[0][key])
    self.assertEqual(saved_exchange.participants[0]['appearances'], [])
    for key in ['slider_value',
                'video_external',
                'complete_dt',
               ]:
      self.assertEqual(saved_exchange.participants[0][key], None)
    self.assertTrue(saved_exchange.participants[0]['entered_dt']) # b/c quick-ping now request

  def test_add_request_exchange_save(self):
    self.are_request_rows_to_delete = True
    with TimerLogger("  test", format="{name}: {elapsed:6.3f} s | {msg}") as timer:
      prop1 = rt.prop_u2_2to3_in1hr_in2hr
      prop2 = rt.prop_uA_2to2_in1hr
      or_group1 = rst.add_request(USER2, prop1)
      timer.check("1st add_request")
      or_group2 = rst.add_request(ADMIN, prop2)
      timer.check("2nd add_request")
      requests = list(app_tables.requests.search(or_group_id=q.any_of(or_group1, or_group2)))
      timer.check("grab request rows created")
      row_2hr = next((row for row in requests 
                      if row['start_dt'] - sm.now() > datetime.timedelta(hours=1.5)))
      self.assertFalse(row_2hr['current'])
      timer.check("check row_2hr")
      upcomings = list(eg.exchanges_by_user(USER2, records=True))
      self.exchange_records_saved.extend(upcomings)
      self.assertEqual(len(upcomings), 1)
      timer.check("grab upcomings")
      match_dicts2 = ei.upcoming_match_dicts(USER2)
      match_dictsA = ei.upcoming_match_dicts(ADMIN)
      timer.check("grab match_dicts")
      self.assertEqual(len(match_dicts2[0]), 5)
      self.assertEqual(len(match_dicts2), 1)
      self.assertEqual(len(match_dicts2), len(match_dictsA))
      for key in match_dicts2[0]:
        if key != 'other_user_ids':
          self.assertEqual(match_dicts2[0][key], match_dictsA[0][key])

  def test_add_request_no_exchange(self):
    self.are_request_rows_to_delete = True
    prop1 = rt.prop_u2_2to3_in1hr_in2hr
    prop2 = rt.prop_uA_2to2_in1hr
    requests2 = rs.Requests(rs.prop_to_requests(prop2, user_id=ADMIN.get_id()))
    requests2[0].eligible = 0
    requests2[0].eligible_users = []
    requests2[0].eligible_starred = False
    or_group1 = rst.add_request(USER2, prop1)
    or_group2 = ri.add_requests(ADMIN, requests2)
    upcomings = list(eg.exchanges_by_user(USER2, records=True))
    if upcomings:
      self.exchange_records_saved.append(upcomings[0])
    self.assertFalse(len(upcomings))
    requests = list(app_tables.requests.search(or_group_id=q.any_of(or_group1, or_group2)))
    row_2hr = next((row for row in requests 
                    if row['start_dt'] - sm.now() > datetime.timedelta(hours=1.5)))
    self.assertTrue(row_2hr['current'])
    
  def tearDown(self):
    n.email_send = self._email_send
    n.send_sms = self._send_sms
    ri.RequestManager.notify_edit = self._notify_edit
    ei.ping = self._ping
    if self.are_request_rows_to_delete:
      rows_created = app_tables.requests.search(rg.requests_fetch, create_dt=q.greater_than_or_equal_to(self.test_start_dt))
    with anvil.tables.batch_delete:
      for row in [rr._row for rr in self.request_records_saved]:
        row.delete()
      for row in [er._row for er in self.exchange_records_saved]:
        for p_row in row['participants']:
          for a_row in p_row['appearances']:
            a_row.delete()
          p_row.delete()
        row.delete()
      if self.are_request_rows_to_delete:
        for row in rows_created:
          row.delete()
