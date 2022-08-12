import unittest
from empathy_chat import network_controller as nc
from empathy_chat import glob
from empathy_chat import portable as port
from empathy_chat.groups import Group, MyGroups
from . import test_helper as th


glob.connections = [
  dict(user_id1='me', user_id2='o1'),
  dict(user_id1='o1', user_id2='me'),
  dict(user_id1='o1', user_id2='o2'),
  dict(user_id1='o2', user_id2='o1'),
  dict(user_id1='me', user_id2='o3'),
  dict(user_id1='o3', user_id2='me'),
]
my_profile = port.UserFull(name="Tim", last_active=10, distance=0)
o1_profile = port.UserFull(name="Other 1", last_active=1, distance=1)
o2_profile = port.UserFull(name="Other 2", last_active=2, distance=2)
o3_profile = port.UserFull(name="Other 3", last_active=3, distance=1)
o4_profile = port.UserFull(name="Other 4", last_active=4, common_group_names=["Group 1"], starred=True)
glob.users = {
  'me': my_profile,
  'o1': o1_profile,
  'o2': o2_profile,
  'o3': o3_profile,
  'o4': o4_profile,
}
glob.my_groups = MyGroups()
glob.their_groups = {
  'g1': Group(name='Group 1', group_id='g1', members=['o4'], hosts=['o4'])
}
glob.logged_in_user_id = 'me'
glob.trust_level = 2


class RelationshipsTest(unittest.TestCase):
  def test_self_relationships(self):
    rel = nc.get_relationships(glob.logged_in_user_id)
    self.assertEqual(rel, [])
    
  def test_unlinked_relationships(self):
    rel = nc.get_relationships('o4')
    self.assertEqual(rel, [])


class CreateFormTest(unittest.TestCase):
  def test_group_items(self):
    items = nc.get_create_group_items()
    self.assertEqual(len(items), 1)
    self.assertEqual(items[0], dict(key='Group 1', value=glob.their_groups['g1'], subtext="(host: Other 4)"))
    
  def test_create_user_items(self):
    name_items, starred_name_list = nc.get_create_user_items()
    self.assertEqual(len(name_items), 3)
    self.assertEqual(name_items, [glob.users[id].name_item() for id in ['o1', 'o3', 'o4']])
    self.assertEqual(starred_name_list, ["Other 4"])
  

class ConnectionsTest(unittest.TestCase):
  def test_no_connections(self):
    self.assertEqual(nc.get_connections('123'), [])

  def test_my_connections(self):
    my_connections = nc.get_connections('me')
    self.assertEqual(len(my_connections), 4)
    self.assertEqual(my_connections, [glob.users[id] for id in ['o3', 'o1', 'o2', 'o4']])

  def test_their_connections(self):
    o1_connections = nc.get_connections('o1')
    self.assertEqual(len(o1_connections), 2)
    o2_connections = nc.get_connections('o2')
    self.assertEqual(len(o2_connections), 1)
    o3_connections = nc.get_connections('o3')
    self.assertEqual(len(o3_connections), 1)
    o4_connections = nc.get_connections('o4')
    self.assertEqual(len(o4_connections), 0)
