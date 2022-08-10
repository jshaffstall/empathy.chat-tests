import unittest
from empathy_chat import network_controller as nc
from empathy_chat import glob
from empathy_chat import portable as port
from . import test_helper as th


class ConnectionsTest(unittest.TestCase):
  def setUp(self):
    glob.connections = [
      dict(user_id1='me', user_id2='o1'),
      dict(user_id1='o1', user_id2='me'),
      dict(user_id1='o1', user_id2='o2'),
      dict(user_id1='o2', user_id2='o1'),
      dict(user_id1='me', user_id2='o3'),
      dict(user_id1='o3', user_id2='me'),
    ]
    glob.users = {
      'me': 'my profile',
      'o1': 'o1 profile',
      'o2': 'o2 profile',
      'o3': 'o3 profile',
    }
    glob.logged_in_user_id = 'me'
  
  def test_no_connections(self):
    self.assertEqual(nc.get_connections('123'), [])

  def test_my_connections(self):
    my_connections = nc.get_connections('me')
    self.assertEqual(len(my_connections), 3)
    self.assertEqual(set(my_connections), set(glob.users.values()) - {glob.users['me']})

  def test_their_connections(self):
    o1_connections = nc.get_connections('o1')
    self.assertEqual(len(o1_connections), 2)
    o2_connections = nc.get_connections('o2')
    self.assertEqual(len(o2_connections), 1)
    o3_connections = nc.get_connections('o3')
    self.assertEqual(len(o3_connections), 1)
