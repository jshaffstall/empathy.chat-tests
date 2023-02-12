import unittest
from .misc_server_test import ADMIN, USER2, USER3
from . import request_test as rt
from empathy_chat import request_interactor as ri
from empathy_chat import request_gateway as rg
from empathy_chat import requests as rs
from empathy_chat import server_misc as sm


class TestRequestRecord(unittest.TestCase):
  def setUp(self):
    self.request_records_created = []
  
  def test_save_request(self):
    request = next(rs.prop_to_requests(rt.prop_uA_3to10_in1hr))
    request_record = rg.RequestRecord(request)
    self.assertFalse(request_record.record_id)
    request_record.save()
    self.assertTrue(request_record.record_id)
    self.
