# import anvil.users
import anvil.server
import anvil.secrets as secrets
import anvil.tables
from anvil.tables import app_tables, order_by
import anvil.tables.query as q
import unittest
from unittest.mock import Mock
from empathy_chat import matcher as m
from empathy_chat import parameters as p
from empathy_chat import connections as c
from empathy_chat import server_misc as sm
from empathy_chat import notifies as n


ADMIN = app_tables.users.get(email=secrets.get_secret('admin_email')) #anvil.users.get_user()
USER2 = app_tables.users.get(email=secrets.get_secret('test_user2_email'))


def name_mock(user, to_user):
  return user


class NamesTest(unittest.TestCase):
  def setUp(self):
    self.name_fn = Mock()
    self.name_fn.side_effect = name_mock
  
  def test_single_name(self):
    self.assertEqual("Peter", n._names(["Peter"], to_user=USER2, name_fn=self.name_fn))
    
  def test_two_names(self):
    self.assertEqual("Peter and Paul", n._names(["Peter", "Paul"], to_user=USER2, name_fn=self.name_fn))

  def test_three_plus_names(self):  
    self.assertEqual("Peter, Paul, and Mary", n._names(["Peter", "Paul", "Mary"], to_user=USER2, name_fn=self.name_fn))
    self.assertEqual("Peter, Paul, James, and Mary", n._names(["Peter", "Paul", "James", "Mary"], to_user=USER2, name_fn=self.name_fn))

      
class SecondsLeftTest(unittest.TestCase):
  def test_initial_requesting(self):
    self.assertEqual(m._seconds_left("requesting"), p.WAIT_SECONDS)
 

class NotifyConnectedTest(unittest.TestCase):
  def test_notify_connected(self):
    class FakeUser(dict):
      def get_id(self):
        return [42,42]
    invite_dict = {'user1': FakeUser(), 'user2': FakeUser(first_name="first", last_name="last"), 'distance': 1}
    invite_reply_dict = {'relationship2to1': "spouse"}
    self.assertEqual(c._connected_prompt(invite_dict, invite_reply_dict)['spec'], 
                     dict(name="connected", to_name="first last", to_id=[42,42], rel="spouse"),
                    )

    
# @anvil.server.background_task
# def server_auto_tests(verbosity=1):
#   #unittest.main(exit=False)
#   import sys
#   test_modules = ['auto_test', 'relationship_test']
#   test = unittest.TestLoader().loadTestsFromNames(test_modules)
#   unittest.TextTestRunner(stream=sys.stdout, verbosity=verbosity).run(test)

  
@anvil.server.callable
def slow_tests(verbosity=2):
  #unittest.main(exit=False)
  if True: #anvil.users.get_user()['trust_level'] >= sm.TEST_TRUST_LEVEL:
    import sys
    test_modules = ['exchange_test', 'invite_server_test']
    test = unittest.TestLoader().loadTestsFromNames(test_modules)
    unittest.TextTestRunner(stream=sys.stdout, verbosity=verbosity).run(test)
