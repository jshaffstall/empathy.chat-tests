import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import unittest
from empathy_chat import portable as port
from .test_helper import UserLoggedIn


class PortUserTest(unittest.TestCase):
  def test_from_logged_in(self):
    from empathy_chat import glob
    with UserLoggedIn():
      port_user_old = port.User.from_logged_in()
      glob.populate_lazy_vars()
      port_user = port.User.from_logged_in()
      self.assertEqual(port_user.user_id, port_user_old.user_id)
      self.assertEqual(port_user.distance, 0)
      self.assertEqual(port_user_old.distance, 0)
      self.assertTrue(port_user.profile)
    