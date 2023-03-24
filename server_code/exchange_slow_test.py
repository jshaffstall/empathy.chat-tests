import unittest
from unittest.mock import Mock
from anvil.tables import app_tables
import anvil.tables.query as q
from .misc_server_test import ADMIN, USER2, USER3
from . import request_test as rt
from empathy_chat import request_interactor as ri
from empathy_chat import exchange_gateway as eg
from empathy_chat import requests as rs
from empathy_chat import server_misc as sm
from empathy_chat import portable as port
from empathy_chat import exchanges as es

class TestExchangeGateway(unittest.TestCase):
  def setUp(self):
    self.exchange_records_created = []
    self.exchange_rows_created = []
  
  def test_exchange_record_save(self):
    prop = rt.prop_u2_2to3_now
    request = next(rs.prop_to_requests(prop))
    exchange = es.Exchange.from_exchange_prospect(rs.ExchangeProspect([request]))
    exchange_record = eg.ExchangeRecord(exchange)
    self.assertFalse(exchange_record.record_id)
    exchange_record.save()
    #self.exchange_records_created.append(exchange_record)
    self.assertTrue(exchange_record.record_id)
    exchange.exchange_id = exchange_record.record_id
    saved_exchange = eg.ExchangeRecord.from_id(exchange_record.record_id)
    self.assertEqual(exchange, saved_exchange)

    # self.assertTrue(request.or_group_id)
    # self.assertEqual(request.exchange_format.duration, prop.times[0].duration)
    # self.assertEqual(request.expire_dt, prop.times[0].expire_date)
    # self.assertEqual(request.user, prop.user.user_id)
    # self.assertEqual(request.start_dt, prop.times[0].start_date)
    # self.assertEqual(request.create_dt, request.edit_dt)
    # self.assertEqual(request.min_size, prop.min_size)
    # self.assertEqual(request.max_size, prop.max_size)
    # self.assertEqual(request.eligible, prop.eligible)
    # self.assertEqual(request.eligible_users, [pu.user_id for pu in prop.eligible_users])
    # self.assertEqual(request.eligible_groups, prop.eligible_groups)
    # self.assertEqual(request.eligible_starred, prop.eligible_starred)
    # self.assertEqual(request.pref_order, 0)
    # self.assertEqual(request.current, True)
    # self.assertEqual(tuple(request.with_users), (rt.admin_id,))

  def tearDown(self):
    for er in self.exchange_records_created:
      er._row.delete()
    for row in self.exchange_rows_created:
      row.delete()