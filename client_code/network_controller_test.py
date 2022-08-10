import unittest
from . import network_controller as nc
from . import glob
from . import helper as h


class ConnectionsTest(unittest.TestCase):
  def test_no_connections(self):
    self.assertEqual(nc.get_connections(), [])
