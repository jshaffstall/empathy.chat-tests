import unittest
from empathy_chat import network_controller as nc
from empathy_chat import glob
from . import test_helper as th


class ConnectionsTest(unittest.TestCase):
  def test_no_connections(self):
    self.assertEqual(nc.get_connections(), [])
