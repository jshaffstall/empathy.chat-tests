import unittest
from empathy_chat import network_controller as nc
from empathy_chat import glob
from . import test_helper as th


class ConnectionsTest(unittest.TestCase):
  def setUp(self):
    glob.connections = [
      dict(user_id1='me', user_id2='o1'),
      dict(user_id1='o1', user_id2='me'),
    ]
  
  def test_no_connections(self):
    self.assertEqual(nc.get_connections('123'), [])

  def test_my_connections(self):
    self.assertEqual(len(nc.get_connections('me')), 1)
